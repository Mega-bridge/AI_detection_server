from celery import Celery
import os
import json
import requests
import time
from config import STATIC_FOLDER, CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from utils import save_image, load_image, draw_detections, draw_detections_v2, run_detection, run_detection_v2
import imghdr

#  Celery 인스턴스 생성
celery = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

@celery.task
def process_image(photo_uid, image_data, start_time, callback_url):
    print(f"Task received at: {start_time}")

    # 이미지 크기 출력
    image_size = len(image_data)
    print(f"Received image size: {image_size} bytes")

    # 이미지 확장자 확인
    image_format = imghdr.what(None, h=image_data)
    print(f"Received image format: {image_format if image_format else 'Unknown'}")

    # 이미지 저장 및 로드
    filepath, filename = save_image(image_data)
    image = load_image(filepath)

    # 객체 탐지
    detections = run_detection(image)

    # 클래스 충치만 필터링
    filtered_detections = [det for det in detections if det["class"] == 0]


    # 탐지 결과 이미지 생성
    output_image = draw_detections(image, filtered_detections)
    output_path = os.path.join(STATIC_FOLDER, filename)
    output_image.save(output_path)

    # 탐지 결과 정리
    results = [{"startX": det["bbox"][0], "startY": det["bbox"][1], 
                "endX": det["bbox"][2], "endY": det["bbox"][3]} for det in filtered_detections]

    response_data = {
        "photoUid": photo_uid,
        "cariesCount": len(results),
        "positions": results
    }

    # 이미지 파일 전송 (최대 2번 시도)
    attempt = 0
    while attempt < 2:
        try:
            with open(output_path, "rb") as image_file:
                files = {"files": (filename, image_file, "image/jpeg")}
                data = {"photoUid": photo_uid, "cariesCount": len(results), "positions": json.dumps(results)}
                response = requests.post(callback_url, data=data, files=files, timeout=5)
                response.raise_for_status()
                break  # 성공 후 루프 종료
        except requests.exceptions.RequestException as e:
            print(f"Error sending results (attempt {attempt + 1}): {e}")
            attempt += 1
            if attempt < 2:
                time.sleep(2)  # 재시도 전 대기
    
    end_time = time.time()  # 결과 전송 완료 시간 기록
    print(f"Task completed at: {end_time}")
    print(f"Total processing time: {end_time - start_time} seconds")

    return response_data


@celery.task
def process_image_v2(result_id, image_data, start_time, callback_url):
    print(f"[V2] Task received at: {start_time}")

    image_size = len(image_data)
    print(f"[V2] Received image size: {image_size} bytes")

    image_format = imghdr.what(None, h=image_data)
    print(f"[V2] Received image format: {image_format if image_format else 'Unknown'}")

    filepath, filename = save_image(image_data)
    image = load_image(filepath)

    # v2
    detections = run_detection_v2(image)

    # filtered_detections = [det for det in detections if det["class"] != 3]
    filtered_detections = [det for det in detections if det["class"] != -1]

    output_image = draw_detections_v2(image, filtered_detections)
    output_path = os.path.join(STATIC_FOLDER, filename)
    output_image.save(output_path)

    results = [{
        "startX": det["bbox"][0],
        "startY": det["bbox"][1],
        "endX": det["bbox"][2],
        "endY": det["bbox"][3],
        "cariesStatus": det["label"]
    } for det in filtered_detections]

    response_data = {
        "resultId": result_id,
        "positions": results
    }

    attempt = 0
    while attempt < 2:
        try:
            with open(output_path, "rb") as image_file:
                files = {"files": (filename, image_file, "image/jpeg")}
                data = {
                    "resultId": result_id,
                    "positions": json.dumps(results)
                }
                response = requests.post(callback_url, data=data, files=files, timeout=5)
                response.raise_for_status()
                break
        except requests.exceptions.RequestException as e:
            print(f"[V2] Error sending results (attempt {attempt + 1}): {e}")
            attempt += 1
            if attempt < 2:
                time.sleep(2)

    end_time = time.time()
    print(f"[V2] Task completed at: {end_time}")
    print(f"[V2] Total processing time: {end_time - start_time} seconds")

    return response_data


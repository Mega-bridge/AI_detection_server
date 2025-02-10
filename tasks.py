from celery import Celery
import os
import requests
from config import STATIC_FOLDER, CALLBACK_URL, CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from utils import save_image, load_image, draw_detections, run_detection

# Celery 인스턴스 생성
celery = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

@celery.task
def process_image(photo_uid, image_data):
    # 이미지 저장 및 로드
    filepath, filename = save_image(image_data)
    image = load_image(filepath)

    # 객체 탐지
    detections = run_detection(image)

    # 탐지 결과 이미지 생성
    output_image = draw_detections(image, detections)
    output_path = os.path.join(STATIC_FOLDER, filename)
    output_image.save(output_path)

    # 탐지 결과 정리
    results = [{"startX": det["bbox"][0], "startY": det["bbox"][1], 
                "endX": det["bbox"][2], "endY": det["bbox"][3]} for det in detections]

    response_data = {
        "photoUid": photo_uid,
        "cariesCount": len(results),
        "positions": results,
        "image_url": f"/result/{filename}"
    }

    # 요청을 보낸 서버로 결과 전달
    try:
        requests.post(CALLBACK_URL, json=response_data, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Error sending results: {e}")

    return response_data

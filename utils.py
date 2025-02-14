import os
from PIL import Image, ImageDraw
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from config import MODEL_PATH
from tempfile import NamedTemporaryFile

# YOLO 모델 로드
model = YOLO(MODEL_PATH)

def save_image(file):
    """ 업로드된 이미지를 저장하고 파일 경로 반환 """
    temp_file = NamedTemporaryFile(delete=False)  # 임시 파일 생성, 삭제하지 않도록 설정
    temp_file.write(file)  # image_data를 임시 파일에 기록
    temp_file.close() 
    
    filename = secure_filename(temp_file.name.split(os.sep)[-1])
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        filename += '.png'  # 확장자 없으면 .png 추가

    return temp_file.name, filename

def load_image(filepath):
    """ 이미지 파일 PIL 이미지 객체로 반환 """
    return Image.open(filepath)

def draw_detections(image, detections):
    """ 탐지된 객체 박스를 이미지 위에 그림 """
    output_image = image.copy()
    draw = ImageDraw.Draw(output_image)
    for det in detections:
        draw.rectangle(det["bbox"], outline="red", width=3)
    return output_image

def run_detection(image):
    """ YOLO 모델 실행해 탐지 결과 반환 (NMS 적용) """
    results = model.predict(image, conf=0.35, iou=0.5)  # conf와 iou 값 조정 가능
    detections = []
    
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            detections.append({"bbox": [x1, y1, x2, y2], "confidence": conf, "class": cls})
    
    return detections

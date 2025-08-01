import os
from PIL import Image, ImageDraw, ImageFont
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from config import MODEL_PATH, MODEL_PATH_v2
from tempfile import NamedTemporaryFile
import matplotlib.font_manager as fm


# YOLO 모델 로드
model = YOLO(MODEL_PATH)
model2 = YOLO(MODEL_PATH_v2)


# 클래스 ID - 이름 매핑
CLASS_NAMES = {
    0: "CROWN",
    1: "EXTRACTION",
    2: "INLAY_RESIN",
    3: "TREATED"
}

CLASS_COLORS = {
    0: "#4c22b2",
    1: "#ea1415",
    2: "#ffab00",
    3: "#ffffff"
}

def draw_detections(image, detections):
    """ 탐지된 객체 박스를 이미지 위에 그림 """
    output_image = image.copy()
    draw = ImageDraw.Draw(output_image)
    
    # font_path = fm.findSystemFonts(fontpaths=None, fontext='ttf')
    # korean_fonts = [f for f in font_path if 'malgun' in f.lower() or 'gothic' in f.lower()]

    #try:
    #    font = ImageFont.truetype(korean_fonts[0], 20)
    #except:
    #    font = ImageFont.load_default()
    
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
    #    conf = det["confidence"]
        class_id = det["class"]
    #    label_text = f"{CLASS_NAMES.get(class_id, 'Unknown')} ({conf:.2f})"
        color = "white"
        thickness = 2

        draw.rectangle([x1, y1, x2, y2], outline=color, width=thickness)

    #    text_size = draw.textbbox((x1, y1), label_text, font=font)
    #    text_height = text_size[3] - text_size[1]
    #    text_y = max(y1 - text_height, 0)

    #    draw.rectangle([text_size[0], text_y, text_size[2], text_y + text_height], fill=color)
    #    draw.text((x1, text_y), label_text, fill='black', font=font)
    
    return output_image

def draw_detections_v2(image, detections):
    """ 탐지된 객체 박스를 이미지 위에 그림 """
    output_image = image.copy()
    draw = ImageDraw.Draw(output_image)
    
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        class_id = det["class"]
        color = CLASS_COLORS.get(class_id, "white")
        thickness = 2

        draw.rectangle([x1, y1, x2, y2], outline=color, width=thickness)
 
    return output_image

def run_detection(image):
    """ YOLO 모델 실행해 탐지 결과 반환 (NMS 적용) """
    results = model.predict(image, conf=0.38, iou=0.5)  # conf와 iou 값 조정 가능
    detections = []

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            class_id = int(box.cls[0])  # 클래스 인덱스
            label = model.names[class_id]

            detections.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": conf,
                "class": class_id,
                "label": label
            })

    return detections

def run_detection_v2(image):
    """ YOLO 모델 실행해 탐지 결과 반환 (NMS 적용) """
    results = model2.predict(image, conf=0.38, iou=0.5)
    detections = []

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            class_id = int(box.cls[0])
            label = CLASS_NAMES.get(class_id, "Unknown")

            detections.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": conf,
                "class": class_id,
                "label": label
            })

    return detections


def save_image(file):
    """ 업로드된 이미지를 저장하고 파일 경로 반환 """
    temp_file = NamedTemporaryFile(delete=False)  # 임시 파일 생성, 삭제하지 않도록 설정
    temp_file.write(file)  # image_data를 임시 파일에 기록
    temp_file.close() 
    
    filename = secure_filename(temp_file.name.split(os.sep)[-1])
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        filename += '.jpeg'  # 확장자 없으면 .jpeg 추가

    return temp_file.name, filename

def load_image(filepath):
    """ 이미지 파일 PIL 이미지 객체로 반환 """
    return Image.open(filepath)





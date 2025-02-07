from flask import Flask, request, jsonify, send_file
import os
from config import UPLOAD_FOLDER, STATIC_FOLDER
from utils import save_image, load_image, draw_detections, run_detection

app = Flask(__name__)

@app.route("/")
def home():
    return "Flask 서버 실행 중"

@app.route("/detect", methods=["POST"])
def detect():
    if "image" not in request.files or "photoUid" not in request.form:
        return jsonify({"error": "Image and photoUid are required"}), 400

    file = request.files["image"]
    photo_uid = request.form["photoUid"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # 이미지 저장 및 로드
    filepath, filename = save_image(file)
    image = load_image(filepath)

    # 객체 탐지
    detections = run_detection(image)

    # 탐지 결과 이미지 생성
    output_image = draw_detections(image, detections)

    # 결과 이미지 저장
    output_path = os.path.join(STATIC_FOLDER, filename)
    output_image.save(output_path)

    # 필요한 값만 추출
    results = []
    for det in detections:
        startX, startY, endX, endY = det["bbox"]  # bounding box 좌표
        results.append({
            "startX": startX,
            "startY": startY,
            "endX": endX,
            "endY": endY
        })
    
    # 결과 데이터 구성
    response_data = {
        "photoUid": photo_uid,
        "cariesCount": len(results),
        "positions": results,
        "image_url": f"/result/{filename}"
    }
    
    return jsonify(response_data)

@app.route("/result/<filename>")
def result(filename):
    return send_file(os.path.join(STATIC_FOLDER, filename), mimetype="image/png")

@app.route('/favicon.ico')
def favicon():
    return "", 204  # 204 No Content 응답

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(STATIC_FOLDER, exist_ok=True)
    app.run(host="0.0.0.0", port=5000)

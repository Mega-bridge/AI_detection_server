from flask import Flask, request, jsonify, send_file
import os
from config import UPLOAD_FOLDER, STATIC_FOLDER
from utils import save_image
import time
from tasks import process_image, process_image_v2


app = Flask(__name__)

@app.route("/")
def home():
    return "Flask 서버 실행 중!"

@app.route("/detect", methods=["POST"])
def detect():
    if "image" not in request.files or "photoUid" not in request.form:
        return jsonify({"error": "Image and photoUid are required"}), 400

    file = request.files["image"]
    photo_uid = request.form["photoUid"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    start_time = time.time()  # 요청을 받은 시점 기록
    callback_url = "https://toothly.megabridge.co.kr/api/ai/advance-diagnosis"
    process_image.delay(photo_uid, file.read(), start_time, callback_url)

    return jsonify({"message": "Processing started", "photoUid": photo_uid})


@app.route("/detect/v2", methods=["POST"]) # v2
def detectV2():
    if "image" not in request.files or "resultId" not in request.form:
        return jsonify({"error": "Image and resultId are required"}), 400

    file = request.files["image"]
    result_id = request.form["resultId"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    start_time = time.time()  # 요청을 받은 시점 기록
    callback_url = "https://toothly.megabridge.co.kr/api/ai/advance-diagnosis/v2" #v2
    process_image_v2.delay(result_id, file.read(), start_time, callback_url)

    return jsonify({"message": "Processing started", "resultId": result_id})



@app.route("/result/<filename>")
def result(filename):
    return send_file(os.path.join(STATIC_FOLDER, filename), mimetype="image/jpeg")

@app.route('/favicon.ico')
def favicon():
    return "", 204

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(STATIC_FOLDER, exist_ok=True)
    app.run(host="0.0.0.0", port=5000)


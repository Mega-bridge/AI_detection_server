# 1. Python 3.11 기반의 공식 이미지 사용
FROM python:3.11

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 필요한 파일 복사
COPY requirements.txt .
COPY app.py .
COPY config.py .
COPY utils.py .
COPY model /app/model

# 4. 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. Flask API 실행
CMD ["python", "app.py"]

# 1. Python 3.11 기반 공식 이미지 사용
FROM python:3.11

# 시스템 패키지 설치 (libGL 해결)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 파일 복사
COPY . .

# 4. 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 포트 오픈
EXPOSE 5000

# 5. Flask API 실행
CMD ["python", "app.py"]

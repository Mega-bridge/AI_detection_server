import requests
import threading
import time
import os
import psutil
import docker

API_URL = "http://localhost:5000/detect"
IMAGE_PATH = "C:/Users/ljh86/Documents/ai_detection_server/uploads/23.jpg"

# Docker 클라이언트 설정
client = docker.from_env()

# 현재 실행 중인 모든 컨테이너의 메모리 사용량 합산
def get_total_container_memory():
    total_memory = 0
    print("\n--- Docker Container Memory Usage ---")
    for container in client.containers.list():
        stats = container.stats(stream=False)  # 컨테이너 상태 정보 가져오기
        mem_usage = stats["memory_stats"]["usage"] / 1024 / 1024  # MB 단위 변환
        total_memory += mem_usage
        print(f"{container.name}: {mem_usage:.2f} MB")
    print(f"Total Memory Usage: {total_memory:.2f} MB\n")
    return total_memory

# API 호출 함수
def send_request(i):
    with open(IMAGE_PATH, "rb") as img:
        files = {"image": img}
        data = {"photoUid": f"test_{i}"}
        try:
            response = requests.post(API_URL, files=files, data=data)
            print(f"[{i}] Status Code: {response.status_code}, Response: {response.json()}")
        except Exception as e:
            print(f"[{i}] Error: {e}")

# 동시 실행할 스레드 생성
threads = []
start_memory = get_total_container_memory()
print(f"Before Requests: {start_memory:.2f} MB")

start_time = time.time()

for i in range(100):  # 100개의 요청 실행
    t = threading.Thread(target=send_request, args=(i,))
    t.start()
    threads.append(t)

# 모든 요청 완료 대기
for t in threads:
    t.join()

end_time = time.time()
end_memory = get_total_container_memory()

# 결과 출력
print(f"After Requests: {end_memory:.2f} MB")
print(f"Memory Increase: {end_memory - start_memory:.2f} MB")
print(f"Total Time Taken: {end_time - start_time:.2f} seconds")

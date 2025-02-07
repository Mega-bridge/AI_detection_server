MODEL_PATH = "model/11n_train7_best.pt"
UPLOAD_FOLDER = "uploads"
STATIC_FOLDER = "static"
ALLOWED_EXTENSIONS = {"jpg", "png"}

# Celery 설정
CELERY_BROKER_URL = "pyamqp://guest@localhost//"  # RabbitMQ
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"  # 결과 저장소
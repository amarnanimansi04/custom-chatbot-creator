from celery import Celery
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

UPSTASH_REDIS_REST_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_REDIS_REST_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

# Build proper SSL Redis URL for Upstash
hostname = UPSTASH_REDIS_REST_URL.replace("https://", "")
broker_url = f"rediss://:{UPSTASH_REDIS_REST_TOKEN}@{hostname}:6379?ssl_cert_reqs=CERT_NONE"

celery_app = Celery(
    "custom_chatbot_creator",
    broker=broker_url,
    backend=broker_url,
    include=["tasks.scrape_task"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    broker_connection_retry_on_startup=True,
    broker_use_ssl={
        "ssl_cert_reqs": "CERT_NONE"
    },
    redis_backend_use_ssl={
        "ssl_cert_reqs": "CERT_NONE"
    },
    worker_pool="solo", 
)
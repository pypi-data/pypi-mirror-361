from celery import Celery
import os


CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')

app = Celery(
    'sskw_tasks',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['sskw.tasks'],
    timezone='UTC',
    enable_utc=True,
    
    # JSON 序列化配置
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    result_accept_content=['json'],
)
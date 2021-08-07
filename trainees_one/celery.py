import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trainees_one.settings')
celery_app = Celery('trainees_one')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()

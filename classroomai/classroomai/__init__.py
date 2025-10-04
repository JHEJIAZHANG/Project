# 這將確保 Django 啟動時載入 Celery 應用
from .celery import app as celery_app

__all__ = ('celery_app',)
"""
Celery 配置檔案
用於配置 Celery 任務隊列和定時任務
"""
import os
from celery import Celery
from django.conf import settings

# 設定 Django 設定模組
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'classroomai.settings')

# 創建 Celery 應用
app = Celery('classroomai')

# 使用 Django 設定配置 Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自動發現任務
app.autodiscover_tasks()

# 配置定時任務
app.conf.beat_schedule = {
    # 每小時自動同步 Google Classroom
    'auto-sync-classroom-hourly': {
        'task': 'services.tasks.auto_sync_classroom_for_all_users',
        'schedule': 60.0 * 60.0,  # 每小時執行一次
    },
    # 每 6 小時自動同步 Google Calendar
    'auto-sync-calendar-6hourly': {
        'task': 'services.tasks.auto_sync_calendar_for_all_users',
        'schedule': 60.0 * 60.0 * 6,  # 每 6 小時執行一次
    },
    # 每天清理過期的暫存資料
    'cleanup-expired-cache-daily': {
        'task': 'services.tasks.cleanup_expired_cache',
        'schedule': 60.0 * 60.0 * 24,  # 每天執行一次
    },
}

# 設定時區
app.conf.timezone = 'Asia/Taipei'

@app.task(bind=True)
def debug_task(self):
    """除錯任務"""
    print(f'Request: {self.request!r}')
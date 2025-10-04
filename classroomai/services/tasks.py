"""
Celery 定時任務
用於自動同步 Google Classroom 和 Google Calendar
"""
import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from user.models import LineProfile
from services.classroom_sync_service import ClassroomSyncService
from services.calendar_sync_service import CalendarSyncService
from line_bot.models import HomeworkStatisticsCache

logger = logging.getLogger(__name__)

@shared_task
def auto_sync_classroom_for_all_users():
    """
    為所有已連接 Google Classroom 的用戶自動同步課程和作業
    """
    try:
        logger.info("Starting auto sync for all Google Classroom users")
        
        # 獲取所有已連接 Google Classroom 的用戶
        connected_users = LineProfile.objects.filter(
            google_refresh_token__isnull=False
        ).exclude(google_refresh_token="")
        
        sync_count = 0
        error_count = 0
        
        for user in connected_users:
            try:
                logger.info(f"Auto syncing Google Classroom for user: {user.line_user_id}")
                
                # 創建同步服務實例
                sync_service = ClassroomSyncService(user.line_user_id)
                
                # 同步課程和作業
                result = sync_service.sync_all_courses()
                
                if result.get('success'):
                    sync_count += 1
                    logger.info(f"Successfully synced for user {user.line_user_id}")
                else:
                    error_count += 1
                    logger.error(f"Failed to sync for user {user.line_user_id}: {result.get('message')}")
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error syncing for user {user.line_user_id}: {str(e)}")
        
        logger.info(f"Auto sync completed. Success: {sync_count}, Errors: {error_count}")
        return {
            'success': True,
            'synced_users': sync_count,
            'error_count': error_count
        }
        
    except Exception as e:
        logger.error(f"Error in auto_sync_classroom_for_all_users: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@shared_task
def auto_sync_calendar_for_all_users():
    """
    為所有已連接 Google Calendar 的用戶自動同步日曆事件
    """
    try:
        logger.info("Starting auto sync for all Google Calendar users")
        
        # 獲取所有已連接 Google 服務的用戶
        connected_users = LineProfile.objects.filter(
            google_refresh_token__isnull=False
        ).exclude(google_refresh_token="")
        
        sync_count = 0
        error_count = 0
        
        for user in connected_users:
            try:
                logger.info(f"Auto syncing Google Calendar for user: {user.line_user_id}")
                
                # 創建同步服務實例
                sync_service = CalendarSyncService(user.line_user_id)
                
                # 同步日曆事件（使用 primary 日曆）
                result = sync_service.sync_events_for_user(
                    line_user_id=user.line_user_id,
                    calendar_ids=['primary']
                )
                
                if result.get('success'):
                    sync_count += 1
                    logger.info(f"Successfully synced calendar for user {user.line_user_id}")
                else:
                    error_count += 1
                    logger.error(f"Failed to sync calendar for user {user.line_user_id}: {result.get('message')}")
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error syncing calendar for user {user.line_user_id}: {str(e)}")
        
        logger.info(f"Auto calendar sync completed. Success: {sync_count}, Errors: {error_count}")
        return {
            'success': True,
            'synced_users': sync_count,
            'error_count': error_count
        }
        
    except Exception as e:
        logger.error(f"Error in auto_sync_calendar_for_all_users: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@shared_task
def cleanup_expired_cache():
    """
    清理過期的作業統計暫存資料
    """
    try:
        logger.info("Starting cleanup of expired cache")
        
        # 刪除 24 小時前的暫存資料
        cutoff_time = timezone.now() - timedelta(hours=24)
        deleted_count, _ = HomeworkStatisticsCache.objects.filter(
            created_at__lt=cutoff_time
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} expired cache entries")
        return {
            'success': True,
            'deleted_count': deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup_expired_cache: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@shared_task
def sync_user_data(line_user_id: str, sync_type: str = 'all'):
    """
    為特定用戶同步資料
    
    Args:
        line_user_id: LINE 用戶 ID
        sync_type: 同步類型 ('classroom', 'calendar', 'all')
    """
    try:
        logger.info(f"Starting sync for user {line_user_id}, type: {sync_type}")
        
        results = {}
        
        if sync_type in ['classroom', 'all']:
            # 同步 Google Classroom
            try:
                sync_service = ClassroomSyncService(line_user_id)
                classroom_result = sync_service.sync_all_courses_and_assignments()
                results['classroom'] = classroom_result
            except Exception as e:
                results['classroom'] = {'success': False, 'error': str(e)}
        
        if sync_type in ['calendar', 'all']:
            # 同步 Google Calendar
            try:
                sync_service = CalendarSyncService(line_user_id)
                calendar_result = sync_service.sync_events_for_user(
                    line_user_id=line_user_id,
                    calendar_ids=['primary']
                )
                results['calendar'] = calendar_result
            except Exception as e:
                results['calendar'] = {'success': False, 'error': str(e)}
        
        logger.info(f"Sync completed for user {line_user_id}")
        return {
            'success': True,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Error in sync_user_data for user {line_user_id}: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
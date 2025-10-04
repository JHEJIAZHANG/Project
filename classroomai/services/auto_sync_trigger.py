"""
自動同步觸發服務
在老師 Classroom 操作成功後自動觸發同步
"""
import logging
import asyncio
from typing import Dict, Optional
from django.utils import timezone
from .classroom_sync_service import ClassroomSyncService

logger = logging.getLogger(__name__)


class AutoSyncTrigger:
    """自動同步觸發器"""
    
    @classmethod
    def trigger_course_sync(cls, line_user_id: str, google_course_id: str, operation: str = 'update') -> Dict:
        """
        觸發單一課程同步
        
        Args:
            line_user_id: LINE 使用者 ID
            google_course_id: Google Classroom 課程 ID
            operation: 操作類型 (create, update, delete)
            
        Returns:
            Dict: 同步結果
        """
        try:
            logger.info(f"Auto sync triggered for course {google_course_id}, operation: {operation}")
            
            # 執行同步
            sync_service = ClassroomSyncService(line_user_id)
            sync_result = sync_service.sync_single_course(google_course_id)
            
            # 記錄同步結果
            if sync_result['success']:
                logger.info(f"Auto sync completed successfully for course {google_course_id}")
                cls._log_sync_success(line_user_id, google_course_id, operation, sync_result)
            else:
                logger.warning(f"Auto sync failed for course {google_course_id}: {sync_result.get('message', 'Unknown error')}")
                cls._log_sync_failure(line_user_id, google_course_id, operation, sync_result)
            
            return sync_result
            
        except Exception as e:
            logger.error(f"Error in auto sync trigger for course {google_course_id}: {str(e)}")
            error_result = {
                'success': False,
                'message': f'自動同步失敗: {str(e)}',
                'assignments_synced': 0,
                'errors': [str(e)]
            }
            cls._log_sync_failure(line_user_id, google_course_id, operation, error_result)
            return error_result
    
    @classmethod
    def trigger_assignment_sync(cls, line_user_id: str, google_course_id: str, coursework_id: str, operation: str = 'update') -> Dict:
        """
        觸發作業相關同步
        
        Args:
            line_user_id: LINE 使用者 ID
            google_course_id: Google Classroom 課程 ID
            coursework_id: 作業 ID
            operation: 操作類型 (create, update, delete)
            
        Returns:
            Dict: 同步結果
        """
        try:
            logger.info(f"Auto sync triggered for assignment {coursework_id} in course {google_course_id}, operation: {operation}")
            
            # 對於作業操作，同步整個課程以確保一致性
            sync_result = cls.trigger_course_sync(line_user_id, google_course_id, f'assignment_{operation}')
            
            # 添加作業相關資訊到結果中
            if sync_result['success']:
                sync_result['triggered_by'] = f'assignment_{operation}'
                sync_result['coursework_id'] = coursework_id
            
            return sync_result
            
        except Exception as e:
            logger.error(f"Error in auto sync trigger for assignment {coursework_id}: {str(e)}")
            return {
                'success': False,
                'message': f'自動同步失敗: {str(e)}',
                'assignments_synced': 0,
                'errors': [str(e)]
            }
    
    @classmethod
    def schedule_delayed_sync(cls, line_user_id: str, google_course_id: str, delay_seconds: int = 30) -> None:
        """
        排程延遲同步（避免頻繁同步）
        
        Args:
            line_user_id: LINE 使用者 ID
            google_course_id: Google Classroom 課程 ID
            delay_seconds: 延遲秒數
        """
        try:
            logger.info(f"Scheduling delayed sync for course {google_course_id} in {delay_seconds} seconds")
            
            # 這裡可以使用 Celery 或其他任務隊列來實現延遲執行
            # 目前先使用簡單的實現
            import threading
            import time
            
            def delayed_sync():
                time.sleep(delay_seconds)
                cls.trigger_course_sync(line_user_id, google_course_id, 'scheduled')
            
            thread = threading.Thread(target=delayed_sync)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            logger.error(f"Error scheduling delayed sync: {str(e)}")
    
    @classmethod
    def _log_sync_success(cls, line_user_id: str, google_course_id: str, operation: str, result: Dict) -> None:
        """記錄同步成功"""
        try:
            log_data = {
                'timestamp': timezone.now().isoformat(),
                'user_id': line_user_id,
                'course_id': google_course_id,
                'operation': operation,
                'status': 'success',
                'assignments_synced': result.get('assignments_synced', 0),
                'trigger_type': 'auto'
            }
            
            logger.info(f"Sync success logged: {log_data}")
            
            # 這裡可以將日誌寫入資料庫或外部日誌系統
            # 目前先記錄到應用程式日誌
            
        except Exception as e:
            logger.error(f"Error logging sync success: {str(e)}")
    
    @classmethod
    def _log_sync_failure(cls, line_user_id: str, google_course_id: str, operation: str, result: Dict) -> None:
        """記錄同步失敗"""
        try:
            log_data = {
                'timestamp': timezone.now().isoformat(),
                'user_id': line_user_id,
                'course_id': google_course_id,
                'operation': operation,
                'status': 'failure',
                'error_message': result.get('message', 'Unknown error'),
                'errors': result.get('errors', []),
                'trigger_type': 'auto'
            }
            
            logger.warning(f"Sync failure logged: {log_data}")
            
            # 這裡可以將錯誤日誌寫入資料庫或發送通知
            # 目前先記錄到應用程式日誌
            
        except Exception as e:
            logger.error(f"Error logging sync failure: {str(e)}")
    
    @classmethod
    def get_sync_status(cls, line_user_id: str, google_course_id: Optional[str] = None) -> Dict:
        """
        獲取同步狀態
        
        Args:
            line_user_id: LINE 使用者 ID
            google_course_id: Google Classroom 課程 ID（可選）
            
        Returns:
            Dict: 同步狀態資訊
        """
        try:
            # 這裡可以從資料庫或快取中獲取同步狀態
            # 目前返回基本狀態資訊
            
            status_info = {
                'user_id': line_user_id,
                'last_check': timezone.now().isoformat(),
                'auto_sync_enabled': True,
                'sync_frequency': 'on_demand'  # 按需同步
            }
            
            if google_course_id:
                status_info['course_id'] = google_course_id
                # 可以添加特定課程的同步狀態
            
            return {
                'success': True,
                'data': status_info
            }
            
        except Exception as e:
            logger.error(f"Error getting sync status: {str(e)}")
            return {
                'success': False,
                'message': f'獲取同步狀態失敗: {str(e)}'
            }


class SyncNotificationService:
    """同步通知服務"""
    
    @classmethod
    def send_sync_notification(cls, line_user_id: str, sync_result: Dict, operation: str = 'sync') -> None:
        """
        發送同步通知
        
        Args:
            line_user_id: LINE 使用者 ID
            sync_result: 同步結果
            operation: 操作類型
        """
        try:
            if sync_result['success']:
                message = cls._format_success_message(sync_result, operation)
            else:
                message = cls._format_error_message(sync_result, operation)
            
            # 這裡可以整合 LINE Bot API 發送通知
            # 目前先記錄到日誌
            logger.info(f"Sync notification for {line_user_id}: {message}")
            
        except Exception as e:
            logger.error(f"Error sending sync notification: {str(e)}")
    
    @classmethod
    def _format_success_message(cls, result: Dict, operation: str) -> str:
        """格式化成功訊息"""
        assignments_count = result.get('assignments_synced', 0)
        
        if operation.startswith('assignment_'):
            return f"✅ 作業同步完成！已更新 {assignments_count} 個作業。"
        else:
            return f"✅ 課程同步完成！已同步 {assignments_count} 個作業。"
    
    @classmethod
    def _format_error_message(cls, result: Dict, operation: str) -> str:
        """格式化錯誤訊息"""
        error_msg = result.get('message', '未知錯誤')
        
        if operation.startswith('assignment_'):
            return f"❌ 作業同步失敗：{error_msg}"
        else:
            return f"❌ 課程同步失敗：{error_msg}"
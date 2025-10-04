"""
Google Calendar 同步服務
提供 Google Calendar API 的基本功能
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.utils import timezone
from user.models import LineProfile
from user.utils import get_valid_google_credentials

logger = logging.getLogger(__name__)


class CalendarSyncError(Exception):
    """Calendar 同步過程中的錯誤"""
    pass


class CalendarSyncService:
    """Google Calendar 同步服務"""
    
    def __init__(self, line_user_id: str):
        """
        初始化 Calendar 同步服務
        
        Args:
            line_user_id: LINE 使用者 ID
            
        Raises:
            CalendarSyncError: 當無法獲取使用者或憑證時
        """
        try:
            self.user = LineProfile.objects.get(line_user_id=line_user_id)
            self.credentials = get_valid_google_credentials(self.user)
            self.service = None
            self._initialize_service()
            logger.info(f"CalendarSyncService initialized for user: {line_user_id}")
        except LineProfile.DoesNotExist:
            raise CalendarSyncError(f"使用者不存在: {line_user_id}")
        except Exception as e:
            logger.error(f"Failed to initialize CalendarSyncService for {line_user_id}: {str(e)}")
            raise CalendarSyncError(f"無法初始化 Calendar 同步服務: {str(e)}")
    
    def _initialize_service(self):
        """初始化 Google Calendar API 服務"""
        try:
            # 使用已經驗證和刷新的憑證
            self.service = build('calendar', 'v3', credentials=self.credentials, cache_discovery=False)
            logger.info("Calendar service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Calendar service: {str(e)}")
            self.service = None
    
    def test_connection(self) -> Dict[str, Any]:
        """
        測試 Google Calendar 連接
        
        Returns:
            Dict: 測試結果
        """
        try:
            if not self.service:
                return {
                    'success': False,
                    'message': 'Calendar service not initialized',
                    'error_code': 'SERVICE_NOT_INITIALIZED'
                }
            
            # 嘗試獲取日曆列表來測試連接
            calendars_result = self.service.calendarList().list().execute()
            calendars = calendars_result.get('items', [])
            
            return {
                'success': True,
                'message': 'Calendar connection successful',
                'calendar_count': len(calendars)
            }
            
        except HttpError as e:
            logger.error(f"HTTP error testing calendar connection: {str(e)}")
            return {
                'success': False,
                'message': f'HTTP error: {e.resp.status}',
                'error_code': f'HTTP_{e.resp.status}'
            }
        except Exception as e:
            logger.error(f"Error testing calendar connection: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def get_calendars(self) -> List[Dict[str, Any]]:
        """
        獲取用戶的日曆列表
        
        Returns:
            List: 日曆列表
        """
        try:
            if not self.service:
                logger.warning("Calendar service not initialized")
                return []
            
            calendars_result = self.service.calendarList().list().execute()
            calendars = calendars_result.get('items', [])
            
            formatted_calendars = []
            for calendar in calendars:
                formatted_calendar = {
                    'id': calendar.get('id', ''),
                    'summary': calendar.get('summary', ''),
                    'description': calendar.get('description', ''),
                    'primary': calendar.get('primary', False),
                    'accessRole': calendar.get('accessRole', ''),
                    'backgroundColor': calendar.get('backgroundColor', ''),
                    'foregroundColor': calendar.get('foregroundColor', ''),
                    'selected': calendar.get('selected', False)
                }
                formatted_calendars.append(formatted_calendar)
            
            logger.info(f"Retrieved {len(formatted_calendars)} calendars")
            return formatted_calendars
            
        except HttpError as e:
            logger.error(f"HTTP error getting calendars: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error getting calendars: {str(e)}")
            return []
    
    def get_events(self, calendar_id: str = 'primary', time_min: Optional[str] = None, 
                   time_max: Optional[str] = None, max_results: int = 10) -> Dict[str, Any]:
        """
        獲取日曆事件
        
        Args:
            calendar_id: 日曆 ID
            time_min: 開始時間 (ISO format)
            time_max: 結束時間 (ISO format)
            max_results: 最大結果數量
            
        Returns:
            Dict: 事件列表和狀態
        """
        try:
            if not self.service:
                return {
                    'success': False,
                    'message': 'Calendar service not initialized',
                    'events': []
                }
            
            # 設置預設時間範圍（如果未提供）
            if not time_min:
                time_min = timezone.now().isoformat()
            if not time_max:
                # 預設獲取未來30天的事件
                time_max = (timezone.now() + timedelta(days=30)).isoformat()
            
            # 調用 Google Calendar API
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            logger.info(f"Retrieved {len(events)} events from calendar {calendar_id}")
            return {
                'success': True,
                'events': events,
                'total_count': len(events)
            }
            
        except HttpError as e:
            logger.error(f"HTTP error getting events: {str(e)}")
            return {
                'success': False,
                'message': f'HTTP error: {e.resp.status}',
                'events': [],
                'error_code': f'HTTP_{e.resp.status}'
            }
        except Exception as e:
            logger.error(f"Error getting events: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'events': [],
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def create_event(self, calendar_id: str = 'primary', summary: str = '', 
                     description: str = '', start_datetime: str = '', 
                     end_datetime: str = '', location: str = '', 
                     attendees: List[str] = None) -> Dict[str, Any]:
        """
        創建日曆事件
        
        Args:
            calendar_id: 日曆 ID
            summary: 事件標題
            description: 事件描述
            start_datetime: 開始時間
            end_datetime: 結束時間
            location: 地點
            attendees: 參與者郵箱列表
            
        Returns:
            Dict: 創建結果
        """
        try:
            if not self.service:
                return {
                    'success': False,
                    'message': 'Calendar service not initialized'
                }
            
            # 構建事件數據
            event_data = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_datetime,
                    'timeZone': 'Asia/Taipei',
                },
                'end': {
                    'dateTime': end_datetime,
                    'timeZone': 'Asia/Taipei',
                },
                'location': location,
            }
            
            # 添加參與者
            if attendees:
                event_data['attendees'] = [{'email': email} for email in attendees]
            
            # 創建事件
            event = self.service.events().insert(
                calendarId=calendar_id,
                body=event_data
            ).execute()
            
            logger.info(f"Created event: {event.get('id')}")
            return {
                'success': True,
                'event': event,
                'message': 'Event created successfully'
            }
            
        except HttpError as e:
            logger.error(f"HTTP error creating event: {str(e)}")
            return {
                'success': False,
                'message': f'HTTP error: {e.resp.status}',
                'error_code': f'HTTP_{e.resp.status}'
            }
        except Exception as e:
            logger.error(f"Error creating event: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def update_event(self, calendar_id: str = 'primary', event_id: str = '', 
                     **kwargs) -> Dict[str, Any]:
        """
        更新日曆事件
        
        Args:
            calendar_id: 日曆 ID
            event_id: 事件 ID
            **kwargs: 要更新的字段
            
        Returns:
            Dict: 更新結果
        """
        try:
            if not self.service:
                return {
                    'success': False,
                    'message': 'Calendar service not initialized'
                }
            
            # 先獲取現有事件
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # 更新字段
            if 'summary' in kwargs:
                event['summary'] = kwargs['summary']
            if 'description' in kwargs:
                event['description'] = kwargs['description']
            if 'start_datetime' in kwargs:
                event['start'] = {
                    'dateTime': kwargs['start_datetime'],
                    'timeZone': 'Asia/Taipei',
                }
            if 'end_datetime' in kwargs:
                event['end'] = {
                    'dateTime': kwargs['end_datetime'],
                    'timeZone': 'Asia/Taipei',
                }
            if 'location' in kwargs:
                event['location'] = kwargs['location']
            if 'attendees' in kwargs:
                event['attendees'] = [{'email': email} for email in kwargs['attendees']]
            
            # 更新事件
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"Updated event: {event_id}")
            return {
                'success': True,
                'event': updated_event,
                'message': 'Event updated successfully'
            }
            
        except HttpError as e:
            logger.error(f"HTTP error updating event: {str(e)}")
            return {
                'success': False,
                'message': f'HTTP error: {e.resp.status}',
                'error_code': f'HTTP_{e.resp.status}'
            }
        except Exception as e:
            logger.error(f"Error updating event: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def delete_event(self, calendar_id: str = 'primary', event_id: str = '') -> Dict[str, Any]:
        """
        刪除日曆事件
        
        Args:
            calendar_id: 日曆 ID
            event_id: 事件 ID
            
        Returns:
            Dict: 刪除結果
        """
        try:
            if not self.service:
                return {
                    'success': False,
                    'message': 'Calendar service not initialized'
                }
            
            # 刪除事件
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"Deleted event: {event_id}")
            return {
                'success': True,
                'message': 'Event deleted successfully'
            }
            
        except HttpError as e:
            logger.error(f"HTTP error deleting event: {str(e)}")
            return {
                'success': False,
                'message': f'HTTP error: {e.resp.status}',
                'error_code': f'HTTP_{e.resp.status}'
            }
        except Exception as e:
            logger.error(f"Error deleting event: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def manage_attendees(self, calendar_id: str = 'primary', event_id: str = '', 
                        attendees: List[str] = None, 
                        attendees_to_remove: List[str] = None) -> Dict[str, Any]:
        """
        管理事件參與者
        
        Args:
            calendar_id: 日曆 ID
            event_id: 事件 ID
            attendees: 要添加的參與者郵箱列表
            attendees_to_remove: 要移除的參與者郵箱列表
            
        Returns:
            Dict: 管理結果
        """
        try:
            if not self.service:
                return {
                    'success': False,
                    'message': 'Calendar service not initialized'
                }
            
            # 獲取現有事件
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            current_attendees = event.get('attendees', [])
            current_emails = {attendee.get('email') for attendee in current_attendees}
            
            # 添加新參與者
            if attendees:
                for email in attendees:
                    if email not in current_emails:
                        current_attendees.append({'email': email})
            
            # 移除參與者
            if attendees_to_remove:
                current_attendees = [
                    attendee for attendee in current_attendees 
                    if attendee.get('email') not in attendees_to_remove
                ]
            
            # 更新事件
            event['attendees'] = current_attendees
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"Managed attendees for event: {event_id}")
            return {
                'success': True,
                'event': updated_event,
                'message': 'Attendees managed successfully'
            }
            
        except HttpError as e:
            logger.error(f"HTTP error managing attendees: {str(e)}")
            return {
                'success': False,
                'message': f'HTTP error: {e.resp.status}',
                'error_code': f'HTTP_{e.resp.status}'
            }
        except Exception as e:
            logger.error(f"Error managing attendees: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def sync_events_for_user(self, line_user_id: str, calendar_ids: List[str]) -> Dict[str, Any]:
        """
        為用戶同步事件（佔位符實現）
        
        Args:
            line_user_id: LINE 用戶 ID
            calendar_ids: 要同步的日曆 ID 列表
            
        Returns:
            Dict: 同步結果
        """
        # 這是一個佔位符實現，實際應該將事件同步到本地數據庫
        try:
            total_synced = 0
            total_created = 0
            total_updated = 0
            
            for calendar_id in calendar_ids:
                events_result = self.get_events(calendar_id=calendar_id)
                if events_result.get('success'):
                    events = events_result.get('events', [])
                    total_synced += len(events)
                    # 這裡應該實現實際的數據庫同步邏輯
                    total_created += len(events)  # 簡化實現
            
            return {
                'success': True,
                'total_synced': total_synced,
                'total_created': total_created,
                'total_updated': total_updated,
                'message': 'Events synced successfully'
            }
            
        except Exception as e:
            logger.error(f"Error syncing events for user {line_user_id}: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'total_synced': 0,
                'total_created': 0,
                'total_updated': 0
            }
    
    def _selective_sync_events(self, selected_event_ids: List[str]) -> Dict[str, Any]:
        """
        選擇性同步指定的 Google Calendar 事件
        
        Args:
            selected_event_ids: 要同步的事件 ID 列表
            
        Returns:
            Dict: 同步結果
        """
        try:
            synced_events = []
            errors = []
            
            logger.info(f"開始選擇性同步 {len(selected_event_ids)} 個 Calendar 事件")
            
            for event_id in selected_event_ids:
                try:
                    # 從 Google Calendar API 獲取事件詳細資訊
                    event = self.service.events().get(
                        calendarId='primary',
                        eventId=event_id
                    ).execute()
                    
                    # 這裡應該實現將事件同步到本地數據庫的邏輯
                    # 目前只是記錄同步的事件
                    synced_events.append({
                        'id': event.get('id'),
                        'summary': event.get('summary', ''),
                        'start': event.get('start', {}),
                        'end': event.get('end', {}),
                        'description': event.get('description', ''),
                        'location': event.get('location', '')
                    })
                    
                    logger.info(f"成功同步事件: {event.get('summary', event_id)}")
                    
                except HttpError as e:
                    error_msg = f"HTTP 錯誤同步事件 {event_id}: {e.resp.status}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                except Exception as e:
                    error_msg = f"同步事件 {event_id} 失敗: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            success = len(synced_events) > 0
            
            logger.info(f"Calendar 選擇性同步完成: {len(synced_events)} 個事件成功, {len(errors)} 個錯誤")
            
            return {
                'success': success,
                'events_synced': len(synced_events),
                'synced_events': synced_events,
                'errors': errors,
                'total_selected': len(selected_event_ids)
            }
            
        except Exception as e:
            logger.error(f"Calendar 選擇性同步失敗: {str(e)}")
            return {
                'success': False,
                'events_synced': 0,
                'synced_events': [],
                'errors': [str(e)],
                'total_selected': len(selected_event_ids)
            }

    def get_upcoming_events(self, line_user_id: str, days: int = 7) -> List[Any]:
        """
        獲取即將到來的事件（佔位符實現）
        
        Args:
            line_user_id: LINE 用戶 ID
            days: 天數範圍
            
        Returns:
            List: 事件列表
        """
        # 這是一個佔位符實現，實際應該從本地數據庫查詢
        try:
            time_min = timezone.now().isoformat()
            time_max = (timezone.now() + timedelta(days=days)).isoformat()
            
            events_result = self.get_events(
                calendar_id='primary',
                time_min=time_min,
                time_max=time_max,
                max_results=50
            )
            
            if events_result.get('success'):
                return events_result.get('events', [])
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting upcoming events for user {line_user_id}: {str(e)}")
            return []
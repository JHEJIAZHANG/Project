"""
預覽同步服務
獲取 Google 服務資料但不寫入資料庫，供使用者預覽和選擇
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
from django.utils import timezone
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from user.models import LineProfile
from user.utils import get_valid_google_credentials
from api_v2.models import CourseV2, AssignmentV2
from services.error_handler import APIErrorHandler, retry_on_error
from services.classroom_sync_service import ClassroomSyncService, ClassroomSyncError

from line_bot.utils_encoding import create_google_classroom_assignment_url, create_google_classroom_course_url

logger = logging.getLogger(__name__)


class PreviewSyncService:
    """預覽同步服務 - 獲取資料但不寫入資料庫"""
    
    def __init__(self, line_user_id: str):
        """
        初始化預覽同步服務
        
        Args:
            line_user_id: LINE 使用者 ID
        """
        try:
            self.line_user_id = line_user_id
            self.user = LineProfile.objects.get(line_user_id=line_user_id)
            self.credentials = get_valid_google_credentials(self.user)
            self.classroom_service = build('classroom', 'v1', credentials=self.credentials, cache_discovery=False)
            logger.info(f"PreviewSyncService initialized for user: {line_user_id}")
        except LineProfile.DoesNotExist:
            raise ClassroomSyncError(f"使用者不存在: {line_user_id}")
        except Exception as e:
            logger.error(f"Failed to initialize PreviewSyncService for {line_user_id}: {str(e)}")
            raise ClassroomSyncError(f"無法初始化預覽同步服務: {str(e)}")
    
    def preview_all_sync_data(self) -> Dict:
        """
        預覽 Google Classroom 的同步資料
        
        Returns:
            Dict: 預覽資料
            {
                'success': bool,
                'classroom': {
                    'courses': List[Dict],
                    'total_assignments': int
                },
                'existing_data': {
                    'courses': List[str],  # 已存在的課程 ID
                    'assignments': List[str]  # 已存在的作業 ID
                },
                'errors': List[str]
            }
        """
        logger.info(f"Starting preview sync for user: {self.line_user_id}")
        
        result = {
            'success': True,
            'classroom': {
                'courses': [],
                'total_assignments': 0
            },
            'existing_data': {
                'courses': [],
                'assignments': []
            },
            'errors': []
        }
        
        try:
            # 1. 預覽 Google Classroom 資料
            classroom_result = self._preview_classroom_data()
            result['classroom'] = classroom_result
            
            # 2. 獲取現有資料
            existing_data = self._get_existing_data()
            result['existing_data'] = existing_data
            
            logger.info(f"Preview sync completed for user: {self.line_user_id}")
            
        except Exception as e:
            error_msg = f"預覽同步過程發生錯誤: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
            result['success'] = False
        
        return result
    
    def _preview_classroom_data(self) -> Dict:
        """
        預覽 Google Classroom 資料
        
        Returns:
            Dict: Classroom 預覽資料
        """
        try:
            # 獲取所有課程
            courses_response = self.classroom_service.courses().list().execute()
            courses = courses_response.get('courses', [])
            
            preview_courses = []
            total_assignments = 0
            
            for classroom_course in courses:
                google_course_id = classroom_course['id']
                
                # 獲取課程作業
                coursework_response = self.classroom_service.courses().courseWork().list(
                    courseId=google_course_id
                ).execute()
                coursework_list = coursework_response.get('courseWork', [])
                
                # 處理作業資料
                assignments = []
                for coursework in coursework_list:
                    assignment_data = {
                        'id': coursework['id'],
                        'title': coursework['title'],
                        'description': coursework.get('description', ''),
                        'due_date': self._parse_due_date(
                            coursework.get('dueDate'),
                            coursework.get('dueTime')
                        ),
                        'google_classroom_url': create_google_classroom_assignment_url(
                            google_course_id, coursework['id']
                        ),
                        'state': coursework.get('state', 'PUBLISHED')
                    }
                    assignments.append(assignment_data)
                
                total_assignments += len(assignments)
                
                # 課程資料
                course_data = {
                    'google_course_id': google_course_id,
                    'name': classroom_course['name'],
                    'description': classroom_course.get('description', ''),
                    'instructor': self._get_teacher_name(classroom_course.get('ownerId', '')),
                    'google_classroom_url': create_google_classroom_course_url(google_course_id),
                    'assignments': assignments,
                    'assignments_count': len(assignments)
                }
                preview_courses.append(course_data)
            
            return {
                'courses': preview_courses,
                'total_assignments': total_assignments
            }
            
        except HttpError as e:
            error_info = APIErrorHandler.handle_google_api_error(e)
            raise Exception(f"Google Classroom API 錯誤: {error_info['message']}")
        except Exception as e:
            raise Exception(f"預覽 Classroom 資料失敗: {str(e)}")
    
    def _get_existing_data(self) -> Dict:
        """
        獲取使用者現有的資料
        
        Returns:
            Dict: 現有資料
        """
        try:
            # 獲取現有課程
            existing_courses = list(CourseV2.objects.filter(
                user=self.user,
                is_google_classroom=True
            ).values_list('google_classroom_id', flat=True))
            
            # 獲取現有作業
            existing_assignments = list(AssignmentV2.objects.filter(
                course__user=self.user,
                course__is_google_classroom=True
            ).values_list('google_classroom_id', flat=True))
            
            return {
                'courses': existing_courses,
                'assignments': existing_assignments
            }
            
        except Exception as e:
            logger.error(f"獲取現有資料失敗: {str(e)}")
            return {
                'courses': [],
                'assignments': []
            }
    
    def _get_teacher_name(self, owner_id: str) -> str:
        """
        獲取教師姓名
        
        Args:
            owner_id: 教師 ID
            
        Returns:
            str: 教師姓名
        """
        try:
            if not owner_id:
                return "未知教師"
            
            # 獲取教師資訊
            teacher_profile = self.classroom_service.userProfiles().get(userId=owner_id).execute()
            return teacher_profile.get('name', {}).get('fullName', '未知教師')
            
        except Exception as e:
            logger.warning(f"無法獲取教師姓名 {owner_id}: {str(e)}")
            return "未知教師"
    
    def _parse_due_date(self, due_date_dict: Optional[Dict], due_time_dict: Optional[Dict]) -> Optional[str]:
        """
        解析到期日期
        
        Args:
            due_date_dict: 到期日期字典
            due_time_dict: 到期時間字典
            
        Returns:
            Optional[str]: ISO 格式的日期時間字串
        """
        try:
            if not due_date_dict:
                return None
            
            year = due_date_dict.get('year')
            month = due_date_dict.get('month')
            day = due_date_dict.get('day')
            
            if not all([year, month, day]):
                return None
            
            # 處理時間
            hour = 23
            minute = 59
            if due_time_dict:
                hour = due_time_dict.get('hours', 23)
                minute = due_time_dict.get('minutes', 59)
            
            due_datetime = datetime(year, month, day, hour, minute)
            return due_datetime.isoformat()
            
        except Exception as e:
            logger.warning(f"解析到期日期失敗: {str(e)}")
            return None
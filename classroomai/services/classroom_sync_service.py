"""
Google Classroom 同步服務
處理 Classroom 資料與本地 V2 資料的同步
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, time
from django.utils import timezone
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from user.models import LineProfile
from user.utils import get_valid_google_credentials
from api_v2.models import CourseV2, AssignmentV2, CourseScheduleV2
from .error_handler import APIErrorHandler, retry_on_error
from line_bot.utils_encoding import create_google_classroom_assignment_url, create_google_classroom_course_url

logger = logging.getLogger(__name__)


class ClassroomSyncError(Exception):
    """同步過程中的錯誤"""
    pass


class ClassroomSyncService:
    """Google Classroom 同步服務"""
    
    def __init__(self, line_user_id: str):
        """
        初始化同步服務
        
        Args:
            line_user_id: LINE 使用者 ID
            
        Raises:
            ClassroomSyncError: 當無法獲取使用者或憑證時
        """
        try:
            self.user = LineProfile.objects.get(line_user_id=line_user_id)
            self.credentials = get_valid_google_credentials(self.user)
            self.classroom_service = build('classroom', 'v1', credentials=self.credentials, cache_discovery=False)
            logger.info(f"ClassroomSyncService initialized for user: {line_user_id}")
        except LineProfile.DoesNotExist:
            raise ClassroomSyncError(f"使用者不存在: {line_user_id}")
        except Exception as e:
            logger.error(f"Failed to initialize ClassroomSyncService for {line_user_id}: {str(e)}")
            raise ClassroomSyncError(f"無法初始化同步服務: {str(e)}")
    
    def sync_all_courses(self) -> Dict:
        """
        全量同步所有 Classroom 課程和作業到 V2
        
        Returns:
            Dict: 同步結果統計
            {
                'success': bool,
                'courses_synced': int,
                'assignments_synced': int,
                'errors': List[str]
            }
        """
        logger.info(f"Starting full sync for user: {self.user.line_user_id}")
        
        result = {
            'success': True,
            'courses_synced': 0,
            'assignments_synced': 0,
            'errors': []
        }
        
        try:
            # 獲取所有 Classroom 課程（使用重試機制）
            courses_response = self._get_courses_with_retry()
            courses = courses_response.get('courses', [])
            logger.info(f"Found {len(courses)} courses to sync")
            
            for classroom_course in courses:
                try:
                    # 同步單一課程
                    course_result = self._sync_single_course_data(classroom_course)
                    result['courses_synced'] += 1
                    result['assignments_synced'] += course_result['assignments_synced']
                    
                except Exception as e:
                    error_msg = f"同步課程失敗 {classroom_course.get('name', 'Unknown')}: {str(e)}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
                    result['success'] = False
            
            logger.info(f"Full sync completed. Courses: {result['courses_synced']}, Assignments: {result['assignments_synced']}")
            
        except HttpError as e:
            error_info = APIErrorHandler.handle_google_api_error(e)
            result['errors'].append(error_info['message'])
            result['success'] = False
        except Exception as e:
            error_msg = f"同步過程發生未預期錯誤: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
            result['success'] = False
        
        return result
    
    def sync_single_course(self, google_course_id: str) -> Dict:
        """
        同步單一課程的作業
        
        Args:
            google_course_id: Google Classroom 課程 ID
            
        Returns:
            Dict: 同步結果
        """
        logger.info(f"Starting single course sync: {google_course_id}")
        
        result = {
            'success': True,
            'course_id': google_course_id,
            'assignments_synced': 0,
            'errors': []
        }
        
        try:
            # 獲取課程資訊（使用重試機制）
            classroom_course = self._get_course_with_retry(google_course_id)
            
            # 同步課程資料
            course_result = self._sync_single_course_data(classroom_course)
            result['assignments_synced'] = course_result['assignments_synced']
            
            logger.info(f"Single course sync completed: {google_course_id}, Assignments: {result['assignments_synced']}")
            
        except HttpError as e:
            error_info = APIErrorHandler.handle_google_api_error(e)
            result['errors'].append(error_info['message'])
            result['success'] = False
        except Exception as e:
            error_msg = f"同步課程時發生錯誤: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
            result['success'] = False
        
        return result

    def _selective_sync_courses(self, selected_course_ids: List[str]) -> Dict:
        """
        選擇性同步指定的課程
        
        Args:
            selected_course_ids: 選擇的 Google Classroom 課程 ID 列表
            
        Returns:
            Dict: 同步結果統計
        """
        logger.info(f"Starting selective sync for {len(selected_course_ids)} courses")
        
        result = {
            'success': True,
            'courses_synced': 0,
            'assignments_synced': 0,
            'errors': []
        }
        
        try:
            for google_course_id in selected_course_ids:
                try:
                    # 獲取課程資訊
                    classroom_course = self._get_course_with_retry(google_course_id)
                    
                    # 同步單一課程
                    course_result = self._sync_single_course_data(classroom_course)
                    result['courses_synced'] += 1
                    result['assignments_synced'] += course_result['assignments_synced']
                    
                    logger.info(f"Selective sync completed for course: {google_course_id}")
                    
                except Exception as e:
                    error_msg = f"選擇性同步課程失敗 {google_course_id}: {str(e)}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
                    result['success'] = False
            
            logger.info(f"Selective sync completed. Courses: {result['courses_synced']}, Assignments: {result['assignments_synced']}")
            
        except Exception as e:
            error_msg = f"選擇性同步過程發生未預期錯誤: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
            result['success'] = False
        
        return result

    def _sync_single_course_data(self, classroom_course: Dict) -> Dict:
        """
        同步單一課程的資料（內部方法）
        
        Args:
            classroom_course: Classroom 課程資料
            
        Returns:
            Dict: 同步結果
        """
        google_course_id = classroom_course['id']
        
        # 生成 Google Classroom 課程連結（使用編碼）
        classroom_url = create_google_classroom_course_url(google_course_id)
        
        # 獲取教師真實姓名
        instructor_name = self._get_teacher_name(classroom_course.get('ownerId', ''))
        
        # 創建或更新 CourseV2
        course_v2, created = CourseV2.objects.update_or_create(
            google_classroom_id=google_course_id,
            user=self.user,
            defaults={
                'title': classroom_course['name'],
                'description': classroom_course.get('description', ''),
                'instructor': instructor_name,
                'is_google_classroom': True,
                'google_classroom_url': classroom_url,
            }
        )
        
        if created:
            logger.info(f"Created new CourseV2: {course_v2.title}")
        else:
            logger.info(f"Updated CourseV2: {course_v2.title}")
        
        # 處理課程時間問題
        self._handle_course_schedule(course_v2, classroom_course)
        
        # 同步課程作業
        assignments_synced = self._sync_course_assignments(google_course_id, course_v2)
        
        return {
            'course_v2': course_v2,
            'assignments_synced': assignments_synced
        }
    
    def _sync_course_assignments(self, google_course_id: str, course_v2: CourseV2) -> int:
        """
        同步課程的所有作業
        
        Args:
            google_course_id: Google Classroom 課程 ID
            course_v2: 對應的 CourseV2 物件
            
        Returns:
            int: 同步的作業數量
        """
        try:
            # 獲取課程作業（使用重試機制）
            coursework_response = self._get_coursework_with_retry(google_course_id)
            
            courseworks = coursework_response.get('courseWork', [])
            assignments_synced = 0
            
            for coursework in courseworks:
                try:
                    # 解析截止日期
                    due_date = self._parse_due_date(coursework.get('dueDate'), coursework.get('dueTime'))
                    
                    # 檢查作業提交狀態
                    assignment_status = self._get_assignment_submission_status(
                        google_course_id, coursework['id'], due_date
                    )
                    
                    # 生成 Google Classroom 作業連結（使用編碼）
                    assignment_url = create_google_classroom_assignment_url(google_course_id, coursework['id'])
                    
                    # 創建或更新 AssignmentV2
                    assignment_v2, created = AssignmentV2.objects.update_or_create(
                        google_coursework_id=coursework['id'],
                        user=self.user,
                        defaults={
                            'course': course_v2,
                            'title': coursework['title'],
                            'description': coursework.get('description', ''),
                            'due_date': due_date,
                            'type': 'assignment',
                            'status': assignment_status,
                            'google_classroom_url': assignment_url,
                        }
                    )
                    
                    assignments_synced += 1
                    
                    if created:
                        logger.debug(f"Created new AssignmentV2: {assignment_v2.title} with status: {assignment_status}")
                    else:
                        logger.debug(f"Updated AssignmentV2: {assignment_v2.title} with status: {assignment_status}")
                        
                except Exception as e:
                    logger.error(f"Failed to sync assignment {coursework.get('title', 'Unknown')}: {str(e)}")
            
            logger.info(f"Synced {assignments_synced} assignments for course: {course_v2.title}")
            return assignments_synced
            
        except HttpError as e:
            error_info = APIErrorHandler.handle_google_api_error(e)
            logger.error(f"Failed to fetch coursework for {google_course_id}: {error_info['message']}")
            return 0
    
    def _handle_course_schedule(self, course_v2: CourseV2, classroom_course: Dict) -> None:
        """
        處理課程時間問題 - Google Classroom 沒有時間資訊
        
        Args:
            course_v2: CourseV2 物件
            classroom_course: Classroom 課程資料
        """
        # 檢查是否已有手動設定的時間
        existing_manual_schedules = course_v2.schedules.filter(schedule_source='manual')
        if existing_manual_schedules.exists():
            logger.debug(f"Course {course_v2.title} already has manual schedules, skipping schedule handling")
            return
        
        # 不再自動創建預設時間，讓使用者自行決定是否要設定課程時間
        logger.debug(f"Course {course_v2.title} imported without schedule - user can manually set schedule if needed")
    
    def _create_default_schedule_placeholder(self, course_v2: CourseV2) -> None:
        """
        為沒有時間資訊的 Classroom 課程創建預設時間佔位符
        
        Args:
            course_v2: CourseV2 物件
        """
        CourseScheduleV2.objects.create(
            course=course_v2,
            day_of_week=1,  # 預設週二
            start_time=time(9, 0),  # 預設上午 9 點
            end_time=time(10, 30),   # 預設 1.5 小時
            location='待設定',
            schedule_source='inferred',
            is_default_schedule=True
        )
    
    def _get_teacher_name(self, owner_id: str) -> str:
        """
        獲取教師的真實姓名
        
        Args:
            owner_id: Google Classroom 課程擁有者 ID
            
        Returns:
            str: 教師真實姓名，如果無法獲取則返回預設值
        """
        if not owner_id:
            return "老師"
        
        try:
            # 使用 Google Classroom API 獲取用戶資料
            teacher_profile = self.classroom_service.userProfiles().get(userId=owner_id).execute()
            teacher_name = teacher_profile.get("name", {}).get("fullName", "")
            
            if teacher_name:
                logger.info(f"Successfully retrieved teacher name: {teacher_name} for owner_id: {owner_id}")
                return teacher_name
            else:
                logger.warning(f"Teacher name not found in profile for owner_id: {owner_id}")
                return "老師"
                
        except HttpError as e:
            logger.warning(f"Failed to get teacher profile for owner_id {owner_id}: {e}")
            return "老師"
        except Exception as e:
            logger.error(f"Unexpected error getting teacher name for owner_id {owner_id}: {e}")
            return "老師"
    
    def _parse_due_date(self, due_date_dict: Optional[Dict], due_time_dict: Optional[Dict]) -> datetime:
        """
        解析 Classroom 的截止日期格式
        
        Args:
            due_date_dict: Classroom 日期格式 {'year': 2024, 'month': 9, 'day': 30}
            due_time_dict: Classroom 時間格式 {'hours': 23, 'minutes': 59}
            
        Returns:
            datetime: 解析後的截止日期
        """
        if not due_date_dict:
            # 如果沒有截止日期，設定為一週後
            return timezone.now() + timezone.timedelta(days=7)
        
        year = due_date_dict.get('year', timezone.now().year)
        month = due_date_dict.get('month', 1)
        day = due_date_dict.get('day', 1)
        
        if due_time_dict:
            hour = due_time_dict.get('hours', 23)
            minute = due_time_dict.get('minutes', 59)
        else:
            hour, minute = 23, 59  # 預設為當天結束
        
        try:
            return timezone.make_aware(datetime(year, month, day, hour, minute))
        except ValueError as e:
            logger.warning(f"Invalid date format, using default: {str(e)}")
            return timezone.now() + timezone.timedelta(days=7) 
   # Google API 呼叫方法（帶重試機制）
    
    @retry_on_error(max_retries=3, delay=1.0, backoff=2.0)
    def _get_courses_with_retry(self) -> Dict:
        """
        獲取課程列表（帶重試機制）
        只獲取用戶作為學生身份的活躍課程，並過濾當前學期的課程
        
        Returns:
            Dict: Google Classroom API 回應
        """
        # 只獲取 ACTIVE 狀態的課程，排除 ARCHIVED 等過期課程
        response = self.classroom_service.courses().list(
            studentId='me',
            courseStates=['ACTIVE']
        ).execute()
        
        # 進一步過濾當前學期的課程（過去6個月內創建的課程）
        current_courses = []
        current_time = timezone.now()
        six_months_ago = current_time - timezone.timedelta(days=180)
        
        for course in response.get('courses', []):
            try:
                # 解析課程創建時間
                creation_time_str = course.get('creationTime')
                if creation_time_str:
                    # Google API 返回的時間格式為 RFC 3339
                    from dateutil import parser
                    creation_time = parser.parse(creation_time_str)
                    
                    # 只保留最近6個月內創建的課程
                    if creation_time >= six_months_ago:
                        current_courses.append(course)
                    else:
                        logger.info(f"Filtering out old course: {course.get('name')} (created: {creation_time_str})")
                else:
                    # 如果沒有創建時間，保留課程（可能是較舊的API版本）
                    current_courses.append(course)
            except Exception as e:
                logger.warning(f"Error parsing course creation time for {course.get('name', 'Unknown')}: {str(e)}")
                # 解析失敗時保留課程
                current_courses.append(course)
        
        logger.info(f"Filtered courses: {len(current_courses)} out of {len(response.get('courses', []))} total courses")
        
        # 返回過濾後的結果
        response['courses'] = current_courses
        return response
    
    @retry_on_error(max_retries=3, delay=1.0, backoff=2.0)
    def _get_course_with_retry(self, course_id: str) -> Dict:
        """
        獲取單一課程資訊（帶重試機制）
        
        Args:
            course_id: 課程 ID
            
        Returns:
            Dict: Google Classroom API 回應
        """
        return self.classroom_service.courses().get(id=course_id).execute()
    
    @retry_on_error(max_retries=3, delay=1.0, backoff=2.0)
    def _get_coursework_with_retry(self, course_id: str) -> Dict:
        """
        獲取課程作業列表（帶重試機制）
        
        Args:
            course_id: 課程 ID
            
        Returns:
            Dict: Google Classroom API 回應
        """
        return self.classroom_service.courses().courseWork().list(
            courseId=course_id,
            courseWorkStates=['PUBLISHED']
        ).execute()
    
    def get_api_quota_status(self) -> Dict:
        """
        獲取 API 配額狀態
        
        Returns:
            Dict: API 配額資訊
        """
        try:
            # 嘗試一個簡單的 API 呼叫來檢查配額狀態
            self.classroom_service.courses().list(pageSize=1).execute()
            
            return {
                'status': 'healthy',
                'message': 'API 配額正常',
                'timestamp': timezone.now().isoformat()
            }
        except HttpError as e:
            if e.resp.status == 429:
                return {
                    'status': 'quota_exceeded',
                    'message': 'API 配額已用盡，請稍後再試',
                    'timestamp': timezone.now().isoformat()
                }
            else:
                error_info = APIErrorHandler.handle_google_api_error(e)
                return {
                    'status': 'error',
                    'message': error_info['message'],
                    'timestamp': timezone.now().isoformat()
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'檢查 API 狀態時發生錯誤: {str(e)}',
                'timestamp': timezone.now().isoformat()
            }
    
    def validate_permissions(self) -> Dict:
        """
        驗證 Google Classroom 權限
        
        Returns:
            Dict: 權限驗證結果
        """
        permissions = {
            'courses_read': False,
            'coursework_read': False,
            'profile_read': False
        }
        
        errors = []
        
        try:
            # 測試課程讀取權限
            self.classroom_service.courses().list(pageSize=1).execute()
            permissions['courses_read'] = True
        except HttpError as e:
            error_info = APIErrorHandler.handle_google_api_error(e)
            errors.append(f"課程讀取權限: {error_info['message']}")
        
        try:
            # 測試個人資料讀取權限
            self.classroom_service.userProfiles().get(userId='me').execute()
            permissions['profile_read'] = True
        except HttpError as e:
            error_info = APIErrorHandler.handle_google_api_error(e)
            errors.append(f"個人資料讀取權限: {error_info['message']}")
        
        # 如果有課程，測試作業讀取權限
        if permissions['courses_read']:
            try:
                courses_response = self.classroom_service.courses().list(pageSize=1).execute()
                courses = courses_response.get('courses', [])
                
                if courses:
                    course_id = courses[0]['id']
                    self.classroom_service.courses().courseWork().list(
                        courseId=course_id,
                        pageSize=1
                    ).execute()
                    permissions['coursework_read'] = True
                else:
                    permissions['coursework_read'] = True  # 沒有課程時假設有權限
            except HttpError as e:
                error_info = APIErrorHandler.handle_google_api_error(e)
                errors.append(f"作業讀取權限: {error_info['message']}")
        
        all_permissions_valid = all(permissions.values())
        
        return {
            'valid': all_permissions_valid,
            'permissions': permissions,
            'errors': errors,
            'message': '所有權限正常' if all_permissions_valid else '部分權限缺失'
        }
    
    def _get_assignment_submission_status(self, course_id: str, coursework_id: str, due_date: Optional[datetime]) -> str:
        """
        檢查作業的提交狀態
        
        Args:
            course_id: Google Classroom 課程 ID
            coursework_id: 作業 ID
            due_date: 作業截止日期
            
        Returns:
            str: 作業狀態 ('completed', 'pending', 'overdue')
        """
        try:
            # 獲取學生提交狀態
            submissions_response = self.classroom_service.courses().courseWork().studentSubmissions().list(
                courseId=course_id,
                courseWorkId=coursework_id,
                userId='me'
            ).execute()
            
            submissions = submissions_response.get('studentSubmissions', [])
            
            if not submissions:
                # 沒有提交記錄，檢查是否過期
                if due_date and timezone.now() > due_date:
                    return 'overdue'
                return 'pending'
            
            # 檢查第一個提交記錄（通常只有一個）
            submission = submissions[0]
            submission_state = submission.get('state', 'NEW')
            
            # Google Classroom 提交狀態：
            # NEW: 尚未提交
            # CREATED: 已創建但未提交
            # TURNED_IN: 已提交
            # RETURNED: 已退還
            # RECLAIMED_BY_STUDENT: 學生已收回
            
            if submission_state in ['TURNED_IN', 'RETURNED']:
                return 'completed'
            elif submission_state in ['NEW', 'CREATED', 'RECLAIMED_BY_STUDENT']:
                # 檢查是否過期
                if due_date and timezone.now() > due_date:
                    return 'overdue'
                return 'pending'
            else:
                # 未知狀態，預設為 pending
                logger.warning(f"Unknown submission state: {submission_state} for coursework {coursework_id}")
                if due_date and timezone.now() > due_date:
                    return 'overdue'
                return 'pending'
                
        except HttpError as e:
            error_info = APIErrorHandler.handle_google_api_error(e)
            logger.error(f"Failed to get submission status for coursework {coursework_id}: {error_info['message']}")
            
            # API 錯誤時，根據截止日期判斷狀態
            if due_date and timezone.now() > due_date:
                return 'overdue'
            return 'pending'
        except Exception as e:
            logger.error(f"Unexpected error getting submission status for coursework {coursework_id}: {str(e)}")
            
            # 其他錯誤時，根據截止日期判斷狀態
            if due_date and timezone.now() > due_date:
                return 'overdue'
            return 'pending'
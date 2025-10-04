"""
整合查詢服務
提供 Classroom 和本地資料的整合查詢功能
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from user.models import LineProfile
from user.utils import get_valid_google_credentials
from api_v2.models import CourseV2, AssignmentV2
from course.models import Course, Homework

logger = logging.getLogger(__name__)


class IntegratedQueryService:
    """整合查詢服務"""
    
    def __init__(self, line_user_id: str):
        """
        初始化查詢服務
        
        Args:
            line_user_id: LINE 使用者 ID
        """
        self.user = LineProfile.objects.get(line_user_id=line_user_id)
        try:
            self.credentials = get_valid_google_credentials(self.user)
            self.classroom_service = build('classroom', 'v1', credentials=self.credentials, cache_discovery=False)
        except Exception as e:
            logger.warning(f"Failed to initialize Google services for {line_user_id}: {str(e)}")
            self.classroom_service = None
    
    def get_integrated_courses(self, include_classroom: bool = True) -> List[Dict]:
        """
        獲取整合的課程列表（V2 本地 + Classroom 即時）
        
        Args:
            include_classroom: 是否包含 Classroom 即時資料
            
        Returns:
            List[Dict]: 整合的課程列表
        """
        result = []
        
        # 1. 獲取 V2 本地資料（包含鏡像）
        v2_courses = CourseV2.objects.filter(user=self.user).prefetch_related('schedules').order_by('-created_at')
        
        for course in v2_courses:
            course_data = {
                'id': str(course.id),
                'title': course.title,
                'description': course.description or '',
                'instructor': course.instructor or '',
                'classroom': course.classroom or '',
                'color': course.color,
                'source': 'classroom_mirror' if course.is_google_classroom else 'local',
                'is_google_classroom': course.is_google_classroom,
                'google_classroom_id': course.google_classroom_id,
                'created_at': course.created_at.isoformat(),
                'updated_at': course.updated_at.isoformat(),
                'schedules': []
            }
            
            # 添加課程時間
            for schedule in course.schedules.all():
                schedule_data = {
                    'day_of_week': schedule.day_of_week,
                    'start_time': schedule.start_time.strftime('%H:%M:%S'),
                    'end_time': schedule.end_time.strftime('%H:%M:%S'),
                    'location': schedule.location or '',
                    'schedule_source': schedule.schedule_source,
                    'is_default_schedule': schedule.is_default_schedule
                }
                course_data['schedules'].append(schedule_data)
            
            result.append(course_data)
        
        # 2. 如果需要，獲取 Classroom 即時資料（未同步的課程）
        if include_classroom and self.classroom_service:
            try:
                classroom_courses = self._get_classroom_courses_not_in_v2()
                result.extend(classroom_courses)
            except Exception as e:
                logger.error(f"Failed to fetch classroom courses: {str(e)}")
        
        return result
    
    def get_integrated_assignments(self, **filters) -> List[Dict]:
        """
        獲取整合的作業列表（V2 本地 + Classroom 即時）
        
        Args:
            **filters: 篩選條件
            
        Returns:
            List[Dict]: 整合的作業列表
        """
        result = []
        
        # 1. 獲取 V2 本地資料（包含鏡像）
        queryset = AssignmentV2.objects.filter(user=self.user).select_related('course')
        
        # 應用篩選條件
        if 'status' in filters:
            queryset = queryset.filter(status=filters['status'])
        
        if 'upcomingWithinDays' in filters:
            days = int(filters['upcomingWithinDays'])
            end_date = timezone.now() + timedelta(days=days)
            queryset = queryset.filter(due_date__lte=end_date, due_date__gte=timezone.now())
        
        assignments = queryset.order_by('due_date')
        
        for assignment in assignments:
            assignment_data = {
                'id': str(assignment.id),
                'title': assignment.title,
                'description': assignment.description or '',
                'due_date': assignment.due_date.isoformat(),
                'type': assignment.type,
                'status': assignment.status,
                'source': 'classroom_mirror' if assignment.is_google_classroom else 'local',
                'is_google_classroom': assignment.is_google_classroom,
                'google_coursework_id': assignment.google_coursework_id,
                'course': {
                    'id': str(assignment.course.id),
                    'title': assignment.course.title,
                    'is_google_classroom': assignment.course.is_google_classroom
                },
                'created_at': assignment.created_at.isoformat(),
                'updated_at': assignment.updated_at.isoformat()
            }
            result.append(assignment_data)
        
        # 2. 如果需要，獲取 Classroom 即時資料（未同步的作業）
        if self.classroom_service:
            try:
                classroom_assignments = self._get_classroom_assignments_not_in_v2(**filters)
                result.extend(classroom_assignments)
            except Exception as e:
                logger.error(f"Failed to fetch classroom assignments: {str(e)}")
        
        # 3. 重新排序
        result.sort(key=lambda x: x['due_date'])
        
        return result
    
    def get_course_summary(self) -> Dict:
        """
        獲取課程摘要統計
        
        Returns:
            Dict: 課程統計資訊
        """
        v2_courses = CourseV2.objects.filter(user=self.user)
        v2_assignments = AssignmentV2.objects.filter(user=self.user)
        
        # 統計本地和鏡像資料
        local_courses = v2_courses.filter(is_google_classroom=False).count()
        mirror_courses = v2_courses.filter(is_google_classroom=True).count()
        
        local_assignments = v2_assignments.filter(google_coursework_id__isnull=True).count()
        mirror_assignments = v2_assignments.filter(google_coursework_id__isnull=False).count()
        
        # 統計作業狀態
        pending_assignments = v2_assignments.filter(status='pending').count()
        completed_assignments = v2_assignments.filter(status='completed').count()
        overdue_assignments = v2_assignments.filter(status='overdue').count()
        
        # 統計即將到期的作業（7天內）
        upcoming_deadline = timezone.now() + timedelta(days=7)
        upcoming_assignments = v2_assignments.filter(
            due_date__lte=upcoming_deadline,
            due_date__gte=timezone.now(),
            status='pending'
        ).count()
        
        return {
            'courses': {
                'total': local_courses + mirror_courses,
                'local': local_courses,
                'classroom_mirror': mirror_courses
            },
            'assignments': {
                'total': local_assignments + mirror_assignments,
                'local': local_assignments,
                'classroom_mirror': mirror_assignments,
                'by_status': {
                    'pending': pending_assignments,
                    'completed': completed_assignments,
                    'overdue': overdue_assignments
                },
                'upcoming_7_days': upcoming_assignments
            }
        }
    
    def search_courses_and_assignments(self, query: str) -> Dict:
        """
        搜尋課程和作業
        
        Args:
            query: 搜尋關鍵字
            
        Returns:
            Dict: 搜尋結果
        """
        # 搜尋課程
        courses = CourseV2.objects.filter(
            user=self.user,
            title__icontains=query
        ).values('id', 'title', 'is_google_classroom')
        
        # 搜尋作業
        assignments = AssignmentV2.objects.filter(
            user=self.user,
            title__icontains=query
        ).select_related('course').values(
            'id', 'title', 'due_date', 'status',
            'course__title', 'course__is_google_classroom'
        )
        
        return {
            'query': query,
            'courses': list(courses),
            'assignments': list(assignments),
            'total_results': len(courses) + len(assignments)
        }
    
    def _get_classroom_courses_not_in_v2(self) -> List[Dict]:
        """
        獲取尚未同步到 V2 的 Classroom 課程
        
        Returns:
            List[Dict]: 未同步的課程列表
        """
        try:
            # 獲取所有 Classroom 課程（學生身份）
            # 只獲取 ACTIVE 狀態的課程，排除 ARCHIVED 等過期課程
            courses_response = self.classroom_service.courses().list(
                studentId='me',
                courseStates=['ACTIVE']
            ).execute()
            
            # 過濾當前學期的課程（過去6個月內創建的課程）
            current_time = timezone.now()
            six_months_ago = current_time - timezone.timedelta(days=180)
            current_courses = []
            
            for course in courses_response.get('courses', []):
                try:
                    creation_time_str = course.get('creationTime')
                    if creation_time_str:
                        from dateutil import parser
                        creation_time = parser.parse(creation_time_str)
                        if creation_time >= six_months_ago:
                            current_courses.append(course)
                    else:
                        current_courses.append(course)
                except Exception:
                    current_courses.append(course)
            
            courses_response['courses'] = current_courses
            
            classroom_courses = courses_response.get('courses', [])
            
            # 獲取已同步的課程 ID
            synced_course_ids = set(
                CourseV2.objects.filter(
                    user=self.user,
                    is_google_classroom=True,
                    google_classroom_id__isnull=False
                ).values_list('google_classroom_id', flat=True)
            )
            
            # 篩選未同步的課程
            unsynced_courses = []
            for course in classroom_courses:
                if course['id'] not in synced_course_ids:
                    course_data = {
                        'id': f"classroom_{course['id']}",  # 臨時 ID
                        'title': course['name'],
                        'description': course.get('description', ''),
                        'instructor': course.get('ownerId', ''),
                        'classroom': '',
                        'color': '#fbbf24',  # 黃色表示未同步
                        'source': 'classroom_live',
                        'is_google_classroom': True,
                        'google_classroom_id': course['id'],
                        'created_at': course.get('creationTime', ''),
                        'updated_at': course.get('updateTime', ''),
                        'schedules': [],
                        'sync_status': 'not_synced'
                    }
                    unsynced_courses.append(course_data)
            
            return unsynced_courses
            
        except HttpError as e:
            logger.error(f"Failed to fetch classroom courses: {str(e)}")
            return []
    
    def _get_classroom_assignments_not_in_v2(self, **filters) -> List[Dict]:
        """
        獲取尚未同步到 V2 的 Classroom 作業
        
        Args:
            **filters: 篩選條件
            
        Returns:
            List[Dict]: 未同步的作業列表
        """
        try:
            # 獲取已同步的作業 ID
            synced_assignment_ids = set(
                AssignmentV2.objects.filter(
                    user=self.user,
                    google_coursework_id__isnull=False
                ).values_list('google_coursework_id', flat=True)
            )
            
            # 獲取所有 Classroom 課程的作業
            unsynced_assignments = []
            
            courses_response = self.classroom_service.courses().list(
                studentId='me',
                courseStates=['ACTIVE']
            ).execute()
            
            for course in courses_response.get('courses', []):
                try:
                    coursework_response = self.classroom_service.courses().courseWork().list(
                        courseId=course['id'],
                        courseWorkStates=['PUBLISHED']
                    ).execute()
                    
                    for coursework in coursework_response.get('courseWork', []):
                        if coursework['id'] not in synced_assignment_ids:
                            # 解析截止日期
                            due_date = self._parse_classroom_due_date(
                                coursework.get('dueDate'),
                                coursework.get('dueTime')
                            )
                            
                            # 應用篩選條件
                            if 'upcomingWithinDays' in filters:
                                days = int(filters['upcomingWithinDays'])
                                end_date = timezone.now() + timedelta(days=days)
                                if due_date > end_date or due_date < timezone.now():
                                    continue
                            
                            assignment_data = {
                                'id': f"classroom_{coursework['id']}",  # 臨時 ID
                                'title': coursework['title'],
                                'description': coursework.get('description', ''),
                                'due_date': due_date.isoformat(),
                                'type': 'assignment',
                                'status': 'pending',
                                'source': 'classroom_live',
                                'is_google_classroom': True,
                                'google_coursework_id': coursework['id'],
                                'course': {
                                    'id': f"classroom_{course['id']}",
                                    'title': course['name'],
                                    'is_google_classroom': True
                                },
                                'created_at': coursework.get('creationTime', ''),
                                'updated_at': coursework.get('updateTime', ''),
                                'sync_status': 'not_synced'
                            }
                            unsynced_assignments.append(assignment_data)
                            
                except HttpError as e:
                    logger.warning(f"Failed to fetch coursework for course {course['id']}: {str(e)}")
                    continue
            
            return unsynced_assignments
            
        except HttpError as e:
            logger.error(f"Failed to fetch classroom assignments: {str(e)}")
            return []
    
    def _parse_classroom_due_date(self, due_date_dict: Optional[Dict], due_time_dict: Optional[Dict]) -> datetime:
        """
        解析 Classroom 的截止日期格式
        
        Args:
            due_date_dict: Classroom 日期格式
            due_time_dict: Classroom 時間格式
            
        Returns:
            datetime: 解析後的截止日期
        """
        if not due_date_dict:
            return timezone.now() + timedelta(days=7)
        
        year = due_date_dict.get('year', timezone.now().year)
        month = due_date_dict.get('month', 1)
        day = due_date_dict.get('day', 1)
        
        if due_time_dict:
            hour = due_time_dict.get('hours', 23)
            minute = due_time_dict.get('minutes', 59)
        else:
            hour, minute = 23, 59
        
        try:
            return timezone.make_aware(datetime(year, month, day, hour, minute))
        except ValueError:
            return timezone.now() + timedelta(days=7)
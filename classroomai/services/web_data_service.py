"""
網頁本地資料服務
處理 LIFF 網頁端的本地資料 CRUD 操作
"""
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime, time
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from user.models import LineProfile
from api_v2.models import CourseV2, AssignmentV2, CourseScheduleV2
from .error_handler import APIErrorHandler
import re

logger = logging.getLogger(__name__)


class WebDataError(Exception):
    """網頁資料操作錯誤"""
    pass


class PermissionDeniedError(WebDataError):
    """權限拒絕錯誤"""
    pass


class WebDataService:
    """網頁本地資料服務"""
    
    @staticmethod
    def _validate_user_permission(user: LineProfile, obj: Union[CourseV2, AssignmentV2]) -> None:
        """
        驗證使用者權限
        
        Args:
            user: 使用者物件
            obj: 要操作的物件
            
        Raises:
            PermissionDeniedError: 當使用者無權限操作時
        """
        if obj.user != user:
            raise PermissionDeniedError("無權限操作此資料")
    
    @staticmethod
    def _check_classroom_mirror_protection(obj: Union[CourseV2, AssignmentV2], allow_schedule_update: bool = False) -> None:
        """
        檢查是否為 Classroom 鏡像資料並拒絕修改
        
        Args:
            obj: 要檢查的物件
            allow_schedule_update: 是否允許時間表更新（僅對課程有效）
            
        Raises:
            PermissionDeniedError: 當嘗試修改鏡像資料時
        """
        if isinstance(obj, CourseV2) and obj.is_google_classroom:
            if not allow_schedule_update:
                raise PermissionDeniedError("無法修改 Google Classroom 同步的課程資料")
        elif isinstance(obj, AssignmentV2) and obj.is_google_classroom:
            raise PermissionDeniedError("無法修改 Google Classroom 同步的作業資料")
    
    @staticmethod
    def create_local_course(user: LineProfile, **kwargs) -> CourseV2:
        """
        創建本地課程
        
        Args:
            user: 使用者物件
            **kwargs: 課程資料
            
        Returns:
            CourseV2: 創建的課程物件
            
        Raises:
            WebDataError: 當創建失敗時
        """
        try:
            with transaction.atomic():
                # 確保不是 Classroom 鏡像
                kwargs['is_google_classroom'] = False
                kwargs['google_classroom_id'] = None
                kwargs['user'] = user
                
                # 設定預設值
                kwargs.setdefault('color', '#8b5cf6')
                kwargs.setdefault('description', '')
                
                course = CourseV2.objects.create(**kwargs)
                logger.info(f"Created local course: {course.title} for user: {user.line_user_id}")
                
                return course
                
        except ValidationError as e:
            logger.error(f"Validation error creating course: {str(e)}")
            raise WebDataError(f"課程資料驗證失敗: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating course: {str(e)}")
            raise WebDataError(f"創建課程失敗: {str(e)}")
    
    @staticmethod
    def update_local_course(user: LineProfile, course_id: str, **kwargs) -> CourseV2:
        """
        更新本地課程（檢查是否為鏡像資料）
        
        Args:
            user: 使用者物件
            course_id: 課程 ID
            **kwargs: 要更新的資料
            
        Returns:
            CourseV2: 更新後的課程物件
            
        Raises:
            WebDataError: 當更新失敗時
            PermissionDeniedError: 當無權限或嘗試修改鏡像資料時
        """
        try:
            course = CourseV2.objects.get(id=course_id)
            
            # 檢查權限
            WebDataService._validate_user_permission(user, course)
            
            # 檢查是否為鏡像資料
            WebDataService._check_classroom_mirror_protection(course)
            
            # 防止修改關鍵欄位
            kwargs.pop('is_google_classroom', None)
            kwargs.pop('google_classroom_id', None)
            kwargs.pop('user', None)
            kwargs.pop('id', None)
            
            # 更新課程
            for key, value in kwargs.items():
                if hasattr(course, key):
                    setattr(course, key, value)
            
            course.save()
            logger.info(f"Updated local course: {course.title} for user: {user.line_user_id}")
            
            return course
            
        except CourseV2.DoesNotExist:
            raise WebDataError("課程不存在")
        except ValidationError as e:
            logger.error(f"Validation error updating course: {str(e)}")
            raise WebDataError(f"課程資料驗證失敗: {str(e)}")
        except Exception as e:
            logger.error(f"Error updating course {course_id}: {str(e)}")
            raise WebDataError(f"更新課程失敗: {str(e)}")
    
    @staticmethod
    def delete_local_course(user: LineProfile, course_id: str) -> bool:
        """
        刪除課程（包括Google Classroom同步的課程）
        
        Args:
            user: 使用者物件
            course_id: 課程 ID
            
        Returns:
            bool: 是否成功刪除
            
        Raises:
            WebDataError: 當刪除失敗時
            PermissionDeniedError: 當無權限時
        """
        try:
            course = CourseV2.objects.get(id=course_id)
            
            # 檢查權限
            WebDataService._validate_user_permission(user, course)
            
            # 注意：允許刪除Google Classroom課程，但會記錄警告
            if course.is_google_classroom:
                logger.warning(f"Deleting Google Classroom course: {course.title} (ID: {course_id}) for user: {user.line_user_id}")
            
            course_title = course.title
            course.delete()
            logger.info(f"Deleted course: {course_title} for user: {user.line_user_id}")
            
            return True
            
        except CourseV2.DoesNotExist:
            raise WebDataError("課程不存在")
        except Exception as e:
            logger.error(f"Error deleting course {course_id}: {str(e)}")
            raise WebDataError(f"刪除課程失敗: {str(e)}")
    
    @staticmethod
    def get_integrated_courses(user: LineProfile) -> List[Dict]:
        """
        獲取整合的課程列表（本地 + 鏡像）
        
        Args:
            user: 使用者物件
            
        Returns:
            List[Dict]: 課程列表，包含來源標記
        """
        try:
            courses = CourseV2.objects.filter(user=user).prefetch_related('schedules').order_by('-created_at')
            
            result = []
            for course in courses:
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
                    'google_classroom_url': course.google_classroom_url,
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
            
            logger.info(f"Retrieved {len(result)} courses for user: {user.line_user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving courses for user {user.line_user_id}: {str(e)}")
            raise WebDataError(f"獲取課程列表失敗: {str(e)}")
    
    @staticmethod
    def create_local_assignment(user: LineProfile, **kwargs) -> AssignmentV2:
        """
        創建本地作業
        
        Args:
            user: 使用者物件
            **kwargs: 作業資料
            
        Returns:
            AssignmentV2: 創建的作業物件
        """
        try:
            with transaction.atomic():
                # 驗證課程存在且屬於使用者
                course_id = kwargs.get('course_id')
                if course_id:
                    course = CourseV2.objects.get(id=course_id, user=user)
                    kwargs['course'] = course
                    kwargs.pop('course_id', None)
                
                # 確保不是 Classroom 鏡像
                kwargs['google_coursework_id'] = None
                kwargs['user'] = user
                
                # 設定預設值
                kwargs.setdefault('type', 'assignment')
                kwargs.setdefault('status', 'pending')
                
                assignment = AssignmentV2.objects.create(**kwargs)
                logger.info(f"Created local assignment: {assignment.title} for user: {user.line_user_id}")
                
                return assignment
                
        except CourseV2.DoesNotExist:
            raise WebDataError("指定的課程不存在或無權限訪問")
        except ValidationError as e:
            logger.error(f"Validation error creating assignment: {str(e)}")
            raise WebDataError(f"作業資料驗證失敗: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating assignment: {str(e)}")
            raise WebDataError(f"創建作業失敗: {str(e)}")
    
    @staticmethod
    def update_local_assignment(user: LineProfile, assignment_id: str, **kwargs) -> AssignmentV2:
        """
        更新本地作業（檢查是否為鏡像資料）
        
        Args:
            user: 使用者物件
            assignment_id: 作業 ID
            **kwargs: 要更新的資料
            
        Returns:
            AssignmentV2: 更新後的作業物件
        """
        try:
            assignment = AssignmentV2.objects.get(id=assignment_id)
            
            # 檢查權限
            WebDataService._validate_user_permission(user, assignment)
            
            # 檢查是否為鏡像資料
            WebDataService._check_classroom_mirror_protection(assignment)
            
            # 防止修改關鍵欄位
            kwargs.pop('google_coursework_id', None)
            kwargs.pop('user', None)
            kwargs.pop('id', None)
            
            # 處理課程更新
            if 'course_id' in kwargs:
                course_id = kwargs.pop('course_id')
                course = CourseV2.objects.get(id=course_id, user=user)
                kwargs['course'] = course
            
            # 更新作業
            for key, value in kwargs.items():
                if hasattr(assignment, key):
                    setattr(assignment, key, value)
            
            assignment.save()
            logger.info(f"Updated local assignment: {assignment.title} for user: {user.line_user_id}")
            
            return assignment
            
        except AssignmentV2.DoesNotExist:
            raise WebDataError("作業不存在")
        except CourseV2.DoesNotExist:
            raise WebDataError("指定的課程不存在或無權限訪問")
        except ValidationError as e:
            logger.error(f"Validation error updating assignment: {str(e)}")
            raise WebDataError(f"作業資料驗證失敗: {str(e)}")
        except Exception as e:
            logger.error(f"Error updating assignment {assignment_id}: {str(e)}")
            raise WebDataError(f"更新作業失敗: {str(e)}")
    
    @staticmethod
    def delete_local_assignment(user: LineProfile, assignment_id: str) -> bool:
        """
        刪除本地作業（檢查是否為鏡像資料）
        
        Args:
            user: 使用者物件
            assignment_id: 作業 ID
            
        Returns:
            bool: 是否成功刪除
        """
        try:
            assignment = AssignmentV2.objects.get(id=assignment_id)
            
            # 檢查權限
            WebDataService._validate_user_permission(user, assignment)
            
            # 檢查是否為鏡像資料
            WebDataService._check_classroom_mirror_protection(assignment)
            
            assignment_title = assignment.title
            assignment.delete()
            logger.info(f"Deleted local assignment: {assignment_title} for user: {user.line_user_id}")
            
            return True
            
        except AssignmentV2.DoesNotExist:
            raise WebDataError("作業不存在")
        except Exception as e:
            logger.error(f"Error deleting assignment {assignment_id}: {str(e)}")
            raise WebDataError(f"刪除作業失敗: {str(e)}")
    
    @staticmethod
    def get_integrated_assignments(user: LineProfile, **filters) -> List[Dict]:
        """
        獲取整合的作業列表（本地 + 鏡像）
        
        Args:
            user: 使用者物件
            **filters: 篩選條件
            
        Returns:
            List[Dict]: 作業列表，包含來源標記
        """
        try:
            queryset = AssignmentV2.objects.filter(user=user).select_related('course')
            
            # 應用篩選條件
            if 'status' in filters:
                queryset = queryset.filter(status=filters['status'])
            
            if 'upcomingWithinDays' in filters:
                days = int(filters['upcomingWithinDays'])
                end_date = timezone.now() + timezone.timedelta(days=days)
                queryset = queryset.filter(due_date__lte=end_date, due_date__gte=timezone.now())
            
            assignments = queryset.order_by('due_date')
            
            result = []
            for assignment in assignments:
                assignment_data = {
                    'id': str(assignment.id),
                    'title': assignment.title,
                    'description': assignment.description or '',
                    'due_date': assignment.due_date.isoformat(),
                    'type': assignment.type,
                    'status': assignment.status,
                    'is_google_classroom': assignment.is_google_classroom,
                    'google_coursework_id': assignment.google_coursework_id,
                    'google_classroom_url': assignment.google_classroom_url,
                    'course': {
                        'id': str(assignment.course.id),
                        'title': assignment.course.title,
                        'is_google_classroom': assignment.course.is_google_classroom
                    },
                    'created_at': assignment.created_at.isoformat(),
                    'updated_at': assignment.updated_at.isoformat()
                }
                result.append(assignment_data)
            
            logger.info(f"Retrieved {len(result)} assignments for user: {user.line_user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving assignments for user {user.line_user_id}: {str(e)}")
            raise WebDataError(f"獲取作業列表失敗: {str(e)}")
    
    @staticmethod
    def update_course_schedule(user: LineProfile, course_id: str, schedules: List[Dict]) -> bool:
        """
        更新課程時間（包含 Classroom 鏡像課程的時間設定）
        
        Args:
            user: 使用者物件
            course_id: 課程 ID
            schedules: 時間設定列表
            
        Returns:
            bool: 是否成功更新
        """
        try:
            course = CourseV2.objects.get(id=course_id, user=user)
            
            with transaction.atomic():
                # 刪除現有的手動設定時間（保留推測時間作為備份）
                CourseScheduleV2.objects.filter(
                    course=course,
                    schedule_source='manual'
                ).delete()
                
                # 創建新的時間設定
                for schedule_data in schedules:
                    CourseScheduleV2.objects.create(
                        course=course,
                        day_of_week=schedule_data['day_of_week'],
                        start_time=schedule_data['start_time'],
                        end_time=schedule_data['end_time'],
                        location=schedule_data.get('location', ''),
                        schedule_source='manual',  # 標記為手動設定
                        is_default_schedule=False
                    )
                
                # 如果有新的手動時間，刪除預設時間佔位符
                CourseScheduleV2.objects.filter(
                    course=course,
                    is_default_schedule=True
                ).delete()
            
            logger.info(f"Updated schedule for course: {course.title} for user: {user.line_user_id}")
            return True
            
        except CourseV2.DoesNotExist:
            raise WebDataError("課程不存在或無權限訪問")
        except Exception as e:
            logger.error(f"Error updating course schedule {course_id}: {str(e)}")
            raise WebDataError(f"更新課程時間失敗: {str(e)}")
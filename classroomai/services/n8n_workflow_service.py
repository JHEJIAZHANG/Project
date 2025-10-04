"""
n8n 工作流整合服務
處理自然語言意圖識別到 API 呼叫的轉換
"""
import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import JsonResponse
from rest_framework import status
from api_v2.models import CourseV2, AssignmentV2
from user.models import LineProfile
from .web_data_service import WebDataService
from .classroom_sync_service import ClassroomSyncService

logger = logging.getLogger(__name__)


class N8nWorkflowService:
    """n8n 工作流整合服務"""
    
    # 意圖類型定義
    INTENT_TYPES = {
        # 本地課程操作
        'create_local_course': 'create_local_course',
        'update_local_course': 'update_local_course', 
        'delete_local_course': 'delete_local_course',
        
        # 本地作業操作
        'create_local_assignment': 'create_local_assignment',
        'update_local_assignment': 'update_local_assignment',
        'delete_local_assignment': 'delete_local_assignment',
        
        # 課程時間設定
        'set_course_schedule': 'set_course_schedule',
        
        # 查詢操作
        'list_my_courses': 'list_my_courses',
        'list_my_assignments': 'list_my_assignments',
        
        # 同步操作
        'sync_all_classroom': 'sync_all_classroom',
        'sync_single_course': 'sync_single_course'
    }
    
    # 星期對應表
    DAY_MAP = {
        '週一': 0, '週二': 1, '週三': 2, '週四': 3, '週五': 4, '週六': 5, '週日': 6,
        '星期一': 0, '星期二': 1, '星期三': 2, '星期四': 3, '星期五': 4, '星期六': 5, '星期日': 6,
        '禮拜一': 0, '禮拜二': 1, '禮拜三': 2, '禮拜四': 3, '禮拜五': 4, '禮拜六': 5, '禮拜日': 6
    }
    
    @classmethod
    def process_intent(cls, intent_data: Dict, line_user_id: str) -> Dict:
        """
        處理意圖並執行對應的 API 操作
        
        Args:
            intent_data: 意圖識別結果
            line_user_id: LINE 使用者 ID
            
        Returns:
            Dict: API 執行結果
        """
        try:
            intent_type = intent_data.get('intent')
            parameters = intent_data.get('parameters', {})
            
            if intent_type not in cls.INTENT_TYPES:
                return cls._error_response('INVALID_INTENT', f'不支援的意圖類型: {intent_type}')
            
            # 驗證使用者
            try:
                user = LineProfile.objects.get(line_user_id=line_user_id)
            except LineProfile.DoesNotExist:
                return cls._error_response('USER_NOT_FOUND', '找不到使用者')
            
            # 根據意圖類型執行對應操作
            handler_method = getattr(cls, f'_handle_{intent_type}', None)
            if not handler_method:
                return cls._error_response('HANDLER_NOT_FOUND', f'找不到處理器: {intent_type}')
            
            return handler_method(parameters, line_user_id)
            
        except Exception as e:
            logger.error(f"Error processing intent: {str(e)}")
            return cls._error_response('INTERNAL_ERROR', '處理意圖時發生錯誤')
    
    @classmethod
    def _handle_create_local_course(cls, parameters: Dict, line_user_id: str) -> Dict:
        """處理創建本地課程意圖"""
        try:
            # 準備 API 參數
            api_data = {
                'line_user_id': line_user_id,
                'title': parameters.get('title'),
                'description': parameters.get('description', ''),
                'instructor': parameters.get('instructor', ''),
                'classroom': parameters.get('classroom', ''),
                'color': parameters.get('color', '#8b5cf6')
            }
            
            # 驗證必要參數
            if not api_data['title']:
                return cls._error_response('MISSING_PARAMETER', '缺少課程名稱')
            
            # 呼叫 WebDataService
            result = WebDataService.create_local_course(**api_data)
            
            if result['success']:
                return cls._success_response(
                    'CREATE_COURSE_SUCCESS',
                    f"✅ 課程「{result['data']['title']}」創建成功！",
                    result['data']
                )
            else:
                return cls._error_response('CREATE_COURSE_FAILED', result['message'])
                
        except Exception as e:
            logger.error(f"Error creating local course: {str(e)}")
            return cls._error_response('INTERNAL_ERROR', '創建課程時發生錯誤')
    
    @classmethod
    def _handle_update_local_course(cls, parameters: Dict, line_user_id: str) -> Dict:
        """處理更新本地課程意圖"""
        try:
            course_name = parameters.get('course_name')
            if not course_name:
                return cls._error_response('MISSING_PARAMETER', '缺少課程名稱')
            
            # 查找課程 ID
            course = cls._find_course_by_name(course_name, line_user_id)
            if not course:
                return cls._error_response('COURSE_NOT_FOUND', f'找不到課程: {course_name}')
            
            # 準備更新資料
            update_data = {
                'line_user_id': line_user_id,
                'course_id': str(course.id)
            }
            
            # 添加要更新的欄位
            for field in ['title', 'description', 'instructor', 'classroom']:
                if parameters.get(field):
                    update_data[field] = parameters[field]
            
            if len(update_data) <= 2:  # 只有 line_user_id 和 course_id
                return cls._error_response('NO_UPDATE_DATA', '沒有要更新的資料')
            
            # 呼叫 WebDataService
            result = WebDataService.update_local_course(**update_data)
            
            if result['success']:
                return cls._success_response(
                    'UPDATE_COURSE_SUCCESS',
                    f"✅ 課程「{result['data']['title']}」更新成功！",
                    result['data']
                )
            else:
                return cls._error_response('UPDATE_COURSE_FAILED', result['message'])
                
        except Exception as e:
            logger.error(f"Error updating local course: {str(e)}")
            return cls._error_response('INTERNAL_ERROR', '更新課程時發生錯誤')
    
    @classmethod
    def _handle_delete_local_course(cls, parameters: Dict, line_user_id: str) -> Dict:
        """處理刪除本地課程意圖"""
        try:
            course_name = parameters.get('course_name')
            if not course_name:
                return cls._error_response('MISSING_PARAMETER', '缺少課程名稱')
            
            # 查找課程 ID
            course = cls._find_course_by_name(course_name, line_user_id)
            if not course:
                return cls._error_response('COURSE_NOT_FOUND', f'找不到課程: {course_name}')
            
            # 呼叫 WebDataService
            result = WebDataService.delete_local_course(
                line_user_id=line_user_id,
                course_id=str(course.id)
            )
            
            if result['success']:
                return cls._success_response(
                    'DELETE_COURSE_SUCCESS',
                    f"✅ 課程「{course.title}」刪除成功！",
                    {'deleted_course_id': str(course.id)}
                )
            else:
                return cls._error_response('DELETE_COURSE_FAILED', result['message'])
                
        except Exception as e:
            logger.error(f"Error deleting local course: {str(e)}")
            return cls._error_response('INTERNAL_ERROR', '刪除課程時發生錯誤')
    
    @classmethod
    def _handle_create_local_assignment(cls, parameters: Dict, line_user_id: str) -> Dict:
        """處理創建本地作業意圖"""
        try:
            course_name = parameters.get('course_name')
            if not course_name:
                return cls._error_response('MISSING_PARAMETER', '缺少課程名稱')
            
            # 查找課程 ID
            course = cls._find_course_by_name(course_name, line_user_id)
            if not course:
                return cls._error_response('COURSE_NOT_FOUND', f'找不到課程: {course_name}')
            
            # 解析截止日期
            due_date = cls._parse_due_date(parameters.get('due_date'))
            if not due_date:
                return cls._error_response('INVALID_DUE_DATE', '無效的截止日期格式')
            
            # 準備 API 參數
            api_data = {
                'line_user_id': line_user_id,
                'course_id': str(course.id),
                'title': parameters.get('title'),
                'description': parameters.get('description', ''),
                'due_date': due_date.isoformat(),
                'type': parameters.get('type', 'assignment')
            }
            
            # 驗證必要參數
            if not api_data['title']:
                return cls._error_response('MISSING_PARAMETER', '缺少作業標題')
            
            # 呼叫 WebDataService
            result = WebDataService.create_local_assignment(**api_data)
            
            if result['success']:
                return cls._success_response(
                    'CREATE_ASSIGNMENT_SUCCESS',
                    f"✅ 作業「{result['data']['title']}」創建成功！",
                    result['data']
                )
            else:
                return cls._error_response('CREATE_ASSIGNMENT_FAILED', result['message'])
                
        except Exception as e:
            logger.error(f"Error creating local assignment: {str(e)}")
            return cls._error_response('INTERNAL_ERROR', '創建作業時發生錯誤')
    
    @classmethod
    def _handle_update_local_assignment(cls, parameters: Dict, line_user_id: str) -> Dict:
        """處理更新本地作業意圖"""
        try:
            assignment_name = parameters.get('assignment_name')
            course_name = parameters.get('course_name')
            
            if not assignment_name:
                return cls._error_response('MISSING_PARAMETER', '缺少作業名稱')
            
            # 查找作業 ID
            assignment = cls._find_assignment_by_name(assignment_name, course_name, line_user_id)
            if not assignment:
                return cls._error_response('ASSIGNMENT_NOT_FOUND', f'找不到作業: {assignment_name}')
            
            # 準備更新資料
            update_data = {
                'line_user_id': line_user_id,
                'assignment_id': str(assignment.id)
            }
            
            # 添加要更新的欄位
            for field in ['title', 'description', 'status']:
                if parameters.get(field):
                    update_data[field] = parameters[field]
            
            # 處理截止日期
            if parameters.get('due_date'):
                due_date = cls._parse_due_date(parameters['due_date'])
                if due_date:
                    update_data['due_date'] = due_date.isoformat()
            
            if len(update_data) <= 2:  # 只有 line_user_id 和 assignment_id
                return cls._error_response('NO_UPDATE_DATA', '沒有要更新的資料')
            
            # 呼叫 WebDataService
            result = WebDataService.update_local_assignment(**update_data)
            
            if result['success']:
                return cls._success_response(
                    'UPDATE_ASSIGNMENT_SUCCESS',
                    f"✅ 作業「{result['data']['title']}」更新成功！",
                    result['data']
                )
            else:
                return cls._error_response('UPDATE_ASSIGNMENT_FAILED', result['message'])
                
        except Exception as e:
            logger.error(f"Error updating local assignment: {str(e)}")
            return cls._error_response('INTERNAL_ERROR', '更新作業時發生錯誤')
    
    @classmethod
    def _handle_delete_local_assignment(cls, parameters: Dict, line_user_id: str) -> Dict:
        """處理刪除本地作業意圖"""
        try:
            assignment_name = parameters.get('assignment_name')
            course_name = parameters.get('course_name')
            
            if not assignment_name:
                return cls._error_response('MISSING_PARAMETER', '缺少作業名稱')
            
            # 查找作業 ID
            assignment = cls._find_assignment_by_name(assignment_name, course_name, line_user_id)
            if not assignment:
                return cls._error_response('ASSIGNMENT_NOT_FOUND', f'找不到作業: {assignment_name}')
            
            # 呼叫 WebDataService
            result = WebDataService.delete_local_assignment(
                line_user_id=line_user_id,
                assignment_id=str(assignment.id)
            )
            
            if result['success']:
                return cls._success_response(
                    'DELETE_ASSIGNMENT_SUCCESS',
                    f"✅ 作業「{assignment.title}」刪除成功！",
                    {'deleted_assignment_id': str(assignment.id)}
                )
            else:
                return cls._error_response('DELETE_ASSIGNMENT_FAILED', result['message'])
                
        except Exception as e:
            logger.error(f"Error deleting local assignment: {str(e)}")
            return cls._error_response('INTERNAL_ERROR', '刪除作業時發生錯誤')
    
    @classmethod
    def _handle_set_course_schedule(cls, parameters: Dict, line_user_id: str) -> Dict:
        """處理設定課程時間意圖"""
        try:
            course_name = parameters.get('course_name')
            if not course_name:
                return cls._error_response('MISSING_PARAMETER', '缺少課程名稱')
            
            # 查找課程 ID
            course = cls._find_course_by_name(course_name, line_user_id)
            if not course:
                return cls._error_response('COURSE_NOT_FOUND', f'找不到課程: {course_name}')
            
            # 解析時間表
            schedules = parameters.get('schedules', [])
            if not schedules:
                # 嘗試從文字中解析時間
                schedule_text = parameters.get('schedule_text', '')
                if schedule_text:
                    parsed_schedule = cls._parse_schedule_from_text(schedule_text)
                    if parsed_schedule:
                        schedules = [parsed_schedule]
            
            if not schedules:
                return cls._error_response('MISSING_SCHEDULE', '缺少課程時間資訊')
            
            # 呼叫 WebDataService
            result = WebDataService.update_course_schedule(
                line_user_id=line_user_id,
                course_id=str(course.id),
                schedules=schedules
            )
            
            if result['success']:
                return cls._success_response(
                    'SET_SCHEDULE_SUCCESS',
                    f"✅ 課程「{course.title}」時間設定成功！已設定 {len(schedules)} 個時段。",
                    result['data']
                )
            else:
                return cls._error_response('SET_SCHEDULE_FAILED', result['message'])
                
        except Exception as e:
            logger.error(f"Error setting course schedule: {str(e)}")
            return cls._error_response('INTERNAL_ERROR', '設定課程時間時發生錯誤')
    
    @classmethod
    def _handle_list_my_courses(cls, parameters: Dict, line_user_id: str) -> Dict:
        """處理查詢我的課程意圖"""
        try:
            # 呼叫 WebDataService
            user = LineProfile.objects.get(line_user_id=line_user_id)
            courses = WebDataService.get_integrated_courses(user)
            result = {'success': True, 'data': {'courses': courses}}
            
            if result['success']:
                courses = result['data']['courses']
                course_count = len(courses)
                
                # 格式化回應訊息
                if course_count == 0:
                    message = "📚 您目前沒有任何課程。"
                else:
                    message = f"📚 您共有 {course_count} 個課程：\n\n"
                    for i, course in enumerate(courses[:10], 1):  # 最多顯示 10 個
                        source_icon = "🔄" if course['is_google_classroom'] else "📝"
                        message += f"{i}. {source_icon} {course['title']}\n"
                        if course.get('instructor'):
                            message += f"   👨‍🏫 {course['instructor']}\n"
                        if course.get('schedules'):
                            schedule = course['schedules'][0]
                            day_name = cls._get_day_name(schedule['day_of_week'])
                            message += f"   ⏰ {day_name} {schedule['start_time'][:5]}-{schedule['end_time'][:5]}\n"
                        message += "\n"
                    
                    if course_count > 10:
                        message += f"... 還有 {course_count - 10} 個課程"
                
                return cls._success_response(
                    'LIST_COURSES_SUCCESS',
                    message,
                    result['data']
                )
            else:
                return cls._error_response('LIST_COURSES_FAILED', result['message'])
                
        except Exception as e:
            logger.error(f"Error listing courses: {str(e)}")
            return cls._error_response('INTERNAL_ERROR', '查詢課程時發生錯誤')
    
    @classmethod
    def _handle_list_my_assignments(cls, parameters: Dict, line_user_id: str) -> Dict:
        """處理查詢我的作業意圖"""
        try:
            # 準備查詢參數
            query_params = {'line_user_id': line_user_id}
            
            if parameters.get('status'):
                query_params['status'] = parameters['status']
            
            if parameters.get('upcomingWithinDays'):
                query_params['upcomingWithinDays'] = parameters['upcomingWithinDays']
            
            # 呼叫 WebDataService
            user = LineProfile.objects.get(line_user_id=line_user_id)
            filters = {k: v for k, v in query_params.items() if k != 'line_user_id'}
            assignments = WebDataService.get_integrated_assignments(user, **filters)
            result = {'success': True, 'data': {'assignments': assignments}}
            
            if result['success']:
                assignments = result['data']['assignments']
                assignment_count = len(assignments)
                
                # 格式化回應訊息
                if assignment_count == 0:
                    message = "📋 沒有找到符合條件的作業。"
                else:
                    status_text = parameters.get('status', '所有')
                    message = f"📋 找到 {assignment_count} 個{status_text}作業：\n\n"
                    
                    for i, assignment in enumerate(assignments[:10], 1):  # 最多顯示 10 個
                        source_icon = "🔄" if assignment['is_google_classroom'] else "📝"
                        status_icon = cls._get_status_icon(assignment['status'])
                        
                        message += f"{i}. {source_icon}{status_icon} {assignment['title']}\n"
                        message += f"   📚 {assignment['course']['title']}\n"
                        
                        # 格式化截止日期
                        due_date = datetime.fromisoformat(assignment['due_date'].replace('Z', '+00:00'))
                        message += f"   ⏰ {due_date.strftime('%m/%d %H:%M')}\n\n"
                    
                    if assignment_count > 10:
                        message += f"... 還有 {assignment_count - 10} 個作業"
                
                return cls._success_response(
                    'LIST_ASSIGNMENTS_SUCCESS',
                    message,
                    result['data']
                )
            else:
                return cls._error_response('LIST_ASSIGNMENTS_FAILED', result['message'])
                
        except Exception as e:
            logger.error(f"Error listing assignments: {str(e)}")
            return cls._error_response('INTERNAL_ERROR', '查詢作業時發生錯誤')
    
    @classmethod
    def _handle_sync_all_classroom(cls, parameters: Dict, line_user_id: str) -> Dict:
        """處理全量同步意圖"""
        try:
            # 呼叫同步服務
            sync_service = ClassroomSyncService(line_user_id)
            result = sync_service.sync_all_courses()
            
            if result['success']:
                courses_synced = result['data']['courses_synced']
                assignments_synced = result['data']['assignments_synced']
                
                message = f"✅ 同步完成！\n"
                message += f"📚 已同步 {courses_synced} 個課程\n"
                message += f"📋 已同步 {assignments_synced} 個作業"
                
                return cls._success_response(
                    'SYNC_ALL_SUCCESS',
                    message,
                    result['data']
                )
            else:
                return cls._error_response('SYNC_ALL_FAILED', result['message'])
                
        except Exception as e:
            logger.error(f"Error syncing all classroom: {str(e)}")
            return cls._error_response('INTERNAL_ERROR', '全量同步時發生錯誤')
    
    @classmethod
    def _handle_sync_single_course(cls, parameters: Dict, line_user_id: str) -> Dict:
        """處理單一課程同步意圖"""
        try:
            course_name = parameters.get('course_name')
            if not course_name:
                return cls._error_response('MISSING_PARAMETER', '缺少課程名稱')
            
            # 查找課程的 Google Classroom ID
            course = cls._find_course_by_name(course_name, line_user_id)
            if not course:
                return cls._error_response('COURSE_NOT_FOUND', f'找不到課程: {course_name}')
            
            if not course.google_classroom_id:
                return cls._error_response('NOT_CLASSROOM_COURSE', '此課程不是 Google Classroom 課程')
            
            # 呼叫同步服務
            sync_service = ClassroomSyncService(line_user_id)
            result = sync_service.sync_single_course(course.google_classroom_id)
            
            if result['success']:
                assignments_synced = result['data']['assignments_synced']
                
                message = f"✅ 課程「{course.title}」同步完成！\n"
                message += f"📋 已同步 {assignments_synced} 個作業"
                
                return cls._success_response(
                    'SYNC_COURSE_SUCCESS',
                    message,
                    result['data']
                )
            else:
                return cls._error_response('SYNC_COURSE_FAILED', result['message'])
                
        except Exception as e:
            logger.error(f"Error syncing single course: {str(e)}")
            return cls._error_response('INTERNAL_ERROR', '課程同步時發生錯誤')
    
    # 輔助方法
    
    @classmethod
    def _find_course_by_name(cls, course_name: str, line_user_id: str) -> Optional[CourseV2]:
        """根據名稱查找課程"""
        try:
            user = LineProfile.objects.get(line_user_id=line_user_id)
            courses = CourseV2.objects.filter(user=user)
            
            # 精確匹配
            course = courses.filter(title=course_name).first()
            if course:
                return course
            
            # 模糊匹配
            for course in courses:
                if course_name in course.title or course.title in course_name:
                    return course
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding course by name: {str(e)}")
            return None
    
    @classmethod
    def _find_assignment_by_name(cls, assignment_name: str, course_name: Optional[str], line_user_id: str) -> Optional[AssignmentV2]:
        """根據名稱查找作業"""
        try:
            user = LineProfile.objects.get(line_user_id=line_user_id)
            assignments = AssignmentV2.objects.filter(user=user).select_related('course')
            
            # 如果指定了課程名稱，先篩選課程
            if course_name:
                course_assignments = []
                for assignment in assignments:
                    if (course_name in assignment.course.title or 
                        assignment.course.title in course_name):
                        course_assignments.append(assignment)
                assignments = course_assignments
            
            # 精確匹配
            for assignment in assignments:
                if assignment.title == assignment_name:
                    return assignment
            
            # 模糊匹配
            for assignment in assignments:
                if assignment_name in assignment.title or assignment.title in assignment_name:
                    return assignment
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding assignment by name: {str(e)}")
            return None
    
    @classmethod
    def _parse_due_date(cls, due_date_str: str) -> Optional[datetime]:
        """解析截止日期字串"""
        if not due_date_str:
            return None
        
        try:
            # 嘗試多種日期格式
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%Y-%m-%d',
                '%m/%d %H:%M',
                '%m/%d',
                '%Y/%m/%d %H:%M:%S',
                '%Y/%m/%d %H:%M',
                '%Y/%m/%d'
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(due_date_str, fmt)
                    # 如果沒有年份，使用當前年份
                    if dt.year == 1900:
                        dt = dt.replace(year=timezone.now().year)
                    # 如果沒有時間，設定為 23:59
                    if dt.hour == 0 and dt.minute == 0:
                        dt = dt.replace(hour=23, minute=59)
                    
                    return timezone.make_aware(dt)
                except ValueError:
                    continue
            
            # 嘗試相對日期（如"明天"、"下週一"等）
            return cls._parse_relative_date(due_date_str)
            
        except Exception as e:
            logger.error(f"Error parsing due date: {str(e)}")
            return None
    
    @classmethod
    def _parse_relative_date(cls, date_str: str) -> Optional[datetime]:
        """解析相對日期"""
        now = timezone.now()
        
        if '今天' in date_str:
            return now.replace(hour=23, minute=59, second=0, microsecond=0)
        elif '明天' in date_str:
            return (now + timedelta(days=1)).replace(hour=23, minute=59, second=0, microsecond=0)
        elif '後天' in date_str:
            return (now + timedelta(days=2)).replace(hour=23, minute=59, second=0, microsecond=0)
        elif '下週' in date_str:
            return (now + timedelta(days=7)).replace(hour=23, minute=59, second=0, microsecond=0)
        
        return None
    
    @classmethod
    def _parse_schedule_from_text(cls, text: str) -> Optional[Dict]:
        """從文字中解析課程時間"""
        try:
            # 解析星期幾
            day_of_week = None
            for day, num in cls.DAY_MAP.items():
                if day in text:
                    day_of_week = num
                    break
            
            if day_of_week is None:
                return None
            
            # 解析時間
            time_regex = r'(\d{1,2})[點:](\d{0,2})'
            times = []
            
            for match in re.finditer(time_regex, text):
                hour = int(match.group(1))
                minute = int(match.group(2)) if match.group(2) else 0
                times.append(f"{hour:02d}:{minute:02d}:00")
            
            if len(times) >= 2:
                return {
                    'day_of_week': day_of_week,
                    'start_time': times[0],
                    'end_time': times[1],
                    'location': ''
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing schedule from text: {str(e)}")
            return None
    
    @classmethod
    def _get_day_name(cls, day_of_week: int) -> str:
        """獲取星期名稱"""
        day_names = ['週一', '週二', '週三', '週四', '週五', '週六', '週日']
        return day_names[day_of_week] if 0 <= day_of_week <= 6 else '未知'
    
    @classmethod
    def _get_status_icon(cls, status: str) -> str:
        """獲取狀態圖示"""
        status_icons = {
            'pending': '⏳',
            'completed': '✅',
            'overdue': '🔴'
        }
        return status_icons.get(status, '❓')
    
    @classmethod
    def _success_response(cls, code: str, message: str, data: Any = None) -> Dict:
        """成功回應格式"""
        return {
            'success': True,
            'code': code,
            'message': message,
            'data': data or {}
        }
    
    @classmethod
    def _error_response(cls, code: str, message: str) -> Dict:
        """錯誤回應格式"""
        return {
            'success': False,
            'code': code,
            'message': message,
            'data': {}
        }
"""
API V2 URL 配置
包含同步、網頁資料 CRUD 和整合查詢的路由
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import sync_views, web_views, integrated_views, legacy_views, views, calendar_views

app_name = 'api_v2'

# DRF Router 配置
router = DefaultRouter()
router.register(r'files', views.FileUploadViewSet, basename='files')
router.register(r'courses', views.CourseViewSet, basename='courses')
router.register(r'assignments', views.AssignmentViewSet, basename='assignments')
router.register(r'exams', views.ExamViewSet, basename='exams')
router.register(r'notes', views.NoteViewSet, basename='notes')
router.register(r'custom-categories', views.CustomCategoryViewSet, basename='custom-categories')
router.register(r'custom-todos', views.CustomTodoItemViewSet, basename='custom-todos')

urlpatterns = [
    # DRF Router URLs (包含 files/, courses/, assignments/ 等)
    path('', include(router.urls)),
    
    # 健康檢查端點
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
    
    # 用戶配置文件端點
    path('profile/<str:line_user_id>/', views.UserProfileView.as_view(), name='user_profile'),
    
    # 作業推薦端點
    path('assignments/<str:assignment_id>/recommendations/', views.AssignmentRecommendationView.as_view(), name='assignment_recommendations'),
    # 兼容：無結尾斜線（避免客戶端漏斜線造成 404）
    path('assignments/<str:assignment_id>/recommendations', views.AssignmentRecommendationView.as_view()),
    
    # 考試推薦端點
    path('exams/<str:exam_id>/recommendations/', views.ExamRecommendationView.as_view(), name='exam_recommendations'),
    # 兼容：無結尾斜線（避免客戶端漏斜線造成 404）
    path('exams/<str:exam_id>/recommendations', views.ExamRecommendationView.as_view()),
    
    # 作業狀態端點
    path('assignments/<str:assignment_id>/status/', views.AssignmentStatusView.as_view(), name='assignment_status'),
    
    # 同步相關 API
    path('sync/classroom-to-v2/', sync_views.sync_classroom_to_v2, name='sync_classroom_to_v2'),
    path('sync/classroom-course/', sync_views.sync_classroom_course, name='sync_classroom_course'),
    path('sync/auto-trigger/', sync_views.trigger_auto_sync, name='trigger_auto_sync'),
    path('sync/status/', sync_views.get_sync_status, name='get_sync_status'),
    path('sync/google-status/', sync_views.check_google_api_status, name='check_google_api_status'),

    path('sync/manual-sync-all/', sync_views.manual_sync_all, name='manual_sync_all'),
    
    # Google Calendar API
    path('calendar/get_calendar_events/', calendar_views.get_calendar_events, name='get_calendar_events'),
    path('calendar/create_calendar_event/', calendar_views.create_calendar_event, name='create_calendar_event'),
    path('calendar/update_calendar_event/', calendar_views.update_calendar_event, name='update_calendar_event'),
    path('calendar/delete_calendar_event/', calendar_views.delete_calendar_event, name='delete_calendar_event'),
    path('calendar/events/attendees/', calendar_views.manage_calendar_attendees, name='manage_calendar_attendees'),
    
    # 課程相關 API
    path('web/courses/create/', web_views.create_course, name='create_course'),
    path('web/courses/update/', web_views.update_course, name='update_course'),
    path('web/courses/delete/', web_views.delete_course, name='delete_course'),
    path('web/courses/list/', web_views.list_courses, name='list_courses'),
    path('web/courses/schedule/', web_views.set_course_schedule, name='set_course_schedule'),
    
    # 作業相關 API
    path('web/assignments/create/', web_views.create_assignment, name='create_assignment'),
    path('web/assignments/update/', web_views.update_assignment, name='update_assignment'),
    path('web/assignments/delete/', web_views.delete_assignment, name='delete_assignment'),
    path('web/assignments/list/', web_views.list_assignments, name='list_assignments'),
    
    # 整合查詢 API
    path('integrated/courses/', integrated_views.get_integrated_courses, name='get_integrated_courses'),
    path('integrated/assignments/', integrated_views.get_integrated_assignments, name='get_integrated_assignments'),
    path('integrated/summary/', integrated_views.get_course_summary, name='get_course_summary'),
    path('integrated/search/', integrated_views.search_courses_and_assignments, name='search_courses_and_assignments'),
    path('integrated/dashboard/', integrated_views.get_dashboard_data, name='get_dashboard_data'),
    
    # n8n 工作流整合 API
    path('integrated/n8n-intent/', integrated_views.process_n8n_intent, name='process_n8n_intent'),
    
    # Legacy API（與前端相容）
    path('courses/', legacy_views.get_courses, name='get_courses'),
    path('assignments/', legacy_views.get_assignments, name='get_assignments'),
    path('custom-categories/', legacy_views.get_custom_categories, name='get_custom_categories'),
    path('custom-categories/<str:category_id>/', legacy_views.manage_custom_category, name='manage_custom_category'),
    path('custom-todos/', legacy_views.get_custom_todos, name='get_custom_todos'),
    path('custom-todos/<str:todo_id>/', legacy_views.manage_custom_todo, name='manage_custom_todo'),
    path('notes/', legacy_views.get_notes, name='get_notes'),
    path('notes/<str:note_id>/', legacy_views.manage_note, name='manage_note'),
    path('exams/', legacy_views.get_exams, name='get_exams'),
]
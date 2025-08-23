from django.urls import path
from .views import (create_classroom, 
                    create_homework, 
                    update_homework, 
                    delete_homework,
                    check_course,
                    get_homeworks,
                    get_courses,
                    delete_course,
                    create_calendar_event,
                    update_calendar_event,
                    delete_calendar_event,
                    get_calendar_events,
                    manage_calendar_attendees,
                    get_submissions_status,
                    create_note,
                    get_notes,
                    get_note_detail,
                    update_note,
                    delete_note)

urlpatterns = [
    # Classroom APIs
    path("api/classrooms/", create_classroom, name="create_classroom"),
    path("api/homeworks/", create_homework, name="create_homework"),
    path("api/homeworks/", update_homework, name="update_homework"),  # PATCH
    path("api/delete_homework/", delete_homework, name="delete_homework"),  # DELETE
    path("api/check-course/", check_course, name="check_course"),
    path("api/get-homeworks/", get_homeworks, name="get_homeworks"),
    path("api/courses/", get_courses, name="get_courses"),
    path("api/delete-course/", delete_course, name="delete_course"),  # DELETE
    
    # Google Calendar APIs
    path("api/calendar/create_calendar_event/", create_calendar_event, name="create_calendar_event"),
    path("api/calendar/update_calendar_event/", update_calendar_event, name="update_calendar_event"),
    path("api/calendar/delete_calendar_event/", delete_calendar_event, name="delete_calendar_event"),
    path("api/calendar/get_calendar_events/", get_calendar_events, name="get_calendar_events"),
    path("api/calendar/events/attendees/", manage_calendar_attendees, name="manage_calendar_attendees"),

    # Progress & Notes
    path("api/classroom/submissions/status/", get_submissions_status, name="get_submissions_status"),
    
    # Notes APIs - 完整CRUD功能
    path("api/notes/", create_note, name="create_note"),           # POST - 創建筆記
    path("api/notes/", update_note, name="update_note"),           # PATCH/PUT - 更新筆記  
    path("api/notes/", delete_note, name="delete_note"),           # DELETE - 刪除筆記
    path("api/notes/list/", get_notes, name="get_notes"),          # GET - 查詢筆記列表
    path("api/notes/detail/", get_note_detail, name="get_note_detail"),  # GET - 取得單一筆記
]

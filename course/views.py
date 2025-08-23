from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from googleapiclient.discovery import build
from dateutil import parser as date_parser
from user.models import LineProfile
from user.utils import get_valid_google_credentials
from line_bot.utils import send_course_created_message, send_homework_created_message, send_multiple_homework_created_message, send_note_created_message
from line_bot.models import GroupBinding
from .models import Course, Homework
from .serializers import (
    CreateHomeworkSerializer,
    UpdateHomeworkSerializer,
    DeleteHomeworkSerializer,
    CreateClassSerializer,
    DeleteCourseSerializer,
    CreateCalendarEventSerializer,
    UpdateCalendarEventSerializer,
    DeleteCalendarEventSerializer,
    GetCalendarEventsSerializer,
    ManageCalendarAttendeesSerializer,
    SubmissionsStatusSerializer, 
    CreateNoteSerializer,
    GetNotesSerializer,
    UpdateNoteSerializer,
    DeleteNoteSerializer,
    GetNoteDetailSerializer
)
from .models import CourseSchedule, StudentNote

# Helper functions to reduce code duplication
def get_user_and_credentials(line_user_id):
    """
    取得用戶和Google憑證的helper function
    Returns: (prof, creds) or Response (if error)
    """
    prof = get_object_or_404(LineProfile, line_user_id=line_user_id)
    
    try:
        creds = get_valid_google_credentials(prof)
        return prof, creds
    except Exception as e:
        return Response({
            "error": "Google 授權失敗",
            "message": "無法獲取 Google 憑證，請檢查您的授權狀態",
            "details": str(e)
        }, status=401)

def build_google_service(service_name, version, creds):
    """
    建立Google service的helper function
    """
    return build(service_name, version, credentials=creds, cache_discovery=False)

def validate_course_exists(service, course_id):
    """
    驗證課程是否存在的helper function
    Returns: course object or Response (if error)
    """
    try:
        course = service.courses().get(id=course_id).execute()
        return course
    except Exception as e:
        return Response({
            "error": "課程不存在或無權限訪問",
            "course_id": course_id,
            "details": str(e)
        }, status=404)

@api_view(["POST"])
@permission_classes([AllowAny])  # 生产环境建议改成 IsAuthenticated
def create_classroom(request):
    """
    n8n 呼叫此接口於 Google Classroom 建立課程，並存回本地 DB。
    POST /api/classrooms/
    body: {
      "line_user_id": "...",
      "name": "...",
      "section": "...",         # optional
      "description": "...",     # optional
    }
    """
    ser = CreateClassSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    # 取得用戶和憑證
    result = get_user_and_credentials(ser.validated_data["line_user_id"])
    if isinstance(result, Response):  # 如果返回錯誤
        return result
    prof, creds = result

    # 建立 Google Classroom service
    service = build_google_service("classroom", "v1", creds)

    # API 呼叫 payload：必須指定 ownerId 為老師的 Google email
    course_body = {
        "name":        ser.validated_data["name"],
        "section":     ser.validated_data.get("section", ""),
        "description": ser.validated_data.get("description", ""),
        "ownerId":     prof.email,
        "courseState": "ACTIVE",  # 直接啟用課程
    }

    # 呼叫 Google Classroom 建課
    gc_course = service.courses().create(body=course_body).execute()

    # 存回本地資料庫
    course = Course.objects.create(
        owner           = prof,
        name            = ser.validated_data["name"],
        section         = ser.validated_data.get("section", ""),
        description     = ser.validated_data.get("description", ""),
        gc_course_id    = gc_course["id"],
        enrollment_code = gc_course.get("enrollmentCode", "")
    )

    # 發送課程創建成功的Flex Message給老師
    try:
        send_course_created_message(
            line_user_id=prof.line_user_id,
            course_name=course.name,
            gc_course_id=course.gc_course_id,
            enrollment_code=course.enrollment_code,
            alternate_link=gc_course.get("alternateLink")
        )
    except Exception as e:
        print(f"發送課程創建消息失敗: {e}")
        # 不影響API回應，繼續執行

    return Response({
        "course_id":      course.id,
        "gc_course_id":   course.gc_course_id,
        "enrollmentCode": course.enrollment_code,
        "alternate_link": gc_course.get("alternateLink"),
    }, status=201)


@api_view(["POST"])
@permission_classes([AllowAny])
def create_homework(request):
    """
    POST /api/homeworks/
    {
      "line_user_id": "...",
      "course_id": "...",  # 可以是單一課程ID或逗號分隔的多個課程ID
      "title": "...",
      "due": "YYYY-MM-DD" 或 "MM/DD/YYYY"
    }
    """
    ser = CreateHomeworkSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    # 取得用戶和憑證
    result = get_user_and_credentials(ser.validated_data["line_user_id"])
    if isinstance(result, Response):
        return result
    prof, creds = result
    
    service = build_google_service("classroom", "v1", creds)

    # 分割課程ID（支援多個課程）
    course_ids = [cid.strip() for cid in ser.validated_data["course_id"].split(",")]
    
    # 驗證課程ID不是placeholder
    for course_id in course_ids:
        if course_id == "placeholder_course_id" or not course_id or course_id.strip() == "":
            return Response({
                "error": "無效的課程ID",
                "course_id": course_id,
                "message": "請選擇有效的課程ID"
            }, status=400)
    
    # parse due date
    dt = date_parser.parse(ser.validated_data["due"])
    due_date = dt.date()
    
    # 格式化日期顯示
    formatted_due_date = due_date.strftime("%Y-%m-%d")

    body = {
        "title": ser.validated_data["title"],
        "workType": "ASSIGNMENT",  # 必填！
        "state": "PUBLISHED",
        "dueDate": {
            "year":  due_date.year,
            "month": due_date.month,
            "day":   due_date.day,
        },
        "dueTime": {
            "hours": 23,
            "minutes": 59
        }
    }
    
    # 如果有 description，加入 body
    if "description" in ser.validated_data:
        body["description"] = ser.validated_data["description"]
        print(f"加入作業說明: {ser.validated_data['description']}")
    else:
        print("沒有作業說明")
    
    results = []
    errors = []
    
    # 為每個課程創建作業
    for course_id in course_ids:
        try:
            # 先驗證課程是否存在
            course = service.courses().get(id=course_id).execute()
            
            # 創建作業
            gc_hw = service.courses().courseWork().create(
                courseId=course_id,
                body=body
            ).execute()
            
            # 儲存到本地資料庫
            try:
                # 獲取對應的課程
                local_course = Course.objects.get(gc_course_id=course_id)
                
                # 解析到期時間
                due_time = None
                if due_date:
                    from datetime import time
                    due_time = time(23, 59)  # 23:59
                
                # 創建本地作業記錄
                homework = Homework.objects.create(
                    course=local_course,
                    owner=prof,
                    title=ser.validated_data["title"],
                    description=ser.validated_data.get("description", ""),
                    gc_homework_id=gc_hw["id"],
                    gc_course_id=course_id,
                    state="PUBLISHED",
                    work_type="ASSIGNMENT",
                    due_date=due_date,
                    due_time=due_time,
                    max_points=None
                )
                print(f"作業已儲存到本地資料庫: {homework.id}")
                
            except Course.DoesNotExist:
                print(f"警告: 找不到對應的本地課程記錄: {course_id}")
            except Exception as e:
                print(f"警告: 儲存到本地資料庫失敗: {e}")
            
            # 記錄成功結果
            results.append({
                "course_id": course_id,
                "coursework_id": gc_hw["id"],
                "title": gc_hw["title"],
                "dueDate": gc_hw.get("dueDate"),
                "description": gc_hw.get("description", ""),
                "course_name": course.get("name", "未知課程"),
                "alternate_link": gc_hw.get("alternateLink")
            })
            
        except Exception as e:
            error_msg = f"課程 {course_id} 創建作業失敗: {str(e)}"
            errors.append({
                "course_id": course_id,
                "error": error_msg
            })
            print(error_msg)
    
    # 如果有錯誤，返回錯誤信息
    if errors and not results:
        return Response({
            "error": "所有課程創建作業都失敗",
            "errors": errors,
            "course_ids": course_ids
        }, status=400)
    
    # 發送作業創建成功的Flex Message給老師
    try:
        if len(results) == 1:
            # 單一課程 → 私訊老師 + 推播到綁定群組
            result = results[0]
            send_homework_created_message(
                line_user_id=prof.line_user_id,
                homework_title=ser.validated_data["title"],
                course_name=result["course_name"],
                due_date=formatted_due_date,
                gc_course_id=result["course_id"],
                alternate_link=result.get("alternate_link"),
                homework_description=result.get("description", "") or ser.validated_data.get("description", "") or "請完成指定的作業內容"
            )

            group_ids = list(GroupBinding.objects.filter(course_id=result["course_id"]).values_list("group_id", flat=True))
            for gid in group_ids:
                try:
                    send_homework_created_message(
                        line_user_id=gid,
                        homework_title=ser.validated_data["title"],
                        course_name=result["course_name"],
                        due_date=formatted_due_date,
                        gc_course_id=result["course_id"],
                        alternate_link=result.get("alternate_link"),
                        homework_description=result.get("description", "") or ser.validated_data.get("description", "") or "請完成指定的作業內容"
                    )
                except Exception as e:
                    print(f"群組推播作業 Flex 失敗 ({gid}): {e}")
        else:
            # 多個課程 → 私訊老師總覽 + 各課程推播到其綁定群組
            send_multiple_homework_created_message(
                line_user_id=prof.line_user_id,
                homework_title=ser.validated_data["title"],
                due_date=formatted_due_date,
                results=results,
                errors=errors
            )

            for r in results:
                group_ids = list(GroupBinding.objects.filter(course_id=r["course_id"]).values_list("group_id", flat=True))
                for gid in group_ids:
                    try:
                        send_homework_created_message(
                            line_user_id=gid,
                            homework_title=ser.validated_data["title"],
                            course_name=r["course_name"],
                            due_date=formatted_due_date,
                            gc_course_id=r["course_id"],
                            alternate_link=r.get("alternate_link"),
                            homework_description=r.get("description", "") or ser.validated_data.get("description", "") or "請完成指定的作業內容"
                        )
                    except Exception as e:
                        print(f"群組推播作業 Flex 失敗 ({gid}): {e}")
            
    except Exception as e:
        print(f"發送作業創建消息或群組公告失敗: {e}")
        # 不影響API回應，繼續執行

    # 返回結果
    if len(results) == 1:
        # 單一課程結果
        result = results[0]
        return Response({
            "coursework_id": result["coursework_id"],
            "title": result["title"],
            "dueDate": result["dueDate"],
            "description": result["description"],
            "request_description": ser.validated_data.get("description", ""),
        }, status=201)
    else:
        # 多個課程結果
        return Response({
            "message": f"成功為 {len(results)}/{len(course_ids)} 個課程創建作業",
            "results": results,
            "errors": errors,
            "total_courses": len(course_ids),
            "successful_courses": len(results),
            "failed_courses": len(errors)
        }, status=201)

@api_view(["PATCH"])
@permission_classes([AllowAny])
def update_homework(request):
    """
    PATCH /api/homeworks/
    {
      "line_user_id": "...",
      "course_id": "...",
      "coursework_id": "...",
      "title": "...",      # optional
      "due": "YYYY-MM-DD"  # optional
    }
    """
    ser = UpdateHomeworkSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    # 取得用戶和憑證
    result = get_user_and_credentials(ser.validated_data["line_user_id"])
    if isinstance(result, Response):
        return result
    prof, creds = result
    
    service = build_google_service("classroom", "v1", creds)

    # 驗證課程是否存在
    course_result = validate_course_exists(service, ser.validated_data["course_id"])
    if isinstance(course_result, Response):
        return course_result
    course = course_result

    body = {}
    update_mask = []

    if "title" in ser.validated_data:
        body["title"] = ser.validated_data["title"]
        update_mask.append("title")
    if "description" in ser.validated_data:
        body["description"] = ser.validated_data["description"]
        update_mask.append("description")
    if "due" in ser.validated_data:
        dt = date_parser.parse(ser.validated_data["due"])
        d = dt.date()
        body["dueDate"] = {"year": d.year, "month": d.month, "day": d.day}
        body["dueTime"] = {"hours": 23, "minutes": 59}
        update_mask.append("dueDate")
        update_mask.append("dueTime")

    try:
        gc_hw = service.courses().courseWork().patch(
            courseId=ser.validated_data["course_id"],
            id=ser.validated_data["coursework_id"],
            updateMask=",".join(update_mask),
            body=body
        ).execute()
    except Exception as e:
        return Response({
            "error": "更新作業失敗",
            "course_id": ser.validated_data["course_id"],
            "coursework_id": ser.validated_data["coursework_id"],
            "details": str(e)
        }, status=400)

    return Response({
        "coursework_id": gc_hw["id"],
        "title":         gc_hw["title"],
        "dueDate":       gc_hw.get("dueDate"),
    }, status=200)

@api_view(["DELETE"])
@permission_classes([AllowAny])
def delete_homework(request):
    """
    DELETE /api/homeworks/
    {
      "line_user_id":"...",
      "course_id":"...",
      "coursework_id":"..."
    }
    """
    ser = DeleteHomeworkSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    # 取得用戶和憑證
    result = get_user_and_credentials(ser.validated_data["line_user_id"])
    if isinstance(result, Response):
        return result
    prof, creds = result
    
    service = build_google_service("classroom", "v1", creds)

    # 驗證課程是否存在
    course_result = validate_course_exists(service, ser.validated_data["course_id"])
    if isinstance(course_result, Response):
        return course_result
    course = course_result

    try:
        service.courses().courseWork().delete(
            courseId=ser.validated_data["course_id"],
            id=ser.validated_data["coursework_id"]
        ).execute()
    except Exception as e:
        return Response({
            "error": "刪除作業失敗",
            "course_id": ser.validated_data["course_id"],
            "coursework_id": ser.validated_data["coursework_id"],
            "details": str(e)
        }, status=400)

    return Response(status=204)

@api_view(["GET"])
@permission_classes([AllowAny])
def check_course(request):
    """
    GET /api/check-course/?course_id=xxx&line_user_id=xxx
    檢查課程是否存在且用戶有權限訪問
    """
    course_id = request.GET.get("course_id")
    line_user_id = request.GET.get("line_user_id")
    
    if not course_id or not line_user_id:
        return Response({
            "error": "缺少必要參數",
            "required": ["course_id", "line_user_id"]
        }, status=400)
    
    try:
        # 檢查用戶是否存在
        prof = get_object_or_404(LineProfile, line_user_id=line_user_id)
        
        # 檢查本地資料庫中是否有此課程
        try:
            local_course = Course.objects.get(gc_course_id=course_id)
            local_exists = True
            local_owner = local_course.owner.line_user_id
        except Course.DoesNotExist:
            local_exists = False
            local_owner = None
        
        # 檢查Google Classroom中的課程
        try:
            creds = get_valid_google_credentials(prof)
            service = build_google_service("classroom", "v1", creds)
        except Exception as e:
            return Response({
                "error": "Google 授權失敗",
                "message": "無法獲取 Google 憑證，請檢查您的授權狀態",
                "details": str(e)
            }, status=401)
        
        try:
            gc_course = service.courses().get(id=course_id).execute()
            gc_exists = True
            gc_owner = gc_course.get("ownerId")
        except Exception as e:
            gc_exists = False
            gc_owner = None
            gc_error = str(e)
        
        return Response({
            "course_id": course_id,
            "line_user_id": line_user_id,
            "local_database": {
                "exists": local_exists,
                "owner": local_owner
            },
            "google_classroom": {
                "exists": gc_exists,
                "owner": gc_owner,
                "error": gc_error if not gc_exists else None
            },
            "user_role": prof.role,
            "user_email": prof.email
        })
        
    except LineProfile.DoesNotExist:
        return Response({
            "error": "用戶不存在",
            "line_user_id": line_user_id
        }, status=404)
    except Exception as e:
        return Response({
            "error": "檢查課程時發生錯誤",
            "details": str(e)
        }, status=500)

@api_view(["GET"])
@permission_classes([AllowAny])
def get_homeworks(request):
    """
    GET /api/homeworks/?course_id=xxx&line_user_id=xxx
    抓取Google Classroom課程的所有作業
    """
    course_id = request.GET.get("course_id")
    line_user_id = request.GET.get("line_user_id")
    
    if not course_id or not line_user_id:
        return Response({
            "error": "缺少必要參數",
            "required": ["course_id", "line_user_id"]
        }, status=400)
    
    try:
        # 取得用戶和憑證
        result = get_user_and_credentials(line_user_id)
        if isinstance(result, Response):
            return result
        prof, creds = result
        
        service = build_google_service("classroom", "v1", creds)
        
        # 驗證課程是否存在
        course_result = validate_course_exists(service, course_id)
        if isinstance(course_result, Response):
            return course_result
        course = course_result
        
        # 抓取課程的所有作業
        try:
            course_works = service.courses().courseWork().list(courseId=course_id).execute()
            
            homeworks = []
            for work in course_works.get("courseWork", []):
                # 格式化到期時間
                due_date = work.get("dueDate")
                due_time = work.get("dueTime")
                
                formatted_due = ""
                if due_date:
                    due_str = f"{due_date['year']}-{due_date['month']:02d}-{due_date['day']:02d}"
                    if due_time:
                        due_str += f" {due_time['hours']:02d}:{due_time['minutes']:02d}"
                    else:
                        due_str += " 23:59"
                    formatted_due = due_str
                
                homework_info = {
                    "id": work.get("id"),
                    "title": work.get("title"),
                    "description": work.get("description", ""),
                    "state": work.get("state"),
                    "workType": work.get("workType"),
                    "dueDate": formatted_due,
                    "creationTime": work.get("creationTime"),
                    "updateTime": work.get("updateTime"),
                    "maxPoints": work.get("maxPoints"),
                    "assigneeMode": work.get("assigneeMode"),
                }
                homeworks.append(homework_info)
            
            return Response({
                "course_id": course_id,
                "course_name": course.get("name", ""),
                "course_section": course.get("section", ""),
                "total_homeworks": len(homeworks),
                "homeworks": homeworks
            })
            
        except Exception as e:
            err = str(e)
            # 若是權限不足或 scope 缺失，提示重新授權
            if "insufficientPermissions" in err or "Request had insufficient authentication scopes" in err:
                return Response({
                    "error": "權限不足，請重新授權以取得作業讀取權限",
                    "details": err,
                    "action": "relogin"
                }, status=401)
            return Response({
                "error": "抓取作業失敗",
                "course_id": course_id,
                "details": err
            }, status=400)
            
    except LineProfile.DoesNotExist:
        return Response({
            "error": "用戶不存在",
            "line_user_id": line_user_id
        }, status=404)
    except Exception as e:
        return Response({
            "error": "抓取作業時發生錯誤",
            "details": str(e)
        }, status=500)

@api_view(["GET"])
@permission_classes([AllowAny])
def get_courses(request):
    """
    GET /api/courses/?line_user_id=xxx
    抓取用戶的所有課程列表
    """
    line_user_id = request.GET.get("line_user_id")
    
    if not line_user_id:
        return Response({
            "error": "缺少必要參數",
            "required": ["line_user_id"]
        }, status=400)
    
    try:
        # 取得用戶和憑證
        result = get_user_and_credentials(line_user_id)
        if isinstance(result, Response):
            return result
        prof, creds = result
        
        service = build_google_service("classroom", "v1", creds)
        
        # 獲取課程列表
        courses_response = service.courses().list(
            courseStates=["ACTIVE"],
            pageSize=50  # 增加頁面大小以獲取更多課程
        ).execute()
        
        courses = courses_response.get("courses", [])
        
        # 格式化課程資料
        formatted_courses = []
        for course in courses:
            course_info = {
                "id": course.get("id"),
                "name": course.get("name", "未命名課程"),
                "section": course.get("section", ""),
                "description": course.get("description", ""),
                "ownerId": course.get("ownerId"),
                "enrollmentCode": course.get("enrollmentCode", ""),
                "courseState": course.get("courseState"),
                "creationTime": course.get("creationTime"),
                "updateTime": course.get("updateTime"),
                "teacherFolder": course.get("teacherFolder", {}),
                "courseGroup": course.get("courseGroup", {}),
                "guardiansEnabled": course.get("guardiansEnabled", False),
                "calendarId": course.get("calendarId", ""),
                "gradebookSettings": course.get("gradebookSettings", {})
            }
            formatted_courses.append(course_info)
        
        return Response({
            "line_user_id": line_user_id,
            "user_email": prof.email,
            "user_role": prof.role,
            "total_courses": len(formatted_courses),
            "courses": formatted_courses
        })
        
    except LineProfile.DoesNotExist:
        return Response({
            "error": "用戶不存在",
            "line_user_id": line_user_id
        }, status=404)
    except Exception as e:
        # 若是 OAuth 錯誤，回 401 讓前端提示重新授權
        err_text = str(e)
        if "invalid_grant" in err_text or "unauthorized_client" in err_text or "invalid_client" in err_text or "insufficientPermissions" in err_text or "invalid_credentials" in err_text or "Invalid Credentials" in err_text:
            return Response({
                "error": "Google 授權失效",
                "details": err_text,
                "action": "relogin"
            }, status=401)
        return Response({
            "error": "抓取課程列表時發生錯誤",
            "details": str(e)
        }, status=500)

@api_view(["DELETE"])
@permission_classes([AllowAny])
def delete_course(request):
    """
    DELETE /api/delete-course/
    支援兩種格式：
    1. JSON body: {"line_user_id": "...", "course_id": "..."}
    2. URL 參數: /api/delete-course/?line_user_id=...&course_id=...
    """
    # 除錯：印出請求資料
    print(f"DELETE 請求資料: {request.data}")
    print(f"請求方法: {request.method}")
    print(f"Content-Type: {request.content_type}")
    print(f"URL 參數: {request.GET}")
    
    # 嘗試從不同來源取得資料
    data = {}
    
    # 1. 先嘗試從 body 取得 JSON 資料
    if request.data:
        try:
            if isinstance(request.data, dict):
                data.update(request.data)
            else:
                import json
                body_data = json.loads(request.body.decode('utf-8'))
                data.update(body_data)
        except Exception as e:
            print(f"解析 body JSON 失敗: {e}")
    
    # 2. 如果 body 沒有資料，嘗試從 URL 參數取得
    if not data:
        line_user_id = request.GET.get('line_user_id')
        course_id = request.GET.get('course_id')
        if line_user_id and course_id:
            data = {
                'line_user_id': line_user_id,
                'course_id': course_id
            }
            print(f"從 URL 參數取得資料: {data}")
    
    # 3. 如果還是沒有資料，嘗試從 POST 資料取得（某些客戶端可能用 POST 發送 DELETE）
    if not data and request.method == "POST":
        data = request.data
        print(f"從 POST 資料取得: {data}")
    
    print(f"最終解析的資料: {data}")
    
    # 驗證必要參數
    if not data or 'line_user_id' not in data or 'course_id' not in data:
        return Response({
            "error": "缺少必要參數",
            "message": "請提供 line_user_id 和 course_id",
            "required": ["line_user_id", "course_id"],
            "received": list(data.keys()) if data else []
        }, status=400)
    
    ser = DeleteCourseSerializer(data=data)
    if not ser.is_valid():
        print(f"序列化器驗證失敗: {ser.errors}")
        return Response({
            "error": "參數驗證失敗",
            "errors": ser.errors,
            "received_data": data
        }, status=400)
    
    # 取得用戶和憑證
    try:
        result = get_user_and_credentials(ser.validated_data["line_user_id"])
        if isinstance(result, Response):
            return result
        prof, creds = result
    except Exception as e:
        print(f"找不到用戶: {ser.validated_data['line_user_id']}, 錯誤: {e}")
        return Response({
            "error": "用戶不存在",
            "line_user_id": ser.validated_data["line_user_id"],
            "details": str(e)
        }, status=404)
    
    service = build_google_service("classroom", "v1", creds)

    course_id = ser.validated_data["course_id"]
    print(f"準備刪除課程: {course_id}")

    # 驗證課程是否存在
    course_result = validate_course_exists(service, course_id)
    if isinstance(course_result, Response):
        return course_result
    course = course_result
    course_name = course.get("name", "未知課程")
    print(f"找到課程: {course_name}")

    try:
        # 刪除 Google Classroom 中的課程
        print(f"開始刪除 Google Classroom 課程: {course_id}")
        
        # 先檢查課程狀態
        course_state = course.get("courseState", "ACTIVE")
        print(f"課程狀態: {course_state}")
        
        # 如果課程是 ARCHIVED 狀態，需要先啟用再刪除
        if course_state == "ARCHIVED":
            print(f"課程已封存，先啟用課程: {course_id}")
            try:
                service.courses().patch(
                    id=course_id,
                    updateMask="courseState",
                    body={"courseState": "ACTIVE"}
                ).execute()
                print(f"課程已啟用: {course_id}")
            except Exception as e:
                print(f"啟用課程失敗: {e}")
                return Response({
                    "error": "無法啟用已封存的課程",
                    "course_id": course_id,
                    "course_name": course_name,
                    "details": str(e)
                }, status=400)
        
        # 嘗試刪除課程
        try:
            service.courses().delete(id=course_id).execute()
            print(f"Google Classroom 課程刪除成功: {course_id}")
        except Exception as delete_error:
            print(f"直接刪除失敗，嘗試先封存再刪除: {delete_error}")
            
            # 如果直接刪除失敗，嘗試先封存再刪除
            try:
                # 先封存課程
                service.courses().patch(
                    id=course_id,
                    updateMask="courseState",
                    body={"courseState": "ARCHIVED"}
                ).execute()
                print(f"課程已封存: {course_id}")
                
                # 再刪除課程
                service.courses().delete(id=course_id).execute()
                print(f"Google Classroom 課程刪除成功: {course_id}")
                
            except Exception as archive_error:
                print(f"封存後刪除也失敗: {archive_error}")
                return Response({
                    "error": "刪除課程失敗",
                    "course_id": course_id,
                    "course_name": course_name,
                    "message": "課程可能包含學生或作業，無法刪除",
                    "details": str(archive_error)
                }, status=400)
        
        # 刪除本地資料庫中的課程記錄
        try:
            local_course = Course.objects.get(gc_course_id=course_id)
            local_course.delete()
            local_deleted = True
            print(f"本地課程記錄刪除成功: {course_id}")
        except Course.DoesNotExist:
            local_deleted = False
            print(f"本地找不到課程記錄: {course_id}")
        except Exception as e:
            print(f"警告: 刪除本地課程記錄失敗: {e}")
            local_deleted = False
        
        return Response({
            "message": "課程刪除成功",
            "course_id": course_id,
            "course_name": course_name,
            "google_classroom_deleted": True,
            "local_database_deleted": local_deleted
        }, status=200)
        
    except Exception as e:
        print(f"刪除課程失敗: {course_id}, 錯誤: {e}")
        return Response({
            "error": "刪除課程失敗",
            "course_id": course_id,
            "course_name": course_name,
            "message": "課程可能包含學生或作業，無法刪除",
            "details": str(e)
        }, status=400)


# ================ Google Calendar API Functions ================

@api_view(["POST"])
@permission_classes([AllowAny])
def create_calendar_event(request):
    """
    建立 Google Calendar 事件
    POST /api/calendar/events/
    body: {
        "line_user_id": "...",
        "calendar_id": "primary",  # 可選，預設為 primary
        "summary": "事件標題",
        "description": "事件描述",  # 可選
        "start_datetime": "2024-01-15T10:00:00+08:00",
        "end_datetime": "2024-01-15T11:00:00+08:00",
        "location": "會議室A",  # 可選
        "attendees": ["user1@example.com", "user2@example.com"]  # 可選
    }
    """
    ser = CreateCalendarEventSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    
    # 取得用戶和憑證
    result = get_user_and_credentials(ser.validated_data["line_user_id"])
    if isinstance(result, Response):
        return result
    prof, creds = result
    
    # 建立 Google Calendar service
    service = build_google_service("calendar", "v3", creds)
    
    try:
        # 準備事件數據
        event_data = {
            'summary': ser.validated_data['summary'],
            'start': {
                'dateTime': ser.validated_data['start_datetime'].isoformat(),
                'timeZone': 'Asia/Taipei',
            },
            'end': {
                'dateTime': ser.validated_data['end_datetime'].isoformat(),
                'timeZone': 'Asia/Taipei',
            },
        }
        
        # 添加可選字段
        if ser.validated_data.get('description'):
            event_data['description'] = ser.validated_data['description']
        
        if ser.validated_data.get('location'):
            event_data['location'] = ser.validated_data['location']
        
        # 建立事件
        calendar_id = ser.validated_data.get('calendar_id', 'primary')
        event = service.events().insert(calendarId=calendar_id, body=event_data).execute()
        
        return Response({
            "message": "Google Calendar 事件建立成功",
            "event_id": event['id'],
            "event_link": event.get('htmlLink'),
            "summary": event['summary'],
            "start": event['start'],
            "end": event['end'],
        }, status=201)
        
    except Exception as e:
        print(f"建立 Calendar 事件失敗: {e}")
        return Response({
            "error": "建立 Calendar 事件失敗",
            "details": str(e)
        }, status=400)


@api_view(["PATCH"])
@permission_classes([AllowAny])
def update_calendar_event(request):
    """
    更新 Google Calendar 事件
    PATCH /api/calendar/events/
    body: {
        "line_user_id": "...",
        "calendar_id": "primary",  # 可選
        "event_id": "...",
        "summary": "新標題",  # 可選
        "description": "新描述",  # 可選
        "start_datetime": "2024-01-15T14:00:00+08:00",  # 可選
        "end_datetime": "2024-01-15T15:00:00+08:00",  # 可選
        "location": "新地點",  # 可選
        "attendees": ["new@example.com"]  # 可選
    }
    """
    ser = UpdateCalendarEventSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    
    # 取得用戶和憑證
    result = get_user_and_credentials(ser.validated_data["line_user_id"])
    if isinstance(result, Response):
        return result
    prof, creds = result
    
    # 建立 Google Calendar service
    service = build_google_service("calendar", "v3", creds)
    
    try:
        calendar_id = ser.validated_data.get('calendar_id', 'primary')
        event_id = ser.validated_data['event_id']
        
        # 先取得現有事件
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        
        # 更新字段
        if ser.validated_data.get('summary'):
            event['summary'] = ser.validated_data['summary']
        
        if ser.validated_data.get('description'):
            event['description'] = ser.validated_data['description']
        
        if ser.validated_data.get('location'):
            event['location'] = ser.validated_data['location']
        
        if ser.validated_data.get('start_datetime'):
            event['start'] = {
                'dateTime': ser.validated_data['start_datetime'].isoformat(),
                'timeZone': 'Asia/Taipei',
            }
        
        if ser.validated_data.get('end_datetime'):
            event['end'] = {
                'dateTime': ser.validated_data['end_datetime'].isoformat(),
                'timeZone': 'Asia/Taipei',
            }
        
        # 更新事件
        updated_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
        
        return Response({
            "message": "Google Calendar 事件更新成功",
            "event_id": updated_event['id'],
            "event_link": updated_event.get('htmlLink'),
            "summary": updated_event['summary'],
            "start": updated_event['start'],
            "end": updated_event['end'],
        }, status=200)
        
    except Exception as e:
        print(f"更新 Calendar 事件失敗: {e}")
        return Response({
            "error": "更新 Calendar 事件失敗",
            "details": str(e)
        }, status=400)


@api_view(["DELETE"])
@permission_classes([AllowAny])
def delete_calendar_event(request):
    """
    刪除 Google Calendar 事件
    DELETE /api/calendar/events/
    body: {
        "line_user_id": "...",
        "calendar_id": "primary",  # 可選
        "event_id": "..."
    }
    """
    ser = DeleteCalendarEventSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    
    # 取得用戶和憑證
    result = get_user_and_credentials(ser.validated_data["line_user_id"])
    if isinstance(result, Response):
        return result
    prof, creds = result
    
    # 建立 Google Calendar service
    service = build_google_service("calendar", "v3", creds)
    
    try:
        calendar_id = ser.validated_data.get('calendar_id', 'primary')
        event_id = ser.validated_data['event_id']
        
        # 先取得事件資訊（用於回傳）
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        event_summary = event.get('summary', 'Unknown Event')
        
        # 刪除事件
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        
        return Response({
            "message": "Google Calendar 事件刪除成功",
            "event_id": event_id,
            "event_summary": event_summary,
        }, status=200)
        
    except Exception as e:
        print(f"刪除 Calendar 事件失敗: {e}")
        return Response({
            "error": "刪除 Calendar 事件失敗",
            "details": str(e)
        }, status=400)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_calendar_events(request):
    """
    查詢 Google Calendar 事件
    GET /api/calendar/events/?line_user_id=...&calendar_id=primary&time_min=...&time_max=...&max_results=10
    """
    ser = GetCalendarEventsSerializer(data=request.GET)
    ser.is_valid(raise_exception=True)
    
    # 取得用戶和憑證
    result = get_user_and_credentials(ser.validated_data["line_user_id"])
    if isinstance(result, Response):
        return result
    prof, creds = result
    
    # 建立 Google Calendar service
    service = build_google_service("calendar", "v3", creds)
    
    try:
        calendar_id = ser.validated_data.get('calendar_id', 'primary')
        max_results = ser.validated_data.get('max_results', 10)
        
        # 準備查詢參數
        query_params = {
            'calendarId': calendar_id,
            'maxResults': max_results,
            'singleEvents': True,
            'orderBy': 'startTime'
        }
        
        if ser.validated_data.get('time_min'):
            query_params['timeMin'] = ser.validated_data['time_min'].isoformat()
        
        if ser.validated_data.get('time_max'):
            query_params['timeMax'] = ser.validated_data['time_max'].isoformat()
        
        # 查詢事件
        events_result = service.events().list(**query_params).execute()
        events = events_result.get('items', [])
        
        # 格式化回傳數據
        formatted_events = []
        for event in events:
            formatted_event = {
                'id': event['id'],
                'summary': event.get('summary', 'No Title'),
                'description': event.get('description', ''),
                'location': event.get('location', ''),
                'start': event.get('start', {}),
                'end': event.get('end', {}),
                'html_link': event.get('htmlLink', ''),
                'created': event.get('created', ''),
                'updated': event.get('updated', ''),
            }
            
            # 處理參與者
            if 'attendees' in event:
                formatted_event['attendees'] = [
                    {
                        'email': attendee.get('email', ''),
                        'response_status': attendee.get('responseStatus', 'needsAction')
                    }
                    for attendee in event['attendees']
                ]
            
            formatted_events.append(formatted_event)
        
        return Response({
            "message": "Google Calendar 事件查詢成功",
            "events_count": len(formatted_events),
            "events": formatted_events,
            "next_page_token": events_result.get('nextPageToken'),
        }, status=200)
        
    except Exception as e:
        print(f"查詢 Calendar 事件失敗: {e}")
        return Response({
            "error": "查詢 Calendar 事件失敗",
            "details": str(e)
        }, status=400)


@api_view(["POST"])
@permission_classes([AllowAny])
def manage_calendar_attendees(request):
    """
    管理 Google Calendar 事件的參與者
    POST /api/calendar/events/attendees/
    body: {
        "line_user_id": "...",
        "calendar_id": "primary",
        "event_id": "...",
        "attendees": ["new@example.com"],           # 新增
        "attendees_to_remove": ["old@example.com"]  # 移除
    }
    """
    ser = ManageCalendarAttendeesSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    
    # 取得用戶和憑證
    result = get_user_and_credentials(ser.validated_data["line_user_id"])
    if isinstance(result, Response):
        return result
    prof, creds = result
    
    # 建立 Google Calendar service
    service = build_google_service("calendar", "v3", creds)
    
    try:
        calendar_id = ser.validated_data.get('calendar_id', 'primary')
        event_id = ser.validated_data['event_id']
        
        # 先取得現有事件
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        
        # 取得現有參與者
        current_attendees = {attendee['email'] for attendee in event.get('attendees', [])}
        
        # 新增參與者
        new_attendees = ser.validated_data.get('attendees', [])
        for email in new_attendees:
            current_attendees.add(email)
            
        # 移除參與者
        attendees_to_remove = ser.validated_data.get('attendees_to_remove', [])
        for email in attendees_to_remove:
            current_attendees.discard(email)
            
        # 更新事件的參與者列表
        event['attendees'] = [{'email': email} for email in current_attendees]
        
        # 更新事件
        updated_event = service.events().update(
            calendarId=calendar_id, 
            eventId=event_id, 
            body=event,
            sendNotifications=True  # 發送通知
        ).execute()
        
        return Response({
            "message": "參與者更新成功",
            "event_id": updated_event['id'],
            "attendees": updated_event.get('attendees', [])
        }, status=200)
        
    except Exception as e:
        return Response({
            "error": "更新參與者失敗",
            "details": str(e)
        }, status=400)


@api_view(["GET", "POST"])  # 支援 GET 與 POST，便於 n8n
@permission_classes([AllowAny])
def get_submissions_status(request):
    """
    課堂作業繳交統計
    GET /api/classroom/submissions/status?line_user_id=...&course_id=...&coursework_id=...
    回傳：total、TURNED_IN、RETURNED、CREATED（未繳）、明細
    """
    params = request.GET if request.method == "GET" else request.data
    ser = SubmissionsStatusSerializer(data=params)
    ser.is_valid(raise_exception=True)

    result = get_user_and_credentials(ser.validated_data["line_user_id"])
    if isinstance(result, Response):
        return result
    prof, creds = result

    service = build_google_service("classroom", "v1", creds)
    course_id = ser.validated_data["course_id"]
    coursework_id = ser.validated_data["coursework_id"]

    try:
        resp = service.courses().courseWork().studentSubmissions().list(
            courseId=course_id,
            courseWorkId=coursework_id,
            pageSize=200
        ).execute()
        items = resp.get("studentSubmissions", [])
        counts = {"TURNED_IN": 0, "RETURNED": 0, "CREATED": 0}
        details = []
        for s in items:
            state = s.get("state", "CREATED")
            counts[state] = counts.get(state, 0) + 1
            details.append({
                "id": s.get("id"),
                "userId": s.get("userId"),
                "state": state,
                "updateTime": s.get("updateTime"),
                "late": s.get("late"),
            })
        return Response({
            "course_id": course_id,
            "coursework_id": coursework_id,
            "total": len(items),
            "counts": counts,
            "submissions": details,
        })
    except Exception as e:
        return Response({"error": "取得繳交狀態失敗", "details": str(e)}, status=400)


def _find_course_by_time_or_name(author: LineProfile, captured_at, course_id: str | None, text: str | None):
    # 1) 指定 course_id
    if course_id:
        try:
            return Course.objects.get(gc_course_id=course_id)
        except Course.DoesNotExist:
            return None
    # 2) 依時間對照課表
    if captured_at is not None:
        import pytz
        from django.utils import timezone
        local_dt = captured_at
        if timezone.is_naive(local_dt):
            local_dt = timezone.make_aware(local_dt, pytz.UTC)
        dow = local_dt.weekday()
        t = local_dt.time()
        slots = CourseSchedule.objects.filter(day_of_week=dow, start_time__lte=t, end_time__gte=t).select_related("course")
        for s in slots:
            if s.course.owner_id == author.line_user_id:
                return s.course
        if slots:
            return slots.first().course
    # 3) 依名稱包含
    if text:
        candidates = Course.objects.all()[:100]
        for c in candidates:
            if c.name and c.name in text:
                return c
    return None


@api_view(["POST"])
@permission_classes([AllowAny])
def create_note(request):
    """
    建立學生筆記並嘗試自動歸類
    POST /api/notes/
    {"line_user_id":"...","text":"...","image_url":"...","captured_at":"...","course_id":"..."}
    """
    ser = CreateNoteSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    try:
        author = LineProfile.objects.get(pk=ser.validated_data["line_user_id"])
    except LineProfile.DoesNotExist:
        return Response({"error": "line_user 不存在"}, status=404)

    text = ser.validated_data.get("text", "")
    image_url = ser.validated_data.get("image_url", "")
    captured_at = ser.validated_data.get("captured_at")
    course_id = ser.validated_data.get("course_id") or None
    note_type = ser.validated_data.get("note_type", "")
    tags = ser.validated_data.get("tags", "")
    priority = ser.validated_data.get("priority", "")

    course = _find_course_by_time_or_name(author, captured_at, course_id, text)
    classified_by = "none"
    if course_id:
        classified_by = "name"
    elif captured_at:
        classified_by = "time"

    note = StudentNote.objects.create(
        author=author,
        text=text,
        image_url=image_url,
        captured_at=captured_at,
        course=course,
        classified_by=classified_by if course else "none",
        note_type=note_type,
        tags=tags,
        priority=priority,
    )

    # 發送筆記創建成功的Flex Message
    try:
        send_note_created_message(
            line_user_id=author.line_user_id,
            note_id=note.id,
            text=note.text,
            image_url=note.image_url,
            course_name=course.name if course else "",
            note_type=note.note_type,
            tags=note.tags,
            priority=note.priority,
            classified_by=note.classified_by,
            created_at=note.created_at.isoformat()
        )
    except Exception as e:
        print(f"發送筆記創建預覽消息失敗: {e}")
        # 不影響API回應，繼續執行

    return Response({
        "id": note.id,
        "course_id": course.gc_course_id if course else None,
        "classified_by": note.classified_by,
        "note_type": note.note_type,
        "tags": note.tags,
        "priority": note.priority,
        "created_at": note.created_at,
    }, status=201)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_notes(request):
    """
    查詢筆記列表
    GET /api/notes/list/?line_user_id=...&course_id=...&start_date=...&end_date=...&limit=20&offset=0&search=...&classified_by=...
    支持多種查詢條件和分頁
    """
    ser = GetNotesSerializer(data=request.GET)
    ser.is_valid(raise_exception=True)
    
    try:
        author = LineProfile.objects.get(pk=ser.validated_data["line_user_id"])
    except LineProfile.DoesNotExist:
        return Response({"error": "用戶不存在"}, status=404)
    
    # 構建查詢條件
    filters = {"author": author}
    
    # 課程過濾
    if ser.validated_data.get("course_id"):
        try:
            course = Course.objects.get(gc_course_id=ser.validated_data["course_id"])
            filters["course"] = course
        except Course.DoesNotExist:
            pass  # 如果課程不存在，就不過濾課程
    
    # 時間範圍過濾
    if ser.validated_data.get("start_date"):
        filters["created_at__gte"] = ser.validated_data["start_date"]
    if ser.validated_data.get("end_date"):
        filters["created_at__lte"] = ser.validated_data["end_date"]
    
    # 分類方式過濾
    if ser.validated_data.get("classified_by"):
        filters["classified_by"] = ser.validated_data["classified_by"]
    
    # 筆記類型過濾
    if ser.validated_data.get("note_type"):
        filters["note_type__icontains"] = ser.validated_data["note_type"]
    
    # 優先級過濾
    if ser.validated_data.get("priority"):
        filters["priority__icontains"] = ser.validated_data["priority"]
    
    # 基本查詢
    notes = StudentNote.objects.filter(**filters).select_related("course")
    
    # 文本搜索（包含文字內容和標籤）
    if ser.validated_data.get("search"):
        from django.db.models import Q
        search_text = ser.validated_data["search"]
        notes = notes.filter(
            Q(text__icontains=search_text) | 
            Q(tags__icontains=search_text) |
            Q(note_type__icontains=search_text)
        )
    
    # 標籤過濾
    if ser.validated_data.get("tags"):
        tags = ser.validated_data["tags"]
        notes = notes.filter(tags__icontains=tags)
    
    # 總數
    total_count = notes.count()
    
    # 分頁
    offset = ser.validated_data.get("offset", 0)
    limit = ser.validated_data.get("limit", 20)
    notes = notes.order_by("-created_at")[offset:offset + limit]
    
    # 格式化數據
    formatted_notes = []
    for note in notes:
        formatted_note = {
            "id": note.id,
            "text": note.text,
            "image_url": note.image_url,
            "captured_at": note.captured_at,
            "course_id": note.course.gc_course_id if note.course else None,
            "course_name": note.course.name if note.course else None,
            "classified_by": note.classified_by,
            "note_type": note.note_type,
            "tags": note.tags,
            "priority": note.priority,
            "created_at": note.created_at,
            "updated_at": note.updated_at,
        }
        formatted_notes.append(formatted_note)
    
    return Response({
        "total_count": total_count,
        "count": len(formatted_notes),
        "offset": offset,
        "limit": limit,
        "notes": formatted_notes,
    }, status=200)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_note_detail(request):
    """
    取得單一筆記詳細資訊
    GET /api/notes/detail/?line_user_id=...&note_id=...
    """
    ser = GetNoteDetailSerializer(data=request.GET)
    ser.is_valid(raise_exception=True)
    
    try:
        author = LineProfile.objects.get(pk=ser.validated_data["line_user_id"])
    except LineProfile.DoesNotExist:
        return Response({"error": "用戶不存在"}, status=404)
    
    try:
        note = StudentNote.objects.select_related("course").get(
            id=ser.validated_data["note_id"],
            author=author
        )
    except StudentNote.DoesNotExist:
        return Response({"error": "筆記不存在或無權限訪問"}, status=404)
    
    return Response({
        "id": note.id,
        "text": note.text,
        "image_url": note.image_url,
        "captured_at": note.captured_at,
        "course_id": note.course.gc_course_id if note.course else None,
        "course_name": note.course.name if note.course else None,
        "classified_by": note.classified_by,
        "note_type": note.note_type,
        "tags": note.tags,
        "priority": note.priority,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
    }, status=200)


@api_view(["PATCH", "PUT"])
@permission_classes([AllowAny])
def update_note(request):
    """
    更新筆記
    PATCH/PUT /api/notes/
    {
        "line_user_id": "...",
        "note_id": 123,
        "text": "...",         # optional
        "image_url": "...",   # optional  
        "captured_at": "...", # optional
        "course_id": "..."    # optional
    }
    """
    ser = UpdateNoteSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    
    try:
        author = LineProfile.objects.get(pk=ser.validated_data["line_user_id"])
    except LineProfile.DoesNotExist:
        return Response({"error": "用戶不存在"}, status=404)
    
    try:
        note = StudentNote.objects.get(
            id=ser.validated_data["note_id"],
            author=author
        )
    except StudentNote.DoesNotExist:
        return Response({"error": "筆記不存在或無權限訪問"}, status=404)
    
    # 更新字段
    updated_fields = []
    
    if "text" in ser.validated_data:
        note.text = ser.validated_data["text"]
        updated_fields.append("text")
    
    if "image_url" in ser.validated_data:
        note.image_url = ser.validated_data["image_url"]
        updated_fields.append("image_url")
    
    if "captured_at" in ser.validated_data:
        note.captured_at = ser.validated_data["captured_at"]
        updated_fields.append("captured_at")
    
    if "note_type" in ser.validated_data:
        note.note_type = ser.validated_data["note_type"]
        updated_fields.append("note_type")
    
    if "tags" in ser.validated_data:
        note.tags = ser.validated_data["tags"]
        updated_fields.append("tags")
    
    if "priority" in ser.validated_data:
        note.priority = ser.validated_data["priority"]
        updated_fields.append("priority")
    
    if "course_id" in ser.validated_data:
        course_id = ser.validated_data["course_id"]
        if course_id:
            try:
                course = Course.objects.get(gc_course_id=course_id)
                note.course = course
                note.classified_by = "name"
                updated_fields.extend(["course", "classified_by"])
            except Course.DoesNotExist:
                return Response({"error": "指定的課程不存在"}, status=400)
        else:
            # 如果course_id為空字串或None，則移除課程關聯
            note.course = None
            note.classified_by = "none"
            updated_fields.extend(["course", "classified_by"])
    
    # 檢查是否還有有效內容
    if not note.text and not note.image_url:
        return Response({"error": "筆記內容不能為空，text 和 image_url 至少需要一個"}, status=400)
    
    note.save()
    
    return Response({
        "message": "筆記更新成功",
        "id": note.id,
        "updated_fields": updated_fields,
        "text": note.text,
        "image_url": note.image_url,
        "captured_at": note.captured_at,
        "course_id": note.course.gc_course_id if note.course else None,
        "course_name": note.course.name if note.course else None,
        "classified_by": note.classified_by,
        "note_type": note.note_type,
        "tags": note.tags,
        "priority": note.priority,
        "updated_at": note.updated_at,
    }, status=200)


@api_view(["DELETE"])
@permission_classes([AllowAny])
def delete_note(request):
    """
    刪除筆記
    DELETE /api/notes/
    {
        "line_user_id": "...",
        "note_id": 123
    }
    也支持URL參數：DELETE /api/notes/?line_user_id=...&note_id=...
    """
    # 支持多種數據來源
    data = {}
    
    # 1. 嘗試從 body 取得數據
    if request.data:
        data.update(request.data)
    
    # 2. 如果 body 沒有數據，嘗試從 URL 參數取得
    if not data:
        line_user_id = request.GET.get('line_user_id')
        note_id = request.GET.get('note_id')
        if line_user_id and note_id:
            data = {
                'line_user_id': line_user_id,
                'note_id': int(note_id)
            }
    
    ser = DeleteNoteSerializer(data=data)
    ser.is_valid(raise_exception=True)
    
    try:
        author = LineProfile.objects.get(pk=ser.validated_data["line_user_id"])
    except LineProfile.DoesNotExist:
        return Response({"error": "用戶不存在"}, status=404)
    
    try:
        note = StudentNote.objects.get(
            id=ser.validated_data["note_id"],
            author=author
        )
    except StudentNote.DoesNotExist:
        return Response({"error": "筆記不存在或無權限訪問"}, status=404)
    
    # 保存刪除前的資訊用於回應
    note_info = {
        "id": note.id,
        "text": note.text,
        "image_url": note.image_url,
        "course_name": note.course.name if note.course else None,
        "created_at": note.created_at,
    }
    
    # 刪除筆記
    note.delete()
    
    return Response({
        "message": "筆記刪除成功",
        "deleted_note": note_info,
    }, status=200)



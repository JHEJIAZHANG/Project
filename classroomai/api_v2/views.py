from rest_framework import viewsets, status, filters, parsers
from rest_framework.decorators import action, api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from datetime import timedelta, datetime
import uuid
import os
import traceback
from .models import CourseV2, AssignmentV2, ExamV2, NoteV2, FileAttachment, CustomCategory, CustomTodoItem
from .serializers import (
    CourseSerializer,
    AssignmentSerializer,
    ExamSerializer,
    NoteSerializer,
    FileAttachmentSerializer,
    CustomCategorySerializer,
    CustomTodoItemSerializer,
)
from user.models import LineProfile
from .authentication import LineUserAuthentication
from services.recommendation import build_query, fetch_candidates, rerank, diversify_by_source, fallback_wiki_and_video
from services.importers import parse_courses_csv, parse_courses_ical, parse_courses_xlsx, parse_courses_xls


class LineUserViewSetMixin:
    """
    ViewSet mixin 為了處理 LINE 用戶認證
    直接使用現有的 LINE bot 認證系統
    支持自動創建測試用戶
    """
    
    def get_line_profile(self):
        """獲取當前用戶的 LineProfile，如果不存在則自動創建"""
        # 從 HTTP 頭部獲取 LINE 用戶 ID
        line_user_id = self.request.META.get('HTTP_X_LINE_USER_ID')
        
        # 某些瀏覽器或代理可能重複附帶 header，形如 "id1, id1"
        if line_user_id and ',' in line_user_id:
            line_user_id = line_user_id.split(',')[0].strip()
        
        # 如果頭部中沒有，則從查詢參數獲取
        if not line_user_id:
            line_user_id = self.request.query_params.get('line_user_id')
        
        # 防呆：資料庫欄位長度 50，避免超長造成 500
        if line_user_id:
            line_user_id = line_user_id.strip()[:50]
            
        print(f"🔍 正在查找用戶: {line_user_id}")
            
        if not line_user_id:
            print("❌ 未找到用戶ID")
            return None
            
        try:
            # 直接使用 LINE User ID 查找 LineProfile
            line_profile = LineProfile.objects.get(line_user_id=line_user_id)
            print(f"✅ 找到已存在用戶: {line_profile.name} ({line_user_id})")
            return line_profile
        except LineProfile.DoesNotExist:
            print(f"❓ 用戶不存在，嘗試創建: {line_user_id}")
            # 允許任何提供的 ID（含 guest- / test_user_）自動建立訪客帳號，方便前端無 LINE 連結測試
            default_name = '訪客使用者'
            if line_user_id.startswith('test_user_'):
                display_names = {
                    'test_user_001': '張三同學',
                    'test_user_002': '李四老師',
                    'test_user_003': '王五助教',
                }
                default_name = display_names.get(line_user_id, f'測試用戶_{line_user_id[-3:]}')
            elif line_user_id.startswith('guest-'):
                default_name = '訪客使用者'
            else:
                # 其他自訂 ID 也允許建立，名稱以 ID 後三碼區分
                try:
                    default_name = f'訪客_{line_user_id[-3:]}'
                except Exception:
                    default_name = '訪客使用者'

            line_profile = LineProfile.objects.create(
                line_user_id=line_user_id,
                name=default_name,
                role='student'
            )
            print(f"✅ 自動創建用戶: {default_name} ({line_user_id})")
            return line_profile


class CourseViewSet(LineUserViewSetMixin, viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = []  # 簡化權限檢查
    authentication_classes = []  # 使用現有的 LINE 認證
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'instructor', 'classroom']
    ordering_fields = ['title', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        line_profile = self.get_line_profile()
        if line_profile:
            return CourseV2.objects.filter(user=line_profile)
        return CourseV2.objects.none()

    def create(self, request, *args, **kwargs):
        try:
            line_profile = self.get_line_profile()
            if not line_profile:
                return Response({'error': '無法獲取LINE用戶資料'}, status=status.HTTP_401_UNAUTHORIZED)

            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({'error': '資料驗證失敗', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            # 寫入使用者並保存
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            print("[courses.create] error:", e)
            import traceback as _tb
            _tb.print_exc()
            return Response({'error': '建立課程失敗', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        line_profile = self.get_line_profile()
        serializer.save(user=line_profile)
        if line_profile:
            print(f"✅ 為用戶 {line_profile.name} ({line_profile.line_user_id}) 創建資料")
    
    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """
        批量刪除課程
        接受 course_ids 陣列作為請求體
        """
        line_profile = self.get_line_profile()
        if not line_profile:
            return Response(
                {'error': '用戶未找到'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        course_ids = request.data.get('course_ids', [])
        if not course_ids:
            return Response(
                {'error': '請提供要刪除的課程ID列表'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(course_ids, list):
            return Response(
                {'error': 'course_ids 必須是陣列格式'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 驗證課程ID格式
        valid_course_ids = []
        for course_id in course_ids:
            try:
                uuid.UUID(course_id)
                valid_course_ids.append(course_id)
            except (ValueError, TypeError):
                continue
        
        if not valid_course_ids:
            return Response(
                {'error': '無效的課程ID格式'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 查找並刪除課程
        courses_to_delete = CourseV2.objects.filter(
            id__in=valid_course_ids,
            user=line_profile
        )
        
        deleted_count = courses_to_delete.count()
        if deleted_count == 0:
            return Response(
                {'error': '未找到要刪除的課程'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 執行刪除
        courses_to_delete.delete()
        
        return Response({
            'message': f'成功刪除 {deleted_count} 門課程',
            'deleted_count': deleted_count,
            'deleted_course_ids': valid_course_ids[:deleted_count]
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['delete'], url_path='delete-all')
    def delete_all(self, request):
        """
        刪除用戶的所有課程
        """
        line_profile = self.get_line_profile()
        if not line_profile:
            return Response(
                {'error': '用戶未找到'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # 確認參數
        confirm = request.query_params.get('confirm', 'false').lower()
        if confirm != 'true':
            return Response(
                {'error': '請添加 ?confirm=true 參數來確認刪除所有課程'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 獲取所有課程
        all_courses = CourseV2.objects.filter(user=line_profile)
        total_count = all_courses.count()
        
        if total_count == 0:
            return Response(
                {'message': '沒有課程需要刪除'}, 
                status=status.HTTP_200_OK
            )
        
        # 執行刪除
        all_courses.delete()
        
        return Response({
            'message': f'成功刪除所有 {total_count} 門課程',
            'deleted_count': total_count
        }, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Apply additional filters
        search = request.query_params.get('search', None)
        from_date = request.query_params.get('from', None)
        to_date = request.query_params.get('to', None)
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(instructor__icontains=search) |
                Q(classroom__icontains=search)
            )
            
        if from_date:
            queryset = queryset.filter(created_at__gte=from_date)
            
        if to_date:
            queryset = queryset.filter(created_at__lte=to_date)
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ExamViewSet(LineUserViewSetMixin, viewsets.ModelViewSet):
    serializer_class = ExamSerializer
    permission_classes = []  # 簡化權限檢查
    authentication_classes = []  # 使用現有的 LINE 認證
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['exam_date', 'created_at', 'updated_at']
    ordering = ['exam_date']

    def get_queryset(self):
        line_profile = self.get_line_profile()
        if line_profile:
            queryset = ExamV2.objects.filter(user=line_profile)
        else:
            queryset = ExamV2.objects.none()
        
        # Apply filters
        course_id = self.request.query_params.get('courseId', None)
        status_filter = self.request.query_params.get('status', None)
        from_date = self.request.query_params.get('from', None)
        to_date = self.request.query_params.get('to', None)
        upcoming_days = self.request.query_params.get('upcomingWithinDays', None)
        
        if course_id:
            queryset = queryset.filter(course_id=course_id)
            
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        if from_date:
            queryset = queryset.filter(exam_date__gte=from_date)
            
        if to_date:
            queryset = queryset.filter(exam_date__lte=to_date)
            
        if upcoming_days:
            days = int(upcoming_days)
            now = timezone.now()
            end_date = now + timedelta(days=days)
            queryset = queryset.filter(exam_date__gte=now, exam_date__lte=end_date)
            
        return queryset

    def perform_create(self, serializer):
        line_profile = self.get_line_profile()
        if line_profile:
            serializer.save(user=line_profile)
        else:
            raise ValueError("無法獲取LINE用戶資料")

    @action(detail=True, methods=['post'])
    def status(self, request, pk=None):
        exam = self.get_object()
        status_value = request.data.get('status')
        
        if not status_value:
            return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        if status_value not in [choice[0] for choice in ExamV2._meta.get_field('status').choices]:
            return Response({'error': 'Invalid status value'}, status=status.HTTP_400_BAD_REQUEST)
            
        exam.status = status_value
        exam.save()
        
        serializer = self.get_serializer(exam)
        return Response(serializer.data)


class AssignmentViewSet(LineUserViewSetMixin, viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = []  # 簡化權限檢查
    authentication_classes = []  # 使用現有的 LINE 認證
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'created_at', 'updated_at']
    ordering = ['due_date']

    def get_queryset(self):
        line_profile = self.get_line_profile()
        if line_profile:
            queryset = AssignmentV2.objects.filter(user=line_profile)
        else:
            queryset = AssignmentV2.objects.none()
        
        # Apply filters
        course_id = self.request.query_params.get('courseId', None)
        status_filter = self.request.query_params.get('status', None)
        from_date = self.request.query_params.get('from', None)
        to_date = self.request.query_params.get('to', None)
        upcoming_days = self.request.query_params.get('upcomingWithinDays', None)
        search = self.request.query_params.get('search', None)
        
        if course_id:
            queryset = queryset.filter(course_id=course_id)
            
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        if from_date:
            queryset = queryset.filter(due_date__gte=from_date)
            
        if to_date:
            queryset = queryset.filter(due_date__lte=to_date)
            
        if upcoming_days:
            days = int(upcoming_days)
            now = timezone.now()
            end_date = now + timedelta(days=days)
            queryset = queryset.filter(due_date__gte=now, due_date__lte=end_date)
            
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
            
        return queryset

    def perform_create(self, serializer):
        line_profile = self.get_line_profile()
        if line_profile:
            serializer.save(user=line_profile)
        else:
            raise ValueError("無法獲取LINE用戶資料")

    @action(detail=False, methods=['post'], url_path='quick-add')
    def quick_add(self, request):
        """一句話快速新增：例如「下週三晚上交 網路作業」
        極簡解析：
        - 先找日期關鍵詞（今天/明天/後天/下週X/週X/下週三等）
        - 找時間（HH:MM / 晚上/下午 => 使用 20:00/15:00 預設）
        - 其餘文字作為標題
        """
        line_profile = self.get_line_profile()
        if not line_profile:
            return Response({'error': '無法獲取LINE用戶資料'}, status=status.HTTP_401_UNAUTHORIZED)

        text = (request.data.get('text') or '').strip()
        course_id = (request.data.get('course') or '').strip() or None
        if not text:
            return Response({'error': '請提供 text'}, status=status.HTTP_400_BAD_REQUEST)

        import re
        now = timezone.now()
        due = None

        # 日詞
        m = re.search(r'(今天|明天|後天|下?週[一二三四五六日天])', text)
        if m:
            w = m.group(1)
            delta = 0
            if w == '明天':
                delta = 1
            elif w == '後天':
                delta = 2
            elif '週' in w or '天' in w:
                mapw = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'日':0,'天':0}
                target = mapw[w[-1]]
                cur = now.weekday() if now.weekday()!=6 else 0
                # 下週或本週
                k = (target - cur) % 7
                if k == 0:
                    k = 7
                if w.startswith('下'):
                    k += 7
                delta = k
            due_date = now + timedelta(days=delta)
        else:
            due_date = now + timedelta(days=2)

        # 時間
        t = re.search(r'(\d{1,2}):(\d{2})', text)
        if t:
            hh, mm = int(t.group(1)), int(t.group(2))
        else:
            if '晚上' in text or '夜' in text:
                hh, mm = 20, 0
            elif '下午' in text:
                hh, mm = 15, 0
            else:
                hh, mm = 23, 59
        due = due_date.replace(hour=hh, minute=mm, second=0, microsecond=0)

        # 標題
        title = re.sub(r'\s+', ' ', re.sub(r'(今天|明天|後天|下?週[一二三四五六日天])|\d{1,2}:\d{2}|(晚上|下午|早上)', '', text)).strip() or '未命名代辦'

        # 若未指定課程，使用使用者第一門課；若不存在則自動建立「未分類」
        if not course_id:
            first = CourseV2.objects.filter(user=line_profile).only('id', 'title').first()
            if not first:
                first = CourseV2.objects.create(user=line_profile, title='未分類', description='', instructor='', classroom='')
            course_id = str(first.id)

        obj = AssignmentV2.objects.create(
            user=line_profile,
            course_id=course_id,
            title=title[:255],
            description='',
            due_date=due,
            type='assignment',
            status='pending',
        )
        return Response(AssignmentSerializer(obj).data, status=201)

    @action(detail=True, methods=['post'])
    def status(self, request, pk=None):
        assignment = self.get_object()
        status_value = request.data.get('status')
        
        if not status_value:
            return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        if status_value not in [choice[0] for choice in AssignmentV2._meta.get_field('status').choices]:
            return Response({'error': 'Invalid status value'}, status=status.HTTP_400_BAD_REQUEST)
            
        assignment.status = status_value
        assignment.save()
        
        serializer = self.get_serializer(assignment)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def recommendations(self, request, pk=None):
        try:
            assignment = self.get_object()
            title = assignment.title or ""
            desc = assignment.description or ""
            user_q = (request.query_params.get('q') or '').strip()
            if user_q:
                query = user_q
                print(f"[rec] override query via 'q': {query}")
                assignment_text = user_q
            else:
                query = build_query(title, desc)
                assignment_text = f"{title} {desc}"

            try:
                candidates = fetch_candidates(query)
            except Exception as e:
                print(f"[rec] fetch_candidates error: {e}")
                candidates = []
            print(f"[rec] candidates total={len(candidates)} by source:")
            tmp = {}
            for it in candidates:
                s = (it.get('source') or '').lower()
                tmp[s] = tmp.get(s, 0) + 1
            print(f"[rec] candidates sources: {tmp}")

            try:
                ranked = rerank(assignment_text, candidates)
            except Exception as e:
                print(f"[rec] rerank error: {e}")
                ranked = candidates
            print(f"[rec] ranked total={len(ranked)}")

            try:
                limit = int(request.query_params.get('limit', '6'))
            except Exception:
                limit = 6
            try:
                per_source = int(request.query_params.get('per_source', '3'))
            except Exception:
                per_source = 3

            only = (request.query_params.get('only') or '').lower().strip()
            if only in {'perplexity', 'youtube'}:
                ranked = [it for it in ranked if (it.get('source') or '').lower() == only]
                print(f"[rec] ONLY filter applied: {only}, items={len(ranked)}")

            try:
                diversified = diversify_by_source(ranked, max_total=limit, per_source_limit=per_source)
            except Exception as e:
                print(f"[rec] diversify error: {e}")
                diversified = ranked[:limit]
            print(f"[rec] diversified total={len(diversified)} per_source={per_source} limit={limit}")

            src_counts = {}
            for it in diversified:
                src = (it.get("source") or "").lower()
                src_counts[src] = src_counts.get(src, 0) + 1
            print(f"[rec] diversified sources: {src_counts}")

            return Response({
                "assignment": str(assignment.id),
                "query": query,
                "results": diversified,
                "meta": {"sources": src_counts}
            })
        except Exception as e:
            print("[rec] outer error:", e)
            import traceback as _tb
            _tb.print_exc()
            # 絕不再 500，回保底資料
            from services.recommendation import fallback_wiki_and_video
            safe_query = request.query_params.get('q') or ''
            fbq = safe_query or (getattr(assignment, 'title', '') or '')
            try:
                items = fallback_wiki_and_video(fbq or 'learning')
            except Exception:
                items = []
            return Response({
                "assignment": str(getattr(assignment, 'id', '')),
                "query": fbq,
                "results": items,
                "meta": {"sources": {i.get('source','unknown'): 1 for i in items}}
            }, status=200)


# 筆記功能已整合至 course 應用中
# 請使用 course.views 中的相關 API：
# - POST /api/notes/ - 創建筆記
# - GET /api/notes/list/ - 取得筆記列表
# - GET /api/notes/detail/ - 取得單一筆記
# - PATCH /api/notes/ - 更新筆記
# - DELETE /api/notes/ - 刪除筆記
# - POST /api/files/ - 上傳文件附件

class NoteViewSet(LineUserViewSetMixin, viewsets.ModelViewSet):
    """
    整合筆記功能 - 使用 course.models.StudentNote
    支援附件顯示和管理
    """
    permission_classes = []  # 簡化權限檢查
    authentication_classes = []  # 使用現有的 LINE 認證
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        # 使用動態序列化器來支援 StudentNote
        from rest_framework import serializers
        from course.models import StudentNote
        from .models import FileAttachment
        from .serializers import FileAttachmentSerializer
        from django.contrib.contenttypes.models import ContentType
        
        class StudentNoteSerializer(serializers.ModelSerializer):
            attachments = serializers.SerializerMethodField()
            # 回傳課程 UUID 與名稱，供前端比對/顯示
            course = serializers.SerializerMethodField()
            course_name = serializers.SerializerMethodField()
            
            class Meta:
                model = StudentNote
                fields = ['id', 'course', 'course_name', 'title', 'content', 'attachments', 
                         'created_at', 'updated_at']
                read_only_fields = ['id', 'created_at', 'updated_at']
            
            def get_attachments(self, obj):
                # 獲取關聯的附件
                content_type = ContentType.objects.get_for_model(StudentNote)
                attachments = FileAttachment.objects.filter(
                    content_type=content_type,
                    object_id=obj.id
                )
                return FileAttachmentSerializer(attachments, many=True).data

            def _extract_course_v2_id(self, obj):
                # 後備：從 note_type 儲存的 course_v2:<uuid> 提取
                try:
                    text = getattr(obj, 'note_type', '') or ''
                    if text.startswith('course_v2:'):
                        return text.split(':', 1)[1]
                except Exception:
                    pass
                return None

            def get_course(self, obj):
                # 優先使用舊課程 FK；若無，回退讀取 course_v2:UUID
                if getattr(obj, 'course_id', None):
                    return str(obj.course_id)
                return self._extract_course_v2_id(obj)

            def get_course_name(self, obj):
                # 優先使用舊課程名稱；若無且有 course_v2 UUID，查詢 CourseV2 取得名稱
                try:
                    if getattr(obj, 'course', None):
                        return getattr(obj.course, 'name', None)
                    from .models import CourseV2
                    course_v2_id = self._extract_course_v2_id(obj)
                    if course_v2_id:
                        c = CourseV2.objects.filter(id=course_v2_id).only('title').first()
                        if c:
                            return c.title
                except Exception:
                    pass
                return None
        
        return StudentNoteSerializer

    def get_queryset(self):
        from course.models import StudentNote
        line_profile = self.get_line_profile()
        if line_profile:
            queryset = StudentNote.objects.filter(author=line_profile).select_related('course')
        else:
            queryset = StudentNote.objects.none()
        
        # Apply filters
        course_id = self.request.query_params.get('courseId', None)
        search = self.request.query_params.get('search', None)
        
        if course_id:
            queryset = queryset.filter(course__id=course_id)
            
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search)
            )
            
        return queryset

    def perform_create(self, serializer):
        from course.models import StudentNote
        from django.contrib.contenttypes.models import ContentType
        line_profile = self.get_line_profile()
        if not line_profile:
            raise ValueError("無法獲取LINE用戶資料")

        # 先建立筆記
        note = serializer.save(author=line_profile)

        # 嘗試關聯課程：支援 legacy Course 或 CourseV2 UUID（以 note_type 儲存）
        course_value = self.request.data.get('course')
        if course_value:
            try:
                # 嘗試當成 legacy Course 的主鍵
                from course.models import Course as LegacyCourse
                # 若是 UUID 會失敗，except 中處理
                legacy_course = LegacyCourse.objects.filter(id=course_value).first()
                if legacy_course:
                    note.course = legacy_course
                    note.save()
                else:
                    # 當作 CourseV2 UUID 保存於 note_type
                    from .models import CourseV2
                    if CourseV2.objects.filter(id=course_value).exists():
                        note.note_type = f"course_v2:{course_value}"
                        note.save(update_fields=['note_type'])
            except Exception:
                # 防禦性處理：若任何異常，嘗試當作 CourseV2 UUID
                try:
                    from .models import CourseV2
                    if CourseV2.objects.filter(id=course_value).exists():
                        note.note_type = f"course_v2:{course_value}"
                        note.save(update_fields=['note_type'])
                except Exception:
                    pass

        # 綁定附件（若前端帶入 attachment_ids）
        attachment_ids = self.request.data.get('attachment_ids', [])
        if isinstance(attachment_ids, list) and attachment_ids:
            content_type = ContentType.objects.get_for_model(StudentNote)
            FileAttachment.objects.filter(id__in=attachment_ids).update(
                content_type=content_type,
                object_id=note.id
            )

    def perform_update(self, serializer):
        from course.models import StudentNote
        from django.contrib.contenttypes.models import ContentType
        line_profile = self.get_line_profile()
        if not line_profile:
            raise ValueError("無法獲取LINE用戶資料")

        note = serializer.save()

        # 更新課程關聯邏輯同 create
        course_value = self.request.data.get('course', None)
        if course_value is not None:
            try:
                from course.models import Course as LegacyCourse
                legacy_course = LegacyCourse.objects.filter(id=course_value).first()
                if legacy_course:
                    note.course = legacy_course
                    # 清除 v2 標記
                    if note.note_type and note.note_type.startswith('course_v2:'):
                        note.note_type = ''
                    note.save()
                else:
                    from .models import CourseV2
                    if CourseV2.objects.filter(id=course_value).exists():
                        note.course = None
                        note.note_type = f"course_v2:{course_value}"
                        note.save()
            except Exception:
                try:
                    from .models import CourseV2
                    if CourseV2.objects.filter(id=course_value).exists():
                        note.course = None
                        note.note_type = f"course_v2:{course_value}"
                        note.save()
                except Exception:
                    pass

        # 若帶入新的附件 id，重新綁定
        attachment_ids = self.request.data.get('attachment_ids', None)
        if isinstance(attachment_ids, list):
            content_type = ContentType.objects.get_for_model(StudentNote)
            # 先清掉原關聯
            FileAttachment.objects.filter(content_type=content_type, object_id=note.id).update(
                content_type=None,
                object_id=None
            )
            if attachment_ids:
                FileAttachment.objects.filter(id__in=attachment_ids).update(
                    content_type=content_type,
                    object_id=note.id
                )

    @action(detail=True, methods=['post'], url_path='ai/summary')
    def ai_summary(self, request, pk=None):
        from course.models import StudentNote
        import os, re
        note = get_object_or_404(StudentNote, pk=pk)
        # 取純文字：剝除 HTML 標籤
        html = (note.content or '')
        text = re.sub(r'<br\s*/?>', '\n', html)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        summary = ''
        keywords = []
        print(f'[ai_summary] note_id={pk}, text_len={len(text)}, api_key_present={bool(os.getenv("Gemini_API_KEY") or os.getenv("GEMINI_API_KEY"))}')
        try:
            import json
            if os.getenv('Gemini_API_KEY') or os.getenv('GEMINI_API_KEY'):
                from services.gemini_client import get_model  # type: ignore
                model = get_model('gemini-1.5-flash')
                prompt = (
                    'Summarize the following note in Traditional Chinese within 3 bullet points, '
                    'and extract 3-6 comma-separated keywords. Output JSON only: '
                    '{"summary":["...","...","..."],"keywords":["k1","k2"]}\n\n' + text
                )
                resp = model.generate_content([{ 'role': 'user', 'parts': [prompt] }])
                print(f'[ai_summary] Gemini response: {resp.text[:200]}...')
                raw = (resp.text or '').strip()
                if raw.startswith('```json') and raw.endswith('```'):
                    raw = raw[7:-3].strip()
                data = json.loads(raw)
                summary = '\n'.join(data.get('summary') or [])
                keywords = data.get('keywords') or []
                print(f'[ai_summary] parsed summary={summary[:100]}..., keywords={keywords}')
            else:
                clean = text
                summary = clean[:200]
                words = [w for w in re.split(r'[^\w\u4e00-\u9fa5]+', clean) if len(w) >= 2]
                from collections import Counter
                keywords = [w for w,_ in Counter(words).most_common(5)]
                print(f'[ai_summary] fallback summary={summary[:100]}..., keywords={keywords}')
        except Exception as e:
            print('[ai_summary] error:', e)
            summary = (text or '')[:200]
            keywords = []

        return Response({'id': str(note.id), 'summary': summary, 'keywords': keywords})


class FileUploadViewSet(LineUserViewSetMixin, viewsets.ViewSet):
    permission_classes = []  # 簡化權限檢查
    authentication_classes = []  # 使用現有的 LINE 認證
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    
    def create(self, request):
        """標準的 POST 方法來上傳檔案"""
        line_profile = self.get_line_profile()
        if not line_profile:
            return Response({'error': '無法獲取LINE用戶資料'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # 取得關聯物件 ID
        course_id = request.data.get('courseId')
        assignment_id = request.data.get('assignmentId')
        exam_id = request.data.get('examId')
        note_id = request.data.get('noteId')
        
        # 檢查是否有上傳檔案
        if 'file' not in request.FILES:
            return Response({'error': '沒有上傳檔案'}, status=status.HTTP_400_BAD_REQUEST)
            
        file = request.FILES['file']

        # 大小限制（保險）：優先讀取環境變數或 settings 上限
        max_file_size = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 20 * 1024 * 1024)
        if hasattr(file, 'size') and file.size and file.size > max_file_size:
            return Response({
                'error': '檔案過大',
                'maxSize': max_file_size,
                'maxSizeMB': round(max_file_size / (1024 * 1024), 2)
            }, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        
        # 產生唯一檔名
        ext = os.path.splitext(file.name)[1]
        unique_filename = f"{uuid.uuid4()}{ext}"
        
        # 儲存檔案到 media 目錄
        if not hasattr(settings, 'MEDIA_ROOT') or not settings.MEDIA_ROOT:
            media_root = os.path.join(settings.BASE_DIR, 'media')
        else:
            media_root = settings.MEDIA_ROOT
            
        file_path = os.path.join(media_root, unique_filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        os.makedirs(media_root, exist_ok=True)
        
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
                
        # 建立檔案附件記錄
        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        file_url = f"{media_url}{unique_filename}"
        attachment = FileAttachment.objects.create(
            name=file.name,
            size=file.size,
            type=file.content_type or 'application/octet-stream',
            url=file_url
            # content_type 和 object_id 為空，表示獨立文件
        )
        
        # 關聯到相關物件
        if note_id:
            from django.contrib.contenttypes.models import ContentType
            from course.models import StudentNote  # 使用實際的筆記模型
            try:
                # 驗證筆記存在且屬於當前用戶
                note = StudentNote.objects.get(id=note_id, author=line_profile)
                note_content_type = ContentType.objects.get_for_model(StudentNote)
                attachment.content_type = note_content_type
                attachment.object_id = note_id
                attachment.save()
            except StudentNote.DoesNotExist:
                return Response({'error': '筆記不存在或無權限訪問'}, status=status.HTTP_404_NOT_FOUND)
            
        return Response(
            FileAttachmentSerializer(attachment).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'])
    def import_courses(self, request):
        """匯入課程：支援上傳 CSV 或 iCal 檔案。
        - CSV: 欄位 title/description/instructor/classroom（不區分大小寫）
        - iCal: 取 VEVENT 的 SUMMARY/DESCRIPTION/LOCATION
        """
        line_profile = self.get_line_profile()
        if not line_profile:
            return Response({'error': '無法獲取LINE用戶資料'}, status=status.HTTP_401_UNAUTHORIZED)

        if 'file' not in request.FILES:
            return Response({'error': '沒有上傳檔案'}, status=status.HTTP_400_BAD_REQUEST)
        file = request.FILES['file']
        name = (file.name or '').lower()
        data = file.read()
        
        print(f'[import_courses] 檔案: {file.name}, 大小: {len(data)} bytes, 用戶: {line_profile.line_user_id}')

        try:
            items = []
            if name.endswith('.csv'):
                print('[import_courses] 使用 CSV 解析器')
                items = parse_courses_csv(data)
            elif name.endswith('.ics') or name.endswith('.ical'):
                print('[import_courses] 使用 iCal 解析器')
                items = parse_courses_ical(data)
            elif name.endswith('.xlsx'):
                print('[import_courses] 使用 XLSX 解析器')
                items = parse_courses_xlsx(data)
            elif name.endswith('.xls'):
                print('[import_courses] 使用 XLS 解析器')
                items = parse_courses_xls(data)
            else:
                return Response({'error': '不支援的檔案類型，請上傳 CSV / iCal(.ics) / Excel(.xlsx/.xls)'}, status=status.HTTP_400_BAD_REQUEST)

            print(f'[import_courses] 解析到 {len(items)} 個課程')
            created = []
            for i, it in enumerate(items):
                try:
                    obj = CourseV2.objects.create(
                        user=line_profile,
                        title=it.get('title',''),
                        description=it.get('description',''),
                        instructor=it.get('instructor',''),
                        classroom=it.get('classroom','')
                    )
                    created.append(str(obj.id))
                    print(f'[import_courses] 創建課程 {i+1}: {obj.title}')
                except Exception as e:
                    print(f'[import_courses] 創建課程 {i+1} 失敗: {e}')
                    continue
                    
            print(f'[import_courses] 成功創建 {len(created)} 個課程')
            return Response({'count': len(created), 'ids': created})
        except Exception as e:
            print(f'[import_courses] 錯誤: {e}')
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        
    @action(detail=False, methods=['post'])
    def presign(self, request):
        # In a real implementation, this would generate a pre-signed URL for direct upload
        # For simplicity, we'll just return a mock response
        filename = request.data.get('filename')
        content_type = request.data.get('contentType')
        size = request.data.get('size')
        
        if not all([filename, content_type, size]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
            
        file_id = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(minutes=10)
        
        return Response({
            'uploadUrl': f"/api/v2/files/upload/?file_id={file_id}",
            'fileId': file_id,
            'expiresAt': expires_at
        })
        
    def list(self, request):
        line_profile = self.get_line_profile()
        if not line_profile:
            return Response({'error': '無法獲取LINE用戶資料'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get filters
        course_id = request.query_params.get('courseId')
        assignment_id = request.query_params.get('assignmentId')
        exam_id = request.query_params.get('examId')
        note_id = request.query_params.get('noteId')
        
        # Base queryset - get all files
        # 簡化實現，返回所有文件
        queryset = FileAttachment.objects.all()
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FileAttachmentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = FileAttachmentSerializer(queryset, many=True)
        return Response(serializer.data)
        
    def retrieve(self, request, pk=None):
        attachment = get_object_or_404(FileAttachment, pk=pk)
        serializer = FileAttachmentSerializer(attachment)
        return Response(serializer.data)
        
    def destroy(self, request, pk=None):
        attachment = get_object_or_404(FileAttachment, pk=pk)
        attachment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomCategoryViewSet(LineUserViewSetMixin, viewsets.ModelViewSet):
    serializer_class = CustomCategorySerializer
    permission_classes = []
    authentication_classes = []
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']

    def get_queryset(self):
        line_profile = self.get_line_profile()
        if not line_profile:
            return CustomCategory.objects.none()
        return CustomCategory.objects.filter(user=line_profile)

    def perform_create(self, serializer):
        line_profile = self.get_line_profile()
        if not line_profile:
            raise ValueError('無法獲取LINE用戶資料')
        # 去除重複：同使用者 + 同名稱 視為相同分類
        from django.db import IntegrityError
        from .models import CustomCategory as _Cat
        name = (serializer.validated_data.get('name') or '').strip()
        icon = serializer.validated_data.get('icon') or 'clipboard'
        color = serializer.validated_data.get('color') or '#3b82f6'
        try:
            obj, created = _Cat.objects.get_or_create(
                user=line_profile, name=name,
                defaults={'icon': icon, 'color': color}
            )
        except IntegrityError:
            # 競態同名：回傳已存在的
            obj = _Cat.objects.filter(user=line_profile, name=name).first()
        # 將序列化器指向該物件，回傳一致格式
        serializer.instance = obj


class CustomTodoItemViewSet(LineUserViewSetMixin, viewsets.ModelViewSet):
    serializer_class = CustomTodoItemSerializer
    permission_classes = []
    authentication_classes = []
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'created_at', 'updated_at']
    ordering = ['due_date']

    def get_queryset(self):
        line_profile = self.get_line_profile()
        if not line_profile:
            return CustomTodoItem.objects.none()
        qs = CustomTodoItem.objects.filter(user=line_profile)

        category_id = self.request.query_params.get('category')
        course_id = self.request.query_params.get('course')
        status_filter = self.request.query_params.get('status')
        from_date = self.request.query_params.get('from')
        to_date = self.request.query_params.get('to')
        search = self.request.query_params.get('search')

        if category_id:
            qs = qs.filter(category_id=category_id)
        if course_id:
            qs = qs.filter(course_id=course_id)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if from_date:
            qs = qs.filter(due_date__gte=from_date)
        if to_date:
            qs = qs.filter(due_date__lte=to_date)
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        return qs

    def perform_create(self, serializer):
        line_profile = self.get_line_profile()
        if not line_profile:
            raise ValueError('無法獲取LINE用戶資料')
        serializer.save(user=line_profile)
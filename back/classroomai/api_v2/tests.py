from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from user.models import LineProfile
from .models import CourseV2, CourseScheduleV2, AssignmentV2, ExamV2, NoteV2, FileAttachment
import tempfile
from PIL import Image
import io
import json


class ApiV2TestCase(TestCase):
    def setUp(self):
        # 創建測試用戶
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # 創建LINE用戶資料
        self.line_profile = LineProfile.objects.create(
            line_user_id='test_line_user_id',
            role='student',
            name='Test User',
            email='test@example.com'
        )
        
        # 創建測試課程
        self.course = CourseV2.objects.create(
            title='測試課程',
            description='這是一個測試課程',
            instructor='測試教師',
            classroom='測試教室',
            user=self.line_profile
        )
        
        # 創建測試課程時間表
        self.schedule = CourseScheduleV2.objects.create(
            course=self.course,
            day_of_week=1,  # 星期一
            start_time='09:00:00',
            end_time='12:00:00'
        )
        
        # 創建測試作業
        self.assignment = AssignmentV2.objects.create(
            course=self.course,
            title='測試作業',
            description='這是一個測試作業',
            due_date='2023-12-31T23:59:59Z',
            user=self.line_profile
        )
        
        # 創建測試考試
        self.exam = ExamV2.objects.create(
            course=self.course,
            title='測試考試',
            description='這是一個測試考試',
            exam_date='2023-12-15T09:00:00Z',
            duration=120,
            location='測試考場',
            user=self.line_profile
        )
        
        # 創建測試筆記
        self.note = NoteV2.objects.create(
            course=self.course,
            title='測試筆記',
            content='這是一個測試筆記的內容',
            user=self.line_profile
        )
        
        # 設置API客戶端
        self.client = APIClient()
        # 使用LINE認證而不是force_authenticate
        self.client.credentials(HTTP_X_LINE_USER_ID='test_line_user_id')
    
    def test_course_list(self):
        """測試課程列表API"""
        url = reverse('course-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], '測試課程')
    
    def test_course_create(self):
        """測試創建課程API"""
        url = reverse('course-list')
        data = {
            'title': '新課程',
            'description': '這是一個新課程',
            'instructor': '新教師',
            'classroom': '新教室',
            'schedules': [
                {
                    'day_of_week': 2,
                    'start_time': '13:00:00',
                    'end_time': '16:00:00'
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CourseV2.objects.count(), 2)
        self.assertEqual(CourseScheduleV2.objects.count(), 2)
    
    def test_course_detail(self):
        """測試課程詳情API"""
        url = reverse('course-detail', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], '測試課程')
    
    def test_course_update(self):
        """測試更新課程API"""
        url = reverse('course-detail', args=[self.course.id])
        data = {
            'title': '更新的課程',
            'description': '這是一個更新的課程',
            'instructor': '更新的教師',
            'classroom': '更新的教室'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, '更新的課程')
    
    def test_course_delete(self):
        """測試刪除課程API"""
        url = reverse('course-detail', args=[self.course.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CourseV2.objects.count(), 0)
    
    def test_assignment_list(self):
        """測試作業列表API"""
        url = reverse('assignment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], '測試作業')
    
    def test_assignment_create(self):
        """測試創建作業API"""
        url = reverse('assignment-list')
        data = {
            'course': self.course.id,
            'title': '新作業',
            'description': '這是一個新作業',
            'due_date': '2024-01-15T23:59:59Z'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AssignmentV2.objects.count(), 2)
    
    def test_exam_list(self):
        """測試考試列表API"""
        url = reverse('exam-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], '測試考試')
    
    def test_exam_create(self):
        """測試創建考試API"""
        url = reverse('exam-list')
        data = {
            'course': self.course.id,
            'title': '新考試',
            'description': '這是一個新考試',
            'exam_date': '2024-01-20T13:00:00Z',
            'duration': 120,
            'location': '新考場'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExamV2.objects.count(), 2)
    
    def test_note_list(self):
        """測試筆記列表API"""
        url = reverse('note-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], '測試筆記')
    
    def test_note_create(self):
        """測試創建筆記API"""
        url = reverse('note-list')
        data = {
            'course': self.course.id,
            'title': '新筆記',
            'content': '這是一個新筆記的內容'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NoteV2.objects.count(), 2)
    
    def test_file_upload(self):
        """測試文件上傳API"""
        # 創建一個測試圖片
        image = Image.new('RGB', (100, 100), color='red')
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(temp_file, format='JPEG')
        temp_file.seek(0)
        
        # 上傳文件
        url = reverse('file-list')
        data = {
            'file': temp_file,
            'noteId': str(self.note.id)
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FileAttachment.objects.count(), 1)
        
        # 獲取文件列表
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # 刪除文件
        file_id = response.data[0]['id']
        url = reverse('file-detail', args=[file_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FileAttachment.objects.count(), 0)
    
    def test_line_authentication(self):
        """測試LINE認證"""
        # 創建一個未認證的客戶端
        client = APIClient()
        
        # 使用LINE用戶ID進行認證
        client.credentials(HTTP_X_LINE_USER_ID='test_line_user_id')
        
        # 測試訪問課程列表API
        url = reverse('course-list')
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 使用無效的LINE用戶ID
        client.credentials(HTTP_X_LINE_USER_ID='invalid_line_user_id')
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
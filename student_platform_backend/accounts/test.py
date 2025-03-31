from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import EmailVerification, PasswordReset

User = get_user_model()

class AccountTests(APITestCase):

    def test_register_and_verify_email(self):
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'strongpassword'
        }
        # 測試註冊 API
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 從資料庫中取得驗證碼（實際上應用中會從 email 中取得）
        ev = EmailVerification.objects.filter(email='test@example.com').latest('created_at')
        verify_url = reverse('verify-email')
        verify_data = {
            'email': 'test@example.com',
            'code': ev.code
        }
        response = self.client.post(verify_url, verify_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 檢查用戶是否啟用
        user = User.objects.get(email='test@example.com')
        self.assertTrue(user.is_active)

    def test_login(self):
        # 建立啟用用戶
        user = User.objects.create_user(username='loginuser', email='login@example.com', password='loginpassword')
        user.is_active = True
        user.save()
        url = reverse('login')
        data = {
            'identifier': 'loginuser',
            'password': 'loginpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_forgot_and_reset_password(self):
        user = User.objects.create_user(username='resetuser', email='reset@example.com', password='oldpassword')
        user.is_active = True
        user.save()
        forgot_url = reverse('forgot-password')
        data = {'email': 'reset@example.com'}
        response = self.client.post(forgot_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 從資料庫中取得 PasswordReset token
        pr = PasswordReset.objects.filter(user=user).latest('created_at')
        reset_url = reverse('reset-password')
        reset_data = {
            'token': pr.token,
            'new_password': 'newstrongpassword'
        }
        response = self.client.post(reset_url, reset_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 刷新 user 物件以獲得最新密碼 hash
        user.refresh_from_db()
        self.assertTrue(user.check_password('newstrongpassword'))


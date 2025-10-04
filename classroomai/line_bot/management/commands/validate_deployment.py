"""
部署驗證管理命令
"""
import json
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.test import Client
from django.utils import timezone
from user.models import LineProfile


class Command(BaseCommand):
    help = '驗證部署功能'
    
    def __init__(self):
        super().__init__()
        self.client = Client()
        self.test_user_id = 'test_deployment_user'
        self.results = []
    
    def log_result(self, test_name: str, success: bool, message: str = ''):
        """記錄測試結果"""
        status = '✅' if success else '❌'
        self.results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
        self.stdout.write(f"{status} {test_name}: {message}")
    
    def setup_test_user(self):
        """設置測試使用者"""
        user, created = LineProfile.objects.get_or_create(
            line_user_id=self.test_user_id,
            defaults={
                'role': 'student',
                'name': '測試使用者',
                'email': 'test@example.com'
            }
        )
        return user
    
    def cleanup_test_data(self):
        """清理測試資料"""
        try:
            LineProfile.objects.filter(line_user_id=self.test_user_id).delete()
        except:
            pass
    
    def test_legacy_apis(self):
        """測試 Legacy API"""
        self.stdout.write("\n=== 測試 Legacy API ===")
        
        endpoints = [
            '/api/v2/courses/',
            '/api/v2/assignments/',
            '/api/v2/custom-categories/',
            '/api/v2/custom-todos/',
            '/api/v2/notes/',
            '/api/v2/exams/'
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint, {'line_user_id': self.test_user_id})
            
            self.log_result(
                f"Legacy API {endpoint}",
                response.status_code == 200,
                f"狀態碼: {response.status_code}"
            )
    
    def test_web_crud_apis(self):
        """測試網頁 CRUD API"""
        self.stdout.write("\n=== 測試網頁 CRUD API ===")
        
        # 測試創建課程
        course_data = {
            'line_user_id': self.test_user_id,
            'title': '測試課程',
            'description': '測試描述',
            'instructor': '測試老師',
            'classroom': 'A101'
        }
        
        response = self.client.post(
            '/api/v2/web/courses/create/',
            data=json.dumps(course_data),
            content_type='application/json'
        )
        
        create_success = response.status_code in [200, 201]
        self.log_result(
            "創建課程 API",
            create_success,
            f"狀態碼: {response.status_code}"
        )
        
        if create_success:
            response_data = response.json()
            course_id = response_data.get('data', {}).get('id')
            
            # 測試更新課程
            update_data = {
                'line_user_id': self.test_user_id,
                'course_id': course_id,
                'title': '更新後課程'
            }
            
            response = self.client.patch(
                '/api/v2/web/courses/update/',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            self.log_result(
                "更新課程 API",
                response.status_code == 200,
                f"狀態碼: {response.status_code}"
            )
            
            # 測試創建作業
            assignment_data = {
                'line_user_id': self.test_user_id,
                'course_id': course_id,
                'title': '測試作業',
                'due_date': (timezone.now() + timedelta(days=7)).isoformat()
            }
            
            response = self.client.post(
                '/api/v2/web/assignments/create/',
                data=json.dumps(assignment_data),
                content_type='application/json'
            )
            
            self.log_result(
                "創建作業 API",
                response.status_code in [200, 201],
                f"狀態碼: {response.status_code}"
            )
        
        # 測試列表 API
        response = self.client.get('/api/v2/web/courses/list/', {'line_user_id': self.test_user_id})
        self.log_result(
            "課程列表 API",
            response.status_code == 200,
            f"狀態碼: {response.status_code}"
        )
        
        response = self.client.get('/api/v2/web/assignments/list/', {'line_user_id': self.test_user_id})
        self.log_result(
            "作業列表 API",
            response.status_code == 200,
            f"狀態碼: {response.status_code}"
        )
    
    def test_integrated_apis(self):
        """測試整合 API"""
        self.stdout.write("\n=== 測試整合 API ===")
        
        endpoints = [
            '/api/v2/integrated/courses/',
            '/api/v2/integrated/assignments/',
            '/api/v2/integrated/summary/',
            '/api/v2/integrated/dashboard/'
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint, {'line_user_id': self.test_user_id})
            
            self.log_result(
                f"整合 API {endpoint}",
                response.status_code == 200,
                f"狀態碼: {response.status_code}"
            )
        
        # 測試搜尋 API
        response = self.client.get('/api/v2/integrated/search/', {
            'line_user_id': self.test_user_id,
            'q': '測試'
        })
        
        self.log_result(
            "搜尋 API",
            response.status_code == 200,
            f"狀態碼: {response.status_code}"
        )
    
    def test_n8n_workflow_api(self):
        """測試 n8n 工作流 API"""
        self.stdout.write("\n=== 測試 n8n 工作流 API ===")
        
        intent_data = {
            'line_user_id': self.test_user_id,
            'intent': 'list_my_courses',
            'parameters': {}
        }
        
        response = self.client.post(
            '/api/v2/integrated/n8n-intent/',
            data=json.dumps(intent_data),
            content_type='application/json'
        )
        
        self.log_result(
            "n8n 意圖處理 API",
            response.status_code == 200,
            f"狀態碼: {response.status_code}"
        )
    
    def test_sync_apis(self):
        """測試同步 API"""
        self.stdout.write("\n=== 測試同步 API ===")
        
        # 測試同步狀態
        response = self.client.get('/api/v2/sync/status/', {'line_user_id': self.test_user_id})
        
        self.log_result(
            "同步狀態 API",
            response.status_code == 200,
            f"狀態碼: {response.status_code}"
        )
        
        # 測試 Google 狀態檢查（預期失敗）
        response = self.client.get('/api/v2/sync/google-status/', {'line_user_id': self.test_user_id})
        
        self.log_result(
            "Google 狀態檢查 API",
            response.status_code in [400, 401],  # 預期失敗
            f"狀態碼: {response.status_code} (預期失敗)"
        )
    
    def test_error_handling(self):
        """測試錯誤處理"""
        self.stdout.write("\n=== 測試錯誤處理 ===")
        
        # 測試缺少參數
        response = self.client.post('/api/v2/web/courses/create/', {})
        
        self.log_result(
            "缺少參數錯誤處理",
            response.status_code == 400,
            f"狀態碼: {response.status_code}"
        )
        
        # 測試不存在的使用者
        response = self.client.get('/api/v2/web/courses/list/', {'line_user_id': 'nonexistent'})
        
        self.log_result(
            "不存在使用者錯誤處理",
            response.status_code in [403, 404],  # 可能是 403 或 404
            f"狀態碼: {response.status_code}"
        )
    
    def handle(self, *args, **options):
        """執行驗證"""
        self.stdout.write("開始部署功能驗證...")
        self.stdout.write("=" * 60)
        
        # 設置測試環境
        self.setup_test_user()
        
        try:
            # 執行各項測試
            self.test_legacy_apis()
            self.test_web_crud_apis()
            self.test_integrated_apis()
            self.test_n8n_workflow_api()
            self.test_sync_apis()
            self.test_error_handling()
            
            # 統計結果
            total_tests = len(self.results)
            passed_tests = sum(1 for r in self.results if r['success'])
            failed_tests = total_tests - passed_tests
            
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("測試結果統計:")
            self.stdout.write(f"總測試數: {total_tests}")
            self.stdout.write(f"通過: {passed_tests}")
            self.stdout.write(f"失敗: {failed_tests}")
            self.stdout.write(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
            
            if failed_tests > 0:
                self.stdout.write("\n失敗的測試:")
                for result in self.results:
                    if not result['success']:
                        self.stdout.write(f"  ❌ {result['test']}: {result['message']}")
            
            if failed_tests == 0:
                self.stdout.write(self.style.SUCCESS("\n✅ 所有測試通過！部署驗證成功。"))
            else:
                self.stdout.write(self.style.ERROR(f"\n❌ {failed_tests} 個測試失敗"))
        
        finally:
            # 清理測試資料
            self.cleanup_test_data()
#!/usr/bin/env python
"""
部署驗證腳本
測試所有新增 API 端點的功能
"""
import json
import requests
from datetime import datetime, timedelta


class DeploymentValidator:
    """部署驗證器"""
    
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
        self.test_user_id = None  # No default test user
        self.results = []
    
    def log_result(self, test_name: str, success: bool, message: str = ''):
        """記錄測試結果"""
        status = '✅' if success else '❌'
        self.results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
        print(f"{status} {test_name}: {message}")
    
    def test_api_endpoint(self, method: str, endpoint: str, data: dict = None, expected_status: int = 200) -> dict:
        """測試 API 端點"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=data)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
            elif method.upper() == 'PATCH':
                response = requests.patch(url, json=data, headers={'Content-Type': 'application/json'})
            elif method.upper() == 'DELETE':
                response = requests.delete(url, json=data, headers={'Content-Type': 'application/json'})
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == expected_status:
                return {
                    'success': True,
                    'data': response.json() if response.content else {},
                    'status_code': response.status_code
                }
            else:
                return {
                    'success': False,
                    'error': f"Expected {expected_status}, got {response.status_code}",
                    'data': response.json() if response.content else {},
                    'status_code': response.status_code
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': {},
                'status_code': 0
            }
    
    def test_legacy_api_endpoints(self):
        """測試 Legacy API 端點"""
        print("\n=== 測試 Legacy API 端點 ===")
        
        endpoints = [
            '/api/v2/courses/',
            '/api/v2/assignments/',
            '/api/v2/custom-categories/',
            '/api/v2/custom-todos/',
            '/api/v2/notes/',
            '/api/v2/exams/'
        ]
        
        for endpoint in endpoints:
            result = self.test_api_endpoint(
                'GET', 
                endpoint, 
                {'line_user_id': self.test_user_id}
            )
            
            self.log_result(
                f"Legacy API {endpoint}",
                result['success'],
                result.get('error', 'API 回應正常')
            )
    
    def test_web_data_crud_apis(self):
        """測試網頁資料 CRUD API"""
        print("\n=== 測試網頁資料 CRUD API ===")
        
        # 測試創建課程 - 需要提供真實用戶ID
        if not self.test_user_id:
            self.log_result("創建課程 API", False, "需要提供測試用戶ID")
            return
            
        course_data = {
            'line_user_id': self.test_user_id,
            'title': 'API測試課程',
            'description': 'API功能驗證',
            'instructor': 'API測試',
            'classroom': 'TEST',
            'color': '#0066cc'
        }
        
        create_result = self.test_api_endpoint(
            'POST',
            '/api/v2/web/courses/create/',
            course_data
        )
        
        self.log_result(
            "創建課程 API",
            create_result['success'],
            create_result.get('error', '課程創建成功')
        )
        
        if create_result['success']:
            course_id = create_result['data'].get('data', {}).get('id')
            
            # 測試更新課程
            update_data = {
                'line_user_id': self.test_user_id,
                'course_id': course_id,
                'title': '更新後的課程'
            }
            
            update_result = self.test_api_endpoint(
                'PATCH',
                '/api/v2/web/courses/update/',
                update_data
            )
            
            self.log_result(
                "更新課程 API",
                update_result['success'],
                update_result.get('error', '課程更新成功')
            )
            
            # 測試設定課程時間
            schedule_data = {
                'line_user_id': self.test_user_id,
                'course_id': course_id,
                'schedules': [
                    {
                        'day_of_week': 1,
                        'start_time': '09:00:00',
                        'end_time': '10:30:00',
                        'location': 'A101'
                    }
                ]
            }
            
            schedule_result = self.test_api_endpoint(
                'POST',
                '/api/v2/web/courses/schedule/',
                schedule_data
            )
            
            self.log_result(
                "設定課程時間 API",
                schedule_result['success'],
                schedule_result.get('error', '課程時間設定成功')
            )
            
            # 測試創建作業
            assignment_data = {
                'line_user_id': self.test_user_id,
                'course_id': course_id,
                'title': '測試作業',
                'description': '測試作業描述',
                'due_date': (datetime.now() + timedelta(days=7)).isoformat(),
                'type': 'assignment'
            }
            
            assignment_result = self.test_api_endpoint(
                'POST',
                '/api/v2/web/assignments/create/',
                assignment_data
            )
            
            self.log_result(
                "創建作業 API",
                assignment_result['success'],
                assignment_result.get('error', '作業創建成功')
            )
        
        # 測試列出課程
        list_result = self.test_api_endpoint(
            'GET',
            '/api/v2/web/courses/list/',
            {'line_user_id': self.test_user_id}
        )
        
        self.log_result(
            "列出課程 API",
            list_result['success'],
            list_result.get('error', '課程列表獲取成功')
        )
        
        # 測試列出作業
        assignment_list_result = self.test_api_endpoint(
            'GET',
            '/api/v2/web/assignments/list/',
            {'line_user_id': self.test_user_id}
        )
        
        self.log_result(
            "列出作業 API",
            assignment_list_result['success'],
            assignment_list_result.get('error', '作業列表獲取成功')
        )
    
    def test_integrated_query_apis(self):
        """測試整合查詢 API"""
        print("\n=== 測試整合查詢 API ===")
        
        # 測試獲取整合課程
        courses_result = self.test_api_endpoint(
            'GET',
            '/api/v2/integrated/courses/',
            {'line_user_id': self.test_user_id}
        )
        
        self.log_result(
            "整合課程查詢 API",
            courses_result['success'],
            courses_result.get('error', '整合課程查詢成功')
        )
        
        # 測試獲取整合作業
        assignments_result = self.test_api_endpoint(
            'GET',
            '/api/v2/integrated/assignments/',
            {'line_user_id': self.test_user_id}
        )
        
        self.log_result(
            "整合作業查詢 API",
            assignments_result['success'],
            assignments_result.get('error', '整合作業查詢成功')
        )
        
        # 測試獲取課程摘要
        summary_result = self.test_api_endpoint(
            'GET',
            '/api/v2/integrated/summary/',
            {'line_user_id': self.test_user_id}
        )
        
        self.log_result(
            "課程摘要 API",
            summary_result['success'],
            summary_result.get('error', '課程摘要獲取成功')
        )
        
        # 測試搜尋功能
        search_result = self.test_api_endpoint(
            'GET',
            '/api/v2/integrated/search/',
            {'line_user_id': self.test_user_id, 'q': '測試'}
        )
        
        self.log_result(
            "搜尋功能 API",
            search_result['success'],
            search_result.get('error', '搜尋功能正常')
        )
        
        # 測試儀表板資料
        dashboard_result = self.test_api_endpoint(
            'GET',
            '/api/v2/integrated/dashboard/',
            {'line_user_id': self.test_user_id}
        )
        
        self.log_result(
            "儀表板資料 API",
            dashboard_result['success'],
            dashboard_result.get('error', '儀表板資料獲取成功')
        )
    
    def test_n8n_workflow_api(self):
        """測試 n8n 工作流 API"""
        print("\n=== 測試 n8n 工作流 API ===")
        
        # 測試意圖處理
        intent_data = {
            'line_user_id': self.test_user_id,
            'intent': 'list_my_courses',
            'parameters': {}
        }
        
        intent_result = self.test_api_endpoint(
            'POST',
            '/api/v2/integrated/n8n-intent/',
            intent_data
        )
        
        self.log_result(
            "n8n 意圖處理 API",
            intent_result['success'],
            intent_result.get('error', 'n8n 意圖處理成功')
        )
    
    def test_sync_apis(self):
        """測試同步 API（不需要實際 Google 憑證）"""
        print("\n=== 測試同步 API ===")
        
        # 測試同步狀態
        status_result = self.test_api_endpoint(
            'GET',
            '/api/v2/sync/status/',
            {'line_user_id': self.test_user_id}
        )
        
        self.log_result(
            "同步狀態 API",
            status_result['success'],
            status_result.get('error', '同步狀態查詢成功')
        )
        
        # 測試 Google API 狀態檢查（預期會失敗，因為沒有憑證）
        google_status_result = self.test_api_endpoint(
            'GET',
            '/api/v2/sync/google-status/',
            {'line_user_id': self.test_user_id},
            expected_status=400  # 預期失敗
        )
        
        self.log_result(
            "Google API 狀態檢查",
            google_status_result['success'],
            "預期失敗（無 Google 憑證）"
        )
    
    def test_error_handling(self):
        """測試錯誤處理"""
        print("\n=== 測試錯誤處理 ===")
        
        # 測試缺少參數的情況
        missing_param_result = self.test_api_endpoint(
            'POST',
            '/api/v2/web/courses/create/',
            {},  # 缺少必要參數
            expected_status=400
        )
        
        self.log_result(
            "缺少參數錯誤處理",
            missing_param_result['success'],
            "正確回傳 400 錯誤"
        )
        
        # 測試不存在的使用者
        invalid_user_result = self.test_api_endpoint(
            'GET',
            '/api/v2/web/courses/list/',
            {'line_user_id': 'nonexistent_user'},
            expected_status=404
        )
        
        self.log_result(
            "不存在使用者錯誤處理",
            invalid_user_result['success'],
            "正確回傳 404 錯誤"
        )
    
    def run_all_tests(self):
        """運行所有測試"""
        print("開始部署驗證測試...")
        print("=" * 60)
        
        # 測試各個 API 模組
        self.test_legacy_api_endpoints()
        self.test_web_data_crud_apis()
        self.test_integrated_query_apis()
        self.test_n8n_workflow_api()
        self.test_sync_apis()
        self.test_error_handling()
        
        # 統計結果
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 60)
        print("測試結果統計:")
        print(f"總測試數: {total_tests}")
        print(f"通過: {passed_tests}")
        print(f"失敗: {failed_tests}")
        print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n失敗的測試:")
            for result in self.results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['message']}")
        
        print("\n" + ("✅ 所有測試通過！" if failed_tests == 0 else "❌ 部分測試失敗"))
        
        return failed_tests == 0


def main():
    """主函數"""
    import sys
    
    # 檢查服務器是否運行
    validator = DeploymentValidator()
    
    try:
        response = requests.get(f"{validator.base_url}/admin/", timeout=5)
        print(f"✅ Django 服務器運行中 ({validator.base_url})")
    except requests.exceptions.RequestException:
        print(f"❌ Django 服務器未運行或無法訪問 ({validator.base_url})")
        print("請先啟動 Django 開發服務器: python manage.py runserver")
        return 1
    
    # 運行測試
    success = validator.run_all_tests()
    
    return 0 if success else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
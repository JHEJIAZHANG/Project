from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from user.models import LineProfile
from django.contrib.auth.models import User
from django.conf import settings


class LineUserAuthentication(BaseAuthentication):
    """
    自定義認證類，支持通過LINE用戶ID進行認證
    可以通過HTTP頭部 X-Line-User-ID 或查詢參數 line_user_id 提供LINE用戶ID
    """
    
    def authenticate(self, request):
        # 從HTTP頭部獲取LINE用戶ID
        line_user_id = request.META.get('HTTP_X_LINE_USER_ID')
        
        # 如果頭部中沒有，則從查詢參數獲取
        if not line_user_id:
            line_user_id = request.query_params.get('line_user_id')
            
        if not line_user_id:
            return None
            
        try:
            # 查找對應的LineProfile
            line_profile = LineProfile.objects.get(line_user_id=line_user_id)
            
            # 創建Django用戶
            username = f"line_{line_user_id}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': line_profile.email or f"{username}@example.com",
                    'is_active': True
                }
            )
                
            return (user, line_profile)
        except LineProfile.DoesNotExist:
            raise AuthenticationFailed('無效的LINE用戶ID')
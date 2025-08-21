# line_bot/middleware.py
from django.utils.deprecation import MiddlewareMixin
from user.models import LineProfile

class LineRoleMiddleware(MiddlewareMixin):
    """
    將 LINE ID 映射成 role，存到 request.user_role
    （只有 /line/webhook/ 這條路徑才會用到）
    """
    def process_request(self, request):
        if request.path.startswith("/line/webhook/"):
            line_id = request.headers.get("X-Line-UserId")  # 你自己在 webhook view 塞的
            request.user_role = None
            if line_id:
                request.user_role = (
                    LineProfile.objects.filter(pk=line_id)
                    .values_list("role", flat=True)
                    .first()
                )

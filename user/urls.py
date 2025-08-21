from django.urls import path
from . import views

urlpatterns = [
    path("onboard/pre_register/", views.pre_register, name="pre_register"),
    path("oauth/google/callback/", views.google_callback, name="google_callback"),
    path("onboard/status/<str:line_user_id>/", views.onboard_status),
    # path("profile/<str:line_user_id>/", views.get_profile),  # 👈 新增這行
    path("profile/<str:line_user_id>/", views.get_profile, name="get_profile"),
]
    
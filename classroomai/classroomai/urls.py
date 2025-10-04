"""
URL configuration for classroomai project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('user.urls')),  # Include user app URLs
    path("after-oauth.html", TemplateView.as_view(template_name="after-oauth.html")),
    path("", include("line_bot.urls")), # Include LINE bot URLs
    path("", include("course.urls")),
    path('api/v2/', include('api_v2.urls')),  # Include new API v2 URLs
    
    # 處理根路徑 - 重定向到前端應用（改為 Vercel 網域）
    path('', RedirectView.as_view(url='https://coursemanagement01.vercel.app/', permanent=False), name='home'),
]

# 根據記憶中的文件上傳配置，在開發模式下為媒體文件提供URL服務
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

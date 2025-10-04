# line_bot/urls.py
from django.urls import path
from .views import (callback, api_create_bind_code, api_line_push, api_group_bindings, api_n8n_response, render_flex)

urlpatterns = [
    path("line/webhook/", callback),
    path("internal/api/create-bind-code", api_create_bind_code),
    path("internal/api/line/push", api_line_push),
    path("internal/api/group-bindings", api_group_bindings),
    path("internal/api/n8n/response", api_n8n_response),
    
    # ═══ 統一 Flex 模板渲染 API ═══
    path("line/render-flex/", render_flex, name="render_flex"),
]

# line_bot/urls.py
from django.urls import path
from .views import callback, api_create_bind_code, api_line_push, api_group_bindings

urlpatterns = [
    path("line/webhook/", callback),
    path("internal/api/create-bind-code", api_create_bind_code),
    path("internal/api/line/push", api_line_push),
    path("internal/api/group-bindings", api_group_bindings),
]

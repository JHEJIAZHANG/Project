from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet,
    AssignmentViewSet,
    ExamViewSet,
    NoteViewSet,
    FileUploadViewSet,
    CustomCategoryViewSet,
    CustomTodoItemViewSet,
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'exams', ExamViewSet, basename='exam')
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'files', FileUploadViewSet, basename='file')
router.register(r'custom-categories', CustomCategoryViewSet, basename='custom-category')
router.register(r'custom-todos', CustomTodoItemViewSet, basename='custom-todo')

urlpatterns = [
    path('', include(router.urls)),
]
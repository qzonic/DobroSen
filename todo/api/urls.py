from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    TaskViewSet,
    TaskUpdateViewSet,
    UserViewSet,
    SubtaskViewSet,
)


router = DefaultRouter()
router.register(
    'category',
    CategoryViewSet,
    basename='category',
)
router.register(
    'users',
    UserViewSet,
)
router.register(
    'tasks',
    TaskUpdateViewSet,
    basename='tasks-update',
)
router.register(
    'creation-tasks',
    TaskViewSet,
    basename='creation-tasks',
)
router.register(
    r'tasks/(?P<task_id>\d+)/subtasks',
    SubtaskViewSet,
    basename='subtasks',
)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

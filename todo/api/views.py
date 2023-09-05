from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
)
from rest_framework.response import Response

from .mixins import ListCreateViewSet, ListRetrieveUpdateViewSet
from .permissions import IsAssigned, IsTaskCreator, IsSubTaskCreator
from .filters import TaskFilter
from .serializers import (
    CategorySerializer,
    TaskCreateSerializer,
    TaskReadSerializer,
    TaskUpdateSerializer,
    SubtaskCreateSerializer,
    SubtaskReadSerializer,
    UserSerializer,
    UserTaskAnaliseSerializer,
)
from main.models import Category, Task, Subtask


User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ Viewset that provides only `list()` and `retrieve()` actions. """

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)


class CategoryViewSet(ListCreateViewSet):
    """ Viewset that provides `GET` and `POST` methods. """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'id',)


class TaskViewSet(viewsets.ModelViewSet):
    """
    Viewset that provides `GET`, `POST`, `PUT`, `PATCH` and `DELETE` methods
    with Task model.
    """

    permission_classes = (IsTaskCreator,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TaskFilter
    ordering_fields = ('priority',)

    def get_queryset(self):
        return Task.objects.filter(creator=self.request.user)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return TaskReadSerializer
        return TaskCreateSerializer


class TaskUpdateViewSet(ListRetrieveUpdateViewSet):
    """
    Viewset that provides `GET`, `PUT` and `PATCH` methods
    with Task model.
    """

    permission_classes = (IsAssigned,)
    serializer_class = TaskUpdateSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TaskFilter
    ordering_fields = ('priority',)

    def get_queryset(self, pk=None):
        return Task.objects.filter(assigned_to=self.request.user)

    @action(
        detail=False,
        methods=('get',),
        url_path='statistics',
    )
    def statistics(self, request,):
        queryset = self.get_queryset()
        return Response(UserTaskAnaliseSerializer(queryset).data)


class SubtaskViewSet(viewsets.ModelViewSet):
    """
    Viewset that provides `GET`, `POST`, `PUT`, `PATCH` and `DELETE` methods
    with Subtask model.
    """

    permission_classes = (IsSubTaskCreator,)

    def get_task(self):
        return get_object_or_404(Task, id=self.kwargs.get('task_id'))

    def get_queryset(self):
        return Subtask.objects.filter(parent_task=self.get_task())

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return SubtaskReadSerializer
        return SubtaskCreateSerializer

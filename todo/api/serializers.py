from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db.models import Avg, F
from django.utils import timezone
from rest_framework import serializers

from main.models import Category, Task, Subtask


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """ User serializer. """

    class Meta:
        model = User
        fields = (
            'id',
            'username',
        )


class UserTaskAnaliseSerializer(serializers.ModelSerializer):
    """ Analise user tasks serializer. """

    tasks_count = serializers.SerializerMethodField()
    average_time = serializers.SerializerMethodField()
    completed_tasks_count = serializers.SerializerMethodField()
    uncompleted_tasks_count = serializers.SerializerMethodField()
    overdue_tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = (
            'tasks_count',
            'average_time',
            'completed_tasks_count',
            'uncompleted_tasks_count',
            'overdue_tasks_count',
        )

    def get_tasks_count(self, obj):
        return obj.count()

    def get_average_time(self, obj):
        return obj.filter(is_completed=True).aggregate(
                average_time=Avg(F('finish_date') - F('created_at'))
            )['average_time']

    def get_completed_tasks_count(self, obj):
        return obj.filter(is_completed=True).count()

    def get_uncompleted_tasks_count(self, obj):
        return obj.filter(is_completed=False).count()

    def get_overdue_tasks_count(self, obj):
        return obj.filter(finish_date__gt=F('due_date')).count()


class CategorySerializer(serializers.ModelSerializer):
    """ Category serializer. """

    class Meta:
        model = Category
        fields = (
            'id',
            'name',
        )


class TaskReadSerializer(serializers.ModelSerializer):
    """ Task serializer for reading. """

    category = CategorySerializer()
    file = serializers.SerializerMethodField()
    creator = UserSerializer()
    assigned_to = UserSerializer()
    subtasks = serializers.SerializerMethodField()
    priority = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'description',
            'created_at',
            'due_date',
            'category',
            'file',
            'creator',
            'assigned_to',
            'priority',
            'subtasks',
            'is_completed',
        )

    def get_file(self, obj):
        if obj.file:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.file.url)
        return None

    def get_subtasks(self, obj):
        return SubtaskReadSerializer(obj.related_subtasks, many=True).data

    def get_priority(self, obj):
        return obj.get_priority_display()


class SubtaskCreateSerializer(serializers.ModelSerializer):
    """ Subtask serializer. """

    creator = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    parent_task = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
    )

    class Meta:
        model = Subtask
        fields = (
            'title',
            'description',
            'creator',
            'is_completed',
            'parent_task',
        )

    def validate(self, attrs):

        creator = attrs.get('creator')
        if 'parent_task' in attrs:
            parent_task = attrs.get('parent_task')
            if creator not in [parent_task.creator, parent_task.assigned_to]:
                raise serializers.ValidationError(
                    {
                        'error': 'Подзадачу к этой задаче может добавить либо создатель задачи, '
                                 'либо тот, кто должен выполнять эту задачу.'
                     }
                )
        return attrs



    def to_representation(self, instance):
        return SubtaskReadSerializer(instance).data


class TaskCreateSerializer(serializers.ModelSerializer):
    """ Task serializer for creation. """

    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
    )
    creator = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    due_date = serializers.DateTimeField(
        validators=[MinValueValidator(
            limit_value=timezone.now(),
            message='Дата окончания задачи не может быть меньше текущей.'
        )]
    )
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
    )

    class Meta:
        model = Task
        fields = (
            'title',
            'description',
            'due_date',
            'creator',
            'category',
            'file',
            'assigned_to',
            'priority',
            'is_completed',
        )

    def to_representation(self, instance):
        return TaskReadSerializer(instance, context=self.context).data


class TaskUpdateSerializer(serializers.ModelSerializer):
    """ Serializer for update tasks by assigned user. """

    due_date = serializers.DateTimeField(
        validators=[MinValueValidator(
            limit_value=timezone.now(),
            message='Дата окончания задачи не может быть меньше текущей.'
        )]
    )

    class Meta:
        model = Task
        fields = (
            'due_date',
            'file',
            'is_completed',
        )

    def to_representation(self, instance):
        return TaskReadSerializer(instance, context=self.context).data


class SubtaskReadSerializer(serializers.ModelSerializer):
    """ Subtask serializer. """

    class Meta:
        model = Subtask
        fields = (
            'id',
            'title',
            'description',
            'is_completed',
        )




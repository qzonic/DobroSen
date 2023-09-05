from django_filters import filterset

from main.models import Task


class TaskFilter(filterset.FilterSet):
    """ Class that allow filter tasks by category name. """

    category = filterset.CharFilter(
        field_name='category__name',
        lookup_expr='exact',
    )

    class Meta:
        model = Task
        fields = ('category',)

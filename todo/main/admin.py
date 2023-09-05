from django.contrib import admin

from .models import Category, CustomUser, Task, Subtask


class CategoryAdmin(admin.ModelAdmin):
    """ Category admin model. """

    list_display = (
        'id',
        'name',
        'get_tasks_count',
    )
    list_editable = (
        'name',
    )
    search_fields = (
        'name',
    )

    @admin.display(description='Tasks count')
    def get_tasks_count(self, obj):
        return obj.tasks.count()


class CustomUserAdmin(admin.ModelAdmin):
    """ CustomUser admin model. """

    list_display = (
        'id',
        'username',
        'email',
    )


class TaskAdmin(admin.ModelAdmin):
    """ Task admin model. """

    list_display = (
        'id',
        'title',
        'created_at',
        'due_date',
        'category',
        'creator',
        'priority',
        'is_completed',
    )
    list_editable = (
        'title',
        'due_date',
        'priority',
    )
    list_filter = (
        'created_at',
        'due_date',
        'is_completed',
    )
    search_fields = (
        'title',
        'category__name',
        'creator__username',
    )


class SubtaskAdmin(admin.ModelAdmin):
    """ Subtask admin model. """

    list_display = (
        'id',
        'title',
        'creator',
        'is_completed',
    )
    list_editable = (
        'title',
    )
    list_filter = (
        'is_completed',
    )
    search_fields = (
        'title',
        'creator__username',
    )


admin.site.register(Category, CategoryAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Subtask, SubtaskAdmin)

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from . import models
from .messages import NOTIFICATION_EMAIL


@shared_task
def send_notification(task_id):
    task = models.Task.objects.filter(id=task_id).first()
    email_title = 'Для Вас есть новая задача!'
    if task:
        send_mail(
            email_title,
            NOTIFICATION_EMAIL.format(
                task.title,
                task.category,
                task.description,
                task.created_at,
                task.due_date,
                task.get_priority_display(),
                task.creator
            ),
            settings.EMAIL_HOST_USER,
            [task.assigned_to.email],
            fail_silently=False,
        )

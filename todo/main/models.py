from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .tasks import send_notification


class CustomUser(AbstractUser):
    """ Custom user model with required email field. """

    email = models.EmailField(unique=True, blank=False)


class Category(models.Model):
    """ Category model. """

    name = models.CharField(
        max_length=128,
    )

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


class AbstractTaskModel(models.Model):
    """ Abstract model for task and subtask model. """

    title = models.CharField(
        max_length=128,
    )
    description = models.TextField(
        blank=True,
    )
    is_completed = models.BooleanField(
        default=False,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Task(AbstractTaskModel):
    """ Task model. """

    LOW_INDEX = '0'
    MEDIUM_INDEX = '1'
    HIGH_INDEX = '2'

    LOW_STATUS = 'Низкий'
    MEDIUM_STATUS = 'Средний'
    HIGH_STATUS = 'Высокий'

    PRIORITY_CHOICES = (
        (LOW_INDEX, LOW_STATUS),
        (MEDIUM_INDEX, MEDIUM_STATUS),
        (HIGH_INDEX, HIGH_STATUS),
    )

    category = models.ForeignKey(
        to=Category,
        on_delete=models.CASCADE,
        related_name='tasks',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    due_date = models.DateTimeField(
        default=timezone.now,
    )
    assigned_to = models.ForeignKey(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
    )
    priority = models.CharField(
        max_length=7,
        choices=PRIORITY_CHOICES,
        default=LOW_INDEX,
    )
    file = models.FileField(
        upload_to='tasks/',
        blank=True,
        null=True,
    )
    finish_date = models.DateTimeField(
        blank=True,
        null=True,
    )
    creator = models.ForeignKey(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='creation_tasks',
    )

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.is_completed and not self.finish_date:
            self.finish_date = timezone.now()
        return super().save(*args, **kwargs)


class Subtask(AbstractTaskModel):
    """ Subtask model. """

    parent_task = models.ForeignKey(
        to=Task,
        on_delete=models.CASCADE,
        related_name='related_subtasks',
    )
    creator = models.ForeignKey(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='creation_subtasks',
    )

    class Meta:
        ordering = ['-id']


@receiver(post_save, sender=Task)
def send_task_notification(sender, instance, created, **kwargs):
    if created and not settings.TESTING:
        send_notification.delay(instance.id)


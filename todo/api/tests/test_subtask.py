from datetime import timedelta

from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from main.models import Category, Task, Subtask

User = get_user_model()


class TestTask(APITestCase):
    """ Test task. """

    URL = '/api/v1/tasks/{0}/subtasks/'
    OBJECT_URL = '/api/v1/tasks/{0}/subtasks/{1}/'

    @classmethod
    def setUpClass(cls) -> None:
        super(TestTask, cls).setUpClass()
        setattr(settings, 'TESTING', True)
        cls.first_user = User.objects.create_user(
            username='first_test_user',
            email='first@test.ru',
        )
        cls.second_user = User.objects.create_user(
            username='second_test_user',
            email='second@test.ru',
        )
        cls.first_category = Category.objects.create(
            name='Первая категория',
        )
        cls.second_category = Category.objects.create(
            name='Вторая категория',
        )
        cls.first_task = Task.objects.create(
            title='API',
            description='Нужно написать сериализаторы для api.',
            due_date=timezone.now()+timedelta(days=1),
            category=cls.first_category,
            creator=cls.first_user,
            priority='1',
            assigned_to=cls.first_user,
        )
        cls.second_task = Task.objects.create(
            title='Тесты',
            description='Нужно написать тесты для проверки работы тасков.',
            due_date=timezone.now()+timedelta(days=1),
            category=cls.second_category,
            creator=cls.second_user,
            priority='2',
            assigned_to=cls.first_user,
        )
        cls.first_subtask = Subtask.objects.create(
            title='',
            description='',
            parent_task=cls.first_task,
            creator=cls.first_user,
        )
        cls.second_subtask = Subtask.objects.create(
            title='',
            description='',
            parent_task=cls.second_task,
            creator=cls.second_user,
        )

    def setUp(self) -> None:
        self.guest_client = APIClient()

        self.authorized_client = APIClient()
        token = RefreshToken.for_user(self.first_user)
        self.authorized_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(token.access_token)}'
        )

        self.second_authorized_client = APIClient()
        second_token = RefreshToken.for_user(self.second_user)
        self.second_authorized_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(second_token.access_token)}'
        )

    def test_get_subtasks_list_by_guest(self):
        response = self.guest_client.get(self.URL.format(self.first_task.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_subtasks_list_by_authorized(self):
        tasks_count = Subtask.objects.filter(parent_task=self.first_task).count()
        response = self.authorized_client.get(self.URL.format(self.first_task.id))
        expected_keys = ['count', 'next', 'previous', 'results']
        response_json = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response_json.keys()), expected_keys)
        self.assertEqual(response_json['count'], tasks_count)

        for task in response_json['results']:
            self.assertTrue(
                Subtask.objects.filter(
                    id=task['id'],
                    parent_task=self.first_task
                ).exists()
            )

    def test_put_patch_delete_subtask_by_guest(self):
        methods = ['put', 'patch', 'delete']
        for method in methods:
            met = getattr(self.guest_client, method)
            response = met(self.OBJECT_URL.format(self.first_task.id, self.first_subtask.id))

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_patch_delete_creation_task_by_another_client(self):
        methods = ['put', 'patch', 'delete']

        for method in methods:
            met = getattr(self.second_authorized_client, method)
            response = met(self.OBJECT_URL.format(self.first_task.id, self.first_subtask.id))

            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_patch_task_by_creator(self):
        method_data = {
            'put': {
                'title': 'TEST',
                'description': 'Test description',
                'parent_task': self.first_task.id
            },
            'patch': {
                'title': 'New title',
            }
        }

        for method, data in method_data.items():
            met = getattr(self.authorized_client, method)
            response = met(
                self.OBJECT_URL.format(self.first_task.id, self.first_subtask.id),
                data=data,
            )
            subtask = Subtask.objects.get(id=self.first_subtask.id)
            response_json = response.json()

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEquals(
                [
                    subtask.id,
                    subtask.title,
                    subtask.description,
                ],
                [
                    response_json['id'],
                    response_json['title'],
                    response_json['description'],
                ]
            )

    def test_validate_parent_task(self):
        data = {
            'title': 'TEST',
            'description': 'Test description',
            'parent_task': self.first_task.id
        }

        response = self.second_authorized_client.post(
            self.URL.format(self.first_task.id),
            data=data,
        )
        response_json = response.json()
        message = {'error':
                       ['Подзадачу к этой задаче может добавить либо создатель задачи, '
                        'либо тот, кто должен выполнять эту задачу.']
                     }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, message)

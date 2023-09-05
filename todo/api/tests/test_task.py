from datetime import timedelta

from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from main.models import Category, Task

User = get_user_model()


class TestTask(APITestCase):
    """ Test task. """

    CREATOR_URL = '/api/v1/creation-tasks/'
    CREATOR_OBJECT_URL = '/api/v1/creation-tasks/{0}/'

    ASSIGNED_URL = '/api/v1/tasks/'
    ASSIGNED_OBJECT_URL = '/api/v1/tasks/{0}/'

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
        cls.third_task = Task.objects.create(
            title='Модели',
            description='Закончить писать модель Task.',
            due_date=timezone.now()+timedelta(days=1),
            category=cls.first_category,
            creator=cls.second_user,
            priority='0',
            assigned_to=cls.second_user,
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

    def test_get_creation_tasks_list_by_guest(self):
        response = self.guest_client.get(self.CREATOR_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_assigned_tasks_list_by_guest(self):
        response = self.guest_client.get(self.ASSIGNED_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_creation_tasks_list_by_authorized(self):
        tasks_count = Task.objects.filter(creator=self.first_user).count()
        response = self.authorized_client.get(self.CREATOR_URL)
        expected_keys = ['count', 'next', 'previous', 'results']
        response_json = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response_json.keys()), expected_keys)
        self.assertEqual(response_json['count'], tasks_count)

        for task in response_json['results']:
            self.assertTrue(
                Task.objects.filter(
                    id=task['id'],
                    creator=self.first_user.id
                ).exists()
            )

    def test_get_assigned_tasks_list_by_authorized(self):
        tasks_count = Task.objects.filter(assigned_to=self.first_user).count()
        response = self.authorized_client.get(self.ASSIGNED_URL)
        expected_keys = ['count', 'next', 'previous', 'results']
        response_json = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response_json.keys()), expected_keys)
        self.assertEqual(response_json['count'], tasks_count)

        for task in response_json['results']:
            self.assertTrue(
                Task.objects.filter(
                    id=task['id'],
                    assigned_to=self.first_user.id
                ).exists()
            )

    def test_put_patch_delete_creation_task_by_guest(self):
        methods = ['put', 'patch', 'delete']

        for method in methods:
            met = getattr(self.guest_client, method)
            response = met(self.CREATOR_OBJECT_URL.format(self.first_task.id))

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_patch_delete_assigned_task_by_guest(self):
        methods = ['put', 'patch', 'delete']

        for method in methods:
            met = getattr(self.guest_client, method)
            response = met(self.ASSIGNED_OBJECT_URL.format(self.first_task.id))

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_patch_delete_creation_task_by_another_client(self):
        methods = ['put', 'patch', 'delete']

        for method in methods:
            met = getattr(self.authorized_client, method)
            response = met(self.CREATOR_OBJECT_URL.format(self.third_task.id))

            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_patch_assigned_task_by_another_client(self):
        methods = ['put', 'patch']

        for method in methods:
            met = getattr(self.authorized_client, method)
            response = met(self.ASSIGNED_OBJECT_URL.format(self.third_task.id))

            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_patch_task_by_creator(self):
        target_date = timezone.now() + timedelta(days=1)
        method_data = {
            'put': {
                'title': 'TEST',
                'description': 'Test description',
                'due_date': target_date.strftime('%Y-%m-%d %H:%M:%S'),
                'category': self.second_category.id,
                'assigned_to': self.second_user.id,
                'priority': '2'
            },
            'patch': {
                'title': 'New title',
            }
        }

        for method, data in method_data.items():
            met = getattr(self.authorized_client, method)
            response = met(
                self.CREATOR_OBJECT_URL.format(self.first_task.id),
                data=data,
            )
            task = Task.objects.get(id=self.first_task.id)
            response_json = response.json()

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEquals(
                [
                    task.id,
                    task.title,
                    task.description,
                    task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    task.due_date.strftime('%Y-%m-%d %H:%M:%S'),
                    task.category.id,
                    task.get_priority_display()
                ],
                [
                    response_json['id'],
                    response_json['title'],
                    response_json['description'],
                    response_json['created_at'],
                    response_json['due_date'],
                    response_json['category']['id'],
                    response_json['priority']
                ]
            )

    def test_put_patch_task_by_assigned(self):
        target_date = timezone.now() + timedelta(days=1)
        method_data = {
            'put': {
                'due_date': target_date.strftime('%Y-%m-%d %H:%M:%S'),
            },
            'patch': {
                'due_date': target_date.strftime('%Y-%m-%d %H:%M:%S')
            }
        }

        for method, data in method_data.items():
            met = getattr(self.authorized_client, method)
            response = met(
                self.ASSIGNED_OBJECT_URL.format(self.second_task.id),
                data=data,
            )
            task = Task.objects.get(id=self.second_task.id)
            response_json = response.json()

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEquals(
                [
                    task.id,
                    task.title,
                    task.description,
                    task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    task.due_date.strftime('%Y-%m-%d %H:%M:%S'),
                    task.category.id,
                    task.get_priority_display()
                ],
                [
                    response_json['id'],
                    response_json['title'],
                    response_json['description'],
                    response_json['created_at'],
                    response_json['due_date'],
                    response_json['category']['id'],
                    response_json['priority']
                ]
            )

    def test_put_patch_task_by_assigned_with_bad_fields(self):
        target_date = timezone.now() + timedelta(days=1)
        method_data = {
            'put': {
                'due_date': target_date.strftime('%Y-%m-%d %H:%M:%S'),
                'priority': '0'
            },
            'patch': {
                'priority': '0'
            }
        }

        for method, data in method_data.items():
            met = getattr(self.authorized_client, method)
            response = met(
                self.ASSIGNED_OBJECT_URL.format(self.second_task.id),
                data=data,
            )
            task = Task.objects.get(id=self.second_task.id)
            response_json = response.json()

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEquals(
                [
                    task.id,
                    task.title,
                    task.description,
                    task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    task.due_date.strftime('%Y-%m-%d %H:%M:%S'),
                    task.category.id,
                ],
                [
                    response_json['id'],
                    response_json['title'],
                    response_json['description'],
                    response_json['created_at'],
                    response_json['due_date'],
                    response_json['category']['id'],
                ]
            )
            self.assertNotEqual(task.get_priority_display(), 'Низкий')

    def test_validate_due_date(self):
        task_count = Task.objects.filter(creator=self.first_user).count()
        target_date = timezone.now() - timedelta(days=1)
        data = {
            'title': 'New task',
            'description': 'New task description',
            'due_date': target_date,
            'category': self.second_category.id,
            'assigned_to': self.second_user.id,
        }
        response = self.authorized_client.post(self.CREATOR_URL, data=data)
        expected_error = {
            'due_date': ['Дата окончания задачи не может быть меньше текущей.']
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), expected_error)
        self.assertEqual(
            Task.objects.filter(creator=self.first_user).count(),
            task_count
        )

    def test_upload_file(self):
        file_path = 'api/tests/file.txt'
        full_path = settings.BASE_DIR / file_path
        target_date = timezone.now() + timedelta(days=1)
        with open(full_path, 'r') as file:
            data = {
                'title': 'New task',
                'description': 'New task description',
                'due_date': target_date,
                'category': self.second_category.id,
                'file': file,
                'assigned_to': self.second_user.id,
            }
            response = self.authorized_client.post(self.CREATOR_URL, data=data)
            response_json = response.json()
            task = Task.objects.filter(
                id=response_json['id'],
                assigned_to=self.second_user
            )

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(task.exists())
            self.assertTrue(task.first().file)

    def test_filter_task(self):
        param = 'Первая категория'
        expected_count = 1
        response = self.authorized_client.get(self.CREATOR_URL + f'?category={param}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], expected_count)
        self.assertEqual(
            response.json()['results'][0]['title'],
            self.first_task.title
        )

    def test_ordering_creation_tasks(self):
        param = '-priority'
        tasks = Task.objects.filter(creator=self.first_user).order_by(param)
        response = self.authorized_client.get(self.CREATOR_URL + f'?ordering={param}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], tasks.count())
        for task_db, task_json in zip(tasks, response.json()['results']):
            self.assertEqual(task_db.id, task_json['id'])

    def test_ordering_assigned_tasks(self):
        param = '-priority'
        tasks = Task.objects.filter(assigned_to=self.first_user).order_by(param)
        response = self.authorized_client.get(self.ASSIGNED_URL + f'?ordering={param}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], tasks.count())
        for task_db, task_json in zip(tasks, response.json()['results']):
            self.assertEqual(task_db.id, task_json['id'])

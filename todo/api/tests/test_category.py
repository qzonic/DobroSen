from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from main.models import Category

User = get_user_model()


class TestCategory(APITestCase):
    """ Test category. """

    URL = '/api/v1/category/'

    @classmethod
    def setUpClass(cls) -> None:
        super(TestCategory, cls).setUpClass()
        cls.user = User.objects.create_user(
            username='test_user',
        )
        cls.first_category = Category.objects.create(
            name='Первая категория',
        )
        cls.second_category = Category.objects.create(
            name='Вторая категория',
        )
        cls.third_category = Category.objects.create(
            name='Третья категория',
        )

    def setUp(self) -> None:
        self.guest_client = APIClient()

        self.authorized_client = APIClient()
        token = RefreshToken.for_user(self.user)
        self.authorized_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(token.access_token)}'
        )

    def test_get_category_list_by_different_clients(self):
        clients = [self.guest_client, self.authorized_client]
        expected_keys = ['count', 'next', 'previous', 'results']
        for client in clients:
            category_count = Category.objects.count()
            response = client.get(self.URL)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response_json = response.json()

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(list(response_json.keys()), expected_keys)
            self.assertEqual(response_json['count'], category_count)

            for contact in response_json['results']:
                self.assertTrue(Category.objects.filter(
                    name=contact['name'],
                ).exists())

    def test_create_category_by_guest(self):
        response = self.guest_client.post(self.URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_category_by_authorized(self):
        category_count = Category.objects.count()
        data = {
            'name': 'Тестовая категория'
        }
        response = self.authorized_client.post(self.URL, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), category_count + 1)

    def test_put_patch_delete_category(self):
        methods = ['put', 'patch', 'delete']

        for method in methods:
            met = getattr(self.authorized_client, method)
            response = met(self.URL + str(self.first_category) + '/')

            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_category(self):
        param = 'Первая'
        expected_count = 1
        response = self.authorized_client.get(self.URL + f'?search={param}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], expected_count)
        self.assertEqual(
            response.json()['results'][0]['name'],
            self.first_category.name
        )
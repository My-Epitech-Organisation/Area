from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User

class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('auth_register')
        self.login_url = reverse('token_obtain_pair')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'StrongPassword123',
            'password2': 'StrongPassword123'
        }
        self.user = User.objects.create_user(username='testuser2', password='StrongPassword123')

    def test_register_user(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_login_user(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {'username': 'testuser', 'password': 'StrongPassword123'}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_detail(self):
        self.client.force_authenticate(user=self.user)
        detail_url = reverse('user_detail')
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def test_token_refresh(self):
        """Test JWT token refresh mechanism"""
        # First, register and login to get tokens
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {'username': 'testuser', 'password': 'StrongPassword123'}
        login_response = self.client.post(self.login_url, login_data, format='json')

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_response.data)
        self.assertIn('refresh', login_response.data)

        # Extract the refresh token
        refresh_token = login_response.data['refresh']

        # Use the refresh token to get a new access token
        refresh_url = reverse('token_refresh')
        refresh_data = {'refresh': refresh_token}
        refresh_response = self.client.post(refresh_url, refresh_data, format='json')

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

        # The new access token should be different from the original
        new_access_token = refresh_response.data['access']
        original_access_token = login_response.data['access']
        self.assertNotEqual(new_access_token, original_access_token)

    def test_invalid_refresh_token(self):
        """Test that invalid refresh tokens are rejected"""
        refresh_url = reverse('token_refresh')
        invalid_refresh_data = {'refresh': 'invalid-token-123'}
        response = self.client.post(refresh_url, invalid_refresh_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

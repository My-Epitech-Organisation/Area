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

    def test_user_registration_email_unverified(self):
        """Test that new users have email_verified=False by default"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('email_verified', response.data)
        self.assertFalse(response.data['email_verified'])
        
        # Verify in database
        user = User.objects.get(username='testuser')
        self.assertFalse(user.email_verified)
        self.assertIsNone(user.email_verification_token)

    def test_send_verification_email(self):
        """Test sending verification email to authenticated user"""
        # Create and authenticate user
        user = User.objects.create_user(
            username='testverify',
            email='test@example.com',
            password='StrongPassword123'
        )
        self.client.force_authenticate(user=user)
        
        send_verification_url = reverse('send_verification_email')
        response = self.client.post(send_verification_url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Check that token was generated
        user.refresh_from_db()
        self.assertIsNotNone(user.email_verification_token)

    def test_verify_email_with_valid_token(self):
        """Test email verification with valid token"""
        # Create user with verification token
        user = User.objects.create_user(
            username='testverify2',
            email='test2@example.com',
            password='StrongPassword123'
        )
        user.email_verification_token = 'valid-token-123'
        user.save()
        
        verify_url = reverse('verify_email', kwargs={'token': 'valid-token-123'})
        response = self.client.get(verify_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Email verified successfully', response.data['message'])
        
        # Check database
        user.refresh_from_db()
        self.assertTrue(user.email_verified)
        self.assertIsNone(user.email_verification_token)

    def test_verify_email_with_invalid_token(self):
        """Test email verification with invalid token"""
        verify_url = reverse('verify_email', kwargs={'token': 'invalid-token-456'})
        response = self.client.get(verify_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid verification token', response.data['error'])

    def test_complete_authentication_flow(self):
        """Test complete flow: register → login → refresh → /users/me"""
        # Step 1: Register
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['email_verified'])
        
        # Step 2: Login
        login_data = {'username': 'testuser', 'password': 'StrongPassword123'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_response.data)
        self.assertIn('refresh', login_response.data)
        
        # Store tokens
        access_token = login_response.data['access']
        refresh_token = login_response.data['refresh']
        
        # Step 3: Access protected endpoint with access token
        detail_url = reverse('user_detail')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        me_response = self.client.get(detail_url)
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data['username'], 'testuser')
        self.assertEqual(me_response.data['email'], 'test@example.com')
        self.assertFalse(me_response.data['email_verified'])
        
        # Step 4: Refresh token
        refresh_url = reverse('token_refresh')
        refresh_data = {'refresh': refresh_token}
        refresh_response = self.client.post(refresh_url, refresh_data, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)
        
        # Step 5: Use new access token
        new_access_token = refresh_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        me_response2 = self.client.get(detail_url)
        self.assertEqual(me_response2.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response2.data['username'], 'testuser')
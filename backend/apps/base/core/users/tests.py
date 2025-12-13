"""
User Tests for Owls E-commerce Platform
========================================
Unit and integration tests for user authentication and management.
"""

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
import uuid

User = get_user_model()


class UserModelTests(TestCase):
    """Tests for the User model."""
    
    def test_create_user_with_email(self):
        """Test creating a user with email works."""
        email = 'test@example.com'
        password = 'TestPass123!'
        user = User.objects.create_user(email=email, password=password)
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.role, User.Role.CUSTOMER)
    
    def test_create_user_without_email_raises_error(self):
        """Test that creating user without email raises ValueError."""
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='test123')
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        email = 'admin@example.com'
        password = 'AdminPass123!'
        user = User.objects.create_superuser(email=email, password=password)
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_verified)
        self.assertEqual(user.role, User.Role.ADMIN)
    
    def test_email_is_normalized(self):
        """Test that email is normalized to lowercase domain."""
        email = 'test@EXAMPLE.COM'
        user = User.objects.create_user(email=email, password='test123')
        
        self.assertEqual(user.email, 'test@example.com')
    
    def test_user_uuid_is_generated(self):
        """Test that UUID is auto-generated for new users."""
        user = User.objects.create_user(
            email='uuid@example.com',
            password='test123'
        )
        
        self.assertIsNotNone(user.id)
        self.assertIsInstance(user.id, uuid.UUID)
    
    def test_user_full_name_property(self):
        """Test getting user's full name property."""
        user = User.objects.create_user(
            email='name@example.com',
            password='test123',
            first_name='John',
            last_name='Doe'
        )
        
        # Use full_name property instead of get_full_name method
        self.assertEqual(user.full_name, 'John Doe')
    
    def test_user_roles(self):
        """Test different user roles."""
        for role_value, role_label in User.Role.choices:
            user = User.objects.create_user(
                email=f'{role_value}@example.com',
                password='test123',
                role=role_value
            )
            self.assertEqual(user.role, role_value)


@override_settings(
    SIMPLE_JWT={
        'ALGORITHM': 'HS256',
        'SIGNING_KEY': 'test-secret-key-for-testing-only',
    }
)
class UserRegistrationTests(APITestCase):
    """Tests for user registration endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/v1/auth/register/'
        self.valid_payload = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_register_user_success(self):
        """Test successful user registration."""
        response = self.client.post(
            self.register_url,
            self.valid_payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('tokens', response.data['data'])
        self.assertIn('access', response.data['data']['tokens'])
        self.assertIn('refresh', response.data['data']['tokens'])
        
        # Verify user was created
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
    
    def test_register_duplicate_email(self):
        """Test registration fails for duplicate email."""
        # Create first user
        User.objects.create_user(
            email='existing@example.com',
            password='test123'
        )
        
        payload = self.valid_payload.copy()
        payload['email'] = 'existing@example.com'
        
        response = self.client.post(
            self.register_url,
            payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_password_mismatch(self):
        """Test registration fails when passwords don't match."""
        payload = self.valid_payload.copy()
        payload['password_confirm'] = 'DifferentPass123!'
        
        response = self.client.post(
            self.register_url,
            payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_weak_password(self):
        """Test registration fails for weak password."""
        payload = self.valid_payload.copy()
        payload['password'] = '123'
        payload['password_confirm'] = '123'
        
        response = self.client.post(
            self.register_url,
            payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@override_settings(
    SIMPLE_JWT={
        'ALGORITHM': 'HS256',
        'SIGNING_KEY': 'test-secret-key-for-testing-only',
    }
)
class UserLoginTests(APITestCase):
    """Tests for user login endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = '/api/v1/auth/login/'
        self.user = User.objects.create_user(
            email='login@example.com',
            password='SecurePass123!',
            is_active=True
        )
    
    def test_login_success(self):
        """Test successful login returns tokens."""
        response = self.client.post(
            self.login_url,
            {'email': 'login@example.com', 'password': 'SecurePass123!'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
    
    def test_login_wrong_password(self):
        """Test login fails with wrong password."""
        response = self.client.post(
            self.login_url,
            {'email': 'login@example.com', 'password': 'WrongPass123!'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_nonexistent_user(self):
        """Test login fails for non-existent user."""
        response = self.client.post(
            self.login_url,
            {'email': 'nonexistent@example.com', 'password': 'Test123!'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_inactive_user(self):
        """Test login fails for inactive user."""
        self.user.is_active = False
        self.user.save()
        
        response = self.client.post(
            self.login_url,
            {'email': 'login@example.com', 'password': 'SecurePass123!'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(
    SIMPLE_JWT={
        'ALGORITHM': 'HS256',
        'SIGNING_KEY': 'test-secret-key-for-testing-only',
    }
)
class UserLogoutTests(APITestCase):
    """Tests for user logout endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.logout_url = '/api/v1/auth/logout/'
        self.user = User.objects.create_user(
            email='logout@example.com',
            password='SecurePass123!',
            is_active=True
        )
        # Generate token manually for test
        from rest_framework_simplejwt.tokens import RefreshToken
        self.refresh = RefreshToken.for_user(self.user)
        self.access = self.refresh.access_token
    
    def test_logout_success(self):
        """Test successful logout blacklists token."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(self.access)}'
        )
        
        response = self.client.post(
            self.logout_url,
            {'refresh': str(self.refresh)},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_logout_without_refresh_token(self):
        """Test logout fails without refresh token."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(self.access)}'
        )
        
        response = self.client.post(
            self.logout_url,
            {},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_logout_unauthenticated(self):
        """Test logout fails without authentication."""
        response = self.client.post(
            self.logout_url,
            {'refresh': str(self.refresh)},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(
    SIMPLE_JWT={
        'ALGORITHM': 'HS256',
        'SIGNING_KEY': 'test-secret-key-for-testing-only',
    }
)
class UserProfileTests(APITestCase):
    """Tests for user profile endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.profile_url = '/api/v1/auth/profile/'
        self.user = User.objects.create_user(
            email='profile@example.com',
            password='SecurePass123!',
            first_name='Original',
            last_name='Name',
            is_active=True
        )
        from rest_framework_simplejwt.tokens import RefreshToken
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(self.refresh.access_token)}'
        )
    
    def test_get_profile(self):
        """Test getting user profile."""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['email'], 'profile@example.com')
    
    def test_update_profile(self):
        """Test updating user profile."""
        response = self.client.patch(
            self.profile_url,
            {'first_name': 'Updated', 'last_name': 'User'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify update
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'User')
    
    def test_profile_unauthenticated(self):
        """Test profile access fails without authentication."""
        self.client.credentials()  # Remove auth
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(
    SIMPLE_JWT={
        'ALGORITHM': 'HS256',
        'SIGNING_KEY': 'test-secret-key-for-testing-only',
    }
)
class ChangePasswordTests(APITestCase):
    """Tests for password change endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.change_password_url = '/api/v1/auth/password/change/'
        self.user = User.objects.create_user(
            email='changepass@example.com',
            password='OldPass123!',
            is_active=True
        )
        from rest_framework_simplejwt.tokens import RefreshToken
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(self.refresh.access_token)}'
        )
    
    def test_change_password_success(self):
        """Test successful password change."""
        response = self.client.post(
            self.change_password_url,
            {
                'old_password': 'OldPass123!',
                'new_password': 'NewSecure456!',
                'new_password_confirm': 'NewSecure456!'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewSecure456!'))
    
    def test_change_password_wrong_old_password(self):
        """Test password change fails with wrong old password."""
        response = self.client.post(
            self.change_password_url,
            {
                'old_password': 'WrongOldPass!',
                'new_password': 'NewSecure456!',
                'new_password_confirm': 'NewSecure456!'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PasswordResetTests(APITestCase):
    """Tests for password reset endpoint."""
    
    def setUp(self):
        self.client = APIClient()
        self.reset_request_url = '/api/v1/auth/password/reset/'
        self.user = User.objects.create_user(
            email='reset@example.com',
            password='OldPass123!',
            is_active=True
        )
    
    @patch('apps.base.core.users.views.send_password_reset_email_task')
    def test_password_reset_request_existing_email(self, mock_send_email):
        """Test password reset request for existing email."""
        mock_send_email.delay = MagicMock()
        
        response = self.client.post(
            self.reset_request_url,
            {'email': 'reset@example.com'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should always return success to prevent user enumeration
        self.assertTrue(response.data['success'])
    
    def test_password_reset_request_nonexistent_email(self):
        """Test password reset request for non-existent email returns same response."""
        response = self.client.post(
            self.reset_request_url,
            {'email': 'nonexistent@example.com'},
            format='json'
        )
        
        # Should return same success message to prevent user enumeration
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])


@override_settings(
    SIMPLE_JWT={
        'ALGORITHM': 'HS256',
        'SIGNING_KEY': 'test-secret-key-for-testing-only',
    }
)
class TokenBlacklistTests(APITestCase):
    """Tests for token blacklist functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='blacklist@example.com',
            password='SecurePass123!',
            is_active=True
        )
        from rest_framework_simplejwt.tokens import RefreshToken
        self.refresh = RefreshToken.for_user(self.user)
        self.access = self.refresh.access_token
    
    def test_blacklisted_token_rejected(self):
        """Test that blacklisted refresh token is rejected."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(self.access)}'
        )
        
        # First logout to blacklist the token
        self.client.post(
            '/api/v1/auth/logout/',
            {'refresh': str(self.refresh)},
            format='json'
        )
        
        # Try to use blacklisted refresh token
        response = self.client.post(
            '/api/v1/auth/token/refresh/',
            {'refresh': str(self.refresh)},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(
    SIMPLE_JWT={
        'ALGORITHM': 'HS256',
        'SIGNING_KEY': 'test-secret-key-for-testing-only',
    }
)
class UserAddressTests(APITestCase):
    """Tests for user address management."""
    
    def setUp(self):
        self.client = APIClient()
        self.addresses_url = '/api/v1/auth/addresses/'
        self.user = User.objects.create_user(
            email='address@example.com',
            password='SecurePass123!',
            is_active=True
        )
        from rest_framework_simplejwt.tokens import RefreshToken
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(self.refresh.access_token)}'
        )
    
    def test_create_address(self):
        """Test creating a new address."""
        response = self.client.post(
            self.addresses_url,
            {
                'label': 'Home',
                'full_name': 'Test User',
                'phone_number': '+84912345678',
                'address_line1': '123 Test Street',
                'city': 'Ho Chi Minh',
                'province': 'Ho Chi Minh',
                'postal_code': '70000',
                'country': 'VN'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_addresses(self):
        """Test listing user addresses."""
        from .models import UserAddress
        
        # Create an address first
        UserAddress.objects.create(
            user=self.user,
            label='Home',
            full_name='Test User',
            phone_number='+84912345678',
            address_line1='123 Test Street',
            city='Ho Chi Minh',
            province='Ho Chi Minh',
            postal_code='70000',
            country='VN'
        )
        
        response = self.client.get(self.addresses_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)


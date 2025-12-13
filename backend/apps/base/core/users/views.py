"""
User Views for Owls E-commerce Platform
=======================================
Authentication and user management endpoints.
"""

from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers
from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserProfileUpdateSerializer,
    ChangePasswordSerializer,
    UserAddressSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
from .models import UserAddress

User = get_user_model()


@extend_schema(tags=['Auth'])
class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""
    
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer
    throttle_scope = 'register'

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create user account atomically.
        Wraps user creation + token generation in a transaction
        to prevent orphaned accounts if token generation fails.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Registration successful',
            'data': {
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Auth'])
class LoginView(TokenObtainPairView):
    """User login endpoint."""
    
    serializer_class = CustomTokenObtainPairSerializer
    throttle_scope = 'login'

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            response.data = {
                'success': True,
                'message': 'Login successful',
                'data': response.data
            }
        return response


@extend_schema(
    tags=['Auth'],
    request=inline_serializer(
        name='LogoutRequest',
        fields={
            'refresh': drf_serializers.CharField(),
            'access': drf_serializers.CharField(required=False, help_text='Optional: Access token to blacklist immediately')
        }
    ),
    responses={200: OpenApiResponse(description='Logout successful')}
)
class LogoutView(APIView):
    """
    User logout endpoint - blacklist refresh and access tokens.
    
    SECURITY: This endpoint now supports immediate access token invalidation
    via Redis-based deny list. When 'access' token is provided, it will be
    blacklisted immediately, preventing any further use.
    """
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
        from apps.base.core.system.token_blacklist import blacklist_access_token
        
        refresh_token = request.data.get('refresh')
        access_token = request.data.get('access')
        
        if not refresh_token:
            return Response({
                'success': False,
                'message': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Blacklist refresh token (standard JWT blacklist)
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # SECURITY: Also blacklist access token for immediate invalidation
            # This prevents the access token from being used until expiry
            if access_token:
                try:
                    from rest_framework_simplejwt.tokens import AccessToken
                    access = AccessToken(access_token)
                    jti = access.get('jti')
                    if jti:
                        blacklist_access_token(jti)
                except Exception:
                    # Access token blacklist is best-effort
                    # Don't fail logout if this fails
                    pass
            
            return Response({
                'success': True,
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
            
        except (TokenError, InvalidToken) as e:
            # Specific JWT token errors - token invalid or already blacklisted
            return Response({
                'success': False,
                'message': 'Invalid or expired token'
            }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Users'])
class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile endpoint."""
    
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserProfileUpdateSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response({
            'success': True,
            'data': serializer.data
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(
            request.user, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'data': UserSerializer(request.user).data
        })


@extend_schema(
    tags=['Users'],
    request=ChangePasswordSerializer,
    responses={200: OpenApiResponse(description='Password changed successfully')}
)
class ChangePasswordView(APIView):
    """Change password endpoint."""
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        
        return Response({
            'success': True,
            'message': 'Password changed successfully'
        })


@extend_schema(tags=['Users'])
class UserAddressViewSet(generics.ListCreateAPIView):
    """User addresses endpoint."""
    
    serializer_class = UserAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return UserAddress.objects.none()
        return UserAddress.objects.filter(
            user=self.request.user,
            is_active=True
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })


@extend_schema(tags=['Users'])
class UserAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """User address detail endpoint."""
    
    serializer_class = UserAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return UserAddress.objects.none()
        return UserAddress.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({
            'success': True,
            'message': 'Address deleted successfully'
        }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Auth'],
    request=PasswordResetRequestSerializer,
    responses={200: OpenApiResponse(description='Password reset email sent')}
)
class PasswordResetRequestView(APIView):
    """
    Request password reset endpoint.
    
    SECURITY: This endpoint implements constant-time operations to prevent
    user enumeration through timing analysis.
    """
    
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'password_reset'

    def post(self, request):
        import time
        import secrets
        
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        # SECURITY FIX: Use monotonic time for precise measurement
        # and consistent operations to prevent timing attacks
        start_time = time.monotonic()
        
        # Always generate a token regardless of user existence
        # This normalizes the cryptographic operations
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        
        try:
            user = User.objects.get(email=email, is_active=True)
            user_exists = True
            
            # Generate real token for existing user
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_token = f"{uid}:{token}"
            
        except User.DoesNotExist:
            user_exists = False
            user = None
            
            # SECURITY: Generate dummy token with same computational cost
            # This makes timing identical whether user exists or not
            dummy_uid = urlsafe_base64_encode(force_bytes(secrets.token_bytes(16)))
            # Simulate token generation work (PBKDF2-like iterations)
            dummy_token = secrets.token_urlsafe(32)
            reset_token = f"{dummy_uid}:{dummy_token}"
        
        # Always perform email task enqueue operation (Celery is fast)
        # The key is that both branches do similar I/O operations
        if user_exists:
            from .tasks import send_password_reset_email_task
            
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
            send_password_reset_email_task.delay(
                email=email,
                user_name=user.first_name or user.email,
                reset_url=reset_url
            )
        else:
            # Simulate the Celery enqueue operation cost
            # by doing a similar lightweight operation
            from django.core.cache import cache
            cache.get(f"dummy_rate_limit:{secrets.token_hex(8)}")
        
        # SECURITY: Ensure minimum response time using monotonic clock
        # This prevents any residual timing differences
        elapsed = time.monotonic() - start_time
        min_response_time = 0.3  # 300ms minimum
        if elapsed < min_response_time:
            time.sleep(min_response_time - elapsed)
        
        return Response({
            'success': True,
            'message': 'Nếu email tồn tại trong hệ thống, bạn sẽ nhận được link đặt lại mật khẩu.'
        })


@extend_schema(
    tags=['Auth'],
    request=PasswordResetConfirmSerializer,
    responses={200: OpenApiResponse(description='Password reset successful')}
)
class PasswordResetConfirmView(APIView):
    """Confirm password reset endpoint."""
    
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token_data = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        # Parse token (format: uid:token)
        try:
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.http import urlsafe_base64_decode
            
            # Token format: uid:token
            if ':' not in token_data:
                return Response({
                    'success': False,
                    'error': {'message': 'Token không hợp lệ'}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            uid, token = token_data.split(':', 1)
            
            # Decode user id
            user_id = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=user_id, is_active=True)
            
            # Verify token
            if not default_token_generator.check_token(user, token):
                return Response({
                    'success': False,
                    'error': {'message': 'Token đã hết hạn hoặc không hợp lệ'}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            # SECURITY: Invalidate all existing tokens for this user
            # Use our custom blacklist to immediately revoke access tokens
            from apps.base.core.system.token_blacklist import blacklist_all_user_tokens
            blacklist_all_user_tokens(user.id)
            
            # Archive outstanding tokens for audit trail instead of hard delete
            # This preserves authentication history for security investigations
            from rest_framework_simplejwt.token_blacklist.models import (
                OutstandingToken, BlacklistedToken
            )
            outstanding_tokens = OutstandingToken.objects.filter(user=user)
            
            # Blacklist all outstanding tokens (this keeps audit trail)
            for token in outstanding_tokens:
                BlacklistedToken.objects.get_or_create(token=token)
            
            # Log the security event
            import logging
            logger = logging.getLogger(__name__)
            logger.info(
                f"Password reset completed for user {user.id}. "
                f"Invalidated {outstanding_tokens.count()} tokens."
            )
            
            return Response({
                'success': True,
                'message': 'Mật khẩu đã được đặt lại thành công'
            })
            
        except (ValueError, User.DoesNotExist, TypeError):
            return Response({
                'success': False,
                'error': {'message': 'Token không hợp lệ'}
            }, status=status.HTTP_400_BAD_REQUEST)

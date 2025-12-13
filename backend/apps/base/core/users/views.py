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
from django.utils import timezone
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

    def create(self, request, *args, **kwargs):
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
        fields={'refresh': drf_serializers.CharField()}
    ),
    responses={200: OpenApiResponse(description='Logout successful')}
)
class LogoutView(APIView):
    """User logout endpoint - blacklist refresh token."""
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'success': True,
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({
                'success': False,
                'message': 'Invalid token'
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
    """Request password reset endpoint."""
    
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'password_reset'

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email, is_active=True)
            
            # Generate password reset token
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.http import urlsafe_base64_encode
            from django.utils.encoding import force_bytes
            from django.core.mail import send_mail
            from django.conf import settings
            
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset URL
            reset_url = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"
            
            # Send email
            send_mail(
                subject='Đặt lại mật khẩu - Owls',
                message=f'''Xin chào {user.first_name or user.email},

Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản Owls.

Nhấp vào liên kết sau để đặt lại mật khẩu:
{reset_url}

Liên kết này sẽ hết hạn sau 1 giờ.

Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.

Trân trọng,
Đội ngũ Owls''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
            
        except User.DoesNotExist:
            # Don't reveal that user doesn't exist
            pass
        
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
            
            # Invalidate all sessions
            from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
            OutstandingToken.objects.filter(user=user).delete()
            
            return Response({
                'success': True,
                'message': 'Mật khẩu đã được đặt lại thành công'
            })
            
        except (ValueError, User.DoesNotExist, TypeError):
            return Response({
                'success': False,
                'error': {'message': 'Token không hợp lệ'}
            }, status=status.HTTP_400_BAD_REQUEST)

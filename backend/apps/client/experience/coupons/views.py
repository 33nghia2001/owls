"""
Coupons Views for Owls E-commerce Platform
==========================================
"""

from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Coupon, CouponUsage
from .serializers import (
    CouponSerializer,
    CouponDetailSerializer,
    ValidateCouponSerializer,
    ApplyCouponSerializer,
    CouponUsageSerializer,
    CouponCalculationResultSerializer
)


@extend_schema(tags=['Coupons'])
class PublicCouponsView(generics.ListAPIView):
    """
    List all active public coupons.
    
    Only shows coupons that are:
    - Active
    - Currently valid (started and not expired)
    - Not reached usage limit
    """
    
    serializer_class = CouponSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        now = timezone.now()
        return Coupon.objects.filter(
            is_active=True,
            starts_at__lte=now
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=now)
        ).filter(
            Q(usage_limit__isnull=True) | Q(times_used__lt=models.F('usage_limit'))
        ).order_by('-created_at')


@extend_schema(
    tags=['Coupons'],
    request=ValidateCouponSerializer,
    responses={
        200: CouponCalculationResultSerializer,
        400: OpenApiResponse(description='Invalid coupon')
    }
)
class ValidateCouponView(APIView):
    """
    Validate a coupon code and calculate discount.
    
    Returns whether the coupon is valid and the discount amount
    based on the provided subtotal.
    """
    
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ValidateCouponSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        subtotal = serializer.validated_data.get('subtotal', 0)
        
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return Response({
                'success': False,
                'data': {
                    'valid': False,
                    'code': code,
                    'message': 'Invalid coupon code'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check validity
        if not coupon.is_valid:
            return Response({
                'success': False,
                'data': {
                    'valid': False,
                    'code': code,
                    'message': 'This coupon is no longer valid'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check minimum order
        if subtotal and subtotal < coupon.min_order_amount:
            return Response({
                'success': False,
                'data': {
                    'valid': False,
                    'code': code,
                    'message': f'Minimum order amount is {coupon.min_order_amount}'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check per-user limit if authenticated
        if request.user.is_authenticated:
            user_usage = CouponUsage.objects.filter(
                coupon=coupon,
                user=request.user
            ).count()
            
            if user_usage >= coupon.usage_limit_per_user:
                return Response({
                    'success': False,
                    'data': {
                        'valid': False,
                        'code': code,
                        'message': 'You have reached the usage limit for this coupon'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate discount
        discount_amount = coupon.calculate_discount(subtotal) if subtotal else 0
        
        return Response({
            'success': True,
            'data': {
                'valid': True,
                'code': coupon.code,
                'name': coupon.name,
                'discount_type': coupon.discount_type,
                'discount_value': str(coupon.discount_value),
                'discount_amount': str(discount_amount),
                'min_order_amount': str(coupon.min_order_amount),
                'max_discount': str(coupon.max_discount) if coupon.max_discount else None,
                'expires_at': coupon.expires_at
            }
        })


@extend_schema(
    tags=['Coupons'],
    request=ApplyCouponSerializer,
    responses={
        200: OpenApiResponse(description='Coupon applied successfully'),
        400: OpenApiResponse(description='Invalid coupon')
    }
)
class ApplyCouponToCartView(APIView):
    """
    Apply a coupon to the user's cart.
    """
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from apps.business.commerce.cart.models import Cart
        
        serializer = ApplyCouponSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        coupon = Coupon.objects.get(code=code)
        
        # Get user's cart
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': 'Cart not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check minimum order amount
        if cart.subtotal < coupon.min_order_amount:
            return Response({
                'success': False,
                'error': {
                    'message': f'Minimum order amount is {coupon.min_order_amount}'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Apply coupon to cart
        cart.coupon = coupon
        cart.save(update_fields=['coupon', 'updated_at'])
        
        # Calculate discount
        discount_amount = coupon.calculate_discount(cart.subtotal)
        
        return Response({
            'success': True,
            'message': 'Coupon applied successfully',
            'data': {
                'code': coupon.code,
                'discount_type': coupon.discount_type,
                'discount_amount': str(discount_amount),
                'new_total': str(cart.subtotal - discount_amount)
            }
        })


@extend_schema(
    tags=['Coupons'],
    responses={
        200: OpenApiResponse(description='Coupon removed'),
        404: OpenApiResponse(description='No coupon applied')
    }
)
class RemoveCouponFromCartView(APIView):
    """Remove coupon from the user's cart."""
    
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        from apps.business.commerce.cart.models import Cart
        
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': 'Cart not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not cart.coupon:
            return Response({
                'success': False,
                'error': {'message': 'No coupon applied to cart'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cart.coupon = None
        cart.save(update_fields=['coupon', 'updated_at'])
        
        return Response({
            'success': True,
            'message': 'Coupon removed from cart'
        })


@extend_schema(tags=['Coupons'])
class CouponDetailView(generics.RetrieveAPIView):
    """Get coupon details by code."""
    
    serializer_class = CouponDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'code'

    def get_queryset(self):
        return Coupon.objects.filter(is_active=True)

    def get_object(self):
        code = self.kwargs['code'].upper().strip()
        return generics.get_object_or_404(self.get_queryset(), code=code)


@extend_schema(tags=['Coupons'])
class MyCouponUsageView(generics.ListAPIView):
    """List current user's coupon usage history."""
    
    serializer_class = CouponUsageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CouponUsage.objects.filter(
            user=self.request.user
        ).select_related('coupon', 'order').order_by('-used_at')


# Import models.F for the query
from django.db import models

"""
Order Views for Owls E-commerce Platform
========================================
"""

from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Order, OrderItem
from .serializers import (
    OrderListSerializer, OrderDetailSerializer,
    CreateOrderSerializer, CancelOrderSerializer
)
from apps.business.commerce.cart.models import Cart


@extend_schema(tags=['Orders'])
class OrderListView(generics.ListAPIView):
    """List user's orders."""
    
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


@extend_schema(tags=['Orders'])
class OrderDetailView(generics.RetrieveAPIView):
    """Get order details."""
    
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'order_number'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items', 'status_history', 'shipments')


@extend_schema(tags=['Orders'], request=CreateOrderSerializer, responses={201: OrderDetailSerializer})
class CreateOrderView(APIView):
    """
    Create order from cart.
    
    Security features:
    - Idempotency key required to prevent duplicate orders from double-clicks
    - Cart locked during order creation to prevent race conditions
    """
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from django.db import transaction
        from django.core.cache import cache
        
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        idempotency_key = str(serializer.validated_data['idempotency_key'])
        
        # SECURITY FIX: Use cache.add() for atomic idempotency check
        # Key format: order_idempotency:{user_id}:{idempotency_key}
        cache_key = f"order_idempotency:{user.id}:{idempotency_key}"
        
        # SECURITY: Use cache.add() which is atomic - only succeeds if key doesn't exist
        # This prevents TOCTOU race condition between cache.get() and cache.set()
        # Value 'processing' indicates request is being processed
        lock_acquired = cache.add(cache_key, 'processing', timeout=86400)  # 24 hours
        
        if not lock_acquired:
            # Key already exists - either processing or completed
            existing_value = cache.get(cache_key)
            if existing_value and existing_value != 'processing':
                # It's an order ID - return the existing order
                try:
                    existing_order = Order.objects.get(id=existing_value, user=user)
                    return Response({
                        'success': True,
                        'message': 'Order already created (duplicate request detected)',
                        'data': OrderDetailSerializer(existing_order).data,
                        'duplicate': True
                    }, status=status.HTTP_200_OK)
                except Order.DoesNotExist:
                    # Order was deleted, clear the key and allow retry
                    cache.delete(cache_key)
                    # Re-acquire the lock
                    if not cache.add(cache_key, 'processing', timeout=86400):
                        return Response({
                            'success': False,
                            'error': {'message': 'Request already in progress. Please wait.'}
                        }, status=status.HTTP_409_CONFLICT)
            else:
                # Another request is processing - return conflict
                return Response({
                    'success': False,
                    'error': {'message': 'Request already in progress. Please wait.'}
                }, status=status.HTTP_409_CONFLICT)
        
        try:
            # Lock cart with select_for_update to prevent race conditions
            cart = Cart.objects.select_for_update().get(user=user)
        except Cart.DoesNotExist:
            # Release the idempotency lock on failure
            cache.delete(cache_key)
            return Response({
                'success': False,
                'error': {'message': 'Cart not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        if cart.items.count() == 0:
            # Release the idempotency lock on failure
            cache.delete(cache_key)
            return Response({
                'success': False,
                'error': {'message': 'Cart is empty'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from apps.base.core.users.models import UserAddress
            shipping_address = UserAddress.objects.get(
                id=serializer.validated_data['shipping_address_id'],
                user=user
            )
        except UserAddress.DoesNotExist:
            # Release the idempotency lock on failure
            cache.delete(cache_key)
            return Response({
                'success': False,
                'error': {'message': 'Shipping address not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Use OrderService for atomic inventory management
            from .services import OrderService
            from apps.base.core.system.network import get_client_ip
            
            order_service = OrderService()
            order = order_service.create_from_cart(
                cart=cart,
                user=user,
                shipping_address=shipping_address,
                customer_note=serializer.validated_data.get('customer_note', ''),
                # SECURITY: Get real client IP, not proxy IP
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                source='web'
            )
            
            # SECURITY: Update idempotency key with actual order ID
            # This atomically replaces 'processing' with the real order ID
            cache.set(cache_key, str(order.id), timeout=86400)
            
            return Response({
                'success': True,
                'message': 'Order created successfully',
                'data': OrderDetailSerializer(order).data
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            # Release the idempotency lock on failure
            cache.delete(cache_key)
            return Response({
                'success': False,
                'error': {'message': str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Orders'], 
    request=CancelOrderSerializer,
    responses={
        200: OrderDetailSerializer,
        404: OpenApiResponse(description='Order not found'),
        400: OpenApiResponse(description='Order cannot be cancelled')
    }
)
class CancelOrderView(APIView):
    """Cancel an order."""
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_number):
        serializer = CancelOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            order = Order.objects.get(
                order_number=order_number,
                user=request.user
            )
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': 'Order not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Use OrderService for atomic inventory restoration
        from .services import OrderService
        
        order_service = OrderService(order)
        cancelled = order_service.cancel_order(
            reason=serializer.validated_data['reason']
        )
        
        if not cancelled:
            return Response({
                'success': False,
                'error': {'message': 'This order cannot be cancelled'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': True,
            'message': 'Order cancelled successfully',
            'data': OrderDetailSerializer(order_service.order).data
        })


@extend_schema(
    tags=['Orders'],
    responses={
        200: OpenApiResponse(description='Order tracking information'),
        404: OpenApiResponse(description='Order not found')
    }
)
class OrderTrackingView(APIView):
    """Track order status."""
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_number):
        try:
            order = Order.objects.get(
                order_number=order_number,
                user=request.user
            )
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': 'Order not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'data': {
                'order_number': order.order_number,
                'status': order.status,
                'payment_status': order.payment_status,
                'history': [
                    {
                        'status': h.new_status,
                        'note': h.note,
                        'timestamp': h.created_at
                    }
                    for h in order.status_history.all()
                ],
                'shipments': [
                    {
                        'tracking_number': s.tracking_number,
                        'carrier': s.carrier,
                        'status': s.status,
                        'tracking_url': s.tracking_url
                    }
                    for s in order.shipments.all()
                ]
            }
        })

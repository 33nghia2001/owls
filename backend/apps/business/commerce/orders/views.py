"""
Order Views for Owls E-commerce Platform
========================================
"""

from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
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
    """Create order from cart."""
    
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': 'Cart not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        if cart.items.count() == 0:
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
            return Response({
                'success': False,
                'error': {'message': 'Shipping address not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        order = Order.objects.create(
            user=user,
            email=user.email,
            phone=shipping_address.phone_number,
            subtotal=cart.subtotal,
            discount_amount=cart.discount_amount,
            shipping_amount=cart.shipping_amount,
            tax_amount=cart.tax_amount,
            total=cart.total,
            coupon=cart.coupon,
            coupon_code=cart.coupon.code if cart.coupon else '',
            shipping_address=shipping_address,
            shipping_name=shipping_address.recipient_name,
            shipping_phone=shipping_address.phone_number,
            shipping_address_line=shipping_address.full_address,
            shipping_city=shipping_address.city,
            shipping_country=shipping_address.country,
            customer_note=serializer.validated_data.get('customer_note', ''),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            source='web'
        )
        
        for cart_item in cart.items.select_related('product', 'variant'):
            product = cart_item.product
            vendor = product.vendor
            
            OrderItem.objects.create(
                order=order,
                vendor=vendor,
                product=product,
                variant=cart_item.variant,
                product_name=product.name,
                product_sku=product.sku,
                product_image=product.images.filter(is_primary=True).first().image.url if product.images.exists() else '',
                variant_name=cart_item.variant.name if cart_item.variant else '',
                selected_options=cart_item.selected_options,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                total_price=cart_item.total_price,
                commission_rate=vendor.commission_rate
            )
            
            if product.track_inventory:
                if cart_item.variant:
                    cart_item.variant.stock_quantity -= cart_item.quantity
                    cart_item.variant.save(update_fields=['stock_quantity'])
                else:
                    product.stock_quantity -= cart_item.quantity
                    product.save(update_fields=['stock_quantity'])
        
        # Increment coupon usage
        if cart.coupon:
            cart.coupon.increment_usage()
        
        cart.clear()
        
        return Response({
            'success': True,
            'message': 'Order created successfully',
            'data': OrderDetailSerializer(order).data
        }, status=status.HTTP_201_CREATED)


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
        
        if not order.can_cancel:
            return Response({
                'success': False,
                'error': {'message': 'This order cannot be cancelled'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        order.update_status(
            Order.Status.CANCELLED,
            note=serializer.validated_data['reason']
        )
        
        for item in order.items.select_related('product', 'variant'):
            if item.product.track_inventory:
                if item.variant:
                    item.variant.stock_quantity += item.quantity
                    item.variant.save(update_fields=['stock_quantity'])
                else:
                    item.product.stock_quantity += item.quantity
                    item.product.save(update_fields=['stock_quantity'])
        
        return Response({
            'success': True,
            'message': 'Order cancelled successfully',
            'data': OrderDetailSerializer(order).data
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

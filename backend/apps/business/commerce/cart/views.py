"""
Cart Views for Owls E-commerce Platform
=======================================
"""

from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Cart, CartItem
from .serializers import (
    CartSerializer, CartItemSerializer,
    AddToCartSerializer, UpdateCartItemSerializer, ApplyCouponSerializer
)
from apps.business.commerce.products.models import Product, ProductVariant


def get_or_create_cart(request):
    """Get or create cart for user/session."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        session_key = request.session.session_key
        if session_key:
            try:
                session_cart = Cart.objects.get(session_key=session_key, user__isnull=True)
                cart.merge_with(session_cart)
            except Cart.DoesNotExist:
                pass
    else:
        if not request.session.session_key:
            request.session.create()
        
        cart, created = Cart.objects.get_or_create(
            session_key=request.session.session_key,
            user__isnull=True
        )
    
    return cart


@extend_schema(tags=['Cart'], responses={200: CartSerializer})
class CartView(APIView):
    """Get current user's cart."""
    
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        cart = get_or_create_cart(request)
        serializer = CartSerializer(cart)
        return Response({
            'success': True,
            'data': serializer.data
        })


@extend_schema(tags=['Cart'], request=AddToCartSerializer, responses={200: CartSerializer, 201: CartSerializer})
class AddToCartView(APIView):
    """Add item to cart."""
    
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart = get_or_create_cart(request)
        
        try:
            product = Product.objects.get(
                id=serializer.validated_data['product_id'],
                status=Product.Status.PUBLISHED,
                is_active=True
            )
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': 'Product not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        quantity = serializer.validated_data['quantity']
        variant = None
        variant_id = serializer.validated_data.get('variant_id')
        
        if variant_id:
            try:
                variant = ProductVariant.objects.get(id=variant_id, product=product)
                if product.track_inventory and variant.stock_quantity < quantity:
                    return Response({
                        'success': False,
                        'error': {'message': 'Insufficient stock'}
                    }, status=status.HTTP_400_BAD_REQUEST)
            except ProductVariant.DoesNotExist:
                return Response({
                    'success': False,
                    'error': {'message': 'Variant not found'}
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            if product.track_inventory and product.stock_quantity < quantity:
                return Response({
                    'success': False,
                    'error': {'message': 'Insufficient stock'}
                }, status=status.HTTP_400_BAD_REQUEST)
        
        max_items = settings.OWLS_CONFIG.get('MAX_CART_ITEMS', 50)
        if cart.items.count() >= max_items:
            return Response({
                'success': False,
                'error': {'message': f'Maximum {max_items} items allowed in cart'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={
                'quantity': quantity,
                'selected_options': serializer.validated_data.get('selected_options', {})
            }
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return Response({
            'success': True,
            'message': 'Item added to cart',
            'data': CartSerializer(cart).data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@extend_schema(tags=['Cart'], request=UpdateCartItemSerializer, responses={200: CartSerializer})
class UpdateCartItemView(APIView):
    """Update cart item quantity."""
    
    permission_classes = [permissions.AllowAny]

    def patch(self, request, item_id):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart = get_or_create_cart(request)
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': 'Cart item not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        quantity = serializer.validated_data['quantity']
        
        if quantity == 0:
            cart_item.delete()
            message = 'Item removed from cart'
        else:
            product = cart_item.product
            if product.track_inventory:
                stock = cart_item.variant.stock_quantity if cart_item.variant else product.stock_quantity
                if stock < quantity:
                    return Response({
                        'success': False,
                        'error': {'message': 'Insufficient stock'}
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            cart_item.quantity = quantity
            cart_item.save()
            message = 'Cart updated'
        
        return Response({
            'success': True,
            'message': message,
            'data': CartSerializer(cart).data
        })


@extend_schema(tags=['Cart'], responses={200: CartSerializer})
class RemoveCartItemView(APIView):
    """Remove item from cart."""
    
    permission_classes = [permissions.AllowAny]

    def delete(self, request, item_id):
        cart = get_or_create_cart(request)
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
        except CartItem.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': 'Cart item not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'message': 'Item removed from cart',
            'data': CartSerializer(cart).data
        })


@extend_schema(
    tags=['Cart'], 
    request=None,
    responses={200: CartSerializer}
)
class ClearCartView(APIView):
    """Clear all items from cart."""
    
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        cart = get_or_create_cart(request)
        cart.clear()
        
        return Response({
            'success': True,
            'message': 'Cart cleared',
            'data': CartSerializer(cart).data
        })


@extend_schema(tags=['Cart'], request=ApplyCouponSerializer, responses={200: CartSerializer})
class ApplyCouponView(APIView):
    """Apply coupon to cart."""
    
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ApplyCouponSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart = get_or_create_cart(request)
        coupon_code = serializer.validated_data['coupon_code'].upper()
        
        # Import coupon model
        from apps.client.experience.coupons.models import Coupon
        
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code)
        except Coupon.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': 'Mã giảm giá không tồn tại'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate coupon
        if not coupon.is_valid:
            return Response({
                'success': False,
                'error': {'message': 'Mã giảm giá đã hết hạn hoặc không còn hiệu lực'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check minimum order amount
        if cart.subtotal < coupon.min_order_amount:
            return Response({
                'success': False,
                'error': {
                    'message': f'Đơn hàng tối thiểu {coupon.min_order_amount:,.0f}đ để sử dụng mã này'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check per-user usage limit
        if request.user.is_authenticated and coupon.usage_limit_per_user:
            from apps.business.commerce.orders.models import Order
            user_usage = Order.objects.filter(
                user=request.user,
                coupon=coupon
            ).count()
            if user_usage >= coupon.usage_limit_per_user:
                return Response({
                    'success': False,
                    'error': {'message': 'Bạn đã sử dụng hết lượt của mã giảm giá này'}
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Apply coupon
        cart.coupon = coupon
        cart.recalculate()
        
        return Response({
            'success': True,
            'message': f'Đã áp dụng mã giảm giá {coupon.code}',
            'data': CartSerializer(cart).data
        })


@extend_schema(
    tags=['Cart'], 
    request=None,
    responses={200: CartSerializer}
)
class RemoveCouponView(APIView):
    """Remove coupon from cart."""
    
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        cart = get_or_create_cart(request)
        cart.coupon = None
        cart.recalculate()
        
        return Response({
            'success': True,
            'message': 'Coupon removed',
            'data': CartSerializer(cart).data
        })

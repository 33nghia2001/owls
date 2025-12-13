"""
Coupon Service for Owls E-commerce Platform
============================================
Business logic for coupon validation and application with concurrency safety.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Optional, Dict, Any, List
from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone
import logging

if TYPE_CHECKING:
    from .models import Coupon
    from apps.business.commerce.cart.models import Cart
    from django.contrib.auth import get_user_model
    User = get_user_model()

logger = logging.getLogger(__name__)


class CouponValidationError(Exception):
    """Exception raised when coupon validation fails."""
    
    def __init__(self, message: str, code: str = 'invalid'):
        self.message = message
        self.code = code
        super().__init__(message)


class CouponService:
    """
    Service class for coupon operations with concurrency safety.
    Handles validation, application, and usage tracking.
    """
    
    @staticmethod
    @transaction.atomic
    def validate_and_apply(
        coupon_code: str,
        cart: 'Cart',
        user: Optional['User'] = None
    ) -> Dict[str, Any]:
        """
        Validate coupon and apply to cart with proper locking.
        Prevents race conditions when multiple users apply the same coupon.
        
        Args:
            coupon_code: Coupon code string
            cart: Cart instance
            user: Optional user instance
            
        Returns:
            dict with validation result
            
        Raises:
            CouponValidationError: If validation fails
        """
        from .models import Coupon, CouponUsage
        
        # Lock the coupon row to prevent race conditions
        try:
            coupon = Coupon.objects.select_for_update().get(
                code__iexact=coupon_code.strip()
            )
        except Coupon.DoesNotExist:
            raise CouponValidationError(
                'Mã giảm giá không tồn tại',
                code='not_found'
            )
        
        # Basic validity check
        now = timezone.now()
        
        if not coupon.is_active:
            raise CouponValidationError(
                'Mã giảm giá đã bị vô hiệu hóa',
                code='inactive'
            )
        
        if coupon.starts_at > now:
            raise CouponValidationError(
                f'Mã giảm giá sẽ có hiệu lực từ {coupon.starts_at.strftime("%d/%m/%Y %H:%M")}',
                code='not_started'
            )
        
        if coupon.expires_at and coupon.expires_at < now:
            raise CouponValidationError(
                'Mã giảm giá đã hết hạn',
                code='expired'
            )
        
        # Check global usage limit
        if coupon.usage_limit and coupon.times_used >= coupon.usage_limit:
            raise CouponValidationError(
                'Mã giảm giá đã hết lượt sử dụng',
                code='usage_limit_reached'
            )
        
        # Check minimum order amount
        if coupon.min_order_amount and cart.subtotal < coupon.min_order_amount:
            raise CouponValidationError(
                f'Đơn hàng tối thiểu {coupon.min_order_amount:,.0f}đ để sử dụng mã này',
                code='min_order_not_met'
            )
        
        # Check user-specific limits
        if user and coupon.usage_limit_per_user:
            user_usage_count = CouponUsage.objects.filter(
                coupon=coupon,
                user=user
            ).count()
            
            if user_usage_count >= coupon.usage_limit_per_user:
                raise CouponValidationError(
                    f'Bạn đã sử dụng mã này {user_usage_count} lần (tối đa {coupon.usage_limit_per_user})',
                    code='user_limit_reached'
                )
        
        # Check category restrictions (if applicable)
        if hasattr(coupon, 'allowed_categories') and coupon.allowed_categories.exists():
            cart_categories = set(
                item.product.category_id 
                for item in cart.items.select_related('product')
            )
            allowed_categories = set(
                coupon.allowed_categories.values_list('id', flat=True)
            )
            
            if not cart_categories.intersection(allowed_categories):
                raise CouponValidationError(
                    'Mã giảm giá không áp dụng cho các sản phẩm trong giỏ hàng',
                    code='category_not_allowed'
                )
        
        # Check product restrictions (if applicable)
        if hasattr(coupon, 'allowed_products') and coupon.allowed_products.exists():
            cart_products = set(
                item.product_id 
                for item in cart.items.all()
            )
            allowed_products = set(
                coupon.allowed_products.values_list('id', flat=True)
            )
            
            if not cart_products.intersection(allowed_products):
                raise CouponValidationError(
                    'Mã giảm giá không áp dụng cho các sản phẩm trong giỏ hàng',
                    code='product_not_allowed'
                )
        
        # Check user restrictions (if applicable)
        if hasattr(coupon, 'allowed_users') and coupon.allowed_users.exists():
            if not user or user.id not in coupon.allowed_users.values_list('id', flat=True):
                raise CouponValidationError(
                    'Mã giảm giá này chỉ dành cho một số khách hàng được chọn',
                    code='user_not_allowed'
                )
        
        # Calculate discount
        discount_amount = coupon.calculate_discount(cart.subtotal)
        
        logger.info(
            f"Coupon {coupon.code} validated for cart {cart.id}: "
            f"discount={discount_amount}"
        )
        
        return {
            'valid': True,
            'coupon': coupon,
            'discount_amount': discount_amount,
            'discount_type': coupon.discount_type,
            'message': f'Áp dụng mã giảm giá thành công! Giảm {discount_amount:,.0f}đ'
        }
    
    @staticmethod
    @transaction.atomic
    def record_usage(coupon: 'Coupon', user: Optional['User'], order) -> None:
        """
        Record coupon usage after successful order.
        Uses F() expression for atomic increment.
        
        Args:
            coupon: Coupon instance
            user: User who used the coupon
            order: Order instance
        """
        from .models import Coupon, CouponUsage
        
        # Atomic increment using F()
        Coupon.objects.filter(pk=coupon.pk).update(
            times_used=F('times_used') + 1
        )
        
        # Record usage for user tracking
        if user:
            CouponUsage.objects.create(
                coupon=coupon,
                user=user,
                order=order,
                discount_amount=order.discount_amount
            )
        
        logger.info(f"Coupon {coupon.code} usage recorded for order {order.order_number}")
    
    @staticmethod
    def get_available_coupons(
        user: Optional['User'] = None,
        cart_subtotal: Decimal = Decimal('0')
    ) -> List['Coupon']:
        """
        Get list of available coupons for user.
        
        Args:
            user: Optional user instance
            cart_subtotal: Current cart subtotal
            
        Returns:
            List of available Coupon instances
        """
        from .models import Coupon, CouponUsage
        
        now = timezone.now()
        
        # Base queryset: active, not expired, started
        queryset = Coupon.objects.filter(
            is_active=True,
            starts_at__lte=now
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=now)
        ).filter(
            Q(usage_limit__isnull=True) | Q(times_used__lt=F('usage_limit'))
        )
        
        # Filter by minimum order if subtotal provided
        if cart_subtotal > 0:
            queryset = queryset.filter(min_order_amount__lte=cart_subtotal)
        
        coupons = list(queryset)
        
        # Filter by user usage limit
        if user:
            user_usage = CouponUsage.objects.filter(user=user).values_list('coupon_id', flat=True)
            usage_counts = {}
            for coupon_id in user_usage:
                usage_counts[coupon_id] = usage_counts.get(coupon_id, 0) + 1
            
            coupons = [
                c for c in coupons
                if usage_counts.get(c.id, 0) < c.usage_limit_per_user
            ]
        
        return coupons

"""
Cart Service for Owls E-commerce Platform
=========================================
Business logic layer for cart operations with optimized DB queries.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Optional, Dict, Any
from django.db import transaction
from django.db.models import Sum, Count
from django.conf import settings
import logging

if TYPE_CHECKING:
    from .models import Cart, CartItem

logger = logging.getLogger(__name__)


class CartService:
    """
    Service class for cart operations.
    Separates business logic from models and uses DB aggregation for performance.
    """
    
    def __init__(self, cart):
        """
        Initialize cart service.
        
        Args:
            cart: Cart model instance
        """
        self.cart = cart
    
    def recalculate_totals(self) -> 'CartService':
        """
        Recalculate cart totals using database aggregation.
        More efficient than Python loops for large carts.
        
        Returns:
            self for method chaining
        """
        from .models import CartItem
        
        # Use database aggregation instead of Python loops
        aggregates = CartItem.objects.filter(cart=self.cart).aggregate(
            subtotal=Sum('total_price'),
            item_count=Sum('quantity'),
            total_items=Count('id')
        )
        
        self.cart.subtotal = aggregates['subtotal'] or Decimal('0.00')
        self.cart.item_count = aggregates['item_count'] or 0
        
        # Apply coupon discount
        if self.cart.coupon and self.cart.coupon.is_valid:
            self.cart.discount_amount = self.cart.coupon.calculate_discount(
                self.cart.subtotal
            )
        else:
            self.cart.discount_amount = Decimal('0.00')
        
        # Calculate tax (VAT)
        tax_rate = Decimal(str(settings.OWLS_CONFIG.get('TAX_RATE', 0.10)))
        taxable_amount = self.cart.subtotal - self.cart.discount_amount
        self.cart.tax_amount = taxable_amount * tax_rate
        
        # Calculate total
        self.cart.total = (
            self.cart.subtotal 
            - self.cart.discount_amount 
            + self.cart.tax_amount 
            + self.cart.shipping_amount
        )
        
        self.cart.save(update_fields=[
            'subtotal', 'discount_amount', 'tax_amount',
            'total', 'item_count', 'updated_at'
        ])
        
        return self
    
    @transaction.atomic
    def add_item(
        self, 
        product, 
        quantity: int = 1, 
        variant=None, 
        selected_options: Optional[Dict] = None
    ) -> 'CartItem':
        """
        Add item to cart with proper locking to prevent race conditions.
        
        Args:
            product: Product instance
            quantity: Quantity to add
            variant: Optional ProductVariant instance
            selected_options: Optional dict of selected options
            
        Returns:
            CartItem instance
        """
        from .models import CartItem
        
        # Lock the cart row to prevent concurrent modifications
        cart = type(self.cart).objects.select_for_update().get(pk=self.cart.pk)
        
        # Check for existing item
        existing_item = CartItem.objects.filter(
            cart=cart,
            product=product,
            variant=variant
        ).first()
        
        # Determine price
        unit_price = variant.price if variant else product.price
        
        if existing_item:
            existing_item.quantity += quantity
            existing_item.total_price = existing_item.unit_price * existing_item.quantity
            existing_item.save(update_fields=['quantity', 'total_price', 'updated_at'])
            item = existing_item
        else:
            item = CartItem.objects.create(
                cart=cart,
                product=product,
                variant=variant,
                quantity=quantity,
                unit_price=unit_price,
                total_price=unit_price * quantity,
                selected_options=selected_options or {}
            )
        
        # Recalculate totals
        self.cart = cart
        self.recalculate_totals()
        
        return item
    
    @transaction.atomic
    def update_item_quantity(self, item_id: str, quantity: int) -> Optional['CartItem']:
        """
        Update cart item quantity with locking.
        
        Args:
            item_id: CartItem ID
            quantity: New quantity (0 to remove)
            
        Returns:
            Updated CartItem or None if removed
        """
        from .models import CartItem
        
        # Lock the cart
        cart = type(self.cart).objects.select_for_update().get(pk=self.cart.pk)
        
        try:
            item = CartItem.objects.select_for_update().get(
                id=item_id,
                cart=cart
            )
        except CartItem.DoesNotExist:
            return None
        
        if quantity <= 0:
            item.delete()
            self.cart = cart
            self.recalculate_totals()
            return None
        
        item.quantity = quantity
        item.total_price = item.unit_price * quantity
        item.save(update_fields=['quantity', 'total_price', 'updated_at'])
        
        self.cart = cart
        self.recalculate_totals()
        
        return item
    
    @transaction.atomic
    def remove_item(self, item_id: str) -> bool:
        """
        Remove item from cart.
        
        Args:
            item_id: CartItem ID
            
        Returns:
            True if removed, False if not found
        """
        from .models import CartItem
        
        cart = type(self.cart).objects.select_for_update().get(pk=self.cart.pk)
        
        deleted_count, _ = CartItem.objects.filter(
            id=item_id,
            cart=cart
        ).delete()
        
        if deleted_count > 0:
            self.cart = cart
            self.recalculate_totals()
            return True
        
        return False
    
    @transaction.atomic
    def clear(self) -> 'CartService':
        """
        Clear all items from cart.
        
        Returns:
            self for method chaining
        """
        cart = type(self.cart).objects.select_for_update().get(pk=self.cart.pk)
        
        cart.items.all().delete()
        cart.coupon = None
        
        self.cart = cart
        self.recalculate_totals()
        
        return self
    
    @transaction.atomic
    def apply_coupon(self, coupon) -> Dict[str, Any]:
        """
        Apply coupon to cart with validation.
        
        Args:
            coupon: Coupon instance
            
        Returns:
            dict with status and message
        """
        cart = type(self.cart).objects.select_for_update().get(pk=self.cart.pk)
        
        # Validate coupon
        if not coupon.is_valid:
            return {
                'success': False,
                'message': 'Mã giảm giá không hợp lệ hoặc đã hết hạn'
            }
        
        # Check minimum order amount
        if hasattr(coupon, 'minimum_order_amount') and coupon.minimum_order_amount:
            if cart.subtotal < coupon.minimum_order_amount:
                return {
                    'success': False,
                    'message': f'Đơn hàng tối thiểu {coupon.minimum_order_amount:,.0f}đ để áp dụng mã này'
                }
        
        cart.coupon = coupon
        cart.save(update_fields=['coupon', 'updated_at'])
        
        self.cart = cart
        self.recalculate_totals()
        
        return {
            'success': True,
            'message': 'Áp dụng mã giảm giá thành công',
            'discount_amount': float(self.cart.discount_amount)
        }
    
    @transaction.atomic
    def remove_coupon(self) -> 'CartService':
        """
        Remove coupon from cart.
        
        Returns:
            self for method chaining
        """
        cart = type(self.cart).objects.select_for_update().get(pk=self.cart.pk)
        
        cart.coupon = None
        cart.save(update_fields=['coupon', 'updated_at'])
        
        self.cart = cart
        self.recalculate_totals()
        
        return self
    
    @transaction.atomic
    def merge_with(self, other_cart) -> 'CartService':
        """
        Merge another cart into this one with transaction safety.
        Validates stock limits when combining quantities.
        
        Args:
            other_cart: Cart instance to merge from
            
        Returns:
            self for method chaining
        """
        from .models import CartItem
        
        if other_cart.pk == self.cart.pk:
            return self
        
        # Lock both carts to prevent race conditions
        cart = type(self.cart).objects.select_for_update().get(pk=self.cart.pk)
        other = type(self.cart).objects.select_for_update().get(pk=other_cart.pk)
        
        for item in other.items.select_related('product', 'variant'):
            existing_item = CartItem.objects.filter(
                cart=cart,
                product=item.product,
                variant=item.variant
            ).first()
            
            if existing_item:
                # Calculate new quantity
                new_quantity = existing_item.quantity + item.quantity
                
                # Validate against stock
                if item.product.track_inventory:
                    available_stock = (
                        item.variant.stock_quantity if item.variant 
                        else item.product.stock_quantity
                    )
                    if new_quantity > available_stock:
                        # Cap at available stock instead of failing
                        new_quantity = available_stock
                        logger.warning(
                            f"Cart merge capped quantity for {item.product.name}: "
                            f"requested {existing_item.quantity + item.quantity}, "
                            f"available {available_stock}"
                        )
                
                existing_item.quantity = new_quantity
                existing_item.total_price = existing_item.unit_price * existing_item.quantity
                existing_item.save(update_fields=['quantity', 'total_price', 'updated_at'])
                
                # Delete the merged item
                item.delete()
            else:
                # Move item to this cart
                item.cart = cart
                item.save(update_fields=['cart', 'updated_at'])
        
        # Delete the other cart after successful merge
        other.delete()
        
        self.cart = cart
        self.recalculate_totals()
        
        return self
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get cart summary with all totals.
        
        Returns:
            dict with cart summary
        """
        return {
            'subtotal': float(self.cart.subtotal),
            'discount_amount': float(self.cart.discount_amount),
            'tax_amount': float(self.cart.tax_amount),
            'shipping_amount': float(self.cart.shipping_amount),
            'total': float(self.cart.total),
            'item_count': self.cart.item_count,
            'currency': self.cart.currency,
            'coupon_code': self.cart.coupon.code if self.cart.coupon else None,
        }


def get_cart_service(cart) -> CartService:
    """
    Factory function to create CartService instance.
    
    Args:
        cart: Cart instance
        
    Returns:
        CartService instance
    """
    return CartService(cart)

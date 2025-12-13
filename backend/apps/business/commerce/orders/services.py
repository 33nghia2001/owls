"""
Order Service for Owls E-commerce Platform
==========================================
Business logic layer for order operations with inventory locking.
"""

from __future__ import annotations

import secrets
import string
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, Dict, Any, List
from django.db import transaction, IntegrityError
from django.db.models import F
from django.conf import settings
from rest_framework.exceptions import ValidationError as DRFValidationError
import logging

if TYPE_CHECKING:
    from .models import Order

logger = logging.getLogger(__name__)


def generate_order_number() -> str:
    """
    Generate cryptographically secure unique order number.
    Uses secrets module instead of random for better entropy.
    
    Format: {PREFIX}{YYMMDD}{6-digit-random}
    Example: OWL2312130A3B5C
    
    Returns:
        str: Unique order number
    """
    prefix = settings.OWLS_CONFIG.get('ORDER_ID_PREFIX', 'OWL')
    date_part = datetime.now().strftime('%y%m%d')
    
    # Use secrets module for cryptographically secure random
    # Generate 6 alphanumeric characters (uppercase + digits)
    alphabet = string.ascii_uppercase + string.digits
    random_part = ''.join(secrets.choice(alphabet) for _ in range(6))
    
    return f'{prefix}{date_part}{random_part}'


def generate_tracking_number() -> str:
    """
    Generate unique tracking number for shipments.
    
    Returns:
        str: Unique tracking number
    """
    prefix = 'TRK'
    timestamp = datetime.now().strftime('%y%m%d%H%M')
    random_part = ''.join(secrets.choice(string.digits) for _ in range(6))
    
    return f'{prefix}{timestamp}{random_part}'


class OrderService:
    """
    Service class for order operations.
    Handles inventory management with proper locking.
    """
    
    def __init__(self, order=None):
        """
        Initialize order service.
        
        Args:
            order: Optional Order instance
        """
        self.order = order
    
    @transaction.atomic
    def create_from_cart(
        self, 
        cart, 
        user, 
        shipping_address,
        customer_note: str = '',
        ip_address: str = None,
        user_agent: str = '',
        source: str = 'web'
    ) -> 'Order':
        """
        Create order from cart with inventory locking to prevent overselling.
        
        Args:
            cart: Cart instance
            user: User instance
            shipping_address: UserAddress instance
            customer_note: Optional customer note
            ip_address: Client IP address
            user_agent: Client user agent
            source: Order source (web, app, etc.)
            
        Returns:
            Order instance
            
        Raises:
            ValueError: If cart is empty or inventory insufficient
        """
        from .models import Order, OrderItem
        from apps.business.commerce.products.models import Product, ProductVariant
        
        cart_items = list(cart.items.select_related('product', 'variant'))
        
        if not cart_items:
            raise ValueError('Cart is empty')
        
        # Lock all products and variants for update to prevent race conditions
        # IMPORTANT: Sort by ID to prevent deadlocks when multiple requests
        # lock the same products in different order
        product_ids = sorted([item.product_id for item in cart_items])
        variant_ids = sorted([item.variant_id for item in cart_items if item.variant_id])
        
        # Lock products (ordered by ID to prevent deadlock)
        locked_products = {
            p.id: p for p in Product.objects.select_for_update().filter(
                id__in=product_ids
            ).order_by('id')
        }
        
        # Lock variants (ordered by ID to prevent deadlock)
        locked_variants = {}
        if variant_ids:
            locked_variants = {
                v.id: v for v in ProductVariant.objects.select_for_update().filter(
                    id__in=variant_ids
                ).order_by('id')
            }
        
        # Validate inventory before creating order
        for item in cart_items:
            product = locked_products.get(item.product_id)
            if not product:
                raise ValueError(f'Product not found: {item.product_id}')
            
            if product.track_inventory:
                if item.variant_id:
                    variant = locked_variants.get(item.variant_id)
                    if not variant:
                        raise ValueError(f'Variant not found: {item.variant_id}')
                    if variant.stock_quantity < item.quantity:
                        raise ValueError(
                            f'Insufficient stock for {product.name} - {variant.name}: '
                            f'requested {item.quantity}, available {variant.stock_quantity}'
                        )
                else:
                    if product.stock_quantity < item.quantity:
                        raise ValueError(
                            f'Insufficient stock for {product.name}: '
                            f'requested {item.quantity}, available {product.stock_quantity}'
                        )
        
        # Create order
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
            customer_note=customer_note,
            ip_address=ip_address,
            user_agent=user_agent[:500] if user_agent else '',
            source=source
        )
        
        # Create order items and update inventory atomically
        for item in cart_items:
            product = locked_products[item.product_id]
            vendor = product.vendor
            
            # Get product image
            product_image = ''
            primary_image = product.images.filter(is_primary=True).first()
            if primary_image:
                product_image = primary_image.image.url
            
            OrderItem.objects.create(
                order=order,
                vendor=vendor,
                product=product,
                variant=item.variant,
                product_name=product.name,
                product_sku=product.sku,
                product_image=product_image,
                variant_name=item.variant.name if item.variant else '',
                selected_options=item.selected_options,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
                commission_rate=vendor.commission_rate
            )
            
            # Update inventory using F() expressions for atomicity
            # Wrapped in try/except to handle race condition where CheckConstraint
            # prevents stock going negative (two users buy last item simultaneously)
            if product.track_inventory:
                try:
                    if item.variant_id:
                        updated = ProductVariant.objects.filter(id=item.variant_id).update(
                            stock_quantity=F('stock_quantity') - item.quantity
                        )
                        if not updated:
                            raise DRFValidationError(
                                f'Sản phẩm {product.name} - {item.variant.name} không còn tồn tại.'
                            )
                    else:
                        updated = Product.objects.filter(id=product.id).update(
                            stock_quantity=F('stock_quantity') - item.quantity
                        )
                        if not updated:
                            raise DRFValidationError(
                                f'Sản phẩm {product.name} không còn tồn tại.'
                            )
                except IntegrityError:
                    # Database CheckConstraint violation - stock would go negative
                    variant_name = f' - {item.variant.name}' if item.variant else ''
                    raise DRFValidationError(
                        f'Sản phẩm {product.name}{variant_name} vừa hết hàng. '
                        f'Vui lòng giảm số lượng hoặc chọn sản phẩm khác.'
                    )
        
        # Increment coupon usage
        if cart.coupon:
            cart.coupon.increment_usage()
        
        # Clear cart
        from apps.business.commerce.cart.services import CartService
        CartService(cart).clear()
        
        self.order = order
        logger.info(f"Order {order.order_number} created successfully")
        
        return order
    
    @transaction.atomic
    def cancel_order(self, reason: str = '') -> bool:
        """
        Cancel order and restore inventory.
        
        Args:
            reason: Cancellation reason
            
        Returns:
            bool: True if cancelled successfully
        """
        from .models import Order
        from apps.business.commerce.products.models import Product, ProductVariant
        
        if not self.order:
            raise ValueError('No order specified')
        
        # Lock order
        order = Order.objects.select_for_update().get(pk=self.order.pk)
        
        if not order.can_cancel:
            return False
        
        # Get order items
        order_items = list(order.items.select_related('product', 'variant'))
        
        # Lock products and variants (sorted by ID to prevent deadlock)
        product_ids = sorted([item.product_id for item in order_items])
        variant_ids = sorted([item.variant_id for item in order_items if item.variant_id])
        
        Product.objects.select_for_update().filter(id__in=product_ids).order_by('id')
        if variant_ids:
            ProductVariant.objects.select_for_update().filter(id__in=variant_ids).order_by('id')
        
        # Restore inventory using F() expressions
        for item in order_items:
            if item.product.track_inventory:
                if item.variant_id:
                    ProductVariant.objects.filter(id=item.variant_id).update(
                        stock_quantity=F('stock_quantity') + item.quantity
                    )
                else:
                    Product.objects.filter(id=item.product_id).update(
                        stock_quantity=F('stock_quantity') + item.quantity
                    )
        
        # Update order status
        order.update_status(Order.Status.CANCELLED, note=reason)
        
        self.order = order
        logger.info(f"Order {order.order_number} cancelled")
        
        return True
    
    @transaction.atomic
    def refund_order(self, reason: str = '') -> bool:
        """
        Refund order and restore inventory.
        
        Args:
            reason: Refund reason
            
        Returns:
            bool: True if refunded successfully
        """
        from .models import Order
        from apps.business.commerce.products.models import Product, ProductVariant
        
        if not self.order:
            raise ValueError('No order specified')
        
        order = Order.objects.select_for_update().get(pk=self.order.pk)
        
        if not order.can_refund:
            return False
        
        # Restore inventory with proper locking (sorted by ID to prevent deadlock)
        order_items = list(order.items.select_related('product', 'variant'))
        
        product_ids = sorted([item.product_id for item in order_items])
        variant_ids = sorted([item.variant_id for item in order_items if item.variant_id])
        
        # Lock in consistent order
        Product.objects.select_for_update().filter(id__in=product_ids).order_by('id')
        if variant_ids:
            ProductVariant.objects.select_for_update().filter(id__in=variant_ids).order_by('id')
        
        for item in order_items:
            if item.product.track_inventory:
                if item.variant_id:
                    ProductVariant.objects.filter(id=item.variant_id).update(
                        stock_quantity=F('stock_quantity') + item.quantity
                    )
                else:
                    Product.objects.filter(id=item.product_id).update(
                        stock_quantity=F('stock_quantity') + item.quantity
                    )
        
        order.payment_status = Order.PaymentStatus.REFUNDED
        order.update_status(Order.Status.REFUNDED, note=reason)
        
        self.order = order
        logger.info(f"Order {order.order_number} refunded")
        
        return True
    
    def calculate_vendor_payouts(self) -> List[Dict[str, Any]]:
        """
        Calculate vendor payouts for the order.
        
        Returns:
            List of vendor payout details
        """
        if not self.order:
            raise ValueError('No order specified')
        
        payouts = {}
        
        for item in self.order.items.select_related('vendor'):
            vendor_id = str(item.vendor_id)
            
            if vendor_id not in payouts:
                payouts[vendor_id] = {
                    'vendor_id': vendor_id,
                    'vendor_name': item.vendor.name,
                    'total_sales': Decimal('0.00'),
                    'total_commission': Decimal('0.00'),
                    'total_payout': Decimal('0.00'),
                    'items': []
                }
            
            payouts[vendor_id]['total_sales'] += item.total_price
            payouts[vendor_id]['total_commission'] += item.commission_amount
            payouts[vendor_id]['total_payout'] += item.vendor_amount
            payouts[vendor_id]['items'].append({
                'product_name': item.product_name,
                'quantity': item.quantity,
                'total': float(item.total_price),
                'commission': float(item.commission_amount),
                'payout': float(item.vendor_amount),
            })
        
        return list(payouts.values())


def get_order_service(order=None) -> OrderService:
    """
    Factory function to create OrderService instance.
    
    Args:
        order: Optional Order instance
        
    Returns:
        OrderService instance
    """
    return OrderService(order)

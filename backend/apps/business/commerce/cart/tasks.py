"""
Cart Celery Tasks for Owls E-commerce Platform
==============================================
Asynchronous tasks for cart-related operations.
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(name='cart.cleanup_expired_carts')
def cleanup_expired_carts_task():
    """
    Periodic task to cleanup expired guest carts.
    Guest carts are identified by having session_key but no user.
    Should be scheduled via Celery Beat.
    """
    from .models import Cart
    
    try:
        now = timezone.now()
        
        # Delete guest carts that have expired
        expired_count, _ = Cart.objects.filter(
            user__isnull=True,
            session_key__isnull=False,
            expires_at__lt=now
        ).delete()
        
        # Delete old guest carts without expiration (older than 30 days)
        cutoff_date = now - timedelta(days=30)
        old_count, _ = Cart.objects.filter(
            user__isnull=True,
            session_key__isnull=False,
            expires_at__isnull=True,
            updated_at__lt=cutoff_date
        ).delete()
        
        # Delete empty carts older than 7 days
        empty_cutoff = now - timedelta(days=7)
        empty_count, _ = Cart.objects.filter(
            item_count=0,
            updated_at__lt=empty_cutoff
        ).delete()
        
        total_deleted = expired_count + old_count + empty_count
        logger.info(
            f"Cleaned up {total_deleted} carts "
            f"(expired: {expired_count}, old: {old_count}, empty: {empty_count})"
        )
        
        return {
            'status': 'success',
            'deleted': {
                'expired': expired_count,
                'old': old_count,
                'empty': empty_count,
                'total': total_deleted
            }
        }
        
    except Exception as exc:
        logger.error(f"Failed to cleanup carts: {exc}")
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
    name='cart.send_abandoned_cart_reminder'
)
def send_abandoned_cart_reminder_task(self, cart_id: str):
    """
    Send abandoned cart reminder email.
    
    Args:
        cart_id: Cart UUID
    """
    from django.core.mail import send_mail
    from django.conf import settings
    from .models import Cart
    
    try:
        cart = Cart.objects.select_related('user').prefetch_related('items__product').get(
            id=cart_id,
            user__isnull=False
        )
        
        if cart.item_count == 0:
            logger.info(f"Cart {cart_id} is empty, skipping reminder")
            return {'status': 'skipped', 'reason': 'empty_cart'}
        
        user = cart.user
        items_preview = ', '.join([
            item.product.name for item in cart.items.all()[:3]
        ])
        
        if cart.items.count() > 3:
            items_preview += f' và {cart.items.count() - 3} sản phẩm khác'
        
        subject = 'Bạn có sản phẩm trong giỏ hàng chờ thanh toán!'
        message = f'''Xin chào {user.first_name or user.email},

Bạn có {cart.item_count} sản phẩm trong giỏ hàng đang chờ thanh toán:
{items_preview}

Tổng giá trị: {cart.total:,.0f}đ

Đừng để lỡ cơ hội! Hoàn tất đơn hàng ngay hôm nay.

Truy cập: {settings.FRONTEND_URL}/cart

Trân trọng,
Đội ngũ {settings.SITE_NAME}'''

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Abandoned cart reminder sent to {user.email}")
        return {'status': 'success', 'email': user.email}
        
    except Cart.DoesNotExist:
        logger.warning(f"Cart {cart_id} not found or no user")
        return {'status': 'skipped', 'reason': 'cart_not_found'}
    except Exception as exc:
        logger.error(f"Failed to send abandoned cart reminder: {exc}")
        raise self.retry(exc=exc)


@shared_task(name='cart.identify_abandoned_carts')
def identify_abandoned_carts_task():
    """
    Identify abandoned carts and queue reminder emails.
    A cart is considered abandoned if:
    - User is logged in
    - Has items
    - Not updated in the last 24 hours
    - Not already reminded in the last 7 days
    """
    from django.utils import timezone
    from datetime import timedelta
    from .models import Cart
    
    try:
        now = timezone.now()
        abandoned_threshold = now - timedelta(hours=24)
        
        # Find abandoned carts
        abandoned_carts = Cart.objects.filter(
            user__isnull=False,
            item_count__gt=0,
            updated_at__lt=abandoned_threshold,
            updated_at__gt=now - timedelta(days=7),  # Don't remind for very old carts
        ).values_list('id', flat=True)
        
        queued_count = 0
        for cart_id in abandoned_carts:
            send_abandoned_cart_reminder_task.delay(str(cart_id))
            queued_count += 1
        
        logger.info(f"Queued {queued_count} abandoned cart reminders")
        
        return {
            'status': 'success',
            'queued': queued_count
        }
        
    except Exception as exc:
        logger.error(f"Failed to identify abandoned carts: {exc}")
        raise

"""
Order Celery Tasks for Owls E-commerce Platform
================================================
Asynchronous tasks for order-related operations.
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
    name='orders.cancel_unpaid_orders'
)
def cancel_unpaid_orders_task(self):
    """
    Periodic task to cancel orders that haven't been paid within timeout period.
    Restores inventory for cancelled orders.
    
    Should be scheduled via Celery Beat (e.g., every 5 minutes).
    
    This handles the scenario where:
    - User places order but abandons payment
    - Payment fails or times out
    - Stock is stuck as "deducted" but order never completes
    """
    from .models import Order
    from .services import OrderService
    
    # Get payment timeout from settings (default 30 minutes)
    timeout_minutes = settings.OWLS_CONFIG.get('PAYMENT_TIMEOUT_MINUTES', 30)
    cutoff_time = timezone.now() - timedelta(minutes=timeout_minutes)
    
    # Find orders that are:
    # 1. Still in PENDING status
    # 2. Payment status is UNPAID
    # 3. Created more than timeout_minutes ago
    unpaid_orders = Order.objects.filter(
        status=Order.Status.PENDING,
        payment_status=Order.PaymentStatus.UNPAID,
        created_at__lt=cutoff_time
    ).select_related('user')
    
    cancelled_count = 0
    failed_count = 0
    
    for order in unpaid_orders:
        try:
            service = OrderService(order)
            success = service.cancel_order(
                reason=f'Tự động hủy do không thanh toán trong {timeout_minutes} phút'
            )
            
            if success:
                cancelled_count += 1
                logger.info(
                    f"Auto-cancelled unpaid order {order.order_number} "
                    f"(created {order.created_at})"
                )
            else:
                failed_count += 1
                logger.warning(
                    f"Could not auto-cancel order {order.order_number}: "
                    f"status={order.status}"
                )
                
        except Exception as exc:
            failed_count += 1
            logger.error(
                f"Failed to auto-cancel order {order.order_number}: {exc}"
            )
    
    result = {
        'status': 'success',
        'cancelled': cancelled_count,
        'failed': failed_count,
        'timeout_minutes': timeout_minutes
    }
    
    if cancelled_count > 0:
        logger.info(
            f"Auto-cancelled {cancelled_count} unpaid orders "
            f"(timeout: {timeout_minutes} mins)"
        )
    
    return result


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
    name='orders.restore_stock_for_failed_payment'
)
def restore_stock_for_failed_payment_task(self, order_id: str):
    """
    Restore inventory when payment fails.
    Called from payment webhook when payment status is failed.
    
    Args:
        order_id: UUID of the order to restore stock for
    """
    from .models import Order
    from .services import OrderService
    
    try:
        order = Order.objects.get(id=order_id)
        
        # Only restore if order is still pending (not yet shipped/delivered)
        if order.status not in [Order.Status.PENDING, Order.Status.CONFIRMED]:
            logger.warning(
                f"Order {order.order_number} status is {order.status}, "
                f"skipping stock restoration"
            )
            return {'status': 'skipped', 'reason': 'invalid_status'}
        
        service = OrderService(order)
        success = service.cancel_order(reason='Thanh toán thất bại')
        
        if success:
            logger.info(f"Restored stock for failed payment order {order.order_number}")
            return {'status': 'success', 'order_number': order.order_number}
        else:
            logger.error(f"Failed to restore stock for order {order.order_number}")
            return {'status': 'failed', 'order_number': order.order_number}
            
    except Order.DoesNotExist:
        logger.error(f"Order not found: {order_id}")
        return {'status': 'error', 'reason': 'order_not_found'}


@shared_task(name='orders.send_order_confirmation_email')
def send_order_confirmation_email_task(order_id: str):
    """
    Send order confirmation email to customer.
    
    Args:
        order_id: UUID of the order
    """
    from .models import Order
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    
    try:
        order = Order.objects.select_related('user').prefetch_related('items').get(id=order_id)
        
        subject = f'Xác nhận đơn hàng #{order.order_number} - {settings.SITE_NAME}'
        
        # Plain text fallback
        message = f'''Xin chào {order.user.get_full_name() or order.user.email},

Cảm ơn bạn đã đặt hàng tại {settings.SITE_NAME}!

Mã đơn hàng: {order.order_number}
Tổng tiền: {order.total:,.0f} VNĐ

Trạng thái: {order.get_status_display()}

Chúng tôi sẽ thông báo khi đơn hàng được vận chuyển.

Trân trọng,
Đội ngũ {settings.SITE_NAME}'''

        # Try HTML template
        html_message = None
        try:
            html_message = render_to_string('emails/order_confirmation.html', {
                'order': order,
                'site_name': settings.SITE_NAME,
            })
        except Exception:
            pass  # Template not found, use plain text
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Order confirmation email sent for {order.order_number}")
        return {'status': 'success', 'order_number': order.order_number}
        
    except Order.DoesNotExist:
        logger.error(f"Order not found for email: {order_id}")
        return {'status': 'error', 'reason': 'order_not_found'}
    except Exception as exc:
        logger.error(f"Failed to send order confirmation email: {exc}")
        raise


@shared_task(name='orders.send_order_shipped_email')
def send_order_shipped_email_task(order_id: str, tracking_number: str = ''):
    """
    Send shipping notification email to customer.
    
    Args:
        order_id: UUID of the order
        tracking_number: Optional tracking number
    """
    from .models import Order
    from django.core.mail import send_mail
    
    try:
        order = Order.objects.select_related('user').get(id=order_id)
        
        subject = f'Đơn hàng #{order.order_number} đang được vận chuyển - {settings.SITE_NAME}'
        
        tracking_info = ''
        if tracking_number:
            tracking_info = f'\nMã vận đơn: {tracking_number}'
        
        message = f'''Xin chào {order.user.get_full_name() or order.user.email},

Đơn hàng #{order.order_number} của bạn đã được giao cho đơn vị vận chuyển.{tracking_info}

Địa chỉ giao hàng:
{order.shipping_name}
{order.shipping_address_line}
{order.shipping_city}

Bạn sẽ nhận được hàng trong vài ngày tới.

Trân trọng,
Đội ngũ {settings.SITE_NAME}'''

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=False,
        )
        
        logger.info(f"Shipped email sent for {order.order_number}")
        return {'status': 'success', 'order_number': order.order_number}
        
    except Order.DoesNotExist:
        logger.error(f"Order not found for shipped email: {order_id}")
        return {'status': 'error', 'reason': 'order_not_found'}
    except Exception as exc:
        logger.error(f"Failed to send shipped email: {exc}")
        raise

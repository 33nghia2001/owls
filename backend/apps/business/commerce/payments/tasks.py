"""
Payment Celery Tasks for Owls E-commerce Platform
==================================================
Asynchronous tasks for payment processing and reconciliation.
"""

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging
import hashlib
import hmac
import requests

from .models import Payment

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name='payments.reconcile_pending_payments',
    max_retries=3,
    default_retry_delay=60
)
def reconcile_pending_payments_task(self):
    """
    Reconcile pending payments by querying payment gateways.
    
    CRITICAL: Webhooks from VNPay/MoMo can be lost due to network issues
    or server downtime. This task proactively checks pending payments
    that are older than 15 minutes and queries the payment gateway
    to get the actual status.
    
    This prevents orders from being stuck in "pending" forever when
    the customer has already paid.
    
    Should be scheduled to run every 15 minutes via Celery Beat.
    """
    # Get pending payments older than 15 minutes but less than 24 hours
    now = timezone.now()
    min_age = now - timedelta(minutes=15)
    max_age = now - timedelta(hours=24)
    
    pending_payments = Payment.objects.filter(
        status=Payment.Status.PENDING,
        created_at__lt=min_age,
        created_at__gt=max_age
    ).select_related('payment_method', 'order')
    
    reconciled_count = 0
    failed_count = 0
    
    for payment in pending_payments:
        try:
            gateway = payment.payment_method.gateway if payment.payment_method else None
            
            if gateway == 'vnpay':
                result = _query_vnpay_transaction(payment)
            elif gateway == 'momo':
                result = _query_momo_transaction(payment)
            elif gateway == 'zalopay':
                result = _query_zalopay_transaction(payment)
            else:
                # Skip unknown gateways
                continue
            
            if result['success']:
                if result['status'] == 'completed':
                    _mark_payment_completed(payment, result.get('gateway_response', {}))
                    reconciled_count += 1
                elif result['status'] == 'failed':
                    _mark_payment_failed(payment, result.get('reason', 'Gateway reported failure'))
                    reconciled_count += 1
                # 'pending' status means still waiting - do nothing
                
        except Exception as e:
            logger.error(f"Error reconciling payment {payment.id}: {e}")
            failed_count += 1
    
    logger.info(
        f"Payment reconciliation completed: {reconciled_count} updated, "
        f"{failed_count} errors, {pending_payments.count()} checked"
    )
    
    return {
        'checked': pending_payments.count(),
        'reconciled': reconciled_count,
        'failed': failed_count
    }


def _query_vnpay_transaction(payment: Payment) -> dict:
    """
    Query VNPay for transaction status.
    
    Uses VNPay's Query Transaction API.
    """
    vnpay_config = getattr(settings, 'VNPAY_CONFIG', {})
    api_url = vnpay_config.get('API_URL', '')
    tmn_code = vnpay_config.get('TMN_CODE', '')
    hash_secret = vnpay_config.get('HASH_SECRET', '')
    
    if not all([api_url, tmn_code, hash_secret]):
        logger.warning("VNPay config incomplete, skipping reconciliation")
        return {'success': False, 'reason': 'config_missing'}
    
    try:
        import urllib.parse
        
        # Build query parameters
        params = {
            'vnp_RequestId': f"recon_{payment.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}",
            'vnp_Version': '2.1.0',
            'vnp_Command': 'querydr',
            'vnp_TmnCode': tmn_code,
            'vnp_TxnRef': payment.transaction_id,
            'vnp_OrderInfo': f'Reconcile order {payment.order.order_number}',
            'vnp_TransactionDate': payment.created_at.strftime('%Y%m%d%H%M%S'),
            'vnp_CreateDate': timezone.now().strftime('%Y%m%d%H%M%S'),
            'vnp_IpAddr': '127.0.0.1',
        }
        
        # Sort and build signature
        sorted_params = sorted(params.items())
        query_string = urllib.parse.urlencode(sorted_params)
        signature = hmac.new(
            hash_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest().upper()
        
        params['vnp_SecureHash'] = signature
        
        # Make API call
        response = requests.post(api_url, data=params, timeout=30)
        response.raise_for_status()
        
        result = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
        
        # Parse VNPay response
        response_code = result.get('vnp_ResponseCode', '')
        transaction_status = result.get('vnp_TransactionStatus', '')
        
        if response_code == '00' and transaction_status == '00':
            return {
                'success': True,
                'status': 'completed',
                'gateway_response': result
            }
        elif response_code == '00' and transaction_status in ['01', '02']:
            return {
                'success': True,
                'status': 'failed',
                'reason': f'VNPay status: {transaction_status}',
                'gateway_response': result
            }
        else:
            return {
                'success': True,
                'status': 'pending',
                'gateway_response': result
            }
            
    except requests.RequestException as e:
        logger.error(f"VNPay API error for payment {payment.id}: {e}")
        return {'success': False, 'reason': str(e)}


def _query_momo_transaction(payment: Payment) -> dict:
    """
    Query MoMo for transaction status.
    """
    momo_config = getattr(settings, 'MOMO_CONFIG', {})
    endpoint = momo_config.get('ENDPOINT', '')
    partner_code = momo_config.get('PARTNER_CODE', '')
    access_key = momo_config.get('ACCESS_KEY', '')
    secret_key = momo_config.get('SECRET_KEY', '')
    
    if not all([endpoint, partner_code, access_key, secret_key]):
        logger.warning("MoMo config incomplete, skipping reconciliation")
        return {'success': False, 'reason': 'config_missing'}
    
    try:
        request_id = f"recon_{payment.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}"
        
        # Build signature
        raw_signature = (
            f"accessKey={access_key}"
            f"&orderId={payment.transaction_id}"
            f"&partnerCode={partner_code}"
            f"&requestId={request_id}"
        )
        signature = hmac.new(
            secret_key.encode('utf-8'),
            raw_signature.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        payload = {
            'partnerCode': partner_code,
            'requestId': request_id,
            'orderId': payment.transaction_id,
            'signature': signature,
            'lang': 'vi'
        }
        
        response = requests.post(
            f"{endpoint}/query",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        result_code = result.get('resultCode', -1)
        
        if result_code == 0:
            return {
                'success': True,
                'status': 'completed',
                'gateway_response': result
            }
        elif result_code in [1000, 1001, 1002, 1003]:
            return {
                'success': True,
                'status': 'pending',
                'gateway_response': result
            }
        else:
            return {
                'success': True,
                'status': 'failed',
                'reason': f'MoMo error: {result_code}',
                'gateway_response': result
            }
            
    except requests.RequestException as e:
        logger.error(f"MoMo API error for payment {payment.id}: {e}")
        return {'success': False, 'reason': str(e)}


def _query_zalopay_transaction(payment: Payment) -> dict:
    """
    Query ZaloPay for transaction status.
    """
    zalopay_config = getattr(settings, 'ZALOPAY_CONFIG', {})
    endpoint = zalopay_config.get('ENDPOINT', '')
    app_id = zalopay_config.get('APP_ID', '')
    key1 = zalopay_config.get('KEY1', '')
    
    if not all([endpoint, app_id, key1]):
        logger.warning("ZaloPay config incomplete, skipping reconciliation")
        return {'success': False, 'reason': 'config_missing'}
    
    try:
        # Build MAC
        data = f"{app_id}|{payment.transaction_id}|{key1}"
        mac = hmac.new(
            key1.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        params = {
            'app_id': app_id,
            'app_trans_id': payment.transaction_id,
            'mac': mac
        }
        
        response = requests.post(
            f"{endpoint}/query",
            data=params,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        return_code = result.get('return_code', -1)
        
        if return_code == 1:
            return {
                'success': True,
                'status': 'completed',
                'gateway_response': result
            }
        elif return_code == 2:
            return {
                'success': True,
                'status': 'failed',
                'reason': 'ZaloPay reported failure',
                'gateway_response': result
            }
        else:
            return {
                'success': True,
                'status': 'pending',
                'gateway_response': result
            }
            
    except requests.RequestException as e:
        logger.error(f"ZaloPay API error for payment {payment.id}: {e}")
        return {'success': False, 'reason': str(e)}


def _mark_payment_completed(payment: Payment, gateway_response: dict):
    """Mark payment as completed and update order."""
    from django.db import transaction as db_transaction
    
    with db_transaction.atomic():
        # Sanitize gateway response before storing
        from apps.base.core.system.security import mask_sensitive_data
        
        payment.status = Payment.Status.COMPLETED
        payment.gateway_response = gateway_response
        payment.paid_at = timezone.now()
        payment.save()
        
        # Update order
        order = payment.order
        order.payment_status = 'paid'
        order.paid_at = timezone.now()
        order.save()
        order.update_status('confirmed', note='Payment confirmed via reconciliation')
    
    logger.info(f"Payment {payment.id} marked completed via reconciliation")


def _mark_payment_failed(payment: Payment, reason: str):
    """Mark payment as failed and restore stock."""
    from django.db import transaction as db_transaction
    
    with db_transaction.atomic():
        payment.status = Payment.Status.FAILED
        payment.failure_reason = reason
        payment.save()
        
        # Trigger stock restoration
        from apps.business.commerce.orders.tasks import restore_stock_for_failed_payment_task
        restore_stock_for_failed_payment_task.delay(str(payment.order_id))
    
    logger.warning(f"Payment {payment.id} marked failed via reconciliation: {reason}")


@shared_task(name='payments.expire_old_pending_payments')
def expire_old_pending_payments_task():
    """
    Expire payments that have been pending for more than 24 hours.
    
    These are likely abandoned payment attempts. Mark them as expired
    and restore the reserved stock.
    
    Should be scheduled to run every hour via Celery Beat.
    """
    cutoff = timezone.now() - timedelta(hours=24)
    
    expired_payments = Payment.objects.filter(
        status=Payment.Status.PENDING,
        created_at__lt=cutoff
    )
    
    count = 0
    for payment in expired_payments:
        _mark_payment_failed(payment, 'Payment expired after 24 hours')
        count += 1
    
    if count > 0:
        logger.info(f"Expired {count} old pending payments")
    
    return {'expired': count}

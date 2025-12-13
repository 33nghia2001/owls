"""
Payment Service for Owls E-commerce Platform
=============================================
Payment processing with idempotency and gateway adapters.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import string
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, Dict, Any
from datetime import datetime, timedelta
from django.db import transaction
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
import logging

if TYPE_CHECKING:
    from .models import Payment, PaymentMethod
    from apps.business.commerce.orders.models import Order

logger = logging.getLogger(__name__)


class IdempotencyError(Exception):
    """Raised when idempotent request is duplicated."""
    pass


class PaymentGatewayError(Exception):
    """Base exception for payment gateway errors."""
    
    def __init__(self, message: str, code: str = 'gateway_error', details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


# =============================================================================
# IDEMPOTENCY MANAGER
# =============================================================================

class IdempotencyManager:
    """
    Manages idempotency keys to prevent duplicate payments.
    Uses Redis cache for distributed environments.
    
    How it works:
    1. Client sends payment request with Idempotency-Key header
    2. If key exists in cache → return cached result (don't charge again)
    3. If key doesn't exist → process payment and cache result
    """
    
    CACHE_PREFIX = 'idempotency:'
    DEFAULT_TTL = 86400  # 24 hours
    
    @classmethod
    def generate_key(cls, user_id: str, order_id: str) -> str:
        """
        Generate idempotency key from user and order.
        
        Args:
            user_id: User UUID
            order_id: Order UUID
            
        Returns:
            str: Idempotency key
        """
        random_suffix = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
        raw_key = f'{user_id}:{order_id}:{random_suffix}'
        return hashlib.sha256(raw_key.encode()).hexdigest()[:32]
    
    @classmethod
    def check_and_set(cls, key: str, ttl: int = None) -> bool:
        """
        Check if key exists, if not set it atomically.
        
        Args:
            key: Idempotency key
            ttl: Time to live in seconds
            
        Returns:
            bool: True if key was set (new request), False if exists (duplicate)
        """
        cache_key = f'{cls.CACHE_PREFIX}{key}'
        ttl = ttl or cls.DEFAULT_TTL
        
        # Use Redis SETNX-like behavior
        result = cache.add(cache_key, 'processing', timeout=ttl)
        return result
    
    @classmethod
    def set_result(cls, key: str, result: Dict[str, Any], ttl: int = None) -> None:
        """
        Store the result of idempotent operation.
        
        Args:
            key: Idempotency key
            result: Result to cache
            ttl: Time to live in seconds
        """
        cache_key = f'{cls.CACHE_PREFIX}{key}'
        ttl = ttl or cls.DEFAULT_TTL
        cache.set(cache_key, result, timeout=ttl)
    
    @classmethod
    def get_result(cls, key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached result for idempotent operation.
        
        Args:
            key: Idempotency key
            
        Returns:
            Cached result or None
        """
        cache_key = f'{cls.CACHE_PREFIX}{key}'
        result = cache.get(cache_key)
        
        if result == 'processing':
            return None  # Still processing
        
        return result
    
    @classmethod
    def invalidate(cls, key: str) -> None:
        """
        Remove idempotency key (e.g., on failure).
        
        Args:
            key: Idempotency key
        """
        cache_key = f'{cls.CACHE_PREFIX}{key}'
        cache.delete(cache_key)


# =============================================================================
# PAYMENT GATEWAY ADAPTERS (Strategy Pattern)
# =============================================================================

class PaymentGatewayAdapter(ABC):
    """
    Abstract base class for payment gateway adapters.
    Each gateway (VNPay, MoMo, etc.) implements this interface.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize adapter with configuration.
        
        Args:
            config: Gateway-specific configuration
        """
        self.config = config or {}
    
    @abstractmethod
    def create_payment(
        self, 
        order: 'Order', 
        payment: 'Payment',
        return_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create payment on gateway.
        
        Args:
            order: Order instance
            payment: Payment instance
            return_url: URL to redirect after payment
            
        Returns:
            dict with payment_url and gateway-specific data
        """
        pass
    
    @abstractmethod
    def verify_callback(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify webhook/callback from gateway.
        
        Args:
            payload: Callback payload
            
        Returns:
            dict with verified data
        """
        pass
    
    @abstractmethod
    def check_status(self, transaction_id: str) -> Dict[str, Any]:
        """
        Query payment status from gateway.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            dict with status info
        """
        pass
    
    @abstractmethod
    def refund(self, payment: 'Payment', amount: Decimal, reason: str) -> Dict[str, Any]:
        """
        Process refund through gateway.
        
        Args:
            payment: Original payment
            amount: Amount to refund
            reason: Refund reason
            
        Returns:
            dict with refund result
        """
        pass


class VNPayAdapter(PaymentGatewayAdapter):
    """VNPay payment gateway adapter."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.tmn_code = self.config.get('TMN_CODE') or settings.VNPAY_CONFIG.get('TMN_CODE', '')
        self.hash_secret = self.config.get('HASH_SECRET') or settings.VNPAY_CONFIG.get('HASH_SECRET', '')
        self.payment_url = self.config.get('PAYMENT_URL') or settings.VNPAY_CONFIG.get('PAYMENT_URL', '')
        self.api_url = self.config.get('API_URL') or settings.VNPAY_CONFIG.get('API_URL', '')
    
    def _generate_signature(self, data: Dict[str, str]) -> str:
        """Generate HMAC-SHA512 signature for VNPay."""
        sorted_data = sorted(data.items())
        query_string = '&'.join(f'{k}={v}' for k, v in sorted_data if v)
        
        signature = hmac.new(
            self.hash_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        return signature
    
    def create_payment(
        self, 
        order: 'Order', 
        payment: 'Payment',
        return_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create VNPay payment URL."""
        import urllib.parse
        
        vnp_params = {
            'vnp_Version': '2.1.0',
            'vnp_Command': 'pay',
            'vnp_TmnCode': self.tmn_code,
            'vnp_Amount': int(payment.amount * 100),  # VNPay uses smallest unit
            'vnp_CurrCode': 'VND',
            'vnp_TxnRef': payment.transaction_id,
            'vnp_OrderInfo': f'Thanh toan don hang {order.order_number}',
            'vnp_OrderType': 'other',
            'vnp_Locale': 'vn',
            'vnp_ReturnUrl': return_url,
            'vnp_IpAddr': kwargs.get('ip_address', '127.0.0.1'),
            'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
        }
        
        # Add signature
        vnp_params['vnp_SecureHash'] = self._generate_signature(vnp_params)
        
        # Build payment URL
        query_string = urllib.parse.urlencode(vnp_params)
        payment_url = f'{self.payment_url}?{query_string}'
        
        logger.info(f"VNPay payment URL created for {payment.transaction_id}")
        
        return {
            'payment_url': payment_url,
            'transaction_id': payment.transaction_id,
            'gateway': 'vnpay'
        }
    
    def verify_callback(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Verify VNPay IPN callback."""
        received_signature = payload.pop('vnp_SecureHash', '')
        payload.pop('vnp_SecureHashType', None)
        
        # Recalculate signature
        calculated_signature = self._generate_signature(payload)
        
        if not hmac.compare_digest(calculated_signature.lower(), received_signature.lower()):
            raise PaymentGatewayError('Invalid signature', code='invalid_signature')
        
        response_code = payload.get('vnp_ResponseCode')
        transaction_status = payload.get('vnp_TransactionStatus')
        
        return {
            'verified': True,
            'success': response_code == '00' and transaction_status == '00',
            'transaction_id': payload.get('vnp_TxnRef'),
            'gateway_transaction_id': payload.get('vnp_TransactionNo'),
            'amount': int(payload.get('vnp_Amount', 0)) / 100,
            'response_code': response_code,
            'raw_payload': payload
        }
    
    def check_status(self, transaction_id: str) -> Dict[str, Any]:
        """Query VNPay for transaction status."""
        import requests
        
        query_params = {
            'vnp_Version': '2.1.0',
            'vnp_Command': 'querydr',
            'vnp_TmnCode': self.tmn_code,
            'vnp_TxnRef': transaction_id,
            'vnp_OrderInfo': f'Query transaction {transaction_id}',
            'vnp_TransactionDate': datetime.now().strftime('%Y%m%d%H%M%S'),
            'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
            'vnp_IpAddr': '127.0.0.1',
        }
        
        query_params['vnp_SecureHash'] = self._generate_signature(query_params)
        
        try:
            response = requests.post(self.api_url, data=query_params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return {
                'success': result.get('vnp_ResponseCode') == '00',
                'status': result.get('vnp_TransactionStatus'),
                'raw_response': result
            }
        except requests.RequestException as e:
            raise PaymentGatewayError(f'VNPay API error: {e}', code='api_error')
    
    def refund(self, payment: 'Payment', amount: Decimal, reason: str) -> Dict[str, Any]:
        """Process refund through VNPay."""
        import requests
        
        refund_params = {
            'vnp_Version': '2.1.0',
            'vnp_Command': 'refund',
            'vnp_TmnCode': self.tmn_code,
            'vnp_TxnRef': payment.transaction_id,
            'vnp_Amount': int(amount * 100),
            'vnp_TransactionNo': payment.gateway_transaction_id,
            'vnp_TransactionType': '02',  # Full refund
            'vnp_OrderInfo': reason,
            'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
            'vnp_IpAddr': '127.0.0.1',
        }
        
        refund_params['vnp_SecureHash'] = self._generate_signature(refund_params)
        
        try:
            response = requests.post(self.api_url, data=refund_params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            success = result.get('vnp_ResponseCode') == '00'
            
            return {
                'success': success,
                'refund_id': result.get('vnp_TransactionNo'),
                'raw_response': result
            }
        except requests.RequestException as e:
            raise PaymentGatewayError(f'VNPay refund error: {e}', code='refund_error')


class MoMoAdapter(PaymentGatewayAdapter):
    """MoMo payment gateway adapter."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.partner_code = self.config.get('PARTNER_CODE') or settings.MOMO_CONFIG.get('PARTNER_CODE', '')
        self.access_key = self.config.get('ACCESS_KEY') or settings.MOMO_CONFIG.get('ACCESS_KEY', '')
        self.secret_key = self.config.get('SECRET_KEY') or settings.MOMO_CONFIG.get('SECRET_KEY', '')
        self.endpoint = self.config.get('ENDPOINT') or settings.MOMO_CONFIG.get('ENDPOINT', '')
    
    def _generate_signature(self, raw_data: str) -> str:
        """Generate HMAC-SHA256 signature for MoMo."""
        return hmac.new(
            self.secret_key.encode('utf-8'),
            raw_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def create_payment(
        self, 
        order: 'Order', 
        payment: 'Payment',
        return_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create MoMo payment URL."""
        import requests
        import json
        
        request_id = payment.transaction_id
        order_id = payment.transaction_id
        order_info = f'Thanh toan don hang {order.order_number}'
        amount = int(payment.amount)
        notify_url = kwargs.get('notify_url', return_url)
        
        # Build raw signature string
        raw_signature = (
            f'accessKey={self.access_key}'
            f'&amount={amount}'
            f'&extraData='
            f'&ipnUrl={notify_url}'
            f'&orderId={order_id}'
            f'&orderInfo={order_info}'
            f'&partnerCode={self.partner_code}'
            f'&redirectUrl={return_url}'
            f'&requestId={request_id}'
            f'&requestType=captureWallet'
        )
        
        signature = self._generate_signature(raw_signature)
        
        payload = {
            'partnerCode': self.partner_code,
            'accessKey': self.access_key,
            'requestId': request_id,
            'amount': str(amount),
            'orderId': order_id,
            'orderInfo': order_info,
            'redirectUrl': return_url,
            'ipnUrl': notify_url,
            'extraData': '',
            'requestType': 'captureWallet',
            'signature': signature,
            'lang': 'vi'
        }
        
        try:
            response = requests.post(
                f'{self.endpoint}/v2/gateway/api/create',
                json=payload,
                timeout=30
            )
            result = response.json()
            
            if result.get('resultCode') == 0:
                return {
                    'payment_url': result.get('payUrl'),
                    'transaction_id': payment.transaction_id,
                    'gateway': 'momo'
                }
            else:
                raise PaymentGatewayError(
                    result.get('message', 'MoMo error'),
                    code='momo_error',
                    details=result
                )
        except requests.RequestException as e:
            raise PaymentGatewayError(f'MoMo API error: {e}', code='api_error')
    
    def verify_callback(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Verify MoMo IPN callback."""
        received_signature = payload.get('signature', '')
        
        # Build raw signature string for verification
        raw_signature = (
            f'accessKey={self.access_key}'
            f'&amount={payload.get("amount")}'
            f'&extraData={payload.get("extraData", "")}'
            f'&message={payload.get("message")}'
            f'&orderId={payload.get("orderId")}'
            f'&orderInfo={payload.get("orderInfo")}'
            f'&orderType={payload.get("orderType")}'
            f'&partnerCode={payload.get("partnerCode")}'
            f'&payType={payload.get("payType")}'
            f'&requestId={payload.get("requestId")}'
            f'&responseTime={payload.get("responseTime")}'
            f'&resultCode={payload.get("resultCode")}'
            f'&transId={payload.get("transId")}'
        )
        
        calculated_signature = self._generate_signature(raw_signature)
        
        if not hmac.compare_digest(calculated_signature, received_signature):
            raise PaymentGatewayError('Invalid signature', code='invalid_signature')
        
        return {
            'verified': True,
            'success': payload.get('resultCode') == 0,
            'transaction_id': payload.get('orderId'),
            'gateway_transaction_id': payload.get('transId'),
            'amount': int(payload.get('amount', 0)),
            'response_code': payload.get('resultCode'),
            'raw_payload': payload
        }
    
    def check_status(self, transaction_id: str) -> Dict[str, Any]:
        """Query MoMo for transaction status."""
        # Implementation similar to create_payment
        return {'success': False, 'message': 'Not implemented'}
    
    def refund(self, payment: 'Payment', amount: Decimal, reason: str) -> Dict[str, Any]:
        """Process refund through MoMo."""
        # Implementation similar to create_payment
        return {'success': False, 'message': 'Not implemented'}


class CODAdapter(PaymentGatewayAdapter):
    """Cash on Delivery adapter (no external gateway)."""
    
    def create_payment(
        self, 
        order: 'Order', 
        payment: 'Payment',
        return_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """COD doesn't need external gateway."""
        return {
            'payment_url': None,
            'transaction_id': payment.transaction_id,
            'gateway': 'cod',
            'message': 'Thanh toán khi nhận hàng'
        }
    
    def verify_callback(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """COD doesn't have callbacks."""
        return {'verified': True, 'success': True}
    
    def check_status(self, transaction_id: str) -> Dict[str, Any]:
        """COD status is tracked internally."""
        return {'success': True, 'status': 'pending'}
    
    def refund(self, payment: 'Payment', amount: Decimal, reason: str) -> Dict[str, Any]:
        """COD refund is handled manually."""
        return {'success': True, 'message': 'Refund processed manually'}


# =============================================================================
# GATEWAY FACTORY
# =============================================================================

class PaymentGatewayFactory:
    """
    Factory for creating payment gateway adapters.
    """
    
    _adapters = {
        'vnpay': VNPayAdapter,
        'momo': MoMoAdapter,
        'cod': CODAdapter,
        # Add more gateways here
    }
    
    @classmethod
    def create(cls, gateway_code: str, config: Dict[str, Any] = None) -> PaymentGatewayAdapter:
        """
        Create appropriate gateway adapter.
        
        Args:
            gateway_code: Gateway code (vnpay, momo, etc.)
            config: Optional configuration override
            
        Returns:
            PaymentGatewayAdapter instance
            
        Raises:
            ValueError: If gateway not supported
        """
        adapter_class = cls._adapters.get(gateway_code)
        
        if not adapter_class:
            raise ValueError(f'Unsupported payment gateway: {gateway_code}')
        
        return adapter_class(config)
    
    @classmethod
    def register(cls, gateway_code: str, adapter_class: type) -> None:
        """
        Register a new gateway adapter.
        
        Args:
            gateway_code: Gateway code
            adapter_class: Adapter class
        """
        cls._adapters[gateway_code] = adapter_class


# =============================================================================
# PAYMENT SERVICE
# =============================================================================

class PaymentService:
    """
    Main payment service with idempotency support.
    Orchestrates payment creation, verification, and refunds.
    """
    
    @classmethod
    @transaction.atomic
    def create_payment(
        cls,
        order: 'Order',
        payment_method: 'PaymentMethod',
        return_url: str,
        idempotency_key: str = None,
        ip_address: str = None,
        user_agent: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create payment with idempotency protection.
        
        Args:
            order: Order to pay for
            payment_method: Selected payment method
            return_url: Redirect URL after payment
            idempotency_key: Client-provided idempotency key
            ip_address: Client IP
            user_agent: Client user agent
            
        Returns:
            dict with payment info and redirect URL
            
        Raises:
            IdempotencyError: If duplicate request detected
            PaymentGatewayError: If gateway error occurs
        """
        from .models import Payment
        
        # Check idempotency
        if idempotency_key:
            existing_result = IdempotencyManager.get_result(idempotency_key)
            if existing_result:
                logger.info(f"Idempotent request detected: {idempotency_key}")
                return existing_result
            
            if not IdempotencyManager.check_and_set(idempotency_key):
                raise IdempotencyError(
                    'Yêu cầu thanh toán đang được xử lý. Vui lòng đợi.'
                )
        
        try:
            # Calculate fee
            fee = payment_method.calculate_fee(order.total)
            
            # Create payment record
            payment = Payment.objects.create(
                order=order,
                user=order.user,
                payment_method=payment_method,
                currency=order.currency,
                amount=order.total,
                fee=fee,
                net_amount=order.total - fee,
                ip_address=ip_address,
                user_agent=user_agent[:500] if user_agent else ''
            )
            
            # Get gateway adapter and create payment
            gateway = PaymentGatewayFactory.create(payment_method.gateway)
            
            result = gateway.create_payment(
                order=order,
                payment=payment,
                return_url=return_url,
                ip_address=ip_address,
                **kwargs
            )
            
            # Update payment with gateway info
            payment.gateway_response = result
            payment.save(update_fields=['gateway_response'])
            
            response = {
                'success': True,
                'payment_id': str(payment.id),
                'transaction_id': payment.transaction_id,
                'payment_url': result.get('payment_url'),
                'amount': str(payment.amount),
                'fee': str(payment.fee),
                'gateway': payment_method.gateway,
                'message': result.get('message', 'Thanh toán đã được tạo')
            }
            
            # Cache result for idempotency
            if idempotency_key:
                IdempotencyManager.set_result(idempotency_key, response)
            
            logger.info(
                f"Payment {payment.transaction_id} created for order {order.order_number}"
            )
            
            return response
            
        except Exception as e:
            # Invalidate idempotency on failure
            if idempotency_key:
                IdempotencyManager.invalidate(idempotency_key)
            raise
    
    @classmethod
    def process_callback(
        cls,
        gateway_code: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process payment gateway callback/webhook.
        
        Args:
            gateway_code: Gateway that sent the callback
            payload: Callback payload
            
        Returns:
            dict with processing result
        """
        from .models import Payment
        from apps.business.commerce.orders.models import Order
        
        gateway = PaymentGatewayFactory.create(gateway_code)
        
        # Verify callback signature
        verified_data = gateway.verify_callback(payload)
        
        if not verified_data.get('verified'):
            raise PaymentGatewayError('Callback verification failed')
        
        # Find payment
        transaction_id = verified_data.get('transaction_id')
        
        try:
            payment = Payment.objects.select_for_update().get(
                transaction_id=transaction_id
            )
        except Payment.DoesNotExist:
            raise PaymentGatewayError(
                f'Payment not found: {transaction_id}',
                code='payment_not_found'
            )
        
        # Prevent duplicate processing
        if payment.status == Payment.Status.COMPLETED:
            logger.warning(f"Payment {transaction_id} already completed, skipping")
            return {'success': True, 'message': 'Already processed'}
        
        # Update payment based on result
        if verified_data.get('success'):
            payment.status = Payment.Status.COMPLETED
            payment.gateway_transaction_id = verified_data.get('gateway_transaction_id', '')
            payment.gateway_response = verified_data.get('raw_payload', {})
            payment.paid_at = timezone.now()
            payment.save()
            
            # Update order status
            order = payment.order
            order.payment_status = Order.PaymentStatus.PAID
            order.paid_at = timezone.now()
            order.save()
            order.update_status(Order.Status.PAID, note=f'Payment via {gateway_code}')
            
            logger.info(f"Payment {transaction_id} completed successfully")
            
        else:
            payment.status = Payment.Status.FAILED
            payment.gateway_response = verified_data.get('raw_payload', {})
            payment.failure_reason = f"Gateway error: {verified_data.get('response_code')}"
            payment.save()
            
            # Trigger stock restoration
            from apps.business.commerce.orders.tasks import restore_stock_for_failed_payment_task
            restore_stock_for_failed_payment_task.delay(str(payment.order_id))
            
            logger.warning(f"Payment {transaction_id} failed: {verified_data.get('response_code')}")
        
        return {
            'success': verified_data.get('success'),
            'transaction_id': transaction_id,
            'status': payment.status
        }

"""
Payment Views for Owls E-commerce Platform
==========================================
"""

from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import PaymentMethod, Payment
from .serializers import (
    PaymentMethodSerializer, PaymentSerializer,
    CreatePaymentSerializer, VerifyPaymentSerializer
)
from apps.business.commerce.orders.models import Order


@extend_schema(tags=['Payments'])
class PaymentMethodListView(generics.ListAPIView):
    """List available payment methods."""
    
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return PaymentMethod.objects.filter(is_active=True).order_by('order')


@extend_schema(
    tags=['Payments'],
    request=CreatePaymentSerializer,
    responses={
        201: OpenApiResponse(description='Payment created successfully'),
        404: OpenApiResponse(description='Order or payment method not found')
    }
)
class CreatePaymentView(APIView):
    """Create payment for order."""
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            order = Order.objects.get(
                id=serializer.validated_data['order_id'],
                user=request.user,
                status=Order.Status.PENDING
            )
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': 'Order not found or already processed'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            payment_method = PaymentMethod.objects.get(
                code=serializer.validated_data['payment_method_code'],
                is_active=True
            )
        except PaymentMethod.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': 'Payment method not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        fee = payment_method.calculate_fee(order.total)
        
        # SECURITY: Get real client IP, not proxy IP
        from apps.base.core.system.network import get_client_ip
        
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            payment_method=payment_method,
            currency=order.currency,
            amount=order.total,
            fee=fee,
            net_amount=order.total - fee,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )
        
        payment_data = {
            'payment_id': str(payment.id),
            'transaction_id': payment.transaction_id,
            'amount': str(order.total),
            'currency': order.currency,
        }
        
        if payment_method.gateway == 'cod':
            payment.status = Payment.Status.PENDING
            payment.save()
            payment_data['message'] = 'Cash on delivery - pay when you receive'
        else:
            payment_data['payment_url'] = f'https://payment.owls.asia/pay/{payment.transaction_id}'
        
        return Response({
            'success': True,
            'message': 'Payment created',
            'data': payment_data
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Payments'])
class PaymentDetailView(generics.RetrieveAPIView):
    """Get payment details."""
    
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'transaction_id'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Payment.objects.none()
        return Payment.objects.filter(user=self.request.user)


@extend_schema(
    tags=['Payments'],
    request=None,
    responses={
        200: PaymentSerializer,
        404: OpenApiResponse(description='Payment not found')
    }
)
class VerifyPaymentView(APIView):
    """Verify payment status."""
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, transaction_id):
        try:
            payment = Payment.objects.get(
                transaction_id=transaction_id,
                user=request.user
            )
        except Payment.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': 'Payment not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'data': PaymentSerializer(payment).data
        })


@extend_schema(
    tags=['Payments'],
    request=None,
    responses={200: OpenApiResponse(description='Webhook received')}
)
class PaymentWebhookView(APIView):
    """Handle payment gateway webhooks with signature verification."""
    
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # No auth for webhooks
    
    # SECURITY: Fields that should be redacted from stored gateway responses
    # to prevent sensitive data from being logged or stored in database
    SENSITIVE_FIELDS = {
        'vnp_SecureHash', 'vnp_SecureHashType',
        'signature', 'accessKey', 'secretKey',
        'mac', 'key1', 'key2',
        'cardNumber', 'card_number', 'cardNo',
        'cvv', 'cvc', 'securityCode',
        'expiryDate', 'expiry_date', 'exp',
        'password', 'pin', 'otp',
    }
    
    def _sanitize_payload(self, payload: dict) -> dict:
        """
        Remove sensitive fields from payload before storing.
        
        SECURITY: Prevents sensitive data from being logged or stored in DB.
        """
        if not isinstance(payload, dict):
            return payload
        
        sanitized = {}
        for key, value in payload.items():
            if key.lower() in {f.lower() for f in self.SENSITIVE_FIELDS}:
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_payload(value)
            else:
                sanitized[key] = value
        return sanitized

    def post(self, request, gateway):
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Log webhook received (sanitize sensitive data)
        logger.info(f"Webhook received from {gateway}")
        
        payload = request.data
        
        if gateway == 'vnpay':
            return self._handle_vnpay_webhook(request, payload)
        elif gateway == 'momo':
            return self._handle_momo_webhook(request, payload)
        elif gateway == 'zalopay':
            return self._handle_zalopay_webhook(request, payload)
        else:
            logger.warning(f"Unknown payment gateway: {gateway}")
            return Response({'status': 'unknown_gateway'}, status=status.HTTP_400_BAD_REQUEST)
    
    def _verify_vnpay_signature(self, payload: dict) -> bool:
        """
        Verify VNPay secure hash signature.
        
        CRITICAL SECURITY: Prevents webhook forgery attacks.
        """
        import hashlib
        import hmac
        import urllib.parse
        from django.conf import settings
        
        received_hash = payload.get('vnp_SecureHash', '')
        if not received_hash:
            return False
        
        # Get secret key from settings
        vnpay_config = getattr(settings, 'VNPAY_CONFIG', {})
        hash_secret = vnpay_config.get('HASH_SECRET', '')
        if not hash_secret:
            import logging
            logging.getLogger(__name__).error("VNPAY_CONFIG['HASH_SECRET'] not configured")
            return False
        
        # Build data string (exclude vnp_SecureHash and vnp_SecureHashType)
        input_data = sorted([
            (k, v) for k, v in payload.items() 
            if k not in ('vnp_SecureHash', 'vnp_SecureHashType') and v
        ])
        query_string = urllib.parse.urlencode(input_data)
        
        # Calculate HMAC-SHA512
        calculated_hash = hmac.new(
            hash_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest().upper()
        
        return hmac.compare_digest(calculated_hash, received_hash.upper())
    
    def _verify_momo_signature(self, payload: dict) -> bool:
        """
        Verify MoMo HMAC-SHA256 signature.
        
        CRITICAL SECURITY: Prevents webhook forgery attacks.
        """
        import hashlib
        import hmac
        from django.conf import settings
        
        received_signature = payload.get('signature', '')
        if not received_signature:
            return False
        
        momo_config = getattr(settings, 'MOMO_CONFIG', {})
        secret_key = momo_config.get('SECRET_KEY', '')
        if not secret_key:
            import logging
            logging.getLogger(__name__).error("MOMO_CONFIG['SECRET_KEY'] not configured")
            return False
        
        # Build raw signature string per MoMo spec
        raw_signature = (
            f"accessKey={momo_config.get('ACCESS_KEY', '')}"
            f"&amount={payload.get('amount', '')}"
            f"&extraData={payload.get('extraData', '')}"
            f"&message={payload.get('message', '')}"
            f"&orderId={payload.get('orderId', '')}"
            f"&orderInfo={payload.get('orderInfo', '')}"
            f"&orderType={payload.get('orderType', '')}"
            f"&partnerCode={payload.get('partnerCode', '')}"
            f"&payType={payload.get('payType', '')}"
            f"&requestId={payload.get('requestId', '')}"
            f"&responseTime={payload.get('responseTime', '')}"
            f"&resultCode={payload.get('resultCode', '')}"
            f"&transId={payload.get('transId', '')}"
        )
        
        calculated_signature = hmac.new(
            secret_key.encode('utf-8'),
            raw_signature.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(calculated_signature, received_signature)
    
    def _verify_zalopay_signature(self, payload: dict) -> bool:
        """
        Verify ZaloPay HMAC-SHA256 MAC.
        
        CRITICAL SECURITY: Prevents webhook forgery attacks.
        """
        import hashlib
        import hmac
        from django.conf import settings
        
        received_mac = payload.get('mac', '')
        if not received_mac:
            return False
        
        zalopay_config = getattr(settings, 'ZALOPAY_CONFIG', {})
        key2 = zalopay_config.get('KEY2', '')
        if not key2:
            import logging
            logging.getLogger(__name__).error("ZALOPAY_CONFIG['KEY2'] not configured")
            return False
        
        # Build data string per ZaloPay spec
        data = payload.get('data', '')
        
        calculated_mac = hmac.new(
            key2.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(calculated_mac, received_mac)
    
    def _handle_vnpay_webhook(self, request, payload):
        """
        Handle VNPay IPN callback with signature verification and idempotency.
        
        Security measures:
        1. Verify HMAC-SHA512 signature to prevent forgery
        2. Check payment status to ensure idempotency
        3. Use select_for_update to prevent race conditions
        """
        import logging
        from django.conf import settings
        from django.db import transaction
        
        logger = logging.getLogger(__name__)
        
        # SECURITY: Verify signature FIRST before any processing
        if not self._verify_vnpay_signature(payload):
            logger.warning(f"VNPay webhook signature verification FAILED")
            return Response({'RspCode': '97', 'Message': 'Invalid Checksum'})
        
        # Get transaction reference
        txn_ref = payload.get('vnp_TxnRef')
        response_code = payload.get('vnp_ResponseCode')
        amount = payload.get('vnp_Amount')
        
        if not txn_ref:
            return Response({'RspCode': '99', 'Message': 'Invalid request'})
        
        try:
            # Use transaction and select_for_update to prevent race conditions
            with transaction.atomic():
                payment = Payment.objects.select_for_update().get(transaction_id=txn_ref)
                
                # IDEMPOTENCY: Check if payment already processed
                if payment.status in [Payment.Status.COMPLETED, Payment.Status.FAILED]:
                    logger.info(f"VNPay webhook ignored - payment {txn_ref} already {payment.status}")
                    return Response({'RspCode': '00', 'Message': 'Confirm Success'})
                
                # CURRENCY PRECISION: Use Decimal for amount comparison to avoid float errors
                # VNPay amount is in smallest unit (xu), payment.amount is in VND
                from decimal import Decimal, ROUND_DOWN
                expected_amount = int((payment.amount * Decimal('100')).quantize(Decimal('1'), rounding=ROUND_DOWN))
                received_amount = int(amount) if amount else 0
                if expected_amount != received_amount:
                    logger.warning(f"VNPay amount mismatch: expected {expected_amount}, got {received_amount}")
                    return Response({'RspCode': '04', 'Message': 'Invalid Amount'})
                
                if response_code == '00':  # Success
                    payment.status = Payment.Status.COMPLETED
                    # SECURITY: Sanitize sensitive fields before storing
                    payment.gateway_response = self._sanitize_payload(payload)
                    payment.paid_at = timezone.now()
                    payment.save()
                    
                    # Update order status
                    order = payment.order
                    order.payment_status = 'paid'
                    order.paid_at = timezone.now()
                    order.save()
                    order.update_status('confirmed', note='Payment received via VNPay')
                    
                    logger.info(f"VNPay payment successful: {txn_ref}")
                else:
                    payment.status = Payment.Status.FAILED
                    # SECURITY: Sanitize sensitive fields before storing
                    payment.gateway_response = self._sanitize_payload(payload)
                    payment.failure_reason = f"VNPay error: {response_code}"
                    payment.save()
                    
                    # Trigger stock restoration task (task handles its own idempotency)
                    from apps.business.commerce.orders.tasks import restore_stock_for_failed_payment_task
                    restore_stock_for_failed_payment_task.delay(str(payment.order_id))
                    
                    logger.warning(f"VNPay payment failed: {txn_ref}, code: {response_code}")
                
                return Response({'RspCode': '00', 'Message': 'Confirm Success'})
                
        except Payment.DoesNotExist:
            logger.error(f"Payment not found: {txn_ref}")
            return Response({'RspCode': '01', 'Message': 'Order not found'})
    
    def _handle_momo_webhook(self, request, payload):
        """
        Handle MoMo IPN callback with signature verification and idempotency.
        
        Security measures:
        1. Verify HMAC-SHA256 signature to prevent forgery
        2. Check payment status to ensure idempotency
        3. Use select_for_update to prevent race conditions
        """
        import logging
        from django.db import transaction
        
        logger = logging.getLogger(__name__)
        
        # SECURITY: Verify signature FIRST before any processing
        if not self._verify_momo_signature(payload):
            logger.warning(f"MoMo webhook signature verification FAILED")
            return Response({'status': 'invalid_signature'}, status=status.HTTP_400_BAD_REQUEST)
        
        order_id = payload.get('orderId')
        result_code = payload.get('resultCode')
        amount = payload.get('amount')
        
        if not order_id:
            return Response({'status': 'invalid_request'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Use transaction and select_for_update to prevent race conditions
            with transaction.atomic():
                payment = Payment.objects.select_for_update().get(transaction_id=order_id)
                
                # IDEMPOTENCY: Check if payment already processed
                if payment.status in [Payment.Status.COMPLETED, Payment.Status.FAILED]:
                    logger.info(f"MoMo webhook ignored - payment {order_id} already {payment.status}")
                    return Response({'status': 'received'})
                
                # Verify amount matches
                if amount and int(amount) != int(payment.amount):
                    logger.warning(f"MoMo amount mismatch: expected {payment.amount}, got {amount}")
                    return Response({'status': 'invalid_amount'}, status=status.HTTP_400_BAD_REQUEST)
                
                if result_code == 0:  # Success
                    payment.status = Payment.Status.COMPLETED
                    # SECURITY: Sanitize sensitive fields before storing
                    payment.gateway_response = self._sanitize_payload(payload)
                    payment.paid_at = timezone.now()
                    payment.save()
                    
                    # Update order
                    order = payment.order
                    order.payment_status = 'paid'
                    order.paid_at = timezone.now()
                    order.save()
                    order.update_status('confirmed', note='Payment received via MoMo')
                    
                    logger.info(f"MoMo payment successful: {order_id}")
                else:
                    payment.status = Payment.Status.FAILED
                    # SECURITY: Sanitize sensitive fields before storing
                    payment.gateway_response = self._sanitize_payload(payload)
                    payment.failure_reason = f"MoMo error: {result_code}"
                    payment.save()
                    
                    # Trigger stock restoration task
                    from apps.business.commerce.orders.tasks import restore_stock_for_failed_payment_task
                    restore_stock_for_failed_payment_task.delay(str(payment.order_id))
                    
                    logger.warning(f"MoMo payment failed: {order_id}, code: {result_code}")
                
        except Payment.DoesNotExist:
            logger.error(f"Payment not found: {order_id}")
        
        return Response({'status': 'received'})
    
    def _handle_zalopay_webhook(self, request, payload):
        """
        Handle ZaloPay callback with signature verification and idempotency.
        
        Security measures:
        1. Verify HMAC-SHA256 MAC to prevent forgery
        2. Check payment status to ensure idempotency
        3. Use select_for_update to prevent race conditions
        """
        import logging
        import json
        from django.db import transaction
        
        logger = logging.getLogger(__name__)
        
        # SECURITY: Verify MAC FIRST before any processing
        if not self._verify_zalopay_signature(payload):
            logger.warning(f"ZaloPay webhook MAC verification FAILED")
            return Response({'return_code': -1, 'return_message': 'mac not equal'})
        
        # ZaloPay sends data as JSON string in 'data' field
        data_str = payload.get('data', '{}')
        try:
            data = json.loads(data_str) if isinstance(data_str, str) else data_str
        except json.JSONDecodeError:
            data = {}
        
        app_trans_id = data.get('app_trans_id') or payload.get('app_trans_id')
        status_code = data.get('status') or payload.get('status')
        amount = data.get('amount') or payload.get('amount')
        
        if not app_trans_id:
            return Response({'return_code': -1, 'return_message': 'invalid request'})
        
        try:
            # Use transaction and select_for_update to prevent race conditions
            with transaction.atomic():
                payment = Payment.objects.select_for_update().get(transaction_id=app_trans_id)
                
                # IDEMPOTENCY: Check if payment already processed
                if payment.status in [Payment.Status.COMPLETED, Payment.Status.FAILED]:
                    logger.info(f"ZaloPay webhook ignored - payment {app_trans_id} already {payment.status}")
                    return Response({'return_code': 1, 'return_message': 'success'})
                
                # Verify amount matches
                if amount and int(amount) != int(payment.amount):
                    logger.warning(f"ZaloPay amount mismatch: expected {payment.amount}, got {amount}")
                    return Response({'return_code': -1, 'return_message': 'invalid amount'})
                
                if status_code == 1:  # Success
                    payment.status = Payment.Status.COMPLETED
                    # SECURITY: Sanitize sensitive fields before storing
                    payment.gateway_response = self._sanitize_payload(payload)
                    payment.paid_at = timezone.now()
                    payment.save()
                    
                    # Update order
                    order = payment.order
                    order.payment_status = 'paid'
                    order.paid_at = timezone.now()
                    order.save()
                    order.update_status('confirmed', note='Payment received via ZaloPay')
                    
                    logger.info(f"ZaloPay payment successful: {app_trans_id}")
                else:
                    payment.status = Payment.Status.FAILED
                    # SECURITY: Sanitize sensitive fields before storing
                    payment.gateway_response = self._sanitize_payload(payload)
                    payment.failure_reason = f"ZaloPay error: {status_code}"
                    payment.save()
                    
                    # Trigger stock restoration task
                    from apps.business.commerce.orders.tasks import restore_stock_for_failed_payment_task
                    restore_stock_for_failed_payment_task.delay(str(payment.order_id))
                    
                    logger.warning(f"ZaloPay payment failed: {app_trans_id}, code: {status_code}")
                
        except Payment.DoesNotExist:
            logger.error(f"Payment not found: {app_trans_id}")
        
        return Response({'return_code': 1, 'return_message': 'success'})

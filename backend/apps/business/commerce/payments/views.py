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
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            payment_method=payment_method,
            currency=order.currency,
            amount=order.total,
            fee=fee,
            net_amount=order.total - fee,
            ip_address=request.META.get('REMOTE_ADDR'),
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
    """Handle payment gateway webhooks."""
    
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # No auth for webhooks

    def post(self, request, gateway):
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Log webhook received
        logger.info(f"Webhook received from {gateway}: {request.data}")
        
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
    
    def _handle_vnpay_webhook(self, request, payload):
        """Handle VNPay IPN callback."""
        import logging
        from django.conf import settings
        
        logger = logging.getLogger(__name__)
        
        # Get transaction reference
        txn_ref = payload.get('vnp_TxnRef')
        response_code = payload.get('vnp_ResponseCode')
        amount = payload.get('vnp_Amount')
        
        if not txn_ref:
            return Response({'RspCode': '99', 'Message': 'Invalid request'})
        
        try:
            payment = Payment.objects.get(transaction_id=txn_ref)
            
            if response_code == '00':  # Success
                payment.status = Payment.Status.COMPLETED
                payment.gateway_response = payload
                payment.paid_at = timezone.now()
                payment.save()
                
                # Update order status
                order = payment.order
                order.payment_status = 'paid'
                order.paid_at = timezone.now()
                order.save()
                order.update_status('confirmed', note='Payment received via VNPay')
                
                logger.info(f"VNPay payment successful: {txn_ref}")
                return Response({'RspCode': '00', 'Message': 'Confirm Success'})
            else:
                payment.status = Payment.Status.FAILED
                payment.gateway_response = payload
                payment.failure_reason = f"VNPay error: {response_code}"
                payment.save()
                
                logger.warning(f"VNPay payment failed: {txn_ref}, code: {response_code}")
                return Response({'RspCode': '00', 'Message': 'Confirm Success'})
                
        except Payment.DoesNotExist:
            logger.error(f"Payment not found: {txn_ref}")
            return Response({'RspCode': '01', 'Message': 'Order not found'})
    
    def _handle_momo_webhook(self, request, payload):
        """Handle MoMo IPN callback."""
        import logging
        
        logger = logging.getLogger(__name__)
        
        order_id = payload.get('orderId')
        result_code = payload.get('resultCode')
        
        if not order_id:
            return Response({'status': 'invalid_request'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payment = Payment.objects.get(transaction_id=order_id)
            
            if result_code == 0:  # Success
                payment.status = Payment.Status.COMPLETED
                payment.gateway_response = payload
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
                payment.gateway_response = payload
                payment.failure_reason = f"MoMo error: {result_code}"
                payment.save()
                
                logger.warning(f"MoMo payment failed: {order_id}, code: {result_code}")
                
        except Payment.DoesNotExist:
            logger.error(f"Payment not found: {order_id}")
        
        return Response({'status': 'received'})
    
    def _handle_zalopay_webhook(self, request, payload):
        """Handle ZaloPay callback."""
        import logging
        
        logger = logging.getLogger(__name__)
        
        app_trans_id = payload.get('app_trans_id')
        status_code = payload.get('status')
        
        if not app_trans_id:
            return Response({'return_code': -1, 'return_message': 'invalid request'})
        
        try:
            payment = Payment.objects.get(transaction_id=app_trans_id)
            
            if status_code == 1:  # Success
                payment.status = Payment.Status.COMPLETED
                payment.gateway_response = payload
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
                payment.gateway_response = payload
                payment.failure_reason = f"ZaloPay error: {status_code}"
                payment.save()
                
                logger.warning(f"ZaloPay payment failed: {app_trans_id}, code: {status_code}")
                
        except Payment.DoesNotExist:
            logger.error(f"Payment not found: {app_trans_id}")
        
        return Response({'return_code': 1, 'return_message': 'success'})

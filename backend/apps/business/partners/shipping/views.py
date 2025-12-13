"""
Shipping Views for Owls E-commerce Platform
===========================================
"""

from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from decimal import Decimal
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import ShippingProvider, ShippingZone, ShippingRate
from .serializers import (
    ShippingProviderSerializer,
    ShippingZoneSerializer,
    ShippingRateSerializer,
    CalculateShippingSerializer,
    ShippingCalculationResultSerializer
)
from .services import ShippingService


@extend_schema(tags=['Shipping'])
class ShippingProvidersView(generics.ListAPIView):
    """List all active shipping providers."""
    
    serializer_class = ShippingProviderSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return ShippingProvider.objects.filter(
            is_active=True
        ).order_by('order', 'name')


@extend_schema(
    tags=['Shipping'],
    request=CalculateShippingSerializer,
    responses={
        200: ShippingCalculationResultSerializer,
        400: OpenApiResponse(description='Invalid input')
    }
)
class CalculateShippingView(APIView):
    """
    Calculate shipping rates for given destination.
    
    Accepts destination address info and package details,
    returns available shipping options with rates.
    """
    
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CalculateShippingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Build destination address
        to_address = {
            'province': data.get('province', ''),
            'province_code': data.get('province_code', ''),
            'district': data.get('district', ''),
            'district_id': data.get('district_id'),
            'ward': data.get('ward', ''),
            'ward_code': data.get('ward_code', '')
        }
        
        # Package info
        weight = data.get('weight', Decimal('0.5'))  # Default 500g
        total_value = data.get('total_value', Decimal('0'))
        
        dimensions = None
        if any([data.get('length'), data.get('width'), data.get('height')]):
            dimensions = {
                'length': data.get('length', Decimal('20')),
                'width': data.get('width', Decimal('15')),
                'height': data.get('height', Decimal('10'))
            }
        
        # Calculate shipping using service
        service = ShippingService()
        options = []
        
        # Get all active providers
        providers = ShippingProvider.objects.filter(is_active=True)
        
        for provider in providers:
            try:
                rate_result = service.calculate_shipping(
                    provider=provider,
                    to_address=to_address,
                    weight=weight,
                    order_value=total_value,
                    dimensions=dimensions
                )
                
                if rate_result:
                    # Check free shipping threshold
                    owls_config = getattr(settings, 'OWLS_CONFIG', {})
                    free_threshold = Decimal(str(owls_config.get('FREE_SHIPPING_THRESHOLD', 500000)))
                    
                    is_free = total_value >= free_threshold
                    original_rate = rate_result.get('rate', Decimal('0'))
                    final_rate = Decimal('0') if is_free else original_rate
                    
                    options.append({
                        'provider_code': provider.code,
                        'provider_name': provider.name,
                        'provider_logo': provider.logo.url if provider.logo else None,
                        'service_code': rate_result.get('service_code'),
                        'service_name': rate_result.get('service_name', 'Standard'),
                        'rate': final_rate,
                        'original_rate': original_rate if is_free else None,
                        'is_free': is_free,
                        'delivery_estimate': f"{provider.min_delivery_days}-{provider.max_delivery_days} ngày",
                        'min_delivery_days': provider.min_delivery_days,
                        'max_delivery_days': provider.max_delivery_days
                    })
                    
            except Exception as e:
                # Log error but continue with other providers
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to calculate shipping for {provider.code}: {e}")
                continue
        
        # Sort by rate
        options.sort(key=lambda x: x['rate'])
        
        # Find default option
        default_option = None
        if options:
            # Prefer default provider if available
            for opt in options:
                provider = providers.filter(code=opt['provider_code'], is_default=True).first()
                if provider:
                    default_option = opt
                    break
            
            if not default_option:
                default_option = options[0]  # Cheapest option
        
        # Calculate amount needed for free shipping
        owls_config = getattr(settings, 'OWLS_CONFIG', {})
        free_threshold = Decimal(str(owls_config.get('FREE_SHIPPING_THRESHOLD', 500000)))
        amount_for_free = None
        
        if total_value < free_threshold:
            amount_for_free = free_threshold - total_value
        
        return Response({
            'success': True,
            'data': {
                'options': options,
                'default_option': default_option,
                'free_shipping_threshold': str(free_threshold),
                'amount_for_free_shipping': str(amount_for_free) if amount_for_free else None
            }
        })


@extend_schema(
    tags=['Shipping'],
    responses={
        200: ShippingCalculationResultSerializer
    }
)
class CalculateCartShippingView(APIView):
    """
    Calculate shipping rates for user's cart.
    
    Uses cart items to determine weight and value,
    and user's default address for destination.
    """
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.business.commerce.cart.models import Cart
        from apps.base.core.users.models import UserAddress
        
        # Get user's cart
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': 'Cart not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        if cart.item_count == 0:
            return Response({
                'success': False,
                'error': {'message': 'Cart is empty'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user's default address
        address = UserAddress.objects.filter(
            user=request.user,
            is_default=True
        ).first()
        
        if not address:
            # Try any address
            address = UserAddress.objects.filter(user=request.user).first()
        
        if not address:
            return Response({
                'success': False,
                'error': {'message': 'No shipping address found. Please add an address.'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Build destination address
        to_address = {
            'province': address.province or '',
            'province_code': address.province_code or '',
            'district': address.district or '',
            'district_id': getattr(address, 'district_id', None),
            'ward': address.ward or '',
            'ward_code': getattr(address, 'ward_code', '')
        }
        
        # Calculate total weight from cart items
        total_weight = Decimal('0')
        for item in cart.items.select_related('product').all():
            product_weight = getattr(item.product, 'weight', None) or Decimal('0.3')
            total_weight += product_weight * item.quantity
        
        # Minimum weight 0.1 kg
        total_weight = max(total_weight, Decimal('0.1'))
        
        # Get cart value
        total_value = cart.subtotal
        
        # Calculate shipping using service
        service = ShippingService()
        options = []
        
        providers = ShippingProvider.objects.filter(is_active=True)
        
        for provider in providers:
            try:
                rate_result = service.calculate_shipping(
                    provider=provider,
                    to_address=to_address,
                    weight=total_weight,
                    order_value=total_value
                )
                
                if rate_result:
                    owls_config = getattr(settings, 'OWLS_CONFIG', {})
                    free_threshold = Decimal(str(owls_config.get('FREE_SHIPPING_THRESHOLD', 500000)))
                    
                    is_free = total_value >= free_threshold
                    original_rate = rate_result.get('rate', Decimal('0'))
                    final_rate = Decimal('0') if is_free else original_rate
                    
                    options.append({
                        'provider_code': provider.code,
                        'provider_name': provider.name,
                        'provider_logo': provider.logo.url if provider.logo else None,
                        'service_code': rate_result.get('service_code'),
                        'service_name': rate_result.get('service_name', 'Standard'),
                        'rate': final_rate,
                        'original_rate': original_rate if is_free else None,
                        'is_free': is_free,
                        'delivery_estimate': f"{provider.min_delivery_days}-{provider.max_delivery_days} ngày",
                        'min_delivery_days': provider.min_delivery_days,
                        'max_delivery_days': provider.max_delivery_days
                    })
                    
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to calculate shipping for {provider.code}: {e}")
                continue
        
        options.sort(key=lambda x: x['rate'])
        
        default_option = None
        if options:
            for opt in options:
                provider = providers.filter(code=opt['provider_code'], is_default=True).first()
                if provider:
                    default_option = opt
                    break
            if not default_option:
                default_option = options[0]
        
        owls_config = getattr(settings, 'OWLS_CONFIG', {})
        free_threshold = Decimal(str(owls_config.get('FREE_SHIPPING_THRESHOLD', 500000)))
        amount_for_free = None
        
        if total_value < free_threshold:
            amount_for_free = free_threshold - total_value
        
        return Response({
            'success': True,
            'data': {
                'options': options,
                'default_option': default_option,
                'free_shipping_threshold': str(free_threshold),
                'amount_for_free_shipping': str(amount_for_free) if amount_for_free else None,
                'shipping_address': {
                    'id': str(address.id),
                    'full_address': str(address)
                },
                'package_info': {
                    'total_weight_kg': str(total_weight),
                    'item_count': cart.item_count,
                    'subtotal': str(total_value)
                }
            }
        })


@extend_schema(tags=['Shipping'])
class ShippingZonesView(generics.ListAPIView):
    """List all shipping zones."""
    
    serializer_class = ShippingZoneSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return ShippingZone.objects.filter(is_active=True).order_by('name')


@extend_schema(tags=['Shipping'])
class ShippingRatesView(generics.ListAPIView):
    """
    List shipping rates.
    
    Can filter by provider or zone.
    """
    
    serializer_class = ShippingRateSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = ShippingRate.objects.filter(
            is_active=True
        ).select_related('provider', 'zone')
        
        provider_id = self.request.query_params.get('provider')
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
        
        zone_id = self.request.query_params.get('zone')
        if zone_id:
            queryset = queryset.filter(zone_id=zone_id)
        
        return queryset.order_by('base_rate')

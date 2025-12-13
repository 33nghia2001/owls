"""
Shipping Service for Owls E-commerce Platform
==============================================
Shipping rate calculation with API integration (GHN, GHTK).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, Dict, Any, List
from django.conf import settings
import logging
import requests

if TYPE_CHECKING:
    from .models import ShippingProvider, ShippingRate
    from apps.base.core.users.models import UserAddress

logger = logging.getLogger(__name__)


class ShippingCalculationError(Exception):
    """Exception raised when shipping calculation fails."""
    pass


# =============================================================================
# SHIPPING PROVIDER ADAPTERS
# =============================================================================

class ShippingProviderAdapter(ABC):
    """Abstract base class for shipping provider adapters."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    @abstractmethod
    def calculate_rate(
        self,
        from_address: Dict[str, Any],
        to_address: Dict[str, Any],
        weight: Decimal,
        dimensions: Dict[str, Decimal] = None,
        service_code: str = None
    ) -> Dict[str, Any]:
        """
        Calculate shipping rate from provider API.
        
        Args:
            from_address: Sender address
            to_address: Recipient address
            weight: Package weight in grams
            dimensions: Package dimensions (length, width, height in cm)
            service_code: Optional service code
            
        Returns:
            dict with rate info
        """
        pass
    
    @abstractmethod
    def get_available_services(
        self,
        from_address: Dict[str, Any],
        to_address: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get available shipping services for route."""
        pass


class GHNAdapter(ShippingProviderAdapter):
    """Giao Hàng Nhanh (GHN) shipping adapter."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.token = self.config.get('token') or settings.GHN_CONFIG.get('TOKEN', '')
        self.shop_id = self.config.get('shop_id') or settings.GHN_CONFIG.get('SHOP_ID', '')
        self.base_url = self.config.get('base_url') or 'https://online-gateway.ghn.vn/shiip/public-api'
    
    def _request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make request to GHN API."""
        headers = {
            'Content-Type': 'application/json',
            'Token': self.token,
            'ShopId': str(self.shop_id)
        }
        
        try:
            response = requests.post(
                f'{self.base_url}{endpoint}',
                json=data,
                headers=headers,
                timeout=30
            )
            result = response.json()
            
            if result.get('code') != 200:
                raise ShippingCalculationError(
                    result.get('message', 'GHN API error')
                )
            
            return result.get('data', {})
            
        except requests.RequestException as e:
            raise ShippingCalculationError(f'GHN API connection error: {e}')
    
    def calculate_rate(
        self,
        from_address: Dict[str, Any],
        to_address: Dict[str, Any],
        weight: Decimal,
        dimensions: Dict[str, Decimal] = None,
        service_code: str = None
    ) -> Dict[str, Any]:
        """Calculate GHN shipping rate."""
        
        # Convert weight to grams
        weight_grams = int(weight * 1000)
        
        data = {
            'from_district_id': from_address.get('district_id'),
            'from_ward_code': from_address.get('ward_code'),
            'service_id': int(service_code) if service_code else None,
            'service_type_id': 2,  # Standard delivery
            'to_district_id': to_address.get('district_id'),
            'to_ward_code': to_address.get('ward_code'),
            'weight': weight_grams,
            'length': int(dimensions.get('length', 20)) if dimensions else 20,
            'width': int(dimensions.get('width', 15)) if dimensions else 15,
            'height': int(dimensions.get('height', 10)) if dimensions else 10,
            'insurance_value': 0,
        }
        
        result = self._request('/v2/shipping-order/fee', data)
        
        return {
            'provider': 'ghn',
            'service_code': service_code,
            'total_fee': Decimal(str(result.get('total', 0))),
            'service_fee': Decimal(str(result.get('service_fee', 0))),
            'insurance_fee': Decimal(str(result.get('insurance_fee', 0))),
            'delivery_time': result.get('expected_delivery_time'),
            'raw_response': result
        }
    
    def get_available_services(
        self,
        from_address: Dict[str, Any],
        to_address: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get available GHN services."""
        
        data = {
            'shop_id': int(self.shop_id),
            'from_district': from_address.get('district_id'),
            'to_district': to_address.get('district_id')
        }
        
        result = self._request('/v2/shipping-order/available-services', data)
        
        services = []
        for service in result if isinstance(result, list) else []:
            services.append({
                'code': str(service.get('service_id')),
                'name': service.get('short_name'),
                'description': service.get('service_type_id')
            })
        
        return services


class GHTKAdapter(ShippingProviderAdapter):
    """Giao Hàng Tiết Kiệm (GHTK) shipping adapter."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.token = self.config.get('token') or settings.GHTK_CONFIG.get('TOKEN', '')
        self.base_url = self.config.get('base_url') or 'https://services.giaohangtietkiem.vn'
    
    def _request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make request to GHTK API."""
        headers = {
            'Content-Type': 'application/json',
            'Token': self.token
        }
        
        try:
            response = requests.post(
                f'{self.base_url}{endpoint}',
                json=data,
                headers=headers,
                timeout=30
            )
            result = response.json()
            
            if not result.get('success'):
                raise ShippingCalculationError(
                    result.get('message', 'GHTK API error')
                )
            
            return result.get('fee', {})
            
        except requests.RequestException as e:
            raise ShippingCalculationError(f'GHTK API connection error: {e}')
    
    def calculate_rate(
        self,
        from_address: Dict[str, Any],
        to_address: Dict[str, Any],
        weight: Decimal,
        dimensions: Dict[str, Decimal] = None,
        service_code: str = None
    ) -> Dict[str, Any]:
        """Calculate GHTK shipping rate."""
        
        # Convert weight to grams
        weight_grams = int(weight * 1000)
        
        data = {
            'pick_province': from_address.get('province'),
            'pick_district': from_address.get('district'),
            'province': to_address.get('province'),
            'district': to_address.get('district'),
            'address': to_address.get('address', ''),
            'weight': weight_grams,
            'value': 0,
            'transport': 'road' if service_code == 'road' else 'fly',
            'deliver_option': 'none'
        }
        
        result = self._request('/services/shipment/fee', data)
        
        return {
            'provider': 'ghtk',
            'service_code': service_code or 'road',
            'total_fee': Decimal(str(result.get('fee', 0))),
            'insurance_fee': Decimal(str(result.get('insurance_fee', 0))),
            'delivery_time': result.get('delivery_time'),
            'raw_response': result
        }
    
    def get_available_services(
        self,
        from_address: Dict[str, Any],
        to_address: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get available GHTK services."""
        return [
            {'code': 'road', 'name': 'Đường bộ', 'description': 'Giao hàng đường bộ'},
            {'code': 'fly', 'name': 'Bay', 'description': 'Giao hàng máy bay (nhanh hơn)'},
        ]


class ManualAdapter(ShippingProviderAdapter):
    """Manual shipping rate adapter (uses database rates)."""
    
    def calculate_rate(
        self,
        from_address: Dict[str, Any],
        to_address: Dict[str, Any],
        weight: Decimal,
        dimensions: Dict[str, Decimal] = None,
        service_code: str = None
    ) -> Dict[str, Any]:
        """Calculate rate from database."""
        from .models import ShippingRate, ShippingZone
        
        # Find zone for destination
        province_code = to_address.get('province_code')
        
        zone = ShippingZone.objects.filter(
            is_active=True,
            provinces__contains=[province_code]
        ).first()
        
        if not zone:
            # Use default zone or raise error
            zone = ShippingZone.objects.filter(
                is_active=True,
                name__icontains='Mặc định'
            ).first()
        
        if not zone:
            raise ShippingCalculationError('Không tìm thấy vùng vận chuyển phù hợp')
        
        # Find rate for weight
        rate = ShippingRate.objects.filter(
            zone=zone,
            is_active=True,
            min_weight__lte=weight
        ).filter(
            models.Q(max_weight__isnull=True) | models.Q(max_weight__gte=weight)
        ).first()
        
        if not rate:
            raise ShippingCalculationError('Không tìm thấy phí vận chuyển phù hợp')
        
        total_fee = rate.calculate_rate(weight, Decimal('0'))
        
        return {
            'provider': 'manual',
            'service_code': 'standard',
            'total_fee': total_fee,
            'zone_name': zone.name,
            'rate_name': rate.name
        }
    
    def get_available_services(
        self,
        from_address: Dict[str, Any],
        to_address: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get manual services."""
        return [
            {'code': 'standard', 'name': 'Tiêu chuẩn', 'description': 'Giao hàng tiêu chuẩn'},
        ]


# Import models
from django.db import models


# =============================================================================
# SHIPPING PROVIDER FACTORY
# =============================================================================

class ShippingProviderFactory:
    """Factory for creating shipping provider adapters."""
    
    _adapters = {
        'ghn': GHNAdapter,
        'ghtk': GHTKAdapter,
        'manual': ManualAdapter,
    }
    
    @classmethod
    def create(cls, provider_type: str, config: Dict[str, Any] = None) -> ShippingProviderAdapter:
        """Create adapter for provider type."""
        adapter_class = cls._adapters.get(provider_type)
        
        if not adapter_class:
            # Default to manual
            adapter_class = ManualAdapter
        
        return adapter_class(config)


# =============================================================================
# SHIPPING SERVICE
# =============================================================================

class ShippingService:
    """
    Main shipping service for rate calculation.
    Orchestrates provider adapters and fallback logic.
    """
    
    @classmethod
    def calculate_shipping(
        cls,
        cart_or_order,
        shipping_address: 'UserAddress',
        provider_code: str = None
    ) -> Dict[str, Any]:
        """
        Calculate shipping cost for cart or order.
        
        Args:
            cart_or_order: Cart or Order instance
            shipping_address: Destination address
            provider_code: Optional specific provider
            
        Returns:
            dict with shipping options and costs
        """
        from .models import ShippingProvider
        
        # Calculate total weight from items
        total_weight = cls._calculate_weight(cart_or_order)
        
        # Get store address (from settings or first warehouse)
        from_address = cls._get_store_address()
        
        # Convert shipping address to dict
        to_address = {
            'province': shipping_address.city,
            'province_code': getattr(shipping_address, 'province_code', None),
            'district': getattr(shipping_address, 'district', ''),
            'district_id': getattr(shipping_address, 'district_id', None),
            'ward_code': getattr(shipping_address, 'ward_code', None),
            'address': shipping_address.full_address,
        }
        
        # Get providers to try
        if provider_code:
            providers = ShippingProvider.objects.filter(
                code=provider_code,
                is_active=True
            )
        else:
            providers = ShippingProvider.objects.filter(is_active=True).order_by('order')
        
        results = []
        
        for provider in providers:
            try:
                adapter = ShippingProviderFactory.create(
                    provider.provider_type,
                    provider.api_config
                )
                
                # Get available services
                services = adapter.get_available_services(from_address, to_address)
                
                for service in services:
                    try:
                        rate_result = adapter.calculate_rate(
                            from_address=from_address,
                            to_address=to_address,
                            weight=total_weight,
                            service_code=service.get('code')
                        )
                        
                        # Apply free shipping threshold from settings
                        order_value = getattr(cart_or_order, 'subtotal', Decimal('0'))
                        free_threshold = Decimal(str(
                            settings.OWLS_CONFIG.get('FREE_SHIPPING_THRESHOLD', 500000)
                        ))
                        
                        if order_value >= free_threshold:
                            rate_result['total_fee'] = Decimal('0')
                            rate_result['free_shipping_applied'] = True
                        
                        results.append({
                            'provider_id': str(provider.id),
                            'provider_code': provider.code,
                            'provider_name': provider.name,
                            'service_code': service.get('code'),
                            'service_name': service.get('name'),
                            'total_fee': float(rate_result.get('total_fee', 0)),
                            'delivery_days': f"{provider.min_delivery_days}-{provider.max_delivery_days}",
                            'free_shipping_applied': rate_result.get('free_shipping_applied', False)
                        })
                        
                    except ShippingCalculationError as e:
                        logger.warning(f"Service {service.get('code')} rate error: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Provider {provider.code} error: {e}")
                continue
        
        if not results:
            # Fallback to flat rate from settings
            flat_rate = Decimal(str(settings.OWLS_CONFIG.get('DEFAULT_SHIPPING_RATE', 30000)))
            order_value = getattr(cart_or_order, 'subtotal', Decimal('0'))
            free_threshold = Decimal(str(settings.OWLS_CONFIG.get('FREE_SHIPPING_THRESHOLD', 500000)))
            
            if order_value >= free_threshold:
                flat_rate = Decimal('0')
            
            results.append({
                'provider_code': 'default',
                'provider_name': 'Giao hàng tiêu chuẩn',
                'service_code': 'standard',
                'service_name': 'Tiêu chuẩn',
                'total_fee': float(flat_rate),
                'delivery_days': '3-5',
                'free_shipping_applied': flat_rate == 0
            })
        
        return {
            'success': True,
            'weight_kg': float(total_weight),
            'options': results
        }
    
    @classmethod
    def _calculate_weight(cls, cart_or_order) -> Decimal:
        """Calculate total weight from items."""
        total_weight = Decimal('0')
        
        items = getattr(cart_or_order, 'items', None)
        if items:
            for item in items.select_related('product'):
                product = item.product
                weight = getattr(product, 'weight', None) or Decimal('0.5')
                total_weight += weight * item.quantity
        
        # Minimum weight
        if total_weight < Decimal('0.1'):
            total_weight = Decimal('0.5')
        
        return total_weight
    
    @classmethod
    def _get_store_address(cls) -> Dict[str, Any]:
        """Get store/warehouse address from settings."""
        return {
            'province': settings.OWLS_CONFIG.get('STORE_PROVINCE', 'Hồ Chí Minh'),
            'province_code': settings.OWLS_CONFIG.get('STORE_PROVINCE_CODE', '79'),
            'district': settings.OWLS_CONFIG.get('STORE_DISTRICT', 'Quận 1'),
            'district_id': settings.OWLS_CONFIG.get('STORE_DISTRICT_ID', 1442),
            'ward_code': settings.OWLS_CONFIG.get('STORE_WARD_CODE', '21012'),
        }

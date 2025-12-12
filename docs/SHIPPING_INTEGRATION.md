# Shipping API Integration Guide

## Tổng quan

Hệ thống hiện tại đang sử dụng logic tính phí ship đơn giản dựa trên công thức:
```
shipping_cost = base_cost + (weight_kg * cost_per_kg)
```

Để vận hành production với multi-vendor marketplace, cần tích hợp API vận chuyển thực tế từ các đơn vị như:
- **GHN (Giao Hàng Nhanh)**: https://api.ghn.vn/
- **GHTK (Giao Hàng Tiết Kiệm)**: https://docs.giaohangtietkiem.vn/
- **Viettel Post**: https://viettelpost.vn/

## Architecture cho Multi-vendor Shipping

### 1. Model Structure (Đã implement)

```
Order (Đơn hàng tổng)
  └── SubOrder (Đơn hàng con - mỗi vendor)
        ├── vendor: Vendor
        ├── shipping_cost: Phí ship riêng
        ├── tracking_number: Mã vận đơn
        └── carrier_name: Đơn vị vận chuyển
```

### 2. Flow tính phí ship cho Multi-vendor

```
1. Customer chọn sản phẩm từ nhiều shop
2. System group items theo Vendor
3. Với mỗi Vendor:
   - Lấy địa chỉ kho của Vendor
   - Lấy địa chỉ giao hàng của Customer
   - Gọi API shipping để tính phí
4. Tổng phí ship = Σ (phí ship mỗi SubOrder)
```

## Integration Code Example

### apps/shipping/services.py

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from decimal import Decimal
import requests
from django.conf import settings
from django.core.cache import cache


class ShippingProvider(ABC):
    """Abstract base class for shipping providers."""
    
    @abstractmethod
    def calculate_fee(
        self,
        from_province: str,
        from_district: str,
        to_province: str,
        to_district: str,
        weight: int,  # grams
        service_type: str = 'standard'
    ) -> Dict[str, Any]:
        """Calculate shipping fee."""
        pass
    
    @abstractmethod
    def create_order(self, order_data: Dict) -> Dict[str, Any]:
        """Create shipping order and get tracking number."""
        pass
    
    @abstractmethod
    def get_tracking(self, tracking_number: str) -> Dict[str, Any]:
        """Get tracking information."""
        pass


class GHNProvider(ShippingProvider):
    """Giao Hàng Nhanh integration."""
    
    BASE_URL = "https://online-gateway.ghn.vn/shiip/public-api"
    
    def __init__(self):
        self.token = settings.GHN_TOKEN
        self.shop_id = settings.GHN_SHOP_ID
    
    def _headers(self):
        return {
            "Token": self.token,
            "ShopId": str(self.shop_id),
            "Content-Type": "application/json"
        }
    
    def calculate_fee(
        self,
        from_district_id: int,
        from_ward_code: str,
        to_district_id: int,
        to_ward_code: str,
        weight: int,
        service_type_id: int = 2  # 2 = standard, 1 = express
    ) -> Dict[str, Any]:
        """
        Calculate shipping fee using GHN API.
        
        API Docs: https://api.ghn.vn/home/docs/detail?id=76
        """
        cache_key = f"ghn_fee:{from_district_id}:{to_district_id}:{weight}:{service_type_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        url = f"{self.BASE_URL}/v2/shipping-order/fee"
        payload = {
            "from_district_id": from_district_id,
            "from_ward_code": from_ward_code,
            "to_district_id": to_district_id,
            "to_ward_code": to_ward_code,
            "weight": weight,
            "service_type_id": service_type_id,
            "insurance_value": 0,  # Có thể thêm giá trị bảo hiểm
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._headers(), timeout=10)
            data = response.json()
            
            if data.get("code") == 200:
                result = {
                    "success": True,
                    "total_fee": data["data"]["total"],
                    "service_fee": data["data"]["service_fee"],
                    "insurance_fee": data["data"]["insurance_fee"],
                    "expected_delivery": data["data"].get("expected_delivery_time"),
                }
                cache.set(cache_key, result, timeout=3600)  # Cache 1 hour
                return result
            else:
                return {"success": False, "error": data.get("message")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_order(self, order_data: Dict) -> Dict[str, Any]:
        """
        Create shipping order.
        
        API Docs: https://api.ghn.vn/home/docs/detail?id=122
        """
        url = f"{self.BASE_URL}/v2/shipping-order/create"
        
        payload = {
            "to_name": order_data["recipient_name"],
            "to_phone": order_data["recipient_phone"],
            "to_address": order_data["to_address"],
            "to_ward_code": order_data["to_ward_code"],
            "to_district_id": order_data["to_district_id"],
            "weight": order_data["weight"],
            "length": order_data.get("length", 20),
            "width": order_data.get("width", 20),
            "height": order_data.get("height", 10),
            "service_type_id": order_data.get("service_type_id", 2),
            "payment_type_id": 2,  # 1 = seller pays, 2 = buyer pays
            "required_note": "KHONGCHOXEMHANG",  # CHOTHUHANG, CHOXEMHANGKHONGTHU, KHONGCHOXEMHANG
            "items": order_data["items"],
            "cod_amount": order_data.get("cod_amount", 0),
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._headers(), timeout=30)
            data = response.json()
            
            if data.get("code") == 200:
                return {
                    "success": True,
                    "order_code": data["data"]["order_code"],
                    "expected_delivery": data["data"].get("expected_delivery_time"),
                    "total_fee": data["data"]["total_fee"],
                }
            else:
                return {"success": False, "error": data.get("message")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_tracking(self, order_code: str) -> Dict[str, Any]:
        """
        Get order tracking info.
        
        API Docs: https://api.ghn.vn/home/docs/detail?id=66
        """
        url = f"{self.BASE_URL}/v2/shipping-order/detail"
        payload = {"order_code": order_code}
        
        try:
            response = requests.post(url, json=payload, headers=self._headers(), timeout=10)
            data = response.json()
            
            if data.get("code") == 200:
                return {
                    "success": True,
                    "status": data["data"]["status"],
                    "log": data["data"].get("log", []),
                }
            else:
                return {"success": False, "error": data.get("message")}
        except Exception as e:
            return {"success": False, "error": str(e)}


class GHTKProvider(ShippingProvider):
    """Giao Hàng Tiết Kiệm integration."""
    
    BASE_URL = "https://services.giaohangtietkiem.vn"
    
    def __init__(self):
        self.token = settings.GHTK_TOKEN
    
    def _headers(self):
        return {
            "Token": self.token,
            "Content-Type": "application/json"
        }
    
    def calculate_fee(
        self,
        pick_province: str,
        pick_district: str,
        province: str,
        district: str,
        weight: int,  # grams
        deliver_option: str = "none"  # "xteam" for express
    ) -> Dict[str, Any]:
        """
        Calculate shipping fee using GHTK API.
        
        API Docs: https://docs.giaohangtietkiem.vn/#phi-van-chuyen
        """
        url = f"{self.BASE_URL}/services/shipment/fee"
        params = {
            "pick_province": pick_province,
            "pick_district": pick_district,
            "province": province,
            "district": district,
            "weight": weight,
            "deliver_option": deliver_option,
        }
        
        try:
            response = requests.get(url, params=params, headers=self._headers(), timeout=10)
            data = response.json()
            
            if data.get("success"):
                return {
                    "success": True,
                    "total_fee": data["fee"]["fee"],
                    "delivery_time": data["fee"].get("delivery_time"),
                }
            else:
                return {"success": False, "error": data.get("message")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_order(self, order_data: Dict) -> Dict[str, Any]:
        """Create GHTK shipping order."""
        url = f"{self.BASE_URL}/services/shipment/order"
        
        payload = {
            "products": order_data["products"],
            "order": {
                "id": order_data["order_id"],
                "pick_name": order_data["pick_name"],
                "pick_address": order_data["pick_address"],
                "pick_province": order_data["pick_province"],
                "pick_district": order_data["pick_district"],
                "pick_tel": order_data["pick_tel"],
                "name": order_data["recipient_name"],
                "address": order_data["to_address"],
                "province": order_data["to_province"],
                "district": order_data["to_district"],
                "tel": order_data["recipient_phone"],
                "weight": order_data["weight"],
                "pick_money": order_data.get("cod_amount", 0),
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._headers(), timeout=30)
            data = response.json()
            
            if data.get("success"):
                return {
                    "success": True,
                    "tracking_id": data["order"]["tracking_id"],
                    "label": data["order"].get("label"),
                    "fee": data["order"]["fee"],
                }
            else:
                return {"success": False, "error": data.get("message")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_tracking(self, tracking_id: str) -> Dict[str, Any]:
        """Get GHTK tracking info."""
        url = f"{self.BASE_URL}/services/shipment/v2/{tracking_id}"
        
        try:
            response = requests.get(url, headers=self._headers(), timeout=10)
            data = response.json()
            
            if data.get("success"):
                return {
                    "success": True,
                    "status": data["order"]["status"],
                    "status_text": data["order"]["status_text"],
                }
            else:
                return {"success": False, "error": data.get("message")}
        except Exception as e:
            return {"success": False, "error": str(e)}


class ShippingService:
    """
    Main shipping service that coordinates between providers.
    """
    
    def __init__(self):
        self.providers = {
            "ghn": GHNProvider(),
            "ghtk": GHTKProvider(),
        }
        self.default_provider = "ghn"
    
    def calculate_fee_for_sub_order(self, sub_order) -> Decimal:
        """
        Calculate shipping fee for a sub-order based on vendor location.
        
        Args:
            sub_order: SubOrder instance
            
        Returns:
            Decimal: Shipping fee in VND
        """
        vendor = sub_order.vendor
        order = sub_order.order
        
        # Get vendor warehouse location
        from_province = vendor.province or "Hồ Chí Minh"
        from_district = vendor.district or "Quận 1"
        
        # Get customer delivery location
        to_province = order.shipping_province
        to_ward = order.shipping_ward
        
        # Calculate total weight from items
        total_weight = sum(
            (item.product.weight or 500) * item.quantity  # Default 500g
            for item in order.items.filter(vendor=vendor)
        )
        
        # Try each provider until one succeeds
        for provider_name, provider in self.providers.items():
            try:
                result = provider.calculate_fee(
                    from_province=from_province,
                    from_district=from_district,
                    to_province=to_province,
                    to_district=to_ward,  # Using ward as district for now
                    weight=total_weight
                )
                
                if result.get("success"):
                    return Decimal(str(result["total_fee"]))
            except Exception:
                continue
        
        # Fallback to default calculation
        return self._fallback_fee(to_province, total_weight)
    
    def _fallback_fee(self, province: str, weight: int) -> Decimal:
        """
        Fallback shipping fee calculation when API is unavailable.
        """
        # Major cities get lower rate
        major_cities = ["Hồ Chí Minh", "Hà Nội", "Đà Nẵng"]
        
        base_fee = Decimal("20000") if province in major_cities else Decimal("30000")
        weight_fee = Decimal(str(weight / 1000)) * Decimal("5000")  # 5000đ/kg
        
        return base_fee + weight_fee
    
    def calculate_total_shipping(self, order) -> Decimal:
        """
        Calculate total shipping cost for an order with multiple vendors.
        
        Returns sum of shipping fees from all sub-orders.
        """
        total = Decimal("0")
        
        for sub_order in order.sub_orders.all():
            fee = self.calculate_fee_for_sub_order(sub_order)
            sub_order.shipping_cost = fee
            sub_order.save(update_fields=['shipping_cost', 'total'])
            total += fee
        
        return total


# Singleton instance
shipping_service = ShippingService()
```

## Environment Variables

Thêm vào `.env`:

```bash
# GHN (Giao Hàng Nhanh)
GHN_TOKEN=your_ghn_api_token
GHN_SHOP_ID=your_shop_id

# GHTK (Giao Hàng Tiết Kiệm)
GHTK_TOKEN=your_ghtk_api_token
```

Thêm vào `settings.py`:

```python
# Shipping Provider Config
GHN_TOKEN = os.environ.get('GHN_TOKEN', '')
GHN_SHOP_ID = os.environ.get('GHN_SHOP_ID', '')
GHTK_TOKEN = os.environ.get('GHTK_TOKEN', '')
```

## API Endpoints cần thêm

### 1. Calculate Shipping Fee (Preview)

```
POST /api/v1/shipping/calculate/
{
    "items": [
        {"product_id": "...", "quantity": 2},
        {"product_id": "...", "quantity": 1}
    ],
    "to_province": "Hà Nội",
    "to_district": "Quận Cầu Giấy",
    "to_ward": "Phường Dịch Vọng"
}

Response:
{
    "shipping_fees": [
        {
            "vendor": "Shop ABC",
            "vendor_id": "...",
            "fee": 35000,
            "carrier": "GHN",
            "estimated_days": "2-3"
        },
        {
            "vendor": "Shop XYZ", 
            "vendor_id": "...",
            "fee": 42000,
            "carrier": "GHTK",
            "estimated_days": "3-4"
        }
    ],
    "total_shipping": 77000
}
```

### 2. Create Shipping Order (After order confirmed)

```
POST /api/v1/orders/{order_id}/create-shipment/
POST /api/v1/sub-orders/{sub_order_id}/create-shipment/
```

### 3. Track Shipment

```
GET /api/v1/sub-orders/{sub_order_id}/tracking/
```

## Frontend Changes

### Checkout Page

1. Gọi `/shipping/calculate/` khi user nhập địa chỉ
2. Hiển thị phí ship theo từng vendor
3. Cho phép chọn carrier khác nhau cho mỗi vendor (optional)

### Order Detail Page

1. Hiển thị từng SubOrder riêng biệt
2. Mỗi SubOrder có tracking number riêng
3. Status badge riêng cho mỗi vendor

## Migration Steps

1. Chạy `python manage.py makemigrations orders`
2. Chạy `python manage.py migrate`
3. Update frontend để handle sub_orders trong API response
4. Đăng ký tài khoản GHN/GHTK và lấy API token
5. Test integration với sandbox environment trước production

## Notes

- GHN yêu cầu đăng ký Shop ID riêng cho từng Vendor (nếu muốn ship trực tiếp từ kho Vendor)
- Có thể sử dụng mô hình Hub: Tất cả hàng gửi về kho trung tâm trước khi ship cho khách
- Cân nhắc caching kết quả tính phí ship (1 hour) để giảm số lượng API calls

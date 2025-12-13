"""
Vendor Views for Owls E-commerce Platform
=========================================
"""

from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.text import slugify
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Vendor, VendorDocument, VendorBankAccount
from .serializers import (
    VendorListSerializer, VendorDetailSerializer, VendorProfileSerializer,
    VendorRegistrationSerializer, VendorDocumentSerializer,
    VendorBankAccountSerializer
)


class IsVendorOwner(permissions.BasePermission):
    """Permission for vendor owner only."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'vendor_profile')

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


@extend_schema(tags=['Vendors'])
class VendorListView(generics.ListAPIView):
    """List approved vendors (public)."""
    
    serializer_class = VendorListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Vendor.objects.filter(
            status=Vendor.Status.APPROVED,
            is_active=True
        ).order_by('-rating')


@extend_schema(tags=['Vendors'])
class VendorDetailView(generics.RetrieveAPIView):
    """Get vendor details (public)."""
    
    serializer_class = VendorDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return Vendor.objects.filter(
            status=Vendor.Status.APPROVED,
            is_active=True
        )


@extend_schema(
    tags=['Vendors'],
    request=VendorRegistrationSerializer,
    responses={
        201: VendorProfileSerializer,
        400: OpenApiResponse(description='Already registered as vendor')
    }
)
class VendorRegisterView(APIView):
    """Register as a vendor."""
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if hasattr(request.user, 'vendor_profile'):
            return Response({
                'success': False,
                'error': {'message': 'You are already registered as a vendor'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = VendorRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        vendor = serializer.save(
            owner=request.user,
            slug=slugify(serializer.validated_data['store_name']),
            status=Vendor.Status.PENDING
        )
        
        request.user.role = 'vendor'
        request.user.save(update_fields=['role'])
        
        return Response({
            'success': True,
            'message': 'Vendor registration submitted for approval',
            'data': VendorProfileSerializer(vendor).data
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Vendors'])
class VendorProfileView(generics.RetrieveUpdateAPIView):
    """Vendor profile management."""
    
    serializer_class = VendorProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendorOwner]

    def get_object(self):
        if getattr(self, 'swagger_fake_view', False):
            return None
        return self.request.user.vendor_profile


@extend_schema(
    tags=['Vendors'],
    responses={200: OpenApiResponse(description='Vendor dashboard statistics')}
)
class VendorDashboardView(APIView):
    """Vendor dashboard with statistics."""
    
    permission_classes = [permissions.IsAuthenticated, IsVendorOwner]

    def get(self, request):
        vendor = request.user.vendor_profile
        
        from apps.business.commerce.orders.models import OrderItem
        from apps.business.commerce.products.models import Product
        
        pending_orders = OrderItem.objects.filter(
            vendor=vendor,
            status='pending'
        ).count()
        
        recent_orders = OrderItem.objects.filter(
            vendor=vendor
        ).select_related('order').order_by('-created_at')[:10]
        
        top_products = Product.objects.filter(
            vendor=vendor,
            is_active=True
        ).order_by('-sold_count')[:5]
        
        data = {
            'total_products': vendor.total_products,
            'total_orders': vendor.total_orders,
            'total_sales': str(vendor.total_sales),
            'pending_orders': pending_orders,
            'rating': str(vendor.rating),
            'total_reviews': vendor.total_reviews,
            'recent_orders': [
                {
                    'id': str(item.order.id),
                    'order_number': item.order.order_number,
                    'product_name': item.product_name,
                    'quantity': item.quantity,
                    'total': str(item.total_price),
                    'status': item.status,
                    'created_at': item.created_at
                }
                for item in recent_orders
            ],
            'top_products': [
                {
                    'id': str(p.id),
                    'name': p.name,
                    'sold_count': p.sold_count,
                    'rating': str(p.rating)
                }
                for p in top_products
            ]
        }
        
        return Response({
            'success': True,
            'data': data
        })


@extend_schema(tags=['Vendors'])
class VendorDocumentListView(generics.ListCreateAPIView):
    """Vendor documents management."""
    
    serializer_class = VendorDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendorOwner]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return VendorDocument.objects.none()
        return VendorDocument.objects.filter(
            vendor=self.request.user.vendor_profile
        )

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user.vendor_profile)


@extend_schema(tags=['Vendors'])
class VendorBankAccountListView(generics.ListCreateAPIView):
    """Vendor bank accounts management."""
    
    serializer_class = VendorBankAccountSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendorOwner]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return VendorBankAccount.objects.none()
        return VendorBankAccount.objects.filter(
            vendor=self.request.user.vendor_profile
        )

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user.vendor_profile)


@extend_schema(tags=['Vendors'])
class VendorBankAccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vendor bank account detail management."""
    
    serializer_class = VendorBankAccountSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendorOwner]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return VendorBankAccount.objects.none()
        return VendorBankAccount.objects.filter(
            vendor=self.request.user.vendor_profile
        )

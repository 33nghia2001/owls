"""
Product Views for Owls E-commerce Platform
==========================================
"""

from rest_framework import generics, status, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from .models import Category, Brand, Product, ProductAttribute
from .serializers import (
    CategorySerializer, CategoryListSerializer, BrandSerializer,
    ProductListSerializer, ProductDetailSerializer,
    ProductCreateUpdateSerializer, ProductAttributeSerializer
)
from .filters import ProductFilter


class IsVendorOrReadOnly(permissions.BasePermission):
    """Custom permission for vendor-only write operations."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_vendor

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.vendor.owner == request.user


@extend_schema(tags=['Products'])
class CategoryListView(generics.ListAPIView):
    """List all categories."""
    
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Category.objects.filter(
            is_active=True,
            parent__isnull=True
        ).prefetch_related('children')


@extend_schema(tags=['Products'])
class CategoryDetailView(generics.RetrieveAPIView):
    """Get category details."""
    
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return Category.objects.filter(is_active=True)


@extend_schema(tags=['Products'])
class BrandListView(generics.ListAPIView):
    """List all brands."""
    
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Brand.objects.filter(is_active=True)


@extend_schema(tags=['Products'])
class ProductListView(generics.ListAPIView):
    """List products with filtering and search."""
    
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'sku', 'tags']
    ordering_fields = ['price', 'rating', 'created_at', 'sold_count', 'view_count']
    ordering = ['-created_at']

    def get_queryset(self):
        return Product.objects.filter(
            status=Product.Status.PUBLISHED,
            is_active=True
        ).select_related('category', 'brand', 'vendor').prefetch_related('images')


@extend_schema(tags=['Products'])
class ProductDetailView(generics.RetrieveAPIView):
    """Get product details."""
    
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return Product.objects.filter(
            status=Product.Status.PUBLISHED,
            is_active=True
        ).select_related('category', 'brand', 'vendor').prefetch_related('images', 'variants')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })


@extend_schema(tags=['Products'])
class FeaturedProductsView(generics.ListAPIView):
    """List featured products."""
    
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Product.objects.filter(
            status=Product.Status.PUBLISHED,
            is_active=True,
            is_featured=True
        ).select_related('category', 'brand', 'vendor').prefetch_related('images')[:12]


@extend_schema(tags=['Products'])
class BestsellerProductsView(generics.ListAPIView):
    """List bestseller products."""
    
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Product.objects.filter(
            status=Product.Status.PUBLISHED,
            is_active=True
        ).order_by('-sold_count').select_related('category', 'brand', 'vendor').prefetch_related('images')[:12]


@extend_schema(tags=['Products'])
class NewArrivalsView(generics.ListAPIView):
    """List new arrival products."""
    
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Product.objects.filter(
            status=Product.Status.PUBLISHED,
            is_active=True,
            is_new_arrival=True
        ).order_by('-created_at').select_related('category', 'brand', 'vendor').prefetch_related('images')[:12]


@extend_schema(tags=['Products'])
class ProductAttributeListView(generics.ListAPIView):
    """List product attributes for filtering."""
    
    serializer_class = ProductAttributeSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return ProductAttribute.objects.filter(is_filterable=True).prefetch_related('values')


@extend_schema(tags=['Vendor Products'])
class VendorProductListView(generics.ListCreateAPIView):
    """Vendor's product management."""
    
    permission_classes = [permissions.IsAuthenticated, IsVendorOrReadOnly]
    serializer_class = ProductListSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateUpdateSerializer
        return ProductListSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Product.objects.none()
        return Product.objects.filter(
            vendor__owner=self.request.user
        ).select_related('category', 'brand').prefetch_related('images')

    def perform_create(self, serializer):
        vendor = self.request.user.vendor_profile
        serializer.save(vendor=vendor, status=Product.Status.PENDING)


@extend_schema(tags=['Vendor Products'])
class VendorProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vendor's product detail management."""
    
    permission_classes = [permissions.IsAuthenticated, IsVendorOrReadOnly]
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductDetailSerializer
        return ProductCreateUpdateSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Product.objects.none()
        return Product.objects.filter(
            vendor__owner=self.request.user
        ).select_related('category', 'brand').prefetch_related('images', 'variants')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.is_deleted = True
        instance.save()
        return Response({
            'success': True,
            'message': 'Product deleted successfully'
        }, status=status.HTTP_200_OK)

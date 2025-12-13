"""
Wishlist Views for Owls E-commerce Platform
===========================================
"""

from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Wishlist, WishlistItem
from .serializers import (
    WishlistSerializer,
    WishlistSummarySerializer,
    WishlistItemSerializer,
    AddToWishlistSerializer
)
from apps.business.commerce.products.models import Product, ProductVariant


def get_or_create_wishlist(user):
    """Get or create user's wishlist."""
    wishlist, _ = Wishlist.objects.get_or_create(user=user)
    return wishlist


@extend_schema(tags=['Wishlist'])
class WishlistView(generics.RetrieveUpdateAPIView):
    """
    Get or update user's wishlist.
    
    GET: Returns wishlist with all items
    PATCH: Update wishlist settings (name, is_public)
    """
    
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_or_create_wishlist(self.request.user)


@extend_schema(tags=['Wishlist'])
class WishlistItemsView(generics.ListAPIView):
    """List all items in user's wishlist."""
    
    serializer_class = WishlistItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        wishlist = get_or_create_wishlist(self.request.user)
        return WishlistItem.objects.filter(
            wishlist=wishlist
        ).select_related('product', 'variant', 'product__vendor')


@extend_schema(
    tags=['Wishlist'],
    request=AddToWishlistSerializer,
    responses={
        201: WishlistItemSerializer,
        200: OpenApiResponse(description='Product already in wishlist'),
        404: OpenApiResponse(description='Product not found')
    }
)
class AddToWishlistView(APIView):
    """Add product to wishlist."""
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddToWishlistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product_id = serializer.validated_data['product_id']
        variant_id = serializer.validated_data.get('variant_id')
        notes = serializer.validated_data.get('notes', '')
        
        # Get product and optional variant
        product = get_object_or_404(Product, id=product_id)
        variant = None
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id)
        
        # Get or create wishlist
        wishlist = get_or_create_wishlist(request.user)
        
        # Check if already in wishlist
        existing = WishlistItem.objects.filter(
            wishlist=wishlist,
            product=product,
            variant=variant
        ).first()
        
        if existing:
            return Response({
                'success': True,
                'message': 'Product already in wishlist',
                'data': WishlistItemSerializer(existing).data
            }, status=status.HTTP_200_OK)
        
        # Add to wishlist
        item = WishlistItem.objects.create(
            wishlist=wishlist,
            product=product,
            variant=variant,
            notes=notes
        )
        
        return Response({
            'success': True,
            'message': 'Product added to wishlist',
            'data': WishlistItemSerializer(item).data
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=['Wishlist'],
    responses={
        204: OpenApiResponse(description='Item removed from wishlist'),
        404: OpenApiResponse(description='Item not found in wishlist')
    }
)
class RemoveFromWishlistView(APIView):
    """Remove product from wishlist."""
    
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, item_id):
        wishlist = get_or_create_wishlist(request.user)
        
        try:
            item = WishlistItem.objects.get(
                id=item_id,
                wishlist=wishlist
            )
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except WishlistItem.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': 'Item not found in wishlist'}
            }, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    tags=['Wishlist'],
    responses={
        204: OpenApiResponse(description='Wishlist cleared')
    }
)
class ClearWishlistView(APIView):
    """Clear all items from wishlist."""
    
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        wishlist = get_or_create_wishlist(request.user)
        wishlist.clear()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=['Wishlist'],
    responses={
        200: OpenApiResponse(description='Product wishlist status')
    }
)
class CheckWishlistView(APIView):
    """Check if product is in wishlist."""
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, product_id):
        wishlist = get_or_create_wishlist(request.user)
        variant_id = request.query_params.get('variant_id')
        
        filters = {
            'wishlist': wishlist,
            'product_id': product_id
        }
        if variant_id:
            filters['variant_id'] = variant_id
        
        exists = WishlistItem.objects.filter(**filters).exists()
        
        return Response({
            'success': True,
            'data': {'in_wishlist': exists}
        })


@extend_schema(
    tags=['Wishlist'],
    responses={
        201: OpenApiResponse(description='Item added to cart'),
        404: OpenApiResponse(description='Item not found')
    }
)
class MoveToCartView(APIView):
    """Move wishlist item to cart."""
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, item_id):
        from apps.business.commerce.cart.models import Cart
        
        wishlist = get_or_create_wishlist(request.user)
        
        try:
            item = WishlistItem.objects.get(
                id=item_id,
                wishlist=wishlist
            )
        except WishlistItem.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': 'Item not found in wishlist'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check product is still available
        if item.product.status != Product.Status.PUBLISHED:
            return Response({
                'success': False,
                'error': {'message': 'Product is no longer available'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create cart
        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        # Add to cart
        cart.add_item(
            product=item.product,
            variant=item.variant,
            quantity=1
        )
        
        # Remove from wishlist
        item.delete()
        
        return Response({
            'success': True,
            'message': 'Item moved to cart'
        }, status=status.HTTP_201_CREATED)

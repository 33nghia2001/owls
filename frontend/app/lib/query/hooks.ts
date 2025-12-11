import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "./client";
import {
  productsApi,
  cartApi,
  wishlistApi,
  ordersApi,
  reviewsApi,
  vendorsApi,
  addressApi,
  authApi,
} from "../services";
import { getGuestCartId } from "../api";
import { getErrorMessage, parseApiError } from "../types/api-errors";
import type {
  Product,
  ProductListItem,
  Category,
  Brand,
  Cart,
  Order,
  Vendor,
  ShippingAddress,
  PaginatedResponse,
} from "../types";

// ==================== AUTH HOOKS ====================

export function useProfile() {
  return useQuery({
    queryKey: queryKeys.auth.profile(),
    queryFn: authApi.getProfile,
    retry: false,
  });
}

// ==================== PRODUCT HOOKS ====================

interface ProductFilters {
  page?: number;
  search?: string;
  category?: string;
  category_slug?: string;
  brand?: string;
  brand_slug?: string;
  min_price?: number;
  max_price?: number;
  ordering?: string;
  is_on_sale?: boolean;
  is_featured?: boolean;
}

export function useProducts(filters: ProductFilters = {}) {
  return useQuery({
    queryKey: queryKeys.products.list(filters),
    queryFn: () => productsApi.getProducts(filters),
    placeholderData: (previousData) => previousData,
  });
}

export function useProduct(slug: string) {
  return useQuery({
    queryKey: queryKeys.products.detail(slug),
    queryFn: () => productsApi.getProduct(slug),
    enabled: !!slug,
  });
}

export function useFeaturedProducts() {
  return useQuery({
    queryKey: queryKeys.products.featured(),
    queryFn: productsApi.getFeaturedProducts,
  });
}

export function useBestSellers() {
  return useQuery({
    queryKey: queryKeys.products.bestSellers(),
    queryFn: productsApi.getBestSellers,
  });
}

export function useNewArrivals() {
  return useQuery({
    queryKey: queryKeys.products.newArrivals(),
    queryFn: productsApi.getNewArrivals,
  });
}

export function useProductSearch(query: string) {
  return useQuery({
    queryKey: queryKeys.products.search(query),
    queryFn: () => productsApi.searchProducts(query),
    enabled: query.length > 2,
  });
}

// ==================== CATEGORY HOOKS ====================

export function useCategories() {
  return useQuery({
    queryKey: queryKeys.categories.list(),
    queryFn: productsApi.getCategories,
    staleTime: 10 * 60 * 1000, // Categories change rarely
  });
}

export function useCategoryTree() {
  return useQuery({
    queryKey: queryKeys.categories.tree(),
    queryFn: productsApi.getCategoryTree,
    staleTime: 10 * 60 * 1000,
  });
}

export function useCategoryProducts(
  slug: string,
  filters?: object
) {
  return useQuery({
    queryKey: queryKeys.categories.products(slug, filters),
    queryFn: () => productsApi.getCategoryProducts(slug, filters),
    enabled: !!slug,
  });
}

// ==================== BRAND HOOKS ====================

export function useBrands() {
  return useQuery({
    queryKey: queryKeys.brands.list(),
    queryFn: productsApi.getBrands,
    staleTime: 10 * 60 * 1000,
  });
}

// ==================== CART HOOKS ====================

export function useCart() {
  const guestCartId = getGuestCartId();

  return useQuery({
    queryKey: queryKeys.cart.detail(guestCartId),
    queryFn: () => cartApi.getCart(guestCartId),
    staleTime: 1 * 60 * 1000, // Cart data should be fresher
  });
}

export function useAddToCart() {
  const queryClient = useQueryClient();
  const guestCartId = getGuestCartId();

  return useMutation({
    mutationFn: (data: {
      productId: string;
      quantity: number;
      variantId?: string;
    }) =>
      cartApi.addToCart({
        product_id: data.productId,
        variant_id: data.variantId,
        quantity: data.quantity,
        guest_cart_id: guestCartId,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.cart.all });
    },
  });
}

export function useUpdateCartItem() {
  const queryClient = useQueryClient();
  const guestCartId = getGuestCartId();

  return useMutation({
    mutationFn: (data: { itemId: string; quantity: number }) =>
      cartApi.updateCartItem(data.itemId, data.quantity, guestCartId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.cart.all });
    },
  });
}

export function useRemoveCartItem() {
  const queryClient = useQueryClient();
  const guestCartId = getGuestCartId();

  return useMutation({
    mutationFn: (itemId: string) => cartApi.removeCartItem(itemId, guestCartId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.cart.all });
    },
  });
}

export function useClearCart() {
  const queryClient = useQueryClient();
  const guestCartId = getGuestCartId();

  return useMutation({
    mutationFn: () => cartApi.clearCart(guestCartId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.cart.all });
    },
  });
}

export function useApplyCoupon() {
  const queryClient = useQueryClient();
  const guestCartId = getGuestCartId();

  return useMutation({
    mutationFn: (code: string) => cartApi.applyCoupon(code, guestCartId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.cart.all });
    },
  });
}

export function useRemoveCoupon() {
  const queryClient = useQueryClient();
  const guestCartId = getGuestCartId();

  return useMutation({
    mutationFn: () => cartApi.removeCoupon(guestCartId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.cart.all });
    },
  });
}

// ==================== WISHLIST HOOKS ====================

export function useWishlist() {
  return useQuery({
    queryKey: queryKeys.wishlist.list(),
    queryFn: wishlistApi.getWishlist,
    retry: false, // Don't retry if user is not authenticated
  });
}

export function useAddToWishlist() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (productId: string) => wishlistApi.addToWishlist(productId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.wishlist.all });
    },
  });
}

export function useRemoveFromWishlist() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (productId: string) => wishlistApi.removeFromWishlist(productId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.wishlist.all });
    },
  });
}

// ==================== ORDER HOOKS ====================

interface OrderFilters {
  page?: number;
  status?: string;
}

export function useOrders(filters: OrderFilters = {}) {
  return useQuery({
    queryKey: queryKeys.orders.list(filters),
    queryFn: () => ordersApi.getOrders(filters),
  });
}

export function useOrder(id: string) {
  return useQuery({
    queryKey: queryKeys.orders.detail(id),
    queryFn: () => ordersApi.getOrder(id),
    enabled: !!id,
  });
}

export function useCreateOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ordersApi.createOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.orders.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.cart.all });
    },
  });
}

export function useCancelOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => ordersApi.cancelOrder(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.orders.all });
    },
  });
}

// ==================== VENDOR HOOKS ====================

interface VendorFilters {
  page?: number;
  search?: string;
}

export function useVendors(filters: VendorFilters = {}) {
  return useQuery({
    queryKey: queryKeys.vendors.list(),
    queryFn: () => vendorsApi.getVendors(filters),
  });
}

export function useVendor(slug: string) {
  return useQuery({
    queryKey: queryKeys.vendors.detail(slug),
    queryFn: () => vendorsApi.getVendor(slug),
    enabled: !!slug,
  });
}

export function useVendorProducts(
  slug: string,
  filters?: object
) {
  return useQuery({
    queryKey: queryKeys.vendors.products(slug, filters),
    queryFn: () => vendorsApi.getVendorProducts(slug, filters),
    enabled: !!slug,
  });
}

// ==================== REVIEW HOOKS ====================

export function useProductReviews(productId: string, page?: number) {
  return useQuery({
    queryKey: queryKeys.reviews.product(productId),
    queryFn: () => reviewsApi.getProductReviews(productId, { page }),
    enabled: !!productId,
  });
}

export function useCreateReview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: reviewsApi.createReview,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.reviews.product(variables.product),
      });
      // Also invalidate product detail to update review count
      queryClient.invalidateQueries({ queryKey: queryKeys.products.all });
    },
  });
}

export function useMarkReviewHelpful() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (reviewId: string) => reviewsApi.markHelpful(reviewId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.reviews.all });
    },
  });
}

// ==================== ADDRESS HOOKS ====================

export function useAddresses() {
  return useQuery({
    queryKey: queryKeys.addresses.list(),
    queryFn: addressApi.getAddresses,
  });
}

export function useCreateAddress() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: addressApi.createAddress,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.addresses.all });
    },
  });
}

export function useUpdateAddress() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: Partial<ShippingAddress>;
    }) => addressApi.updateAddress(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.addresses.all });
    },
  });
}

export function useDeleteAddress() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => addressApi.deleteAddress(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.addresses.all });
    },
  });
}

export function useSetDefaultAddress() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => addressApi.setDefaultAddress(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.addresses.all });
    },
  });
}

import api, { setTokens, getTokens, setGuestCartId } from "./api";
import type { User, AuthTokens, ShippingAddress } from "./types";

// Auth APIs
export const authApi = {
  register: async (data: {
    email: string;
    password: string;
    password_confirm: string;
    first_name: string;
    last_name: string;
    phone?: string;
  }) => {
    const response = await api.post<{ user: User; tokens: AuthTokens }>(
      "/auth/register/",
      data
    );
    setTokens(response.data.tokens);
    return response.data;
  },

  login: async (email: string, password: string, guestCartId?: string | null) => {
    const response = await api.post<{ user: User; tokens: AuthTokens }>(
      "/auth/login/",
      { email, password, guest_cart_id: guestCartId }
    );
    setTokens(response.data.tokens);
    setGuestCartId(null); // Clear guest cart after merge
    return response.data;
  },

  logout: async () => {
    const tokens = getTokens();
    if (tokens?.refresh) {
      try {
        await api.post("/auth/logout/", { refresh: tokens.refresh });
      } catch {
        // Ignore errors on logout
      }
    }
    setTokens(null);
  },

  getProfile: async () => {
    const response = await api.get<User>("/users/me/");
    return response.data;
  },

  updateProfile: async (data: Partial<User>) => {
    const response = await api.patch<User>("/users/me/", data);
    return response.data;
  },

  changePassword: async (data: {
    old_password: string;
    new_password: string;
    new_password_confirm: string;
  }) => {
    const response = await api.post("/users/change-password/", data);
    return response.data;
  },

  forgotPassword: async (email: string) => {
    const response = await api.post("/users/forgot-password/", { email });
    return response.data;
  },

  resetPassword: async (data: {
    token: string;
    password: string;
    password_confirm: string;
  }) => {
    const response = await api.post("/users/reset-password/", data);
    return response.data;
  },
};

// Products APIs
export const productsApi = {
  getProducts: async (params?: {
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
  }) => {
    const response = await api.get("/products/", { params });
    return response.data;
  },

  getProduct: async (slug: string) => {
    const response = await api.get(`/products/${slug}/`);
    return response.data;
  },

  getFeaturedProducts: async () => {
    const response = await api.get("/products/featured/");
    return response.data;
  },

  getBestSellers: async () => {
    const response = await api.get("/products/best_sellers/");
    return response.data;
  },

  getNewArrivals: async () => {
    const response = await api.get("/products/new_arrivals/");
    return response.data;
  },

  getCategories: async () => {
    const response = await api.get("/categories/");
    return response.data;
  },

  getCategoryTree: async () => {
    const response = await api.get("/categories/tree/");
    return response.data;
  },

  getCategoryProducts: async (slug: string, params?: object) => {
    const response = await api.get(`/categories/${slug}/products/`, { params });
    return response.data;
  },

  getBrands: async () => {
    const response = await api.get("/brands/");
    return response.data;
  },

  searchProducts: async (query: string) => {
    const response = await api.get("/products/", {
      params: { search: query },
    });
    return response.data;
  },
};

// Cart APIs
export const cartApi = {
  getCart: async (guestCartId?: string | null) => {
    const params = guestCartId ? { guest_cart_id: guestCartId } : {};
    const response = await api.get("/cart/", { params });
    return response.data;
  },

  addToCart: async (data: {
    product_id: string;
    variant_id?: string;
    quantity: number;
    guest_cart_id?: string | null;
  }) => {
    const response = await api.post("/cart/add/", data);
    // Save guest cart ID if returned
    if (response.data.cart_id && !getTokens()) {
      setGuestCartId(response.data.cart_id);
    }
    return response.data;
  },

  updateCartItem: async (
    itemId: string,
    quantity: number,
    guestCartId?: string | null
  ) => {
    const response = await api.patch(`/cart/items/${itemId}/`, {
      quantity,
      guest_cart_id: guestCartId,
    });
    return response.data;
  },

  removeCartItem: async (itemId: string, guestCartId?: string | null) => {
    const params = guestCartId ? { guest_cart_id: guestCartId } : {};
    await api.delete(`/cart/items/${itemId}/`, { params });
  },

  clearCart: async (guestCartId?: string | null) => {
    const params = guestCartId ? { guest_cart_id: guestCartId } : {};
    await api.post("/cart/clear/", {}, { params });
  },

  applyCoupon: async (code: string, guestCartId?: string | null) => {
    const response = await api.post("/cart/apply_coupon/", {
      code,
      guest_cart_id: guestCartId,
    });
    return response.data;
  },

  removeCoupon: async (guestCartId?: string | null) => {
    const params = guestCartId ? { guest_cart_id: guestCartId } : {};
    const response = await api.post("/cart/remove_coupon/", {}, { params });
    return response.data;
  },
};

// Orders APIs
export const ordersApi = {
  getOrders: async (params?: { page?: number; status?: string }) => {
    const response = await api.get("/orders/", { params });
    return response.data;
  },

  getOrder: async (id: string) => {
    const response = await api.get(`/orders/${id}/`);
    return response.data;
  },

  createOrder: async (data: {
    shipping_address_id?: string;
    shipping_address?: Partial<ShippingAddress>;
    shipping_method_id?: string;
    notes?: string;
    coupon_code?: string;
  }) => {
    const response = await api.post("/orders/", data);
    return response.data;
  },

  cancelOrder: async (id: string) => {
    const response = await api.post(`/orders/${id}/cancel/`);
    return response.data;
  },
};

// Shipping Addresses APIs
export const addressApi = {
  getAddresses: async () => {
    const response = await api.get("/shipping/addresses/");
    return response.data;
  },

  createAddress: async (data: Partial<ShippingAddress>) => {
    const response = await api.post("/shipping/addresses/", data);
    return response.data;
  },

  updateAddress: async (id: string, data: Partial<ShippingAddress>) => {
    const response = await api.patch(`/shipping/addresses/${id}/`, data);
    return response.data;
  },

  deleteAddress: async (id: string) => {
    await api.delete(`/shipping/addresses/${id}/`);
  },

  setDefaultAddress: async (id: string) => {
    const response = await api.post(`/shipping/addresses/${id}/set_default/`);
    return response.data;
  },
};

// Payments APIs
export const paymentsApi = {
  createPayment: async (data: { order_id: string; method: string }) => {
    const response = await api.post("/payments/create_payment/", data);
    return response.data;
  },

  getPayments: async () => {
    const response = await api.get("/payments/");
    return response.data;
  },
};

// Reviews APIs
export const reviewsApi = {
  getProductReviews: async (productId: string, params?: { page?: number }) => {
    const response = await api.get(`/reviews/`, {
      params: { product: productId, ...params },
    });
    return response.data;
  },

  createReview: async (data: {
    product: string;
    order_item: string;
    rating: number;
    title: string;
    comment: string;
  }) => {
    const response = await api.post("/reviews/", data);
    return response.data;
  },

  markHelpful: async (reviewId: string) => {
    const response = await api.post(`/reviews/${reviewId}/helpful/`);
    return response.data;
  },
};

// Wishlist APIs
export const wishlistApi = {
  getWishlist: async () => {
    const response = await api.get("/wishlists/");
    return response.data;
  },

  addToWishlist: async (productId: string) => {
    const response = await api.post("/wishlists/", { product: productId });
    return response.data;
  },

  removeFromWishlist: async (productId: string) => {
    await api.delete(`/wishlists/${productId}/`);
  },

  checkInWishlist: async (productId: string) => {
    const response = await api.get(`/wishlists/check/${productId}/`);
    return response.data;
  },
};

// Vendors APIs
export const vendorsApi = {
  getVendors: async (params?: { page?: number; search?: string }) => {
    const response = await api.get("/vendors/", { params });
    return response.data;
  },

  getVendor: async (slug: string) => {
    const response = await api.get(`/vendors/${slug}/`);
    return response.data;
  },

  getVendorProducts: async (slug: string, params?: object) => {
    const response = await api.get(`/vendors/${slug}/products/`, { params });
    return response.data;
  },
};

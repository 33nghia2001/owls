import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { User, Cart } from "./types";
import { authApi, cartApi } from "./services";
import { getGuestCartId, getTokens } from "./api";

// --- Auth Store ---
interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (data: any) => Promise<void>;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,

  setUser: (user) => set({ user, isAuthenticated: !!user }),

  login: async (email, password) => {
    const guestCartId = getGuestCartId();
    const { user } = await authApi.login(email, password, guestCartId);
    set({ user, isAuthenticated: true });
    useCartStore.getState().fetchCart();
  },

  logout: async () => {
    await authApi.logout();
    set({ user: null, isAuthenticated: false });
    useCartStore.getState().clearLocalCart();
  },

  register: async (data) => {
    const { user } = await authApi.register(data);
    set({ user, isAuthenticated: true });
  },

  checkAuth: async () => {
    const tokens = getTokens();
    if (!tokens) {
      set({ isLoading: false, isAuthenticated: false });
      return;
    }
    try {
      const user = await authApi.getProfile();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },
}));

// --- Cart Store ---
interface CartState {
  cart: Cart | null;
  isLoading: boolean;
  itemCount: number;
  fetchCart: () => Promise<void>;
  addToCart: (productId: string, quantity: number, variantId?: string) => Promise<void>;
  updateQuantity: (itemId: string, quantity: number) => Promise<void>;
  removeItem: (itemId: string) => Promise<void>;
  clearCart: () => Promise<void>;
  clearLocalCart: () => void;
  applyCoupon: (code: string) => Promise<void>;
  removeCoupon: () => Promise<void>;
}

export const useCartStore = create<CartState>((set, get) => ({
  cart: null,
  isLoading: false,
  itemCount: 0,

  fetchCart: async () => {
    set({ isLoading: true });
    try {
      const guestCartId = getGuestCartId();
      const cart = await cartApi.getCart(guestCartId);
      set({
        cart,
        itemCount: cart?.item_count || 0,
        isLoading: false,
      });
    } catch {
      set({ cart: null, itemCount: 0, isLoading: false });
    }
  },

  addToCart: async (productId, quantity, variantId) => {
    const guestCartId = getGuestCartId();
    await cartApi.addToCart({
      product_id: productId,
      variant_id: variantId,
      quantity,
      guest_cart_id: guestCartId,
    });
    await get().fetchCart();
  },

  updateQuantity: async (itemId, quantity) => {
    const guestCartId = getGuestCartId();
    await cartApi.updateCartItem(itemId, quantity, guestCartId);
    await get().fetchCart();
  },

  removeItem: async (itemId) => {
    const guestCartId = getGuestCartId();
    await cartApi.removeCartItem(itemId, guestCartId);
    await get().fetchCart();
  },

  clearCart: async () => {
    const guestCartId = getGuestCartId();
    await cartApi.clearCart(guestCartId);
    set({ cart: null, itemCount: 0 });
  },

  clearLocalCart: () => {
    set({ cart: null, itemCount: 0 });
  },

  applyCoupon: async (code) => {
    const guestCartId = getGuestCartId();
    await cartApi.applyCoupon(code, guestCartId);
    await get().fetchCart();
  },

  removeCoupon: async () => {
    const guestCartId = getGuestCartId();
    await cartApi.removeCoupon(guestCartId);
    await get().fetchCart();
  },
}));

// --- UI Store ---
interface UIState {
  isMobileMenuOpen: boolean;
  isCartSidebarOpen: boolean;
  isSearchOpen: boolean;
  toggleMobileMenu: () => void;
  toggleCartSidebar: () => void;
  toggleSearch: () => void;
  closeAll: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  isMobileMenuOpen: false,
  isCartSidebarOpen: false,
  isSearchOpen: false,
  toggleMobileMenu: () => set((state) => ({ isMobileMenuOpen: !state.isMobileMenuOpen })),
  toggleCartSidebar: () => set((state) => ({ isCartSidebarOpen: !state.isCartSidebarOpen })),
  toggleSearch: () => set((state) => ({ isSearchOpen: !state.isSearchOpen })),
  closeAll: () => set({ isMobileMenuOpen: false, isCartSidebarOpen: false, isSearchOpen: false }),
}));

// --- Wishlist Store (Fixed Hydration) ---
interface WishlistState {
  items: string[];
  isLoading: boolean;
  fetchWishlist: () => Promise<void>;
  addItem: (productId: string) => Promise<void>;
  removeItem: (productId: string) => Promise<void>;
  isInWishlist: (productId: string) => boolean;
  clearWishlist: () => void;
}

export const useWishlistStore = create<WishlistState>()(
  persist(
    (set, get) => ({
      items: [],
      isLoading: false,

      fetchWishlist: async () => {
        if (!getTokens()) return;
        set({ isLoading: true });
        try {
          const wishlist = await import("./services").then((m) =>
            m.wishlistApi.getWishlist()
          );
          const items = wishlist.results?.map((item: any) => item.product.id) || [];
          set({ items, isLoading: false });
        } catch {
          set({ isLoading: false });
        }
      },

      addItem: async (productId) => {
        if (!getTokens()) {
          set((state) => ({ items: [...state.items, productId] }));
          return;
        }
        await import("./services").then((m) =>
          m.wishlistApi.addToWishlist(productId)
        );
        set((state) => ({ items: [...state.items, productId] }));
      },

      removeItem: async (productId) => {
        if (!getTokens()) {
          set((state) => ({
            items: state.items.filter((id) => id !== productId),
          }));
          return;
        }
        await import("./services").then((m) =>
          m.wishlistApi.removeFromWishlist(productId)
        );
        set((state) => ({
          items: state.items.filter((id) => id !== productId),
        }));
      },

      clearWishlist: () => {
        set({ items: [] });
      },

      isInWishlist: (productId) => get().items.includes(productId),
    }),
    {
      name: "wishlist-storage",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ items: state.items }),
      skipHydration: true, // QUAN TRỌNG: Tránh lỗi hydration mismatch
    }
  )
);
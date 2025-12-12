import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { User } from "./types";
import { authApi } from "./services";
import { isAuthenticated as checkTokenAuth } from "./api";

// --- Auth Store ---
interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  login: (email: string, password: string, guestCartId?: string | null) => Promise<void>;
  logout: () => Promise<void>;
  register: (data: any) => Promise<void>;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,

  setUser: (user) => set({ user, isAuthenticated: !!user }),

  login: async (email, password, guestCartId) => {
    const { user } = await authApi.login(email, password, guestCartId);
    set({ user, isAuthenticated: true });
  },

  logout: async () => {
    await authApi.logout();
    set({ user: null, isAuthenticated: false });
  },

  register: async (data) => {
    const { user } = await authApi.register(data);
    set({ user, isAuthenticated: true });
  },

  checkAuth: async () => {
    // With httpOnly cookies, we can't check tokens directly
    // Try to get user profile - if it succeeds, we're authenticated
    try {
      const user = await authApi.getProfile();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      // If profile fails, check legacy tokens for backward compatibility
      if (!checkTokenAuth()) {
        set({ isLoading: false, isAuthenticated: false });
        return;
      }
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
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

// --- Wishlist Store ---
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
        // With httpOnly cookies, we just try to fetch and let server decide
        set({ isLoading: true });
        try {
          const wishlist = await import("./services").then((m) =>
            m.wishlistApi.getWishlist()
          );
          const items = wishlist.results?.map((item: { product: { id: string } }) => item.product.id) || [];
          set({ items, isLoading: false });
        } catch {
          // User not authenticated or error - use local storage
          set({ isLoading: false });
        }
      },

      addItem: async (productId) => {
        // Try server-side first, fall back to local
        try {
          await import("./services").then((m) =>
            m.wishlistApi.addToWishlist(productId)
          );
          set((state) => ({ items: [...state.items, productId] }));
        } catch {
          // Not authenticated - store locally
          set((state) => ({ items: [...state.items, productId] }));
        }
      },

      removeItem: async (productId) => {
        // Try server-side first, fall back to local
        try {
          await import("./services").then((m) =>
            m.wishlistApi.removeFromWishlist(productId)
          );
        } catch {
          // Not authenticated or error - continue with local removal
        }
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
      skipHydration: true,
    }
  )
);
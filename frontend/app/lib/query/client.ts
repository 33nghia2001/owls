import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Stale time: 5 minutes - data is considered fresh for this duration
      staleTime: 5 * 60 * 1000,
      // Cache time: 30 minutes - unused data remains in cache
      gcTime: 30 * 60 * 1000,
      // Retry failed requests 3 times with exponential backoff
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      // Refetch on window focus for fresh data
      refetchOnWindowFocus: true,
      // Don't refetch on mount if data is fresh
      refetchOnMount: true,
    },
    mutations: {
      // Retry mutations once on failure
      retry: 1,
    },
  },
});

// Query keys factory for type-safe query keys
export const queryKeys = {
  // Auth
  auth: {
    all: ["auth"] as const,
    profile: () => [...queryKeys.auth.all, "profile"] as const,
  },

  // Products
  products: {
    all: ["products"] as const,
    lists: () => [...queryKeys.products.all, "list"] as const,
    list: (filters: object) =>
      [...queryKeys.products.lists(), filters] as const,
    details: () => [...queryKeys.products.all, "detail"] as const,
    detail: (slug: string) => [...queryKeys.products.details(), slug] as const,
    featured: () => [...queryKeys.products.all, "featured"] as const,
    bestSellers: () => [...queryKeys.products.all, "best-sellers"] as const,
    newArrivals: () => [...queryKeys.products.all, "new-arrivals"] as const,
    search: (query: string) => [...queryKeys.products.all, "search", query] as const,
  },

  // Categories
  categories: {
    all: ["categories"] as const,
    list: () => [...queryKeys.categories.all, "list"] as const,
    tree: () => [...queryKeys.categories.all, "tree"] as const,
    detail: (slug: string) => [...queryKeys.categories.all, "detail", slug] as const,
    products: (slug: string, filters?: object) =>
      [...queryKeys.categories.all, slug, "products", filters] as const,
  },

  // Brands
  brands: {
    all: ["brands"] as const,
    list: () => [...queryKeys.brands.all, "list"] as const,
  },

  // Cart
  cart: {
    all: ["cart"] as const,
    detail: (guestCartId?: string | null) =>
      [...queryKeys.cart.all, "detail", guestCartId] as const,
  },

  // Wishlist
  wishlist: {
    all: ["wishlist"] as const,
    list: () => [...queryKeys.wishlist.all, "list"] as const,
  },

  // Orders
  orders: {
    all: ["orders"] as const,
    list: (filters?: object) =>
      [...queryKeys.orders.all, "list", filters] as const,
    detail: (id: string) => [...queryKeys.orders.all, "detail", id] as const,
  },

  // Reviews
  reviews: {
    all: ["reviews"] as const,
    product: (productId: string) =>
      [...queryKeys.reviews.all, "product", productId] as const,
    user: () => [...queryKeys.reviews.all, "user"] as const,
  },

  // Vendors
  vendors: {
    all: ["vendors"] as const,
    list: () => [...queryKeys.vendors.all, "list"] as const,
    detail: (slug: string) => [...queryKeys.vendors.all, "detail", slug] as const,
    products: (slug: string, filters?: object) =>
      [...queryKeys.vendors.all, slug, "products", filters] as const,
  },

  // Addresses
  addresses: {
    all: ["addresses"] as const,
    list: () => [...queryKeys.addresses.all, "list"] as const,
  },
} as const;

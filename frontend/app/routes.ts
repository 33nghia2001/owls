import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  
  // Auth routes
  route("login", "routes/auth/login.tsx"),
  route("register", "routes/auth/register.tsx"),
  route("forgot-password", "routes/auth/forgot-password.tsx"),
  
  // Product routes
  route("products", "routes/products/index.tsx"),
  route("products/:slug", "routes/products/detail.tsx"),
  route("search", "routes/search.tsx"),
  
  // Category routes
  route("categories", "routes/categories/index.tsx"),
  route("categories/:slug", "routes/categories/detail.tsx"),
  
  // Cart & Checkout
  route("cart", "routes/cart.tsx"),
  route("checkout", "routes/checkout.tsx"),
  route("checkout/success", "routes/checkout/success.tsx"),
  
  // User account routes
  route("account", "routes/account/index.tsx"),
  route("account/orders", "routes/account/orders.tsx"),
  route("account/orders/:id", "routes/account/order-detail.tsx"),
  route("account/addresses", "routes/account/addresses.tsx"),
  route("account/profile", "routes/account/profile.tsx"),
  route("account/settings", "routes/account/settings.tsx"),
  
  // Wishlist
  route("wishlist", "routes/wishlist.tsx"),
  
  // Vendor/Shop pages
  route("shops", "routes/shops/index.tsx"),
  route("shops/:slug", "routes/shops/detail.tsx"),
  
  // Seller dashboard
  route("seller", "routes/seller/index.tsx"),
  route("seller/products", "routes/seller/products.tsx"),
  route("seller/products/new", "routes/seller/products-new.tsx"),
  route("seller/orders", "routes/seller/orders.tsx"),
  route("seller/orders/:id", "routes/seller/order-detail.tsx"),
  route("seller/settings", "routes/seller/settings.tsx"),
] satisfies RouteConfig;

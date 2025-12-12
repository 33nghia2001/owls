import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  
  // Auth routes - use /auth prefix for consistency
  route("auth/login", "routes/auth/login.tsx"),
  route("auth/register", "routes/auth/register.tsx"),
  route("auth/forgot-password", "routes/auth/forgot-password.tsx"),
  route("auth/reset-password", "routes/auth/reset-password.tsx"),
  
  // Redirect old auth routes for backward compatibility
  route("login", "routes/auth/login-redirect.tsx"),
  route("register", "routes/auth/register-redirect.tsx"),
  
  // Deals page
  route("deals", "routes/deals.tsx"),
  
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
  route("checkout/cancel", "routes/checkout/cancel.tsx"),
  
  // User account routes
  route("account", "routes/account/index.tsx"),
  route("account/orders", "routes/account/orders.tsx"),
  route("account/orders/:id", "routes/account/order-detail.tsx"),
  route("account/addresses", "routes/account/addresses.tsx"),
  route("account/profile", "routes/account/profile.tsx"),
  route("account/settings", "routes/account/settings.tsx"),
  
  // Wishlist
  route("wishlist", "routes/wishlist.tsx"),
  
  // Notifications
  route("notifications", "routes/notifications.tsx"),
  
  // Vendor/Shop pages
  route("shops", "routes/shops/index.tsx"),
  route("shops/:slug", "routes/shops/detail.tsx"),
  
  // Seller dashboard
  route("seller", "routes/seller/index.tsx"),
  route("seller/register", "routes/seller/register.tsx"), // <-- MỚI THÊM
  route("seller/products", "routes/seller/products.tsx"),
  route("seller/products/new", "routes/seller/products-new.tsx"),
  route("seller/orders", "routes/seller/orders.tsx"),
  route("seller/orders/:id", "routes/seller/order-detail.tsx"),
  route("seller/settings", "routes/seller/settings.tsx"),

  // Static/Legal pages
  route("privacy", "routes/pages/privacy.tsx"),
  route("terms", "routes/pages/terms.tsx"),
  route("shipping-policy", "routes/pages/shipping-policy.tsx"),
  route("return-policy", "routes/pages/return-policy.tsx"),
  route("faq", "routes/pages/faq.tsx"),

] satisfies RouteConfig;
// frontend/app/lib/types/index.ts

// Re-export api-errors
export * from "./api-errors";

// ==========================================
// Common Types
// ==========================================

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Money {
  amount: string;
  currency: string;
}

// ==========================================
// Auth Types
// ==========================================

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone?: string;
  avatar?: string;
  is_staff: boolean;
  is_vendor: boolean;
  date_joined: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
  tokens: AuthTokens;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

// ==========================================
// Address Types
// ==========================================

export interface ShippingAddress {
  id: string;
  full_name: string;
  phone: string;
  street_address: string; // Backend: street_address
  city: string;           // Backend: city (Tỉnh/Thành phố)
  state: string;          // Backend: state (Phường/Xã/Quận/Huyện)
  country: string;
  postal_code: string;
  is_default: boolean;

  // Optional fields for UI backward compatibility if needed
  address_line1?: string; 
  province?: string;
  ward?: string;
}

// ==========================================
// Vendor Types
// ==========================================

export interface Vendor {
  id: string;
  shop_name: string;
  slug: string;
  description: string;
  logo: string | null;
  banner: string | null;
  rating: number;
  total_sales: number;
  total_products: number;
  is_featured: boolean;
  city?: string;
  created_at: string;
}

// ==========================================
// Product & Category Types
// ==========================================

export interface Category {
  id: string;
  name: string;
  slug: string;
  image?: string;
  description?: string;
  parent?: string;
  children?: Category[];
  product_count?: number;
}

export interface Brand {
  id: string;
  name: string;
  slug: string;
  logo: string | null;
}

export interface ProductImage {
  id: string;
  image: string;
  alt_text?: string;
  is_primary: boolean;
  order: number;
}

export interface ProductVariant {
  id: string;
  name: string;
  sku: string;
  price: Money;
  compare_price: Money | null;
  image: ProductImage | null;
  is_active: boolean;
  stock_quantity?: number; // Optional based on serializer context
}

export interface Product {
  id: string;
  name: string;
  slug: string;
  sku?: string;
  description: string;
  short_description: string;
  price: Money;
  compare_price: Money | null;
  is_on_sale: boolean;
  discount_percentage: number;
  
  images: ProductImage[];
  primary_image?: ProductImage; // Helper from UI logic
  
  category: Category;
  brand: Brand | null;
  vendor: {
    id: string;
    shop_name: string;
    slug: string;
    logo: string | null;
    rating: number;
  };
  
  variants: ProductVariant[];
  tags: string[];
  
  rating: number;
  review_count: number;
  sold_count: number;
  view_count: number;
  
  created_at: string;
  updated_at: string;
}

export interface ProductListItem {
  id: string;
  name: string;
  slug: string;
  price: Money | string | number;
  compare_price: Money | string | number | null;
  is_on_sale: boolean;
  discount_percentage: number;
  primary_image: ProductImage | null;
  vendor_name: string;
  category_name: string;
  rating: number;
  review_count: number;
  sold_count: number;
  is_featured: boolean;
  has_variants: boolean;
}

// ==========================================
// Cart Types
// ==========================================

export interface CartItem {
  id: string;
  product: ProductListItem; // Cart often uses list item details
  product_id?: string;
  variant: ProductVariant | null;
  variant_id?: string | null;
  quantity: number;
  unit_price: Money;
  total_price: Money;
  created_at: string;
}

export interface Cart {
  id: string;
  items: CartItem[];
  subtotal: Money;
  total_items: number;
  item_count?: number; // Alias for total_items if needed
  created_at: string;
  updated_at: string;
}

// ==========================================
// Order Types
// ==========================================

export interface OrderItem {
  id: string;
  product: string; // ID
  variant: string | null; // ID
  product_name: string;
  product_sku: string;
  variant_name: string;
  quantity: number;
  unit_price: Money;
  total_price: Money;
  status: string;
  // UI Helpers
  primary_image?: string; 
}

export interface OrderStatusHistory {
  id: string;
  status: string;
  note: string;
  created_by_email?: string;
  created_at: string;
}

export interface Order {
  id: string;
  order_number: string;
  status: 'pending' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled' | 'refunded';
  payment_status: 'pending' | 'paid' | 'failed' | 'refunded';
  
  subtotal: Money;
  shipping_cost: Money;
  discount_amount: Money;
  tax_amount: Money;
  total: Money;
  
  // --- Thông tin giao hàng (Khớp Backend Order Model) ---
  shipping_name: string;
  shipping_phone: string;
  shipping_address: string;
  shipping_city: string;      // Tỉnh/Thành phố
  shipping_state: string;     // Phường/Xã/Quận
  shipping_country: string;
  shipping_postal_code: string;
  
  // --- Thông tin thanh toán (Billing) ---
  billing_name?: string;
  billing_phone?: string;
  billing_address?: string;
  billing_city?: string;
  billing_state?: string;
  billing_country?: string;
  billing_postal_code?: string;
  
  customer_note?: string;
  coupon?: string | null; // Coupon code or ID
  
  items: OrderItem[];
  status_history: OrderStatusHistory[];
  
  created_at: string;
  confirmed_at?: string;
  shipped_at?: string;
  delivered_at?: string;
}

// Interface dùng cho Payload gửi lên API
export interface CreateOrderPayload {
  shipping_name: string;
  shipping_phone: string;
  shipping_address: string;
  shipping_city: string;    // Khớp OrderSerializer
  shipping_state: string;   // Khớp OrderSerializer
  shipping_country?: string;
  shipping_postal_code?: string;
  
  customer_note?: string;
  coupon_code?: string;
  payment_method: 'cod' | 'stripe' | 'vnpay';
  
  // Billing optional
  same_as_shipping?: boolean;
  billing_name?: string;
  billing_phone?: string;
  billing_address?: string;
  billing_city?: string;
  billing_state?: string;
  billing_country?: string;
  billing_postal_code?: string;
  
  // Frontend Helpers (mapped before sending)
  shipping_province?: string;
  shipping_ward?: string;
}

// ==========================================
// Payment Types
// ==========================================

export interface CreatePaymentPayload {
  order_id: string;
  method: 'cod' | 'stripe' | 'vnpay';
}

export interface CreatePaymentResponse {
  payment_url?: string;
  checkout_url?: string;
  status?: string;
  message?: string;
  payment?: any;
}

// ==========================================
// Review Types
// ==========================================

export interface ReviewImage {
  id: string;
  image: string;
}

export interface Review {
  id: string;
  user_name: string;
  user_avatar: string | null;
  rating: number;
  title?: string;
  comment: string;
  images: ReviewImage[];
  helpful_count: number;
  is_helpful: boolean;
  created_at: string;
}

export interface ReviewStats {
  total_reviews: number;
  average_rating: number;
  rating_distribution: Record<number, number>;
}
// Re-export api-errors
export * from "./api-errors";

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
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
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
// Product & Category Types
// ==========================================

export interface Category {
  id: string;
  name: string;
  slug: string;
  image?: string;
  description?: string;
  parent?: string; // ID của category cha
}

export interface ProductImage {
  id: string;
  image: string;
  alt_text?: string;
  is_primary: boolean;
}

export interface ProductVariant {
  id: string;
  name: string;
  sku: string;
  price: string;
  stock_quantity: number;
  attributes: Record<string, string>; // JSON attributes
}

export interface Product {
  id: string;
  name: string;
  slug: string;
  sku?: string;
  description: string;
  price: string;
  compare_at_price?: string;
  images: ProductImage[];
  primary_image?: ProductImage;
  category: Category;
  vendor: {
    id: string;
    store_name: string;
    slug: string;
  };
  variants: ProductVariant[];
  in_stock: boolean;
  rating_average: number;
  reviews_count: number;
  created_at: string;
}

// ==========================================
// Cart Types
// ==========================================

export interface CartItem {
  id: string;
  product: Product;
  variant?: ProductVariant;
  quantity: number;
  unit_price: string;
  total_price: string;
}

export interface Cart {
  id: string;
  items: CartItem[];
  subtotal: string;
  total: string;
}

// ==========================================
// Order Types (QUAN TRỌNG: Cập nhật field địa chỉ)
// ==========================================

export interface OrderItem {
  id: string;
  product_name: string;
  product_sku: string;
  variant_name: string;
  quantity: number;
  unit_price: string;
  total_price: string;
  status: string;
  primary_image?: string; // Helper field cho UI nếu cần
}

export interface OrderStatusHistory {
  id: string;
  status: string;
  note: string;
  created_at: string;
}

export interface Order {
  id: string;
  order_number: string;
  status: 'pending' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled' | 'refunded';
  payment_status: 'pending' | 'paid' | 'failed' | 'refunded';
  
  subtotal: string;
  shipping_cost: string;
  discount_amount: string;
  tax_amount: string;
  total: string;
  
  // --- Thông tin giao hàng ---
  shipping_name: string;
  shipping_phone: string;
  shipping_address: string;
  shipping_province: string; // Tỉnh/Thành phố
  shipping_ward: string;     // Phường/Xã
  shipping_country: string;
  shipping_postal_code: string;
  
  // --- Thông tin thanh toán (Billing) ---
  billing_name?: string;
  billing_phone?: string;
  billing_address?: string;
  billing_province?: string;
  billing_ward?: string;
  billing_country?: string;
  billing_postal_code?: string;
  
  customer_note?: string;
  items: OrderItem[];
  status_history: OrderStatusHistory[];
  created_at: string;
}

// Interface dùng cho Payload gửi lên API
export interface CreateOrderPayload {
  shipping_name: string;
  shipping_phone: string;
  shipping_address: string;
  shipping_province: string;
  shipping_ward: string;
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
  billing_province?: string;
  billing_ward?: string;
  billing_country?: string;
  billing_postal_code?: string;
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
  status: string;
}

// ==========================================
// Review Types
// ==========================================

export interface Review {
  id: string;
  user: {
    full_name: string;
    avatar?: string;
  };
  rating: number;
  comment: string;
  created_at: string;
}
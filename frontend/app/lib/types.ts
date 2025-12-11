// User types
export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone: string;
  avatar: string | null;
  is_vendor: boolean;
  date_joined: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

// Product types
export interface Category {
  id: string;
  name: string;
  slug: string;
  description: string;
  image: string | null;
  icon: string;
  parent: string | null;
  children?: Category[];
  product_count?: number;
}

export interface Brand {
  id: string;
  name: string;
  slug: string;
  logo: string | null;
  description: string;
}

export interface ProductImage {
  id: string;
  image: string;
  alt_text: string;
  is_primary: boolean;
  order: number;
}

export interface ProductVariant {
  id: string;
  sku: string;
  name: string;
  price: Money | null;
  compare_price: Money | null;
  image: ProductImage | null;
  is_active: boolean;
  inventory?: {
    available_quantity: number;
    is_in_stock: boolean;
  };
}

export interface Product {
  id: string;
  name: string;
  slug: string;
  sku: string | null;
  description: string;
  short_description: string;
  price: Money;
  compare_price: Money | null;
  is_on_sale: boolean;
  discount_percentage: number;
  status: "draft" | "pending" | "published" | "rejected" | "archived";
  is_featured: boolean;
  is_digital: boolean;
  meta_title: string;
  meta_description: string;
  rating: number;
  review_count: number;
  sold_count: number;
  view_count: number;
  vendor: VendorSummary;
  category: Category | null;
  brand: Brand | null;
  images: ProductImage[];
  variants: ProductVariant[];
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface ProductListItem {
  id: string;
  name: string;
  slug: string;
  price: Money;
  compare_price: Money | null;
  is_on_sale: boolean;
  discount_percentage: number;
  rating: number;
  review_count: number;
  sold_count: number;
  vendor: VendorSummary;
  category: { id: string; name: string; slug: string } | null;
  primary_image: ProductImage | null;
}

export interface Money {
  amount: string;
  currency: string;
}

// Vendor types
export interface VendorSummary {
  id: string;
  shop_name: string;
  slug: string;
  logo: string | null;
  rating: number;
}

export interface Vendor extends VendorSummary {
  description: string;
  banner: string | null;
  business_email: string;
  address: string;
  city: string;
  state: string;
  country: string;
  is_featured: boolean;
  total_sales: number;
  total_products: number;
  created_at: string;
}

// Cart types
export interface CartItem {
  id: string;
  product: ProductListItem;
  variant: ProductVariant | null;
  quantity: number;
  unit_price: Money;
  total_price: Money;
}

export interface Cart {
  id: string;
  items: CartItem[];
  subtotal: Money;
  item_count: number;
  created_at: string;
  updated_at: string;
}

// Order types
export interface OrderItem {
  id: string;
  product_name: string;
  product_slug: string;
  variant_name: string | null;
  sku: string | null;
  quantity: number;
  unit_price: Money;
  total_price: Money;
  product_image: string | null;
}

export interface Order {
  id: string;
  order_number: string;
  status: OrderStatus;
  payment_status: PaymentStatus;
  items: OrderItem[];
  subtotal: Money;
  shipping_fee: Money;
  discount: Money;
  total: Money;
  shipping_address: ShippingAddress;
  notes: string;
  created_at: string;
  confirmed_at: string | null;
  shipped_at: string | null;
  delivered_at: string | null;
}

export type OrderStatus =
  | "pending"
  | "confirmed"
  | "processing"
  | "shipped"
  | "delivered"
  | "cancelled";

export type PaymentStatus = "pending" | "paid" | "failed" | "refunded";

export interface ShippingAddress {
  id: string;
  full_name: string;
  phone: string;
  address_line1: string;
  address_line2: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  is_default: boolean;
}

// Review types
export interface Review {
  id: string;
  user: {
    id: string;
    full_name: string;
    avatar: string | null;
  };
  rating: number;
  title: string;
  comment: string;
  images: { id: string; image: string }[];
  is_verified_purchase: boolean;
  helpful_count: number;
  created_at: string;
}

// Coupon types
export interface Coupon {
  id: string;
  code: string;
  discount_type: "percentage" | "fixed";
  discount_value: number;
  minimum_purchase: Money | null;
  maximum_discount: Money | null;
  valid_from: string;
  valid_to: string;
}

// Pagination
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// API Response
export interface ApiError {
  detail?: string;
  message?: string;
  errors?: Record<string, string[]>;
}

/**
 * Application Constants
 * Centralized definitions for status mappings, configurations, and shared values
 */

// ==========================================
// Order Status Mapping
// ==========================================

export const ORDER_STATUS = {
  pending: { label: "Chờ xác nhận", color: "yellow", bgClass: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400" },
  confirmed: { label: "Đã xác nhận", color: "blue", bgClass: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400" },
  processing: { label: "Đang xử lý", color: "indigo", bgClass: "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400" },
  shipped: { label: "Đang giao", color: "purple", bgClass: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400" },
  delivered: { label: "Đã giao", color: "green", bgClass: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" },
  cancelled: { label: "Đã hủy", color: "red", bgClass: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" },
  refunded: { label: "Hoàn tiền", color: "gray", bgClass: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400" },
} as const;

export type OrderStatusKey = keyof typeof ORDER_STATUS;

// ==========================================
// Payment Status Mapping
// ==========================================

export const PAYMENT_STATUS = {
  pending: { label: "Chờ thanh toán", color: "yellow", bgClass: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400" },
  paid: { label: "Đã thanh toán", color: "green", bgClass: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" },
  failed: { label: "Thất bại", color: "red", bgClass: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" },
  refunded: { label: "Đã hoàn tiền", color: "gray", bgClass: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400" },
} as const;

export type PaymentStatusKey = keyof typeof PAYMENT_STATUS;

// ==========================================
// Vendor Status Mapping
// ==========================================

export const VENDOR_STATUS = {
  pending: { label: "Chờ duyệt", color: "yellow", bgClass: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400" },
  active: { label: "Hoạt động", color: "green", bgClass: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" },
  suspended: { label: "Tạm ngưng", color: "red", bgClass: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" },
  rejected: { label: "Từ chối", color: "gray", bgClass: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400" },
} as const;

export type VendorStatusKey = keyof typeof VENDOR_STATUS;

// ==========================================
// File Upload Constraints
// ==========================================

export const FILE_UPLOAD = {
  MAX_SIZE: 5 * 1024 * 1024, // 5MB in bytes
  MAX_SIZE_DISPLAY: "5MB",
  ALLOWED_IMAGE_TYPES: ["image/jpeg", "image/png", "image/webp", "image/gif"],
  ALLOWED_IMAGE_EXTENSIONS: [".jpg", ".jpeg", ".png", ".webp", ".gif"],
  MAX_IMAGES_PER_PRODUCT: 10,
} as const;

// ==========================================
// Address Field Mapping (FE <-> BE)
// ==========================================

/**
 * Address field naming conventions:
 * 
 * Backend Address Model (apps/users/models.py):
 *   - city: Tỉnh/Thành phố
 *   - state: Phường/Xã/Quận/Huyện
 *   - street_address: Số nhà, tên đường
 * 
 * Backend Order Model (apps/orders/models.py):
 *   - shipping_province: Tỉnh/Thành phố
 *   - shipping_ward: Phường/Xã
 *   - shipping_address: Số nhà, tên đường
 * 
 * Frontend Form Fields:
 *   - province: Tỉnh/Thành phố (maps to city or shipping_province)
 *   - ward: Phường/Xã (maps to state or shipping_ward)
 *   - address: Số nhà, tên đường
 */

export const ADDRESS_FIELDS = {
  // Mapping from UI labels to Address model fields
  UI_TO_ADDRESS: {
    province: "city",
    ward: "state",
    address: "street_address",
  },
  // Mapping from UI labels to Order model fields
  UI_TO_ORDER: {
    province: "shipping_province",
    ward: "shipping_ward",
    address: "shipping_address",
  },
} as const;

// ==========================================
// Helper Functions
// ==========================================

/**
 * Get order status display info
 */
export function getOrderStatusInfo(status: string) {
  return ORDER_STATUS[status as OrderStatusKey] || {
    label: status,
    color: "gray",
    bgClass: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400",
  };
}

/**
 * Get payment status display info
 */
export function getPaymentStatusInfo(status: string) {
  return PAYMENT_STATUS[status as PaymentStatusKey] || {
    label: status,
    color: "gray",
    bgClass: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400",
  };
}

/**
 * Validate file for upload
 * Returns error message if invalid, null if valid
 */
export function validateUploadFile(file: File): string | null {
  if (file.size > FILE_UPLOAD.MAX_SIZE) {
    return `File "${file.name}" vượt quá ${FILE_UPLOAD.MAX_SIZE_DISPLAY}`;
  }
  
  const allowedTypes: readonly string[] = FILE_UPLOAD.ALLOWED_IMAGE_TYPES;
  if (!allowedTypes.includes(file.type)) {
    return `File "${file.name}" không phải định dạng ảnh hợp lệ (chỉ chấp nhận JPG, PNG, WebP, GIF)`;
  }
  
  return null;
}

/**
 * Validate multiple files for upload
 * Returns array of error messages, empty if all valid
 */
export function validateUploadFiles(files: File[]): string[] {
  const errors: string[] = [];
  
  if (files.length > FILE_UPLOAD.MAX_IMAGES_PER_PRODUCT) {
    errors.push(`Chỉ được tải tối đa ${FILE_UPLOAD.MAX_IMAGES_PER_PRODUCT} ảnh`);
  }
  
  files.forEach((file) => {
    const error = validateUploadFile(file);
    if (error) errors.push(error);
  });
  
  return errors;
}

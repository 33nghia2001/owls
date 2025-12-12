import { z } from "zod";

// ============================================
// Common validation patterns
// ============================================

const phoneRegex = /^(\+84|84|0)?[1-9]\d{8}$/;
const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;

// ============================================
// Authentication Schemas
// ============================================

export const loginSchema = z.object({
  email: z
    .string()
    .min(1, "Email không được để trống")
    .email("Email không hợp lệ"),
  password: z
    .string()
    .min(1, "Mật khẩu không được để trống")
    .min(6, "Mật khẩu phải có ít nhất 6 ký tự"),
  remember: z.boolean().optional(),
});

export const registerSchema = z
  .object({
    first_name: z
      .string()
      .min(1, "Tên không được để trống")
      .max(50, "Tên không quá 50 ký tự"),
    last_name: z
      .string()
      .min(1, "Họ không được để trống")
      .max(50, "Họ không quá 50 ký tự"),
    email: z
      .string()
      .min(1, "Email không được để trống")
      .email("Email không hợp lệ"),
    phone: z
      .string()
      .optional()
      .refine(
        (val) => !val || phoneRegex.test(val.replace(/\s/g, "")),
        "Số điện thoại không hợp lệ"
      ),
    password: z
      .string()
      .min(8, "Mật khẩu phải có ít nhất 8 ký tự")
      .regex(
        passwordRegex,
        "Mật khẩu phải chứa chữ hoa, chữ thường và số"
      ),
    password_confirm: z.string().min(1, "Vui lòng xác nhận mật khẩu"),
    terms: z
      .boolean()
      .refine((val) => val === true, "Bạn phải đồng ý với điều khoản sử dụng"),
  })
  .refine((data) => data.password === data.password_confirm, {
    message: "Mật khẩu xác nhận không khớp",
    path: ["password_confirm"],
  });

export const forgotPasswordSchema = z.object({
  email: z
    .string()
    .min(1, "Email không được để trống")
    .email("Email không hợp lệ"),
});

export const resetPasswordSchema = z
  .object({
    password: z
      .string()
      .min(8, "Mật khẩu phải có ít nhất 8 ký tự")
      .regex(passwordRegex, "Mật khẩu phải chứa chữ hoa, chữ thường và số"),
    password_confirm: z.string().min(1, "Vui lòng xác nhận mật khẩu"),
  })
  .refine((data) => data.password === data.password_confirm, {
    message: "Mật khẩu xác nhận không khớp",
    path: ["password_confirm"],
  });

// ============================================
// Checkout Schemas
// ============================================

export const shippingAddressSchema = z.object({
  full_name: z
    .string()
    .min(1, "Họ tên không được để trống")
    .max(100, "Họ tên không quá 100 ký tự"),
  phone: z
    .string()
    .min(1, "Số điện thoại không được để trống")
    .refine(
      (val) => phoneRegex.test(val.replace(/\s/g, "")),
      "Số điện thoại không hợp lệ"
    ),
  address: z
    .string()
    .min(1, "Địa chỉ không được để trống")
    .max(200, "Địa chỉ không quá 200 ký tự"),
  city: z
    .string()
    .min(1, "Tỉnh/Thành phố không được để trống"),
  // Đã xóa district theo yêu cầu
  ward: z
    .string()
    .min(1, "Phường/Xã không được để trống"),
  note: z
    .string()
    .max(500, "Ghi chú không quá 500 ký tự")
    .optional(),
});

export const checkoutSchema = shippingAddressSchema.extend({
  payment_method: z
    .enum(["cod", "vnpay", "stripe"])
    .catch("cod"),
  coupon_code: z.string().optional(),
  // Guest checkout email (optional - only required when not logged in)
  email: z
    .string()
    .email("Email không hợp lệ")
    .optional(),
});

// ============================================
// Profile Schemas
// ============================================

export const updateProfileSchema = z.object({
  first_name: z
    .string()
    .min(1, "Tên không được để trống")
    .max(50, "Tên không quá 50 ký tự"),
  last_name: z
    .string()
    .min(1, "Họ không được để trống")
    .max(50, "Họ không quá 50 ký tự"),
  phone: z
    .string()
    .optional()
    .refine(
      (val) => !val || phoneRegex.test(val.replace(/\s/g, "")),
      "Số điện thoại không hợp lệ"
    ),
});

export const changePasswordSchema = z
  .object({
    current_password: z.string().min(1, "Vui lòng nhập mật khẩu hiện tại"),
    new_password: z
      .string()
      .min(8, "Mật khẩu mới phải có ít nhất 8 ký tự")
      .regex(passwordRegex, "Mật khẩu phải chứa chữ hoa, chữ thường và số"),
    confirm_password: z.string().min(1, "Vui lòng xác nhận mật khẩu mới"),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "Mật khẩu xác nhận không khớp",
    path: ["confirm_password"],
  });

// ============================================
// Review Schema
// ============================================

export const reviewSchema = z.object({
  rating: z
    .number()
    .min(1, "Vui lòng chọn số sao")
    .max(5, "Đánh giá tối đa 5 sao"),
  title: z
    .string()
    .max(100, "Tiêu đề không quá 100 ký tự")
    .optional(),
  comment: z
    .string()
    .min(10, "Nhận xét phải có ít nhất 10 ký tự")
    .max(1000, "Nhận xét không quá 1000 ký tự"),
});

// ============================================
// Type exports
// ============================================

export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;
export type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;
export type ShippingAddressFormData = z.infer<typeof shippingAddressSchema>;
export type CheckoutFormData = z.infer<typeof checkoutSchema>;
export type UpdateProfileFormData = z.infer<typeof updateProfileSchema>;
export type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;
export type ReviewFormData = z.infer<typeof reviewSchema>;
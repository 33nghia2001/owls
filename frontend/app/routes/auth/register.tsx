import { Link, useNavigate } from "react-router";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Eye, EyeOff, User, Mail, Phone, Lock, AlertCircle, Check, X } from "lucide-react";
import { Button } from "~/components/ui";
import { useAuthStore } from "~/lib/stores";
import { registerSchema, type RegisterFormData } from "~/lib/validations";
import { cn } from "~/lib/utils";
import toast from "react-hot-toast";

export function meta() {
  return [
    { title: "Đăng ký - OWLS Marketplace" },
    { name: "description", content: "Tạo tài khoản OWLS mới" },
  ];
}

export default function RegisterPage() {
  const navigate = useNavigate();
  const { register: registerUser, isLoading } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      first_name: "",
      last_name: "",
      email: "",
      phone: "",
      password: "",
      password_confirm: "",
      terms: false,
    },
  });

  // Watch password for real-time validation UI
  const password = watch("password", "");
  
  const passwordRequirements = [
    { text: "Ít nhất 8 ký tự", met: password.length >= 8 },
    { text: "Chứa chữ hoa (A-Z)", met: /[A-Z]/.test(password) },
    { text: "Chứa chữ thường (a-z)", met: /[a-z]/.test(password) },
    { text: "Chứa ít nhất 1 số", met: /\d/.test(password) },
  ];

  const onSubmit = async (data: RegisterFormData) => {
    setServerError(null);
    
    // Format phone number
    let phone = data.phone || "";
    if (phone) {
      phone = phone.replace(/\D/g, "");
      if (phone.startsWith("0")) {
        phone = "+84" + phone.slice(1);
      } else if (!phone.startsWith("+")) {
        phone = "+84" + phone;
      }
    }
    
    try {
      await registerUser({
        email: data.email,
        password: data.password,
        password_confirm: data.password_confirm,
        first_name: data.first_name,
        last_name: data.last_name,
        phone,
      });
      
      toast.success("Đăng ký thành công!");
      navigate("/");
    } catch (error: any) {
      console.error("Register error:", error.response?.data);
      const errorData = error.response?.data;
      
      if (errorData) {
        const errors: string[] = [];
        if (errorData.email) errors.push(`Email: ${Array.isArray(errorData.email) ? errorData.email[0] : errorData.email}`);
        if (errorData.password) errors.push(`Mật khẩu: ${Array.isArray(errorData.password) ? errorData.password[0] : errorData.password}`);
        if (errorData.phone) errors.push(`SĐT: ${Array.isArray(errorData.phone) ? errorData.phone[0] : errorData.phone}`);
        if (errorData.non_field_errors) errors.push(Array.isArray(errorData.non_field_errors) ? errorData.non_field_errors[0] : errorData.non_field_errors);
        if (errorData.detail) errors.push(errorData.detail);
        
        if (errors.length > 0) {
          setServerError(errors.join(". "));
          return;
        }
      }
      
      setServerError("Đăng ký thất bại. Vui lòng thử lại.");
    }
  };

  const inputClasses = (hasError: boolean) =>
    cn(
      "mt-1 h-11 w-full rounded-lg border px-3 pl-10 text-sm transition-colors",
      "focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 focus:outline-none",
      "dark:bg-gray-900 dark:text-gray-100",
      hasError
        ? "border-red-500 dark:border-red-500"
        : "border-gray-200 dark:border-gray-800"
    );

  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm dark:border-gray-800 dark:bg-gray-950">
          {/* Header */}
          <div className="mb-8 text-center">
            <Link to="/" className="mb-4 inline-block">
              <span className="text-3xl font-bold text-orange-500">🦉 OWLS</span>
            </Link>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Tạo tài khoản
            </h1>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              Đăng ký để mua sắm và nhận ưu đãi
            </p>
          </div>

          {/* Server Error */}
          {serverError && (
            <div className="mb-6 flex items-start gap-2 rounded-lg bg-red-50 p-4 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
              <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
              <span>{serverError}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Name Fields */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Họ
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                  <input
                    {...register("last_name")}
                    placeholder="Nguyễn"
                    className={inputClasses(!!errors.last_name)}
                  />
                </div>
                {errors.last_name && (
                  <p className="mt-1 text-xs text-red-500">{errors.last_name.message}</p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Tên
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                  <input
                    {...register("first_name")}
                    placeholder="Văn A"
                    className={inputClasses(!!errors.first_name)}
                  />
                </div>
                {errors.first_name && (
                  <p className="mt-1 text-xs text-red-500">{errors.first_name.message}</p>
                )}
              </div>
            </div>

            {/* Email Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  {...register("email")}
                  type="email"
                  placeholder="email@example.com"
                  autoComplete="email"
                  className={inputClasses(!!errors.email)}
                />
              </div>
              {errors.email && (
                <p className="mt-1 text-sm text-red-500">{errors.email.message}</p>
              )}
            </div>

            {/* Phone Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Số điện thoại <span className="text-gray-400 font-normal">(không bắt buộc)</span>
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  {...register("phone")}
                  type="tel"
                  placeholder="0901234567"
                  inputMode="numeric"
                  className={inputClasses(!!errors.phone)}
                  onKeyDown={(e) => {
                    if ([8, 46, 9, 27, 13, 37, 38, 39, 40].includes(e.keyCode)) return;
                    if ((e.ctrlKey || e.metaKey) && [65, 67, 86, 88].includes(e.keyCode)) return;
                    if (!/[0-9]/.test(e.key)) e.preventDefault();
                  }}
                />
              </div>
              {errors.phone && (
                <p className="mt-1 text-sm text-red-500">{errors.phone.message}</p>
              )}
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Mật khẩu
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  {...register("password")}
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  autoComplete="new-password"
                  className={inputClasses(!!errors.password)}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-500">{errors.password.message}</p>
              )}
            </div>

            {/* Confirm Password Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Xác nhận mật khẩu
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  {...register("password_confirm")}
                  type={showConfirmPassword ? "text" : "password"}
                  placeholder="••••••••"
                  autoComplete="new-password"
                  className={inputClasses(!!errors.password_confirm)}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
              {errors.password_confirm && (
                <p className="mt-1 text-sm text-red-500">{errors.password_confirm.message}</p>
              )}
            </div>

            {/* Password Requirements */}
            <div className="rounded-lg bg-gray-50 p-3 dark:bg-gray-900">
              <p className="mb-2 text-xs font-medium text-gray-700 dark:text-gray-300">
                Yêu cầu mật khẩu:
              </p>
              <ul className="space-y-1">
                {passwordRequirements.map((req, i) => (
                  <li
                    key={i}
                    className={cn(
                      "flex items-center gap-2 text-xs transition-colors",
                      req.met
                        ? "text-green-600 dark:text-green-400"
                        : "text-gray-500 dark:text-gray-400"
                    )}
                  >
                    {req.met ? (
                      <Check className="h-3 w-3" />
                    ) : (
                      <X className="h-3 w-3" />
                    )}
                    {req.text}
                  </li>
                ))}
              </ul>
            </div>

            {/* Terms Checkbox */}
            <div>
              <label className="flex items-start gap-3 cursor-pointer">
                <input
                  {...register("terms")}
                  type="checkbox"
                  className="mt-1 h-4 w-4 rounded border-gray-300 text-orange-500 focus:ring-orange-500"
                />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Tôi đồng ý với{" "}
                  <Link to="/terms" className="text-orange-500 hover:underline">
                    Điều khoản sử dụng
                  </Link>{" "}
                  và{" "}
                  <Link to="/privacy" className="text-orange-500 hover:underline">
                    Chính sách bảo mật
                  </Link>
                </span>
              </label>
              {errors.terms && (
                <p className="mt-1 text-sm text-red-500">{errors.terms.message}</p>
              )}
            </div>

            {/* Submit Button */}
            <Button 
              type="submit" 
              className="w-full" 
              isLoading={isSubmitting || isLoading}
            >
              Đăng ký
            </Button>
          </form>

          {/* Login Link */}
          <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
            Đã có tài khoản?{" "}
            <Link
              to="/login"
              className="font-medium text-orange-500 hover:text-orange-600"
            >
              Đăng nhập
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

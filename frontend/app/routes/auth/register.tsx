import { Link, Form, useActionData, useNavigation } from "react-router";
import { useState } from "react";
import { Eye, EyeOff, Check } from "lucide-react";
import { Button, Input } from "~/components/ui";

export function meta() {
  return [
    { title: "Đăng ký - OWLS Marketplace" },
    { name: "description", content: "Tạo tài khoản OWLS mới" },
  ];
}

export async function clientAction({ request }: { request: Request }) {
  const formData = await request.formData();
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;
  const password_confirm = formData.get("password_confirm") as string;
  const first_name = formData.get("first_name") as string;
  const last_name = formData.get("last_name") as string;
  let phone = formData.get("phone") as string;
  const terms = formData.get("terms");

  // Format phone number to international format (+84)
  if (phone) {
    phone = phone.replace(/\D/g, ""); // Remove non-digits
    if (phone.startsWith("0")) {
      phone = "+84" + phone.slice(1); // Convert 0xxx to +84xxx
    } else if (!phone.startsWith("+")) {
      phone = "+84" + phone;
    }
  }

  // Validation
  if (!email || !password || !password_confirm || !first_name || !last_name) {
    return { error: "Vui lòng nhập đầy đủ thông tin" };
  }

  if (password !== password_confirm) {
    return { error: "Mật khẩu xác nhận không khớp" };
  }

  if (password.length < 8) {
    return { error: "Mật khẩu phải có ít nhất 8 ký tự" };
  }

  if (!terms) {
    return { error: "Vui lòng đồng ý với điều khoản sử dụng" };
  }

  try {
    const { useAuthStore } = await import("~/lib/stores");
    await useAuthStore.getState().register({
      email,
      password,
      password_confirm,
      first_name,
      last_name,
      phone,
    });
    
    window.location.href = "/";
    return { success: true };
  } catch (error: any) {
    console.log("Register error:", error.response?.data);
    const data = error.response?.data;
    
    if (data) {
      // Collect all validation errors
      const errors: string[] = [];
      
      if (data.email) {
        errors.push(`Email: ${Array.isArray(data.email) ? data.email[0] : data.email}`);
      }
      if (data.password) {
        errors.push(`Mật khẩu: ${Array.isArray(data.password) ? data.password[0] : data.password}`);
      }
      if (data.password_confirm) {
        errors.push(`Xác nhận mật khẩu: ${Array.isArray(data.password_confirm) ? data.password_confirm[0] : data.password_confirm}`);
      }
      if (data.first_name) {
        errors.push(`Họ: ${Array.isArray(data.first_name) ? data.first_name[0] : data.first_name}`);
      }
      if (data.last_name) {
        errors.push(`Tên: ${Array.isArray(data.last_name) ? data.last_name[0] : data.last_name}`);
      }
      if (data.phone) {
        errors.push(`Số điện thoại: ${Array.isArray(data.phone) ? data.phone[0] : data.phone}`);
      }
      if (data.non_field_errors) {
        errors.push(Array.isArray(data.non_field_errors) ? data.non_field_errors[0] : data.non_field_errors);
      }
      if (data.detail) {
        errors.push(data.detail);
      }
      
      if (errors.length > 0) {
        return { error: errors.join(". ") };
      }
    }
    
    return { error: "Đăng ký thất bại. Vui lòng thử lại." };
  }
}

export default function RegisterPage() {
  const actionData = useActionData<typeof clientAction>();
  const navigation = useNavigation();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  const isSubmitting = navigation.state === "submitting";

  const passwordRequirements = [
    "Ít nhất 8 ký tự",
    "Chứa chữ hoa và chữ thường",
    "Chứa ít nhất 1 số",
  ];

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

          {/* Error message */}
          {actionData?.error && (
            <div className="mb-6 rounded-lg bg-red-50 p-4 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
              {actionData.error}
            </div>
          )}

          {/* Form */}
          <Form method="post" className="space-y-5">
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Họ"
                name="last_name"
                placeholder="Nguyễn"
                required
              />
              <Input
                label="Tên"
                name="first_name"
                placeholder="Văn A"
                required
              />
            </div>

            <Input
              label="Email"
              name="email"
              type="email"
              placeholder="email@example.com"
              required
              autoComplete="email"
            />

            <Input
              label="Số điện thoại"
              name="phone"
              type="tel"
              placeholder="0901234567"
              pattern="[0-9]*"
              inputMode="numeric"
              onKeyDown={(e) => {
                // Allow: backspace, delete, tab, escape, enter, arrows
                if ([8, 46, 9, 27, 13, 37, 38, 39, 40].includes(e.keyCode)) {
                  return;
                }
                // Allow: Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
                if ((e.ctrlKey || e.metaKey) && [65, 67, 86, 88].includes(e.keyCode)) {
                  return;
                }
                // Block if not a number
                if (!/[0-9]/.test(e.key)) {
                  e.preventDefault();
                }
              }}
              onChange={(e) => {
                // Remove any non-numeric characters on paste/input
                e.target.value = e.target.value.replace(/[^0-9]/g, '');
              }}
            />

            <div className="relative">
              <Input
                label="Mật khẩu"
                name="password"
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                required
                autoComplete="new-password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-[38px] text-gray-500 hover:text-gray-700"
              >
                {showPassword ? (
                  <EyeOff className="h-5 w-5" />
                ) : (
                  <Eye className="h-5 w-5" />
                )}
              </button>
            </div>

            <div className="relative">
              <Input
                label="Xác nhận mật khẩu"
                name="password_confirm"
                type={showConfirmPassword ? "text" : "password"}
                placeholder="••••••••"
                required
                autoComplete="new-password"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-[38px] text-gray-500 hover:text-gray-700"
              >
                {showConfirmPassword ? (
                  <EyeOff className="h-5 w-5" />
                ) : (
                  <Eye className="h-5 w-5" />
                )}
              </button>
            </div>

            {/* Password requirements */}
            <div className="rounded-lg bg-gray-50 p-3 dark:bg-gray-900">
              <p className="mb-2 text-xs font-medium text-gray-700 dark:text-gray-300">
                Yêu cầu mật khẩu:
              </p>
              <ul className="space-y-1">
                {passwordRequirements.map((req, i) => (
                  <li
                    key={i}
                    className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400"
                  >
                    <Check className="h-3 w-3 text-gray-400" />
                    {req}
                  </li>
                ))}
              </ul>
            </div>

            <label className="flex items-start gap-3">
              <input
                type="checkbox"
                name="terms"
                className="mt-1 h-4 w-4 rounded border-gray-300 text-orange-500 focus:ring-orange-500"
                required
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

            <Button type="submit" className="w-full" isLoading={isSubmitting}>
              Đăng ký
            </Button>
          </Form>

          {/* Login link */}
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

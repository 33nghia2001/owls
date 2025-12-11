import { Link, Form, useActionData, useNavigation, type ActionFunctionArgs } from "react-router";
import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { Button, Input } from "~/components/ui";
import { authApi } from "~/lib/services";
import { useAuthStore } from "~/lib/stores";

export function meta() {
  return [
    { title: "Đăng nhập - OWLS Marketplace" },
    { name: "description", content: "Đăng nhập vào tài khoản OWLS của bạn" },
  ];
}

export async function action({ request }: ActionFunctionArgs) {
  const formData = await request.formData();
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;

  if (!email || !password) {
    return { error: "Vui lòng nhập đầy đủ thông tin" };
  }

  try {
    await authApi.login(email, password);
    return { success: true };
  } catch (error: any) {
    const message = error.response?.data?.detail || "Đăng nhập thất bại";
    return { error: message };
  }
}

export async function clientAction({ request }: { request: Request }) {
  const formData = await request.formData();
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;

  if (!email || !password) {
    return { error: "Vui lòng nhập đầy đủ thông tin" };
  }

  try {
    const { useAuthStore } = await import("~/lib/stores");
    await useAuthStore.getState().login(email, password);
    
    // Redirect to home or previous page
    window.location.href = "/";
    return { success: true };
  } catch (error: any) {
    const message = error.response?.data?.detail || "Email hoặc mật khẩu không đúng";
    return { error: message };
  }
}

export default function LoginPage() {
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const [showPassword, setShowPassword] = useState(false);
  
  const isSubmitting = navigation.state === "submitting";

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
              Đăng nhập
            </h1>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              Chào mừng bạn quay trở lại
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
            <Input
              label="Email"
              name="email"
              type="email"
              placeholder="email@example.com"
              required
              autoComplete="email"
            />

            <div className="relative">
              <Input
                label="Mật khẩu"
                name="password"
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                required
                autoComplete="current-password"
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

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  name="remember"
                  className="h-4 w-4 rounded border-gray-300 text-orange-500 focus:ring-orange-500"
                />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Ghi nhớ đăng nhập
                </span>
              </label>
              <Link
                to="/forgot-password"
                className="text-sm font-medium text-orange-500 hover:text-orange-600"
              >
                Quên mật khẩu?
              </Link>
            </div>

            <Button type="submit" className="w-full" isLoading={isSubmitting}>
              Đăng nhập
            </Button>
          </Form>

          {/* Divider */}
          <div className="my-6 flex items-center">
            <div className="flex-1 border-t border-gray-200 dark:border-gray-700" />
            <span className="px-4 text-sm text-gray-500">hoặc</span>
            <div className="flex-1 border-t border-gray-200 dark:border-gray-700" />
          </div>

          {/* Social login */}
          <div className="grid gap-3">
            <button
              type="button"
              className="flex w-full items-center justify-center gap-3 rounded-lg border border-gray-300 bg-white py-2.5 text-sm font-medium hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:hover:bg-gray-800"
            >
              <svg className="h-5 w-5" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Đăng nhập với Google
            </button>
          </div>

          {/* Register link */}
          <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
            Chưa có tài khoản?{" "}
            <Link
              to="/register"
              className="font-medium text-orange-500 hover:text-orange-600"
            >
              Đăng ký ngay
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

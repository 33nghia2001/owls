import { Link, Form, useActionData, useNavigation, useSearchParams } from "react-router";
import { Button, Input } from "~/components/ui";
import { authApi } from "~/lib/services";
import { Lock, ArrowLeft, CheckCircle, AlertCircle } from "lucide-react";
import { useState } from "react";

export function meta() {
  return [
    { title: "Đặt lại mật khẩu - OWLS Marketplace" },
    { name: "description", content: "Đặt lại mật khẩu tài khoản OWLS" },
  ];
}

export async function clientAction({ request }: { request: Request }) {
  const formData = await request.formData();
  const uid = formData.get("uid") as string;
  const token = formData.get("token") as string;
  const new_password = formData.get("new_password") as string;
  const confirm_password = formData.get("confirm_password") as string;

  // Validate
  if (!uid || !token) {
    return { error: "Liên kết đặt lại mật khẩu không hợp lệ." };
  }

  if (!new_password || new_password.length < 8) {
    return { error: "Mật khẩu phải có ít nhất 8 ký tự." };
  }

  if (new_password !== confirm_password) {
    return { error: "Mật khẩu xác nhận không khớp." };
  }

  try {
    await authApi.resetPassword(uid, token, new_password);
    return { success: true };
  } catch (error: unknown) {
    const err = error as { response?: { data?: { error?: string } } };
    return { 
      error: err.response?.data?.error || "Liên kết đặt lại mật khẩu đã hết hạn hoặc không hợp lệ." 
    };
  }
}

export default function ResetPasswordPage() {
  const actionData = useActionData<typeof clientAction>();
  const navigation = useNavigation();
  const [searchParams] = useSearchParams();
  
  const uid = searchParams.get("uid") || "";
  const token = searchParams.get("token") || "";
  
  const isSubmitting = navigation.state === "submitting";
  const [showPassword, setShowPassword] = useState(false);

  // Invalid link - missing uid or token
  if (!uid || !token) {
    return (
      <div className="flex min-h-[80vh] items-center justify-center px-4 py-12">
        <div className="w-full max-w-md text-center">
          <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm dark:border-gray-800 dark:bg-gray-950">
            <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-red-100 dark:bg-red-900/20">
              <AlertCircle className="h-8 w-8 text-red-600" />
            </div>
            <h1 className="mb-2 text-2xl font-bold text-gray-900 dark:text-gray-100">
              Liên kết không hợp lệ
            </h1>
            <p className="mb-6 text-gray-600 dark:text-gray-400">
              Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.
              Vui lòng yêu cầu một liên kết mới.
            </p>
            <Link to="/auth/forgot-password">
              <Button variant="primary" className="w-full">
                Yêu cầu liên kết mới
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Success state
  if (actionData?.success) {
    return (
      <div className="flex min-h-[80vh] items-center justify-center px-4 py-12">
        <div className="w-full max-w-md text-center">
          <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm dark:border-gray-800 dark:bg-gray-950">
            <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/20">
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
            <h1 className="mb-2 text-2xl font-bold text-gray-900 dark:text-gray-100">
              Đặt lại mật khẩu thành công!
            </h1>
            <p className="mb-6 text-gray-600 dark:text-gray-400">
              Mật khẩu của bạn đã được cập nhật. Bạn có thể đăng nhập với mật khẩu mới.
            </p>
            <Link to="/auth/login">
              <Button variant="primary" className="w-full">
                Đăng nhập ngay
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm dark:border-gray-800 dark:bg-gray-950">
          {/* Header */}
          <div className="mb-8 text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-orange-100 dark:bg-orange-900/20">
              <Lock className="h-8 w-8 text-orange-500" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Đặt lại mật khẩu
            </h1>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              Nhập mật khẩu mới cho tài khoản của bạn
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
            {/* Hidden fields for uid and token */}
            <input type="hidden" name="uid" value={uid} />
            <input type="hidden" name="token" value={token} />
            
            <Input
              label="Mật khẩu mới"
              name="new_password"
              type={showPassword ? "text" : "password"}
              placeholder="Nhập mật khẩu mới"
              required
              minLength={8}
              autoComplete="new-password"
            />
            
            <Input
              label="Xác nhận mật khẩu"
              name="confirm_password"
              type={showPassword ? "text" : "password"}
              placeholder="Nhập lại mật khẩu mới"
              required
              minLength={8}
              autoComplete="new-password"
            />
            
            <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <input
                type="checkbox"
                checked={showPassword}
                onChange={(e) => setShowPassword(e.target.checked)}
                className="rounded border-gray-300"
              />
              Hiển thị mật khẩu
            </label>

            <Button
              type="submit"
              variant="primary"
              className="w-full"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Đang xử lý..." : "Đặt lại mật khẩu"}
            </Button>
          </Form>

          {/* Back to login */}
          <div className="mt-6 text-center">
            <Link 
              to="/auth/login"
              className="inline-flex items-center text-sm text-orange-500 hover:text-orange-600"
            >
              <ArrowLeft className="mr-1 h-4 w-4" />
              Quay lại đăng nhập
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

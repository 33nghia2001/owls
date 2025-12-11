import { Link, Form, useActionData, useNavigation } from "react-router";
import { Button, Input } from "~/components/ui";
import { authApi } from "~/lib/services";
import { Mail, ArrowLeft, CheckCircle } from "lucide-react";

export function meta() {
  return [
    { title: "Quên mật khẩu - OWLS Marketplace" },
    { name: "description", content: "Khôi phục mật khẩu tài khoản OWLS" },
  ];
}

export async function clientAction({ request }: { request: Request }) {
  const formData = await request.formData();
  const email = formData.get("email") as string;

  if (!email) {
    return { error: "Vui lòng nhập email" };
  }

  try {
    await authApi.forgotPassword(email);
    return { success: true, email };
  } catch (error: any) {
    // Don't reveal if email exists or not for security
    return { success: true, email };
  }
}

export default function ForgotPasswordPage() {
  const actionData = useActionData<typeof clientAction>();
  const navigation = useNavigation();
  
  const isSubmitting = navigation.state === "submitting";

  if (actionData?.success) {
    return (
      <div className="flex min-h-[80vh] items-center justify-center px-4 py-12">
        <div className="w-full max-w-md text-center">
          <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm dark:border-gray-800 dark:bg-gray-950">
            <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/20">
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
            <h1 className="mb-2 text-2xl font-bold text-gray-900 dark:text-gray-100">
              Kiểm tra email
            </h1>
            <p className="mb-6 text-gray-600 dark:text-gray-400">
              Chúng tôi đã gửi hướng dẫn khôi phục mật khẩu đến{" "}
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {actionData.email}
              </span>
            </p>
            <p className="mb-6 text-sm text-gray-500">
              Không nhận được email? Kiểm tra thư mục spam hoặc thử lại với email khác.
            </p>
            <Link to="/login">
              <Button variant="outline" className="w-full">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Quay lại đăng nhập
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
              <Mail className="h-8 w-8 text-orange-500" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Quên mật khẩu?
            </h1>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              Nhập email của bạn và chúng tôi sẽ gửi hướng dẫn khôi phục
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

            <Button type="submit" className="w-full" isLoading={isSubmitting}>
              Gửi hướng dẫn
            </Button>
          </Form>

          {/* Back to login */}
          <div className="mt-6 text-center">
            <Link
              to="/login"
              className="inline-flex items-center text-sm text-gray-600 hover:text-orange-500 dark:text-gray-400"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Quay lại đăng nhập
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

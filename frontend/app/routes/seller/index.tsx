import { Link, useLoaderData, type LoaderFunctionArgs } from "react-router";
import { Package, ShoppingBag, DollarSign, TrendingUp } from "lucide-react";
import { useAuthStore } from "~/lib/stores";
import { useEffect } from "react";

export function meta() {
  return [
    { title: "Seller Dashboard - OWLS" },
    { name: "description", content: "Quản lý cửa hàng của bạn" },
  ];
}

export default function SellerDashboardPage() {
  const { user, checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  if (!user) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <p className="text-gray-600">Vui lòng đăng nhập để truy cập Seller Dashboard.</p>
        <Link
          to="/login"
          className="mt-4 inline-block rounded-lg bg-orange-500 px-4 py-2 text-white transition hover:bg-orange-600"
        >
          Đăng nhập
        </Link>
      </div>
    );
  }

  if (!user.is_vendor) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <p className="text-gray-600">Bạn cần đăng ký làm người bán để truy cập trang này.</p>
        <Link
          to="/account/profile"
          className="mt-4 inline-block rounded-lg bg-orange-500 px-4 py-2 text-white transition hover:bg-orange-600"
        >
          Đăng ký làm người bán
        </Link>
      </div>
    );
  }

  const stats = [
    { label: "Sản phẩm", value: "0", icon: Package, color: "text-blue-600" },
    { label: "Đơn hàng mới", value: "0", icon: ShoppingBag, color: "text-orange-600" },
    { label: "Doanh thu", value: "0 ₫", icon: DollarSign, color: "text-green-600" },
    { label: "Tăng trưởng", value: "+0%", icon: TrendingUp, color: "text-purple-600" },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-6 text-3xl font-bold text-gray-900 dark:text-gray-100">Seller Dashboard</h1>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</p>
                <p className="mt-2 text-2xl font-bold text-gray-900 dark:text-gray-100">{stat.value}</p>
              </div>
              <stat.icon className={`h-10 w-10 ${stat.color}`} />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Link
          to="/seller/products"
          className="group rounded-xl border border-gray-200 bg-white p-6 transition hover:border-orange-500 hover:shadow-lg dark:border-gray-800 dark:bg-gray-900"
        >
          <Package className="h-8 w-8 text-orange-500" />
          <h3 className="mt-3 text-lg font-semibold text-gray-900 dark:text-gray-100">Sản phẩm</h3>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Quản lý kho sản phẩm của bạn</p>
        </Link>

        <Link
          to="/seller/orders"
          className="group rounded-xl border border-gray-200 bg-white p-6 transition hover:border-orange-500 hover:shadow-lg dark:border-gray-800 dark:bg-gray-900"
        >
          <ShoppingBag className="h-8 w-8 text-orange-500" />
          <h3 className="mt-3 text-lg font-semibold text-gray-900 dark:text-gray-100">Đơn hàng</h3>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Xử lý đơn hàng mới</p>
        </Link>

        <Link
          to="/seller/settings"
          className="group rounded-xl border border-gray-200 bg-white p-6 transition hover:border-orange-500 hover:shadow-lg dark:border-gray-800 dark:bg-gray-900"
        >
          <DollarSign className="h-8 w-8 text-orange-500" />
          <h3 className="mt-3 text-lg font-semibold text-gray-900 dark:text-gray-100">Cài đặt</h3>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Thông tin shop & thanh toán</p>
        </Link>
      </div>
    </div>
  );
}

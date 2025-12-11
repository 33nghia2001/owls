import { Link, useLoaderData, type LoaderFunctionArgs } from "react-router";
import { Package, ShoppingBag, DollarSign, TrendingUp, Star, Loader2 } from "lucide-react";
import { useAuthStore } from "~/lib/stores";
import { vendorAnalyticsApi } from "~/lib/services";
import { formatCurrency } from "~/lib/utils";
import { useEffect, useState } from "react";

export function meta() {
  return [
    { title: "Seller Dashboard - OWLS" },
    { name: "description", content: "Quản lý cửa hàng của bạn" },
  ];
}

interface DashboardStats {
  today: {
    orders: number;
    revenue: number;
    products_sold: number;
  };
  this_month: {
    orders: number;
    revenue: number;
    products_sold: number;
  };
  total: {
    products: number;
    total_sales: number;
    rating: number;
  };
}

export default function SellerDashboardPage() {
  const { user, checkAuth } = useAuthStore();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    const fetchStats = async () => {
      if (!user?.is_vendor) return;
      
      try {
        setIsLoading(true);
        const data = await vendorAnalyticsApi.getDashboardStats();
        setStats(data);
      } catch (err: any) {
        console.error("Failed to fetch dashboard stats:", err);
        setError(err.response?.data?.detail || "Không thể tải dữ liệu thống kê");
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, [user?.is_vendor]);

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

  const statsDisplay = [
    { 
      label: "Sản phẩm", 
      value: isLoading ? "..." : (stats?.total.products.toString() || "0"), 
      icon: Package, 
      color: "text-blue-600",
      bg: "bg-blue-50 dark:bg-blue-900/20"
    },
    { 
      label: "Đơn hàng hôm nay", 
      value: isLoading ? "..." : (stats?.today.orders.toString() || "0"), 
      icon: ShoppingBag, 
      color: "text-orange-600",
      bg: "bg-orange-50 dark:bg-orange-900/20"
    },
    { 
      label: "Doanh thu tháng", 
      value: isLoading ? "..." : formatCurrency(stats?.this_month.revenue || 0), 
      icon: DollarSign, 
      color: "text-green-600",
      bg: "bg-green-50 dark:bg-green-900/20"
    },
    { 
      label: "Đánh giá", 
      value: isLoading ? "..." : `${stats?.total.rating?.toFixed(1) || "0"} ⭐`, 
      icon: Star, 
      color: "text-yellow-600",
      bg: "bg-yellow-50 dark:bg-yellow-900/20"
    },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Seller Dashboard</h1>
        {isLoading && <Loader2 className="h-5 w-5 animate-spin text-orange-500" />}
      </div>

      {error && (
        <div className="mb-6 rounded-lg bg-red-50 p-4 text-red-600 dark:bg-red-900/20 dark:text-red-400">
          {error}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statsDisplay.map((stat) => (
          <div
            key={stat.label}
            className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900 transition-all hover:shadow-md"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</p>
                <p className="mt-2 text-2xl font-bold text-gray-900 dark:text-gray-100">{stat.value}</p>
              </div>
              <div className={`rounded-xl p-3 ${stat.bg}`}>
                <stat.icon className={`h-8 w-8 ${stat.color}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Today Summary */}
      {stats && (
        <div className="mt-8 rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">Tổng quan hôm nay</h2>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-lg bg-gray-50 p-4 dark:bg-gray-800">
              <p className="text-sm text-gray-600 dark:text-gray-400">Đơn hàng</p>
              <p className="mt-1 text-xl font-bold text-gray-900 dark:text-gray-100">{stats.today.orders}</p>
            </div>
            <div className="rounded-lg bg-gray-50 p-4 dark:bg-gray-800">
              <p className="text-sm text-gray-600 dark:text-gray-400">Doanh thu</p>
              <p className="mt-1 text-xl font-bold text-green-600">{formatCurrency(stats.today.revenue)}</p>
            </div>
            <div className="rounded-lg bg-gray-50 p-4 dark:bg-gray-800">
              <p className="text-sm text-gray-600 dark:text-gray-400">Sản phẩm bán</p>
              <p className="mt-1 text-xl font-bold text-gray-900 dark:text-gray-100">{stats.today.products_sold}</p>
            </div>
          </div>
        </div>
      )}

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

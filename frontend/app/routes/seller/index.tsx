import { Link, useLoaderData } from "react-router";
import { Package, ShoppingBag, DollarSign, Star, Loader2, AlertTriangle, CheckCircle } from "lucide-react";
import { useAuthStore } from "~/lib/stores";
import { vendorAnalyticsApi, authApi, vendorsApi } from "~/lib/services";
import { formatCurrency } from "~/lib/utils";
import { useEffect, useState } from "react";

export function meta() {
  return [
    { title: "Seller Dashboard - OWLS" },
    { name: "description", content: "Quản lý cửa hàng của bạn" },
  ];
}

interface DashboardStats {
  today: { orders: number; revenue: number; products_sold: number };
  this_month: { orders: number; revenue: number; products_sold: number };
  total: { products: number; total_sales: number; rating: number };
}

// Client Loader: Fetch user & status info
export async function clientLoader() {
  try {
    const user = await authApi.getProfile();
    let stats = null;
    let vendorProfile = null;

    if (user.is_vendor) {
      try {
        stats = await vendorAnalyticsApi.getDashboardStats();
      } catch {
        // Ignore stats error
      }
    } else {
      // Nếu chưa phải vendor, thử lấy thông tin hồ sơ (để check pending)
      try {
        vendorProfile = await vendorsApi.getCurrentVendor();
      } catch {
        // 404 means no profile yet
      }
    }

    return { user, stats, vendorProfile };
  } catch (error: any) {
    if (error.response?.status === 401) {
      window.location.href = "/auth/login";
      return null;
    }
    throw error;
  }
}

export default function SellerDashboardPage() {
  const loaderData = useLoaderData<typeof clientLoader>();
  
  // Dữ liệu từ loader
  const user = loaderData?.user;
  const stats = loaderData?.stats as DashboardStats | null;
  const vendorProfile = loaderData?.vendorProfile;

  // Nếu chưa đăng nhập hoặc lỗi (đã xử lý ở loader redirect)
  if (!user) return null;

  // --- TRƯỜNG HỢP 1: CHƯA LÀ VENDOR ---
  if (!user.is_vendor) {
    // 1.1: Đã đăng ký nhưng đang chờ duyệt
    if (vendorProfile && vendorProfile.status === 'pending') {
      return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 px-4 dark:bg-[#050505]">
          <div className="max-w-md text-center rounded-2xl bg-white p-8 shadow-sm border border-gray-200 dark:bg-gray-900 dark:border-gray-800">
            <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-yellow-100 text-yellow-600">
              <Loader2 className="h-8 w-8 animate-spin" />
            </div>
            <h2 className="mb-2 text-2xl font-bold text-gray-900 dark:text-white">
              Hồ sơ đang chờ duyệt
            </h2>
            <p className="mb-6 text-gray-600 dark:text-gray-400">
              Cảm ơn bạn đã đăng ký bán hàng. Đội ngũ OWLS đang xem xét hồ sơ của 
              <span className="font-bold text-gray-900 dark:text-white"> {vendorProfile.shop_name}</span>.
              <br />Quá trình này thường mất 1-3 ngày làm việc.
            </p>
            <Link to="/" className="text-orange-600 hover:underline">
              Về trang chủ
            </Link>
          </div>
        </div>
      );
    }

    // 1.2: Bị từ chối
    if (vendorProfile && vendorProfile.status === 'rejected') {
      return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 px-4 dark:bg-[#050505]">
          <div className="max-w-md text-center rounded-2xl bg-white p-8 shadow-sm border border-gray-200 dark:bg-gray-900 dark:border-gray-800">
            <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-red-100 text-red-600">
              <AlertTriangle className="h-8 w-8" />
            </div>
            <h2 className="mb-2 text-2xl font-bold text-gray-900 dark:text-white">
              Đăng ký bị từ chối
            </h2>
            <p className="mb-6 text-gray-600 dark:text-gray-400">
              Rất tiếc, hồ sơ của bạn chưa đạt yêu cầu. Vui lòng liên hệ hỗ trợ hoặc đăng ký lại.
            </p>
            <div className="flex justify-center gap-4">
              <Link to="/" className="text-gray-500 hover:text-gray-900">Về trang chủ</Link>
              <Link to="/seller/register" className="text-orange-600 hover:underline font-medium">Đăng ký lại</Link>
            </div>
          </div>
        </div>
      );
    }

    // 1.3: Chưa đăng ký -> Hiện nút Đăng ký
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 px-4 dark:bg-[#050505]">
        <div className="max-w-md text-center">
          <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-orange-100 text-orange-600 dark:bg-orange-900/20">
            <Package className="h-10 w-10" />
          </div>
          <h2 className="mb-2 text-2xl font-bold text-gray-900 dark:text-white">
            Bạn chưa là Người bán
          </h2>
          <p className="mb-8 text-gray-600 dark:text-gray-400">
            Hãy đăng ký ngay để bắt đầu bán hàng trên OWLS Marketplace và tiếp cận hàng ngàn khách hàng.
          </p>
          <div className="flex flex-col gap-3">
            <Link
              to="/seller/register"
              className="inline-flex items-center justify-center rounded-xl bg-orange-600 px-6 py-3 font-semibold text-white transition hover:bg-orange-700 shadow-lg shadow-orange-500/20"
            >
              Đăng ký mở Shop ngay
            </Link>
            <Link to="/" className="text-sm text-gray-500 hover:text-gray-900 dark:hover:text-gray-300">
              Về trang chủ
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // --- TRƯỜNG HỢP 2: ĐÃ LÀ VENDOR (DASHBOARD) ---
  const statsDisplay = [
    { 
      label: "Sản phẩm", 
      value: stats?.total.products.toString() || "0", 
      icon: Package, 
      color: "text-blue-600",
      bg: "bg-blue-50 dark:bg-blue-900/20"
    },
    { 
      label: "Đơn hàng hôm nay", 
      value: stats?.today.orders.toString() || "0", 
      icon: ShoppingBag, 
      color: "text-orange-600",
      bg: "bg-orange-50 dark:bg-orange-900/20"
    },
    { 
      label: "Doanh thu tháng", 
      value: formatCurrency(stats?.this_month.revenue || 0), 
      icon: DollarSign, 
      color: "text-green-600",
      bg: "bg-green-50 dark:bg-green-900/20"
    },
    { 
      label: "Đánh giá", 
      value: `${stats?.total.rating?.toFixed(1) || "0"} ⭐`, 
      icon: Star, 
      color: "text-yellow-600",
      bg: "bg-yellow-50 dark:bg-yellow-900/20"
    },
  ];

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Tổng quan Shop</h1>
          <p className="text-gray-500 mt-1">Xin chào, {user.full_name}!</p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
        {statsDisplay.map((stat) => (
          <div
            key={stat.label}
            className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</p>
                <p className="mt-2 text-2xl font-bold text-gray-900 dark:text-gray-100">{stat.value}</p>
              </div>
              <div className={`rounded-xl p-3 ${stat.bg}`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Today Summary */}
      {stats && (
        <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900 mb-8">
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">Hôm nay</h2>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-lg bg-gray-50 p-4 dark:bg-gray-800">
              <p className="text-sm text-gray-600 dark:text-gray-400">Đơn hàng mới</p>
              <p className="mt-1 text-xl font-bold text-gray-900 dark:text-gray-100">{stats.today.orders}</p>
            </div>
            <div className="rounded-lg bg-gray-50 p-4 dark:bg-gray-800">
              <p className="text-sm text-gray-600 dark:text-gray-400">Doanh thu</p>
              <p className="mt-1 text-xl font-bold text-green-600">{formatCurrency(stats.today.revenue)}</p>
            </div>
            <div className="rounded-lg bg-gray-50 p-4 dark:bg-gray-800">
              <p className="text-sm text-gray-600 dark:text-gray-400">Sản phẩm bán ra</p>
              <p className="mt-1 text-xl font-bold text-gray-900 dark:text-gray-100">{stats.today.products_sold}</p>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">Menu quản lý</h2>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Link
          to="/seller/products"
          className="group flex flex-col justify-between rounded-xl border border-gray-200 bg-white p-6 transition hover:border-orange-500 hover:shadow-md dark:border-gray-800 dark:bg-gray-900"
        >
          <div>
            <div className="h-10 w-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center mb-4 dark:bg-blue-900/20">
              <Package className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">Sản phẩm</h3>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Quản lý kho hàng và thêm sản phẩm mới</p>
          </div>
        </Link>

        <Link
          to="/seller/orders"
          className="group flex flex-col justify-between rounded-xl border border-gray-200 bg-white p-6 transition hover:border-orange-500 hover:shadow-md dark:border-gray-800 dark:bg-gray-900"
        >
          <div>
            <div className="h-10 w-10 rounded-lg bg-orange-50 text-orange-600 flex items-center justify-center mb-4 dark:bg-orange-900/20">
              <ShoppingBag className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">Đơn hàng</h3>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Xử lý và theo dõi đơn hàng của khách</p>
          </div>
        </Link>

        <Link
          to="/seller/settings"
          className="group flex flex-col justify-between rounded-xl border border-gray-200 bg-white p-6 transition hover:border-orange-500 hover:shadow-md dark:border-gray-800 dark:bg-gray-900"
        >
          <div>
            <div className="h-10 w-10 rounded-lg bg-gray-50 text-gray-600 flex items-center justify-center mb-4 dark:bg-gray-800">
              <DollarSign className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">Cài đặt</h3>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Thông tin cửa hàng và thanh toán</p>
          </div>
        </Link>
      </div>
    </div>
  );
}
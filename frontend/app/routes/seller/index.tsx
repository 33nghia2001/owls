import { Link, useLoaderData } from "react-router";
import { Package, ShoppingBag, DollarSign, Star, Loader2, AlertTriangle, CheckCircle, Clock, Mail, HelpCircle } from "lucide-react";
import { useAuthStore } from "~/lib/stores";
import { vendorAnalyticsApi, authApi, vendorsApi } from "~/lib/services";
import { formatCurrency } from "~/lib/utils";
import { useEffect, useState } from "react";
import { Button } from "~/components/ui";

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
  } catch (error: unknown) {
    const axiosErr = error as { response?: { status?: number } };
    if (axiosErr.response?.status === 401) {
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
      const registeredDate = vendorProfile.created_at 
        ? new Date(vendorProfile.created_at).toLocaleDateString('vi-VN', { 
            day: '2-digit', 
            month: '2-digit', 
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })
        : null;

      return (
        <div className="min-h-screen bg-gray-50 py-12 dark:bg-[#050505]">
          <div className="container mx-auto max-w-2xl px-4">
            {/* Main Card */}
            <div className="rounded-2xl bg-white p-8 shadow-sm border border-gray-200 dark:bg-gray-900 dark:border-gray-800">
              <div className="text-center">
                <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-yellow-100 dark:bg-yellow-900/30">
                  <Clock className="h-10 w-10 text-yellow-600 dark:text-yellow-400" />
                </div>
                <h2 className="mb-2 text-2xl font-bold text-gray-900 dark:text-white">
                  Hồ sơ đang chờ duyệt
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Cảm ơn bạn đã đăng ký bán hàng trên OWLS!
                </p>
              </div>

              {/* Shop Info */}
              <div className="mt-8 rounded-xl bg-gray-50 p-4 dark:bg-gray-800">
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400">
                    <ShoppingBag className="h-6 w-6" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      {vendorProfile.shop_name}
                    </p>
                    {registeredDate && (
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Đăng ký lúc: {registeredDate}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Timeline */}
              <div className="mt-8 space-y-4">
                <h3 className="font-semibold text-gray-900 dark:text-white">Quy trình xét duyệt</h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400">
                      <CheckCircle className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">Gửi đơn đăng ký</p>
                      <p className="text-sm text-gray-500">Hoàn tất</p>
                    </div>
                  </div>
                  <div className="ml-4 h-6 w-px bg-gray-200 dark:bg-gray-700" />
                  <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400">
                      <Loader2 className="h-4 w-4 animate-spin" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">Xem xét hồ sơ</p>
                      <p className="text-sm text-gray-500">Đang xử lý (1-3 ngày làm việc)</p>
                    </div>
                  </div>
                  <div className="ml-4 h-6 w-px bg-gray-200 dark:bg-gray-700" />
                  <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-gray-400 dark:bg-gray-800">
                      <CheckCircle className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-400">Kích hoạt cửa hàng</p>
                      <p className="text-sm text-gray-400">Chờ hoàn tất bước 2</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Help Section */}
              <div className="mt-8 rounded-xl border border-blue-100 bg-blue-50 p-4 dark:border-blue-900/30 dark:bg-blue-900/10">
                <div className="flex gap-3">
                  <HelpCircle className="h-5 w-5 flex-shrink-0 text-blue-600 dark:text-blue-400" />
                  <div>
                    <p className="font-medium text-blue-900 dark:text-blue-100">Cần hỗ trợ?</p>
                    <p className="mt-1 text-sm text-blue-700 dark:text-blue-300">
                      Nếu hồ sơ của bạn chưa được duyệt sau 3 ngày, vui lòng liên hệ:{" "}
                      <a href="mailto:support@owls.vn" className="font-medium underline">
                        support@owls.vn
                      </a>
                    </p>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="mt-8 flex items-center justify-center gap-4">
                <Link to="/">
                  <Button variant="outline">Về trang chủ</Button>
                </Link>
                <Link to="/account">
                  <Button variant="outline">Tài khoản của tôi</Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      );
    }

    // 1.2: Bị từ chối
    if (vendorProfile && vendorProfile.status === 'rejected') {
      return (
        <div className="min-h-screen bg-gray-50 py-12 dark:bg-[#050505]">
          <div className="container mx-auto max-w-2xl px-4">
            <div className="rounded-2xl bg-white p-8 shadow-sm border border-gray-200 dark:bg-gray-900 dark:border-gray-800">
              <div className="text-center">
                <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-red-100 dark:bg-red-900/30">
                  <AlertTriangle className="h-10 w-10 text-red-600 dark:text-red-400" />
                </div>
                <h2 className="mb-2 text-2xl font-bold text-gray-900 dark:text-white">
                  Đăng ký chưa được duyệt
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Rất tiếc, hồ sơ đăng ký của bạn chưa đạt yêu cầu tại thời điểm này.
                </p>
              </div>

              {/* Shop Info */}
              <div className="mt-8 rounded-xl bg-red-50 p-4 dark:bg-red-900/10">
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400">
                    <ShoppingBag className="h-6 w-6" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      {vendorProfile.shop_name}
                    </p>
                    <p className="text-sm text-red-600 dark:text-red-400">
                      Trạng thái: Từ chối
                    </p>
                  </div>
                </div>
              </div>

              {/* Reasons & Next Steps */}
              <div className="mt-8 space-y-4">
                <h3 className="font-semibold text-gray-900 dark:text-white">Bạn có thể</h3>
                <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <li className="flex items-start gap-2">
                    <span className="text-orange-500">•</span>
                    Kiểm tra lại thông tin và đăng ký mới với thông tin chính xác hơn
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-orange-500">•</span>
                    Liên hệ bộ phận hỗ trợ để biết thêm chi tiết về lý do từ chối
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-orange-500">•</span>
                    Bổ sung các giấy tờ cần thiết nếu được yêu cầu
                  </li>
                </ul>
              </div>

              {/* Help Section */}
              <div className="mt-8 rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800">
                <div className="flex gap-3">
                  <Mail className="h-5 w-5 flex-shrink-0 text-gray-600 dark:text-gray-400" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Liên hệ hỗ trợ</p>
                    <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                      Email:{" "}
                      <a href="mailto:seller-support@owls.vn" className="text-orange-500 underline">
                        seller-support@owls.vn
                      </a>
                    </p>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
                <Link to="/seller/register">
                  <Button className="w-full sm:w-auto">Đăng ký lại</Button>
                </Link>
                <Link to="/">
                  <Button variant="outline" className="w-full sm:w-auto">Về trang chủ</Button>
                </Link>
              </div>
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
import { Link, useLoaderData, useNavigate } from "react-router";
import { 
  Package, 
  MapPin, 
  User, 
  Settings, 
  LogOut, 
  Heart, 
  ShoppingBag,
  ChevronRight,
  Clock,
  CheckCircle2,
  XCircle,
  Truck
} from "lucide-react";
import { authApi, ordersApi } from "~/lib/services";
import { useAuthStore } from "~/lib/stores";
import { formatCurrency, cn } from "~/lib/utils";
import { Button } from "~/components/ui";
// Use Intl.DateTimeFormat instead of date-fns to avoid extra dependency in dev

// --- META ---
export function meta() {
  return [
    { title: "Tài khoản của tôi - OWLS" },
    { name: "description", content: "Quản lý tài khoản và đơn hàng của bạn" },
  ];
}

// --- CLIENT LOADER ---
// Sử dụng clientLoader để tránh lỗi 401 khi SSR (do token nằm ở localStorage)
export async function clientLoader() {
  try {
    const [profile, ordersData] = await Promise.all([
      authApi.getProfile(),
      ordersApi.getOrders({ page: 1 })
    ]);
    
    return { 
      user: profile,
      orders: Array.isArray(ordersData) ? ordersData : (ordersData.results || []),
      totalOrders: ordersData.count || 0
    };
  } catch (error: any) {
    if (error.response?.status === 401) {
      window.location.href = "/auth/login";
      return null;
    }
    throw error;
  }
}

// --- COMPONENTS ---
const StatusBadge = ({ status }: { status: string }) => {
  const styles: Record<string, string> = {
    pending: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
    confirmed: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
    shipping: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
    delivered: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
    cancelled: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  };

  const labels: Record<string, string> = {
    pending: "Chờ xử lý",
    confirmed: "Đã xác nhận",
    shipping: "Đang giao",
    delivered: "Đã giao hàng",
    cancelled: "Đã hủy",
  };

  return (
    <span className={cn("px-2.5 py-0.5 rounded-full text-xs font-medium border border-transparent", styles[status] || "bg-gray-100 text-gray-600")}>
      {labels[status] || status}
    </span>
  );
};

export default function AccountDashboard() {
  const data = useLoaderData<typeof clientLoader>();
  const navigate = useNavigate();
  const { logout } = useAuthStore();

  if (!data) return null; // Loading or redirected

  const { user, orders, totalOrders } = data;
  const recentOrder = orders[0];

  // Tính toán thống kê nhanh
  const pendingCount = orders.filter((o: any) => ['pending', 'confirmed'].includes(o.status)).length;
  const totalSpent = orders
    .filter((o: any) => o.status !== 'cancelled')
    .reduce((sum: number, o: any) => sum + Number(o.total.amount || o.total), 0);

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  const menuItems = [
    {
      title: "Đơn mua",
      description: "Xem lịch sử và theo dõi đơn hàng",
      icon: Package,
      href: "/account/orders",
      color: "text-blue-600",
      bgColor: "bg-blue-50 dark:bg-blue-900/20"
    },
    {
      title: "Sổ địa chỉ",
      description: "Quản lý địa chỉ nhận hàng",
      icon: MapPin,
      href: "/account/addresses",
      color: "text-green-600",
      bgColor: "bg-green-50 dark:bg-green-900/20"
    },
    {
      title: "Sản phẩm yêu thích",
      description: "Danh sách sản phẩm đã lưu",
      icon: Heart,
      href: "/wishlist",
      color: "text-red-600",
      bgColor: "bg-red-50 dark:bg-red-900/20"
    },
    {
      title: "Thông tin cá nhân",
      description: "Cập nhật tên, email và số điện thoại",
      icon: User,
      href: "/account/profile",
      color: "text-purple-600",
      bgColor: "bg-purple-50 dark:bg-purple-900/20"
    },
    {
      title: "Cài đặt tài khoản",
      description: "Đổi mật khẩu và bảo mật",
      icon: Settings,
      href: "/account/settings",
      color: "text-gray-600",
      bgColor: "bg-gray-50 dark:bg-gray-800"
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50/50 dark:bg-[#050505] py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        
        {/* 1. Header Profile Card */}
        <div className="mb-8 overflow-hidden rounded-2xl bg-white shadow-sm border border-gray-200 dark:bg-gray-900 dark:border-gray-800">
          <div className="h-32 bg-gradient-to-r from-orange-400 to-red-500 relative">
            <div className="absolute bottom-4 right-4 text-white/80 text-xs font-medium">
              Thành viên từ {new Date(user.date_joined || Date.now()).getFullYear()}
            </div>
          </div>
          <div className="px-6 pb-6 relative">
            <div className="flex flex-col md:flex-row items-start md:items-end -mt-12 gap-4">
              <div className="h-24 w-24 rounded-full border-4 border-white bg-gray-100 overflow-hidden dark:border-gray-900 shadow-md">
                {user.avatar ? (
                  <img src={user.avatar} alt={user.full_name} className="h-full w-full object-cover" />
                ) : (
                  <div className="h-full w-full flex items-center justify-center bg-gray-200 text-gray-500 text-2xl font-bold dark:bg-gray-800">
                    {user.first_name?.[0] || "U"}
                  </div>
                )}
              </div>
              <div className="flex-1 mb-2">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {user.full_name || "Khách hàng"}
                </h1>
                <p className="text-gray-500 dark:text-gray-400">{user.email}</p>
              </div>
              <div className="mb-2 flex gap-3 w-full md:w-auto">
                {user.is_vendor && (
                  <Button 
                    onClick={() => navigate("/seller")}
                    className="flex-1 md:flex-none bg-gray-900 text-white hover:bg-gray-800 dark:bg-white dark:text-black"
                  >
                    Trang người bán
                  </Button>
                )}
                <Button 
                  variant="outline" 
                  onClick={handleLogout}
                  className="flex-1 md:flex-none gap-2 text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200 dark:border-red-900/30 dark:hover:bg-red-900/20"
                >
                  <LogOut className="h-4 w-4" /> Đăng xuất
                </Button>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Column: Stats & Menu */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* 2. Quick Stats */}
            <div className="grid grid-cols-3 gap-4">
              <div className="rounded-xl border border-gray-200 bg-white p-4 dark:bg-gray-900 dark:border-gray-800">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-blue-50 text-blue-600 dark:bg-blue-900/20">
                    <ShoppingBag className="h-5 w-5" />
                  </div>
                  <span className="text-sm text-gray-500 dark:text-gray-400">Đơn hàng</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{totalOrders}</p>
              </div>
              
              <div className="rounded-xl border border-gray-200 bg-white p-4 dark:bg-gray-900 dark:border-gray-800">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-yellow-50 text-yellow-600 dark:bg-yellow-900/20">
                    <Clock className="h-5 w-5" />
                  </div>
                  <span className="text-sm text-gray-500 dark:text-gray-400">Chờ xử lý</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{pendingCount}</p>
              </div>

              <div className="rounded-xl border border-gray-200 bg-white p-4 dark:bg-gray-900 dark:border-gray-800">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 rounded-lg bg-green-50 text-green-600 dark:bg-green-900/20">
                    <CheckCircle2 className="h-5 w-5" />
                  </div>
                  <span className="text-sm text-gray-500 dark:text-gray-400">Đã chi tiêu</span>
                </div>
                <p className="text-lg font-bold text-gray-900 dark:text-white truncate" title={formatCurrency(totalSpent)}>
                  {formatCurrency(totalSpent)}
                </p>
              </div>
            </div>

            {/* 3. Navigation Grid */}
            <div>
              <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Tiện ích của tôi</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {menuItems.map((item) => (
                  <Link
                    key={item.href}
                    to={item.href}
                    className="group flex items-start gap-4 p-4 rounded-xl border border-gray-200 bg-white transition-all hover:border-orange-500 hover:shadow-md dark:bg-gray-900 dark:border-gray-800 dark:hover:border-orange-500"
                  >
                    <div className={cn("p-3 rounded-xl transition-colors group-hover:bg-orange-500 group-hover:text-white", item.bgColor, item.color)}>
                      <item.icon className="h-6 w-6" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 dark:text-gray-100 group-hover:text-orange-600 transition-colors">
                        {item.title}
                      </h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        {item.description}
                      </p>
                    </div>
                    <ChevronRight className="h-5 w-5 text-gray-300 group-hover:text-orange-500 group-hover:translate-x-1 transition-all" />
                  </Link>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column: Recent Order */}
          <div className="space-y-6">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">Đơn hàng mới nhất</h2>
            
            {recentOrder ? (
              <div className="rounded-xl border border-gray-200 bg-white p-5 dark:bg-gray-900 dark:border-gray-800">
                <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-100 dark:border-gray-800">
                  <div className="flex flex-col">
                    <span className="text-xs text-gray-500">Mã đơn hàng</span>
                    <span className="font-mono font-bold text-gray-900 dark:text-white">
                      #{recentOrder.order_number}
                    </span>
                  </div>
                  <StatusBadge status={recentOrder.status} />
                </div>

                <div className="space-y-3 mb-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Ngày đặt:</span>
                    <span className="text-gray-900 dark:text-gray-200">
                      {new Intl.DateTimeFormat('vi-VN').format(new Date(recentOrder.created_at))}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Tổng tiền:</span>
                    <span className="font-bold text-orange-600">
                      {formatCurrency(recentOrder.total?.amount || recentOrder.total)}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Sản phẩm:</span>
                    <span className="text-gray-900 dark:text-gray-200">
                      {recentOrder.items_count || (recentOrder.items ? recentOrder.items.length : 0)} món
                    </span>
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-100 dark:border-gray-800">
                  <div className="flex items-center gap-3 mb-4 text-sm text-gray-600 dark:text-gray-300">
                    <Truck className="h-4 w-4" />
                    <p className="truncate">{recentOrder.shipping_address}</p>
                  </div>
                  <Button 
                    variant="outline" 
                    className="w-full" 
                    onClick={() => navigate(`/account/orders/${recentOrder.id}`)}
                  >
                    Xem chi tiết
                  </Button>
                </div>
              </div>
            ) : (
              <div className="rounded-xl border border-dashed border-gray-200 bg-gray-50 p-8 text-center dark:bg-gray-900 dark:border-gray-800">
                <Package className="h-10 w-10 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500 dark:text-gray-400 text-sm">Bạn chưa có đơn hàng nào.</p>
                <Button 
                  variant="ghost" 
                  onClick={() => navigate("/products")}
                  className="text-orange-600 mt-2"
                >
                  Mua sắm ngay
                </Button>
              </div>
            )}

            {/* Promo Banner (Optional) */}
            <div className="rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 p-5 text-white shadow-lg">
              <h3 className="font-bold text-lg mb-1">Trở thành người bán?</h3>
              <p className="text-sm text-indigo-100 mb-4">
                Mở cửa hàng trên OWLS và tiếp cận hàng ngàn khách hàng tiềm năng.
              </p>
              <Button 
                onClick={() => navigate("/seller")}
                className="w-full bg-white text-indigo-600 hover:bg-gray-100 border-0"
              >
                Đăng ký bán hàng ngay
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
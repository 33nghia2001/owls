import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { motion, AnimatePresence } from "framer-motion";
import { 
  User, Mail, Phone, Calendar, MapPin, Shield, Edit2, LogOut, 
  Camera, Briefcase, CheckCircle2, Settings, Package, Heart, 
  ShoppingBag, Copy, Star, Bell, ChevronRight, CreditCard
} from "lucide-react";
import { useAuthStore } from "~/lib/stores";
import { Button, Badge, Avatar, Card } from "~/components/ui";
import { cn } from "~/lib/utils";
import toast from "react-hot-toast";

export function meta() {
  return [
    { title: "Hồ sơ cá nhân - OWLS Marketplace" },
    { name: "description", content: "Quản lý thông tin tài khoản của bạn" },
  ];
}

export default function ProfilePage() {
  const navigate = useNavigate();
  const { user, isLoading, checkAuth, logout } = useAuthStore();
  const [activeTab, setActiveTab] = useState("overview");
  const [isCopied, setIsCopied] = useState(false);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const handleCopyId = () => {
    if (user?.id) {
      navigator.clipboard.writeText(user.id);
      setIsCopied(true);
      toast.success("Đã sao chép ID");
      setTimeout(() => setIsCopied(false), 2000);
    }
  };

  const handleLogout = async () => {
    await logout();
    toast.success("Đăng xuất thành công");
    navigate("/");
  };

  const tabs = [
    { id: "overview", label: "Tổng quan", icon: Package },
    { id: "orders", label: "Đơn hàng", icon: ShoppingBag },
    { id: "security", label: "Bảo mật", icon: Shield },
    { id: "billing", label: "Thanh toán", icon: CreditCard },
  ];

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-orange-500 border-t-transparent" />
      </div>
    );
  }

  if (!user) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex min-h-[60vh] flex-col items-center justify-center space-y-6 px-4 text-center"
      >
        <div className="rounded-full bg-gray-100 p-6 dark:bg-gray-800">
          <User className="h-12 w-12 text-gray-400" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Chưa đăng nhập
          </h2>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Vui lòng đăng nhập để xem và quản lý hồ sơ của bạn.
          </p>
        </div>
        <Button onClick={() => navigate("/auth/login")} size="lg">
          Đăng nhập ngay
        </Button>
      </motion.div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50/50 dark:bg-[#0a0a0a] pb-20 font-sans text-gray-900 dark:text-gray-100 transition-colors duration-300">
      
      {/* 1. Immersive Cover Image */}
      <div className="relative h-[280px] w-full overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-orange-600 via-rose-600 to-purple-600">
            {/* Pattern Overlay */}
            <div className="absolute inset-0 opacity-20" style={{ backgroundImage: "radial-gradient(#fff 1px, transparent 1px)", backgroundSize: "20px 20px" }}></div>
        </div>
        <div className="absolute inset-0 bg-gradient-to-b from-black/10 via-transparent to-gray-50/90 dark:to-[#0a0a0a]" />
        
        {/* Quick Actions on Cover */}
        <div className="absolute top-6 right-6 flex gap-2">
           <Button variant="secondary" size="sm" className="bg-white/20 backdrop-blur-md border-white/30 text-white hover:bg-white/30 dark:text-white">
              <Camera className="mr-2 h-4 w-4" />
              Sửa ảnh bìa
           </Button>
        </div>
      </div>

      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="relative -mt-24 grid grid-cols-1 gap-8 lg:grid-cols-12">
          
          {/* 2. Left Sidebar (Sticky) */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="lg:col-span-4 xl:col-span-3"
          >
            <div className="sticky top-6 space-y-6">
              
              {/* Profile Card */}
              <Card className="flex flex-col items-center p-6 text-center border-t-4 border-t-orange-500 overflow-visible">
                <div className="relative -mt-20 mb-4 group">
                  <div className="h-32 w-32 md:h-40 md:w-40">
                    <Avatar 
                      src={user.avatar || undefined}
                      fallback={(user.first_name?.[0] || user.email[0]).toUpperCase()}
                      className="h-full w-full border-[6px] border-white dark:border-[#121212] shadow-2xl" 
                    />
                  </div>
                  <button className="absolute bottom-1 right-1 rounded-full bg-gray-900 p-2 text-white shadow-lg transition hover:bg-orange-600 group-hover:scale-110">
                    <Camera className="h-4 w-4" />
                  </button>
                </div>
                
                <h2 className="text-2xl font-bold flex items-center gap-2">
                  {user.full_name || `${user.first_name} ${user.last_name}`.trim() || user.email.split('@')[0]}
                  {user.is_vendor && <CheckCircle2 className="h-5 w-5 text-blue-500" fill="currentColor" color="white" />}
                </h2>
                
                <div className="mt-1 flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                  <span className="font-mono">ID: {user.id.slice(0, 8)}...</span>
                  <button onClick={handleCopyId} className="hover:text-orange-500 transition">
                     {isCopied ? <CheckCircle2 className="h-3.5 w-3.5 text-green-500" /> : <Copy className="h-3.5 w-3.5" />}
                  </button>
                </div>

                <div className="mt-4 mb-6 flex gap-2">
                   <Badge variant="default" className="px-3 py-1">
                      {user.is_vendor ? "Người bán" : "Thành viên"}
                   </Badge>
                </div>

                <div className="w-full grid grid-cols-2 gap-3 mb-6">
                   <button
                     onClick={() => navigate("/wishlist")}
                     className="rounded-xl bg-gray-50 dark:bg-gray-800/50 p-3 hover:bg-orange-50 dark:hover:bg-orange-900/20 transition-colors"
                   >
                      <div className="text-2xl font-bold text-gray-900 dark:text-white">0</div>
                      <div className="text-xs text-gray-500 uppercase font-semibold">Yêu thích</div>
                   </button>
                   <button
                     onClick={() => navigate("/account/orders")}
                     className="rounded-xl bg-gray-50 dark:bg-gray-800/50 p-3 hover:bg-orange-50 dark:hover:bg-orange-900/20 transition-colors"
                   >
                      <div className="text-2xl font-bold text-gray-900 dark:text-white">0</div>
                      <div className="text-xs text-gray-500 uppercase font-semibold">Đơn hàng</div>
                   </button>
                </div>

                <div className="w-full space-y-3">
                  <Button variant="outline" className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 border-red-200 dark:border-red-900/50" onClick={handleLogout}>
                    <LogOut className="mr-2 h-4 w-4" />
                    Đăng xuất
                  </Button>
                </div>
              </Card>

              {/* Contact Info Mini Card */}
              <Card className="p-5 space-y-4">
                 <h3 className="font-semibold text-sm uppercase tracking-wider text-gray-500 dark:text-gray-400">Thông tin liên hệ</h3>
                 <div className="space-y-3">
                    <div className="flex items-center gap-3">
                       <div className="p-2 rounded-lg bg-orange-100 text-orange-600 dark:bg-orange-900/30">
                          <Mail className="h-4 w-4" />
                       </div>
                       <div className="text-sm truncate font-medium">{user.email}</div>
                    </div>
                    {user.phone && (
                      <div className="flex items-center gap-3">
                         <div className="p-2 rounded-lg bg-blue-100 text-blue-600 dark:bg-blue-900/30">
                            <Phone className="h-4 w-4" />
                         </div>
                         <div className="text-sm font-medium">{user.phone}</div>
                      </div>
                    )}
                    <div className="flex items-center gap-3">
                       <div className="p-2 rounded-lg bg-purple-100 text-purple-600 dark:bg-purple-900/30">
                          <Calendar className="h-4 w-4" />
                       </div>
                       <div className="text-sm font-medium">
                         Tham gia {new Date(user.date_joined).toLocaleDateString("vi-VN", { month: "long", year: "numeric" })}
                       </div>
                    </div>
                 </div>
                 <Button variant="ghost" size="sm" className="w-full text-orange-600" onClick={() => navigate("/account/settings")}>
                   Chỉnh sửa thông tin
                 </Button>
              </Card>
            </div>
          </motion.div>

          {/* 3. Right Content Area */}
          <motion.div 
             initial={{ opacity: 0, x: 20 }}
             animate={{ opacity: 1, x: 0 }}
             transition={{ delay: 0.1 }}
             className="lg:col-span-8 xl:col-span-9 space-y-6"
          >
             
             {/* Custom Tab Navigation */}
             <div className="flex overflow-x-auto pb-2 scrollbar-hide">
                <div className="flex p-1 gap-1 bg-white dark:bg-gray-900/50 rounded-xl border border-gray-200 dark:border-gray-800">
                  {tabs.map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={cn(
                        "relative flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all z-10",
                        activeTab === tab.id ? "text-white" : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                      )}
                    >
                      {activeTab === tab.id && (
                        <motion.div
                          layoutId="activeTab"
                          className="absolute inset-0 bg-gray-900 dark:bg-orange-600 rounded-lg shadow-lg"
                          transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                        />
                      )}
                      <span className="relative z-10 flex items-center gap-2">
                         <tab.icon className="h-4 w-4" />
                         {tab.label}
                      </span>
                    </button>
                  ))}
                </div>
             </div>

             {/* Tab Content with AnimatePresence */}
             <AnimatePresence mode="wait">
                <motion.div
                  key={activeTab}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.2 }}
                >
                   {activeTab === 'overview' && (
                      <div className="space-y-6">
                         {/* Stats Row */}
                         <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {[
                               { label: "Sản phẩm yêu thích", val: "24", icon: Heart, color: "text-pink-500", bg: "bg-pink-50 dark:bg-pink-900/20" },
                               { label: "Đơn đang giao", val: "2", icon: Package, color: "text-blue-500", bg: "bg-blue-50 dark:bg-blue-900/20" },
                               { label: "Thông báo mới", val: "5", icon: Bell, color: "text-yellow-500", bg: "bg-yellow-50 dark:bg-yellow-900/20" },
                            ].map((stat, idx) => (
                               <Card key={idx} className="p-4 flex items-center justify-between hover:border-orange-200 transition-colors cursor-pointer group">
                                  <div>
                                     <p className="text-sm text-gray-500 dark:text-gray-400">{stat.label}</p>
                                     <p className="text-2xl font-bold mt-1 group-hover:text-orange-600 transition-colors">{stat.val}</p>
                                  </div>
                                  <div className={cn("h-10 w-10 rounded-full flex items-center justify-center", stat.bg, stat.color)}>
                                     <stat.icon className="h-5 w-5" />
                                  </div>
                               </Card>
                            ))}
                         </div>

                         {/* Recent Activity Section */}
                         <Card className="p-6">
                            <div className="flex items-center justify-between mb-6">
                               <h3 className="text-lg font-bold">Hoạt động gần đây</h3>
                               <Button variant="ghost" size="sm" className="text-orange-600">Xem tất cả</Button>
                            </div>
                            <div className="space-y-6">
                               {[1, 2, 3].map((_, i) => (
                                  <div key={i} className="flex gap-4 group">
                                     <div className="relative mt-1">
                                        <div className="h-10 w-10 rounded-full bg-orange-100 dark:bg-orange-900/30 text-orange-600 flex items-center justify-center z-10 relative group-hover:bg-orange-600 group-hover:text-white transition-colors">
                                           <ShoppingBag className="h-5 w-5" />
                                        </div>
                                        {i !== 2 && <div className="absolute top-10 left-1/2 -translate-x-1/2 w-0.5 h-12 bg-gray-200 dark:bg-gray-800" />}
                                     </div>
                                     <div className="flex-1 pb-6 border-b border-gray-100 dark:border-gray-800 last:border-0 last:pb-0">
                                        <div className="flex justify-between items-start">
                                           <div>
                                              <p className="font-medium text-gray-900 dark:text-gray-100">Đặt hàng thành công #ORD-2023-{8892+i}</p>
                                              <p className="text-sm text-gray-500 mt-1">Đơn hàng bao gồm 3 sản phẩm: Áo thun, Giày sneaker...</p>
                                           </div>
                                           <span className="text-xs text-gray-400">2 giờ trước</span>
                                        </div>
                                     </div>
                                  </div>
                               ))}
                            </div>
                         </Card>

                         {/* Account Health */}
                         <div className="rounded-2xl bg-gradient-to-br from-green-50 to-emerald-100 dark:from-green-900/20 dark:to-emerald-900/10 border border-green-200 dark:border-green-800 p-6 flex items-start gap-4">
                            <div className="p-2 bg-green-200 dark:bg-green-800 rounded-full text-green-700 dark:text-green-300">
                               <Shield className="h-6 w-6" />
                            </div>
                            <div>
                               <h4 className="font-bold text-green-900 dark:text-green-400">Tài khoản bảo mật cao</h4>
                               <p className="text-sm text-green-800/80 dark:text-green-300/70 mt-1">
                                  Bạn đã kích hoạt xác thực 2 lớp và cập nhật mật khẩu gần đây. Tài khoản của bạn đang ở trạng thái an toàn tuyệt đối.
                               </p>
                            </div>
                         </div>
                      </div>
                   )}

                   {activeTab === 'security' && (
                      <div className="space-y-6">
                         <Card className="p-6 divide-y divide-gray-100 dark:divide-gray-800">
                            <div className="py-4 first:pt-0 flex items-center justify-between">
                               <div>
                                  <p className="font-medium">Mật khẩu</p>
                                  <p className="text-sm text-gray-500">Cập nhật lần cuối 3 tháng trước</p>
                               </div>
                               <Button variant="outline" size="sm" onClick={() => navigate("/account/change-password")}>
                                 Đổi mật khẩu
                               </Button>
                            </div>
                            <div className="py-4 flex items-center justify-between">
                               <div>
                                  <p className="font-medium">Xác thực 2 bước (2FA)</p>
                                  <p className="text-sm text-gray-500">Tăng cường bảo mật cho tài khoản</p>
                               </div>
                               <Button variant="primary" size="sm" onClick={() => toast("Tính năng đang phát triển")}>
                                 Kích hoạt
                               </Button>
                            </div>
                            <div className="py-4 last:pb-0 flex items-center justify-between">
                               <div>
                                  <p className="font-medium text-red-600">Xóa tài khoản</p>
                                  <p className="text-sm text-gray-500">Hành động này không thể hoàn tác</p>
                               </div>
                               <Button variant="ghost" size="sm" className="text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20">Xóa vĩnh viễn</Button>
                            </div>
                         </Card>
                      </div>
                   )}
                   
                   {/* Placeholder for other tabs */}
                   {(activeTab !== 'overview' && activeTab !== 'security') && (
                      <motion.div 
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                        className="flex flex-col items-center justify-center py-20 text-center"
                      >
                         <div className="h-20 w-20 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mb-4">
                            <Package className="h-10 w-10 text-gray-400" />
                         </div>
                         <h3 className="text-xl font-bold text-gray-900 dark:text-white">Đang phát triển</h3>
                         <p className="text-gray-500 mt-2 max-w-sm">Tính năng này đang được xây dựng và sẽ sớm ra mắt trong phiên bản tiếp theo.</p>
                      </motion.div>
                   )}
                </motion.div>
             </AnimatePresence>

          </motion.div>
        </div>
      </div>
    </div>
  );
}
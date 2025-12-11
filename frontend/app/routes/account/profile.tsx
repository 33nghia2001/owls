import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { motion, AnimatePresence } from "framer-motion";
import { 
  User, Mail, Phone, Calendar, MapPin, Shield, Edit2, LogOut, 
  Camera, Briefcase, CheckCircle2, Settings, Package, Heart, 
  ShoppingBag, Copy, Star, Bell, ChevronRight, CreditCard,
  Wallet, Trophy
} from "lucide-react";
import { useAuthStore } from "~/lib/stores";
import { Button, Badge, Card } from "~/components/ui"; 
import { cn, getImageUrl } from "~/lib/utils";
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
    { id: "wallet", label: "Ví & Xu", icon: Wallet },
  ];

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#050505]">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-orange-500 border-t-transparent shadow-lg shadow-orange-500/20" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#050505] px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex max-w-md flex-col items-center justify-center space-y-6 rounded-3xl border border-white/10 bg-white/5 p-8 text-center backdrop-blur-xl"
        >
          <div className="rounded-full bg-white/10 p-6 shadow-inner">
            <User className="h-12 w-12 text-white/50" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Chưa đăng nhập</h2>
            <p className="mt-2 text-gray-400">
              Vui lòng đăng nhập để xem và quản lý hồ sơ của bạn.
            </p>
          </div>
          <Button 
            onClick={() => navigate("/auth/login")} 
            size="lg"
            className="w-full rounded-xl bg-gradient-to-r from-orange-500 to-red-600 font-bold text-white shadow-lg shadow-orange-500/20 hover:scale-105"
          >
            Đăng nhập ngay
          </Button>
        </motion.div>
      </div>
    );
  }

  // Helper to get initials
  const getInitials = () => {
    if (user.first_name && user.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    }
    return (user.email[0] || "U").toUpperCase();
  };

  return (
    <div className="min-h-screen bg-gray-50/50 dark:bg-[#050505] pb-20 font-sans text-gray-900 dark:text-gray-100 transition-colors duration-300">
      
      {/* 1. Ultra Modern Cover Image */}
      <div className="relative h-[320px] w-full overflow-hidden">
        {/* Dynamic Gradient Background */}
        <div className="absolute inset-0 bg-black">
            <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(249,115,22,0.15),rgba(255,255,255,0))]" />
            <div className="absolute top-[20%] left-[10%] w-[40vw] h-[40vw] rounded-full bg-orange-500/10 blur-[120px] mix-blend-screen" />
            <div className="absolute bottom-[10%] right-[10%] w-[40vw] h-[40vw] rounded-full bg-purple-600/10 blur-[120px] mix-blend-screen" />
            {/* Grid Pattern Overlay */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808008_1px,transparent_1px),linear-gradient(to_bottom,#80808008_1px,transparent_1px)] bg-[size:24px_24px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>
        </div>
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#050505]/40 to-[#050505]" />
        
        {/* Quick Actions on Cover */}
        <div className="absolute top-6 right-6 flex gap-3 z-10">
           <Button variant="secondary" size="sm" className="bg-black/30 backdrop-blur-md border border-white/10 text-white hover:bg-white/10 dark:text-white rounded-full px-4">
              <Camera className="mr-2 h-4 w-4" />
              Sửa ảnh bìa
           </Button>
        </div>
      </div>

      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="relative -mt-28 grid grid-cols-1 gap-8 lg:grid-cols-12">
          
          {/* 2. Left Sidebar (Sticky Profile Card) */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="lg:col-span-4 xl:col-span-3"
          >
            <div className="sticky top-24 space-y-6">
              
              {/* Main Profile Card */}
              <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-white/80 p-6 text-center shadow-xl backdrop-blur-xl dark:bg-[#111]/80 dark:border-white/5 dark:shadow-2xl">
                {/* Glowing border effect */}
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-orange-500 to-transparent opacity-50"></div>

                <div className="relative mt-4 mb-4 inline-block group">
                  <div className="h-28 w-28 md:h-32 md:w-32 rounded-full p-1 bg-gradient-to-br from-orange-500 via-red-500 to-purple-600 shadow-2xl">
                    <div className="h-full w-full overflow-hidden rounded-full border-[3px] border-white dark:border-[#050505] bg-[#111] relative">
                      {user.avatar ? (
                        <img 
                          src={getImageUrl(user.avatar)} 
                          alt={user.full_name}
                          className="h-full w-full object-cover"
                          onError={(e) => {
                            // Fallback if image fails to load
                            e.currentTarget.style.display = 'none';
                            // Show initials fallback (needs sibling element logic or state, simplified here by hiding img)
                          }}
                        />
                      ) : null}
                      {/* Fallback Initials - Always rendered behind or if img missing */}
                      <div className={`absolute inset-0 flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-900 text-3xl font-bold text-white ${user.avatar ? '-z-10' : 'z-0'}`}>
                        {getInitials()}
                      </div>
                    </div>
                  </div>
                  <button className="absolute bottom-2 right-2 rounded-full bg-white text-black p-2.5 shadow-lg transition-transform hover:scale-110 hover:bg-gray-100 group-hover:scale-105 z-10 cursor-pointer">
                    <Camera className="h-4 w-4" />
                  </button>
                </div>
                
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center justify-center gap-2">
                  {user.full_name || user.email.split('@')[0]}
                  {user.is_vendor && (
                    <div className="rounded-full bg-blue-500/20 p-1" title="Đã xác minh người bán">
                      <CheckCircle2 className="h-4 w-4 text-blue-500" fill="currentColor" color="white" />
                    </div>
                  )}
                </h2>
                
                <div className="mt-2 flex items-center justify-center gap-2 text-xs font-mono text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-white/5 py-1 px-3 rounded-full mx-auto w-fit">
                  <span>ID: {user.id.slice(0, 8)}...</span>
                  <button onClick={handleCopyId} className="hover:text-orange-500 transition-colors" title="Sao chép ID">
                     {isCopied ? <CheckCircle2 className="h-3.5 w-3.5 text-green-500" /> : <Copy className="h-3.5 w-3.5" />}
                  </button>
                </div>

                <div className="mt-6 flex justify-center gap-2">
                   <Badge className={cn("px-3 py-1 text-xs uppercase tracking-wider", user.is_vendor ? "bg-orange-500/10 text-orange-500 border-orange-500/20" : "bg-blue-500/10 text-blue-500 border-blue-500/20")}>
                      {user.is_vendor ? "Người bán" : "Thành viên"}
                   </Badge>
                   <Badge className="bg-yellow-500/10 text-yellow-500 border-yellow-500/20 px-3 py-1 text-xs uppercase tracking-wider flex items-center gap-1">
                      <Star className="w-3 h-3 fill-current" /> Gold Member
                   </Badge>
                </div>

                <div className="mt-8 grid grid-cols-2 gap-3">
                   <div className="rounded-2xl bg-gray-50 dark:bg-white/5 p-4 transition-colors hover:bg-orange-50 dark:hover:bg-white/10 group cursor-pointer" onClick={() => navigate("/wishlist")}>
                      <Heart className="mx-auto h-6 w-6 text-gray-400 group-hover:text-red-500 transition-colors mb-1" />
                      <div className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">Yêu thích</div>
                   </div>
                   <div className="rounded-2xl bg-gray-50 dark:bg-white/5 p-4 transition-colors hover:bg-orange-50 dark:hover:bg-white/10 group cursor-pointer" onClick={() => navigate("/account/orders")}>
                      <ShoppingBag className="mx-auto h-6 w-6 text-gray-400 group-hover:text-orange-500 transition-colors mb-1" />
                      <div className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">Đơn hàng</div>
                   </div>
                </div>

                <div className="mt-6 space-y-3">
                  <Button 
                    variant="outline" 
                    className="w-full justify-start h-12 rounded-xl border-gray-200 dark:border-white/10 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-white/5 group" 
                    onClick={handleLogout}
                  >
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gray-100 dark:bg-white/5 mr-3 group-hover:bg-red-500/10 group-hover:text-red-500 transition-colors">
                      <LogOut className="h-4 w-4" />
                    </div>
                    Đăng xuất
                  </Button>
                </div>
              </div>

              {/* Contact Info Card */}
              <div className="rounded-3xl border border-gray-200 bg-white/50 p-6 shadow-sm backdrop-blur-sm dark:border-white/5 dark:bg-[#111]/50">
                 <h3 className="mb-4 text-xs font-bold uppercase tracking-widest text-gray-500">Thông tin liên hệ</h3>
                 <div className="space-y-4">
                    <div className="flex items-center gap-4 group">
                       <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-orange-100 text-orange-600 dark:bg-orange-500/10 dark:text-orange-400 group-hover:scale-110 transition-transform">
                          <Mail className="h-5 w-5" />
                       </div>
                       <div className="flex-1 min-w-0">
                          <p className="text-xs text-gray-500">Email</p>
                          <p className="text-sm font-medium text-gray-900 dark:text-gray-200 truncate">{user.email}</p>
                       </div>
                    </div>
                    {user.phone && (
                      <div className="flex items-center gap-4 group">
                         <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-100 text-blue-600 dark:bg-blue-500/10 dark:text-blue-400 group-hover:scale-110 transition-transform">
                            <Phone className="h-5 w-5" />
                         </div>
                         <div className="flex-1 min-w-0">
                            <p className="text-xs text-gray-500">Điện thoại</p>
                            <p className="text-sm font-medium text-gray-900 dark:text-gray-200">{user.phone}</p>
                         </div>
                      </div>
                    )}
                    <div className="flex items-center gap-4 group">
                       <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-purple-100 text-purple-600 dark:bg-purple-500/10 dark:text-purple-400 group-hover:scale-110 transition-transform">
                          <Calendar className="h-5 w-5" />
                       </div>
                       <div className="flex-1 min-w-0">
                          <p className="text-xs text-gray-500">Tham gia</p>
                          <p className="text-sm font-medium text-gray-900 dark:text-gray-200">
                             {new Date(user.date_joined).toLocaleDateString("vi-VN", { month: "long", year: "numeric" })}
                          </p>
                       </div>
                    </div>
                 </div>
                 <div className="mt-6 pt-6 border-t border-gray-100 dark:border-white/5">
                    <Button 
                      variant="ghost" 
                      className="w-full justify-between text-gray-600 dark:text-gray-400 hover:text-orange-500 dark:hover:text-orange-400 group" 
                      onClick={() => navigate("/account/settings")}
                    >
                      Chỉnh sửa thông tin
                      <ChevronRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                    </Button>
                 </div>
              </div>
            </div>
          </motion.div>

          {/* 3. Right Content Area (Tabs & Bento Grid) */}
          <motion.div 
             initial={{ opacity: 0, x: 20 }}
             animate={{ opacity: 1, x: 0 }}
             transition={{ delay: 0.1 }}
             className="lg:col-span-8 xl:col-span-9 space-y-8"
          >
             
             {/* Modern Tab Navigation */}
             <div className="flex overflow-x-auto pb-1 scrollbar-hide">
                <div className="flex p-1.5 gap-2 bg-gray-100 dark:bg-white/5 rounded-2xl border border-gray-200 dark:border-white/5 backdrop-blur-md">
                  {tabs.map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={cn(
                        "relative flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-bold transition-all z-10 whitespace-nowrap",
                        activeTab === tab.id ? "text-white" : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-200/50 dark:hover:bg-white/5"
                      )}
                    >
                      {activeTab === tab.id && (
                        <motion.div
                          layoutId="activeTab"
                          className="absolute inset-0 bg-gradient-to-r from-gray-900 to-black dark:from-orange-600 dark:to-red-600 rounded-xl shadow-lg"
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

             {/* Tab Content */}
             <AnimatePresence mode="wait">
                <motion.div
                  key={activeTab}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3 }}
                >
                   {activeTab === 'overview' && (
                      <div className="space-y-6">
                         {/* Bento Grid Stats */}
                         <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {[
                               { label: "Ví OWLS", val: "0₫", icon: Wallet, color: "text-green-500", bg: "bg-green-500/10", border: "border-green-500/20" },
                               { label: "Xu tích lũy", val: "0 Xu", icon: Star, color: "text-yellow-500", bg: "bg-yellow-500/10", border: "border-yellow-500/20" },
                               { label: "Voucher", val: "0 Mã", icon: Package, color: "text-blue-500", bg: "bg-blue-500/10", border: "border-blue-500/20" },
                            ].map((stat, idx) => (
                               <motion.div 
                                  key={idx}
                                  whileHover={{ y: -5 }}
                                  className={cn("rounded-3xl border p-6 bg-white dark:bg-[#111] backdrop-blur-sm shadow-lg", stat.border)}
                               >
                                  <div className="flex items-start justify-between">
                                     <div>
                                        <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{stat.label}</p>
                                        <h4 className="mt-2 text-2xl font-black text-gray-900 dark:text-white">{stat.val}</h4>
                                     </div>
                                     <div className={cn("rounded-2xl p-3", stat.bg)}>
                                        <stat.icon className={cn("h-6 w-6", stat.color)} />
                                     </div>
                                  </div>
                               </motion.div>
                            ))}
                         </div>

                         {/* Recent Orders - Modern List */}
                         <div className="rounded-3xl border border-gray-200 bg-white p-8 dark:border-white/5 dark:bg-[#111]">
                            <div className="flex items-center justify-between mb-8">
                               <div>
                                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">Hoạt động gần đây</h3>
                                  <p className="text-sm text-gray-500 mt-1">Theo dõi các đơn hàng mới nhất của bạn</p>
                               </div>
                               <Button variant="outline" className="rounded-full border-gray-200 dark:border-gray-800 hover:bg-gray-100 dark:hover:bg-gray-800">
                                  Xem tất cả
                               </Button>
                            </div>
                            
                            <div className="space-y-6">
                               {/* Empty state visual */}
                               <div className="py-8 text-center">
                                  <div className="mx-auto h-16 w-16 rounded-full bg-gray-100 flex items-center justify-center mb-3 dark:bg-gray-800">
                                     <Package className="h-8 w-8 text-gray-400" />
                                  </div>
                                  <p className="text-gray-500">Chưa có đơn hàng nào</p>
                               </div>
                            </div>
                         </div>

                         {/* Account Health Banner */}
                         <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-emerald-500 to-teal-600 p-8 text-white shadow-2xl">
                            <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                               <div className="flex items-center gap-5">
                                  <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white/20 backdrop-blur-md shadow-inner">
                                     <Shield className="h-8 w-8 text-white" />
                                  </div>
                                  <div>
                                     <h4 className="text-xl font-bold">Tài khoản được bảo vệ</h4>
                                     <p className="mt-1 text-emerald-100 text-sm max-w-md">Tài khoản của bạn đang ở trạng thái an toàn tuyệt đối. Hãy thường xuyên cập nhật mật khẩu để bảo vệ thông tin.</p>
                                  </div>
                               </div>
                               <Button className="whitespace-nowrap bg-white text-emerald-600 hover:bg-emerald-50 border-none font-bold shadow-lg rounded-xl h-12 px-6">
                                  Kiểm tra bảo mật
                               </Button>
                            </div>
                            {/* Decorative background circles */}
                            <div className="absolute top-0 right-0 -mr-12 -mt-12 h-64 w-64 rounded-full bg-white/10 blur-3xl"></div>
                            <div className="absolute bottom-0 left-0 -ml-12 -mb-12 h-40 w-40 rounded-full bg-black/10 blur-2xl"></div>
                         </div>
                      </div>
                   )}

                   {activeTab === 'security' && (
                      <div className="space-y-6">
                         <Card className="divide-y divide-gray-100 overflow-hidden dark:divide-gray-800 dark:bg-[#111]">
                            <div className="p-6 sm:flex sm:items-center sm:justify-between">
                               <div>
                                  <p className="font-bold text-gray-900 dark:text-white">Mật khẩu</p>
                                  <p className="mt-1 text-sm text-gray-500">Cập nhật mật khẩu định kỳ để bảo vệ tài khoản</p>
                               </div>
                               <Button variant="outline" className="mt-4 sm:mt-0" onClick={() => navigate("/account/change-password")}>
                                 Đổi mật khẩu
                               </Button>
                            </div>
                            <div className="p-6 sm:flex sm:items-center sm:justify-between">
                               <div>
                                  <p className="font-bold text-gray-900 dark:text-white">Xác thực 2 bước (2FA)</p>
                                  <p className="mt-1 text-sm text-gray-500">Tăng cường bảo mật với mã xác thực qua điện thoại</p>
                               </div>
                               <Button variant="secondary" className="mt-4 sm:mt-0 text-orange-600 bg-orange-50 hover:bg-orange-100 dark:bg-orange-900/20 dark:hover:bg-orange-900/30" onClick={() => toast("Tính năng đang phát triển")}>
                                 Kích hoạt ngay
                               </Button>
                            </div>
                            <div className="p-6 sm:flex sm:items-center sm:justify-between bg-red-50/50 dark:bg-red-900/5">
                               <div>
                                  <p className="font-bold text-red-600 dark:text-red-500">Xóa tài khoản</p>
                                  <p className="mt-1 text-sm text-red-600/70 dark:text-red-400/70">Hành động này không thể hoàn tác, mọi dữ liệu sẽ bị xóa</p>
                               </div>
                               <Button variant="ghost" className="mt-4 sm:mt-0 text-red-600 hover:bg-red-100 hover:text-red-700 dark:hover:bg-red-900/30">
                                 Xóa vĩnh viễn
                               </Button>
                            </div>
                         </Card>
                      </div>
                   )}
                   
                   {/* Placeholder for other tabs */}
                   {(activeTab !== 'overview' && activeTab !== 'security') && (
                      <motion.div 
                        initial={{ opacity: 0, scale: 0.95 }} 
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex min-h-[400px] flex-col items-center justify-center rounded-3xl border border-dashed border-gray-300 bg-gray-50 p-12 text-center dark:border-gray-800 dark:bg-[#111]"
                      >
                         <div className="relative mb-6">
                            <div className="absolute inset-0 animate-ping rounded-full bg-orange-500/20 opacity-75"></div>
                            <div className="relative flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-orange-400 to-red-500 shadow-xl">
                               <Package className="h-10 w-10 text-white" />
                            </div>
                         </div>
                         <h3 className="text-2xl font-bold text-gray-900 dark:text-white">Tính năng đang phát triển</h3>
                         <p className="mt-2 max-w-sm text-gray-500">Chúng tôi đang nỗ lực hoàn thiện tính năng này để mang lại trải nghiệm tốt nhất cho bạn.</p>
                         <Button variant="outline" className="mt-8" onClick={() => setActiveTab('overview')}>
                            Quay lại tổng quan
                         </Button>
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
import { Link, useNavigate, useSearchParams } from "react-router";
import {
  Search,
  ShoppingCart,
  Heart,
  User,
  Menu,
  X,
  ChevronDown,
  LogOut,
  Package,
  Settings,
  Store,
  HelpCircle,
  Phone,
  Truck,
  Bell
} from "lucide-react";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "~/components/ui";
import { useAuthStore, useUIStore, useWishlistStore } from "~/lib/stores";
import { useCart } from "~/lib/query"; // Sử dụng Hook React Query thay vì Store cũ
import { cn } from "~/lib/utils";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "~/components/ui/dropdown-menu";
import { Avatar } from "~/components/ui/avatar";

export function Header() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  // Stores
  const { user, isAuthenticated, logout } = useAuthStore();
  
  // Cart Data from React Query (Real-time sync)
  const { data: cart } = useCart();
  const itemCount = cart?.item_count || 0;

  const { items: wishlistItems } = useWishlistStore();
  const { toggleMobileMenu, toggleCartSidebar, isMobileMenuOpen } = useUIStore();

  // Local State
  const [searchQuery, setSearchQuery] = useState(searchParams.get("q") || "");
  const [isScrolled, setIsScrolled] = useState(false);
  const [isSearchFocused, setIsSearchFocused] = useState(false);

  // Sync search input with URL param
  useEffect(() => {
    setSearchQuery(searchParams.get("q") || "");
  }, [searchParams]);

  // Handle Scroll Effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <header 
      className={cn(
        "sticky top-0 z-40 w-full transition-all duration-300",
        isScrolled 
          ? "border-b border-gray-200/80 bg-white/95 shadow-sm backdrop-blur-md dark:border-gray-800/80 dark:bg-gray-950/95" 
          : "border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950"
      )}
    >
      {/* 1. Top Bar (Desktop Only) */}
      <div className="hidden border-b border-gray-100 bg-gray-50 py-2 text-xs font-medium text-gray-600 dark:border-gray-800 dark:bg-gray-900/50 dark:text-gray-400 lg:block">
        <div className="container mx-auto flex items-center justify-between px-4">
          <div className="flex items-center gap-6">
            <span className="flex items-center gap-1.5 hover:text-orange-600 cursor-pointer transition-colors">
              <Phone className="h-3.5 w-3.5" />
              Hotline: <span className="font-bold">1900 1234</span>
            </span>
            <Link to="/seller" className="flex items-center gap-1.5 hover:text-orange-600 transition-colors">
              <Store className="h-3.5 w-3.5" />
              Kênh Người Bán
            </Link>
          </div>
          <div className="flex items-center gap-6">
            <Link to="/help" className="flex items-center gap-1.5 hover:text-orange-600 transition-colors">
              <HelpCircle className="h-3.5 w-3.5" />
              Trợ giúp
            </Link>
            <span className="flex items-center gap-1.5">
              <Truck className="h-3.5 w-3.5" />
              Tra cứu đơn hàng
            </span>
            {!isAuthenticated && (
              <div className="flex items-center gap-3 border-l border-gray-200 pl-4 dark:border-gray-700">
                <Link to="/register" className="hover:text-orange-600 transition-colors">Đăng ký</Link>
                <Link to="/login" className="hover:text-orange-600 transition-colors">Đăng nhập</Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 2. Main Header */}
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between gap-4 lg:h-20">
          
          {/* Mobile Menu Toggle */}
          <button
            onClick={toggleMobileMenu}
            className="flex h-10 w-10 items-center justify-center rounded-xl hover:bg-gray-100 lg:hidden dark:hover:bg-gray-800"
          >
            {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>

          {/* Logo */}
          <Link to="/" className="flex-shrink-0">
            <span className="flex items-center gap-2 text-2xl font-black tracking-tighter text-gray-900 dark:text-white">
              <span className="text-4xl text-orange-500">🦉</span>
              <span className="hidden sm:inline-block">OWLS</span>
            </span>
          </Link>

          {/* Search Bar (Desktop & Tablet) */}
          <div className="hidden flex-1 max-w-2xl px-8 lg:block">
            <form onSubmit={handleSearch} className="relative group">
              <div className={cn(
                "flex h-11 w-full items-center overflow-hidden rounded-full border-2 transition-all duration-300",
                isSearchFocused 
                  ? "border-orange-500 shadow-[0_0_0_4px_rgba(249,115,22,0.1)] bg-white dark:bg-gray-900" 
                  : "border-gray-100 bg-gray-100 dark:border-gray-800 dark:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-700"
              )}>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onFocus={() => setIsSearchFocused(true)}
                  onBlur={() => setIsSearchFocused(false)}
                  placeholder="Tìm kiếm sản phẩm, thương hiệu..."
                  className="flex-1 bg-transparent px-5 text-sm outline-none placeholder:text-gray-400 dark:text-white"
                />
                <button 
                  type="submit"
                  className="flex h-full w-14 items-center justify-center text-gray-400 transition-colors hover:text-orange-500"
                >
                  <Search className="h-5 w-5" />
                </button>
              </div>
            </form>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-1.5 sm:gap-2">
            
            {/* Mobile Search Trigger */}
            <Link to="/search" className="flex h-10 w-10 items-center justify-center rounded-full hover:bg-gray-100 lg:hidden dark:hover:bg-gray-800">
              <Search className="h-5 w-5" />
            </Link>

            {/* Wishlist */}
            <Link 
              to="/wishlist" 
              className="relative hidden h-10 w-10 items-center justify-center rounded-full text-gray-600 transition-colors hover:bg-orange-50 hover:text-orange-600 sm:flex dark:text-gray-300 dark:hover:bg-orange-900/20"
              title="Yêu thích"
            >
              <Heart className="h-5 w-5" />
              {wishlistItems.length > 0 && (
                <span className="absolute right-0 top-0 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white ring-2 ring-white dark:ring-gray-950">
                  {wishlistItems.length}
                </span>
              )}
            </Link>

            {/* Cart Sidebar Trigger */}
            <button 
              onClick={toggleCartSidebar}
              className="relative flex h-10 w-10 items-center justify-center rounded-full text-gray-600 transition-colors hover:bg-orange-50 hover:text-orange-600 dark:text-gray-300 dark:hover:bg-orange-900/20"
              title="Giỏ hàng"
            >
              <ShoppingCart className="h-5 w-5" />
              <AnimatePresence>
                {itemCount > 0 && (
                  <motion.span
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    exit={{ scale: 0 }}
                    className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-orange-500 text-[10px] font-bold text-white ring-2 ring-white dark:ring-gray-950"
                  >
                    {itemCount > 99 ? "99+" : itemCount}
                  </motion.span>
                )}
              </AnimatePresence>
            </button>

            {/* User Dropdown */}
            {isAuthenticated ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="ml-2 flex items-center gap-2 rounded-full border border-gray-200 bg-white py-1 pl-1 pr-3 transition-all hover:border-orange-200 hover:shadow-md dark:border-gray-700 dark:bg-gray-900 dark:hover:border-gray-600">
                    <Avatar 
                      src={user?.avatar || undefined} 
                      alt={user?.full_name} 
                      fallback={user?.first_name?.[0]} 
                      className="h-8 w-8"
                    />
                    <div className="hidden flex-col items-start text-left sm:flex">
                      <span className="w-20 truncate text-xs font-bold text-gray-900 dark:text-gray-100">
                        {user?.last_name}
                      </span>
                    </div>
                    <ChevronDown className="h-3 w-3 text-gray-400" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-60 p-2">
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">{user?.full_name}</p>
                      <p className="text-xs leading-none text-gray-500">{user?.email}</p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild className="cursor-pointer rounded-lg p-2.5 focus:bg-orange-50 dark:focus:bg-gray-800">
                    <Link to="/account">
                      <User className="mr-2 h-4 w-4 text-gray-500" />
                      <span>Hồ sơ cá nhân</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild className="cursor-pointer rounded-lg p-2.5 focus:bg-orange-50 dark:focus:bg-gray-800">
                    <Link to="/account/orders">
                      <Package className="mr-2 h-4 w-4 text-gray-500" />
                      <span>Đơn mua</span>
                    </Link>
                  </DropdownMenuItem>
                  
                  {user?.is_vendor && (
                    <>
                      <DropdownMenuSeparator />
                      <DropdownMenuLabel className="text-xs text-orange-600 dark:text-orange-500">
                        Kênh Người Bán
                      </DropdownMenuLabel>
                      <DropdownMenuItem asChild className="cursor-pointer rounded-lg p-2.5 focus:bg-orange-50 dark:focus:bg-gray-800">
                        <Link to="/seller">
                          <Store className="mr-2 h-4 w-4 text-orange-500" />
                          <span>Quản lý Shop</span>
                        </Link>
                      </DropdownMenuItem>
                    </>
                  )}
                  
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild className="cursor-pointer rounded-lg p-2.5 focus:bg-orange-50 dark:focus:bg-gray-800">
                    <Link to="/account/settings">
                      <Settings className="mr-2 h-4 w-4 text-gray-500" />
                      <span>Cài đặt</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem 
                    onClick={handleLogout}
                    className="cursor-pointer rounded-lg p-2.5 text-red-600 focus:bg-red-50 focus:text-red-600 dark:focus:bg-red-950/30"
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Đăng xuất</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <div className="ml-2 hidden items-center gap-3 sm:flex">
                 <Link to="/auth/login">
                  <Button variant="ghost" className="font-semibold text-gray-600 hover:text-orange-600 hover:bg-orange-50">
                    Đăng nhập
                  </Button>
                </Link>
                <Link to="/auth/register">
                  <Button className="rounded-full bg-orange-500 px-6 font-bold text-white shadow-lg shadow-orange-500/20 hover:bg-orange-600 hover:shadow-orange-500/40">
                    Đăng ký
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 3. Mobile Menu Overlay */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={toggleMobileMenu}
              className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
            />
            <motion.div
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="fixed bottom-0 left-0 top-0 z-50 w-[280px] bg-white shadow-2xl dark:bg-gray-950 lg:hidden"
            >
              <div className="flex h-full flex-col">
                {/* Header */}
                <div className="flex items-center justify-between border-b border-gray-100 p-4 dark:border-gray-800">
                  <span className="text-xl font-black tracking-tight text-orange-500">OWLS</span>
                  <button onClick={toggleMobileMenu} className="rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-800">
                    <X className="h-5 w-5" />
                  </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-4">
                  {isAuthenticated ? (
                    <div className="mb-6 rounded-2xl bg-orange-50 p-4 dark:bg-orange-900/10">
                      <div className="flex items-center gap-3">
                        <Avatar src={user?.avatar || undefined} alt={user?.full_name} fallback={user?.first_name?.[0]} />
                        <div className="overflow-hidden">
                          <p className="truncate font-bold text-gray-900 dark:text-white">{user?.full_name}</p>
                          <p className="truncate text-xs text-gray-500">{user?.email}</p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="mb-6 grid grid-cols-2 gap-3">
                      <Link to="/login" onClick={toggleMobileMenu}>
                        <Button variant="outline" className="w-full justify-center">Đăng nhập</Button>
                      </Link>
                      <Link to="/register" onClick={toggleMobileMenu}>
                        <Button className="w-full justify-center bg-orange-500 text-white hover:bg-orange-600">Đăng ký</Button>
                      </Link>
                    </div>
                  )}

                  <nav className="space-y-1">
                    <p className="mb-2 px-2 text-xs font-bold uppercase text-gray-400">Mua sắm</p>
                    {[
                      { to: "/", label: "Trang chủ", icon: Store },
                      { to: "/products", label: "Tất cả sản phẩm", icon: Package },
                      { to: "/categories", label: "Danh mục", icon: Menu },
                      { to: "/shops", label: "Cửa hàng", icon: Truck },
                      { to: "/search", label: "Tìm kiếm", icon: Search },
                    ].map((item) => (
                      <Link
                        key={item.to}
                        to={item.to}
                        onClick={toggleMobileMenu}
                        className="flex items-center gap-3 rounded-xl px-3 py-2.5 font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800"
                      >
                        <item.icon className="h-5 w-5 text-gray-500" />
                        {item.label}
                      </Link>
                    ))}

                    <div className="my-4 border-t border-gray-100 dark:border-gray-800" />
                    
                    <p className="mb-2 px-2 text-xs font-bold uppercase text-gray-400">Cá nhân</p>
                    <Link to="/wishlist" onClick={toggleMobileMenu} className="flex items-center gap-3 rounded-xl px-3 py-2.5 font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800">
                      <Heart className="h-5 w-5 text-gray-500" />
                      Yêu thích
                    </Link>
                    {isAuthenticated && (
                       <>
                        <Link to="/account/orders" onClick={toggleMobileMenu} className="flex items-center gap-3 rounded-xl px-3 py-2.5 font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800">
                          <Package className="h-5 w-5 text-gray-500" />
                          Đơn hàng
                        </Link>
                        <Link to="/account/settings" onClick={toggleMobileMenu} className="flex items-center gap-3 rounded-xl px-3 py-2.5 font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800">
                          <Settings className="h-5 w-5 text-gray-500" />
                          Cài đặt
                        </Link>
                        <button 
                          onClick={() => {
                            handleLogout();
                            toggleMobileMenu();
                          }}
                          className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 font-medium text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                        >
                          <LogOut className="h-5 w-5" />
                          Đăng xuất
                        </button>
                       </>
                    )}
                  </nav>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </header>
  );
}
import { Link, useNavigate } from "react-router";
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
  Grid3X3,
  Sparkles,
  Tag,
  Truck,
  Phone,
  HelpCircle,
} from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "~/components/ui";
import { useAuthStore, useCartStore, useUIStore } from "~/lib/stores";
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
  const { user, isAuthenticated, logout } = useAuthStore();
  const { itemCount } = useCartStore();
  const { toggleMobileMenu, toggleCartSidebar, isMobileMenuOpen } = useUIStore();
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  // Track scroll for header style
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
    <header className={cn(
      "sticky top-0 z-50 w-full transition-all duration-300",
      isScrolled 
        ? "border-b border-gray-200/80 bg-white/95 shadow-sm backdrop-blur-lg dark:border-gray-800/80 dark:bg-gray-950/95" 
        : "border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950"
    )}>
      {/* Top bar */}
      <div className="hidden border-b border-gray-100 bg-gradient-to-r from-orange-50 to-amber-50 py-2 text-xs text-gray-600 dark:border-gray-800 dark:from-gray-900 dark:to-gray-900 dark:text-gray-400 lg:block">
        <div className="container mx-auto flex items-center justify-between px-4">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <Phone className="h-3.5 w-3.5 text-orange-500" />
              Hotline: <strong className="text-orange-600">1900 1234</strong>
            </span>
            <span className="text-gray-300">|</span>
            <Link to="/seller" className="flex items-center gap-1 transition-colors hover:text-orange-500">
              <Store className="h-3.5 w-3.5" />
              Bán hàng cùng OWLS
            </Link>
            <span className="text-gray-300">|</span>
            <Link to="/help" className="flex items-center gap-1 transition-colors hover:text-orange-500">
              <HelpCircle className="h-3.5 w-3.5" />
              Trợ giúp
            </Link>
          </div>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5">
              <Truck className="h-3.5 w-3.5 text-green-500" />
              Miễn phí vận chuyển đơn từ 500K
            </span>
            {!isAuthenticated && (
              <>
                <span className="text-gray-300">|</span>
                <Link to="/register" className="font-medium transition-colors hover:text-orange-500">
                  Đăng ký
                </Link>
                <span className="text-gray-300">|</span>
                <Link to="/login" className="font-medium transition-colors hover:text-orange-500">
                  Đăng nhập
                </Link>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Main header */}
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between gap-4 lg:h-20">
          {/* Mobile menu button */}
          <motion.button
            onClick={toggleMobileMenu}
            className="flex h-10 w-10 items-center justify-center rounded-xl bg-gray-100 lg:hidden dark:bg-gray-800"
            aria-label="Menu"
            whileTap={{ scale: 0.95 }}
          >
            <AnimatePresence mode="wait">
              {isMobileMenuOpen ? (
                <motion.div
                  key="close"
                  initial={{ rotate: -90, opacity: 0 }}
                  animate={{ rotate: 0, opacity: 1 }}
                  exit={{ rotate: 90, opacity: 0 }}
                >
                  <X className="h-5 w-5" />
                </motion.div>
              ) : (
                <motion.div
                  key="menu"
                  initial={{ rotate: 90, opacity: 0 }}
                  animate={{ rotate: 0, opacity: 1 }}
                  exit={{ rotate: -90, opacity: 0 }}
                >
                  <Menu className="h-5 w-5" />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.button>

          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <motion.span 
              className="text-2xl font-bold lg:text-3xl"
              whileHover={{ scale: 1.02 }}
            >
              <span className="text-orange-500">🦉 OWLS</span>
            </motion.span>
          </Link>

          {/* Search bar - Desktop */}
          <form
            onSubmit={handleSearch}
            className="hidden flex-1 max-w-2xl lg:flex"
          >
            <div className="relative w-full">
              <div className={cn(
                "relative flex overflow-hidden rounded-2xl border-2 transition-all duration-300 bg-gray-100 dark:bg-gray-800",
                isSearchFocused 
                  ? "border-orange-500 shadow-lg shadow-orange-500/10" 
                  : "border-gray-200 dark:border-gray-700"
              )}>
                <input
                  type="text"
                  placeholder="Tìm kiếm sản phẩm, thương hiệu, và hơn thế nữa..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onFocus={() => setIsSearchFocused(true)}
                  onBlur={() => setIsSearchFocused(false)}
                  className="flex-1 bg-transparent py-3 pl-5 pr-4 text-sm text-gray-900 outline-none placeholder:text-gray-500 dark:text-white dark:placeholder:text-gray-400"
                />
                <button
                  type="submit"
                  className="flex items-center justify-center bg-gradient-to-r from-orange-500 to-orange-600 px-6 text-white transition-all hover:from-orange-600 hover:to-orange-700"
                >
                  <Search className="h-5 w-5" />
                </button>
              </div>
            </div>
          </form>

          {/* Right side actions */}
          <div className="flex items-center gap-1 lg:gap-2">
            {/* Search button - Mobile */}
            <Link
              to="/search"
              className="flex h-10 w-10 items-center justify-center rounded-xl text-gray-600 transition-colors hover:bg-gray-100 lg:hidden dark:text-gray-300 dark:hover:bg-gray-800"
            >
              <Search className="h-5 w-5" />
            </Link>

            {/* Wishlist */}
            <Link
              to="/wishlist"
              className="hidden h-10 w-10 items-center justify-center rounded-xl text-gray-600 transition-colors hover:bg-gray-100 hover:text-red-500 sm:flex dark:text-gray-300 dark:hover:bg-gray-800"
              aria-label="Yêu thích"
            >
              <Heart className="h-5 w-5" />
            </Link>

            {/* Cart */}
            <motion.button
              onClick={toggleCartSidebar}
              className="relative flex h-10 w-10 items-center justify-center rounded-xl text-gray-600 transition-colors hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
              aria-label="Giỏ hàng"
              whileTap={{ scale: 0.95 }}
            >
              <ShoppingCart className="h-5 w-5" />
              <AnimatePresence>
                {itemCount > 0 && (
                  <motion.span
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    exit={{ scale: 0 }}
                    className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-gradient-to-r from-orange-500 to-red-500 text-xs font-bold text-white shadow-lg"
                  >
                    {itemCount > 99 ? "99+" : itemCount}
                  </motion.span>
                )}
              </AnimatePresence>
            </motion.button>

            {/* User menu */}
            {isAuthenticated ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="flex items-center gap-2 rounded-xl px-2 py-1.5 transition-colors hover:bg-gray-100 dark:hover:bg-gray-800 lg:px-3 lg:py-2">
                    <Avatar
                      src={user?.avatar || undefined}
                      alt={user?.full_name}
                      fallback={user?.first_name?.[0] || "U"}
                      size="sm"
                    />
                    <span className="hidden max-w-[100px] truncate text-sm font-medium lg:block">
                      {user?.first_name || "Tài khoản"}
                    </span>
                    <ChevronDown className="hidden h-4 w-4 text-gray-400 lg:block" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium">{user?.full_name}</p>
                      <p className="text-xs text-gray-500">{user?.email}</p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link to="/account" className="flex items-center gap-2">
                      <User className="h-4 w-4" />
                      Tài khoản của tôi
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/account/orders" className="flex items-center gap-2">
                      <Package className="h-4 w-4" />
                      Đơn hàng của tôi
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/wishlist" className="flex items-center gap-2">
                      <Heart className="h-4 w-4" />
                      Sản phẩm yêu thích
                    </Link>
                  </DropdownMenuItem>
                  {user?.is_vendor && (
                    <>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem asChild>
                        <Link to="/seller" className="flex items-center gap-2">
                          <Store className="h-4 w-4" />
                          Quản lý cửa hàng
                        </Link>
                      </DropdownMenuItem>
                    </>
                  )}
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link to="/account/settings" className="flex items-center gap-2">
                      <Settings className="h-4 w-4" />
                      Cài đặt
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem 
                    onClick={handleLogout}
                    className="text-red-500 focus:text-red-500"
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    Đăng xuất
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Link to="/login" className="hidden lg:block">
                <Button variant="primary" size="sm">
                  Đăng nhập
                </Button>
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden border-t border-gray-200 bg-white lg:hidden dark:border-gray-800 dark:bg-gray-950"
          >
            <div className="px-4 py-4">
              <form onSubmit={handleSearch} className="mb-4">
                <div className="relative">
              <input
                type="text"
                placeholder="Tìm kiếm sản phẩm..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full rounded-lg border border-gray-300 bg-gray-50 py-2.5 pl-4 pr-12 text-sm focus:border-orange-500 focus:outline-none dark:border-gray-700 dark:bg-gray-900"
              />
              <button
                type="submit"
                className="absolute right-0 top-0 flex h-full items-center justify-center rounded-r-lg bg-orange-500 px-4 text-white"
              >
                <Search className="h-5 w-5" />
              </button>
            </div>
          </form>

          <nav className="space-y-1">
            <Link
              to="/categories"
              className="flex items-center gap-3 rounded-xl px-4 py-3 font-medium transition-colors hover:bg-orange-50 hover:text-orange-600 dark:hover:bg-gray-800"
              onClick={toggleMobileMenu}
            >
              <Grid3X3 className="h-5 w-5" />
              Danh mục
            </Link>
            <Link
              to="/deals"
              className="flex items-center gap-3 rounded-xl px-4 py-3 font-medium transition-colors hover:bg-orange-50 hover:text-orange-600 dark:hover:bg-gray-800"
              onClick={toggleMobileMenu}
            >
              <Tag className="h-5 w-5" />
              Khuyến mãi
            </Link>
            <Link
              to="/shops"
              className="flex items-center gap-3 rounded-xl px-4 py-3 font-medium transition-colors hover:bg-orange-50 hover:text-orange-600 dark:hover:bg-gray-800"
              onClick={toggleMobileMenu}
            >
              <Store className="h-5 w-5" />
              Cửa hàng
            </Link>
            {!isAuthenticated && (
              <>
                <hr className="my-2 border-gray-200 dark:border-gray-700" />
                <Link
                  to="/login"
                  className="flex items-center gap-3 rounded-xl bg-orange-500 px-4 py-3 font-medium text-white"
                  onClick={toggleMobileMenu}
                >
                  Đăng nhập
                </Link>
                <Link
                  to="/register"
                  className="flex items-center gap-3 rounded-xl border border-orange-500 px-4 py-3 font-medium text-orange-500"
                  onClick={toggleMobileMenu}
                >
                  Đăng ký
                </Link>
              </>
            )}
          </nav>
          </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}

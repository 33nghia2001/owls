import { useState, useMemo } from "react";
import { Link, useLoaderData, type LoaderFunctionArgs } from "react-router";
import { motion, AnimatePresence } from "framer-motion";
import { 
  HeartOff, Heart, ShoppingCart, TrendingUp, Tag, 
  Filter, SortAsc, Share2, Trash2, Grid3x3, List,
  Calendar, DollarSign, Star, Package
} from "lucide-react";
import { wishlistApi } from "~/lib/services";
import type { ProductListItem } from "~/lib/types";
import { ProductGrid } from "~/components/product/product-grid";
import { Button, Badge } from "~/components/ui";
import { cn, formatPrice } from "~/lib/utils";
import toast from "react-hot-toast";

export function meta() {
  return [
    { title: "Danh sách yêu thích - OWLS Marketplace" },
    { name: "description", content: "Quản lý và theo dõi các sản phẩm yêu thích của bạn" },
  ];
}

export async function loader({}: LoaderFunctionArgs) {
  try {
    const data = await wishlistApi.getWishlist();
    const products = (data.results || []).map((item: { product: ProductListItem }) => item.product);
    return { products };
  } catch (error) {
    // Return empty array if not authenticated or wishlist doesn't exist
    return { products: [] };
  }
}

export default function WishlistPage() {
  const { products } = useLoaderData<typeof loader>();
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [sortBy, setSortBy] = useState<"newest" | "price-asc" | "price-desc" | "name">("newest");
  const [filterCategory, setFilterCategory] = useState<string>("all");

  // Calculate statistics
  const stats = useMemo(() => {
    const totalValue = products.reduce((sum: number, p: ProductListItem) => {
      const price = parseFloat(p.price?.amount || "0");
      return sum + price;
    }, 0);
    const avgPrice = products.length > 0 ? totalValue / products.length : 0;
    const prices = products.map((p: ProductListItem) => parseFloat(p.price?.amount || "0"));
    const minPrice = products.length > 0 ? Math.min(...prices) : 0;
    const maxPrice = products.length > 0 ? Math.max(...prices) : 0;
    return { totalValue, avgPrice, minPrice, maxPrice };
  }, [products]);

  // Get unique categories
  const categories = useMemo(() => {
    const cats = new Set(products.map((p: ProductListItem) => p.category?.name).filter(Boolean));
    return ["all", ...Array.from(cats)] as string[];
  }, [products]);

  // Filter and sort products
  const filteredProducts = useMemo(() => {
    let filtered = [...products];
    
    // Filter by category
    if (filterCategory !== "all") {
      filtered = filtered.filter((p: ProductListItem) => p.category?.name === filterCategory);
    }

    // Sort
    switch (sortBy) {
      case "price-asc":
        filtered.sort((a: ProductListItem, b: ProductListItem) => {
          const priceA = parseFloat(a.price?.amount || "0");
          const priceB = parseFloat(b.price?.amount || "0");
          return priceA - priceB;
        });
        break;
      case "price-desc":
        filtered.sort((a: ProductListItem, b: ProductListItem) => {
          const priceA = parseFloat(a.price?.amount || "0");
          const priceB = parseFloat(b.price?.amount || "0");
          return priceB - priceA;
        });
        break;
      case "name":
        filtered.sort((a: ProductListItem, b: ProductListItem) => a.name.localeCompare(b.name));
        break;
      default:
        // newest - keep original order
        break;
    }

    return filtered;
  }, [products, filterCategory, sortBy]);

  const handleShare = () => {
    toast.success("Đường dẫn đã được sao chép!");
  };

  const handleClearAll = () => {
    toast.success("Đã xóa tất cả sản phẩm khỏi danh sách yêu thích");
  };

  if (!products.length) {
    return (
      <div className="min-h-screen bg-gray-50/50 dark:bg-[#050505] py-12">
        <div className="container mx-auto px-4">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex min-h-[60vh] flex-col items-center justify-center text-center"
          >
            {/* Animated Heart Icon */}
            <motion.div 
              className="relative mb-8"
              animate={{ 
                scale: [1, 1.1, 1],
              }}
              transition={{ 
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              <div className="absolute inset-0 rounded-full bg-red-500/20 blur-2xl" />
              <div className="relative flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-red-100 to-pink-100 dark:from-red-900/20 dark:to-pink-900/20">
                <HeartOff className="h-12 w-12 text-red-400 dark:text-red-500" />
              </div>
            </motion.div>

            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-3">
              Danh sách yêu thích trống
            </h1>
            <p className="text-gray-500 dark:text-gray-400 max-w-md mb-8">
              Hãy khám phá và thêm những sản phẩm yêu thích vào danh sách để dễ dàng theo dõi và mua sắm sau này.
            </p>

            <div className="flex flex-col sm:flex-row gap-4">
              <Link to="/products">
                <Button size="lg" className="bg-gradient-to-r from-orange-500 to-red-600 text-white hover:from-orange-600 hover:to-red-700 shadow-lg shadow-orange-500/20">
                  <Package className="mr-2 h-5 w-5" />
                  Khám phá sản phẩm
                </Button>
              </Link>
              <Link to="/">
                <Button size="lg" variant="outline" className="border-gray-200 dark:border-gray-800">
                  Về trang chủ
                </Button>
              </Link>
            </div>

            {/* Decorative Elements */}
            <div className="mt-16 grid grid-cols-3 gap-8 text-sm text-gray-400">
              <div className="flex flex-col items-center gap-2">
                <Heart className="h-8 w-8 text-red-400/30" />
                <span>Lưu yêu thích</span>
              </div>
              <div className="flex flex-col items-center gap-2">
                <TrendingUp className="h-8 w-8 text-orange-400/30" />
                <span>Theo dõi giá</span>
              </div>
              <div className="flex flex-col items-center gap-2">
                <ShoppingCart className="h-8 w-8 text-blue-400/30" />
                <span>Mua nhanh</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50/50 dark:bg-[#050505] py-8">
      <div className="container mx-auto px-4">
        
        {/* Header Section */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-4xl font-black text-gray-900 dark:text-gray-100 flex items-center gap-3">
                <Heart className="h-8 w-8 text-red-500 fill-red-500" />
                Danh sách yêu thích
              </h1>
              <p className="mt-2 text-gray-500 dark:text-gray-400">
                Bạn đang theo dõi <span className="font-bold text-orange-500">{products.length}</span> sản phẩm
              </p>
            </div>
            
            <div className="flex flex-wrap gap-3">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleShare}
                className="border-gray-200 dark:border-gray-800"
              >
                <Share2 className="mr-2 h-4 w-4" />
                Chia sẻ
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleClearAll}
                className="border-red-200 text-red-600 hover:bg-red-50 dark:border-red-900/50 dark:text-red-400 dark:hover:bg-red-900/20"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Xóa tất cả
              </Button>
              <Link to="/products">
                <Button size="sm" className="bg-gradient-to-r from-orange-500 to-red-600 text-white">
                  <Package className="mr-2 h-4 w-4" />
                  Thêm sản phẩm
                </Button>
              </Link>
            </div>
          </div>
        </motion.div>

        {/* Statistics Cards */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4"
        >
          {[
            { 
              label: "Tổng giá trị", 
              value: formatPrice(stats.totalValue), 
              icon: DollarSign, 
              color: "text-green-500", 
              bg: "bg-green-500/10",
              border: "border-green-500/20"
            },
            { 
              label: "Giá trung bình", 
              value: formatPrice(stats.avgPrice), 
              icon: TrendingUp, 
              color: "text-blue-500", 
              bg: "bg-blue-500/10",
              border: "border-blue-500/20"
            },
            { 
              label: "Giá thấp nhất", 
              value: formatPrice(stats.minPrice), 
              icon: Tag, 
              color: "text-orange-500", 
              bg: "bg-orange-500/10",
              border: "border-orange-500/20"
            },
            { 
              label: "Giá cao nhất", 
              value: formatPrice(stats.maxPrice), 
              icon: Star, 
              color: "text-purple-500", 
              bg: "bg-purple-500/10",
              border: "border-purple-500/20"
            },
          ].map((stat, idx) => (
            <motion.div
              key={idx}
              whileHover={{ y: -5 }}
              className={cn(
                "rounded-2xl border bg-white p-6 dark:bg-[#111] backdrop-blur-sm shadow-sm",
                stat.border
              )}
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    {stat.label}
                  </p>
                  <h4 className="mt-2 text-xl font-black text-gray-900 dark:text-white">
                    {stat.value}
                  </h4>
                </div>
                <div className={cn("rounded-xl p-2.5", stat.bg)}>
                  <stat.icon className={cn("h-5 w-5", stat.color)} />
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Filters and Controls */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="mb-6 rounded-2xl border border-gray-200 bg-white p-4 dark:border-white/5 dark:bg-[#111]"
        >
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            
            {/* Category Filter */}
            <div className="flex items-center gap-2 flex-wrap">
              <Filter className="h-5 w-5 text-gray-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Danh mục:</span>
              <div className="flex gap-2 flex-wrap">
                {categories.map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setFilterCategory(cat)}
                    className={cn(
                      "rounded-lg px-4 py-1.5 text-sm font-medium transition-all",
                      filterCategory === cat
                        ? "bg-orange-500 text-white shadow-lg shadow-orange-500/20"
                        : "bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-white/5 dark:text-gray-400 dark:hover:bg-white/10"
                    )}
                  >
                    {cat === "all" ? "Tất cả" : cat}
                  </button>
                ))}
              </div>
            </div>

            {/* Sort and View Mode */}
            <div className="flex items-center gap-3">
              {/* Sort */}
              <div className="flex items-center gap-2">
                <SortAsc className="h-5 w-5 text-gray-400" />
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 dark:border-gray-800 dark:bg-[#0a0a0a] dark:text-gray-300"
                >
                  <option value="newest">Mới nhất</option>
                  <option value="price-asc">Giá: Thấp → Cao</option>
                  <option value="price-desc">Giá: Cao → Thấp</option>
                  <option value="name">Tên A-Z</option>
                </select>
              </div>

              {/* View Mode Toggle */}
              <div className="flex gap-1 rounded-lg border border-gray-200 bg-gray-50 p-1 dark:border-gray-800 dark:bg-white/5">
                <button
                  onClick={() => setViewMode("grid")}
                  className={cn(
                    "rounded-md p-2 transition-all",
                    viewMode === "grid"
                      ? "bg-white text-orange-500 shadow-sm dark:bg-[#111]"
                      : "text-gray-400 hover:text-gray-600"
                  )}
                >
                  <Grid3x3 className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setViewMode("list")}
                  className={cn(
                    "rounded-md p-2 transition-all",
                    viewMode === "list"
                      ? "bg-white text-orange-500 shadow-sm dark:bg-[#111]"
                      : "text-gray-400 hover:text-gray-600"
                  )}
                >
                  <List className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Active Filters Display */}
          {filterCategory !== "all" && (
            <div className="mt-3 flex items-center gap-2 pt-3 border-t border-gray-100 dark:border-white/5">
              <span className="text-xs text-gray-500">Đang lọc:</span>
              <Badge className="bg-orange-500/10 text-orange-500 border-orange-500/20">
                {filterCategory}
                <button 
                  onClick={() => setFilterCategory("all")}
                  className="ml-2 hover:text-orange-700"
                >
                  ×
                </button>
              </Badge>
            </div>
          )}
        </motion.div>

        {/* Products Display */}
        <AnimatePresence mode="wait">
          <motion.div
            key={viewMode}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {filteredProducts.length === 0 ? (
              <div className="flex min-h-[300px] flex-col items-center justify-center rounded-2xl border border-dashed border-gray-300 bg-gray-50 p-12 dark:border-gray-800 dark:bg-[#111]">
                <Filter className="h-12 w-12 text-gray-400 mb-3" />
                <p className="text-gray-500 dark:text-gray-400">
                  Không tìm thấy sản phẩm với bộ lọc này
                </p>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="mt-4"
                  onClick={() => {
                    setFilterCategory("all");
                    setSortBy("newest");
                  }}
                >
                  Xóa bộ lọc
                </Button>
              </div>
            ) : (
              <ProductGrid products={filteredProducts} />
            )}
          </motion.div>
        </AnimatePresence>

        {/* Bottom Action Bar */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-12 rounded-2xl border border-gray-200 bg-gradient-to-r from-orange-50 to-red-50 p-6 dark:from-orange-900/10 dark:to-red-900/10 dark:border-white/5"
        >
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                Sẵn sàng mua sắm?
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Thêm các sản phẩm yêu thích vào giỏ hàng và thanh toán ngay
              </p>
            </div>
            <Link to="/cart">
              <Button size="lg" className="bg-gradient-to-r from-orange-500 to-red-600 text-white shadow-lg shadow-orange-500/20">
                <ShoppingCart className="mr-2 h-5 w-5" />
                Xem giỏ hàng
              </Button>
            </Link>
          </div>
        </motion.div>

      </div>
    </div>
  );
}

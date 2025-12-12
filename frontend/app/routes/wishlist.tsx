import { Link } from "react-router";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Heart, 
  ShoppingCart, 
  Trash2, 
  ArrowRight, 
  Package, 
  AlertCircle 
} from "lucide-react";
import { useWishlistStore } from "~/lib/stores";
import { useAddToCart } from "~/lib/query"; // Use React Query hook instead of Store
import { useEffect, useState } from "react";
import { useWishlist } from "~/lib/query/hooks";
import { productsApi } from "~/lib/services";
import { formatCurrency, cn, parsePrice } from "~/lib/utils";
import { Button } from "~/components/ui";
import toast from "react-hot-toast";

// --- META ---
export function meta() {
  return [
    { title: "Sản phẩm yêu thích - OWLS Marketplace" },
    { name: "description", content: "Danh sách sản phẩm bạn đã lưu" },
  ];
}

export default function WishlistPage() {
  const { items: wishlistIds, removeItem, clearWishlist } = useWishlistStore();
  const addToCartMutation = useAddToCart(); // Use React Query mutation
  const wishlistQuery = useWishlist();

  const [localProducts, setLocalProducts] = useState<any[]>([]);

  // If user is authenticated the query will return full product objects.
  // For guest local wishlist (stored as IDs) we fetch product details.
  useEffect(() => {
    const loadLocal = async () => {
      if (!wishlistIds || wishlistIds.length === 0) {
        setLocalProducts([]);
        return;
      }
      try {
        const proms = wishlistIds.map((id) => productsApi.getProduct(id).catch(() => null));
        const results = await Promise.all(proms);
        setLocalProducts(results.filter(Boolean));
      } catch (e) {
        setLocalProducts([]);
      }
    };
    loadLocal();
  }, [wishlistIds]);

  const handleAddToCart = (product: any) => {
    // Use React Query mutation for consistent cart state management
    addToCartMutation.mutate(
      {
        productId: product.id,
        quantity: 1,
        // Note: If product has variants, this should open a modal to select
      },
      {
        onSuccess: () => toast.success("Đã thêm vào giỏ hàng"),
        onError: () => toast.error("Lỗi khi thêm vào giỏ"),
      }
    );
  };

  const handleRemove = (id: string, name?: string) => {
    removeItem(id);
    toast.success(`Đã xóa ${name || "sản phẩm"} khỏi danh sách yêu thích`);
  };

  const handleClearAll = () => {
    if (confirm("Bạn có chắc chắn muốn xóa tất cả sản phẩm yêu thích?")) {
      clearWishlist();
      toast.success("Đã xóa toàn bộ danh sách");
    }
  };

  // Determine products list to render
  const products = wishlistQuery.data
    ? (wishlistQuery.data.results || []).map((r: any) => r.product)
    : localProducts;

  // --- EMPTY STATE ---
  if (!products || products.length === 0) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center bg-gray-50/50 dark:bg-[#050505] px-4">
        <div className="relative mb-6">
          <div className="absolute inset-0 animate-ping rounded-full bg-orange-100 opacity-75 dark:bg-orange-900/20" />
          <div className="relative flex h-24 w-24 items-center justify-center rounded-full bg-white shadow-lg dark:bg-gray-900 dark:shadow-orange-900/10">
            <Heart className="h-10 w-10 text-gray-300 dark:text-gray-600" />
          </div>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Danh sách yêu thích trống
        </h2>
        <p className="mt-2 max-w-sm text-center text-gray-500 dark:text-gray-400">
          Bạn chưa lưu sản phẩm nào. Hãy khám phá thêm các sản phẩm thú vị tại OWLS nhé!
        </p>
        <Link to="/products" className="mt-8">
          <Button size="lg" className="rounded-full px-8 bg-orange-500 hover:bg-orange-600 shadow-lg shadow-orange-500/20">
            Khám phá ngay <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </Link>
      </div>
    );
  }

  // --- MAIN CONTENT ---
  return (
    <div className="min-h-screen bg-gray-50/50 dark:bg-[#050505] py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8 flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
            <div>
            <h1 className="flex items-center gap-3 text-3xl font-bold text-gray-900 dark:text-gray-100">
              <Heart className="h-8 w-8 text-red-500 fill-red-500" />
              Sản phẩm yêu thích
            </h1>
            <p className="mt-1 text-gray-500 dark:text-gray-400">
              Bạn đang lưu <span className="font-medium text-gray-900 dark:text-gray-100">{products.length}</span> sản phẩm
            </p>
          </div>
          
          <Button 
            variant="outline" 
            onClick={handleClearAll}
            className="text-red-500 hover:bg-red-50 hover:text-red-600 hover:border-red-200 dark:hover:bg-red-950/30"
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Xóa tất cả
          </Button>
        </div>

        {/* Grid */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          <AnimatePresence mode="popLayout">
              {products.map((item: any) => (
              <motion.div
                key={item.id}
                layout
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
                className="group relative flex flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm transition-all hover:shadow-md dark:border-gray-800 dark:bg-gray-900"
              >
                {/* Remove Button (Top Right) */}
                <button
                  onClick={() => handleRemove(item.id, item.name)}
                  className="absolute right-3 top-3 z-10 rounded-full bg-white/80 p-2 text-gray-400 backdrop-blur-sm transition-colors hover:bg-red-50 hover:text-red-500 dark:bg-black/50 dark:hover:bg-red-900/30"
                  title="Xóa khỏi danh sách"
                >
                  <Trash2 className="h-4 w-4" />
                </button>

                {/* Image */}
                <Link to={`/products/${item.slug}`} className="relative aspect-square overflow-hidden bg-gray-100 dark:bg-gray-800">
                  {item.primary_image ? (
                    <img
                      src={item.primary_image.image}
                      alt={item.name}
                      className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                    />
                  ) : (
                    <div className="flex h-full w-full items-center justify-center text-gray-400">
                      <Package className="h-10 w-10" />
                    </div>
                  )}
                  {/* Stock Badge */}
                  {(item.quantity || 0) <= 0 && (
                    <div className="absolute bottom-2 left-2 flex items-center gap-1 rounded-md bg-black/60 px-2 py-1 text-xs font-medium text-white backdrop-blur-sm">
                      <AlertCircle className="h-3 w-3" /> Hết hàng
                    </div>
                  )}
                </Link>

                {/* Info */}
                <div className="flex flex-1 flex-col p-4">
                  <Link to={`/products/${item.slug}`} className="flex-1">
                    <h3 className="line-clamp-2 text-sm font-medium text-gray-900 hover:text-orange-500 dark:text-gray-100 transition-colors">
                      {item.name}
                    </h3>
                  </Link>
                  
                  <div className="mt-3 flex items-end justify-between">
                    <div className="flex flex-col">
                      <span className="text-lg font-bold text-orange-600 dark:text-orange-500">
                        {formatCurrency(parsePrice(item.price))}
                      </span>
                      {item.compare_price && parseFloat(item.compare_price) > parseFloat(item.price) && (
                        <span className="text-xs text-gray-400 line-through">
                          {formatCurrency(parsePrice(item.compare_price))}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Add to Cart Button */}
                  <Button
                    onClick={() => handleAddToCart(item)}
                    disabled={(item.quantity || 0) <= 0}
                    className="mt-4 w-full gap-2 rounded-xl bg-gray-900 text-white hover:bg-orange-600 dark:bg-gray-800 dark:hover:bg-orange-600"
                  >
                    <ShoppingCart className="h-4 w-4" />
                    {(item.quantity || 0) > 0 ? "Thêm vào giỏ" : "Hết hàng"}
                  </Button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
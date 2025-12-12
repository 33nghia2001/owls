import { Link, useNavigate } from "react-router";
import { Heart, ShoppingCart, Star, Eye, Settings2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import type { ProductListItem } from "~/lib/types";
import { formatCurrency, getImageUrl, cn, parsePrice } from "~/lib/utils";
import { useWishlistStore } from "~/lib/stores";
import { useAddToCart } from "~/lib/query"; // Sử dụng Hook thay vì Store
import { useState } from "react";
import { toast } from "~/components/ui/toast";

interface ProductCardProps {
  product: ProductListItem;
  className?: string;
  index?: number;
}

export function ProductCard({ product, className, index = 0 }: ProductCardProps) {
  const navigate = useNavigate();
  
  // Thay thế useCartStore bằng Mutation Hook từ React Query
  const addToCartMutation = useAddToCart();
  
  const { isInWishlist, addItem, removeItem } = useWishlistStore();
  const [isHovered, setIsHovered] = useState(false);
  
  const inWishlist = isInWishlist(product.id);
  
  // Use parsePrice to safely handle various price formats from backend
  const price = parsePrice(product.price);
  const comparePrice = product.compare_price ? parsePrice(product.compare_price) : null;
  
  // Check if product has variants (requires selection before adding to cart)
  const hasVariants = product.has_variants ?? false;

  const handleAddToCart = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    // If product has variants, redirect to product detail page
    if (hasVariants) {
      navigate(`/products/${product.slug}`);
      toast.info({
        title: "Chọn phiên bản",
        description: "Vui lòng chọn phiên bản sản phẩm trước khi thêm vào giỏ",
      });
      return;
    }
    
    // Thực hiện Mutation thêm vào giỏ
    addToCartMutation.mutate({
      productId: product.id,
      quantity: 1
    }, {
      onSuccess: () => {
        toast.success({
          title: "Đã thêm vào giỏ",
          description: `${product.name} đã được thêm vào giỏ hàng`,
        });
      },
      onError: (error) => {
        if (import.meta.env.DEV) console.error("Failed to add to cart:", error);
        toast.error({
          title: "Lỗi",
          description: "Không thể thêm sản phẩm vào giỏ hàng",
        });
      }
    });
  };

  // Lấy trạng thái loading trực tiếp từ mutation
  const isAddingToCart = addToCartMutation.isPending;

  const handleToggleWishlist = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (inWishlist) {
      await removeItem(product.id);
      toast.info({
        description: "Đã xóa khỏi danh sách yêu thích",
      });
    } else {
      await addItem(product.id);
      toast.success({
        description: "Đã thêm vào danh sách yêu thích",
      });
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.05 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
    >
      <Link
        to={`/products/${product.slug}`}
        className={cn(
          "group relative flex flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white transition-all duration-300",
          "hover:shadow-xl hover:shadow-orange-500/10 hover:-translate-y-1",
          "dark:border-gray-800 dark:bg-gray-950",
          className
        )}
      >
        {/* Image Container */}
        <div className="relative aspect-square overflow-hidden bg-gray-100">
          <motion.img
            src={getImageUrl(product.primary_image?.image)}
            alt={product.name}
            className="h-full w-full object-cover"
            loading="lazy"
            animate={{ scale: isHovered ? 1.08 : 1 }}
            transition={{ duration: 0.4 }}
          />

          {/* Gradient Overlay on Hover */}
          <AnimatePresence>
            {isHovered && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent"
              />
            )}
          </AnimatePresence>

          {/* Badges */}
          <div className="absolute left-3 top-3 flex flex-col gap-2">
            {product.is_on_sale && product.discount_percentage > 0 && (
              <span className="inline-flex items-center rounded-full bg-red-500 px-2.5 py-0.5 text-xs font-bold text-white">
                -{product.discount_percentage}%
              </span>
            )}
          </div>

          {/* Quick Actions */}
          <div className="absolute right-3 top-3 flex flex-col gap-2">
            <motion.button
              onClick={handleToggleWishlist}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className={cn(
                "flex h-10 w-10 items-center justify-center rounded-full backdrop-blur-md transition-colors",
                inWishlist
                  ? "bg-red-500 text-white"
                  : "bg-white/90 text-gray-600 hover:bg-red-500 hover:text-white"
              )}
            >
              <Heart
                className="h-5 w-5"
                fill={inWishlist ? "currentColor" : "none"}
              />
            </motion.button>
            
            <AnimatePresence>
              {isHovered && (
                <motion.button
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: 0.15 }}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex h-10 w-10 items-center justify-center rounded-full bg-white/90 text-gray-600 backdrop-blur-md transition-colors hover:bg-orange-500 hover:text-white"
                >
                  <Eye className="h-5 w-5" />
                </motion.button>
              )}
            </AnimatePresence>
          </div>

          {/* Add to Cart Button */}
          <AnimatePresence>
            {isHovered && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                transition={{ duration: 0.2 }}
                className="absolute bottom-3 left-3 right-3"
              >
                <motion.button
                  onClick={handleAddToCart}
                  disabled={isAddingToCart}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="flex w-full items-center justify-center gap-2 rounded-xl bg-orange-500 px-4 py-3 font-medium text-white shadow-lg shadow-orange-500/30 transition-colors hover:bg-orange-600 disabled:opacity-50"
                >
                  {hasVariants ? (
                    <>
                      <Settings2 className="h-5 w-5" />
                      Tùy chọn
                    </>
                  ) : (
                    <>
                      <ShoppingCart className="h-5 w-5" />
                      {isAddingToCart ? "Đang thêm..." : "Thêm vào giỏ"}
                    </>
                  )}
                </motion.button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Content */}
        <div className="flex flex-1 flex-col p-4">
          {/* Vendor */}
          <p className="mb-1 text-xs font-medium text-gray-500 dark:text-gray-400">
            {product.vendor_name}
          </p>

          {/* Product Name */}
          <h3 className="mb-3 line-clamp-2 flex-1 text-sm font-semibold text-gray-900 transition-colors group-hover:text-orange-500 dark:text-gray-100">
            {product.name}
          </h3>

          {/* Rating & Sold */}
          {product.review_count > 0 && (
            <div className="mb-3 flex items-center gap-2">
              <div className="flex items-center gap-1 rounded-lg bg-yellow-50 px-2 py-1">
                <Star className="h-3.5 w-3.5 fill-yellow-400 text-yellow-400" />
                <span className="text-xs font-bold text-yellow-700">
                  {product.rating.toFixed(1)}
                </span>
              </div>
              <span className="text-xs text-gray-400">
                ({product.review_count} đánh giá)
              </span>
              <span className="ml-auto text-xs text-gray-500">
                Đã bán {product.sold_count.toLocaleString()}
              </span>
            </div>
          )}

          {/* Price */}
          <div className="flex items-end justify-between">
            <div className="flex flex-col">
              {comparePrice && comparePrice > price && (
                <span className="text-xs text-gray-400 line-through">
                  {formatCurrency(comparePrice)}
                </span>
              )}
              <span className="text-xl font-bold text-orange-500">
                {formatCurrency(price)}
              </span>
            </div>
          </div>
        </div>
      </Link>
    </motion.div>
  );
}
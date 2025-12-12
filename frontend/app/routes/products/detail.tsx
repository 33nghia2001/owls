import { useState } from "react";
import { Link, useLoaderData, useNavigate, type LoaderFunctionArgs, type MetaFunction } from "react-router";
import { Star, ShoppingCart, Heart, Truck, Shield } from "lucide-react";
import { productsApi } from "~/lib/services";
import type { Product, ProductVariant, ProductImage } from "~/lib/types";
import { formatCurrency } from "~/lib/utils";
import { useWishlistStore } from "~/lib/stores";
import { useAddToCart } from "~/lib/query"; // Sử dụng Hook từ React Query
import toast from "react-hot-toast";

export const meta: MetaFunction<typeof loader> = ({ data }) => {
  const product = data?.product;
  
  if (!product) {
    return [
      { title: "Sản phẩm không tìm thấy - OWLS Marketplace" },
      { name: "description", content: "Sản phẩm bạn tìm kiếm không tồn tại" },
    ];
  }

  const title = product.meta_title || `${product.name} - OWLS Marketplace`;
  const description = product.meta_description || product.short_description || product.description?.slice(0, 160);
  const image = product.images?.[0]?.image || "/og-default.jpg";
  const price = product.price?.amount;
  const url = `https://owls.vn/products/${product.slug}`;

  return [
    // Basic
    { title },
    { name: "description", content: description },
    
    // Open Graph
    { property: "og:type", content: "product" },
    { property: "og:title", content: title },
    { property: "og:description", content: description },
    { property: "og:image", content: image },
    { property: "og:url", content: url },
    { property: "og:site_name", content: "OWLS Marketplace" },
    
    // Product specific OG
    { property: "product:price:amount", content: price },
    { property: "product:price:currency", content: "VND" },
    { property: "product:availability", content: "in stock" },
    { property: "product:brand", content: product.brand?.name || "OWLS" },
    { property: "product:category", content: product.category?.name || "" },
    
    // Twitter Card
    { name: "twitter:card", content: "summary_large_image" },
    { name: "twitter:title", content: title },
    { name: "twitter:description", content: description },
    { name: "twitter:image", content: image },
    
    // Additional SEO
    { name: "robots", content: "index, follow" },
    { name: "author", content: product.vendor?.shop_name || "OWLS Marketplace" },
    { name: "keywords", content: [product.name, product.category?.name, product.brand?.name, ...product.tags].filter(Boolean).join(", ") },
    
    // Structured Data (JSON-LD)
    {
      "script:ld+json": {
        "@context": "https://schema.org",
        "@type": "Product",
        name: product.name,
        description: description,
        image: product.images?.map((img: { image: string }) => img.image) || [],
        brand: {
          "@type": "Brand",
          name: product.brand?.name || product.vendor?.shop_name,
        },
        offers: {
          "@type": "Offer",
          price: price,
          priceCurrency: "VND",
          availability: "https://schema.org/InStock",
          seller: {
            "@type": "Organization",
            name: product.vendor?.shop_name,
          },
        },
        aggregateRating: product.review_count > 0 ? {
          "@type": "AggregateRating",
          ratingValue: product.rating,
          reviewCount: product.review_count,
        } : undefined,
      },
    },
  ];
};

export async function loader({ params }: LoaderFunctionArgs) {
  const slug = params.slug as string;
  const product = await productsApi.getProduct(slug);
  return { product };
}

export default function ProductDetailPage() {
  const { product } = useLoaderData<typeof loader>();
  const navigate = useNavigate();
  
  // SỬA ĐỔI: Dùng Hook thay vì Store
  const addToCartMutation = useAddToCart();
  
  const addWishlist = useWishlistStore((s) => s.addItem);
  const removeWishlist = useWishlistStore((s) => s.removeItem);
  const isInWishlist = useWishlistStore((s) => s.isInWishlist);
  const [quantity, setQuantity] = useState(1);
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(
    product.variants?.[0] || null
  );

  const inWishlist = isInWishlist(product.id);

  const price = selectedVariant?.price || product.price;
  const compare = selectedVariant?.compare_price || product.compare_price;

  const handleAddToCart = () => {
    addToCartMutation.mutate({
      productId: product.id,
      quantity,
      variantId: selectedVariant?.id
    }, {
      onSuccess: () => {
        toast.success("Đã thêm vào giỏ hàng");
        navigate("/cart");
      },
      onError: () => {
        toast.error("Có lỗi xảy ra khi thêm vào giỏ");
      }
    });
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid gap-8 lg:grid-cols-2">
        <div>
          <div className="overflow-hidden rounded-2xl border border-gray-100 bg-white dark:border-gray-800 dark:bg-gray-900">
            <img
              src={product.images?.[0]?.image || "/placeholder.jpg"}
              alt={product.name}
              className="aspect-square w-full object-cover"
            />
          </div>
          {product.images?.length > 1 && (
            <div className="mt-4 grid grid-cols-4 gap-2">
              {product.images.slice(0, 4).map((img: ProductImage) => (
                <img
                  key={img.id}
                  src={img.image}
                  alt={img.alt_text}
                  className="aspect-square w-full rounded-lg border border-gray-100 object-cover dark:border-gray-800"
                />
              ))}
            </div>
          )}
        </div>

        <div>
          <nav className="mb-3 text-sm text-gray-500">
            <Link to="/">Trang chủ</Link> / {product.category?.name || "Danh mục"}
          </nav>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">{product.name}</h1>
          <div className="mt-2 flex items-center gap-3 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <Star className="h-4 w-4 fill-orange-500 text-orange-500" />
              {product.rating.toFixed(1)} ({product.review_count} đánh giá)
            </span>
            <span>•</span>
            <span>{product.sold_count} đã bán</span>
          </div>

          <div className="mt-4 flex items-center gap-3">
            <p className="text-3xl font-bold text-orange-600">{formatCurrency(price.amount)}</p>
            {compare && (
              <p className="text-lg text-gray-400 line-through">{formatCurrency(compare.amount)}</p>
            )}
            {product.discount_percentage > 0 && (
              <span className="rounded-full bg-red-100 px-3 py-1 text-sm font-semibold text-red-600 dark:bg-red-900/30">
                -{product.discount_percentage}%
              </span>
            )}
          </div>

          <p className="mt-4 text-gray-700 dark:text-gray-300">{product.short_description}</p>

          {product.variants?.length > 0 && (
            <div className="mt-6">
              <p className="mb-2 text-sm font-medium text-gray-900 dark:text-gray-100">Phiên bản</p>
              <div className="flex flex-wrap gap-2">
                {product.variants.map((variant: ProductVariant) => (
                  <button
                    key={variant.id}
                    type="button"
                    onClick={() => setSelectedVariant(variant)}
                    className={`rounded-lg border px-4 py-2 text-sm transition ${
                      selectedVariant?.id === variant.id
                        ? "border-orange-500 bg-orange-50 text-orange-600"
                        : "border-gray-200 text-gray-700 hover:border-orange-500 dark:border-gray-800 dark:text-gray-200"
                    }`}
                  >
                    {variant.name}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="mt-6 flex items-center gap-3">
            <div className="flex items-center rounded-lg border border-gray-200 dark:border-gray-800">
              <button
                type="button"
                className="px-3 py-2 text-lg"
                onClick={() => setQuantity((q) => Math.max(1, q - 1))}
              >
                -
              </button>
              <span className="w-12 text-center text-sm font-medium">{quantity}</span>
              <button type="button" className="px-3 py-2 text-lg" onClick={() => setQuantity((q) => q + 1)}>
                +
              </button>
            </div>
            
            <button
              onClick={handleAddToCart}
              disabled={addToCartMutation.isPending}
              className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-orange-500 px-4 py-3 text-white transition hover:bg-orange-600 disabled:opacity-70"
            >
              <ShoppingCart className="h-5 w-5" /> 
              {addToCartMutation.isPending ? "Đang xử lý..." : "Thêm vào giỏ"}
            </button>
            
            <button
              onClick={() => (inWishlist ? removeWishlist(product.id) : addWishlist(product.id))}
              className={`rounded-lg border px-4 py-3 transition ${
                inWishlist ? "border-red-500 bg-red-50 text-red-500" : "border-gray-200 text-gray-700 hover:border-orange-500"
              }`}
            >
              <Heart className="h-5 w-5" fill={inWishlist ? "currentColor" : "none"} />
            </button>
          </div>

          <div className="mt-6 grid gap-3 rounded-xl border border-gray-100 bg-white p-4 text-sm text-gray-600 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-300">
            <div className="flex items-center gap-2">
              <Truck className="h-4 w-4 text-orange-500" /> Giao hàng nhanh toàn quốc
            </div>
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-orange-500" /> Đổi trả trong 7 ngày
            </div>
          </div>

          <div className="mt-8">
            <h2 className="mb-3 text-xl font-semibold text-gray-900 dark:text-gray-100">Mô tả sản phẩm</h2>
            <p className="whitespace-pre-line text-gray-700 dark:text-gray-300">
              {product.description || "Đang cập nhật"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
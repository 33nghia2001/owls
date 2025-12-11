import { useState } from "react";
import { Link, useLoaderData, useNavigate, type LoaderFunctionArgs } from "react-router";
import { Star, ShoppingCart, Heart, Truck, Shield } from "lucide-react";
import { productsApi } from "~/lib/services";
import type { Product, ProductVariant } from "~/lib/types";
import { formatCurrency } from "~/lib/utils";
import { useCartStore, useWishlistStore } from "~/lib/stores";

export function meta({ data }: { data: { product?: Product } }) {
  return [
    { title: `${data?.product?.name || "Sản phẩm"} - OWLS Marketplace` },
    { name: "description", content: data?.product?.short_description || "Chi tiết sản phẩm" },
  ];
}

export async function loader({ params }: LoaderFunctionArgs) {
  const slug = params.slug as string;
  const product = await productsApi.getProduct(slug);
  return { product };
}

export default function ProductDetailPage() {
  const { product } = useLoaderData<typeof loader>();
  const navigate = useNavigate();
  const addToCart = useCartStore((s) => s.addToCart);
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

  const handleAddToCart = async () => {
    await addToCart(product.id, quantity, selectedVariant?.id);
    navigate("/cart");
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
              {product.images.slice(0, 4).map((img: Product["images"][number]) => (
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
              className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-orange-500 px-4 py-3 text-white transition hover:bg-orange-600"
            >
              <ShoppingCart className="h-5 w-5" /> Thêm vào giỏ
            </button>
            <button
              onClick={() => (inWishlist ? removeWishlist(product.id) : addWishlist(product.id))}
              className={`rounded-lg border px-4 py-3 transition ${
                inWishlist ? "border-red-500 bg-red-50 text-red-500" : "border-gray-200 text-gray-700 hover:border-orange-500"
              }`}
            >
              <Heart className="h-5 w-5" />
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

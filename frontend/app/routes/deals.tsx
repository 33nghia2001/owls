import { Link, useLoaderData } from "react-router";
import { Flame, Timer, Percent, ArrowRight } from "lucide-react";
import { productsApi } from "~/lib/services";
import type { ProductListItem } from "~/lib/types";
import { formatCurrency, parsePrice } from "~/lib/utils";
import { ProductCard } from "~/components/product";

export function meta() {
  return [
    { title: "Khuyến mãi - OWLS Marketplace" },
    { name: "description", content: "Săn deal hot, giảm giá sốc tại OWLS Marketplace" },
  ];
}

export async function clientLoader() {
  try {
    // Fetch products on sale
    const response = await productsApi.getProducts({ 
      is_on_sale: true,
      ordering: "-discount_percentage"
    });
    return { 
      products: response.results || [],
      count: response.count || 0
    };
  } catch {
    return { products: [], count: 0 };
  }
}

export default function DealsPage() {
  const { products, count } = useLoaderData<typeof clientLoader>();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#050505]">
      {/* Hero Banner */}
      <div className="bg-gradient-to-r from-red-600 via-orange-500 to-yellow-500 py-12">
        <div className="container mx-auto px-4 text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Flame className="h-10 w-10 text-white animate-pulse" />
            <h1 className="text-4xl font-bold text-white">Deal Hot Hôm Nay</h1>
            <Flame className="h-10 w-10 text-white animate-pulse" />
          </div>
          <p className="text-white/90 text-lg">
            Săn ngay {count} sản phẩm giảm giá sốc - Số lượng có hạn!
          </p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Flash Deal Section */}
        <div className="mb-8 rounded-2xl bg-white p-6 shadow-sm dark:bg-gray-900">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-100 dark:bg-red-900/30">
                <Timer className="h-5 w-5 text-red-500" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                  Flash Sale
                </h2>
                <p className="text-sm text-gray-500">Kết thúc trong 02:34:56</p>
              </div>
            </div>
            <Link
              to="/products?is_on_sale=true"
              className="flex items-center gap-1 text-orange-500 hover:text-orange-600 font-medium"
            >
              Xem tất cả <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          {products.length > 0 ? (
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
              {products.slice(0, 6).map((product: ProductListItem) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          ) : (
            <div className="py-12 text-center text-gray-500">
              <Percent className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>Chưa có sản phẩm khuyến mãi</p>
            </div>
          )}
        </div>

        {/* All Deals Section */}
        {products.length > 6 && (
          <div className="rounded-2xl bg-white p-6 shadow-sm dark:bg-gray-900">
            <div className="flex items-center gap-3 mb-6">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-orange-100 dark:bg-orange-900/30">
                <Percent className="h-5 w-5 text-orange-500" />
              </div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                Tất cả khuyến mãi
              </h2>
            </div>

            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
              {products.slice(6).map((product: ProductListItem) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {products.length === 0 && (
          <div className="rounded-2xl bg-white p-12 shadow-sm dark:bg-gray-900 text-center">
            <Flame className="h-16 w-16 mx-auto mb-4 text-gray-300" />
            <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
              Chưa có deal nào
            </h3>
            <p className="text-gray-500 mb-6">
              Hãy quay lại sau để săn các deal hấp dẫn nhé!
            </p>
            <Link
              to="/products"
              className="inline-flex items-center gap-2 rounded-lg bg-orange-500 px-6 py-3 text-white font-medium hover:bg-orange-600 transition"
            >
              Khám phá sản phẩm <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}

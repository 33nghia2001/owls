import { Link, useLoaderData, type LoaderFunctionArgs } from "react-router";
import { HeartOff } from "lucide-react";
import { wishlistApi } from "~/lib/services";
import type { ProductListItem } from "~/lib/types";
import { ProductGrid } from "~/components/product/product-grid";

export function meta() {
  return [
    { title: "Yêu thích - OWLS" },
    { name: "description", content: "Danh sách sản phẩm yêu thích" },
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

  if (!products.length) {
    return (
      <div className="container mx-auto flex min-h-[50vh] flex-col items-center justify-center px-4 text-center">
        <HeartOff className="h-12 w-12 text-gray-400" />
        <h1 className="mt-3 text-2xl font-semibold text-gray-900 dark:text-gray-100">Chưa có sản phẩm yêu thích</h1>
        <p className="mt-1 text-gray-500">Thêm sản phẩm vào danh sách để theo dõi.</p>
        <Link
          to="/products"
          className="mt-4 rounded-lg bg-orange-500 px-4 py-2 font-medium text-white transition hover:bg-orange-600"
        >
          Mua sắm ngay
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{products.length} sản phẩm</p>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Yêu thích</h1>
        </div>
        <Link
          to="/products"
          className="rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:border-orange-500 hover:text-orange-500 dark:border-gray-800 dark:text-gray-200"
        >
          Thêm sản phẩm
        </Link>
      </div>
      <div className="mt-6">
        <ProductGrid products={products} />
      </div>
    </div>
  );
}

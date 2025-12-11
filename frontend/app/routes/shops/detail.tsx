import { useLoaderData, type LoaderFunctionArgs } from "react-router";
import { vendorsApi } from "~/lib/services";
import type { Vendor, ProductListItem } from "~/lib/types";
import { ProductGrid } from "~/components/product/product-grid";

export function meta({ params }: { params: { slug?: string } }) {
  return [
    { title: `Cửa hàng ${params.slug} - OWLS` },
    { name: "description", content: "Chi tiết cửa hàng" },
  ];
}

export async function loader({ params }: LoaderFunctionArgs) {
  const slug = params.slug as string;
  const vendor = await vendorsApi.getVendor(slug);
  const products = await vendorsApi.getVendorProducts(slug);
  return { vendor, products: products.results || [] };
}

export default function ShopDetailPage() {
  const { vendor, products } = useLoaderData<typeof loader>();

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
        <div className="flex items-center gap-4">
          {vendor.logo ? (
            <img src={vendor.logo} alt={vendor.shop_name} className="h-16 w-16 rounded-full object-cover" />
          ) : (
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-orange-100 text-2xl font-semibold text-orange-600 dark:bg-orange-900/30">
              {vendor.shop_name.charAt(0)}
            </div>
          )}
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{vendor.shop_name}</h1>
            <p className="text-sm text-gray-500">{vendor.total_products} sản phẩm • {vendor.rating.toFixed(1)} ★</p>
            <p className="mt-2 text-gray-700 dark:text-gray-300">{vendor.description}</p>
          </div>
        </div>
      </div>

      <div className="mt-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Sản phẩm</h2>
          <span className="text-sm text-gray-500">{products.length} sản phẩm</span>
        </div>
        <div className="mt-4">
          <ProductGrid products={products as ProductListItem[]} />
        </div>
      </div>
    </div>
  );
}

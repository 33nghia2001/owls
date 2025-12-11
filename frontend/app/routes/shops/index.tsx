import { Link, useLoaderData, type LoaderFunctionArgs } from "react-router";
import { vendorsApi } from "~/lib/services";
import type { Vendor } from "~/lib/types";

export function meta() {
  return [
    { title: "Cửa hàng - OWLS" },
    { name: "description", content: "Khám phá các nhà bán" },
  ];
}

export async function loader({}: LoaderFunctionArgs) {
  const data = await vendorsApi.getVendors();
  return { vendors: data.results || [] };
}

export default function ShopsPage() {
  const { vendors } = useLoaderData<typeof loader>();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-6 text-3xl font-bold text-gray-900 dark:text-gray-100">Cửa hàng nổi bật</h1>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {vendors.map((shop: Vendor) => (
          <Link
            key={shop.id}
            to={`/shops/${shop.slug}`}
            className="rounded-xl border border-gray-200 bg-white p-5 transition hover:border-orange-500 hover:shadow-lg dark:border-gray-800 dark:bg-gray-900"
          >
            <div className="flex items-center gap-3">
              {shop.logo ? (
                <img src={shop.logo} alt={shop.shop_name} className="h-12 w-12 rounded-full object-cover" />
              ) : (
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-orange-100 text-lg font-semibold text-orange-600 dark:bg-orange-900/30">
                  {shop.shop_name.charAt(0)}
                </div>
              )}
              <div>
                <p className="font-semibold text-gray-900 dark:text-gray-100">{shop.shop_name}</p>
                <p className="text-sm text-gray-500">{shop.total_products} sản phẩm • {shop.rating.toFixed(1)} ★</p>
              </div>
            </div>
          </Link>
        ))}
      </div>
      {vendors.length === 0 && (
        <p className="text-gray-600 dark:text-gray-300">Chưa có cửa hàng nào.</p>
      )}
    </div>
  );
}

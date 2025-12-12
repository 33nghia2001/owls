import { useLoaderData, type ClientLoaderFunctionArgs, type MetaFunction } from "react-router";
import { vendorsApi } from "~/lib/services";
import type { Vendor, ProductListItem } from "~/lib/types";
import { ProductGrid } from "~/components/product/product-grid";
import { generateMeta, generateOrganizationSchema } from "~/lib/seo";

export const meta: MetaFunction<typeof clientLoader> = ({ data }) => {
  const vendor = data?.vendor;

  if (!vendor) {
    return [
      { title: "Cửa hàng không tìm thấy - OWLS Marketplace" },
      { name: "description", content: "Cửa hàng bạn tìm kiếm không tồn tại" },
    ];
  }

  return [
    ...generateMeta({
      title: `${vendor.shop_name} - Cửa hàng`,
      description: vendor.description || `Khám phá ${vendor.total_products} sản phẩm từ ${vendor.shop_name} trên OWLS Marketplace`,
      image: vendor.logo || vendor.banner,
      url: `/shops/${vendor.slug}`,
      type: "website",
      keywords: [vendor.shop_name, "cửa hàng", "mua sắm", vendor.city].filter(Boolean) as string[],
    }),
    // JSON-LD for Organization/LocalBusiness
    {
      "script:ld+json": {
        "@context": "https://schema.org",
        "@type": "Store",
        name: vendor.shop_name,
        description: vendor.description,
        image: vendor.logo,
        url: `https://owls.vn/shops/${vendor.slug}`,
        address: {
          "@type": "PostalAddress",
          addressLocality: vendor.city,
          addressRegion: vendor.state,
          addressCountry: vendor.country,
        },
        aggregateRating: {
          "@type": "AggregateRating",
          ratingValue: vendor.rating,
          reviewCount: vendor.total_sales,
        },
      },
    },
  ];
};

export async function clientLoader({ params }: ClientLoaderFunctionArgs) {
  const slug = params.slug as string;
  const vendor = await vendorsApi.getVendor(slug);
  const products = await vendorsApi.getVendorProducts(slug);
  return { vendor, products: products.results || [] };
}

export default function ShopDetailPage() {
  const { vendor, products } = useLoaderData<typeof clientLoader>();

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

import { Form, Link, useLoaderData, useSearchParams, type LoaderFunctionArgs } from "react-router";
import { productsApi } from "~/lib/services";
import type { ProductListItem } from "~/lib/types";
import { ProductGrid } from "~/components/product/product-grid";

export function meta() {
  return [
    { title: "Sản phẩm - OWLS Marketplace" },
    { name: "description", content: "Khám phá hàng ngàn sản phẩm tại OWLS" },
  ];
}

export async function loader({ request }: LoaderFunctionArgs) {
  const url = new URL(request.url);
  const page = Number(url.searchParams.get("page")) || 1;
  const search = url.searchParams.get("q") || "";
  const sort = url.searchParams.get("sort") || "-created_at";
  const category = url.searchParams.get("category") || undefined;
  
  // Build params - use category_slug for backend
  const params: any = { page, ordering: sort };
  if (search) params.search = search;
  if (category) params.category_slug = category;

  const products = await productsApi.getProducts(params);
  const categoriesData = await productsApi.getCategories();

  return { products, categories: categoriesData.results || [], params: { search, category, ordering: sort } };
}

export default function ProductsPage() {
  const { products, categories, params } = useLoaderData<typeof loader>();
  const [searchParams] = useSearchParams();
  const totalPages = products?.count ? Math.ceil(products.count / (products.results?.length || 1)) : 1;
  const currentPage = Number(searchParams.get("page")) || 1;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6 flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <p className="text-sm text-gray-500">{products.count || 0} sản phẩm</p>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Tất cả sản phẩm</h1>
        </div>
        <Form method="get" className="flex flex-col gap-3 md:flex-row md:items-center">
          <input
            type="text"
            name="q"
            defaultValue={params.search}
            placeholder="Tìm sản phẩm..."
            className="h-11 rounded-lg border border-gray-200 px-3 text-sm outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
          />
          <select
            name="category"
            defaultValue={params.category || ""}
            className="h-11 rounded-lg border border-gray-200 px-3 text-sm dark:border-gray-800 dark:bg-gray-900"
          >
            <option value="">Tất cả danh mục</option>
            {categories.map((c: any) => (
              <option key={c.id} value={c.slug}>
                {c.name}
              </option>
            ))}
          </select>
          <select
            name="sort"
            defaultValue={params.ordering}
            className="h-11 rounded-lg border border-gray-200 px-3 text-sm dark:border-gray-800 dark:bg-gray-900"
          >
            <option value="-created_at">Mới nhất</option>
            <option value="price">Giá tăng dần</option>
            <option value="-price">Giá giảm dần</option>
            <option value="-sold_count">Bán chạy</option>
          </select>
          <button
            type="submit"
            className="h-11 rounded-lg bg-orange-500 px-4 text-sm font-medium text-white transition hover:bg-orange-600"
          >
            Lọc
          </button>
        </Form>
      </div>

      <ProductGrid products={products.results || []} />

      <div className="mt-8 flex items-center justify-center gap-2">
        {Array.from({ length: totalPages }).map((_, index) => {
          const page = index + 1;
          const newParams = new URLSearchParams(searchParams);
          newParams.set("page", page.toString());
          return (
            <Link
              key={page}
              to={`?${newParams.toString()}`}
              className={`h-10 w-10 rounded-lg border text-sm font-medium flex items-center justify-center transition ${page === currentPage ? "border-orange-500 bg-orange-50 text-orange-600" : "border-gray-200 text-gray-700 hover:border-orange-500"}`}
            >
              {page}
            </Link>
          );
        })}
      </div>
    </div>
  );
}

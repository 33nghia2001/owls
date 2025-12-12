import { Link, useLoaderData, useSearchParams, type ClientLoaderFunctionArgs } from "react-router";
import { useEffect, useState } from "react";
import { ChevronDown, SlidersHorizontal, X } from "lucide-react";
import { productsApi } from "~/lib/services";
import { ProductGrid } from "~/components/product";
import { Button } from "~/components/ui";
import type { Product, Category, Brand, PaginatedResponse, ProductListItem } from "~/lib/types";

export function meta({ data }: { data?: { category?: Category } }) {
  const category = data?.category;
  return [
    { title: category ? `${category.name} - OWLS Marketplace` : "Danh mục - OWLS" },
    { name: "description", content: category?.description || "Khám phá sản phẩm theo danh mục" },
  ];
}

export async function clientLoader({ params, request }: ClientLoaderFunctionArgs) {
  const url = new URL(request.url);
  const page = parseInt(url.searchParams.get("page") || "1");
  const ordering = url.searchParams.get("ordering") || "-created_at";
  const minPrice = url.searchParams.get("min_price");
  const maxPrice = url.searchParams.get("max_price");

  try {
    const [productsData, categories, brands] = await Promise.all([
      productsApi.getCategoryProducts(params.slug!, {
        page,
        ordering,
        min_price: minPrice,
        max_price: maxPrice,
      }),
      productsApi.getCategories(),
      productsApi.getBrands(),
    ]);

    return {
      category: { name: params.slug, slug: params.slug } as Category,
      products: productsData.results || productsData,
      totalCount: productsData.count || productsData.length,
      categories,
      brands,
      currentPage: page,
    };
  } catch (error) {
    throw new Response("Category not found", { status: 404 });
  }
}

const sortOptions = [
  { value: "-created_at", label: "Mới nhất" },
  { value: "price", label: "Giá thấp đến cao" },
  { value: "-price", label: "Giá cao đến thấp" },
  { value: "-sold_count", label: "Bán chạy nhất" },
  { value: "-rating", label: "Đánh giá cao" },
];

export default function CategoryDetailPage() {
  const { category, products, totalCount, categories, currentPage } =
    useLoaderData<typeof clientLoader>();
  const [searchParams, setSearchParams] = useSearchParams();
  const [showFilters, setShowFilters] = useState(false);

  const currentSort = searchParams.get("ordering") || "-created_at";

  const handleSortChange = (value: string) => {
    const params = new URLSearchParams(searchParams);
    params.set("ordering", value);
    params.delete("page");
    setSearchParams(params);
  };

  const handlePriceFilter = (min?: string, max?: string) => {
    const params = new URLSearchParams(searchParams);
    if (min) params.set("min_price", min);
    else params.delete("min_price");
    if (max) params.set("max_price", max);
    else params.delete("max_price");
    params.delete("page");
    setSearchParams(params);
  };

  const clearFilters = () => {
    setSearchParams({});
  };

  const hasFilters =
    searchParams.has("min_price") || searchParams.has("max_price");

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <nav className="mb-6 text-sm">
        <ol className="flex items-center gap-2">
          <li>
            <Link to="/" className="text-gray-500 hover:text-orange-500">
              Trang chủ
            </Link>
          </li>
          <li className="text-gray-400">/</li>
          <li>
            <Link to="/categories" className="text-gray-500 hover:text-orange-500">
              Danh mục
            </Link>
          </li>
          <li className="text-gray-400">/</li>
          <li className="font-medium text-gray-900 dark:text-gray-100">
            {category.name}
          </li>
        </ol>
      </nav>

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
          {category.name}
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          {totalCount} sản phẩm
        </p>
      </div>

      <div className="flex gap-8">
        {/* Sidebar Filters - Desktop */}
        <aside className="hidden w-64 flex-shrink-0 lg:block">
          <div className="sticky top-24 space-y-6">
            {/* Categories */}
            <div>
              <h3 className="mb-3 font-semibold text-gray-900 dark:text-gray-100">
                Danh mục
              </h3>
              <ul className="space-y-2">
                {categories?.slice(0, 10).map((cat: Category) => (
                  <li key={cat.id}>
                    <Link
                      to={`/categories/${cat.slug}`}
                      className={`block text-sm hover:text-orange-500 ${
                        cat.slug === category.slug
                          ? "font-medium text-orange-500"
                          : "text-gray-600 dark:text-gray-400"
                      }`}
                    >
                      {cat.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Price Filter */}
            <div>
              <h3 className="mb-3 font-semibold text-gray-900 dark:text-gray-100">
                Khoảng giá
              </h3>
              <div className="space-y-2">
                <button
                  onClick={() => handlePriceFilter(undefined, "100000")}
                  className="block w-full rounded-lg border border-gray-200 px-3 py-2 text-left text-sm hover:border-orange-500 dark:border-gray-700"
                >
                  Dưới 100.000₫
                </button>
                <button
                  onClick={() => handlePriceFilter("100000", "500000")}
                  className="block w-full rounded-lg border border-gray-200 px-3 py-2 text-left text-sm hover:border-orange-500 dark:border-gray-700"
                >
                  100.000₫ - 500.000₫
                </button>
                <button
                  onClick={() => handlePriceFilter("500000", "1000000")}
                  className="block w-full rounded-lg border border-gray-200 px-3 py-2 text-left text-sm hover:border-orange-500 dark:border-gray-700"
                >
                  500.000₫ - 1.000.000₫
                </button>
                <button
                  onClick={() => handlePriceFilter("1000000", undefined)}
                  className="block w-full rounded-lg border border-gray-200 px-3 py-2 text-left text-sm hover:border-orange-500 dark:border-gray-700"
                >
                  Trên 1.000.000₫
                </button>
              </div>
            </div>

            {hasFilters && (
              <button
                onClick={clearFilters}
                className="flex items-center gap-2 text-sm text-orange-500 hover:underline"
              >
                <X className="h-4 w-4" />
                Xóa bộ lọc
              </button>
            )}
          </div>
        </aside>

        {/* Main Content */}
        <div className="flex-1">
          {/* Toolbar */}
          <div className="mb-6 flex items-center justify-between">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 rounded-lg border border-gray-200 px-4 py-2 text-sm lg:hidden dark:border-gray-700"
            >
              <SlidersHorizontal className="h-4 w-4" />
              Bộ lọc
            </button>

            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">Sắp xếp:</span>
              <select
                value={currentSort}
                onChange={(e) => handleSortChange(e.target.value)}
                className="rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm focus:border-orange-500 focus:outline-none dark:border-gray-700 dark:bg-gray-900"
              >
                {sortOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Products Grid */}
          <ProductGrid products={products} columns={4} />

          {/* Pagination */}
          {totalCount > 20 && (
            <div className="mt-8 flex justify-center gap-2">
              {currentPage > 1 && (
                <Link
                  to={`?${new URLSearchParams({
                    ...Object.fromEntries(searchParams),
                    page: String(currentPage - 1),
                  })}`}
                >
                  <Button variant="outline">Trang trước</Button>
                </Link>
              )}
              <span className="flex items-center px-4 text-sm text-gray-600">
                Trang {currentPage} / {Math.ceil(totalCount / 20)}
              </span>
              {currentPage < Math.ceil(totalCount / 20) && (
                <Link
                  to={`?${new URLSearchParams({
                    ...Object.fromEntries(searchParams),
                    page: String(currentPage + 1),
                  })}`}
                >
                  <Button variant="outline">Trang sau</Button>
                </Link>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

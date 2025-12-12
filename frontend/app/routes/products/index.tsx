import { useState } from "react";
import { 
  Form, 
  Link, 
  useLoaderData, 
  useNavigation, 
  useSearchParams, 
  useSubmit, 
  type ClientLoaderFunctionArgs 
} from "react-router";
import { 
  Filter, 
  SlidersHorizontal, 
  ChevronDown, 
  LayoutGrid, 
  List
} from "lucide-react";
import { productsApi } from "~/lib/services";
import type { ProductListItem, Category, PaginatedResponse } from "~/lib/types";
import { ProductGrid } from "~/components/product/product-grid";
import { Button, Input } from "~/components/ui";
import { cn } from "~/lib/utils";

// --- META ---
export function meta() {
  return [
    { title: "Tất cả sản phẩm - OWLS Marketplace" },
    { name: "description", content: "Khám phá hàng ngàn sản phẩm chất lượng tại OWLS" },
  ];
}

// --- LOADER ---
export async function clientLoader({ request }: ClientLoaderFunctionArgs) {
  const url = new URL(request.url);
  const page = Number(url.searchParams.get("page")) || 1;
  const search = url.searchParams.get("q") || "";
  const sort = url.searchParams.get("sort") || "-created_at";
  const category_slug = url.searchParams.get("category");
  const min_price = url.searchParams.get("min_price");
  const max_price = url.searchParams.get("max_price");

  // Fetch products with full filters
  const [productsData, categoriesData] = await Promise.all([
    productsApi.getProducts({
      search,
      page,
      ordering: sort,
      category_slug: category_slug || undefined,
      min_price: min_price ? Number(min_price) : undefined,
      max_price: max_price ? Number(max_price) : undefined,
    }),
    productsApi.getCategories(),
  ]);

  return { 
    products: productsData as PaginatedResponse<ProductListItem>,
    categories: (categoriesData.results || categoriesData) as Category[],
    params: { search, category_slug, sort, min_price, max_price } 
  };
}

// --- COMPONENT ---
export default function ProductsPage() {
  const { products, categories, params } = useLoaderData<typeof clientLoader>();
  const [searchParams] = useSearchParams();
  const navigation = useNavigation();
  const submit = useSubmit();
  
  const [showMobileFilter, setShowMobileFilter] = useState(false);
  const isLoading = navigation.state === "loading";

  // Pagination Helper
  const totalPages = products.count ? Math.ceil(products.count / 20) : 1; // Assuming pageSize=20
  const currentPage = Number(searchParams.get("page")) || 1;

  const handleFilterChange = (form: HTMLFormElement) => {
    submit(form);
  };

  const clearFilters = () => {
    submit(null, { method: "get", action: "/products" });
  };

  const hasFilters = params.category_slug || params.min_price || params.max_price;

  return (
    <div className="min-h-screen bg-gray-50/50 dark:bg-[#050505] pb-12 pt-8">
      <div className="container mx-auto px-4">
        
        {/* Page Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 tracking-tight">
              Tất cả sản phẩm
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Hiển thị <span className="font-medium text-orange-600">{products.count}</span> kết quả
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Mobile Filter Toggle */}
            <Button
              variant="outline"
              className="md:hidden gap-2"
              onClick={() => setShowMobileFilter(!showMobileFilter)}
            >
              <Filter className="h-4 w-4" />
              Bộ lọc
            </Button>

            {/* Sort Dropdown */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500 hidden sm:inline">Sắp xếp:</span>
              <Form method="get" onChange={(e) => submit(e.currentTarget)}>
                {/* Preserve existing filters */}
                <input type="hidden" name="q" value={params.search} />
                <input type="hidden" name="category" value={params.category_slug || ""} />
                <input type="hidden" name="min_price" value={params.min_price || ""} />
                <input type="hidden" name="max_price" value={params.max_price || ""} />
                
                <div className="relative">
                  <select
                    name="sort"
                    defaultValue={params.sort}
                    className="h-10 appearance-none rounded-xl border border-gray-200 bg-white pl-4 pr-10 text-sm font-medium outline-none transition hover:border-orange-500 focus:border-orange-500 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-100"
                  >
                    <option value="-created_at">Mới nhất</option>
                    <option value="price">Giá: Thấp đến Cao</option>
                    <option value="-price">Giá: Cao đến Thấp</option>
                    <option value="-sold_count">Bán chạy nhất</option>
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400 pointer-events-none" />
                </div>
              </Form>
            </div>
          </div>
        </div>

        <div className="flex flex-col md:flex-row gap-8">
          
          {/* Sidebar Filter */}
          <aside className={cn(
            "w-full md:w-64 flex-shrink-0 space-y-8",
            showMobileFilter ? "block" : "hidden md:block"
          )}>
            <div className="sticky top-24 space-y-6">
              <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                    <SlidersHorizontal className="h-4 w-4" /> Bộ lọc
                  </h3>
                  {hasFilters && (
                    <button 
                      onClick={clearFilters}
                      className="text-xs text-red-500 hover:underline font-medium"
                    >
                      Đặt lại
                    </button>
                  )}
                </div>

                <Form method="get" className="space-y-6">
                  <input type="hidden" name="q" value={params.search} />
                  <input type="hidden" name="sort" value={params.sort} />

                  {/* Categories */}
                  <div>
                    <h4 className="text-sm font-bold mb-3 text-gray-900 dark:text-gray-100">Danh mục</h4>
                    <div className="space-y-2 max-h-64 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-gray-200 dark:scrollbar-thumb-gray-800">
                      <label className="flex items-center gap-2.5 text-sm cursor-pointer group">
                        <input
                          type="radio"
                          name="category"
                          value=""
                          defaultChecked={!params.category_slug}
                          className="w-4 h-4 text-orange-500 border-gray-300 focus:ring-orange-500"
                          onChange={(e) => submit(e.currentTarget.form)}
                        />
                        <span className="text-gray-600 group-hover:text-orange-600 dark:text-gray-400 transition-colors">
                          Tất cả
                        </span>
                      </label>
                      {categories.map((cat) => (
                        <label key={cat.id} className="flex items-center gap-2.5 text-sm cursor-pointer group">
                          <input
                            type="radio"
                            name="category"
                            value={cat.slug}
                            defaultChecked={params.category_slug === cat.slug}
                            className="w-4 h-4 text-orange-500 border-gray-300 focus:ring-orange-500"
                            onChange={(e) => submit(e.currentTarget.form)}
                          />
                          <span className="text-gray-600 group-hover:text-orange-600 dark:text-gray-400 transition-colors">
                            {cat.name}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="h-px bg-gray-100 dark:bg-gray-800" />

                  {/* Price Range */}
                  <div>
                    <h4 className="text-sm font-bold mb-3 text-gray-900 dark:text-gray-100">Khoảng giá</h4>
                    <div className="grid grid-cols-2 gap-2 mb-3">
                      <div className="relative">
                        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">₫</span>
                        <input
                          type="number"
                          name="min_price"
                          placeholder="Từ"
                          defaultValue={params.min_price ?? ""}
                          className="w-full h-9 pl-6 pr-2 rounded-lg border border-gray-200 bg-gray-50 text-xs focus:bg-white focus:border-orange-500 outline-none transition-all dark:bg-gray-900 dark:border-gray-800"
                        />
                      </div>
                      <div className="relative">
                        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">₫</span>
                        <input
                          type="number"
                          name="max_price"
                          placeholder="Đến"
                          defaultValue={params.max_price ?? ""}
                          className="w-full h-9 pl-6 pr-2 rounded-lg border border-gray-200 bg-gray-50 text-xs focus:bg-white focus:border-orange-500 outline-none transition-all dark:bg-gray-900 dark:border-gray-800"
                        />
                      </div>
                    </div>
                    <Button 
                      type="submit" 
                      className="w-full h-9 text-xs font-medium bg-gray-900 text-white hover:bg-orange-600 dark:bg-gray-800 dark:hover:bg-orange-600"
                    >
                      Áp dụng
                    </Button>
                  </div>
                </Form>
              </div>
            </div>
          </aside>

          {/* Main Content */}
          <div className="flex-1">
            {isLoading ? (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {Array.from({ length: 8 }).map((_, i) => (
                  <div key={i} className="aspect-[2/3] rounded-xl bg-gray-200 animate-pulse dark:bg-gray-800" />
                ))}
              </div>
            ) : products.results.length > 0 ? (
              <>
                <ProductGrid products={products.results} className="grid-cols-2 md:grid-cols-3 lg:grid-cols-4" />
                
                {/* Modern Pagination */}
                {totalPages > 1 && (
                  <div className="mt-12 flex justify-center">
                    <div className="flex items-center gap-1 rounded-full bg-white p-1 shadow-sm border border-gray-100 dark:bg-gray-900 dark:border-gray-800">
                      {/* Previous */}
                      {currentPage > 1 && (
                        <Link
                          to={`?${new URLSearchParams({...Object.fromEntries(searchParams), page: String(currentPage - 1)}).toString()}`}
                          className="h-9 w-9 flex items-center justify-center rounded-full hover:bg-gray-100 text-gray-600 dark:text-gray-400 dark:hover:bg-gray-800"
                        >
                          &larr;
                        </Link>
                      )}

                      {/* Pages */}
                      <div className="flex items-center px-2 gap-1">
                        {Array.from({ length: totalPages }).map((_, index) => {
                          const page = index + 1;
                          // Simple logic to show limited pages could be added here
                          const isActive = page === currentPage;
                          return (
                            <Link
                              key={page}
                              to={`?${new URLSearchParams({...Object.fromEntries(searchParams), page: String(page)}).toString()}`}
                              className={cn(
                                "h-9 w-9 flex items-center justify-center rounded-full text-sm font-medium transition-all",
                                isActive
                                  ? "bg-orange-500 text-white shadow-md shadow-orange-500/20"
                                  : "text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
                              )}
                            >
                              {page}
                            </Link>
                          );
                        })}
                      </div>

                      {/* Next */}
                      {currentPage < totalPages && (
                        <Link
                          to={`?${new URLSearchParams({...Object.fromEntries(searchParams), page: String(currentPage + 1)}).toString()}`}
                          className="h-9 w-9 flex items-center justify-center rounded-full hover:bg-gray-100 text-gray-600 dark:text-gray-400 dark:hover:bg-gray-800"
                        >
                          &rarr;
                        </Link>
                      )}
                    </div>
                  </div>
                )}
              </>
            ) : (
              // Empty State
              <div className="flex flex-col items-center justify-center py-20 text-center rounded-2xl border border-dashed border-gray-200 bg-white/50 dark:border-gray-800">
                <div className="h-20 w-20 bg-gray-50 rounded-full flex items-center justify-center mb-4 dark:bg-gray-800">
                  <Filter className="h-8 w-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">Không tìm thấy sản phẩm</h3>
                <p className="text-gray-500 mt-2 max-w-sm mx-auto">
                  Thử thay đổi bộ lọc hoặc tìm kiếm với từ khóa khác.
                </p>
                <Button 
                  variant="outline" 
                  className="mt-6"
                  onClick={clearFilters}
                >
                  Xóa bộ lọc
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
import { useEffect, useState, useCallback, useRef } from "react";
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
  Search, 
  Filter, 
  SlidersHorizontal, 
  X, 
  ChevronDown, 
  ArrowUpDown,
  Loader2
} from "lucide-react";
import { productsApi } from "~/lib/services";
import type { ProductListItem, Category, PaginatedResponse } from "~/lib/types";
import { ProductGrid } from "~/components/product/product-grid";
import { Button, Input, Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "~/components/ui";
import { cn } from "~/lib/utils";

// --- META ---
export function meta({ data }: { data?: { q?: string } }) {
  const q = data?.q || "";
  return [
    { title: q ? `Tìm kiếm: "${q}" - OWLS` : "Tìm kiếm sản phẩm - OWLS" },
    { name: "description", content: "Tìm kiếm sản phẩm giá tốt tại OWLS Marketplace" },
  ];
}

// --- LOADER ---
export async function clientLoader({ request }: ClientLoaderFunctionArgs) {
  const url = new URL(request.url);
  const q = url.searchParams.get("q") || "";
  const page = parseInt(url.searchParams.get("page") || "1");
  const category_slug = url.searchParams.get("category");
  const min_price = url.searchParams.get("min_price");
  const max_price = url.searchParams.get("max_price");
  const ordering = url.searchParams.get("ordering") || "-created_at";

  // Gọi API lấy sản phẩm với filter
  const [productsData, categoriesData] = await Promise.all([
    productsApi.getProducts({
      search: q,
      page,
      category_slug: category_slug || undefined,
      min_price: min_price ? Number(min_price) : undefined,
      max_price: max_price ? Number(max_price) : undefined,
      ordering,
    }),
    productsApi.getCategories(),
  ]);

  return {
    q,
    products: productsData as PaginatedResponse<ProductListItem>,
    categories: (categoriesData.results || categoriesData) as Category[],
    params: { page, category_slug, min_price, max_price, ordering },
  };
}

// --- COMPONENT ---
export default function SearchPage() {
  const { q, products, categories, params } = useLoaderData<typeof clientLoader>();
  const navigation = useNavigation();
  const submit = useSubmit();
  const [searchParams] = useSearchParams();
  const formRef = useRef<HTMLFormElement>(null);
  
  const [showMobileFilter, setShowMobileFilter] = useState(false);
  const isSearching = navigation.state === "loading" || navigation.state === "submitting";

  // Debounced price filter submission for better UX
  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const handlePriceChange = useCallback(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    debounceTimerRef.current = setTimeout(() => {
      if (formRef.current) {
        submit(formRef.current, { method: "get", preventScrollReset: true });
      }
    }, 500); // 500ms debounce
  }, [submit]);
  
  // Cleanup debounce timer on unmount
  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, []);

  const clearFilters = () => {
    const newParams = new URLSearchParams();
    if (q) newParams.set("q", q);
    submit(newParams, { method: "get", preventScrollReset: true });
  };

  const hasFilters = params.category_slug || params.min_price || params.max_price;

  return (
    <div className="min-h-screen bg-gray-50/50 dark:bg-[#050505] pb-12">
      {/* Header Section removed as requested */}

      <div className="container mx-auto px-4 py-8">
        {/* Results Info Bar */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
              {q ? `Kết quả cho "${q}"` : "Tất cả sản phẩm"}
            </h1>
            <p className="text-sm text-gray-500 mt-1">
              Tìm thấy <span className="font-medium text-orange-600">{products.count}</span> sản phẩm
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
                {/* Keep current params */}
                <input type="hidden" name="q" value={q} />
                {params.category_slug && <input type="hidden" name="category" value={params.category_slug} />}
                {params.min_price && <input type="hidden" name="min_price" value={params.min_price} />}
                {params.max_price && <input type="hidden" name="max_price" value={params.max_price} />}
                
                <select
                  name="ordering"
                  defaultValue={params.ordering}
                  className="h-10 rounded-lg border border-gray-200 bg-white px-3 text-sm outline-none focus:border-orange-500 dark:border-gray-800 dark:bg-gray-900"
                >
                  <option value="-created_at">Mới nhất</option>
                  <option value="price">Giá: Thấp đến Cao</option>
                  <option value="-price">Giá: Cao đến Thấp</option>
                  <option value="-sold_count">Bán chạy</option>
                </select>
              </Form>
            </div>
          </div>
        </div>

        <div className="flex flex-col md:flex-row gap-8">
          {/* Sidebar Filter (Desktop) */}
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
                      className="text-xs text-red-500 hover:underline"
                    >
                      Xóa lọc
                    </button>
                  )}
                </div>

                <Form method="get" className="space-y-6" id="filter-form" ref={formRef}>
                  <input type="hidden" name="q" value={q} />
                  <input type="hidden" name="ordering" value={params.ordering} />

                  {/* Categories */}
                  <div>
                    <h4 className="text-sm font-medium mb-3 text-gray-700 dark:text-gray-300">Danh mục</h4>
                    <div className="space-y-2 max-h-60 overflow-y-auto pr-2 scrollbar-thin">
                      <label className="flex items-center gap-2 text-sm cursor-pointer">
                        <input
                          type="radio"
                          name="category"
                          value=""
                          defaultChecked={!params.category_slug}
                          className="text-orange-500 focus:ring-orange-500"
                          onChange={(e) => submit(e.currentTarget.form, { preventScrollReset: true })}
                        />
                        <span className="text-gray-600 dark:text-gray-400">Tất cả</span>
                      </label>
                      {categories.map((cat) => (
                        <label key={cat.id} className="flex items-center gap-2 text-sm cursor-pointer group">
                          <input
                            type="radio"
                            name="category"
                            value={cat.slug}
                            defaultChecked={params.category_slug === cat.slug}
                            className="text-orange-500 focus:ring-orange-500"
                            onChange={(e) => submit(e.currentTarget.form, { preventScrollReset: true })}
                          />
                          <span className="text-gray-600 group-hover:text-orange-500 dark:text-gray-400 transition-colors">
                            {cat.name}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="h-px bg-gray-100 dark:bg-gray-800" />

                  {/* Price Range */}
                  <div>
                    <h4 className="text-sm font-medium mb-3 text-gray-700 dark:text-gray-300">Khoảng giá</h4>
                    <div className="flex items-center gap-2 mb-3">
                      <Input
                        type="number"
                        name="min_price"
                        placeholder="Từ"
                        defaultValue={params.min_price ?? ""}
                        className="h-9 px-2 text-xs"
                        onChange={handlePriceChange}
                      />
                      <span className="text-gray-400">-</span>
                      <Input
                        type="number"
                        name="max_price"
                        placeholder="Đến"
                        defaultValue={params.max_price ?? ""}
                        className="h-9 px-2 text-xs"
                        onChange={handlePriceChange}
                      />
                    </div>
                    <Button 
                      type="submit" 
                      variant="outline" 
                      size="sm" 
                      className="w-full text-xs font-normal"
                      disabled={isSearching}
                    >
                      {isSearching ? (
                        <>
                          <Loader2 className="h-3 w-3 animate-spin mr-1" />
                          Đang lọc...
                        </>
                      ) : (
                        "Áp dụng"
                      )}
                    </Button>
                  </div>
                </Form>
              </div>
            </div>
          </aside>

          {/* Product Grid */}
          <div className="flex-1">
            {isSearching ? (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {Array.from({ length: 8 }).map((_, i) => (
                  <div key={i} className="aspect-[2/3] rounded-xl bg-gray-200 animate-pulse dark:bg-gray-800" />
                ))}
              </div>
            ) : products.results.length > 0 ? (
              <>
                <ProductGrid products={products.results} className="grid-cols-2 md:grid-cols-3 lg:grid-cols-4" />
                
                {/* Pagination */}
                <div className="mt-10 flex justify-center gap-2">
                   {products.previous && (
                     <Link 
                       to={`?${new URLSearchParams({...Object.fromEntries(searchParams), page: String(params.page - 1)}).toString()}`}
                     >
                       <Button variant="outline">Trang trước</Button>
                     </Link>
                   )}
                   <div className="flex items-center px-4 font-medium text-sm">
                     Trang {params.page}
                   </div>
                   {products.next && (
                     <Link 
                       to={`?${new URLSearchParams({...Object.fromEntries(searchParams), page: String(params.page + 1)}).toString()}`}
                     >
                       <Button variant="outline">Trang sau</Button>
                     </Link>
                   )}
                </div>
              </>
            ) : (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <div className="h-24 w-24 bg-gray-100 rounded-full flex items-center justify-center mb-4 dark:bg-gray-800">
                  <Search className="h-10 w-10 text-gray-400" />
                </div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">Không tìm thấy sản phẩm</h3>
                <p className="text-gray-500 mt-2 max-w-md">
                  Rất tiếc, chúng tôi không tìm thấy sản phẩm nào phù hợp với từ khóa "{q}". Hãy thử tìm với từ khóa khác hoặc xóa bộ lọc.
                </p>
                <Button 
                  variant="primary" 
                  className="mt-6"
                  onClick={clearFilters}
                >
                  Xem tất cả sản phẩm
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
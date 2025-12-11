import { Form, useLoaderData, type LoaderFunctionArgs } from "react-router";
import { productsApi } from "~/lib/services";
import type { ProductListItem } from "~/lib/types";
import { ProductGrid } from "~/components/product/product-grid";

export function meta({ data }: { data?: { q?: string } }) {
  const q = data?.q || "";
  return [
    { title: q ? `Tìm kiếm: ${q} - OWLS` : "Tìm kiếm sản phẩm" },
    { name: "description", content: "Tìm kiếm sản phẩm tại OWLS" },
  ];
}

export async function loader({ request }: LoaderFunctionArgs) {
  const url = new URL(request.url);
  const q = url.searchParams.get("q") || "";
  const results = q ? await productsApi.searchProducts(q) : { results: [] };
  return { q, results };
}

export default function SearchPage() {
  const { q, results } = useLoaderData<typeof loader>();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Tìm kiếm</h1>
      <Form method="get" className="mt-4 flex gap-2">
        <input
          type="text"
          name="q"
          defaultValue={q}
          placeholder="Nhập từ khóa..."
          className="h-11 flex-1 rounded-lg border border-gray-200 px-3 text-sm outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
        />
        <button
          type="submit"
          className="h-11 rounded-lg bg-orange-500 px-4 text-sm font-medium text-white transition hover:bg-orange-600"
        >
          Tìm kiếm
        </button>
      </Form>

      <div className="mt-6">
        <ProductGrid products={(results.results as ProductListItem[]) || []} />
      </div>
    </div>
  );
}

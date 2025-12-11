import { Link, useLoaderData, type LoaderFunctionArgs } from "react-router";
import { ChevronRight } from "lucide-react";
import { productsApi } from "~/lib/services";
import type { Category } from "~/lib/types";

export function meta() {
  return [
    { title: "Danh mục sản phẩm - OWLS Marketplace" },
    { name: "description", content: "Khám phá tất cả danh mục sản phẩm tại OWLS" },
  ];
}

export async function loader({}: LoaderFunctionArgs) {
  const categories = await productsApi.getCategories();
  return { categories };
}

export default function CategoriesPage() {
  const { categories } = useLoaderData<typeof loader>();

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
          <li className="font-medium text-gray-900 dark:text-gray-100">
            Danh mục
          </li>
        </ol>
      </nav>

      <h1 className="mb-8 text-3xl font-bold text-gray-900 dark:text-gray-100">
        Danh mục sản phẩm
      </h1>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
        {categories.map((category: Category) => (
          <Link
            key={category.id}
            to={`/categories/${category.slug}`}
            className="group overflow-hidden rounded-xl border border-gray-200 bg-white p-6 transition-all hover:border-orange-500 hover:shadow-lg dark:border-gray-800 dark:bg-gray-950"
          >
            {category.image ? (
              <img
                src={category.image}
                alt={category.name}
                className="mx-auto mb-4 h-20 w-20 object-contain"
              />
            ) : (
              <div className="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-orange-100 text-4xl dark:bg-orange-900/20">
                {category.icon || "📦"}
              </div>
            )}
            <h3 className="text-center font-medium text-gray-900 group-hover:text-orange-500 dark:text-gray-100">
              {category.name}
            </h3>
            {category.product_count !== undefined && (
              <p className="mt-1 text-center text-sm text-gray-500">
                {category.product_count} sản phẩm
              </p>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}

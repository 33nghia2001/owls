import type { ProductListItem } from "~/lib/types";
import { ProductCard } from "./product-card";
import { cn } from "~/lib/utils";

interface ProductGridProps {
  products: ProductListItem[];
  className?: string;
  columns?: 2 | 3 | 4 | 5 | 6;
}

export function ProductGrid({
  products,
  className,
  columns = 4,
}: ProductGridProps) {
  const gridCols = {
    2: "grid-cols-2",
    3: "grid-cols-2 md:grid-cols-3",
    4: "grid-cols-2 md:grid-cols-3 lg:grid-cols-4",
    5: "grid-cols-2 md:grid-cols-3 lg:grid-cols-5",
    6: "grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6",
  };

  if (products.length === 0) {
    return (
      <div className="py-12 text-center">
        <p className="text-gray-500">Không tìm thấy sản phẩm nào</p>
      </div>
    );
  }

  return (
    <div className={cn("grid gap-4", gridCols[columns], className)}>
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}

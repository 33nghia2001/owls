import { Link } from "react-router";
import { Plus } from "lucide-react";

export function meta() {
  return [
    { title: "Sản phẩm - Seller Dashboard" },
    { name: "description", content: "Quản lý sản phẩm" },
  ];
}

export default function SellerProductsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Sản phẩm của tôi</h1>
        <Link
          to="/seller/products/new"
          className="flex items-center gap-2 rounded-lg bg-orange-500 px-4 py-2 font-medium text-white transition hover:bg-orange-600"
        >
          <Plus className="h-5 w-5" />
          Thêm sản phẩm
        </Link>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900">
        <div className="p-6 text-center text-gray-600 dark:text-gray-300">
          Chưa có sản phẩm nào. Thêm sản phẩm đầu tiên của bạn.
        </div>
      </div>
    </div>
  );
}

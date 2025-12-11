export function meta() {
  return [
    { title: "Đơn hàng - Seller Dashboard" },
    { name: "description", content: "Quản lý đơn hàng" },
  ];
}

export default function SellerOrdersPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-6 text-3xl font-bold text-gray-900 dark:text-gray-100">Đơn hàng</h1>

      <div className="rounded-xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900">
        <div className="border-b border-gray-200 dark:border-gray-800">
          <div className="flex gap-4 px-6 py-3">
            <button className="border-b-2 border-orange-500 pb-2 text-sm font-medium text-orange-500">
              Tất cả
            </button>
            <button className="pb-2 text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100">
              Chờ xác nhận
            </button>
            <button className="pb-2 text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100">
              Đang xử lý
            </button>
            <button className="pb-2 text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100">
              Đã giao
            </button>
          </div>
        </div>

        <div className="p-6 text-center text-gray-600 dark:text-gray-300">
          Chưa có đơn hàng nào.
        </div>
      </div>
    </div>
  );
}

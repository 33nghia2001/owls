import { Form } from "react-router";

export function meta() {
  return [
    { title: "Cài đặt - Seller Dashboard" },
    { name: "description", content: "Cài đặt cửa hàng" },
  ];
}

export default function SellerSettingsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-6 text-3xl font-bold text-gray-900 dark:text-gray-100">Cài đặt</h1>

      <div className="space-y-6">
        <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">Thông tin cửa hàng</h2>
          
          <Form className="space-y-4">
            <label className="block text-sm text-gray-700 dark:text-gray-300">
              Tên cửa hàng
              <input
                name="shop_name"
                className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>

            <label className="block text-sm text-gray-700 dark:text-gray-300">
              Mô tả
              <textarea
                name="description"
                rows={4}
                className="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>

            <label className="block text-sm text-gray-700 dark:text-gray-300">
              Email liên hệ
              <input
                name="business_email"
                type="email"
                className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>

            <label className="block text-sm text-gray-700 dark:text-gray-300">
              Địa chỉ
              <input
                name="address"
                className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>

            <div className="grid gap-4 md:grid-cols-2">
              <label className="block text-sm text-gray-700 dark:text-gray-300">
                Tỉnh/Thành phố
                <input
                  name="city"
                  className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
                />
              </label>

              <label className="block text-sm text-gray-700 dark:text-gray-300">
                Quốc gia
                <input
                  name="country"
                  className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
                />
              </label>
            </div>

            <button
              type="submit"
              className="rounded-lg bg-orange-500 px-6 py-3 font-medium text-white transition hover:bg-orange-600"
            >
              Lưu thay đổi
            </button>
          </Form>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">Thông tin thanh toán</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Thông tin tài khoản ngân hàng để nhận thanh toán từ đơn hàng.
          </p>
          
          <Form className="mt-4 space-y-4">
            <label className="block text-sm text-gray-700 dark:text-gray-300">
              Ngân hàng
              <input
                name="bank_name"
                className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>

            <label className="block text-sm text-gray-700 dark:text-gray-300">
              Số tài khoản
              <input
                name="account_number"
                className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>

            <label className="block text-sm text-gray-700 dark:text-gray-300">
              Tên chủ tài khoản
              <input
                name="account_holder"
                className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>

            <button
              type="submit"
              className="rounded-lg bg-orange-500 px-6 py-3 font-medium text-white transition hover:bg-orange-600"
            >
              Cập nhật
            </button>
          </Form>
        </div>
      </div>
    </div>
  );
}

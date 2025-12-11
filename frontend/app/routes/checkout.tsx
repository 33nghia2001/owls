import { Form, useNavigate } from "react-router";
import { useEffect } from "react";
import { useCartStore } from "~/lib/stores";
import { formatCurrency } from "~/lib/utils";

export function meta() {
  return [
    { title: "Thanh toán - OWLS" },
    { name: "description", content: "Hoàn tất đơn hàng" },
  ];
}

export default function CheckoutPage() {
  const navigate = useNavigate();
  const { cart, fetchCart } = useCartStore();

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  if (!cart || cart.items.length === 0) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <p className="text-gray-600">Giỏ hàng trống, vui lòng thêm sản phẩm.</p>
        <button
          onClick={() => navigate("/products")}
          className="mt-4 rounded-lg bg-orange-500 px-4 py-2 text-white"
        >
          Mua sắm ngay
        </button>
      </div>
    );
  }

  const subtotal = parseFloat(cart.subtotal.amount);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-6 text-3xl font-bold text-gray-900 dark:text-gray-100">Thanh toán</h1>
      <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
        <Form className="space-y-4 rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Thông tin giao hàng</h2>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="text-sm text-gray-600">
              Họ tên
              <input
                name="full_name"
                required
                className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>
            <label className="text-sm text-gray-600">
              Số điện thoại
              <input
                name="phone"
                required
                className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>
            <label className="text-sm text-gray-600 md:col-span-2">
              Địa chỉ
              <input
                name="address"
                required
                className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>
            <label className="text-sm text-gray-600">
              Tỉnh/Thành phố
              <input
                name="city"
                required
                className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>
            <label className="text-sm text-gray-600">
              Quận/Huyện
              <input
                name="district"
                required
                className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>
          </div>

          <div className="pt-2">
            <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">Phương thức thanh toán</p>
            <div className="mt-2 space-y-2">
              <label className="flex items-center gap-3 rounded-lg border border-gray-200 p-3 dark:border-gray-800">
                <input type="radio" name="payment" defaultChecked />
                <span>Thanh toán khi nhận hàng (COD)</span>
              </label>
              <label className="flex items-center gap-3 rounded-lg border border-gray-200 p-3 dark:border-gray-800">
                <input type="radio" name="payment" />
                <span>Chuyển khoản / VNPAY</span>
              </label>
            </div>
          </div>

          <button
            type="button"
            onClick={() => navigate("/checkout/success")}
            className="w-full rounded-lg bg-orange-500 py-3 font-medium text-white transition hover:bg-orange-600"
          >
            Đặt hàng
          </button>
        </Form>

        <div className="h-fit rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Đơn hàng</h2>
          <div className="mt-4 space-y-3">
            {cart.items.map((item) => (
              <div key={item.id} className="flex justify-between text-sm text-gray-700 dark:text-gray-300">
                <div>
                  <p className="font-medium text-gray-900 dark:text-gray-100">{item.product.name}</p>
                  <p className="text-xs text-gray-500">x{item.quantity}</p>
                </div>
                <p>{formatCurrency(parseFloat(item.total_price.amount))}</p>
              </div>
            ))}
          </div>
          <div className="mt-4 border-t border-gray-200 pt-4 text-sm text-gray-700 dark:border-gray-800 dark:text-gray-300">
            <div className="flex justify-between">
              <span>Tạm tính</span>
              <span>{formatCurrency(subtotal)}</span>
            </div>
            <div className="flex justify-between">
              <span>Phí vận chuyển</span>
              <span>Đang tính</span>
            </div>
          </div>
          <div className="mt-3 flex items-center justify-between text-lg font-semibold text-gray-900 dark:text-gray-100">
            <span>Tổng cộng</span>
            <span>{formatCurrency(subtotal)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

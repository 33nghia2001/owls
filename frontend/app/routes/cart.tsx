import { Link, useNavigate } from "react-router";
import { useEffect } from "react";
import { Trash2 } from "lucide-react";
import { useCartStore } from "~/lib/stores";
import { formatCurrency } from "~/lib/utils";

export function meta() {
  return [
    { title: "Giỏ hàng - OWLS" },
    { name: "description", content: "Giỏ hàng của bạn" },
  ];
}

export default function CartPage() {
  const navigate = useNavigate();
  const { cart, fetchCart, updateQuantity, removeItem } = useCartStore();

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  const hasItems = cart && cart.items.length > 0;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-6 text-3xl font-bold text-gray-900 dark:text-gray-100">Giỏ hàng</h1>

      {!hasItems && (
        <div className="rounded-xl border border-gray-200 bg-white p-6 text-center dark:border-gray-800 dark:bg-gray-900">
          <p className="text-gray-600">Giỏ hàng của bạn đang trống.</p>
          <Link
            to="/products"
            className="mt-4 inline-flex rounded-lg bg-orange-500 px-4 py-2 text-white transition hover:bg-orange-600"
          >
            Mua sắm ngay
          </Link>
        </div>
      )}

      {hasItems && (
        <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
          <div className="space-y-4">
            {cart.items.map((item) => (
              <div
                key={item.id}
                className="flex gap-4 rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900"
              >
                <img
                  src={item.product.primary_image?.image || "/placeholder.jpg"}
                  alt={item.product.name}
                  className="h-20 w-20 rounded-lg object-cover"
                />
                <div className="flex-1">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <Link
                        to={`/products/${item.product.slug}`}
                        className="font-medium text-gray-900 hover:text-orange-500 dark:text-gray-100"
                      >
                        {item.product.name}
                      </Link>
                      {item.variant && (
                        <p className="text-sm text-gray-500">{item.variant.name}</p>
                      )}
                    </div>
                    <button
                      onClick={() => removeItem(item.id)}
                      className="text-gray-400 transition hover:text-red-500"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </div>

                  <div className="mt-3 flex items-center justify-between">
                    <div className="flex items-center rounded-lg border border-gray-200 dark:border-gray-800">
                      <button
                        type="button"
                        className="px-3 py-2 text-lg"
                        onClick={() => updateQuantity(item.id, Math.max(1, item.quantity - 1))}
                      >
                        -
                      </button>
                      <span className="w-12 text-center text-sm font-medium">{item.quantity}</span>
                      <button
                        type="button"
                        className="px-3 py-2 text-lg"
                        onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      >
                        +
                      </button>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {formatCurrency(parseFloat(item.total_price.amount))}
                      </p>
                      <p className="text-sm text-gray-500">{formatCurrency(parseFloat(item.unit_price.amount))} / sản phẩm</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="h-fit rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Tổng cộng</h2>
            <div className="mt-4 space-y-2 text-sm text-gray-600 dark:text-gray-300">
              <div className="flex justify-between">
                <span>Tạm tính</span>
                <span>{formatCurrency(parseFloat(cart.subtotal.amount))}</span>
              </div>
            </div>
            <div className="mt-4 flex items-center justify-between text-lg font-semibold text-gray-900 dark:text-gray-100">
              <span>Thành tiền</span>
              <span>{formatCurrency(parseFloat(cart.subtotal.amount))}</span>
            </div>
            <button
              onClick={() => navigate("/checkout")}
              className="mt-6 w-full rounded-lg bg-orange-500 py-3 font-medium text-white transition hover:bg-orange-600"
            >
              Tiến hành thanh toán
            </button>
            <p className="mt-2 text-center text-xs text-gray-500">Phí vận chuyển và mã giảm giá tính ở bước tiếp theo.</p>
          </div>
        </div>
      )}
    </div>
  );
}

import { Link, useNavigate } from "react-router";
import { Trash2, Loader2 } from "lucide-react";
import { useCart, useUpdateCartItem, useRemoveCartItem } from "~/lib/query";
import { formatPrice } from "~/lib/utils";
import type { CartItem } from "~/lib/types";

export function meta() {
  return [
    { title: "Giỏ hàng - OWLS" },
    { name: "description", content: "Giỏ hàng của bạn" },
  ];
}

export default function CartPage() {
  const navigate = useNavigate();
  const { data: cart, isLoading, isError } = useCart();
  const updateCartItem = useUpdateCartItem();
  const removeCartItem = useRemoveCartItem();

  const isPending = updateCartItem.isPending || removeCartItem.isPending;
  const hasItems = cart && cart.items.length > 0;

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="mb-6 text-3xl font-bold text-gray-900 dark:text-gray-100">Giỏ hàng</h1>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-orange-500" />
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="mb-6 text-3xl font-bold text-gray-900 dark:text-gray-100">Giỏ hàng</h1>
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center dark:border-red-800 dark:bg-red-900/20">
          <p className="text-red-600 dark:text-red-400">Không thể tải giỏ hàng. Vui lòng thử lại.</p>
        </div>
      </div>
    );
  }

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
            {cart.items.map((item: CartItem) => (
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
                      onClick={() => removeCartItem.mutate(item.id)}
                      disabled={isPending}
                      className="text-gray-400 transition hover:text-red-500 disabled:opacity-50"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </div>

                  <div className="mt-3 flex items-center justify-between">
                    <div className="flex items-center rounded-lg border border-gray-200 dark:border-gray-800">
                      <button
                        type="button"
                        disabled={isPending}
                        className="px-3 py-2 text-lg disabled:opacity-50"
                        onClick={() => 
                          updateCartItem.mutate({
                            itemId: item.id,
                            quantity: Math.max(1, item.quantity - 1),
                          })
                        }
                      >
                        -
                      </button>
                      <span className="w-12 text-center text-sm font-medium">{item.quantity}</span>
                      <button
                        type="button"
                        disabled={isPending}
                        className="px-3 py-2 text-lg disabled:opacity-50"
                        onClick={() =>
                          updateCartItem.mutate({
                            itemId: item.id,
                            quantity: item.quantity + 1,
                          })
                        }
                      >
                        +
                      </button>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {formatPrice(item.total_price)}
                      </p>
                      <p className="text-sm text-gray-500">{formatPrice(item.unit_price)} / sản phẩm</p>
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
                <span>{formatPrice(cart.subtotal)}</span>
              </div>
            </div>
            <div className="mt-4 flex items-center justify-between text-lg font-semibold text-gray-900 dark:text-gray-100">
              <span>Thành tiền</span>
              <span>{formatPrice(cart.subtotal)}</span>
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

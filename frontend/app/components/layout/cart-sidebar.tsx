import { Link } from "react-router";
import { X, Minus, Plus, ShoppingBag } from "lucide-react";
import { Button } from "~/components/ui";
import { useUIStore } from "~/lib/stores";
import { useCart, useUpdateCartItem, useRemoveCartItem } from "~/lib/query";
import { formatPrice, getImageUrl } from "~/lib/utils";
import type { CartItem } from "~/lib/types";

export function CartSidebar() {
  const { data: cart, isLoading } = useCart();
  const updateCartItem = useUpdateCartItem();
  const removeCartItem = useRemoveCartItem();
  const { isCartSidebarOpen, toggleCartSidebar } = useUIStore();

  if (!isCartSidebarOpen) return null;

  const handleQuantityChange = (itemId: string, newQuantity: number) => {
    if (newQuantity < 1) {
      removeCartItem.mutate(itemId);
    } else {
      updateCartItem.mutate({ itemId, quantity: newQuantity });
    }
  };

  const isPending = updateCartItem.isPending || removeCartItem.isPending;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-50 bg-black/50"
        onClick={toggleCartSidebar}
      />

      {/* Sidebar */}
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white shadow-xl dark:bg-gray-950">
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-gray-200 px-4 py-4 dark:border-gray-800">
            <h2 className="text-lg font-semibold">
              Giỏ hàng ({cart?.item_count || 0})
            </h2>
            <button
              onClick={toggleCartSidebar}
              className="rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Cart items */}
          <div className="flex-1 overflow-y-auto p-4">
            {isLoading ? (
              <div className="flex h-full items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-2 border-orange-500 border-t-transparent" />
              </div>
            ) : !cart || cart.items.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center text-center">
                <ShoppingBag className="mb-4 h-16 w-16 text-gray-300" />
                <p className="mb-2 text-lg font-medium">Giỏ hàng trống</p>
                <p className="mb-4 text-sm text-gray-500">
                  Hãy thêm sản phẩm vào giỏ hàng
                </p>
                <Button onClick={toggleCartSidebar}>
                  Tiếp tục mua sắm
                </Button>
              </div>
            ) : (
              <ul className="space-y-4">
                {cart.items.map((item: CartItem) => (
                  <li
                    key={item.id}
                    className="flex gap-4 rounded-lg border border-gray-200 p-3 dark:border-gray-800"
                  >
                    <Link
                      to={`/products/${item.product.slug}`}
                      onClick={toggleCartSidebar}
                      className="h-20 w-20 flex-shrink-0 overflow-hidden rounded-lg bg-gray-100"
                    >
                      <img
                        src={getImageUrl(item.product.primary_image?.image)}
                        alt={item.product.name}
                        className="h-full w-full object-cover"
                      />
                    </Link>

                    <div className="flex flex-1 flex-col">
                      <Link
                        to={`/products/${item.product.slug}`}
                        onClick={toggleCartSidebar}
                        className="line-clamp-2 text-sm font-medium hover:text-orange-500"
                      >
                        {item.product.name}
                      </Link>

                      {item.variant && (
                        <p className="text-xs text-gray-500">
                          {item.variant.name}
                        </p>
                      )}

                      <div className="mt-auto flex items-center justify-between">
                        <div className="flex items-center rounded-lg border border-gray-200 dark:border-gray-700">
                          <button
                            onClick={() =>
                              handleQuantityChange(item.id, item.quantity - 1)
                            }
                            disabled={isPending}
                            className="flex h-8 w-8 items-center justify-center hover:bg-gray-100 disabled:opacity-50 dark:hover:bg-gray-800"
                          >
                            <Minus className="h-4 w-4" />
                          </button>
                          <span className="w-10 text-center text-sm">
                            {item.quantity}
                          </span>
                          <button
                            onClick={() =>
                              handleQuantityChange(item.id, item.quantity + 1)
                            }
                            disabled={isPending}
                            className="flex h-8 w-8 items-center justify-center hover:bg-gray-100 disabled:opacity-50 dark:hover:bg-gray-800"
                          >
                            <Plus className="h-4 w-4" />
                          </button>
                        </div>

                        <div className="text-right">
                          <p className="font-semibold text-orange-500">
                            {formatPrice(item.total_price)}
                          </p>
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={() => removeCartItem.mutate(item.id)}
                      className="self-start p-1 text-gray-400 hover:text-red-500"
                      disabled={isPending}
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Footer */}
          {cart && cart.items.length > 0 && (
            <div className="border-t border-gray-200 p-4 dark:border-gray-800">
              <div className="mb-4 flex items-center justify-between">
                <span className="text-gray-600 dark:text-gray-400">
                  Tạm tính:
                </span>
                <span className="text-lg font-semibold">
                  {formatPrice(cart.subtotal)}
                </span>
              </div>
              <div className="grid gap-2">
                <Link to="/cart" onClick={toggleCartSidebar}>
                  <Button variant="outline" className="w-full">
                    Xem giỏ hàng
                  </Button>
                </Link>
                <Link to="/checkout" onClick={toggleCartSidebar}>
                  <Button className="w-full">Thanh toán</Button>
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

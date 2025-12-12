import { Link } from "react-router";
import { X, Minus, Plus, ShoppingBag, Loader2 } from "lucide-react";
import { Button } from "~/components/ui";
import { useUIStore } from "~/lib/stores";
import { useCart, useUpdateCartItem, useRemoveCartItem } from "~/lib/query";
import { formatPrice, getImageUrl } from "~/lib/utils";
import type { CartItem } from "~/lib/types";

export function CartSidebar() {
  // 1. Sử dụng Hook React Query thay vì Store cũ
  const { data: cart, isLoading } = useCart();
  const updateCartItem = useUpdateCartItem();
  const removeCartItem = useRemoveCartItem();
  
  // 2. UI Store chỉ quản lý trạng thái đóng/mở
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
        className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm transition-opacity"
        onClick={toggleCartSidebar}
      />

      {/* Sidebar */}
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white shadow-2xl transition-transform dark:bg-gray-950">
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4 dark:border-gray-800">
            <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
              Giỏ hàng ({cart?.item_count || 0})
            </h2>
            <button
              onClick={toggleCartSidebar}
              className="rounded-full p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Cart items */}
          <div className="flex-1 overflow-y-auto p-6">
            {isLoading ? (
              <div className="flex h-full items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-orange-500" />
              </div>
            ) : !cart || cart.items.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center text-center">
                <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gray-50 dark:bg-gray-900">
                  <ShoppingBag className="h-8 w-8 text-gray-400" />
                </div>
                <p className="mb-2 text-lg font-semibold text-gray-900 dark:text-gray-100">
                  Giỏ hàng trống
                </p>
                <p className="mb-6 text-sm text-gray-500">
                  Hãy thêm sản phẩm vào giỏ hàng để tiếp tục mua sắm
                </p>
                <Button onClick={toggleCartSidebar} className="bg-orange-500 hover:bg-orange-600">
                  Tiếp tục mua sắm
                </Button>
              </div>
            ) : (
              <ul className="space-y-6">
                {cart.items.map((item: CartItem) => (
                  <li key={item.id} className="flex gap-4">
                    <Link
                      to={`/products/${item.product.slug}`}
                      onClick={toggleCartSidebar}
                      className="h-24 w-24 flex-shrink-0 overflow-hidden rounded-xl border border-gray-100 bg-gray-50 dark:border-gray-800 dark:bg-gray-900"
                    >
                      <img
                        src={getImageUrl(item.product.primary_image?.image)}
                        alt={item.product.name}
                        className="h-full w-full object-cover"
                      />
                    </Link>

                    <div className="flex flex-1 flex-col justify-between">
                      <div>
                        <Link
                          to={`/products/${item.product.slug}`}
                          onClick={toggleCartSidebar}
                          className="line-clamp-2 text-sm font-medium text-gray-900 hover:text-orange-500 dark:text-gray-100"
                        >
                          {item.product.name}
                        </Link>
                        {item.variant && (
                          <p className="mt-1 text-xs text-gray-500">
                            Phân loại: {item.variant.name}
                          </p>
                        )}
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center rounded-lg border border-gray-200 dark:border-gray-800">
                          <button
                            onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                            disabled={isPending}
                            className="p-1.5 hover:text-orange-500 disabled:opacity-50"
                          >
                            <Minus className="h-3.5 w-3.5" />
                          </button>
                          <span className="w-8 text-center text-xs font-medium">
                            {item.quantity}
                          </span>
                          <button
                            onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                            disabled={isPending}
                            className="p-1.5 hover:text-orange-500 disabled:opacity-50"
                          >
                            <Plus className="h-3.5 w-3.5" />
                          </button>
                        </div>
                        
                        <div className="text-right">
                          <p className="text-sm font-bold text-orange-600">
                            {formatPrice(item.total_price)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Footer */}
          {cart && cart.items.length > 0 && (
            <div className="border-t border-gray-100 bg-gray-50 p-6 dark:border-gray-800 dark:bg-gray-900/50">
              <div className="mb-4 flex items-center justify-between">
                <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Tạm tính:
                </span>
                <span className="text-lg font-bold text-gray-900 dark:text-gray-100">
                  {formatPrice(cart.subtotal)}
                </span>
              </div>
              <div className="grid gap-3">
                <Link to="/cart" onClick={toggleCartSidebar}>
                  <Button variant="outline" className="w-full justify-center border-gray-200 bg-white hover:bg-gray-50 dark:border-gray-800 dark:bg-gray-900 dark:hover:bg-gray-800">
                    Xem giỏ hàng
                  </Button>
                </Link>
                <Link to="/checkout" onClick={toggleCartSidebar}>
                  <Button className="w-full justify-center bg-orange-500 text-white hover:bg-orange-600 shadow-lg shadow-orange-500/20">
                    Thanh toán
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
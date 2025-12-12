import { Link, useNavigate } from "react-router";
import { Minus, Plus, Trash2, ArrowRight, ShoppingBag, Loader2 } from "lucide-react";
import { Button } from "~/components/ui";
import { useCart, useUpdateCartItem, useRemoveCartItem } from "~/lib/query";
import { formatCurrency, parsePrice, getImageUrl } from "~/lib/utils";
import toast from "react-hot-toast";

export function meta() {
  return [{ title: "Giỏ hàng - OWLS Marketplace" }];
}

export default function CartPage() {
  const navigate = useNavigate();
  // Sử dụng Hook thay vì Store
  const { data: cart, isLoading } = useCart();
  const updateItemMutation = useUpdateCartItem();
  const removeItemMutation = useRemoveCartItem();

  const handleUpdateQuantity = (itemId: string, newQuantity: number) => {
    if (newQuantity < 1) return;
    updateItemMutation.mutate({ itemId, quantity: newQuantity });
  };

  const handleRemoveItem = (itemId: string) => {
    removeItemMutation.mutate(itemId, {
      onSuccess: () => toast.success("Đã xóa sản phẩm khỏi giỏ"),
    });
  };

  if (isLoading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-orange-500" />
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 px-4 text-center">
        <div className="flex h-20 w-20 items-center justify-center rounded-full bg-orange-50 dark:bg-orange-900/10">
          <ShoppingBag className="h-10 w-10 text-orange-500" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Giỏ hàng của bạn đang trống</h2>
        <p className="max-w-md text-gray-500 dark:text-gray-400">
          Có vẻ như bạn chưa thêm sản phẩm nào vào giỏ hàng. Hãy khám phá thêm các sản phẩm tuyệt vời của chúng tôi nhé!
        </p>
        <Link to="/products">
          <Button size="lg" className="mt-4 bg-orange-500 hover:bg-orange-600">
            Tiếp tục mua sắm
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-8 text-3xl font-bold text-gray-900 dark:text-gray-100">Giỏ hàng ({cart.item_count})</h1>

      <div className="grid gap-8 lg:grid-cols-3">
        {/* Cart Items List */}
        <div className="lg:col-span-2 space-y-4">
          {cart.items.map((item: (typeof cart.items)[number]) => (
            <div
              key={item.id}
              className="flex gap-4 rounded-xl border border-gray-200 bg-white p-4 transition-all hover:shadow-sm dark:border-gray-800 dark:bg-gray-900"
            >
              <div className="h-24 w-24 shrink-0 overflow-hidden rounded-lg border border-gray-100 bg-gray-50 dark:border-gray-800 dark:bg-gray-800">
                <img
                  src={getImageUrl(item.product.primary_image?.image)}
                  alt={item.product.name}
                  className="h-full w-full object-cover"
                />
              </div>

              <div className="flex flex-1 flex-col justify-between">
                <div className="flex justify-between gap-2">
                  <div>
                    <Link
                      to={`/products/${item.product.slug}`}
                      className="font-medium text-gray-900 hover:text-orange-500 dark:text-gray-100"
                    >
                      {item.product.name}
                    </Link>
                    {item.variant && (
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Phân loại: {item.variant.name}
                      </p>
                    )}
                    <p className="mt-1 font-semibold text-orange-600">
                      {formatCurrency(parsePrice(item.price))}
                    </p>
                  </div>
                  <button
                    onClick={() => handleRemoveItem(item.id)}
                    className="h-8 w-8 rounded-lg p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-900/20"
                  >
                    <Trash2 className="h-full w-full" />
                  </button>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center rounded-lg border border-gray-200 dark:border-gray-800">
                    <button
                      onClick={() => handleUpdateQuantity(item.id, item.quantity - 1)}
                      disabled={item.quantity <= 1 || updateItemMutation.isPending}
                      className="p-1.5 hover:text-orange-500 disabled:opacity-50"
                    >
                      <Minus className="h-4 w-4" />
                    </button>
                    <span className="w-8 text-center text-sm font-medium">{item.quantity}</span>
                    <button
                      onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                      disabled={updateItemMutation.isPending}
                      className="p-1.5 hover:text-orange-500 disabled:opacity-50"
                    >
                      <Plus className="h-4 w-4" />
                    </button>
                  </div>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    Tổng: {formatCurrency(parsePrice(item.total_price))}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Order Summary */}
        <div className="h-fit space-y-6 rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">Tóm tắt đơn hàng</h3>
          
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Tạm tính</span>
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {formatCurrency(parsePrice(cart.subtotal))}
              </span>
            </div>
            {/* Nếu có discount thì hiển thị thêm ở đây */}
          </div>

          <div className="border-t border-gray-100 py-4 dark:border-gray-800">
            <div className="flex justify-between items-end">
              <span className="text-base font-bold text-gray-900 dark:text-gray-100">Tổng cộng</span>
              <span className="text-2xl font-bold text-orange-600">
                {formatCurrency(parsePrice(cart.total_price))}
              </span>
            </div>
            <p className="mt-1 text-xs text-gray-400 text-right">Đã bao gồm VAT (nếu có)</p>
          </div>

          <Button 
            className="w-full h-12 bg-orange-500 hover:bg-orange-600 text-base font-semibold shadow-lg shadow-orange-500/20"
            onClick={() => navigate("/checkout")}
          >
            Thanh toán ngay <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
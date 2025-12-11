import { useLoaderData, useNavigate } from "react-router";
import { 
  ArrowLeft, 
  MapPin, 
  User, 
  Phone, 
  Package, 
  Truck,
  CheckCircle,
  XCircle,
  Clock
} from "lucide-react";
import { vendorOrdersApi } from "~/lib/services";
import { formatCurrency, cn } from "~/lib/utils";
import { Button } from "~/components/ui";
// Use built-in Intl for date formatting to avoid date-fns dependency
import toast from "react-hot-toast";

export function meta() {
  return [
    { title: "Chi tiết đơn hàng - Kênh người bán" },
  ];
}

export async function clientLoader({ params }: { params: { id: string } }) {
  try {
    const order = await vendorOrdersApi.getOrderItem(params.id);
    return { order };
  } catch (error) {
    throw new Response("Order not found", { status: 404 });
  }
}

export default function SellerOrderDetailPage() {
  const { order } = useLoaderData<typeof clientLoader>();
  const navigate = useNavigate();

  const updateStatus = async (status: string) => {
    try {
      await vendorOrdersApi.updateOrderItemStatus(order.id, { status });
      toast.success(`Đã cập nhật trạng thái: ${status}`);
      // Refresh data
      navigate(".", { replace: true });
    } catch (error) {
      toast.error("Lỗi cập nhật trạng thái");
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      <Button 
        variant="ghost" 
        onClick={() => navigate("/seller/orders")}
        className="mb-6 gap-2 text-gray-500 hover:text-orange-500"
      >
        <ArrowLeft className="h-4 w-4" /> Quay lại danh sách
      </Button>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Order Header */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  Đơn hàng #{order.order_number}
                </h1>
                <p className="text-sm text-gray-500 mt-1">
                  Ngày đặt: {new Date(order.created_at).toLocaleString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false })}
                </p>
              </div>
              <span className={cn(
                "px-3 py-1 rounded-full text-sm font-medium",
                order.status === 'delivered' ? "bg-green-100 text-green-700" : 
                order.status === 'cancelled' ? "bg-red-100 text-red-700" : "bg-blue-100 text-blue-700"
              )}>
                {order.status.toUpperCase()}
              </span>
            </div>
          </div>

          {/* Product List */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
            <h3 className="font-semibold mb-4 flex items-center gap-2">
              <Package className="h-5 w-5 text-orange-500" /> Sản phẩm
            </h3>
            <div className="divide-y divide-gray-100 dark:divide-gray-800">
              <div className="flex items-start gap-4 py-4">
                <div className="h-20 w-20 flex-shrink-0 rounded-lg border border-gray-100 bg-gray-50 overflow-hidden">
                  <img 
                    src={order.product_image || "/placeholder.jpg"} 
                    alt={order.product_name} 
                    className="h-full w-full object-cover"
                  />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900 dark:text-gray-100">{order.product_name}</h4>
                  <p className="text-sm text-gray-500">{order.variant_name}</p>
                  <div className="mt-2 flex justify-between items-end">
                    <p className="text-sm text-gray-600">Số lượng: x{order.quantity}</p>
                    <p className="font-bold text-orange-600">{formatCurrency(order.unit_price)}</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-4 border-t border-gray-100 pt-4 flex justify-between items-center">
              <span className="font-medium">Tổng tiền hàng</span>
              <span className="text-xl font-bold text-orange-600">{formatCurrency(order.total_price)}</span>
            </div>
          </div>
        </div>

        {/* Sidebar Info */}
        <div className="space-y-6">
          {/* Customer Info */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
            <h3 className="font-semibold mb-4 flex items-center gap-2">
              <User className="h-5 w-5 text-blue-500" /> Khách hàng
            </h3>
            <div className="space-y-3 text-sm">
              <p className="font-medium text-lg">{order.customer_name}</p>
              <div className="flex items-start gap-3 text-gray-600 dark:text-gray-400">
                <MapPin className="h-4 w-4 mt-0.5 flex-shrink-0" />
                <span>{order.shipping_address}</span>
              </div>
              {order.customer_phone && (
                <div className="flex items-center gap-3 text-gray-600 dark:text-gray-400">
                  <Phone className="h-4 w-4" />
                  <span>{order.customer_phone}</span>
                </div>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
            <h3 className="font-semibold mb-4">Xử lý đơn hàng</h3>
            <div className="space-y-3">
              {order.status === "pending" && (
                <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white" onClick={() => updateStatus("confirmed")}>
                  <CheckCircle className="mr-2 h-4 w-4" /> Xác nhận đơn
                </Button>
              )}
              {order.status === "confirmed" && (
                <Button className="w-full bg-purple-600 hover:bg-purple-700 text-white" onClick={() => updateStatus("shipping")}>
                  <Truck className="mr-2 h-4 w-4" /> Giao cho vận chuyển
                </Button>
              )}
              {order.status === "shipping" && (
                <Button className="w-full bg-green-600 hover:bg-green-700 text-white" onClick={() => updateStatus("delivered")}>
                  <CheckCircle className="mr-2 h-4 w-4" /> Đã giao thành công
                </Button>
              )}
              {["pending", "confirmed"].includes(order.status) && (
                <Button variant="outline" className="w-full text-red-600 hover:bg-red-50 border-red-200" onClick={() => updateStatus("cancelled")}>
                  <XCircle className="mr-2 h-4 w-4" /> Hủy đơn hàng
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
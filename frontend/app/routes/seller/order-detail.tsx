import { Link, useLoaderData, type LoaderFunctionArgs } from "react-router";
import { useState } from "react";
import { 
  Package, User, MapPin, Phone, ArrowLeft, 
  CheckCircle, Clock, Truck, XCircle, Loader2
} from "lucide-react";
import { vendorOrdersApi } from "~/lib/services";
import { formatPrice, formatDate } from "~/lib/utils";
import { Button } from "~/components/ui";
import toast from "react-hot-toast";

export function meta({ params }: { params: { id?: string } }) {
  return [
    { title: `Đơn hàng - Seller Dashboard` },
    { name: "description", content: "Chi tiết đơn hàng" },
  ];
}

interface OrderItem {
  id: string;
  order_number: string;
  customer_name: string;
  shipping_address: string;
  product_name: string;
  variant_name: string | null;
  quantity: number;
  unit_price: { amount: string; currency: string };
  total_price: { amount: string; currency: string };
  status: string;
  commission_amount: { amount: string; currency: string };
  created_at: string;
}

export async function loader({ params }: LoaderFunctionArgs) {
  try {
    const orderItem = await vendorOrdersApi.getOrderItem(params.id as string);
    return { orderItem, error: null };
  } catch (error: any) {
    console.error("Failed to load order item:", error);
    return { orderItem: null, error: error.response?.data?.detail || "Không thể tải đơn hàng" };
  }
}

const statusConfig: Record<string, { label: string; color: string; icon: typeof Clock }> = {
  pending: { label: "Chờ xác nhận", color: "text-yellow-600 bg-yellow-100", icon: Clock },
  confirmed: { label: "Đã xác nhận", color: "text-blue-600 bg-blue-100", icon: CheckCircle },
  processing: { label: "Đang xử lý", color: "text-purple-600 bg-purple-100", icon: Package },
  shipped: { label: "Đang giao", color: "text-orange-600 bg-orange-100", icon: Truck },
  delivered: { label: "Đã giao", color: "text-green-600 bg-green-100", icon: CheckCircle },
  cancelled: { label: "Đã hủy", color: "text-red-600 bg-red-100", icon: XCircle },
};

const statusTransitions: Record<string, string[]> = {
  pending: ["confirmed", "cancelled"],
  confirmed: ["processing", "cancelled"],
  processing: ["shipped", "cancelled"],
  shipped: ["delivered"],
  delivered: [],
  cancelled: [],
};

export default function SellerOrderDetailPage() {
  const { orderItem, error } = useLoaderData<typeof loader>();
  const [isUpdating, setIsUpdating] = useState(false);
  const [currentStatus, setCurrentStatus] = useState(orderItem?.status || "");

  if (error || !orderItem) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Link to="/seller/orders" className="mb-4 inline-flex items-center text-orange-500 hover:underline">
          <ArrowLeft className="mr-2 h-4 w-4" /> Quay lại danh sách
        </Link>
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 dark:border-red-800 dark:bg-red-900/20">
          <p className="text-red-600 dark:text-red-400">{error || "Không tìm thấy đơn hàng"}</p>
        </div>
      </div>
    );
  }

  const handleUpdateStatus = async (newStatus: string) => {
    setIsUpdating(true);
    try {
      await vendorOrdersApi.updateOrderItemStatus(orderItem.id, { status: newStatus });
      setCurrentStatus(newStatus);
      toast.success(`Đã cập nhật trạng thái: ${statusConfig[newStatus]?.label}`);
    } catch (error: any) {
      toast.error(error.response?.data?.error || "Không thể cập nhật trạng thái");
    } finally {
      setIsUpdating(false);
    }
  };

  const status = statusConfig[currentStatus] || statusConfig.pending;
  const allowedTransitions = statusTransitions[currentStatus] || [];

  return (
    <div className="container mx-auto px-4 py-8">
      <Link to="/seller/orders" className="mb-4 inline-flex items-center text-orange-500 hover:underline">
        <ArrowLeft className="mr-2 h-4 w-4" /> Quay lại danh sách
      </Link>

      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
          Đơn hàng #{orderItem.order_number}
        </h1>
        <div className={`flex items-center gap-2 rounded-full px-4 py-2 ${status.color}`}>
          <status.icon className="h-4 w-4" />
          <span className="font-medium">{status.label}</span>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Order Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Product Details */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
            <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">Sản phẩm</h2>
            <div className="flex gap-4">
              <div className="h-20 w-20 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                <Package className="h-8 w-8 text-gray-400" />
              </div>
              <div className="flex-1">
                <h3 className="font-medium text-gray-900 dark:text-gray-100">{orderItem.product_name}</h3>
                {orderItem.variant_name && (
                  <p className="text-sm text-gray-500">{orderItem.variant_name}</p>
                )}
                <div className="mt-2 flex items-center gap-4 text-sm">
                  <span className="text-gray-600 dark:text-gray-400">SL: {orderItem.quantity}</span>
                  <span className="text-gray-600 dark:text-gray-400">
                    Đơn giá: {formatPrice(orderItem.unit_price)}
                  </span>
                </div>
              </div>
              <div className="text-right">
                <p className="text-lg font-bold text-orange-500">{formatPrice(orderItem.total_price)}</p>
                <p className="text-xs text-gray-500">
                  Hoa hồng: {formatPrice(orderItem.commission_amount)}
                </p>
              </div>
            </div>
          </div>

          {/* Customer Info */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
            <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">Thông tin khách hàng</h2>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <User className="h-5 w-5 text-gray-400" />
                <span className="text-gray-700 dark:text-gray-300">{orderItem.customer_name}</span>
              </div>
              <div className="flex items-start gap-3">
                <MapPin className="h-5 w-5 text-gray-400 mt-0.5" />
                <span className="text-gray-700 dark:text-gray-300">{orderItem.shipping_address}</span>
              </div>
            </div>
          </div>

          {/* Status Actions */}
          {allowedTransitions.length > 0 && (
            <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
              <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">Cập nhật trạng thái</h2>
              <div className="flex flex-wrap gap-3">
                {allowedTransitions.map((newStatus) => {
                  const config = statusConfig[newStatus];
                  return (
                    <Button
                      key={newStatus}
                      variant={newStatus === "cancelled" ? "outline" : "primary"}
                      onClick={() => handleUpdateStatus(newStatus)}
                      disabled={isUpdating}
                      className={newStatus === "cancelled" ? "border-red-500 text-red-500 hover:bg-red-50" : ""}
                    >
                      {isUpdating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                      {config?.label || newStatus}
                    </Button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Summary */}
        <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900 h-fit">
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">Tổng quan</h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Ngày đặt</span>
              <span className="text-gray-900 dark:text-gray-100">{formatDate(orderItem.created_at)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Tổng tiền</span>
              <span className="font-bold text-gray-900 dark:text-gray-100">{formatPrice(orderItem.total_price)}</span>
            </div>
            <hr className="border-gray-100 dark:border-gray-800" />
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Hoa hồng sàn</span>
              <span className="text-red-500">-{formatPrice(orderItem.commission_amount)}</span>
            </div>
            <div className="flex justify-between font-bold">
              <span className="text-gray-900 dark:text-gray-100">Thực nhận</span>
              <span className="text-green-600">
                {formatPrice({
                  amount: String(
                    parseFloat(orderItem.total_price.amount) - 
                    parseFloat(orderItem.commission_amount.amount)
                  ),
                  currency: orderItem.total_price.currency
                })}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

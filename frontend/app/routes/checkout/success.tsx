import { Link, useSearchParams } from "react-router";
import { useEffect, useState } from "react";
import { CheckCircle, Clock, XCircle, Loader2, Package, CreditCard } from "lucide-react";
import { ordersApi } from "~/lib/services";
import { formatCurrency, parsePrice } from "~/lib/utils";
import { Button } from "~/components/ui";
import type { Order } from "~/lib/types";

export function meta() {
  return [
    { title: "Đặt hàng thành công - OWLS" },
    { name: "description", content: "Cảm ơn bạn đã mua sắm" },
  ];
}

type OrderStatus = "loading" | "success" | "pending" | "failed";

export default function CheckoutSuccessPage() {
  const [searchParams] = useSearchParams();
  const orderId = searchParams.get("order_id");
  
  const [status, setStatus] = useState<OrderStatus>("loading");
  const [order, setOrder] = useState<Order | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const maxRetries = 5;

  useEffect(() => {
    if (!orderId) {
      setStatus("success"); // No order_id means COD or direct navigation, show success
      return;
    }

    const checkOrderStatus = async () => {
      try {
        const orderData = await ordersApi.getOrder(orderId);
        setOrder(orderData);

        if (orderData.payment_status === "paid") {
          setStatus("success");
        } else if (orderData.payment_status === "failed") {
          setStatus("failed");
        } else {
          // Payment pending - might be waiting for IPN callback
          if (retryCount < maxRetries) {
            // Poll again after 2 seconds
            setTimeout(() => setRetryCount((c) => c + 1), 2000);
            setStatus("pending");
          } else {
            // After max retries, show pending status (could be COD)
            setStatus("pending");
          }
        }
      } catch (error) {
        // If order not found or error, still show success (order was created)
        setStatus("success");
      }
    };

    checkOrderStatus();
  }, [orderId, retryCount]);

  // Loading state
  if (status === "loading") {
    return (
      <div className="container mx-auto flex min-h-[60vh] flex-col items-center justify-center px-4 text-center">
        <Loader2 className="h-12 w-12 animate-spin text-orange-500" />
        <p className="mt-4 text-gray-600 dark:text-gray-400">Đang xác nhận đơn hàng...</p>
      </div>
    );
  }

  // Payment failed
  if (status === "failed") {
    return (
      <div className="container mx-auto flex min-h-[60vh] flex-col items-center justify-center px-4 text-center">
        <div className="rounded-full bg-red-100 p-4 dark:bg-red-900/20">
          <XCircle className="h-12 w-12 text-red-500" />
        </div>
        <h1 className="mt-4 text-2xl font-bold text-gray-900 dark:text-gray-100">
          Thanh toán không thành công
        </h1>
        <p className="mt-2 max-w-md text-gray-600 dark:text-gray-400">
          Đã có lỗi xảy ra trong quá trình thanh toán. Đơn hàng của bạn đã được tạo nhưng chưa được thanh toán.
        </p>
        {order && (
          <p className="mt-2 text-sm text-gray-500">
            Mã đơn hàng: <span className="font-medium">{order.order_number}</span>
          </p>
        )}
        <div className="mt-6 flex gap-3">
          <Link to={order ? `/account/orders` : "/cart"}>
            <Button>
              {order ? "Xem đơn hàng" : "Quay lại giỏ hàng"}
            </Button>
          </Link>
          <Link to="/products">
            <Button variant="outline">Tiếp tục mua sắm</Button>
          </Link>
        </div>
      </div>
    );
  }

  // Payment pending (waiting for IPN or COD)
  if (status === "pending" && order) {
    // If payment_status is still pending after retries, it's likely COD
    const isProbablyCOD = retryCount >= maxRetries;
    
    return (
      <div className="container mx-auto flex min-h-[60vh] flex-col items-center justify-center px-4 text-center">
        <div className={`rounded-full p-4 ${isProbablyCOD ? "bg-green-100 dark:bg-green-900/20" : "bg-yellow-100 dark:bg-yellow-900/20"}`}>
          {isProbablyCOD ? (
            <CheckCircle className="h-12 w-12 text-green-500" />
          ) : (
            <Clock className="h-12 w-12 text-yellow-600" />
          )}
        </div>
        <h1 className="mt-4 text-2xl font-bold text-gray-900 dark:text-gray-100">
          {isProbablyCOD ? "Đặt hàng thành công!" : "Đang xử lý thanh toán"}
        </h1>
        <p className="mt-2 max-w-md text-gray-600 dark:text-gray-400">
          {isProbablyCOD 
            ? "Đơn hàng của bạn đã được tạo. Bạn sẽ thanh toán khi nhận hàng."
            : "Đơn hàng của bạn đã được tạo và đang chờ xác nhận thanh toán. Vui lòng đợi trong giây lát hoặc kiểm tra lại sau."
          }
        </p>
        <p className="mt-2 text-sm text-gray-500">
          Mã đơn hàng: <span className="font-medium">{order.order_number}</span>
        </p>
        <div className="mt-6 flex gap-3">
          <Link to="/account/orders">
            <Button>Xem đơn hàng</Button>
          </Link>
          <Link to="/products">
            <Button variant="outline">Tiếp tục mua sắm</Button>
          </Link>
        </div>
      </div>
    );
  }

  // Success state
  return (
    <div className="container mx-auto min-h-[60vh] px-4 py-12">
      <div className="mx-auto max-w-2xl">
        {/* Success Header */}
        <div className="text-center">
          <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/20">
            <CheckCircle className="h-10 w-10 text-green-500" />
          </div>
          <h1 className="mt-4 text-3xl font-bold text-gray-900 dark:text-gray-100">
            Đặt hàng thành công!
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Cảm ơn bạn đã mua sắm tại OWLS. Chúng tôi sẽ liên hệ để xác nhận đơn hàng sớm nhất.
          </p>
        </div>

        {/* Order Summary */}
        {order && (
          <div className="mt-8 rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between border-b border-gray-100 pb-4 dark:border-gray-800">
              <div>
                <p className="text-sm text-gray-500">Mã đơn hàng</p>
                <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                  {order.order_number}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">Trạng thái thanh toán</p>
                <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-sm font-medium ${
                  order.payment_status === "paid" 
                    ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                    : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400"
                }`}>
                  <CreditCard className="h-3.5 w-3.5" />
                  {order.payment_status === "paid" ? "Đã thanh toán" : "Chờ thanh toán (COD)"}
                </span>
              </div>
            </div>

            <div className="mt-4 space-y-3">
              <div className="flex items-center gap-3 text-sm">
                <Package className="h-4 w-4 text-gray-400" />
                <span className="text-gray-600 dark:text-gray-400">
                  {order.items?.length || 0} sản phẩm
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600 dark:text-gray-400">Tổng tiền:</span>
                <span className="text-xl font-bold text-orange-500">
                  {formatCurrency(parsePrice(order.total))}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
          <Link to="/account/orders">
            <Button size="lg" className="w-full sm:w-auto">
              Xem đơn hàng của tôi
            </Button>
          </Link>
          <Link to="/products">
            <Button variant="outline" size="lg" className="w-full sm:w-auto">
              Tiếp tục mua sắm
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}

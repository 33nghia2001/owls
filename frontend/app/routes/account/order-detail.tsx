import { useLoaderData, type LoaderFunctionArgs } from "react-router";
import { ordersApi } from "~/lib/services";
import type { Order } from "~/lib/types";
import { formatPrice, formatDate } from "~/lib/utils";

export function meta({ params }: { params: { id: string } }) {
  return [
    { title: `Đơn hàng ${params.id} - OWLS` },
    { name: "description", content: "Chi tiết đơn hàng" },
  ];
}

export async function loader({ params }: LoaderFunctionArgs) {
  const id = params.id as string;
  const order = await ordersApi.getOrder(id);
  return { order };
}

export default function OrderDetailPage() {
  const { order } = useLoaderData<typeof loader>();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Đơn hàng {order.order_number}</h1>
      <p className="mt-1 text-sm text-gray-500">Ngày đặt: {formatDate(order.created_at)}</p>

      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Sản phẩm</h2>
          <div className="mt-3 divide-y divide-gray-100 dark:divide-gray-800">
            {order.items.map((item: Order["items"][number]) => (
              <div key={item.id} className="flex items-center justify-between py-3 text-sm">
                <div>
                  <p className="font-medium text-gray-900 dark:text-gray-100">{item.product_name}</p>
                  {item.variant_name && <p className="text-xs text-gray-500">{item.variant_name}</p>}
                  <p className="text-xs text-gray-500">x{item.quantity}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900 dark:text-gray-100">
                    {formatPrice(item.total_price)}
                  </p>
                  <p className="text-xs text-gray-500">{formatPrice(item.unit_price)} / sản phẩm</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-5 text-sm text-gray-700 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-300">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Thông tin</h2>
          <div className="mt-3 space-y-2">
            <div className="flex justify-between">
              <span>Trạng thái</span>
              <span className="capitalize">{order.status}</span>
            </div>
            <div className="flex justify-between">
              <span>Thanh toán</span>
              <span className="capitalize">{order.payment_status}</span>
            </div>
            <div className="flex justify-between">
              <span>Tạm tính</span>
              <span>{formatPrice(order.subtotal)}</span>
            </div>
            <div className="flex justify-between">
              <span>Phí vận chuyển</span>
              <span>{formatPrice(order.shipping_fee)}</span>
            </div>
            <div className="flex justify-between">
              <span>Giảm giá</span>
              <span>-{formatPrice(order.discount)}</span>
            </div>
            <div className="flex justify-between text-lg font-semibold text-gray-900 dark:text-gray-100">
              <span>Tổng</span>
              <span>{formatPrice(order.total)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

import { Link, useLoaderData, type LoaderFunctionArgs } from "react-router";
import { ordersApi } from "~/lib/services";
import type { Order } from "~/lib/types";
import { formatDate, formatCurrency } from "~/lib/utils";

export function meta() {
  return [
    { title: "Đơn hàng - OWLS" },
    { name: "description", content: "Xem lịch sử đơn hàng" },
  ];
}

export async function loader({}: LoaderFunctionArgs) {
  const data = await ordersApi.getOrders();
  return { orders: data.results || [] };
}

export default function OrdersPage() {
  const { orders } = useLoaderData<typeof loader>();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-4 text-3xl font-bold text-gray-900 dark:text-gray-100">Đơn hàng</h1>
      <div className="overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-gray-600 dark:bg-gray-900 dark:text-gray-300">
            <tr>
              <th className="px-4 py-3">Mã đơn</th>
              <th className="px-4 py-3">Ngày đặt</th>
              <th className="px-4 py-3">Trạng thái</th>
              <th className="px-4 py-3">Thanh toán</th>
              <th className="px-4 py-3 text-right">Tổng</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
            {orders.map((order: Order) => (
              <tr key={order.id} className="hover:bg-orange-50/40 dark:hover:bg-gray-900/60">
                <td className="px-4 py-3 font-medium text-orange-600">
                  <Link to={`/account/orders/${order.id}`}>{order.order_number}</Link>
                </td>
                <td className="px-4 py-3 text-gray-600 dark:text-gray-300">{formatDate(order.created_at)}</td>
                <td className="px-4 py-3 capitalize text-gray-700 dark:text-gray-200">{order.status}</td>
                <td className="px-4 py-3 capitalize text-gray-700 dark:text-gray-200">{order.payment_status}</td>
                <td className="px-4 py-3 text-right font-semibold text-gray-900 dark:text-gray-100">
                  {formatCurrency(parseFloat(order.total.amount))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {orders.length === 0 && (
          <div className="p-6 text-center text-gray-600 dark:text-gray-300">Chưa có đơn hàng nào.</div>
        )}
      </div>
    </div>
  );
}

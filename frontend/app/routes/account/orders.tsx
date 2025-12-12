import { Link, useLoaderData, type ClientLoaderFunctionArgs } from "react-router";
import { ordersApi } from "~/lib/services";
import type { Order } from "~/lib/types";
import { formatDate, formatPrice } from "~/lib/utils";

export function meta() {
  return [
    { title: "Đơn hàng - OWLS" },
    { name: "description", content: "Xem lịch sử đơn hàng" },
  ];
}

export async function clientLoader({}: ClientLoaderFunctionArgs) {
  try {
    const data = await ordersApi.getOrders();
    return { orders: data.results || [] };
  } catch (error: unknown) {
    const axiosErr = error as { response?: { status?: number } };
    // If 401, user is not authenticated - return empty orders
    if (axiosErr.response?.status === 401) {
      return { orders: [] };
    }
    throw error;
  }
}

export default function OrdersPage() {
  const { orders } = useLoaderData<typeof clientLoader>();

  if (orders.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="mb-4 text-3xl font-bold text-gray-900 dark:text-gray-100">Đơn hàng</h1>
        <div className="rounded-xl border border-gray-200 bg-white p-12 text-center dark:border-gray-800 dark:bg-gray-900">
          <p className="text-gray-600 dark:text-gray-400">Bạn chưa có đơn hàng nào.</p>
          <Link to="/products" className="mt-4 inline-block rounded-lg bg-orange-500 px-6 py-2 text-white hover:bg-orange-600">
            Mua sắm ngay
          </Link>
        </div>
      </div>
    );
  }

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
                  {formatPrice(order.total)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

import { useLoaderData, type ClientLoaderFunctionArgs } from "react-router";
import { ordersApi } from "~/lib/services";
import type { Order } from "~/lib/types";
import { formatPrice, formatDate } from "~/lib/utils";
import { MapPin, Phone, User, StickyNote } from "lucide-react";

export function meta({ params }: { params: { id: string } }) {
  return [
    { title: `Đơn hàng ${params.id} - OWLS` },
    { name: "description", content: "Chi tiết đơn hàng" },
  ];
}

export async function clientLoader({ params }: ClientLoaderFunctionArgs) {
  const id = params.id as string;
  const order = await ordersApi.getOrder(id);
  return { order };
}

export default function OrderDetailPage() {
  const { order } = useLoaderData<typeof clientLoader>();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Đơn hàng {order.order_number}</h1>
      <p className="mt-1 text-sm text-gray-500">Ngày đặt: {formatDate(order.created_at)}</p>

      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        {/* Cột bên trái: Thông tin giao hàng & Sản phẩm */}
        <div className="lg:col-span-2 space-y-4">
          
          {/* 1. Thông tin giao hàng (Mới thêm) */}
          <div className="rounded-xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900">
            <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              <MapPin className="h-5 w-5 text-orange-500" />
              Thông tin giao hàng
            </h2>
            
            <div className="grid gap-4 md:grid-cols-2 text-sm">
              <div className="space-y-1">
                <p className="flex items-center gap-2 text-gray-500">
                  <User className="h-4 w-4" /> Người nhận
                </p>
                <p className="font-medium text-gray-900 dark:text-gray-100 pl-6">
                  {order.shipping_name}
                </p>
              </div>

              <div className="space-y-1">
                <p className="flex items-center gap-2 text-gray-500">
                  <Phone className="h-4 w-4" /> Số điện thoại
                </p>
                <p className="font-medium text-gray-900 dark:text-gray-100 pl-6">
                  {order.shipping_phone}
                </p>
              </div>

              <div className="space-y-1 md:col-span-2">
                <p className="flex items-center gap-2 text-gray-500">
                  <MapPin className="h-4 w-4" /> Địa chỉ
                </p>
                <p className="font-medium text-gray-900 dark:text-gray-100 pl-6">
                  {order.shipping_address}, {order.shipping_ward}, {order.shipping_province}
                </p>
              </div>

              {order.customer_note && (
                <div className="space-y-1 md:col-span-2">
                  <p className="flex items-center gap-2 text-gray-500">
                    <StickyNote className="h-4 w-4" /> Ghi chú
                  </p>
                  <p className="pl-6 text-gray-700 dark:text-gray-300 italic bg-gray-50 dark:bg-gray-800/50 p-2 rounded">
                    "{order.customer_note}"
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* 2. Danh sách sản phẩm */}
          <div className="rounded-xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">Sản phẩm</h2>
            <div className="divide-y divide-gray-100 dark:divide-gray-800">
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
                    <p className="text-xs text-gray-500">{formatPrice(item.unit_price)} / cái</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Cột bên phải: Tổng quan đơn hàng */}
        <div className="h-fit rounded-xl border border-gray-200 bg-white p-5 text-sm text-gray-700 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-300 lg:sticky lg:top-24">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Tổng quan</h2>
          <div className="mt-3 space-y-3">
            <div className="flex justify-between items-center">
              <span>Trạng thái</span>
              <span className={`px-2 py-1 rounded text-xs font-medium capitalize
                ${order.status === 'delivered' ? 'bg-green-100 text-green-700' : 
                  order.status === 'cancelled' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
                }`}>
                {order.status}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Thanh toán</span>
              <span className="capitalize font-medium">{order.payment_status}</span>
            </div>
            <div className="border-t border-gray-100 dark:border-gray-800 my-2 pt-2 space-y-2">
              <div className="flex justify-between">
                <span>Tạm tính</span>
                <span>{formatPrice(order.subtotal)}</span>
              </div>
              <div className="flex justify-between">
                <span>Phí vận chuyển</span>
                {/* Đã sửa shipping_fee -> shipping_cost */}
                <span>{Number(order.shipping_cost) === 0 ? "Miễn phí" : formatPrice(order.shipping_cost)}</span>
              </div>
              <div className="flex justify-between text-green-600">
                <span>Giảm giá</span>
                {/* Đã sửa discount -> discount_amount */}
                <span>-{formatPrice(order.discount_amount)}</span>
              </div>
            </div>
            <div className="border-t border-gray-100 dark:border-gray-800 pt-2 flex justify-between text-lg font-bold text-orange-500">
              <span>Tổng cộng</span>
              <span>{formatPrice(order.total)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
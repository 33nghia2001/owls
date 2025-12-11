import { Link, useLoaderData, useSearchParams, Form, useSubmit } from "react-router";
import { 
  ShoppingBag, 
  Search, 
  Filter, 
  ChevronRight, 
  Calendar 
} from "lucide-react";
import { vendorOrdersApi } from "~/lib/services";
import { formatCurrency, cn } from "~/lib/utils";
import { Button, Input } from "~/components/ui";
// Use Intl.DateTimeFormat to avoid external dependency on date-fns during dev


export function meta() {
  return [
    { title: "Đơn hàng - Kênh người bán" },
  ];
}

export async function clientLoader({ request }: { request: Request }) {
  const url = new URL(request.url);
  const page = Number(url.searchParams.get("page")) || 1;
  const status = url.searchParams.get("status");
  const search = url.searchParams.get("q");

  try {
    const data = await vendorOrdersApi.getOrders({ 
      page, 
      status: status || undefined,
    });
    return { 
      orders: Array.isArray(data) ? data : (data.results || []),
      pagination: { count: data.count || 0, next: data.next } 
    };
  } catch {
    return { orders: [], pagination: { count: 0 } };
  }
}

const OrderStatusBadge = ({ status }: { status: string }) => {
  const colors: Record<string, string> = {
    pending: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
    confirmed: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
    shipping: "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400",
    delivered: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
    cancelled: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
  };
  
  const labels: Record<string, string> = {
    pending: "Chờ xử lý",
    confirmed: "Đã xác nhận",
    shipping: "Đang giao",
    delivered: "Hoàn tất",
    cancelled: "Đã hủy",
  };

  return (
    <span className={cn("px-2.5 py-0.5 rounded-full text-xs font-medium border border-transparent", colors[status] || "bg-gray-100 text-gray-600")}>
      {labels[status] || status}
    </span>
  );
};

export default function SellerOrdersPage() {
  const { orders, pagination } = useLoaderData<typeof clientLoader>();
  const [searchParams] = useSearchParams();
  const submit = useSubmit();
  const currentStatus = searchParams.get("status") || "all";

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <ShoppingBag className="h-6 w-6 text-orange-500" />
            Quản lý đơn hàng
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            {pagination.count} đơn hàng cần xử lý
          </p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="mb-6 overflow-x-auto pb-2">
        <div className="flex gap-2">
          {[
            { id: "all", label: "Tất cả" },
            { id: "pending", label: "Chờ xử lý" },
            { id: "confirmed", label: "Đã xác nhận" },
            { id: "shipping", label: "Đang giao" },
            { id: "delivered", label: "Hoàn thành" },
            { id: "cancelled", label: "Đã hủy" },
          ].map((tab) => (
            <Button
              key={tab.id}
              variant={currentStatus === tab.id ? "secondary" : "ghost"}
              className={cn(
                "whitespace-nowrap rounded-full px-4",
                currentStatus === tab.id && "bg-orange-500 text-white hover:bg-orange-600"
              )}
              onClick={() => {
                const params = new URLSearchParams(searchParams);
                if (tab.id === "all") params.delete("status");
                else params.set("status", tab.id);
                submit(params);
              }}
            >
              {tab.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Search Bar */}
      <div className="mb-6 max-w-md">
        <Form className="relative" onChange={(e) => submit(e.currentTarget)}>
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input 
            name="q" 
            placeholder="Tìm theo mã đơn hàng hoặc tên khách..." 
            className="pl-9 rounded-xl"
            defaultValue={searchParams.get("q") || ""}
          />
        </Form>
      </div>

      {/* Order List */}
      <div className="space-y-4">
        {orders.length > 0 ? (
          orders.map((order: any) => (
            <div 
              key={order.id} 
              className="group rounded-xl border border-gray-200 bg-white p-5 transition-all hover:border-orange-300 hover:shadow-md dark:border-gray-800 dark:bg-gray-900"
            >
              <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-lg font-bold text-gray-900 dark:text-gray-100">
                      #{order.order_number}
                    </span>
                    <OrderStatusBadge status={order.status} />
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Calendar className="h-3.5 w-3.5" />
                    {new Date(order.created_at).toLocaleString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false })}
                  </div>
                </div>

                <div className="flex items-center gap-8">
                  <div className="text-right">
                    <p className="text-xs text-gray-500">Tổng tiền</p>
                    <p className="font-bold text-orange-600 text-lg">
                      {formatCurrency(order.total_amount || order.total)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500">Khách hàng</p>
                    <p className="font-medium text-gray-900 dark:text-gray-100">{order.customer_name}</p>
                  </div>
                  <Link to={`/seller/orders/${order.id}`}>
                    <Button variant="outline" size="sm" className="rounded-full">
                      Chi tiết <ChevronRight className="ml-1 h-4 w-4" />
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="flex flex-col items-center justify-center py-16 rounded-xl border-2 border-dashed border-gray-200 bg-gray-50/50">
            <ShoppingBag className="h-12 w-12 text-gray-300 mb-3" />
            <p className="text-gray-500">Chưa có đơn hàng nào.</p>
          </div>
        )}
      </div>
    </div>
  );
}
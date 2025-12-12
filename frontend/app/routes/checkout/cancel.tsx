import { Link, useSearchParams } from "react-router";
import { XCircle, ArrowLeft, ShoppingCart } from "lucide-react";
import { Button } from "~/components/ui";

export function meta() {
  return [
    { title: "Thanh toán bị hủy - OWLS" },
    { name: "description", content: "Thanh toán đã bị hủy" },
  ];
}

export default function CheckoutCancelPage() {
  const [searchParams] = useSearchParams();
  const orderId = searchParams.get("order_id");

  return (
    <div className="container mx-auto flex min-h-[60vh] flex-col items-center justify-center px-4 text-center">
      <div className="rounded-full bg-gray-100 p-4 dark:bg-gray-800">
        <XCircle className="h-12 w-12 text-gray-500" />
      </div>
      
      <h1 className="mt-4 text-2xl font-bold text-gray-900 dark:text-gray-100">
        Thanh toán đã bị hủy
      </h1>
      
      <p className="mt-2 max-w-md text-gray-600 dark:text-gray-400">
        Bạn đã hủy quá trình thanh toán. Đơn hàng của bạn vẫn được lưu trong giỏ hàng.
        Bạn có thể quay lại thanh toán bất cứ lúc nào.
      </p>

      {orderId && (
        <p className="mt-2 text-sm text-gray-500">
          Đơn hàng liên quan: <span className="font-medium">{orderId}</span>
        </p>
      )}

      <div className="mt-8 flex flex-col gap-3 sm:flex-row">
        <Link to="/checkout">
          <Button size="lg" className="flex items-center gap-2">
            <ArrowLeft className="h-4 w-4" />
            Quay lại thanh toán
          </Button>
        </Link>
        <Link to="/cart">
          <Button variant="outline" size="lg" className="flex items-center gap-2">
            <ShoppingCart className="h-4 w-4" />
            Xem giỏ hàng
          </Button>
        </Link>
      </div>

      <Link 
        to="/products" 
        className="mt-4 text-sm text-gray-500 hover:text-orange-500 transition-colors"
      >
        hoặc tiếp tục mua sắm
      </Link>
    </div>
  );
}

import { Link } from "react-router";
import { CheckCircle } from "lucide-react";

export function meta() {
  return [
    { title: "Đặt hàng thành công - OWLS" },
    { name: "description", content: "Cảm ơn bạn đã mua sắm" },
  ];
}

export default function CheckoutSuccessPage() {
  return (
    <div className="container mx-auto flex min-h-[60vh] flex-col items-center justify-center px-4 text-center">
      <CheckCircle className="h-16 w-16 text-green-500" />
      <h1 className="mt-4 text-3xl font-bold text-gray-900 dark:text-gray-100">Đặt hàng thành công</h1>
      <p className="mt-2 text-gray-600 dark:text-gray-300">
        Cảm ơn bạn đã mua sắm tại OWLS. Chúng tôi sẽ liên hệ để xác nhận đơn hàng sớm nhất.
      </p>
      <div className="mt-6 flex gap-3">
        <Link
          to="/account/orders"
          className="rounded-lg bg-orange-500 px-4 py-2 font-medium text-white transition hover:bg-orange-600"
        >
          Xem đơn hàng
        </Link>
        <Link
          to="/products"
          className="rounded-lg border border-gray-200 px-4 py-2 font-medium text-gray-700 transition hover:border-orange-500 hover:text-orange-500 dark:border-gray-800 dark:text-gray-200"
        >
          Tiếp tục mua sắm
        </Link>
      </div>
    </div>
  );
}

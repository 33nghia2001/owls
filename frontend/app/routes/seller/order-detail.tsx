import { useLoaderData, type LoaderFunctionArgs } from "react-router";

export function meta({ params }: { params: { id?: string } }) {
  return [
    { title: `Đơn hàng ${params.id} - Seller Dashboard` },
    { name: "description", content: "Chi tiết đơn hàng" },
  ];
}

export async function loader({ params }: LoaderFunctionArgs) {
  return { orderId: params.id };
}

export default function SellerOrderDetailPage() {
  const { orderId } = useLoaderData<typeof loader>();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-6 text-3xl font-bold text-gray-900 dark:text-gray-100">Đơn hàng #{orderId}</h1>

      <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
        <p className="text-gray-600 dark:text-gray-300">Chi tiết đơn hàng đang được phát triển...</p>
      </div>
    </div>
  );
}

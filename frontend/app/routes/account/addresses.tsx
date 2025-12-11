import { useLoaderData, type LoaderFunctionArgs } from "react-router";
import { addressApi } from "~/lib/services";
import type { ShippingAddress } from "~/lib/types";

export function meta() {
  return [
    { title: "Địa chỉ - OWLS" },
    { name: "description", content: "Quản lý địa chỉ giao hàng" },
  ];
}

export async function loader({}: LoaderFunctionArgs) {
  const addresses = await addressApi.getAddresses();
  return { addresses };
}

export default function AddressesPage() {
  const { addresses } = useLoaderData<typeof loader>();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-4 text-3xl font-bold text-gray-900 dark:text-gray-100">Địa chỉ giao hàng</h1>
      <div className="grid gap-4 md:grid-cols-2">
        {addresses.map((addr: ShippingAddress) => (
          <div
            key={addr.id}
            className="rounded-xl border border-gray-200 bg-white p-5 text-sm text-gray-700 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-300"
          >
            <div className="flex items-center justify-between">
              <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">{addr.full_name}</p>
              {addr.is_default && (
                <span className="rounded-full bg-orange-100 px-3 py-1 text-xs font-semibold text-orange-600 dark:bg-orange-900/30">Mặc định</span>
              )}
            </div>
            <p className="mt-1">{addr.address_line1}</p>
            {addr.address_line2 && <p>{addr.address_line2}</p>}
            <p>
              {addr.city}, {addr.state}
            </p>
            <p>Điện thoại: {addr.phone}</p>
          </div>
        ))}
      </div>
      {addresses.length === 0 && (
        <p className="text-gray-600 dark:text-gray-300">Chưa có địa chỉ nào.</p>
      )}
    </div>
  );
}

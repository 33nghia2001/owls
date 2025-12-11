import { useLoaderData } from "react-router";
import { addressApi } from "~/lib/services";
import type { ShippingAddress } from "~/lib/types";

export function meta() {
  return [
    { title: "Địa chỉ - OWLS" },
    { name: "description", content: "Quản lý địa chỉ giao hàng" },
  ];
}

// Chạy ở client để truy cập được Token trong localStorage
export async function clientLoader() {
  try {
    const response = await addressApi.getAddresses();
    
    // SỬA LỖI: Kiểm tra xem response có phải dạng phân trang (có .results) không
    // Nếu có .results thì lấy mảng từ đó, nếu không thì dùng chính response (nếu là mảng)
    const addresses = Array.isArray(response) 
      ? response 
      : (response.results || []);

    return { addresses };
  } catch (error: any) {
    // Nếu lỗi 401 (chưa đăng nhập), trả về danh sách rỗng để không crash trang
    if (error.response?.status === 401) {
      return { addresses: [] };
    }
    throw error;
  }
}

// Skeleton loading khi đang fetch dữ liệu
export function HydrateFallback() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-4 text-3xl font-bold text-gray-900 dark:text-gray-100">Địa chỉ giao hàng</h1>
      <div className="grid gap-4 md:grid-cols-2">
        {[1, 2].map((i) => (
          <div key={i} className="h-32 rounded-xl border border-gray-200 bg-gray-50 animate-pulse dark:border-gray-800 dark:bg-gray-900" />
        ))}
      </div>
    </div>
  );
}

export default function AddressesPage() {
  const { addresses } = useLoaderData<typeof clientLoader>();

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Địa chỉ giao hàng</h1>
        {/* Nút thêm mới (Placeholder - cần implement modal/navigate sau này) */}
        <button className="rounded-lg bg-orange-500 px-4 py-2 text-sm font-bold text-white transition hover:bg-orange-600">
          + Thêm địa chỉ
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {addresses.map((addr: ShippingAddress) => (
          <div
            key={addr.id}
            className="group relative rounded-xl border border-gray-200 bg-white p-5 text-sm text-gray-700 transition hover:border-orange-200 hover:shadow-md dark:border-gray-800 dark:bg-gray-900 dark:text-gray-300"
          >
            <div className="flex items-center justify-between">
              <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">{addr.full_name}</p>
              {addr.is_default && (
                <span className="rounded-full bg-orange-100 px-3 py-1 text-xs font-semibold text-orange-600 dark:bg-orange-900/30">Mặc định</span>
              )}
            </div>
            <div className="mt-3 space-y-1">
              <p className="text-gray-600 dark:text-gray-400">{addr.address_line1}</p>
              {addr.address_line2 && <p className="text-gray-600 dark:text-gray-400">{addr.address_line2}</p>}
              <p className="text-gray-900 dark:text-gray-200 font-medium">
                {addr.city}, {addr.state}
              </p>
              <p className="flex items-center gap-2 pt-1 text-gray-500 dark:text-gray-400">
                <span>📞 {addr.phone}</span>
              </p>
            </div>
            
            {/* Action Buttons (Ví dụ) */}
            <div className="mt-4 flex gap-2 border-t border-gray-100 pt-3 dark:border-gray-800 opacity-0 transition-opacity group-hover:opacity-100">
              <button className="text-xs font-medium text-blue-600 hover:underline">Sửa</button>
              <span className="text-gray-300">|</span>
              <button className="text-xs font-medium text-red-600 hover:underline">Xóa</button>
            </div>
          </div>
        ))}
      </div>
      
      {addresses.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 rounded-xl border-2 border-dashed border-gray-200 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/50">
          <p className="text-gray-500 dark:text-gray-400 mb-4">Bạn chưa lưu địa chỉ nào.</p>
          <button className="text-orange-600 font-medium hover:underline">Thêm địa chỉ ngay</button>
        </div>
      )}
    </div>
  );
}
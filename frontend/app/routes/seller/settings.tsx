import { Form } from "react-router";
import { Store, Save, MapPin } from "lucide-react";
import { Button, Input } from "~/components/ui";

export function meta() {
  return [
    { title: "Cài đặt cửa hàng - Kênh người bán" },
  ];
}

export default function SellerSettingsPage() {
  // Mock data - replace with actual loader data later
  const shop = {
    name: "OWLS Official Store",
    description: "Cửa hàng chính hãng chuyên cung cấp các sản phẩm thời trang.",
    address: "123 Nguyễn Văn Linh, Quận 7, TP.HCM",
    phone: "0901234567"
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
          <Store className="h-6 w-6 text-orange-500" />
          Cài đặt cửa hàng
        </h1>
        <p className="text-sm text-gray-500 mt-1">Quản lý thông tin hiển thị của shop bạn</p>
      </div>

      <div className="grid gap-8">
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <h2 className="text-lg font-semibold mb-6 border-b border-gray-100 pb-4 dark:border-gray-800">Thông tin cơ bản</h2>
          
          <form className="space-y-6">
            <div className="flex items-center gap-6">
              <div className="h-24 w-24 rounded-full bg-gray-100 border-2 border-dashed border-gray-300 flex items-center justify-center text-gray-400">
                Logo
              </div>
              <Button variant="outline" size="sm">Thay đổi logo</Button>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium">Tên cửa hàng</label>
                <Input defaultValue={shop.name} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Số điện thoại liên hệ</label>
                <Input defaultValue={shop.phone} />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Giới thiệu cửa hàng</label>
              <textarea 
                className="w-full rounded-lg border border-gray-200 bg-transparent px-3 py-2 text-sm focus:border-orange-500 focus:outline-none dark:border-gray-800 min-h-[100px]"
                defaultValue={shop.description}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Địa chỉ kho hàng</label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input className="pl-9" defaultValue={shop.address} />
              </div>
            </div>

            <div className="pt-4 flex justify-end">
              <Button className="bg-orange-500 hover:bg-orange-600 text-white">
                <Save className="mr-2 h-4 w-4" /> Lưu thay đổi
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
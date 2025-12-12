import { useState, useEffect } from "react";
import { 
  useLoaderData, 
  useFetcher, 
  type ActionFunctionArgs 
} from "react-router";
import { 
  Plus, 
  MapPin, 
  Phone, 
  Trash2, 
  Edit, 
  CheckCircle2,
  Loader2 
} from "lucide-react";
import { addressApi } from "~/lib/services";
import type { ShippingAddress } from "~/lib/types";
import { Button, Input, useConfirm } from "~/components/ui";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "~/components/ui/dialog";
import { toast } from "react-hot-toast";
import { cn } from "~/lib/utils";

// --- META ---
export function meta() {
  return [
    { title: "Sổ địa chỉ - OWLS" },
    { name: "description", content: "Quản lý địa chỉ giao hàng của bạn" },
  ];
}

// --- LOADER (Client Side) ---
export async function clientLoader() {
  try {
    const response = await addressApi.getAddresses();
    // Xử lý dữ liệu trả về (mảng hoặc phân trang)
    const addresses = Array.isArray(response) 
      ? response 
      : (response.results || []);
    return { addresses };
  } catch (error: unknown) {
    const axiosErr = error as { response?: { status?: number } };
    if (axiosErr.response?.status === 401) return { addresses: [] };
    throw error;
  }
}

// --- ACTION (Xử lý Thêm/Xóa/Sửa) ---
export async function clientAction({ request }: ActionFunctionArgs) {
  const formData = await request.formData();
  const intent = formData.get("intent");

  try {
    if (intent === "create") {
      // Map dữ liệu từ Form (name="...") sang cấu trúc Backend (Serializer)
      const data: Partial<ShippingAddress> = {
        full_name: formData.get("full_name") as string,
        phone: formData.get("phone") as string,
        
        // Mapping: Input Name -> Backend Field
        street_address: formData.get("address_line1") as string, 
        city: formData.get("province") as string, // Tỉnh/Thành phố
        state: formData.get("ward") as string,    // Phường/Xã
        
        postal_code: formData.get("postal_code") as string || "700000",
        country: "Vietnam",
        is_default: formData.get("is_default") === "on",
      };

      await addressApi.createAddress(data);
      toast.success("Thêm địa chỉ thành công!");
    } 
    
    else if (intent === "delete") {
      const id = formData.get("id") as string;
      await addressApi.deleteAddress(id);
      toast.success("Đã xóa địa chỉ");
    }

    else if (intent === "set_default") {
      const id = formData.get("id") as string;
      await addressApi.setDefaultAddress(id);
      toast.success("Đã đặt làm mặc định");
    }

    return { success: true };
  } catch (error: unknown) {
    const axiosErr = error as { response?: { data?: { detail?: string } } };
    const msg = axiosErr.response?.data?.detail || "Có lỗi xảy ra";
    toast.error(msg);
    return { success: false, error: msg };
  }
}

// --- LOADING SKELETON ---
export function HydrateFallback() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="flex justify-between items-center mb-6">
        <div className="h-8 w-48 bg-gray-200 rounded animate-pulse" />
        <div className="h-10 w-32 bg-gray-200 rounded animate-pulse" />
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {[1, 2].map((i) => (
          <div key={i} className="h-40 rounded-xl border border-gray-200 bg-gray-50 animate-pulse" />
        ))}
      </div>
    </div>
  );
}

// --- MAIN COMPONENT ---
export default function AddressesPage() {
  const { addresses } = useLoaderData<typeof clientLoader>();
  const fetcher = useFetcher();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const { confirm, ConfirmDialog } = useConfirm();
  const isSubmitting = fetcher.state === "submitting";

  useEffect(() => {
    if (fetcher.state === "idle" && fetcher.data?.success) {
      setIsModalOpen(false);
    }
  }, [fetcher.state, fetcher.data]);

  const handleDelete = async (id: string) => {
    const confirmed = await confirm({
      title: "Xóa địa chỉ?",
      description: "Bạn có chắc muốn xóa địa chỉ này? Hành động này không thể hoàn tác.",
      confirmText: "Xóa địa chỉ",
      variant: "danger",
    });
    if (confirmed) {
      const formData = new FormData();
      formData.append("intent", "delete");
      formData.append("id", id);
      fetcher.submit(formData, { method: "post" });
    }
  };

  return (
    <>
    {ConfirmDialog}
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <MapPin className="h-6 w-6 text-orange-500" />
            Sổ địa chỉ
          </h1>
          <p className="text-sm text-gray-500 mt-1">Quản lý nơi nhận hàng của bạn</p>
        </div>
        
        <Button 
          onClick={() => setIsModalOpen(true)}
          className="gap-2 bg-orange-500 hover:bg-orange-600 text-white shadow-lg shadow-orange-500/20"
        >
          <Plus className="h-4 w-4" />
          Thêm địa chỉ mới
        </Button>
      </div>

      {/* Address Grid */}
      <div className="grid gap-5 md:grid-cols-2">
        {addresses.map((addr: ShippingAddress) => (
          <div
            key={addr.id}
            className={cn(
              "group relative flex flex-col justify-between rounded-xl border p-5 transition-all hover:shadow-md bg-white dark:bg-gray-900",
              addr.is_default 
                ? "border-orange-500 ring-1 ring-orange-500/20 dark:border-orange-500/50" 
                : "border-gray-200 dark:border-gray-800"
            )}
          >
            {/* Card Content */}
            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-gray-900 dark:text-gray-100 text-lg">
                      {addr.full_name}
                    </span>
                    {addr.is_default && (
                      <span className="inline-flex items-center gap-1 rounded-full bg-orange-100 px-2 py-0.5 text-xs font-medium text-orange-700 dark:bg-orange-900/30 dark:text-orange-400">
                        <CheckCircle2 className="h-3 w-3" /> Mặc định
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                    <Phone className="h-3.5 w-3.5" />
                    {addr.phone}
                  </div>
                </div>
              </div>

              <div className="text-sm text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-800/50 p-3 rounded-lg">
                <p className="font-medium">{addr.street_address || ""}</p>
                {/* Backend Address model uses city (province) and state (ward) */}
                <p>
                  {addr.state || ""}
                  {addr.state && addr.city ? ", " : ""}
                  {addr.city || ""}
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="mt-5 flex items-center justify-between border-t border-gray-100 pt-4 dark:border-gray-800">
              {!addr.is_default && (
                <fetcher.Form method="post">
                  <input type="hidden" name="intent" value="set_default" />
                  <input type="hidden" name="id" value={addr.id} />
                  <button 
                    type="submit"
                    className="text-xs font-medium text-gray-500 hover:text-orange-600 hover:underline transition-colors"
                  >
                    Đặt làm mặc định
                  </button>
                </fetcher.Form>
              )}
              
              <div className="flex items-center gap-3 ml-auto">
                <button className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-all dark:hover:bg-blue-900/20">
                  <Edit className="h-4 w-4" />
                </button>
                
                <button 
                  type="button"
                  onClick={() => handleDelete(addr.id)}
                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-all dark:hover:bg-red-900/20"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Confirm Dialog */}
      {ConfirmDialog}

      {/* Empty State */}
      {addresses.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 rounded-2xl border-2 border-dashed border-gray-200 bg-gray-50/50 dark:border-gray-800 dark:bg-gray-900/50">
          <MapPin className="h-12 w-12 text-gray-300 mb-3" />
          <p className="text-gray-500 dark:text-gray-400 mb-4 font-medium">
            Bạn chưa lưu địa chỉ nào
          </p>
          <Button variant="outline" onClick={() => setIsModalOpen(true)}>
            Thêm địa chỉ ngay
          </Button>
        </div>
      )}

      {/* Create Address Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Thêm địa chỉ mới</DialogTitle>
            <DialogDescription>
              Thông tin này sẽ được dùng để giao hàng cho bạn.
            </DialogDescription>
          </DialogHeader>

          <fetcher.Form method="post" className="space-y-4 py-4">
            <input type="hidden" name="intent" value="create" />
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Họ tên</label>
                <Input name="full_name" placeholder="Nguyễn Văn A" required />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Số điện thoại</label>
                <Input name="phone" placeholder="0901..." required />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Địa chỉ chi tiết</label>
              <Input name="address_line1" placeholder="Số nhà, tên đường..." required />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Tỉnh / Thành phố</label>
                {/* Giữ nguyên name="province" để Form bắt được, logic map ở clientAction */}
                <Input name="province" placeholder="Hồ Chí Minh" required />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Phường / Xã</label>
                {/* Giữ nguyên name="ward" để Form bắt được */}
                <Input name="ward" placeholder="Phường Bến Nghé" required />
              </div>
            </div>

            <div className="flex items-center gap-2 pt-2">
              <input 
                type="checkbox" 
                id="is_default" 
                name="is_default" 
                className="h-4 w-4 rounded border-gray-300 text-orange-600 focus:ring-orange-500"
              />
              <label htmlFor="is_default" className="text-sm text-gray-600 dark:text-gray-300 cursor-pointer">
                Đặt làm địa chỉ mặc định
              </label>
            </div>

            <DialogFooter className="mt-6">
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => setIsModalOpen(false)}
                disabled={isSubmitting}
              >
                Hủy
              </Button>
              <Button 
                type="submit" 
                className="bg-orange-500 hover:bg-orange-600 text-white"
                disabled={isSubmitting}
              >
                {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Lưu địa chỉ
              </Button>
            </DialogFooter>
          </fetcher.Form>
        </DialogContent>
      </Dialog>
    </div>
    </>
  );
}
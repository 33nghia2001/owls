import { useState } from "react";
import { Form, useNavigate, Link } from "react-router";
import { Store, MapPin, FileText, Phone, Mail, Loader2 } from "lucide-react";
import { vendorsApi, authApi } from "~/lib/services";
import { useAuthStore } from "~/lib/stores";
import { Button, Input } from "~/components/ui";
import toast from "react-hot-toast";

export function meta() {
  return [{ title: "Đăng ký bán hàng - OWLS" }];
}

export default function SellerRegisterPage() {
  const navigate = useNavigate();
  const { checkAuth } = useAuthStore();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    const formData = new FormData(e.currentTarget);
    
    const data = {
      shop_name: formData.get("shop_name"),
      business_email: formData.get("business_email"),
      business_phone: formData.get("business_phone"),
      business_name: formData.get("business_name"),
      tax_id: formData.get("tax_id"),
      address: formData.get("address"),
      city: formData.get("city"),
      state: formData.get("state") || "Vietnam",
      postal_code: formData.get("postal_code") || "70000",
      description: formData.get("description"),
      country: "Vietnam"
    };

    try {
      await vendorsApi.register(data);
      toast.success("Gửi đơn đăng ký thành công! Vui lòng chờ duyệt.");
      await checkAuth(); // Refresh user state
      navigate("/seller"); // Quay lại dashboard để xem trạng thái chờ
    } catch (error: any) {
      const msg = error.response?.data?.error || error.response?.data?.shop_name?.[0] || "Đăng ký thất bại";
      toast.error(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50/50 py-12 dark:bg-[#050505]">
      <div className="container mx-auto px-4 max-w-2xl">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Đăng ký mở gian hàng</h1>
          <p className="mt-2 text-gray-500">Trở thành đối tác của OWLS và tiếp cận hàng triệu khách hàng</p>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <Form onSubmit={handleSubmit} className="space-y-6">
            
            {/* Shop Info */}
            <div className="space-y-4">
              <h3 className="font-semibold flex items-center gap-2 text-orange-600">
                <Store className="h-5 w-5" /> Thông tin cửa hàng
              </h3>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Tên Shop *</label>
                  <Input name="shop_name" required placeholder="VD: OWLS Official" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Tên doanh nghiệp / Hộ KD</label>
                  <Input name="business_name" placeholder="Công ty TNHH..." />
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Mô tả cửa hàng</label>
                <textarea 
                  name="description" 
                  className="w-full rounded-lg border border-gray-200 bg-transparent px-3 py-2 text-sm focus:border-orange-500 outline-none dark:border-gray-800"
                  rows={3}
                />
              </div>
            </div>

            <div className="h-px bg-gray-100 dark:bg-gray-800" />

            {/* Contact Info */}
            <div className="space-y-4">
              <h3 className="font-semibold flex items-center gap-2 text-blue-600">
                <Phone className="h-5 w-5" /> Liên hệ & Pháp lý
              </h3>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Email kinh doanh *</label>
                  <Input name="business_email" type="email" required />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Số điện thoại *</label>
                  <Input name="business_phone" required />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Mã số thuế</label>
                  <Input name="tax_id" />
                </div>
              </div>
            </div>

            <div className="h-px bg-gray-100 dark:bg-gray-800" />

            {/* Address */}
            <div className="space-y-4">
              <h3 className="font-semibold flex items-center gap-2 text-green-600">
                <MapPin className="h-5 w-5" /> Địa chỉ kho hàng
              </h3>
              <div className="space-y-2">
                <label className="text-sm font-medium">Địa chỉ chi tiết *</label>
                <Input name="address" required placeholder="Số nhà, tên đường..." />
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Tỉnh / Thành phố *</label>
                  <Input name="city" required />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Quận / Huyện</label>
                  <Input name="state" />
                </div>
              </div>
            </div>

            <div className="pt-4 flex items-center justify-between">
              <Link to="/account" className="text-sm text-gray-500 hover:underline">
                Quay lại
              </Link>
              <Button type="submit" disabled={isSubmitting} className="bg-orange-600 hover:bg-orange-700 text-white min-w-[150px]">
                {isSubmitting ? <Loader2 className="animate-spin h-4 w-4" /> : "Gửi đơn đăng ký"}
              </Button>
            </div>
          </Form>
        </div>
      </div>
    </div>
  );
}
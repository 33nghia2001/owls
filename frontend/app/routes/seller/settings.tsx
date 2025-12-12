import { useState, useRef } from "react";
import { useLoaderData, useRevalidator } from "react-router";
import { Store, Save, MapPin, Loader2, Upload, Camera, Image as ImageIcon } from "lucide-react";
import { Button, Input } from "~/components/ui";
import { vendorsApi } from "~/lib/services";
import { getImageUrl } from "~/lib/utils";
import { validateUploadFile, FILE_UPLOAD } from "~/lib/constants";
import toast from "react-hot-toast";

export function meta() {
  return [
    { title: "Cài đặt cửa hàng - Kênh người bán" },
  ];
}

interface VendorProfile {
  id: string;
  shop_name: string;
  slug: string;
  description: string;
  logo: string | null;
  banner: string | null;
  business_email: string;
  business_phone: string;
  address: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
}

// Client Loader - Fetch current vendor profile
export async function clientLoader() {
  try {
    const vendor = await vendorsApi.getCurrentVendor();
    return { vendor };
  } catch (error: any) {
    if (error.response?.status === 401) {
      window.location.href = "/login";
      return { vendor: null };
    }
    if (error.response?.status === 404) {
      // Not a vendor
      window.location.href = "/seller/register";
      return { vendor: null };
    }
    throw error;
  }
}

export function HydrateFallback() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="animate-pulse space-y-6">
        <div className="h-8 w-48 bg-gray-200 rounded" />
        <div className="h-64 bg-gray-200 rounded-xl" />
      </div>
    </div>
  );
}

export default function SellerSettingsPage() {
  const { vendor } = useLoaderData<typeof clientLoader>();
  const revalidator = useRevalidator();
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [bannerPreview, setBannerPreview] = useState<string | null>(null);
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [bannerFile, setBannerFile] = useState<File | null>(null);
  
  const logoInputRef = useRef<HTMLInputElement>(null);
  const bannerInputRef = useRef<HTMLInputElement>(null);

  const [formData, setFormData] = useState({
    shop_name: vendor?.shop_name || "",
    description: vendor?.description || "",
    business_email: vendor?.business_email || "",
    business_phone: vendor?.business_phone || "",
    address: vendor?.address || "",
    city: vendor?.city || "",
  });

  if (!vendor) return null;

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const error = validateUploadFile(file);
    if (error) {
      toast.error(error);
      return;
    }

    setLogoFile(file);
    setLogoPreview(URL.createObjectURL(file));
  };

  const handleBannerChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const error = validateUploadFile(file);
    if (error) {
      toast.error(error);
      return;
    }

    setBannerFile(file);
    setBannerPreview(URL.createObjectURL(file));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const submitData = new FormData();
      
      // Add text fields
      Object.entries(formData).forEach(([key, value]) => {
        if (value) submitData.append(key, value);
      });

      // Add files if changed
      if (logoFile) submitData.append("logo", logoFile);
      if (bannerFile) submitData.append("banner", bannerFile);

      await vendorsApi.updateVendor(submitData);
      
      toast.success("Cập nhật thông tin thành công!");
      
      // Clear file states after successful save
      setLogoFile(null);
      setBannerFile(null);
      
      // Revalidate to get fresh data
      revalidator.revalidate();
    } catch (error: any) {
      console.error("Update vendor error:", error);
      const message = error.response?.data?.detail || 
                      error.response?.data?.shop_name?.[0] || 
                      "Lỗi khi cập nhật thông tin";
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const displayLogo = logoPreview || getImageUrl(vendor.logo);
  const displayBanner = bannerPreview || getImageUrl(vendor.banner);

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
          <Store className="h-6 w-6 text-orange-500" />
          Cài đặt cửa hàng
        </h1>
        <p className="text-sm text-gray-500 mt-1">Quản lý thông tin hiển thị của shop bạn</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Banner Section */}
        <div className="rounded-xl border border-gray-200 bg-white overflow-hidden shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <div className="relative h-48 bg-gradient-to-r from-orange-400 to-orange-600">
            {(displayBanner && displayBanner !== "/placeholder.jpg") && (
              <img 
                src={displayBanner} 
                alt="Shop Banner" 
                className="w-full h-full object-cover"
              />
            )}
            <button
              type="button"
              onClick={() => bannerInputRef.current?.click()}
              className="absolute bottom-4 right-4 flex items-center gap-2 rounded-lg bg-black/50 px-3 py-2 text-sm text-white hover:bg-black/70 transition"
            >
              <ImageIcon className="h-4 w-4" />
              Đổi ảnh bìa
            </button>
            <input
              ref={bannerInputRef}
              type="file"
              accept={FILE_UPLOAD.ALLOWED_IMAGE_EXTENSIONS.join(",")}
              onChange={handleBannerChange}
              className="hidden"
            />
          </div>

          {/* Logo + Basic Info */}
          <div className="p-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6 -mt-16 sm:-mt-12">
              {/* Logo */}
              <div className="relative">
                <div className="h-24 w-24 rounded-xl border-4 border-white bg-gray-100 shadow-lg overflow-hidden dark:border-gray-900">
                  {displayLogo && displayLogo !== "/placeholder.jpg" ? (
                    <img src={displayLogo} alt="Shop Logo" className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                      <Store className="h-8 w-8" />
                    </div>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => logoInputRef.current?.click()}
                  className="absolute -bottom-1 -right-1 p-1.5 rounded-full bg-orange-500 text-white hover:bg-orange-600 transition shadow-md"
                >
                  <Camera className="h-3.5 w-3.5" />
                </button>
                <input
                  ref={logoInputRef}
                  type="file"
                  accept={FILE_UPLOAD.ALLOWED_IMAGE_EXTENSIONS.join(",")}
                  onChange={handleLogoChange}
                  className="hidden"
                />
              </div>

              <div className="flex-1 pt-4 sm:pt-8">
                <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{vendor.shop_name}</p>
                <p className="text-sm text-gray-500">@{vendor.slug}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Basic Info Form */}
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <h2 className="text-lg font-semibold mb-6 border-b border-gray-100 pb-4 dark:border-gray-800">
            Thông tin cơ bản
          </h2>
          
          <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium">Tên cửa hàng</label>
                <Input 
                  name="shop_name" 
                  value={formData.shop_name} 
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Số điện thoại liên hệ</label>
                <Input 
                  name="business_phone" 
                  value={formData.business_phone} 
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Email kinh doanh</label>
              <Input 
                name="business_email" 
                type="email"
                value={formData.business_email} 
                onChange={handleInputChange}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Giới thiệu cửa hàng</label>
              <textarea 
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                className="w-full rounded-lg border border-gray-200 bg-transparent px-3 py-2 text-sm focus:border-orange-500 focus:outline-none dark:border-gray-800 min-h-[100px]"
                placeholder="Mô tả ngắn về cửa hàng của bạn..."
              />
            </div>
          </div>
        </div>

        {/* Address Section */}
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <h2 className="text-lg font-semibold mb-6 border-b border-gray-100 pb-4 dark:border-gray-800 flex items-center gap-2">
            <MapPin className="h-5 w-5 text-orange-500" />
            Địa chỉ kho hàng
          </h2>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Địa chỉ chi tiết</label>
              <Input 
                name="address" 
                value={formData.address} 
                onChange={handleInputChange}
                placeholder="Số nhà, tên đường..."
              />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium">Tỉnh / Thành phố</label>
                <Input 
                  name="city" 
                  value={formData.city} 
                  onChange={handleInputChange}
                  placeholder="TP. Hồ Chí Minh"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end">
          <Button 
            type="submit"
            className="bg-orange-500 hover:bg-orange-600 text-white min-w-[150px]"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Save className="mr-2 h-4 w-4" />
            )}
            {isSubmitting ? "Đang lưu..." : "Lưu thay đổi"}
          </Button>
        </div>
      </form>
    </div>
  );
}
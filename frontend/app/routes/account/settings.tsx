import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { motion } from "framer-motion";
import {
  User, Camera, Save, ArrowLeft, Upload, X,
  Shield, AlertTriangle
} from "lucide-react";
import { useAuthStore } from "~/lib/stores";
import { Button, Input, Avatar, Card } from "~/components/ui";
import { cn } from "~/lib/utils";
import toast from "react-hot-toast";

export function meta() {
  return [
    { title: "Cài đặt tài khoản - OWLS Marketplace" },
    { name: "description", content: "Chỉnh sửa thông tin cá nhân" },
  ];
}

export default function SettingsPage() {
  const navigate = useNavigate();
  const { user, checkAuth, isLoading } = useAuthStore();
  
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    phone: "",
    email: "",
  });
  const [isSaving, setIsSaving] = useState(false);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || "",
        last_name: user.last_name || "",
        phone: user.phone || "",
        email: user.email || "",
      });
      setAvatarPreview(user.avatar);
    }
  }, [user]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        toast.error("Kích thước ảnh không được vượt quá 5MB");
        return;
      }
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      // TODO: Implement API call to update user profile
      await new Promise((resolve) => setTimeout(resolve, 1500));
      toast.success("Cập nhật thông tin thành công!");
      navigate("/account/profile");
    } catch (error) {
      toast.error("Có lỗi xảy ra. Vui lòng thử lại.");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-orange-500 border-t-transparent" />
      </div>
    );
  }

  if (!user) {
    navigate("/auth/login");
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50/50 dark:bg-[#0a0a0a] pb-20 font-sans text-gray-900 dark:text-gray-100 transition-colors duration-300">
      
      {/* 1. Header Background (Matching ProfilePage) */}
      <div className="relative h-[200px] w-full overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-slate-900 via-purple-900 to-slate-900 dark:from-black dark:to-gray-900">
             <div className="absolute inset-0 opacity-20" style={{ backgroundImage: "radial-gradient(#fff 1px, transparent 1px)", backgroundSize: "20px 20px" }}></div>
        </div>
        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-gray-50/90 dark:to-[#0a0a0a]" />
      </div>

      <div className="container mx-auto max-w-4xl px-4 relative -mt-32">
        {/* Navigation Back */}
        <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="mb-6"
        >
          <Button
            variant="ghost"
            onClick={() => navigate("/account/profile")}
            className="group gap-2 text-white hover:text-white hover:bg-white/10"
          >
            <ArrowLeft className="h-4 w-4 transition-transform group-hover:-translate-x-1" />
            Quay lại hồ sơ
          </Button>
        </motion.div>

        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
        >
            <div className="flex flex-col gap-8">
                
                {/* 2. Main Edit Form */}
                <div className="grid gap-8">
                    <Card className="p-0 overflow-hidden border-t-4 border-t-orange-500">
                         <div className="p-6 md:p-8">
                            <div className="flex items-center justify-between mb-8">
                                <div>
                                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Cài đặt chung</h1>
                                    <p className="text-gray-500 dark:text-gray-400 mt-1">Quản lý thông tin hiển thị của bạn trên OWLS</p>
                                </div>
                                <div className="hidden md:block p-3 bg-orange-50 dark:bg-orange-900/20 rounded-xl">
                                    <User className="w-6 h-6 text-orange-600" />
                                </div>
                            </div>

                            <form onSubmit={handleSubmit} className="space-y-8">
                                {/* Avatar Upload Section */}
                                <div className="flex flex-col md:flex-row items-center gap-8 pb-8 border-b border-gray-100 dark:border-gray-800">
                                    <div className="relative group">
                                        <div className="h-32 w-32">
                                          <Avatar
                                              src={avatarPreview || undefined}
                                              fallback={(user.first_name?.[0] || user.email[0]).toUpperCase()}
                                              className="h-full w-full"
                                          />
                                        </div>
                                        <div className="absolute inset-0 bg-black/40 rounded-full opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center cursor-pointer" onClick={() => document.getElementById("avatar")?.click()}>
                                            <Camera className="text-white w-8 h-8" />
                                        </div>
                                        {avatarPreview && avatarPreview !== user.avatar && (
                                            <button
                                                type="button"
                                                onClick={() => setAvatarPreview(user.avatar)}
                                                className="absolute top-0 right-0 p-1.5 bg-red-500 text-white rounded-full shadow-lg hover:bg-red-600 transition-colors z-10"
                                            >
                                                <X className="w-4 h-4" />
                                            </button>
                                        )}
                                    </div>

                                    <div className="flex-1 text-center md:text-left space-y-4">
                                        <div>
                                            <h3 className="font-semibold text-lg">Ảnh hồ sơ</h3>
                                            <p className="text-sm text-gray-500 dark:text-gray-400">Cho phép định dạng JPG, GIF hoặc PNG. Tối đa 5MB.</p>
                                        </div>
                                        <div className="flex items-center justify-center md:justify-start gap-3">
                                            <input
                                                type="file"
                                                id="avatar"
                                                accept="image/*"
                                                onChange={handleAvatarChange}
                                                className="hidden"
                                            />
                                            <Button
                                                type="button"
                                                variant="secondary"
                                                onClick={() => document.getElementById("avatar")?.click()}
                                                className="gap-2"
                                            >
                                                <Upload className="h-4 w-4" />
                                                Tải ảnh lên
                                            </Button>
                                        </div>
                                    </div>
                                </div>

                                {/* Personal Info Fields */}
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <Input
                                        label="Họ & Tên đệm"
                                        name="last_name"
                                        value={formData.last_name}
                                        onChange={handleInputChange}
                                        placeholder="Nguyễn"
                                        required
                                    />
                                    <Input
                                        label="Tên"
                                        name="first_name"
                                        value={formData.first_name}
                                        onChange={handleInputChange}
                                        placeholder="Văn A"
                                        required
                                    />
                                    <div className="md:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <Input
                                            label="Email đăng nhập"
                                            name="email"
                                            type="email"
                                            value={formData.email}
                                            disabled
                                            helperText="Để thay đổi email, vui lòng liên hệ bộ phận hỗ trợ."
                                            className="bg-gray-50 dark:bg-gray-900/50"
                                        />
                                        <Input
                                            label="Số điện thoại"
                                            name="phone"
                                            type="tel"
                                            value={formData.phone}
                                            onChange={handleInputChange}
                                            placeholder="+84..."
                                        />
                                    </div>
                                </div>

                                {/* Form Actions */}
                                <div className="flex items-center justify-between pt-6 border-t border-gray-100 dark:border-gray-800">
                                    <div className="text-sm text-gray-500 italic">
                                        Lần cập nhật cuối: 2 ngày trước
                                    </div>
                                    <div className="flex gap-3">
                                        <Button
                                            type="button"
                                            variant="ghost"
                                            onClick={() => navigate("/account/profile")}
                                            disabled={isSaving}
                                        >
                                            Hủy bỏ
                                        </Button>
                                        <Button
                                            type="submit"
                                            variant="primary"
                                            disabled={isSaving}
                                            className="min-w-[140px]"
                                        >
                                            {isSaving ? "Đang lưu..." : (
                                                <span className="flex items-center gap-2">
                                                    <Save className="w-4 h-4" />
                                                    Lưu thay đổi
                                                </span>
                                            )}
                                        </Button>
                                    </div>
                                </div>
                            </form>
                         </div>
                    </Card>

                    {/* 3. Danger Zone */}
                    <Card className="border-red-100 dark:border-red-900/30 overflow-hidden">
                        <div className="bg-red-50/50 dark:bg-red-900/10 p-4 px-6 border-b border-red-100 dark:border-red-900/30 flex items-center gap-3">
                            <AlertTriangle className="text-red-600 h-5 w-5" />
                            <h3 className="font-semibold text-red-900 dark:text-red-400">Vùng nguy hiểm</h3>
                        </div>
                        <div className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-6">
                            <div>
                                <h4 className="font-medium text-gray-900 dark:text-gray-100">Đổi mật khẩu</h4>
                                <p className="text-sm text-gray-500 mt-1">Nên sử dụng mật khẩu mạnh để bảo vệ tài khoản của bạn.</p>
                            </div>
                            <Button
                                variant="outline"
                                className="border-red-200 text-red-600 hover:bg-red-50 hover:border-red-300 dark:border-red-900 dark:hover:bg-red-900/20 whitespace-nowrap"
                                onClick={() => navigate("/account/change-password")}
                            >
                                <Shield className="w-4 h-4 mr-2" />
                                Cập nhật mật khẩu
                            </Button>
                        </div>
                    </Card>
                </div>

            </div>
        </motion.div>
      </div>
    </div>
  );
}
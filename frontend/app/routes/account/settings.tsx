import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { motion } from "framer-motion";
import {
  User,
  Mail,
  Phone,
  Camera,
  Save,
  ArrowLeft,
  Upload,
  X,
  Shield,
  AlertTriangle,
} from "lucide-react";
import { useAuthStore } from "~/lib/stores";
import { authApi } from "~/lib/services";
import { Button, Input, Card } from "~/components/ui";
import { cn, getImageUrl } from "~/lib/utils";
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
      // Ensure we use getImageUrl for the initial avatar if it exists
      setAvatarPreview(user.avatar ? getImageUrl(user.avatar) : null);
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
      // Call API to update user profile
      await authApi.updateProfile({
        first_name: formData.first_name,
        last_name: formData.last_name,
        phone: formData.phone,
        // Note: Avatar upload should be handled separately with FormData if needed
      });
      
      // Refresh auth state to get updated user data
      await checkAuth();
      
      toast.success("Cập nhật thông tin thành công!");
      navigate("/account/profile");
    } catch (error: any) {
      const message = error.response?.data?.detail || "Có lỗi xảy ra. Vui lòng thử lại.";
      toast.error(message);
    } finally {
      setIsSaving(false);
    }
  };

  // Helper to get initials
  const getInitials = () => {
    if (formData.first_name && formData.last_name) {
      return `${formData.first_name[0]}${formData.last_name[0]}`.toUpperCase();
    }
    return (formData.email[0] || "U").toUpperCase();
  };

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#050505]">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-orange-500 border-t-transparent shadow-lg shadow-orange-500/20" />
      </div>
    );
  }

  if (!user) {
    navigate("/login");
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50/50 dark:bg-[#050505] pb-20 font-sans text-gray-900 dark:text-gray-100 transition-colors duration-300">
      
      {/* 1. Immersive Header Background (Matching ProfilePage) */}
      <div className="relative h-[280px] w-full overflow-hidden">
        <div className="absolute inset-0 bg-black">
            <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(124,58,237,0.15),rgba(255,255,255,0))]" />
            <div className="absolute top-[20%] right-[10%] w-[40vw] h-[40vw] rounded-full bg-purple-600/10 blur-[120px] mix-blend-screen" />
            <div className="absolute bottom-[10%] left-[10%] w-[40vw] h-[40vw] rounded-full bg-blue-600/10 blur-[120px] mix-blend-screen" />
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808008_1px,transparent_1px),linear-gradient(to_bottom,#80808008_1px,transparent_1px)] bg-[size:24px_24px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>
        </div>
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#050505]/40 to-[#050505]" />
      </div>

      <div className="container mx-auto max-w-4xl px-4 relative -mt-40">
        {/* Navigation Back */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="mb-8"
        >
          <Button
            variant="ghost"
            onClick={() => navigate("/account/profile")}
            className="group gap-2 text-white/80 hover:text-white hover:bg-white/10"
          >
            <ArrowLeft className="h-4 w-4 transition-transform group-hover:-translate-x-1" />
            Quay lại hồ sơ
          </Button>
          <h1 className="mt-4 text-3xl font-bold text-white">Cài đặt tài khoản</h1>
          <p className="mt-2 text-gray-400">Quản lý thông tin cá nhân và bảo mật tài khoản</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="space-y-8"
        >
          {/* Main Profile Form */}
          <Card className="overflow-hidden border border-white/10 bg-white/80 dark:bg-[#111]/80 backdrop-blur-xl shadow-xl dark:shadow-2xl p-0">
            <div className="p-6 md:p-8">
              <div className="flex items-center justify-between mb-8 border-b border-gray-100 dark:border-white/5 pb-6">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-orange-500/10 text-orange-500">
                    <User className="h-5 w-5" />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-gray-900 dark:text-white">Thông tin cơ bản</h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Cập nhật ảnh đại diện và thông tin cá nhân</p>
                  </div>
                </div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-8">
                {/* Avatar Section */}
                <div className="flex flex-col md:flex-row items-center gap-8">
                  <div className="relative group">
                    <div className="h-32 w-32 rounded-full p-1 bg-gradient-to-br from-orange-500 via-red-500 to-purple-600 shadow-xl">
                      <div className="h-full w-full overflow-hidden rounded-full border-[4px] border-white dark:border-[#111] bg-gray-100 dark:bg-[#1a1a1a] relative">
                        {avatarPreview ? (
                          <img
                            src={avatarPreview}
                            alt="Avatar Preview"
                            className="h-full w-full object-cover"
                          />
                        ) : null}
                        <div className={`absolute inset-0 flex items-center justify-center bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-800 dark:to-gray-900 text-3xl font-bold text-gray-500 dark:text-white ${avatarPreview ? '-z-10' : 'z-0'}`}>
                          {getInitials()}
                        </div>
                        
                        {/* Hover Overlay */}
                        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center cursor-pointer" onClick={() => document.getElementById("avatar")?.click()}>
                           <Camera className="h-8 w-8 text-white" />
                        </div>
                      </div>
                    </div>
                    {avatarPreview && (
                      <button
                        type="button"
                        onClick={() => {
                          setAvatarPreview(null);
                          // Reset file input
                          const fileInput = document.getElementById("avatar") as HTMLInputElement;
                          if (fileInput) fileInput.value = "";
                        }}
                        className="absolute top-0 right-0 rounded-full bg-red-500 p-1.5 text-white shadow-lg transition hover:bg-red-600 hover:scale-110"
                        title="Xóa ảnh"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    )}
                  </div>
                  
                  <div className="flex-1 text-center md:text-left space-y-4">
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white">Ảnh đại diện</h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        Hỗ trợ định dạng JPG, PNG hoặc GIF. Kích thước tối đa 5MB.
                      </p>
                    </div>
                    
                    <div className="flex flex-col sm:flex-row items-center gap-3 justify-center md:justify-start">
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
                      <Button
                         type="button"
                         variant="ghost"
                         onClick={() => setAvatarPreview(null)}
                         className="text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/10"
                         disabled={!avatarPreview}
                      >
                        Xóa ảnh
                      </Button>
                    </div>
                  </div>
                </div>

                <div className="h-px bg-gray-100 dark:bg-white/5" />

                {/* Personal Info Inputs */}
                <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                  <Input
                    label="Họ"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleInputChange}
                    placeholder="Nguyễn"
                    className="bg-gray-50 dark:bg-black/20 border-gray-200 dark:border-white/10 focus:border-orange-500 dark:focus:border-orange-500"
                    required
                  />
                  <Input
                    label="Tên"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleInputChange}
                    placeholder="Văn A"
                    className="bg-gray-50 dark:bg-black/20 border-gray-200 dark:border-white/10 focus:border-orange-500 dark:focus:border-orange-500"
                    required
                  />
                  
                  <div className="md:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
                     <div className="space-y-1.5">
                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Email</label>
                        <div className="relative">
                           <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-gray-500">
                              <Mail className="h-4 w-4" />
                           </div>
                           <input
                              disabled
                              value={formData.email}
                              className="flex h-10 w-full rounded-lg border border-gray-200 bg-gray-100 px-3 pl-9 py-2 text-sm text-gray-500 cursor-not-allowed dark:border-white/5 dark:bg-white/5 dark:text-gray-400"
                           />
                           <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                              <Shield className="h-4 w-4 text-green-500" />
                           </div>
                        </div>
                        <p className="text-xs text-gray-500">Email đăng nhập không thể thay đổi</p>
                     </div>

                     <div className="space-y-1.5">
                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Số điện thoại</label>
                        <div className="relative">
                           <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-gray-500">
                              <Phone className="h-4 w-4" />
                           </div>
                           <input
                              name="phone"
                              value={formData.phone}
                              onChange={handleInputChange}
                              placeholder="+84..."
                              className="flex h-10 w-full rounded-lg border border-gray-200 bg-gray-50 px-3 pl-9 py-2 text-sm focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-500/20 dark:border-white/10 dark:bg-black/20 dark:text-white dark:focus:border-orange-500"
                           />
                        </div>
                     </div>
                  </div>
                </div>

                <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-3 pt-4">
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => navigate("/account/profile")}
                    disabled={isSaving}
                    className="w-full sm:w-auto text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  >
                    Hủy bỏ
                  </Button>
                  <Button
                    type="submit"
                    variant="primary"
                    disabled={isSaving}
                    className="w-full sm:w-auto gap-2 bg-orange-500 hover:bg-orange-600 text-white shadow-lg shadow-orange-500/20"
                  >
                    {isSaving ? (
                      <>
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                        Đang lưu...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4" />
                        Lưu thay đổi
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </div>
          </Card>

          {/* Danger Zone */}
          <Card className="overflow-hidden border border-red-200 bg-red-50/30 dark:border-red-900/30 dark:bg-red-900/10">
             <div className="border-b border-red-200/60 dark:border-red-900/30 bg-red-100/50 dark:bg-red-900/20 p-4 px-6 flex items-center gap-3">
                <AlertTriangle className="h-5 w-5 text-red-600 dark:text-red-500" />
                <h3 className="font-bold text-red-900 dark:text-red-400">Vùng nguy hiểm</h3>
             </div>
             <div className="p-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                   <div>
                      <h4 className="font-medium text-gray-900 dark:text-white">Đổi mật khẩu</h4>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        Nên sử dụng mật khẩu mạnh để bảo vệ tài khoản của bạn.
                      </p>
                   </div>
                   <Button
                      variant="outline"
                      className="border-red-200 text-red-600 hover:bg-red-50 hover:border-red-300 dark:border-red-900/50 dark:text-red-400 dark:hover:bg-red-900/20 whitespace-nowrap"
                      onClick={() => navigate("/account/change-password")}
                   >
                      <Shield className="mr-2 h-4 w-4" />
                      Cập nhật mật khẩu
                   </Button>
                </div>
             </div>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
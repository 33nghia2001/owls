import { Form, useNavigate } from "react-router";
import { useState } from "react";
import { ArrowLeft, Upload, Loader2, Package, AlertCircle, Save, ImageIcon } from "lucide-react";
import { Link } from "react-router";
import { sellerProductsApi, inventoryApi, productsApi } from "~/lib/services";
import { Button, Input } from "~/components/ui";
import { cn } from "~/lib/utils";
import toast from "react-hot-toast";

export function meta() {
  return [
    { title: "Thêm sản phẩm mới - Kênh người bán" },
  ];
}

interface Category {
  id: string;
  name: string;
  slug: string;
  full_path?: string;
}

export default function NewProductPage() {
  const navigate = useNavigate();
  const [images, setImages] = useState<File[]>([]);
  const [imagePreviews, setImagePreviews] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [categories, setCategories] = useState<Category[]>([]);
  
  // Form State
  const [formData, setFormData] = useState({
    name: "",
    short_description: "",
    description: "",
    price: "",
    compare_price: "",
    sku: "",
    category: "",
    quantity: "0",
    low_stock_threshold: "10",
    warehouse_location: "",
  });

  // Load categories
  useState(() => {
    const loadCategories = async () => {
      try {
        const data = await productsApi.getCategoryTree();
        setCategories(data.results || data || []);
      } catch (error) {
        console.error("Failed to load categories:", error);
      }
    };
    loadCategories();
  });

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      const newFiles = Array.from(files);
      // Validate file size/type if needed
      const newPreviews = newFiles.map((file) => URL.createObjectURL(file));
      setImages((prev) => [...prev, ...newFiles]);
      setImagePreviews((prev) => [...prev, ...newPreviews]);
    }
  };

  const removeImage = (index: number) => {
    URL.revokeObjectURL(imagePreviews[index]);
    setImages((prev) => prev.filter((_, i) => i !== index));
    setImagePreviews((prev) => prev.filter((_, i) => i !== index));
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Step 1: Create product
      const productFormData = new FormData();
      productFormData.append("name", formData.name);
      productFormData.append("short_description", formData.short_description);
      productFormData.append("description", formData.description);
      productFormData.append("price", formData.price);
      if (formData.compare_price) productFormData.append("compare_price", formData.compare_price);
      if (formData.sku) productFormData.append("sku", formData.sku);
      if (formData.category) productFormData.append("category", formData.category);
      
      // Step 2: Upload images
      images.forEach((img) => productFormData.append("uploaded_images", img));

      const product = await sellerProductsApi.createProduct(productFormData);
      
      // Step 3: Create inventory (Optional but recommended)
      const quantity = parseInt(formData.quantity) || 0;
      if (quantity >= 0) {
        try {
          await inventoryApi.createInventory({
            product: product.id,
            quantity: quantity,
            low_stock_threshold: parseInt(formData.low_stock_threshold) || 10,
            warehouse_location: formData.warehouse_location || undefined,
          });
        } catch (invError) {
          console.error("Inventory error", invError);
          toast.error("Sản phẩm đã tạo nhưng lỗi cập nhật kho");
        }
      }

      toast.success("Tạo sản phẩm thành công!");
      navigate("/seller/products");
    } catch (error: any) {
      const message = error.response?.data?.detail || "Lỗi khi tạo sản phẩm";
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50/50 dark:bg-[#050505] pb-20">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        
        {/* Navigation */}
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link 
              to="/seller/products" 
              className="flex h-10 w-10 items-center justify-center rounded-xl border border-gray-200 bg-white transition hover:bg-gray-50 dark:border-gray-800 dark:bg-gray-900"
            >
              <ArrowLeft className="h-5 w-5 text-gray-500" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Thêm sản phẩm mới</h1>
              <p className="text-sm text-gray-500">Điền thông tin chi tiết về sản phẩm của bạn</p>
            </div>
          </div>
          <div className="flex gap-3">
            <Button variant="ghost" onClick={() => navigate("/seller/products")}>Hủy bỏ</Button>
            <Button onClick={handleSubmit} disabled={isSubmitting || !formData.name} className="bg-orange-500 hover:bg-orange-600 text-white">
              {isSubmitting ? <Loader2 className="animate-spin h-4 w-4 mr-2" /> : <Save className="h-4 w-4 mr-2" />}
              Lưu sản phẩm
            </Button>
          </div>
        </div>

        <form className="grid gap-8 lg:grid-cols-3">
          {/* Left Column: Product Info */}
          <div className="lg:col-span-2 space-y-8">
            {/* General Info */}
            <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
              <h2 className="mb-4 font-semibold text-gray-900 dark:text-gray-100">Thông tin chung</h2>
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Tên sản phẩm <span className="text-red-500">*</span></label>
                  <Input 
                    name="name" 
                    value={formData.name} 
                    onChange={handleInputChange} 
                    placeholder="VD: Áo thun Cotton Premium" 
                    required 
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Mô tả ngắn</label>
                  <textarea 
                    name="short_description" 
                    value={formData.short_description}
                    onChange={handleInputChange}
                    className="w-full rounded-lg border border-gray-200 bg-transparent px-3 py-2 text-sm focus:border-orange-500 focus:outline-none dark:border-gray-800 min-h-[80px]"
                    placeholder="Tóm tắt đặc điểm nổi bật..."
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Mô tả chi tiết</label>
                  <textarea 
                    name="description" 
                    value={formData.description}
                    onChange={handleInputChange}
                    className="w-full rounded-lg border border-gray-200 bg-transparent px-3 py-2 text-sm focus:border-orange-500 focus:outline-none dark:border-gray-800 min-h-[150px]"
                    placeholder="Chi tiết thông số, hướng dẫn sử dụng..."
                  />
                </div>
              </div>
            </div>

            {/* Media */}
            <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
              <h2 className="mb-4 font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                <ImageIcon className="h-4 w-4" /> Hình ảnh
              </h2>
              <div className="grid grid-cols-3 gap-4 sm:grid-cols-4 md:grid-cols-5">
                {imagePreviews.map((url, index) => (
                  <div key={index} className="group relative aspect-square overflow-hidden rounded-lg border border-gray-200 bg-gray-50">
                    <img src={url} alt="Preview" className="h-full w-full object-cover" />
                    <button
                      type="button"
                      onClick={() => removeImage(index)}
                      className="absolute right-1 top-1 rounded-full bg-red-500 p-1 text-white opacity-0 transition group-hover:opacity-100"
                    >
                      ×
                    </button>
                  </div>
                ))}
                <label className="flex aspect-square cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 text-gray-400 transition hover:border-orange-500 hover:text-orange-500 hover:bg-orange-50/50 dark:border-gray-700 dark:hover:bg-gray-800">
                  <Upload className="h-6 w-6 mb-1" />
                  <span className="text-xs">Thêm ảnh</span>
                  <input type="file" multiple accept="image/*" onChange={handleImageUpload} className="hidden" />
                </label>
              </div>
            </div>

            {/* Inventory */}
            <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
              <div className="flex items-center gap-2 mb-4">
                <Package className="h-5 w-5 text-orange-500" />
                <h2 className="font-semibold text-gray-900 dark:text-gray-100">Kho hàng & Vận chuyển</h2>
              </div>
              <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-2">
                  <label className="text-sm font-medium">SKU (Mã sản phẩm)</label>
                  <Input name="sku" value={formData.sku} onChange={handleInputChange} placeholder="SP-001" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Số lượng tồn kho</label>
                  <Input type="number" name="quantity" value={formData.quantity} onChange={handleInputChange} min="0" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Ngưỡng cảnh báo sắp hết</label>
                  <Input type="number" name="low_stock_threshold" value={formData.low_stock_threshold} onChange={handleInputChange} />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Vị trí kho</label>
                  <Input name="warehouse_location" value={formData.warehouse_location} onChange={handleInputChange} placeholder="Kệ A, Dãy 2" />
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Pricing & Organization */}
          <div className="space-y-8">
            <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
              <h2 className="mb-4 font-semibold text-gray-900 dark:text-gray-100">Giá bán</h2>
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Giá bán (₫) <span className="text-red-500">*</span></label>
                  <Input 
                    type="number" 
                    name="price" 
                    value={formData.price} 
                    onChange={handleInputChange} 
                    placeholder="0" 
                    required 
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Giá gốc (₫)</label>
                  <Input 
                    type="number" 
                    name="compare_price" 
                    value={formData.compare_price} 
                    onChange={handleInputChange} 
                    placeholder="0" 
                  />
                  <p className="text-xs text-gray-500">Dùng để hiển thị giảm giá (gạch ngang giá gốc)</p>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
              <h2 className="mb-4 font-semibold text-gray-900 dark:text-gray-100">Phân loại</h2>
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Danh mục</label>
                  <select
                    name="category"
                    value={formData.category}
                    onChange={handleInputChange}
                    className="w-full h-10 rounded-lg border border-gray-200 bg-transparent px-3 text-sm focus:border-orange-500 focus:outline-none dark:border-gray-800 dark:bg-gray-900"
                  >
                    <option value="">-- Chọn danh mục --</option>
                    {categories.map((cat) => (
                      <option key={cat.id} value={cat.id}>
                        {cat.full_path || cat.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
import { Form, useNavigate } from "react-router";
import { useState } from "react";
import { ArrowLeft, Upload, Loader2, Package, AlertCircle } from "lucide-react";
import { Link } from "react-router";
import { sellerProductsApi, productsApi } from "~/lib/services";
import { Button } from "~/components/ui";
import toast from "react-hot-toast";

export function meta() {
  return [
    { title: "Thêm sản phẩm mới - Seller Dashboard" },
    { name: "description", content: "Tạo sản phẩm mới" },
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
  const [loadingCategories, setLoadingCategories] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    short_description: "",
    description: "",
    price: "",
    compare_price: "",
    sku: "",
    category: "",
    // Inventory
    quantity: "0",
    low_stock_threshold: "10",
    warehouse_location: "",
  });

  // Load categories on mount
  useState(() => {
    const loadCategories = async () => {
      setLoadingCategories(true);
      try {
        const data = await productsApi.getCategoryTree();
        setCategories(data.results || data || []);
      } catch (error) {
        console.error("Failed to load categories:", error);
      } finally {
        setLoadingCategories(false);
      }
    };
    loadCategories();
  });

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      const newFiles = Array.from(files);
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
      // Create product with inventory data in single atomic request
      // Backend will automatically create inventory record
      const productFormData = new FormData();
      productFormData.append("name", formData.name);
      productFormData.append("short_description", formData.short_description);
      productFormData.append("description", formData.description);
      productFormData.append("price", formData.price);
      if (formData.compare_price) {
        productFormData.append("compare_price", formData.compare_price);
      }
      if (formData.sku) {
        productFormData.append("sku", formData.sku);
      }
      if (formData.category) {
        productFormData.append("category", formData.category);
      }
      
      // Add inventory data - backend handles this atomically
      productFormData.append("initial_stock", formData.quantity || "0");
      productFormData.append("low_stock_threshold", formData.low_stock_threshold || "10");
      if (formData.warehouse_location) {
        productFormData.append("warehouse_location", formData.warehouse_location);
      }
      
      // Add images
      images.forEach((img) => {
        productFormData.append("uploaded_images", img);
      });

      await sellerProductsApi.createProduct(productFormData);

      toast.success("Tạo sản phẩm thành công!");
      navigate("/seller/products");
    } catch (error: any) {
      console.error("Failed to create product:", error);
      const message = error.response?.data?.detail || 
                      error.response?.data?.name?.[0] ||
                      "Không thể tạo sản phẩm. Vui lòng thử lại.";
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Link to="/seller/products" className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-orange-500">
          <ArrowLeft className="h-4 w-4" />
          Quay lại
        </Link>
        <h1 className="mt-2 text-3xl font-bold text-gray-900 dark:text-gray-100">Thêm sản phẩm mới</h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">Thông tin cơ bản</h2>
          
          <div className="space-y-4">
            <label className="block text-sm text-gray-700 dark:text-gray-300">
              Tên sản phẩm *
              <input
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>

            <label className="block text-sm text-gray-700 dark:text-gray-300">
              Danh mục
              <select
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              >
                <option value="">-- Chọn danh mục --</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.full_path || cat.name}
                  </option>
                ))}
              </select>
            </label>

            <label className="block text-sm text-gray-700 dark:text-gray-300">
              Mô tả ngắn
              <textarea
                name="short_description"
                value={formData.short_description}
                onChange={handleInputChange}
                rows={3}
                className="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>

            <label className="block text-sm text-gray-700 dark:text-gray-300">
              Mô tả chi tiết
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows={6}
                className="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>

            <div className="grid gap-4 md:grid-cols-2">
              <label className="block text-sm text-gray-700 dark:text-gray-300">
                Giá (₫) *
                <input
                  name="price"
                  type="number"
                  value={formData.price}
                  onChange={handleInputChange}
                  required
                  min="0"
                  className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
                />
              </label>

              <label className="block text-sm text-gray-700 dark:text-gray-300">
                Giá so sánh (₫)
                <input
                  name="compare_price"
                  type="number"
                  value={formData.compare_price}
                  onChange={handleInputChange}
                  min="0"
                  className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
                />
              </label>
            </div>

            <label className="block text-sm text-gray-700 dark:text-gray-300">
              SKU
              <input
                name="sku"
                value={formData.sku}
                onChange={handleInputChange}
                className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>
          </div>
        </div>

        {/* Inventory Section */}
        <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
          <div className="mb-4 flex items-center gap-2">
            <Package className="h-5 w-5 text-orange-500" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Kho hàng</h2>
          </div>

          <div className="mb-4 flex items-start gap-2 rounded-lg bg-yellow-50 p-3 text-sm text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-200">
            <AlertCircle className="h-5 w-5 flex-shrink-0" />
            <p>
              Nếu sản phẩm có biến thể (size, màu...), bạn cần thiết lập tồn kho cho từng biến thể riêng sau khi tạo sản phẩm.
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <label className="block text-sm text-gray-700 dark:text-gray-300">
              Số lượng tồn kho
              <input
                name="quantity"
                type="number"
                value={formData.quantity}
                onChange={handleInputChange}
                min="0"
                className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>

            <label className="block text-sm text-gray-700 dark:text-gray-300">
              Ngưỡng cảnh báo hết hàng
              <input
                name="low_stock_threshold"
                type="number"
                value={formData.low_stock_threshold}
                onChange={handleInputChange}
                min="0"
                className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>

            <label className="block text-sm text-gray-700 dark:text-gray-300">
              Vị trí kho
              <input
                name="warehouse_location"
                value={formData.warehouse_location}
                onChange={handleInputChange}
                placeholder="VD: A1-02"
                className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>
          </div>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">Hình ảnh</h2>
          
          <div className="grid grid-cols-3 gap-4 md:grid-cols-4 lg:grid-cols-6">
            {imagePreviews.map((url, index) => (
              <div key={index} className="group relative aspect-square overflow-hidden rounded-lg border border-gray-200">
                <img src={url} alt={`Product ${index + 1}`} className="h-full w-full object-cover" />
                <button
                  type="button"
                  onClick={() => removeImage(index)}
                  className="absolute right-1 top-1 rounded-full bg-red-500 p-1 text-white opacity-0 transition group-hover:opacity-100"
                >
                  ✕
                </button>
              </div>
            ))}
            
            <label className="flex aspect-square cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 text-gray-400 transition hover:border-orange-500 hover:text-orange-500">
              <Upload className="h-8 w-8" />
              <span className="mt-2 text-xs">Tải ảnh</span>
              <input type="file" multiple accept="image/*" onChange={handleImageUpload} className="hidden" />
            </label>
          </div>
        </div>

        <div className="flex gap-3">
          <Button
            type="submit"
            disabled={isSubmitting || !formData.name || !formData.price}
          >
            {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {isSubmitting ? "Đang tạo..." : "Tạo sản phẩm"}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate("/seller/products")}
          >
            Hủy
          </Button>
        </div>
      </form>
    </div>
  );
}

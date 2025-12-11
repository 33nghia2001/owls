import { Form, useNavigate } from "react-router";
import { useState } from "react";
import { ArrowLeft, Upload } from "lucide-react";
import { Link } from "react-router";

export function meta() {
  return [
    { title: "Thêm sản phẩm mới - Seller Dashboard" },
    { name: "description", content: "Tạo sản phẩm mới" },
  ];
}

export default function NewProductPage() {
  const navigate = useNavigate();
  const [images, setImages] = useState<string[]>([]);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      const urls = Array.from(files).map((file) => URL.createObjectURL(file));
      setImages((prev) => [...prev, ...urls]);
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

      <Form method="post" className="space-y-6">
        <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">Thông tin cơ bản</h2>
          
          <div className="space-y-4">
            <label className="block text-sm text-gray-700 dark:text-gray-300">
              Tên sản phẩm
              <input
                name="name"
                required
                className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>

            <label className="block text-sm text-gray-700 dark:text-gray-300">
              Mô tả ngắn
              <textarea
                name="short_description"
                rows={3}
                className="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>

            <label className="block text-sm text-gray-700 dark:text-gray-300">
              Mô tả chi tiết
              <textarea
                name="description"
                rows={6}
                className="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>

            <div className="grid gap-4 md:grid-cols-2">
              <label className="block text-sm text-gray-700 dark:text-gray-300">
                Giá (₫)
                <input
                  name="price"
                  type="number"
                  required
                  className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
                />
              </label>

              <label className="block text-sm text-gray-700 dark:text-gray-300">
                Giá so sánh (₫)
                <input
                  name="compare_price"
                  type="number"
                  className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
                />
              </label>
            </div>

            <label className="block text-sm text-gray-700 dark:text-gray-300">
              SKU
              <input
                name="sku"
                className="mt-1 h-11 w-full rounded-lg border border-gray-200 px-3 text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 dark:border-gray-800 dark:bg-gray-900"
              />
            </label>
          </div>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">Hình ảnh</h2>
          
          <div className="grid grid-cols-3 gap-4 md:grid-cols-4 lg:grid-cols-6">
            {images.map((url, index) => (
              <div key={index} className="aspect-square overflow-hidden rounded-lg border border-gray-200">
                <img src={url} alt={`Product ${index + 1}`} className="h-full w-full object-cover" />
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
          <button
            type="submit"
            className="rounded-lg bg-orange-500 px-6 py-3 font-medium text-white transition hover:bg-orange-600"
          >
            Tạo sản phẩm
          </button>
          <button
            type="button"
            onClick={() => navigate("/seller/products")}
            className="rounded-lg border border-gray-200 px-6 py-3 font-medium text-gray-700 transition hover:border-orange-500 hover:text-orange-500 dark:border-gray-800 dark:text-gray-200"
          >
            Hủy
          </button>
        </div>
      </Form>
    </div>
  );
}

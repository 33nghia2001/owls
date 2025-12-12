import { useState, useEffect } from "react";
import { Link, useLoaderData, useSearchParams, Form, useSubmit } from "react-router";
import { 
  Plus, 
  Search, 
  MoreHorizontal, 
  Edit, 
  Trash2, 
  Package, 
  Eye, 
  Filter 
} from "lucide-react";
import { sellerProductsApi } from "~/lib/services";
import { formatPrice, cn } from "~/lib/utils";
import { Button, Input, useConfirm } from "~/components/ui";
import type { ProductListItem } from "~/lib/types";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "~/components/ui/dropdown-menu";
import toast from "react-hot-toast";

export function meta() {
  return [
    { title: "Quản lý sản phẩm - Kênh người bán" },
  ];
}

export async function clientLoader({ request }: { request: Request }) {
  const url = new URL(request.url);
  const page = Number(url.searchParams.get("page")) || 1;
  const status = url.searchParams.get("status");
  const search = url.searchParams.get("q");

  try {
    const data = await sellerProductsApi.getMyProducts({ 
      page, 
      status: status || undefined,
    });
    return { 
      products: Array.isArray(data) ? data : (data.results || []),
      pagination: {
        count: data.count || 0,
        next: data.next,
        previous: data.previous
      }
    };
  } catch (error) {
    return { products: [], pagination: { count: 0 } };
  }
}

export default function SellerProductsPage() {
  const { products, pagination } = useLoaderData<typeof clientLoader>();
  const [searchParams] = useSearchParams();
  const submit = useSubmit();
  const { confirm, ConfirmDialog } = useConfirm();
  
  const currentStatus = searchParams.get("status") || "all";

  const handleDelete = async (slug: string) => {
    const confirmed = await confirm({
      title: "Xóa sản phẩm?",
      description: "Bạn có chắc chắn muốn xóa sản phẩm này? Hành động này không thể hoàn tác.",
      confirmText: "Xóa sản phẩm",
      variant: "danger",
    });
    if (confirmed) {
      try {
        await sellerProductsApi.deleteProduct(slug);
        toast.success("Đã xóa sản phẩm");
        // Reload page
        window.location.reload(); 
      } catch (error) {
        toast.error("Không thể xóa sản phẩm");
      }
    }
  };

  return (
    <>
    {ConfirmDialog}
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <Package className="h-6 w-6 text-orange-500" />
            Sản phẩm của tôi
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Quản lý {pagination.count} sản phẩm trong cửa hàng
          </p>
        </div>
        <Link to="/seller/products/new">
          <Button className="gap-2 bg-orange-500 hover:bg-orange-600 text-white shadow-lg shadow-orange-500/20">
            <Plus className="h-4 w-4" /> Thêm sản phẩm mới
          </Button>
        </Link>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col md:flex-row gap-4 mb-6 rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
        <div className="flex-1">
          <Form className="relative" onChange={(e) => submit(e.currentTarget)}>
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input 
              name="q" 
              placeholder="Tìm theo tên, SKU..." 
              className="pl-9 bg-gray-50 border-gray-200 dark:bg-gray-800 dark:border-gray-700"
              defaultValue={searchParams.get("q") || ""}
            />
          </Form>
        </div>
        <div className="flex gap-2 overflow-x-auto pb-2 md:pb-0">
          {[
            { value: "all", label: "Tất cả" },
            { value: "active", label: "Đang bán" },
            { value: "draft", label: "Nháp" },
            { value: "archived", label: "Đã ẩn" }
          ].map((tab) => (
            <Button
              key={tab.value}
              variant={currentStatus === tab.value ? "secondary" : "ghost"}
              className={cn(
                "whitespace-nowrap",
                currentStatus === tab.value && "bg-orange-100 text-orange-700 hover:bg-orange-200 dark:bg-orange-900/30 dark:text-orange-400"
              )}
              onClick={() => {
                const params = new URLSearchParams(searchParams);
                if (tab.value === "all") params.delete("status");
                else params.set("status", tab.value);
                submit(params);
              }}
            >
              {tab.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Product Table */}
      <div className="rounded-xl border border-gray-200 bg-white overflow-hidden shadow-sm dark:border-gray-800 dark:bg-gray-900">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-gray-500 uppercase bg-gray-50 border-b border-gray-100 dark:bg-gray-800/50 dark:border-gray-800 dark:text-gray-400">
              <tr>
                <th className="px-6 py-4 font-medium">Sản phẩm</th>
                <th className="px-6 py-4 font-medium">Giá bán</th>
                <th className="px-6 py-4 font-medium">Kho hàng</th>
                <th className="px-6 py-4 font-medium">Đã bán</th>
                <th className="px-6 py-4 font-medium">Trạng thái</th>
                <th className="px-6 py-4 font-medium text-right">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
              {products.length > 0 ? (
                (products as ProductListItem[]).map((product) => (
                  <tr key={product.id} className="group hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="h-12 w-12 rounded-lg border border-gray-100 bg-gray-50 overflow-hidden dark:border-gray-800 dark:bg-gray-800">
                          {product.primary_image ? (
                            <img src={product.primary_image.image} alt={product.name} className="h-full w-full object-cover" />
                          ) : (
                            <div className="flex h-full w-full items-center justify-center text-gray-300">
                              <Package className="h-5 w-5" />
                            </div>
                          )}
                        </div>
                        <div>
                          <p className="font-medium text-gray-900 dark:text-gray-100 line-clamp-1 max-w-[200px]">
                            {product.name}
                          </p>
                          <p className="text-xs text-gray-500">SKU: {product.sku || "---"}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 font-medium text-gray-900 dark:text-gray-100">
                      {formatPrice(product.price)}
                    </td>
                    <td className="px-6 py-4">
                      {(product.inventory_quantity ?? product.quantity ?? 0) > 0 ? (
                        <span className="text-green-600 dark:text-green-400 font-medium">
                          {product.inventory_quantity ?? product.quantity ?? 0}
                        </span>
                      ) : (
                        <span className="text-red-500 font-medium">Hết hàng</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-gray-600 dark:text-gray-400">
                      {product.sold_count || 0}
                    </td>
                    <td className="px-6 py-4">
                      <span className={cn(
                        "inline-flex items-center rounded-full px-2 py-1 text-xs font-medium",
                        product.is_active 
                          ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                          : "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400"
                      )}>
                        {product.is_active ? "Đang bán" : "Nháp/Ẩn"}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8 text-gray-500 hover:text-gray-900 dark:hover:text-gray-100">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem asChild>
                            <Link to={`/seller/products/${product.slug}/edit`} className="cursor-pointer">
                              <Edit className="mr-2 h-4 w-4" /> Chỉnh sửa
                            </Link>
                          </DropdownMenuItem>
                          <DropdownMenuItem asChild>
                            <Link to={`/products/${product.slug}`} target="_blank" className="cursor-pointer">
                              <Eye className="mr-2 h-4 w-4" /> Xem chi tiết
                            </Link>
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            className="text-red-600 focus:text-red-600 cursor-pointer"
                            onClick={() => handleDelete(product.slug)}
                          >
                            <Trash2 className="mr-2 h-4 w-4" /> Xóa
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                    <div className="flex flex-col items-center justify-center">
                      <Package className="h-10 w-10 mb-3 opacity-20" />
                      <p>Không tìm thấy sản phẩm nào.</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        {products.length > 0 && (
          <div className="flex items-center justify-between border-t border-gray-100 bg-gray-50 px-6 py-4 dark:border-gray-800 dark:bg-gray-800/50">
            <span className="text-sm text-gray-500">
              Hiển thị {products.length} trên tổng số {pagination.count}
            </span>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                size="sm" 
                disabled={!pagination.previous}
                onClick={() => submit(new URLSearchParams({ ...Object.fromEntries(searchParams), page: String((Number(searchParams.get("page")) || 1) - 1) }))}
              >
                Trước
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                disabled={!pagination.next}
                onClick={() => submit(new URLSearchParams({ ...Object.fromEntries(searchParams), page: String((Number(searchParams.get("page")) || 1) + 1) }))}
              >
                Sau
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
    </>
  );
}
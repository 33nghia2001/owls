import { Link } from "react-router";
import { RotateCcw, ArrowLeft, CheckCircle, XCircle, Clock } from "lucide-react";

export function meta() {
  return [
    { title: "Chính sách Đổi trả - OWLS" },
    { name: "description", content: "Chính sách đổi trả và hoàn tiền tại OWLS Marketplace" },
  ];
}

export default function ReturnPolicyPage() {
  return (
    <div className="min-h-screen bg-gray-50/50 py-12 dark:bg-[#050505]">
      <div className="container mx-auto max-w-4xl px-4">
        {/* Header */}
        <div className="mb-8">
          <Link to="/" className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-orange-500 mb-4">
            <ArrowLeft className="h-4 w-4" />
            Về trang chủ
          </Link>
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-100 dark:bg-purple-900/20">
              <RotateCcw className="h-6 w-6 text-purple-500" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                Chính sách Đổi trả & Hoàn tiền
              </h1>
              <p className="text-sm text-gray-500">Cập nhật lần cuối: 01/12/2024</p>
            </div>
          </div>
        </div>

        {/* Quick Info */}
        <div className="grid gap-4 md:grid-cols-3 mb-8">
          <div className="rounded-xl border border-green-200 bg-green-50 p-4 dark:border-green-800 dark:bg-green-900/20">
            <CheckCircle className="h-6 w-6 text-green-500 mb-2" />
            <h3 className="font-semibold text-green-800 dark:text-green-200">Được đổi trả</h3>
            <ul className="text-sm text-green-700 dark:text-green-300 mt-2 space-y-1">
              <li>• Hàng lỗi, hư hỏng</li>
              <li>• Giao sai sản phẩm</li>
              <li>• Không đúng mô tả</li>
            </ul>
          </div>
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-900/20">
            <XCircle className="h-6 w-6 text-red-500 mb-2" />
            <h3 className="font-semibold text-red-800 dark:text-red-200">Không đổi trả</h3>
            <ul className="text-sm text-red-700 dark:text-red-300 mt-2 space-y-1">
              <li>• Đã qua sử dụng</li>
              <li>• Hết thời hạn 7 ngày</li>
              <li>• Hàng khuyến mãi đặc biệt</li>
            </ul>
          </div>
          <div className="rounded-xl border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-900/20">
            <Clock className="h-6 w-6 text-blue-500 mb-2" />
            <h3 className="font-semibold text-blue-800 dark:text-blue-200">Thời hạn</h3>
            <ul className="text-sm text-blue-700 dark:text-blue-300 mt-2 space-y-1">
              <li>• 7 ngày kể từ khi nhận</li>
              <li>• Hoàn tiền: 3-5 ngày</li>
              <li>• Đổi hàng: 5-7 ngày</li>
            </ul>
          </div>
        </div>

        {/* Content */}
        <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <div className="prose prose-gray max-w-none dark:prose-invert">
            <h2>1. Điều kiện đổi trả</h2>
            <p>Sản phẩm được chấp nhận đổi trả khi:</p>
            <ul>
              <li>Còn trong thời hạn 7 ngày kể từ ngày nhận hàng</li>
              <li>Còn nguyên tem, nhãn, bao bì gốc</li>
              <li>Chưa qua sử dụng, chưa giặt/là (với quần áo)</li>
              <li>Có video quay lúc mở hàng (khuyến nghị)</li>
              <li>Có hóa đơn hoặc mã đơn hàng</li>
            </ul>

            <h2>2. Các trường hợp được hoàn tiền 100%</h2>
            <ul>
              <li>Sản phẩm bị lỗi do nhà sản xuất</li>
              <li>Giao sai mẫu, sai màu, sai size</li>
              <li>Sản phẩm không đúng mô tả trên website</li>
              <li>Hàng bị hư hỏng trong quá trình vận chuyển</li>
              <li>Đơn hàng bị thất lạc không giao được</li>
            </ul>

            <h2>3. Các trường hợp KHÔNG được đổi trả</h2>
            <ul>
              <li>Sản phẩm đã qua sử dụng, có dấu hiệu giặt/là</li>
              <li>Hết thời hạn 7 ngày</li>
              <li>Không còn nguyên bao bì, tem nhãn</li>
              <li>Đổi ý không muốn mua nữa (không áp dụng hoàn tiền)</li>
              <li>Hàng giảm giá trên 50% hoặc hàng thanh lý</li>
              <li>Các sản phẩm đặc biệt: nội y, mỹ phẩm đã khui seal</li>
            </ul>

            <h2>4. Quy trình đổi trả</h2>
            <ol>
              <li>
                <strong>Bước 1:</strong> Liên hệ OWLS hoặc người bán qua chat/hotline trong vòng 7 ngày
              </li>
              <li>
                <strong>Bước 2:</strong> Cung cấp mã đơn hàng, hình ảnh/video sản phẩm lỗi
              </li>
              <li>
                <strong>Bước 3:</strong> Chờ xác nhận từ người bán (trong 24-48h)
              </li>
              <li>
                <strong>Bước 4:</strong> Gửi trả sản phẩm theo hướng dẫn
              </li>
              <li>
                <strong>Bước 5:</strong> Nhận hàng đổi hoặc hoàn tiền sau khi người bán kiểm tra
              </li>
            </ol>

            <h2>5. Phương thức hoàn tiền</h2>
            <p>Tiền sẽ được hoàn lại qua:</p>
            <ul>
              <li><strong>Ví OWLS:</strong> Hoàn ngay sau khi xác nhận (có thể dùng cho đơn sau)</li>
              <li><strong>Tài khoản gốc:</strong> 3-5 ngày làm việc (VNPay, thẻ ngân hàng)</li>
              <li><strong>Chuyển khoản:</strong> 5-7 ngày làm việc (nếu thanh toán COD)</li>
            </ul>

            <h2>6. Phí đổi trả</h2>
            <table className="w-full">
              <thead>
                <tr>
                  <th>Trường hợp</th>
                  <th>Phí ship</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Lỗi từ người bán (sai, lỗi, hư)</td>
                  <td>Người bán chịu 100%</td>
                </tr>
                <tr>
                  <td>Đổi size, đổi màu (theo ý khách)</td>
                  <td>Khách hàng chịu phí ship 2 chiều</td>
                </tr>
              </tbody>
            </table>

            <h2>7. Liên hệ hỗ trợ</h2>
            <p>Cần hỗ trợ đổi trả? Liên hệ ngay:</p>
            <ul>
              <li>Email: <a href="mailto:return@owls.vn">return@owls.vn</a></li>
              <li>Hotline: 1900 1234 (8:00 - 22:00)</li>
              <li>Chat trực tiếp trên website/app</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

import { Link } from "react-router";
import { Truck, ArrowLeft, Clock, MapPin, Package, AlertCircle } from "lucide-react";

export function meta() {
  return [
    { title: "Chính sách Vận chuyển - OWLS" },
    { name: "description", content: "Thông tin về chính sách giao hàng và vận chuyển tại OWLS" },
  ];
}

export default function ShippingPolicyPage() {
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
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-green-100 dark:bg-green-900/20">
              <Truck className="h-6 w-6 text-green-500" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                Chính sách Vận chuyển
              </h1>
              <p className="text-sm text-gray-500">Cập nhật lần cuối: 01/12/2024</p>
            </div>
          </div>
        </div>

        {/* Quick Info Cards */}
        <div className="grid gap-4 md:grid-cols-3 mb-8">
          <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
            <Clock className="h-8 w-8 text-orange-500 mb-2" />
            <h3 className="font-semibold text-gray-900 dark:text-gray-100">Thời gian giao hàng</h3>
            <p className="text-sm text-gray-500">2-5 ngày làm việc (nội thành), 5-7 ngày (tỉnh)</p>
          </div>
          <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
            <MapPin className="h-8 w-8 text-blue-500 mb-2" />
            <h3 className="font-semibold text-gray-900 dark:text-gray-100">Phạm vi giao hàng</h3>
            <p className="text-sm text-gray-500">Toàn quốc 63 tỉnh thành</p>
          </div>
          <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
            <Package className="h-8 w-8 text-purple-500 mb-2" />
            <h3 className="font-semibold text-gray-900 dark:text-gray-100">Miễn phí vận chuyển</h3>
            <p className="text-sm text-gray-500">Đơn hàng từ 500.000đ</p>
          </div>
        </div>

        {/* Content */}
        <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <div className="prose prose-gray max-w-none dark:prose-invert">
            <h2>1. Phí vận chuyển</h2>
            <table className="w-full">
              <thead>
                <tr>
                  <th>Khu vực</th>
                  <th>Phí ship tiêu chuẩn</th>
                  <th>Phí ship nhanh</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Nội thành TP.HCM, Hà Nội</td>
                  <td>15.000đ</td>
                  <td>30.000đ</td>
                </tr>
                <tr>
                  <td>Ngoại thành, các tỉnh lân cận</td>
                  <td>25.000đ</td>
                  <td>45.000đ</td>
                </tr>
                <tr>
                  <td>Các tỉnh khác</td>
                  <td>30.000đ</td>
                  <td>55.000đ</td>
                </tr>
                <tr>
                  <td>Vùng sâu, vùng xa</td>
                  <td>40.000đ</td>
                  <td>Không hỗ trợ</td>
                </tr>
              </tbody>
            </table>
            <p className="text-sm text-gray-500">
              * Phí ship có thể thay đổi tùy theo trọng lượng và kích thước đơn hàng.
            </p>

            <h2>2. Thời gian giao hàng</h2>
            <ul>
              <li><strong>Nội thành:</strong> 1-2 ngày làm việc (ship nhanh), 2-3 ngày (tiêu chuẩn)</li>
              <li><strong>Tỉnh lân cận:</strong> 2-3 ngày làm việc (ship nhanh), 3-5 ngày (tiêu chuẩn)</li>
              <li><strong>Các tỉnh khác:</strong> 3-5 ngày làm việc</li>
              <li><strong>Vùng sâu, vùng xa:</strong> 5-7 ngày làm việc</li>
            </ul>
            <p>
              <strong>Lưu ý:</strong> Thời gian tính từ khi đơn hàng được người bán xác nhận và bàn giao 
              cho đơn vị vận chuyển. Không bao gồm Chủ nhật và ngày lễ.
            </p>

            <h2>3. Đơn vị vận chuyển</h2>
            <p>OWLS hợp tác với các đơn vị vận chuyển uy tín:</p>
            <ul>
              <li>Giao Hàng Nhanh (GHN)</li>
              <li>Giao Hàng Tiết Kiệm (GHTK)</li>
              <li>Viettel Post</li>
              <li>J&T Express</li>
            </ul>

            <h2>4. Theo dõi đơn hàng</h2>
            <p>
              Sau khi đơn hàng được giao cho đơn vị vận chuyển, bạn sẽ nhận được mã vận đơn qua 
              email/SMS. Có thể theo dõi trạng thái giao hàng tại:
            </p>
            <ul>
              <li>Trang "Đơn hàng của tôi" trên OWLS</li>
              <li>Website của đơn vị vận chuyển</li>
            </ul>

            <h2>5. Nhận hàng</h2>
            <p>Khi nhận hàng, vui lòng:</p>
            <ul>
              <li>Kiểm tra tình trạng kiện hàng trước khi ký nhận</li>
              <li>Quay video khi mở hàng (khuyến nghị)</li>
              <li>Liên hệ ngay nếu phát hiện hàng hư hỏng, thiếu, sai</li>
            </ul>

            <div className="rounded-lg bg-yellow-50 p-4 dark:bg-yellow-900/20">
              <div className="flex gap-3">
                <AlertCircle className="h-5 w-5 flex-shrink-0 text-yellow-600" />
                <div>
                  <p className="font-medium text-yellow-800 dark:text-yellow-200">Lưu ý quan trọng</p>
                  <p className="text-sm text-yellow-700 dark:text-yellow-300">
                    Nếu đơn hàng bị trả lại do không liên lạc được hoặc từ chối nhận, 
                    bạn có thể phải chịu phí ship hai chiều.
                  </p>
                </div>
              </div>
            </div>

            <h2>6. Liên hệ hỗ trợ</h2>
            <p>Mọi thắc mắc về vận chuyển, vui lòng liên hệ:</p>
            <ul>
              <li>Email: <a href="mailto:shipping@owls.vn">shipping@owls.vn</a></li>
              <li>Hotline: 1900 1234</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

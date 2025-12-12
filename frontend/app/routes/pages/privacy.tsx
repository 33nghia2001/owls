import { Link } from "react-router";
import { FileText, ArrowLeft } from "lucide-react";
import { Button } from "~/components/ui";

export function meta() {
  return [
    { title: "Chính sách Bảo mật - OWLS" },
    { name: "description", content: "Chính sách bảo mật thông tin người dùng tại OWLS Marketplace" },
  ];
}

export default function PrivacyPolicyPage() {
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
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-orange-100 dark:bg-orange-900/20">
              <FileText className="h-6 w-6 text-orange-500" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                Chính sách Bảo mật
              </h1>
              <p className="text-sm text-gray-500">Cập nhật lần cuối: 01/12/2024</p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <div className="prose prose-gray max-w-none dark:prose-invert">
            <h2>1. Thu thập thông tin</h2>
            <p>
              OWLS Marketplace thu thập các thông tin cá nhân khi bạn đăng ký tài khoản, đặt hàng, 
              hoặc tương tác với các dịch vụ của chúng tôi, bao gồm:
            </p>
            <ul>
              <li>Họ tên, email, số điện thoại</li>
              <li>Địa chỉ giao hàng và thanh toán</li>
              <li>Thông tin thanh toán (được xử lý an toàn qua các cổng thanh toán đối tác)</li>
              <li>Lịch sử đơn hàng và hoạt động trên website</li>
            </ul>

            <h2>2. Sử dụng thông tin</h2>
            <p>Chúng tôi sử dụng thông tin của bạn để:</p>
            <ul>
              <li>Xử lý và giao đơn hàng</li>
              <li>Liên hệ hỗ trợ khi cần thiết</li>
              <li>Gửi thông tin khuyến mãi (nếu bạn đồng ý)</li>
              <li>Cải thiện trải nghiệm mua sắm</li>
              <li>Phòng chống gian lận</li>
            </ul>

            <h2>3. Bảo mật thông tin</h2>
            <p>
              OWLS cam kết bảo vệ thông tin cá nhân của bạn bằng các biện pháp bảo mật tiên tiến:
            </p>
            <ul>
              <li>Mã hóa SSL/TLS cho tất cả kết nối</li>
              <li>Mật khẩu được băm (hash) an toàn</li>
              <li>Hệ thống firewall và giám sát 24/7</li>
              <li>Không lưu trữ thông tin thẻ thanh toán trực tiếp</li>
            </ul>

            <h2>4. Chia sẻ thông tin</h2>
            <p>
              Chúng tôi không bán hoặc cho thuê thông tin cá nhân của bạn. Thông tin chỉ được chia sẻ với:
            </p>
            <ul>
              <li>Đối tác vận chuyển (để giao hàng)</li>
              <li>Cổng thanh toán (để xử lý giao dịch)</li>
              <li>Cơ quan pháp luật (khi có yêu cầu hợp pháp)</li>
            </ul>

            <h2>5. Quyền của bạn</h2>
            <p>Bạn có quyền:</p>
            <ul>
              <li>Truy cập và xem thông tin cá nhân</li>
              <li>Yêu cầu sửa đổi thông tin không chính xác</li>
              <li>Yêu cầu xóa tài khoản và dữ liệu</li>
              <li>Từ chối nhận email marketing</li>
            </ul>

            <h2>6. Cookies</h2>
            <p>
              OWLS sử dụng cookies để cải thiện trải nghiệm người dùng, ghi nhớ đăng nhập, 
              và phân tích lưu lượng truy cập. Bạn có thể tắt cookies trong trình duyệt, 
              nhưng một số tính năng có thể bị ảnh hưởng.
            </p>

            <h2>7. Liên hệ</h2>
            <p>
              Nếu bạn có thắc mắc về chính sách bảo mật, vui lòng liên hệ:
            </p>
            <ul>
              <li>Email: <a href="mailto:privacy@owls.vn">privacy@owls.vn</a></li>
              <li>Hotline: 1900 1234</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

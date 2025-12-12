import { Link } from "react-router";
import { Scale, ArrowLeft } from "lucide-react";

export function meta() {
  return [
    { title: "Điều khoản Sử dụng - OWLS" },
    { name: "description", content: "Điều khoản và điều kiện sử dụng OWLS Marketplace" },
  ];
}

export default function TermsOfServicePage() {
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
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-100 dark:bg-blue-900/20">
              <Scale className="h-6 w-6 text-blue-500" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                Điều khoản Sử dụng
              </h1>
              <p className="text-sm text-gray-500">Cập nhật lần cuối: 01/12/2024</p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <div className="prose prose-gray max-w-none dark:prose-invert">
            <h2>1. Giới thiệu</h2>
            <p>
              Chào mừng bạn đến với OWLS Marketplace. Bằng việc truy cập và sử dụng website, 
              bạn đồng ý tuân thủ các điều khoản và điều kiện dưới đây.
            </p>

            <h2>2. Đăng ký tài khoản</h2>
            <p>Khi đăng ký tài khoản, bạn cam kết:</p>
            <ul>
              <li>Cung cấp thông tin chính xác, đầy đủ</li>
              <li>Bảo mật thông tin đăng nhập</li>
              <li>Chịu trách nhiệm về mọi hoạt động dưới tài khoản của mình</li>
              <li>Thông báo ngay khi phát hiện truy cập trái phép</li>
            </ul>

            <h2>3. Quy định mua hàng</h2>
            <p>Khi đặt hàng trên OWLS, bạn xác nhận:</p>
            <ul>
              <li>Đủ 18 tuổi hoặc có sự giám sát của người giám hộ</li>
              <li>Thông tin đơn hàng chính xác</li>
              <li>Phương thức thanh toán hợp lệ</li>
              <li>Đồng ý với giá và chính sách giao hàng</li>
            </ul>

            <h2>4. Quy định bán hàng (Dành cho Vendor)</h2>
            <p>Người bán trên OWLS phải:</p>
            <ul>
              <li>Đăng ký thông tin doanh nghiệp hợp lệ</li>
              <li>Đảm bảo chất lượng sản phẩm như mô tả</li>
              <li>Xử lý đơn hàng trong thời gian quy định</li>
              <li>Tuân thủ chính sách hoàn tiền/đổi trả</li>
              <li>Không bán hàng cấm, hàng giả, hàng nhái</li>
            </ul>

            <h2>5. Thanh toán</h2>
            <p>
              OWLS hỗ trợ nhiều phương thức thanh toán bao gồm COD, VNPay, và các thẻ quốc tế. 
              Mọi giao dịch được xử lý qua các cổng thanh toán được cấp phép.
            </p>

            <h2>6. Giao hàng</h2>
            <p>
              Thời gian giao hàng phụ thuộc vào địa điểm và đơn vị vận chuyển. 
              OWLS không chịu trách nhiệm về các chậm trễ do bên vận chuyển hoặc bất khả kháng.
            </p>

            <h2>7. Hoàn tiền & Đổi trả</h2>
            <p>
              Chính sách hoàn tiền/đổi trả tùy thuộc vào từng người bán. 
              Vui lòng kiểm tra chính sách cụ thể trước khi mua hàng.
            </p>

            <h2>8. Quyền sở hữu trí tuệ</h2>
            <p>
              Tất cả nội dung trên OWLS (logo, hình ảnh, văn bản) thuộc quyền sở hữu của 
              OWLS hoặc bên cấp phép. Nghiêm cấm sao chép, sử dụng trái phép.
            </p>

            <h2>9. Giới hạn trách nhiệm</h2>
            <p>
              OWLS là nền tảng kết nối người mua và người bán. Chúng tôi không chịu trách nhiệm 
              trực tiếp về chất lượng sản phẩm của từng người bán. Mọi tranh chấp sẽ được 
              giải quyết theo quy trình hòa giải của OWLS.
            </p>

            <h2>10. Thay đổi điều khoản</h2>
            <p>
              OWLS có quyền cập nhật điều khoản sử dụng. Thay đổi sẽ được thông báo qua email 
              hoặc trên website. Việc tiếp tục sử dụng dịch vụ đồng nghĩa với việc chấp nhận thay đổi.
            </p>

            <h2>11. Liên hệ</h2>
            <p>
              Mọi thắc mắc về điều khoản sử dụng, vui lòng liên hệ:
            </p>
            <ul>
              <li>Email: <a href="mailto:legal@owls.vn">legal@owls.vn</a></li>
              <li>Hotline: 1900 1234</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

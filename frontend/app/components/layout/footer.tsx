import { Link } from "react-router";
import { Facebook, Instagram, Youtube, Mail, Phone, MapPin } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white dark:border-gray-800 dark:bg-[#0a0a0a]">
      {/* Main Footer Content */}
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 gap-12 md:grid-cols-2 lg:grid-cols-4">
          {/* Company Info */}
          <div className="space-y-4">
            <Link to="/" className="inline-block">
              <span className="text-2xl font-bold text-orange-500">🦉 OWLS</span>
            </Link>
            <p className="text-sm leading-relaxed text-gray-600 dark:text-gray-400">
              Nền tảng thương mại điện tử đa người bán hàng đầu Việt Nam. Kết nối hàng triệu người mua và người bán, mang lại trải nghiệm mua sắm thông minh, an toàn và tiện lợi.
            </p>
            <div className="flex gap-3">
              {[
                { icon: Facebook, href: "https://facebook.com/owlsmarketplace", color: "hover:text-blue-600" },
                { icon: Instagram, href: "https://instagram.com/owlsmarketplace", color: "hover:text-pink-600" },
                { icon: Youtube, href: "https://youtube.com/@owlsmarketplace", color: "hover:text-red-600" }
              ].map((social, idx) => (
                <a
                  key={idx}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 text-gray-500 transition-all hover:bg-white hover:shadow-md dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700 ${social.color}`}
                >
                  <social.icon className="h-5 w-5" />
                </a>
              ))}
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="mb-6 text-sm font-bold uppercase tracking-wider text-gray-900 dark:text-white">
              Về OWLS
            </h3>
            <ul className="space-y-3 text-sm">
              {[
                { label: "Giới thiệu", to: "/about" },
                { label: "Tuyển dụng", to: "/careers" },
                { label: "Điều khoản sử dụng", to: "/terms" },
                { label: "Chính sách bảo mật", to: "/privacy" },
                { label: "Bán hàng cùng OWLS", to: "/seller" },
              ].map((link) => (
                <li key={link.to}>
                  <Link
                    to={link.to}
                    className="text-gray-600 transition-colors hover:text-orange-500 dark:text-gray-400 dark:hover:text-orange-400"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Customer Support */}
          <div>
            <h3 className="mb-6 text-sm font-bold uppercase tracking-wider text-gray-900 dark:text-white">
              Hỗ trợ khách hàng
            </h3>
            <ul className="space-y-3 text-sm">
              {[
                { label: "Trung tâm trợ giúp", to: "/help" },
                { label: "Chính sách vận chuyển", to: "/shipping-policy" },
                { label: "Chính sách đổi trả", to: "/return-policy" },
                { label: "Hướng dẫn thanh toán", to: "/payment-methods" },
                { label: "Câu hỏi thường gặp", to: "/faq" },
              ].map((link) => (
                <li key={link.to}>
                  <Link
                    to={link.to}
                    className="text-gray-600 transition-colors hover:text-orange-500 dark:text-gray-400 dark:hover:text-orange-400"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact Info */}
          <div>
            <h3 className="mb-6 text-sm font-bold uppercase tracking-wider text-gray-900 dark:text-white">
              Liên hệ
            </h3>
            <ul className="space-y-4 text-sm">
              <li className="flex items-start gap-3 text-gray-600 dark:text-gray-400">
                <MapPin className="mt-0.5 h-5 w-5 flex-shrink-0 text-orange-500" />
                <span>Tòa nhà Bitexco, Số 2 Hải Triều, Bến Nghé, Quận 1, TP. Hồ Chí Minh</span>
              </li>
              <li className="flex items-center gap-3 text-gray-600 dark:text-gray-400">
                <Phone className="h-5 w-5 flex-shrink-0 text-orange-500" />
                <span className="font-medium text-gray-900 dark:text-white">1900 1234</span>
                <span className="text-xs text-gray-400">(8:00 - 21:00)</span>
              </li>
              <li className="flex items-center gap-3 text-gray-600 dark:text-gray-400">
                <Mail className="h-5 w-5 flex-shrink-0 text-orange-500" />
                <a href="mailto:support@owls.vn" className="transition-colors hover:text-orange-500">
                  support@owls.vn
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-gray-100 bg-gray-50 py-6 dark:border-gray-800 dark:bg-black/20">
        <div className="container mx-auto flex flex-col items-center justify-between gap-4 px-4 md:flex-row">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            © 2024 OWLS Marketplace. All rights reserved.
          </p>
          
          <div className="flex flex-wrap items-center gap-6">
            <div className="flex items-center gap-3">
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Thanh toán:</span>
              <div className="flex gap-2">
                {/* Payment Icons - Using simple divs for placeholders, replace with real SVGs/Images */}
                <div className="h-6 w-9 rounded bg-white shadow-sm ring-1 ring-gray-200 dark:bg-gray-800 dark:ring-gray-700 flex items-center justify-center text-[8px] font-bold text-blue-600">VISA</div>
                <div className="h-6 w-9 rounded bg-white shadow-sm ring-1 ring-gray-200 dark:bg-gray-800 dark:ring-gray-700 flex items-center justify-center text-[8px] font-bold text-red-500">Master</div>
                <div className="h-6 w-9 rounded bg-white shadow-sm ring-1 ring-gray-200 dark:bg-gray-800 dark:ring-gray-700 flex items-center justify-center text-[8px] font-bold text-blue-400">VNPAY</div>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Vận chuyển:</span>
              <div className="flex gap-2">
                 <div className="h-6 w-9 rounded bg-white shadow-sm ring-1 ring-gray-200 dark:bg-gray-800 dark:ring-gray-700 flex items-center justify-center text-[8px] font-bold text-orange-500">GHN</div>
                 <div className="h-6 w-9 rounded bg-white shadow-sm ring-1 ring-gray-200 dark:bg-gray-800 dark:ring-gray-700 flex items-center justify-center text-[8px] font-bold text-green-600">GHTK</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
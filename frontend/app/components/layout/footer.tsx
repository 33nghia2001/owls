import { Link } from "react-router";
import { Facebook, Instagram, Youtube, Mail, Phone, MapPin } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-4">
          {/* Company Info */}
          <div>
            <Link to="/" className="mb-4 inline-block">
              <span className="text-2xl font-bold text-orange-500">🦉 OWLS</span>
            </Link>
            <p className="mb-4 text-sm text-gray-600 dark:text-gray-400">
              Nền tảng thương mại điện tử đa người bán hàng đầu Việt Nam. Mua sắm
              thông minh, giá cả hợp lý.
            </p>
            <div className="flex gap-4">
              <a
                href="https://facebook.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-orange-500 dark:text-gray-400"
              >
                <Facebook className="h-5 w-5" />
              </a>
              <a
                href="https://instagram.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-orange-500 dark:text-gray-400"
              >
                <Instagram className="h-5 w-5" />
              </a>
              <a
                href="https://youtube.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-orange-500 dark:text-gray-400"
              >
                <Youtube className="h-5 w-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="mb-4 font-semibold text-gray-900 dark:text-gray-100">
              Về OWLS
            </h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link
                  to="/about"
                  className="text-gray-600 hover:text-orange-500 dark:text-gray-400"
                >
                  Giới thiệu
                </Link>
              </li>
              <li>
                <Link
                  to="/careers"
                  className="text-gray-600 hover:text-orange-500 dark:text-gray-400"
                >
                  Tuyển dụng
                </Link>
              </li>
              <li>
                <Link
                  to="/terms"
                  className="text-gray-600 hover:text-orange-500 dark:text-gray-400"
                >
                  Điều khoản sử dụng
                </Link>
              </li>
              <li>
                <Link
                  to="/privacy"
                  className="text-gray-600 hover:text-orange-500 dark:text-gray-400"
                >
                  Chính sách bảo mật
                </Link>
              </li>
              <li>
                <Link
                  to="/seller"
                  className="text-gray-600 hover:text-orange-500 dark:text-gray-400"
                >
                  Bán hàng cùng OWLS
                </Link>
              </li>
            </ul>
          </div>

          {/* Customer Support */}
          <div>
            <h3 className="mb-4 font-semibold text-gray-900 dark:text-gray-100">
              Hỗ trợ khách hàng
            </h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link
                  to="/help"
                  className="text-gray-600 hover:text-orange-500 dark:text-gray-400"
                >
                  Trung tâm trợ giúp
                </Link>
              </li>
              <li>
                <Link
                  to="/shipping-policy"
                  className="text-gray-600 hover:text-orange-500 dark:text-gray-400"
                >
                  Chính sách vận chuyển
                </Link>
              </li>
              <li>
                <Link
                  to="/return-policy"
                  className="text-gray-600 hover:text-orange-500 dark:text-gray-400"
                >
                  Chính sách đổi trả
                </Link>
              </li>
              <li>
                <Link
                  to="/payment-methods"
                  className="text-gray-600 hover:text-orange-500 dark:text-gray-400"
                >
                  Hướng dẫn thanh toán
                </Link>
              </li>
              <li>
                <Link
                  to="/faq"
                  className="text-gray-600 hover:text-orange-500 dark:text-gray-400"
                >
                  Câu hỏi thường gặp
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="mb-4 font-semibold text-gray-900 dark:text-gray-100">
              Liên hệ
            </h3>
            <ul className="space-y-3 text-sm">
              <li className="flex items-start gap-3 text-gray-600 dark:text-gray-400">
                <MapPin className="mt-0.5 h-5 w-5 flex-shrink-0 text-orange-500" />
                <span>123 Đường ABC, Quận XYZ, TP. Hồ Chí Minh</span>
              </li>
              <li className="flex items-center gap-3 text-gray-600 dark:text-gray-400">
                <Phone className="h-5 w-5 flex-shrink-0 text-orange-500" />
                <span>1900 1234</span>
              </li>
              <li className="flex items-center gap-3 text-gray-600 dark:text-gray-400">
                <Mail className="h-5 w-5 flex-shrink-0 text-orange-500" />
                <a href="mailto:support@owls.vn" className="hover:text-orange-500">
                  support@owls.vn
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Payment methods */}
        <div className="mt-8 border-t border-gray-200 pt-8 dark:border-gray-800">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="mb-2 text-sm font-medium text-gray-900 dark:text-gray-100">
                Phương thức thanh toán
              </p>
              <div className="flex gap-2">
                <div className="rounded bg-white p-2 shadow-sm dark:bg-gray-800">
                  <span className="text-xs font-medium">VISA</span>
                </div>
                <div className="rounded bg-white p-2 shadow-sm dark:bg-gray-800">
                  <span className="text-xs font-medium">MasterCard</span>
                </div>
                <div className="rounded bg-white p-2 shadow-sm dark:bg-gray-800">
                  <span className="text-xs font-medium">VNPay</span>
                </div>
                <div className="rounded bg-white p-2 shadow-sm dark:bg-gray-800">
                  <span className="text-xs font-medium">COD</span>
                </div>
              </div>
            </div>
            <div>
              <p className="mb-2 text-sm font-medium text-gray-900 dark:text-gray-100">
                Đơn vị vận chuyển
              </p>
              <div className="flex gap-2">
                <div className="rounded bg-white p-2 shadow-sm dark:bg-gray-800">
                  <span className="text-xs font-medium">GHN</span>
                </div>
                <div className="rounded bg-white p-2 shadow-sm dark:bg-gray-800">
                  <span className="text-xs font-medium">GHTK</span>
                </div>
                <div className="rounded bg-white p-2 shadow-sm dark:bg-gray-800">
                  <span className="text-xs font-medium">J&T</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-8 border-t border-gray-200 pt-8 text-center text-sm text-gray-600 dark:border-gray-800 dark:text-gray-400">
          <p>© 2024 OWLS Marketplace. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}

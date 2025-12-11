import { Link } from "react-router";

export function meta() {
  return [
    { title: "Tài khoản - OWLS" },
    { name: "description", content: "Quản lý tài khoản của bạn" },
  ];
}

export default function AccountPage() {
  const links = [
    { to: "/account/orders", label: "Đơn hàng" },
    { to: "/account/addresses", label: "Địa chỉ" },
    { to: "/account/profile", label: "Hồ sơ" },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-4 text-3xl font-bold text-gray-900 dark:text-gray-100">Tài khoản</h1>
      <div className="grid gap-4 md:grid-cols-3">
        {links.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className="rounded-xl border border-gray-200 bg-white p-5 transition hover:border-orange-500 hover:shadow-lg dark:border-gray-800 dark:bg-gray-900"
          >
            <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">{link.label}</p>
            <p className="text-sm text-gray-500">Quản lý {link.label.toLowerCase()}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}

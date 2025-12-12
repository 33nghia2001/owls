import { Link } from "react-router";
import { useState } from "react";
import { HelpCircle, ArrowLeft, ChevronDown, Search, ShoppingCart, Truck, CreditCard, User, Package, MessageCircle } from "lucide-react";
import { cn } from "~/lib/utils";
import { Input } from "~/components/ui";

export function meta() {
  return [
    { title: "Câu hỏi thường gặp - OWLS" },
    { name: "description", content: "Giải đáp các thắc mắc phổ biến về OWLS Marketplace" },
  ];
}

interface FAQItem {
  question: string;
  answer: string;
}

interface FAQCategory {
  id: string;
  title: string;
  icon: React.ElementType;
  items: FAQItem[];
}

const faqData: FAQCategory[] = [
  {
    id: "account",
    title: "Tài khoản",
    icon: User,
    items: [
      {
        question: "Làm sao để đăng ký tài khoản OWLS?",
        answer: "Bạn có thể đăng ký tài khoản bằng cách nhấn nút 'Đăng ký' ở góc trên bên phải, sau đó điền email và mật khẩu. Bạn cũng có thể đăng ký nhanh bằng tài khoản Google hoặc Facebook."
      },
      {
        question: "Tôi quên mật khẩu, phải làm sao?",
        answer: "Nhấn vào 'Quên mật khẩu' ở trang đăng nhập, nhập email đã đăng ký, và làm theo hướng dẫn trong email để đặt lại mật khẩu mới."
      },
      {
        question: "Làm sao để thay đổi thông tin cá nhân?",
        answer: "Đăng nhập vào tài khoản, vào mục 'Tài khoản của tôi' > 'Hồ sơ' để chỉnh sửa họ tên, số điện thoại, ảnh đại diện và các thông tin khác."
      },
    ]
  },
  {
    id: "order",
    title: "Đặt hàng",
    icon: ShoppingCart,
    items: [
      {
        question: "Làm sao để đặt hàng trên OWLS?",
        answer: "Chọn sản phẩm muốn mua > Thêm vào giỏ hàng > Vào giỏ hàng kiểm tra > Nhấn 'Thanh toán' > Điền thông tin giao hàng > Chọn phương thức thanh toán > Xác nhận đặt hàng."
      },
      {
        question: "Tôi có thể hủy đơn hàng không?",
        answer: "Bạn có thể hủy đơn hàng khi đơn chưa được người bán xác nhận. Vào 'Đơn hàng của tôi', chọn đơn cần hủy và nhấn 'Hủy đơn'. Nếu đã xác nhận, vui lòng liên hệ người bán trực tiếp."
      },
      {
        question: "Đơn hàng tối thiểu là bao nhiêu?",
        answer: "OWLS không yêu cầu giá trị đơn hàng tối thiểu. Tuy nhiên, để được miễn phí vận chuyển, đơn hàng cần đạt từ 500.000đ trở lên."
      },
    ]
  },
  {
    id: "shipping",
    title: "Vận chuyển",
    icon: Truck,
    items: [
      {
        question: "Phí vận chuyển được tính như thế nào?",
        answer: "Phí ship phụ thuộc vào khoảng cách, trọng lượng và kích thước đơn hàng. Thông thường từ 15.000đ - 40.000đ. Miễn phí ship cho đơn từ 500.000đ."
      },
      {
        question: "Thời gian giao hàng bao lâu?",
        answer: "Nội thành TP.HCM, Hà Nội: 1-3 ngày. Các tỉnh thành khác: 3-7 ngày làm việc. Thời gian có thể thay đổi vào mùa cao điểm."
      },
      {
        question: "Làm sao để theo dõi đơn hàng?",
        answer: "Vào 'Đơn hàng của tôi' để xem trạng thái. Khi đơn được giao cho vận chuyển, bạn sẽ nhận mã vận đơn qua email/SMS để tra cứu chi tiết."
      },
    ]
  },
  {
    id: "payment",
    title: "Thanh toán",
    icon: CreditCard,
    items: [
      {
        question: "OWLS hỗ trợ những phương thức thanh toán nào?",
        answer: "Chúng tôi hỗ trợ: Thanh toán khi nhận hàng (COD), VNPay (ATM, Visa/Master, QR Code), và các thẻ quốc tế qua Stripe."
      },
      {
        question: "Thanh toán online có an toàn không?",
        answer: "Tất cả giao dịch được mã hóa SSL và xử lý qua các cổng thanh toán được cấp phép bởi Ngân hàng Nhà nước. OWLS không lưu trữ thông tin thẻ của bạn."
      },
      {
        question: "Tôi đã thanh toán nhưng đơn hàng chưa được xác nhận?",
        answer: "Vui lòng đợi 15-30 phút để hệ thống xử lý. Nếu sau 1 giờ vẫn chưa cập nhật, liên hệ hotline 1900 1234 kèm mã đơn hàng để được hỗ trợ."
      },
    ]
  },
  {
    id: "return",
    title: "Đổi trả & Hoàn tiền",
    icon: Package,
    items: [
      {
        question: "Chính sách đổi trả của OWLS như thế nào?",
        answer: "Bạn có thể đổi trả trong vòng 7 ngày kể từ khi nhận hàng nếu sản phẩm bị lỗi, sai mẫu hoặc không đúng mô tả. Xem chi tiết tại trang Chính sách Đổi trả."
      },
      {
        question: "Tiền hoàn lại sau bao lâu?",
        answer: "Hoàn vào Ví OWLS: Ngay lập tức. Hoàn vào tài khoản ngân hàng/thẻ: 3-7 ngày làm việc tùy ngân hàng."
      },
      {
        question: "Ai chịu phí ship khi đổi trả?",
        answer: "Nếu lỗi từ người bán (hàng lỗi, sai), người bán chịu 100% phí ship. Nếu đổi theo ý khách (đổi size, màu), khách hàng chịu phí ship 2 chiều."
      },
    ]
  },
  {
    id: "seller",
    title: "Bán hàng trên OWLS",
    icon: MessageCircle,
    items: [
      {
        question: "Làm sao để đăng ký bán hàng?",
        answer: "Đăng nhập tài khoản > Vào 'Kênh người bán' > Nhấn 'Đăng ký bán hàng' > Điền thông tin shop và chờ duyệt (1-3 ngày làm việc)."
      },
      {
        question: "Phí bán hàng trên OWLS là bao nhiêu?",
        answer: "OWLS thu phí hoa hồng từ 3-8% tùy ngành hàng. Không thu phí duy trì shop hàng tháng. Chi tiết xem tại Chính sách Người bán."
      },
      {
        question: "Khi nào tôi nhận được tiền bán hàng?",
        answer: "Tiền sẽ được chuyển vào Ví Người bán sau khi đơn hàng hoàn tất (khách nhận hàng + qua thời hạn khiếu nại). Bạn có thể rút tiền về tài khoản ngân hàng bất cứ lúc nào."
      },
    ]
  },
];

export default function FAQPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [openItems, setOpenItems] = useState<Set<string>>(new Set());

  const toggleItem = (categoryId: string, index: number) => {
    const key = `${categoryId}-${index}`;
    const newOpenItems = new Set(openItems);
    if (newOpenItems.has(key)) {
      newOpenItems.delete(key);
    } else {
      newOpenItems.add(key);
    }
    setOpenItems(newOpenItems);
  };

  // Filter FAQs based on search
  const filteredData = searchQuery
    ? faqData.map(category => ({
        ...category,
        items: category.items.filter(
          item =>
            item.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
            item.answer.toLowerCase().includes(searchQuery.toLowerCase())
        )
      })).filter(category => category.items.length > 0)
    : faqData;

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
              <HelpCircle className="h-6 w-6 text-orange-500" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                Câu hỏi thường gặp
              </h1>
              <p className="text-sm text-gray-500">Tìm câu trả lời nhanh cho thắc mắc của bạn</p>
            </div>
          </div>
        </div>

        {/* Search */}
        <div className="relative mb-8">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <Input
            type="text"
            placeholder="Tìm kiếm câu hỏi..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-12 h-12 text-base"
          />
        </div>

        {/* FAQ Categories */}
        <div className="space-y-6">
          {filteredData.map((category) => (
            <div
              key={category.id}
              className="rounded-2xl border border-gray-200 bg-white overflow-hidden shadow-sm dark:border-gray-800 dark:bg-gray-900"
            >
              {/* Category Header */}
              <div className="flex items-center gap-3 p-4 border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
                <category.icon className="h-5 w-5 text-orange-500" />
                <h2 className="font-semibold text-gray-900 dark:text-gray-100">{category.title}</h2>
                <span className="ml-auto text-sm text-gray-500">{category.items.length} câu hỏi</span>
              </div>

              {/* FAQ Items */}
              <div className="divide-y divide-gray-100 dark:divide-gray-800">
                {category.items.map((item, index) => {
                  const isOpen = openItems.has(`${category.id}-${index}`);
                  return (
                    <div key={index}>
                      <button
                        onClick={() => toggleItem(category.id, index)}
                        className="flex w-full items-center justify-between p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                      >
                        <span className="font-medium text-gray-900 dark:text-gray-100 pr-4">
                          {item.question}
                        </span>
                        <ChevronDown
                          className={cn(
                            "h-5 w-5 flex-shrink-0 text-gray-400 transition-transform",
                            isOpen && "rotate-180"
                          )}
                        />
                      </button>
                      {isOpen && (
                        <div className="px-4 pb-4 text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
                          {item.answer}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* No Results */}
        {filteredData.length === 0 && (
          <div className="text-center py-12">
            <HelpCircle className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">Không tìm thấy câu hỏi phù hợp</p>
            <p className="text-sm text-gray-400 mt-1">Thử tìm kiếm với từ khóa khác hoặc liên hệ hỗ trợ</p>
          </div>
        )}

        {/* Contact Support */}
        <div className="mt-8 rounded-2xl border border-orange-200 bg-orange-50 p-6 text-center dark:border-orange-800 dark:bg-orange-900/20">
          <h3 className="font-semibold text-orange-800 dark:text-orange-200 mb-2">
            Không tìm thấy câu trả lời?
          </h3>
          <p className="text-sm text-orange-700 dark:text-orange-300 mb-4">
            Đội ngũ hỗ trợ OWLS luôn sẵn sàng giúp đỡ bạn
          </p>
          <div className="flex flex-wrap justify-center gap-4 text-sm">
            <a href="mailto:support@owls.vn" className="text-orange-600 hover:underline">
              support@owls.vn
            </a>
            <span className="text-orange-400">|</span>
            <span className="text-orange-600">Hotline: 1900 1234</span>
          </div>
        </div>
      </div>
    </div>
  );
}

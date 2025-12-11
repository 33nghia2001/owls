# OWLS Marketplace

**OWLS** là một nền tảng thương mại điện tử đa người bán (Multi-vendor Marketplace) hiện đại, được xây dựng với kiến trúc Headless: Backend mạnh mẽ bằng **Django** và Frontend tối ưu SEO bằng **React Router v7**.

![Project Status](https://img.shields.io/badge/Status-In%20Development-orange)
![Backend](https://img.shields.io/badge/Backend-Django%20Rest%20Framework-green)
![Frontend](https://img.shields.io/badge/Frontend-React%20Router%20v7-blue)

## 🦉 Tính năng chính

### Cho Khách hàng
- 🛒 **Giỏ hàng thông minh** - Hỗ trợ cả guest và user đăng nhập
- 💳 **Thanh toán đa dạng** - Stripe (Quốc tế), VNPay (Việt Nam), COD
- 📦 **Theo dõi đơn hàng** - Real-time tracking shipment
- ⭐ **Đánh giá sản phẩm** - Review với hình ảnh
- 💬 **Chat với Shop** - Nhắn tin trực tiếp với người bán
- ❤️ **Wishlist** - Lưu sản phẩm yêu thích
- 🔔 **Thông báo** - Push notification cho đơn hàng

### Cho Người bán (Vendor)
- 🏪 **Quản lý Shop** - Dashboard riêng cho từng vendor
- 📊 **Analytics** - Thống kê doanh thu, đơn hàng, sản phẩm bán chạy
- 📦 **Quản lý kho** - Inventory với cảnh báo hết hàng
- 🎫 **Mã giảm giá** - Tạo coupon cho shop
- 💰 **Thanh toán** - Quản lý payout và bank account

### Cho Admin
- 👥 **Quản lý Users** - Customers, Vendors, Staff
- ✅ **Duyệt Vendor** - Phê duyệt shop mới
- 📈 **Platform Analytics** - Thống kê toàn hệ thống
- 🏷️ **Quản lý Categories** - Danh mục sản phẩm (MPTT tree)

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| Python 3.12 | Language |
| Django 5.x | Web Framework |
| Django REST Framework | API |
| PostgreSQL | Database (Aiven Cloud) |
| Redis | Cache & Celery Broker |
| Celery | Background Tasks |
| JWT | Authentication |
| Stripe & VNPay | Payment Gateway |
| drf-spectacular | API Documentation |

### Frontend
| Technology | Purpose |
|------------|---------|
| React Router v7 | Framework |
| TypeScript | Language |
| TailwindCSS | Styling |
| Vite | Build Tool |

## 📁 Project Structure

```
owls/
├── backend/
│   ├── apps/
│   │   ├── users/          # Authentication & User management
│   │   ├── vendors/        # Vendor/Shop management
│   │   ├── products/       # Products, Categories, Variants
│   │   ├── cart/           # Shopping cart
│   │   ├── orders/         # Order processing
│   │   ├── payments/       # Stripe & VNPay integration
│   │   ├── reviews/        # Product & Vendor reviews
│   │   ├── coupons/        # Discount codes
│   │   ├── wishlist/       # User wishlists
│   │   ├── shipping/       # Shipping methods & tracking
│   │   ├── inventory/      # Stock management
│   │   ├── notifications/  # Push notifications
│   │   ├── messaging/      # Customer-Vendor chat
│   │   └── analytics/      # Statistics & Reports
│   ├── backend/            # Django settings
│   └── manage.py
├── frontend/
│   ├── app/
│   │   ├── routes/         # React Router pages
│   │   └── components/     # Reusable components
│   └── package.json
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (hoặc sử dụng cloud như Aiven)
- Redis

### Backend Setup

```bash
# Clone repository
git clone https://github.com/33nghia2001/owls.git
cd owls

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (MacOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Setup environment variables
cp backend/.env.example backend/.env
# Edit .env with your credentials

# Run migrations
cd backend
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## 📚 API Documentation

Sau khi chạy backend server, truy cập:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Admin Panel**: http://localhost:8000/admin/

## 🔑 Environment Variables

Tạo file `.env` trong thư mục `backend/`:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgres://user:password@host:port/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# Stripe
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# VNPay
VNPAY_TMN_CODE=your-tmn-code
VNPAY_HASH_SECRET=your-hash-secret
```

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

**Nghia Hoang**
- GitHub: [@33nghia2001](https://github.com/33nghia2001)

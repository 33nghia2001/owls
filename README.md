# OWLS Marketplace

**OWLS** là một nền tảng thương mại điện tử đa người bán (Multi-vendor Marketplace) hiện đại, được xây dựng với kiến trúc Headless: Backend mạnh mẽ bằng **Django** và Frontend tối ưu SEO bằng **React Router v7**.

![Project Status](https://img.shields.io/badge/Status-In%20Development-orange)
![Backend](https://img.shields.io/badge/Backend-Django%20Rest%20Framework-green)
![Frontend](https://img.shields.io/badge/Frontend-React%20Router%20v7-blue)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.x-green)

## 🦉 Tính năng chính

### Cho Khách hàng
- 🛒 **Giỏ hàng thông minh** - Hỗ trợ cả guest và user đăng nhập, merge cart khi login
- 💳 **Thanh toán đa dạng** - Stripe (Quốc tế), VNPay (Việt Nam), COD
- 📦 **Theo dõi đơn hàng** - Real-time tracking với WebSocket
- ⭐ **Đánh giá sản phẩm** - Review với hình ảnh, chỉ verified purchase
- 💬 **Chat với Shop** - Nhắn tin trực tiếp với người bán qua WebSocket
- ❤️ **Wishlist** - Lưu sản phẩm yêu thích
- 🔔 **Thông báo** - Push notification cho đơn hàng
- 🎫 **Mã giảm giá** - Áp dụng coupon khi checkout

### Cho Người bán (Vendor)
- 🏪 **Quản lý Shop** - Dashboard riêng cho từng vendor
- 📊 **Analytics** - Thống kê doanh thu, đơn hàng, sản phẩm bán chạy
- 📦 **Quản lý kho** - Inventory với cảnh báo low stock, hỗ trợ variants
- 🎫 **Mã giảm giá** - Tạo coupon cho shop với giới hạn sử dụng
- 💰 **Thanh toán** - Quản lý payout với hold period, bank account

### Cho Admin
- 👥 **Quản lý Users** - Customers, Vendors, Staff
- ✅ **Duyệt Vendor** - Phê duyệt shop mới
- 📈 **Platform Analytics** - Thống kê toàn hệ thống
- 🏷️ **Quản lý Categories** - Danh mục sản phẩm (MPTT tree)
- 💸 **Refund Management** - Xử lý hoàn tiền Stripe/VNPay

## 🔒 Security Features

- **JWT Authentication** với refresh token rotation
- **WebSocket Authentication** với ticket-based system
- **Rate Limiting** để chống DDoS
- **XSS Prevention** với bleach HTML sanitization
- **CSRF Protection** cho forms
- **Input Validation** và sanitization
- **Secure Password** với custom validators
- **Open Redirect Prevention** cho payment callbacks

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| Python 3.12 | Language |
| Django 5.x | Web Framework |
| Django REST Framework | API |
| Django Channels | WebSocket (Chat, Notifications) |
| PostgreSQL | Database (Aiven Cloud) |
| Redis | Cache, Celery Broker, Channels Layer |
| Celery | Background Tasks với retry mechanism |
| SimpleJWT | Authentication |
| Stripe & VNPay | Payment Gateway với IPN/Webhook |
| django-money | Currency handling |
| django-mptt | Category tree |
| drf-spectacular | API Documentation |
| bleach | HTML Sanitization |

### Frontend
| Technology | Purpose |
|------------|---------|
| React Router v7 | Framework (SSR) |
| TypeScript | Language |
| TailwindCSS | Styling |
| Vite | Build Tool |

## 📁 Project Structure

```
owls/
├── backend/
│   ├── apps/
│   │   ├── users/          # Authentication & User management
│   │   ├── vendors/        # Vendor/Shop management, Payouts
│   │   ├── products/       # Products, Categories, Variants, Tags
│   │   ├── cart/           # Shopping cart (guest + user)
│   │   ├── orders/         # Order processing, Status workflow
│   │   ├── payments/       # Stripe & VNPay integration, Refunds
│   │   ├── reviews/        # Product & Vendor reviews
│   │   ├── coupons/        # Discount codes với usage limits
│   │   ├── wishlist/       # User wishlists
│   │   ├── shipping/       # Shipping methods & tracking
│   │   ├── inventory/      # Stock management, Movements
│   │   ├── notifications/  # Push notifications
│   │   ├── messaging/      # Customer-Vendor chat (WebSocket)
│   │   └── analytics/      # Statistics & Reports
│   ├── backend/            # Django settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py         # ASGI config for Channels
│   │   └── validators.py   # Custom password validators
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

# Run development server (HTTP only)
python manage.py runserver

# Run with WebSocket support (recommended)
daphne backend.asgi:application
```

### Celery Worker (Background Tasks)

```bash
# Terminal riêng
cd backend
celery -A backend worker -l info

# Celery Beat (scheduled tasks)
celery -A backend beat -l info
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
SECRET_KEY=your-secret-key-use-secrets.token_urlsafe(50)
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Frontend URL (for payment callbacks)
FRONTEND_URL=http://localhost:5173

# Database
DATABASE_URL=postgres://user:password@host:port/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (for order confirmations)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Stripe
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# VNPay
VNPAY_TMN_CODE=your-tmn-code
VNPAY_HASH_SECRET=your-hash-secret
VNPAY_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
VNPAY_RETURN_URL=http://localhost:8000/api/payments/vnpay_return/
```

## 🔄 Order Status Workflow

```
pending → confirmed → processing → shipped → delivered
    ↓         ↓           ↓           ↓
cancelled  cancelled  cancelled  cancelled (với refund)
```

## 📊 Key Business Rules

- **Inventory**: Products với variants phải quản lý stock ở variant level
- **Vendor Payout**: Hold period 7 ngày sau khi đơn hàng delivered
- **Coupons**: Giới hạn usage per user và total usage
- **Reviews**: Chỉ verified purchase mới được review
- **Pending Orders**: Giới hạn 3 pending orders per user

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

**Nghia Hoang**
- GitHub: [@33nghia2001](https://github.com/33nghia2001)

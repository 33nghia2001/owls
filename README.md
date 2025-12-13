# 🦉 Owls E-commerce Platform

<div align="center">

![Owls Logo](https://img.shields.io/badge/Owls-E--commerce-orange?style=for-the-badge&logo=shopify)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![Django](https://img.shields.io/badge/Django-5.2-green?style=flat-square&logo=django)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue?style=flat-square&logo=typescript)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

**Nền tảng thương mại điện tử đa nhà cung cấp (Multi-vendor Marketplace) hiện đại, bảo mật và có khả năng mở rộng cao.**

[Tính năng](#-tính-năng) • [Kiến trúc](#-kiến-trúc) • [Cài đặt](#-cài-đặt) • [API Docs](#-api-documentation) • [Đóng góp](#-đóng-góp)

</div>

---

## 📋 Tổng quan

**Owls** là một nền tảng e-commerce B2C/B2B được xây dựng với Django REST Framework và React/Next.js, được thiết kế để xử lý hàng ngàn đơn hàng mỗi ngày với độ tin cậy cao.

### Điểm nổi bật

- 🔐 **Bảo mật Enterprise-grade**: JWT RS256, Rate Limiting, CORS, XSS/CSRF Protection
- ⚡ **Hiệu năng cao**: Redis Caching, Database Connection Pooling, Async Tasks
- 🏗️ **Kiến trúc Modular**: 4-Pillar Architecture, Service Layer Pattern
- 💳 **Đa phương thức thanh toán**: VNPay, MoMo, ZaloPay
- ☁️ **Cloud-Native**: Cloudflare R2, PostgreSQL, Redis Cloud
- 🔄 **Race Condition Safe**: Database Locking, Atomic Operations

---

## ✨ Tính năng

### 👤 Quản lý Người dùng
- Đăng ký/Đăng nhập với JWT (RS256)
- Xác thực 2 yếu tố (2FA) - *coming soon*
- Quản lý địa chỉ giao hàng
- Lịch sử đơn hàng
- Hệ thống referral

### 🛒 Giỏ hàng & Đặt hàng
- Session-based cart cho guest users
- Merge cart khi đăng nhập
- Áp dụng mã giảm giá
- Tính toán thuế VAT tự động
- Inventory locking chống overselling

### 💰 Thanh toán
- **VNPay**: Thẻ ATM, Visa/Master, QR Code
- **MoMo**: Ví điện tử, QR Code
- **ZaloPay**: Ví điện tử, QR Code
- Webhook xử lý callback tự động
- Refund management

### 🏪 Vendor Portal
- Dashboard analytics
- Quản lý sản phẩm & inventory
- Xử lý đơn hàng
- Commission tracking
- Payout management

### 📦 Sản phẩm
- Product variants (Size, Color, etc.)
- Multi-image upload (Cloudflare R2)
- Category hierarchy
- Product attributes & filters
- SEO-friendly URLs

### 🎯 Marketing & Promotions
- Coupon codes (%, fixed, free shipping)
- Flash sales
- Loyalty points - *coming soon*
- Email campaigns - *coming soon*

---

## 🏗️ Kiến trúc

### 4-Pillar Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OWLS E-COMMERCE                          │
├─────────────┬─────────────┬─────────────┬──────────────────┤
│    BASE     │  BUSINESS   │   CLIENT    │     GROWTH       │
│             │             │             │                  │
│ • Users     │ • Products  │ • Reviews   │ • Search         │
│ • Auth      │ • Cart      │ • Coupons   │ • Recommendations│
│ • Admin     │ • Orders    │ • Wishlist  │ • Campaigns      │
│ • Uploads   │ • Payments  │ • Messaging │ • Affiliates     │
│ • Analytics │ • Vendors   │ • Loyalty   │ • SEO            │
│ • KYC       │ • Inventory │ • Blog      │ • Ads            │
│ • Audit     │ • Shipping  │ • Banners   │                  │
└─────────────┴─────────────┴─────────────┴──────────────────┘
```

### Service Layer Pattern

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Views     │ ──▶ │   Services   │ ──▶ │    Models    │
│  (API Layer) │     │(Business Logic)    │  (Data Layer)│
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ Celery Tasks │
                     │   (Async)    │
                     └──────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Django 5.2, Django REST Framework |
| **Frontend** | Next.js 15 (Store), Vite + React (Admin/Vendor) |
| **Database** | PostgreSQL 15 (Aiven Cloud) |
| **Cache** | Redis 7 (Redis Cloud) |
| **Storage** | Cloudflare R2 (S3-compatible) |
| **Queue** | Celery + Redis |
| **Auth** | JWT RS256 (SimpleJWT) |
| **API Docs** | drf-spectacular (OpenAPI 3.0) |

---

## 📁 Cấu trúc thư mục

```
owls/
├── backend/
│   ├── apps/
│   │   ├── base/                    # Core Infrastructure
│   │   │   ├── core/
│   │   │   │   ├── users/           # User management
│   │   │   │   ├── uploads/         # File storage (R2)
│   │   │   │   ├── notifications/   # Push/Email notifications
│   │   │   │   └── system/          # Base models, exceptions
│   │   │   ├── operations/
│   │   │   │   ├── audit_logs/      # Activity logging
│   │   │   │   └── support/         # Customer support
│   │   │   └── risk/
│   │   │       ├── kyc/             # Know Your Customer
│   │   │       └── fraud_detection/ # Fraud prevention
│   │   │
│   │   ├── business/                # Commerce & Finance
│   │   │   ├── commerce/
│   │   │   │   ├── products/        # Product catalog
│   │   │   │   ├── cart/            # Shopping cart
│   │   │   │   ├── orders/          # Order management
│   │   │   │   └── payments/        # Payment processing
│   │   │   ├── finance/
│   │   │   │   ├── wallets/         # User wallets
│   │   │   │   └── invoices/        # Invoice generation
│   │   │   └── partners/
│   │   │       ├── vendors/         # Vendor management
│   │   │       └── shipping/        # Shipping providers
│   │   │
│   │   ├── client/                  # Customer Experience
│   │   │   ├── experience/
│   │   │   │   ├── reviews/         # Product reviews
│   │   │   │   ├── coupons/         # Discount codes
│   │   │   │   └── wishlist/        # Wishlist
│   │   │   └── content/
│   │   │       ├── blog/            # Blog posts
│   │   │       └── banners/         # Homepage banners
│   │   │
│   │   └── growth/                  # Marketing & Intelligence
│   │       ├── marketing/
│   │       │   ├── campaigns/       # Marketing campaigns
│   │       │   └── affiliates/      # Affiliate program
│   │       └── intelligence/
│   │           ├── search/          # Search engine
│   │           └── recommendations/ # Product recommendations
│   │
│   ├── backend/
│   │   ├── settings.py              # Django settings
│   │   ├── urls.py                  # URL routing
│   │   └── celery.py                # Celery configuration
│   │
│   └── manage.py
│
├── frontend/
│   ├── apps/
│   │   ├── store/                   # Customer-facing (Next.js)
│   │   ├── admin/                   # Admin panel (Vite + React)
│   │   └── vendor/                  # Vendor portal (Vite + React)
│   │
│   └── packages/
│       ├── ui/                      # Shared UI components
│       ├── eslint-config/           # ESLint configurations
│       └── typescript-config/       # TypeScript configurations
│
└── README.md
```

---

## 🚀 Cài đặt

### Yêu cầu hệ thống

- Python 3.12+
- Node.js 20+
- PostgreSQL 15+ (hoặc sử dụng cloud)
- Redis 7+ (hoặc sử dụng cloud)

### 1. Clone repository

```bash
git clone https://github.com/33nghia2001/owls.git
cd owls
```

### 2. Backend Setup

```bash
# Tạo virtual environment
cd backend
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Chỉnh sửa .env với credentials của bạn

# Generate RSA keys cho JWT RS256
python generate_keys.py

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run all apps (turborepo)
npm run dev

# Or run specific app
npm run dev --filter=store
npm run dev --filter=admin
npm run dev --filter=vendor
```

### 4. Celery Workers (Optional)

```bash
# Worker
celery -A backend worker -l info -Q default,email,maintenance

# Beat scheduler (periodic tasks)
celery -A backend beat -l info
```

---

## ⚙️ Cấu hình Environment

```env
# === GENERAL ===
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# === DATABASE ===
DATABASE_URL=postgres://user:pass@host:port/db_name

# === REDIS ===
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1

# === JWT RS256 ===
JWT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"

# === STORAGE (Cloudflare R2) ===
USE_S3=True
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=owls
AWS_S3_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com
AWS_S3_CUSTOM_DOMAIN=cdn.owls.asia

# === PAYMENT GATEWAYS ===
VNPAY_TMN_CODE=xxx
VNPAY_HASH_SECRET=xxx
MOMO_PARTNER_CODE=xxx
ZALOPAY_APP_ID=xxx
```

---

## 📚 API Documentation

Khi server chạy, truy cập:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### API Endpoints chính

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register/` | POST | Đăng ký tài khoản |
| `/api/v1/auth/login/` | POST | Đăng nhập (JWT) |
| `/api/v1/auth/logout/` | POST | Đăng xuất |
| `/api/v1/users/profile/` | GET/PUT | Thông tin user |
| `/api/v1/products/` | GET | Danh sách sản phẩm |
| `/api/v1/cart/` | GET/POST | Giỏ hàng |
| `/api/v1/orders/` | GET/POST | Đơn hàng |
| `/api/v1/payments/vnpay/create/` | POST | Tạo thanh toán VNPay |

---

## 🔒 Bảo mật

### Các biện pháp bảo mật đã triển khai:

- ✅ **JWT RS256**: Asymmetric encryption cho token
- ✅ **Rate Limiting**: Chống brute force attacks
- ✅ **CORS**: Cross-Origin Resource Sharing
- ✅ **CSRF Protection**: Django CSRF middleware
- ✅ **SQL Injection**: Django ORM parameterized queries
- ✅ **XSS Protection**: Content Security Policy headers
- ✅ **Password Hashing**: PBKDF2 với SHA256
- ✅ **Database Locking**: `select_for_update()` chống race conditions
- ✅ **Stock Constraints**: Database-level `CHECK` constraints

### Security Headers (Production)

```python
SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.business.commerce.cart

# With coverage
coverage run manage.py test
coverage report
```

---

## 📈 Performance Optimizations

| Optimization | Implementation |
|--------------|----------------|
| **Database** | Connection pooling, Query optimization, Indexes |
| **Caching** | Redis for sessions, API responses |
| **Async** | Celery for emails, notifications, cleanup |
| **Aggregation** | `Sum()`, `Count()` thay vì Python loops |
| **Locking** | `select_for_update()` với `order_by('id')` tránh deadlock |
| **F() Expressions** | Atomic inventory updates |

---

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 👨‍💻 Tác giả

**Nghia Nguyen** - [@33nghia2001](https://github.com/33nghia2001)

---

## 🙏 Acknowledgments

- [Django REST Framework](https://www.django-rest-framework.org/)
- [Next.js](https://nextjs.org/)
- [Turborepo](https://turbo.build/)
- [Cloudflare R2](https://developers.cloudflare.com/r2/)

---

<div align="center">

**⭐ Star this repo if you find it helpful! ⭐**

Made with ❤️ in Vietnam 🇻🇳

</div>

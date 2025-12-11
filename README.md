# 🦉 OWLS Marketplace

> **O**nline **W**orld of **L**uxury **S**hopping - Nền tảng thương mại điện tử đa người bán thế hệ mới

**OWLS** là một nền tảng thương mại điện tử đa người bán (Multi-vendor Marketplace) hiện đại, được xây dựng với kiến trúc Headless hoàn chỉnh: Backend mạnh mẽ với **Django REST Framework** và Frontend tối ưu SEO với **React Router v7** (SSR).

[![Project Status](https://img.shields.io/badge/Status-In%20Development-orange?style=for-the-badge)](https://github.com/33nghia2001/owls)
[![Backend](https://img.shields.io/badge/Backend-Django%20DRF-092E20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![Frontend](https://img.shields.io/badge/Frontend-React%20Router%20v7-61DAFB?style=for-the-badge&logo=react)](https://reactrouter.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)

## ✨ Highlights

- 🚀 **Modern Tech Stack** - Django 5 + React Router v7 với SSR
- 🔐 **Enterprise Security** - JWT, WebSocket Auth, Rate Limiting
- 💳 **Multi-Payment** - Stripe (Global) + VNPay (Vietnam) + COD
- 💬 **Real-time Chat** - WebSocket customer-vendor messaging
- 📊 **Advanced Analytics** - Dashboard cho vendors và admin
- 🎨 **Beautiful UI** - Tailwind CSS với dark mode support
- 🌐 **SEO Optimized** - Server-side rendering với React Router
- 📱 **Responsive Design** - Mobile-first approach

## 🎯 Tính năng chính

### 🛍️ Cho Khách hàng

<table>
<tr>
<td width="50%">

**Shopping Experience**
- 🛒 Smart Cart - Guest + User với auto-merge
- 🔍 Advanced Search - Filter theo category, brand, price
- ❤️ Wishlist - Quản lý sản phẩm yêu thích với thống kê
- ⭐ Reviews - Đánh giá với hình ảnh (verified only)
- 📱 Responsive - Mobile-first design

</td>
<td width="50%">

**Checkout & Orders**
- 💳 Multi-Payment - Stripe + VNPay + COD
- 🎫 Coupons - Mã giảm giá linh hoạt
- 📦 Order Tracking - Real-time status updates
- 💬 Chat với Shop - WebSocket messaging
- 🔔 Notifications - Push alerts cho orders

</td>
</tr>
</table>

### 🏪 Cho Người bán (Vendor)

<table>
<tr>
<td width="50%">

**Shop Management**
- 📊 Analytics Dashboard - Revenue, orders, trends
- 📦 Inventory System - Stock tracking với variants
- 🎯 Product Management - Unlimited products với SEO
- 🏷️ Categories & Tags - Organize products

</td>
<td width="50%">

**Sales & Marketing**
- 🎫 Coupon System - Tạo mã giảm giá custom
- 💰 Payout Management - Auto-calculate với hold period
- 💬 Customer Chat - Direct messaging
- 📈 Performance Reports - Detailed analytics

</td>
</tr>
</table>

### 👨‍💼 Cho Admin

- 👥 **User Management** - Full CRUD cho customers, vendors, staff
- ✅ **Vendor Approval** - Review và approve vendor applications
- 📈 **Platform Analytics** - System-wide statistics và reports
- 🏷️ **Category Management** - MPTT tree structure
- 💸 **Refund System** - Handle Stripe/VNPay refunds
- 🔧 **System Config** - Platform settings và configurations

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

### Backend Infrastructure

| Category | Technologies |
|----------|-------------|
| **Core** | Python 3.12, Django 5.x, Django REST Framework |
| **Real-time** | Django Channels, WebSocket, Redis Channels Layer |
| **Database** | PostgreSQL (Aiven Cloud), Redis (Cache + Broker) |
| **Background Jobs** | Celery with retry mechanism, Celery Beat |
| **Authentication** | Django SimpleJWT, JWT tokens with refresh |
| **Payments** | Stripe API, VNPay Gateway, IPN/Webhook handling |
| **Media** | Cloudinary (images), django-storages |
| **API Docs** | drf-spectacular (OpenAPI 3.0), Swagger UI |
| **Security** | bleach (XSS prevention), rate limiting |
| **Utilities** | django-money, django-mptt, django-filter |

### Frontend Stack

| Category | Technologies |
|----------|-------------|
| **Framework** | React Router v7 (SSR), React 18 |
| **Language** | TypeScript 5.0 |
| **Styling** | Tailwind CSS 3.x, Framer Motion |
| **State** | Zustand, React Query (planned) |
| **Build** | Vite, ESBuild |
| **UI Components** | Radix UI, Lucide Icons |
| **Forms** | React Hook Form (planned) |

### DevOps & Tools

- **Version Control**: Git + GitHub
- **Code Quality**: ESLint, Prettier, Black, isort
- **Testing**: pytest (backend), Vitest (frontend - planned)
- **Container**: Docker (planned)
- **CI/CD**: GitHub Actions (planned)

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
│   │   ├── settings.py     # Main configuration
│   │   ├── urls.py         # URL routing
│   │   ├── asgi.py         # ASGI config for Channels
│   │   ├── wsgi.py         # WSGI config for production
│   │   └── validators.py   # Custom password validators
│   ├── requirements.txt    # Python dependencies
│   └── manage.py           # Django management commands
├── frontend/
│   ├── app/
│   │   ├── routes/         # React Router v7 pages (file-based routing)
│   │   │   ├── home.tsx                    # Landing page
│   │   │   ├── products/
│   │   │   │   ├── index.tsx               # Products listing
│   │   │   │   └── [slug].tsx              # Product detail
│   │   │   ├── cart.tsx                    # Shopping cart
│   │   │   ├── checkout.tsx                # Checkout process
│   │   │   ├── wishlist.tsx                # Wishlist management
│   │   │   ├── vendors/
│   │   │   │   ├── index.tsx               # Vendors listing
│   │   │   │   └── [slug].tsx              # Vendor profile
│   │   │   ├── account/
│   │   │   │   ├── profile.tsx             # User profile
│   │   │   │   ├── orders.tsx              # Order history
│   │   │   │   └── settings.tsx            # Account settings
│   │   │   └── auth/
│   │   │       ├── login.tsx               # Login page
│   │   │       └── register.tsx            # Registration
│   │   ├── components/         # Reusable React components
│   │   │   ├── layout/                     # Layout components
│   │   │   │   ├── header.tsx
│   │   │   │   ├── footer.tsx
│   │   │   │   └── sidebar.tsx
│   │   │   ├── product/                    # Product-related components
│   │   │   │   ├── product-card.tsx
│   │   │   │   ├── product-grid.tsx
│   │   │   │   └── product-filters.tsx
│   │   │   ├── cart/                       # Cart components
│   │   │   └── ui/                         # UI primitives (buttons, inputs, etc.)
│   │   ├── lib/                # Utilities and configurations
│   │   │   ├── services/                   # API service layer
│   │   │   │   ├── api.ts                  # Axios instance
│   │   │   │   ├── products.ts
│   │   │   │   ├── auth.ts
│   │   │   │   └── index.ts
│   │   │   ├── stores/                     # Zustand state stores
│   │   │   │   ├── auth.ts                 # Auth state
│   │   │   │   └── cart.ts                 # Cart state
│   │   │   ├── types/                      # TypeScript type definitions
│   │   │   │   └── index.ts
│   │   │   └── utils/                      # Helper functions
│   │   │       └── index.ts                # formatPrice, cn, etc.
│   │   ├── root.tsx            # Root layout component
│   │   ├── routes.ts           # Route configuration
│   │   └── app.css             # Global styles
│   ├── public/                 # Static assets
│   │   ├── favicon.ico
│   │   └── images/
│   ├── .eslintrc.json          # ESLint configuration
│   ├── tsconfig.json           # TypeScript configuration
│   ├── vite.config.ts          # Vite build configuration
│   ├── react-router.config.ts  # React Router v7 config
│   ├── tailwind.config.js      # Tailwind CSS configuration
│   └── package.json            # NPM dependencies and scripts
├── .gitignore
├── package.json                # Root package.json (workspace)
└── README.md                   # Project documentation
```

## � Screenshots

> Coming soon - UI screenshots sẽ được cập nhật

## 🚀 Getting Started

### 📋 Prerequisites

Make sure you have these installed:

- **Python** 3.10+ ([Download](https://www.python.org/downloads/))
- **Node.js** 18+ ([Download](https://nodejs.org/))
- **PostgreSQL** 14+ (hoặc cloud database như [Aiven](https://aiven.io/))
- **Redis** 6+ (hoặc [Redis Cloud](https://redis.com/))
- **Git** ([Download](https://git-scm.com/downloads))

### 🔧 Backend Setup

**1. Clone và setup môi trường**

```bash
# Clone repository
git clone https://github.com/33nghia2001/owls.git
cd owls

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# MacOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

**2. Cấu hình Database và Environment**

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit .env file với credentials của bạn
# - Database URL (PostgreSQL)
# - Redis URL
# - Stripe keys
# - VNPay credentials
# - Email settings
```

**3. Chạy migrations và tạo superuser**

```bash
cd backend

# Apply database migrations
python manage.py migrate

# Create superuser for admin panel
python manage.py createsuperuser

# (Optional) Load sample data
python manage.py loaddata fixtures/sample_data.json
```

**4. Start development server**

```bash
# HTTP only (simpler, no WebSocket)
python manage.py runserver

# OR with WebSocket support (recommended for full features)
daphne -b 127.0.0.1 -p 8000 backend.asgi:application
```

**5. (Optional) Start background workers**

Mở terminals riêng:

```bash
# Terminal 2: Celery Worker (for async tasks)
cd backend
celery -A backend worker -l info

# Terminal 3: Celery Beat (for scheduled tasks)
cd backend
celery -A backend beat -l info
```

### 🎨 Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server (with HMR)
npm run dev

# Build for production
npm run build
```

### 🐳 Docker Setup (Alternative - Coming Soon)

```bash
# Start all services with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (SSR)                        │
│           React Router v7 + TypeScript + Tailwind            │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API
                         │ WebSocket
┌────────────────────────┴────────────────────────────────────┐
│                      Backend (Django)                        │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐  ┌──────────┐ │
│  │ REST API │  │WebSocket │  │   Celery   │  │  Admin   │ │
│  │   (DRF)  │  │(Channels)│  │  Workers   │  │  Panel   │ │
│  └────┬─────┘  └────┬─────┘  └─────┬──────┘  └────┬─────┘ │
└───────┼─────────────┼──────────────┼──────────────┼────────┘
        │             │              │              │
┌───────┴─────────────┴──────────────┴──────────────┴────────┐
│                     Data Layer                               │
│  ┌──────────────┐  ┌──────────┐  ┌────────────────────┐   │
│  │  PostgreSQL  │  │  Redis   │  │  Cloudinary (CDN)  │   │
│  │  (Database)  │  │ (Cache)  │  │  (Media Storage)   │   │
│  └──────────────┘  └──────────┘  └────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
        │                    │
┌───────┴────────┐  ┌────────┴──────────┐
│  Stripe API    │  │   VNPay Gateway   │
│  (Payments)    │  │   (Payments VN)   │
└────────────────┘  └───────────────────┘
```

## 📚 API Documentation

Sau khi chạy backend server, truy cập các tài liệu sau:

| Resource | URL | Description |
|----------|-----|-------------|
| **Swagger UI** | http://localhost:8000/api/docs/ | Interactive API documentation |
| **ReDoc** | http://localhost:8000/api/redoc/ | Clean API documentation |
| **Admin Panel** | http://localhost:8000/admin/ | Django admin interface |
| **Frontend** | http://localhost:5173/ | React application |

## 🔑 Environment Variables

Tạo file `.env` trong thư mục `backend/` với cấu hình sau:

```env
# ============================================
# Django Core Settings
# ============================================
SECRET_KEY=your-secret-key-here  # Generate: python -c "import secrets; print(secrets.token_urlsafe(50))"
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173

# Frontend URL (for payment callbacks and redirects)
FRONTEND_URL=http://localhost:5173

# ============================================
# Database Configuration
# ============================================
DATABASE_URL=postgresql://user:password@host:5432/dbname
# Example: postgresql://owls_user:mypassword@localhost:5432/owls_db
# Or Aiven: postgresql://user:pass@host.aivencloud.com:12345/dbname?sslmode=require

# ============================================
# Redis Configuration
# ============================================
REDIS_URL=redis://localhost:6379/0
# Or Redis Cloud: redis://default:password@host:port

# ============================================
# Email Settings (for notifications)
# ============================================
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=OWLS Marketplace <noreply@owls.com>

# ============================================
# Stripe Payment (International)
# ============================================
STRIPE_SECRET_KEY=sk_test_51...  # Get from: https://dashboard.stripe.com/test/apikeys
STRIPE_PUBLISHABLE_KEY=pk_test_51...
STRIPE_WEBHOOK_SECRET=whsec_...  # From Stripe webhook settings

# ============================================
# VNPay Payment (Vietnam)
# ============================================
VNPAY_TMN_CODE=YOUR_TMN_CODE
VNPAY_HASH_SECRET=YOUR_HASH_SECRET
VNPAY_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
VNPAY_RETURN_URL=http://localhost:8000/api/payments/vnpay_return/
VNPAY_IPN_URL=http://localhost:8000/api/payments/vnpay_ipn/

# ============================================
# Cloudinary (Media Storage - Optional)
# ============================================
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# ============================================
# Security Settings (Production)
# ============================================
# Uncomment for production:
# SECURE_SSL_REDIRECT=True
# SESSION_COOKIE_SECURE=True
# CSRF_COOKIE_SECURE=True
# SECURE_HSTS_SECONDS=31536000
```

> **⚠️ Security Note**: Không commit file `.env` lên Git! File này đã được thêm vào `.gitignore`.

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

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards

- **Backend**: Follow PEP 8, use Black formatter
- **Frontend**: Use ESLint + Prettier, follow Airbnb style guide
- **Commits**: Use conventional commits (feat, fix, docs, etc.)

## 🐛 Bug Reports & Feature Requests

Sử dụng [GitHub Issues](https://github.com/33nghia2001/owls/issues) để báo cáo bugs hoặc đề xuất tính năng mới.

## 📝 Roadmap

- [ ] Implement React Query for data fetching
- [ ] Add unit tests (pytest + Vitest)
- [ ] Docker containerization
- [ ] CI/CD with GitHub Actions
- [ ] Social authentication (Google, Facebook)
- [ ] Product comparison feature
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native)
- [ ] Multi-language support (i18n)

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Nghia Hoang**
- GitHub: [@33nghia2001](https://github.com/33nghia2001)
- Email: contact@owls.com

## 🙏 Acknowledgments

- Django REST Framework team for excellent API framework
- React Router team for amazing SSR capabilities
- Tailwind CSS for beautiful utility-first CSS
- All open-source contributors

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

Made with ❤️ by [Nghia Hoang](https://github.com/33nghia2001)

</div>

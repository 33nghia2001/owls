# OWLS Marketplace

**OWLS** là một nền tảng thương mại điện tử đa người bán (Multi-vendor Marketplace) hiện đại, được xây dựng với kiến trúc Headless: Backend mạnh mẽ bằng **Django** và Frontend tối ưu SEO bằng **Remix**.

![Project Status](https://img.shields.io/badge/Status-In%20Development-orange)
![Backend](https://img.shields.io/badge/Backend-Django%20Rest%20Framework-green)
![Frontend](https://img.shields.io/badge/Frontend-Remix%20Run-blue)

## Tính năng chính

* **Multi-vendor System:** Cho phép nhiều người bán đăng ký, mở shop và quản lý kho hàng riêng.
* **Order Splitting:** Tự động tách đơn hàng lớn thành các đơn nhỏ theo từng người bán.
* **Product Variants:** Hỗ trợ sản phẩm nhiều biến thể (Màu sắc, Kích thước, SKU).
* **Smart Payments:** Tích hợp Stripe (Quốc tế) và VNPay (Việt Nam).
* **Real-time:** Thông báo đơn hàng và Chat thời gian thực.
* **Optimization:** Sử dụng Redis Cache và Celery cho tác vụ nền.

## Công nghệ sử dụng (Tech Stack)

### Backend
* **Language:** Python 3.10+
* **Framework:** Django 5.x, Django REST Framework (DRF)
* **Database:** PostgreSQL (Production) / SQLite (Dev)
* **Authentication:** JWT (JSON Web Tokens)
* **Async Tasks:** Celery + Redis
* **Storage:** AWS S3 (Media files)
* **Documentation:** Swagger / Redoc (drf-spectacular)

### Frontend (Dự kiến)
* **Framework:** Remix (React)
* **Styling:** TailwindCSS
* **State Management:** React Context / Zustand

---

## Hướng dẫn cài đặt (Development)

Làm theo các bước sau để chạy dự án trên máy cục bộ (Localhost).

### 1. Yêu cầu tiên quyết
* Python 3.10 trở lên
* Node.js 18 trở lên
* Redis (để chạy Celery)
* Git

### 2. Cài đặt Backend

```bash
# 1. Clone dự án
git clone [https://github.com/33nghia2001/owls.git](https://github.com/33nghia2001/owls.git)
cd owls

# 2. Tạo môi trường ảo (Virtual Environment)
python -m venv .venv

# 3. Kích hoạt môi trường ảo
# Windows:
.venv\Scripts\activate
# MacOS/Linux:
source .venv/bin/activate

# 4. Cài đặt thư viện
pip install -r backend/requirements.txt

# 5. Cấu hình biến môi trường
# Tạo file .env ngang hàng với file manage.py và điền thông tin (xem mẫu bên dưới)

# 6. Chạy Migration (Tạo database)
cd backend
python manage.py migrate

# 7. Tạo Superuser (Admin)
python manage.py createsuperuser

# 8. Khởi chạy Server
python manage.py runserver
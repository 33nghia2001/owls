"""
Django settings for Owls E-commerce Platform.
=============================================
Production-ready configuration with security best practices.
Author: Owls Development Team
Version: 1.0.0
"""

from pathlib import Path
from datetime import timedelta
import os
import environ

# =============================================================================
# ENVIRONMENT CONFIGURATION
# =============================================================================
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    REDIS_URL=(str, 'redis://localhost:6379/0'),
    CELERY_BROKER_URL=(str, 'redis://localhost:6379/1'),
    EMAIL_BACKEND=(str, 'django.core.mail.backends.console.EmailBackend'),
)

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# =============================================================================
# CORE SETTINGS
# =============================================================================
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Site configuration
SITE_NAME = 'Owls'
SITE_DOMAIN = env('SITE_DOMAIN', default='owls.asia')
FRONTEND_URL = env('FRONTEND_URL', default='http://localhost:3000')
ADMIN_URL = env('ADMIN_URL', default='http://localhost:5173')

# =============================================================================
# APPLICATION DEFINITION
# =============================================================================
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
]

THIRD_PARTY_APPS = [
    # REST Framework & Authentication
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    
    # Task Queue & Caching
    'django_celery_beat',
    'django_celery_results',
    'django_redis',
    
    # Development & Documentation
    'drf_spectacular',
    'drf_spectacular_sidecar',
    
    # Storage & Media
    'storages',
    
    # Security & Monitoring
    'axes',  # Brute force protection
]

# =============================================================================
# OWLS APPS - 4 PILLARS ARCHITECTURE
# =============================================================================
LOCAL_APPS = [
    # -------------------------------------------------------------------------
    # 1. BASE PILLAR - Core Infrastructure & Operations
    # -------------------------------------------------------------------------
    # Core Services
    'apps.base.core.users.apps.UsersConfig',
    'apps.base.core.administration.apps.AdministrationConfig',
    'apps.base.core.notifications.apps.NotificationsConfig',
    'apps.base.core.analytics.apps.AnalyticsConfig',
    'apps.base.core.locations.apps.LocationsConfig',
    'apps.base.core.system.apps.SystemConfig',
    'apps.base.core.uploads.apps.UploadsConfig',
    # Operations
    'apps.base.operations.support.apps.SupportConfig',
    'apps.base.operations.audit_logs.apps.AuditLogsConfig',
    # Risk Management
    'apps.base.risk.kyc.apps.KycConfig',
    'apps.base.risk.content_moderation.apps.ContentModerationConfig',
    'apps.base.risk.fraud_detection.apps.FraudDetectionConfig',

    # -------------------------------------------------------------------------
    # 2. BUSINESS PILLAR - Commerce & Finance
    # -------------------------------------------------------------------------
    # Commerce
    'apps.business.commerce.products.apps.ProductsConfig',
    'apps.business.commerce.cart.apps.CartConfig',
    'apps.business.commerce.orders.apps.OrdersConfig',
    'apps.business.commerce.payments.apps.PaymentsConfig',
    'apps.business.commerce.refunds.apps.RefundsConfig',
    # Finance
    'apps.business.finance.wallets.apps.WalletsConfig',
    'apps.business.finance.invoices.apps.InvoicesConfig',
    'apps.business.finance.taxes.apps.TaxesConfig',
    'apps.business.finance.credit.apps.CreditConfig',
    # Partners
    'apps.business.partners.vendors.apps.VendorsConfig',
    'apps.business.partners.inventory.apps.InventoryConfig',
    'apps.business.partners.shipping.apps.ShippingConfig',
    'apps.business.partners.drivers.apps.DriversConfig',

    # -------------------------------------------------------------------------
    # 3. CLIENT PILLAR - Customer Experience
    # -------------------------------------------------------------------------
    # Experience
    'apps.client.experience.reviews.apps.ReviewsConfig',
    'apps.client.experience.coupons.apps.CouponsConfig',
    'apps.client.experience.wishlist.apps.WishlistConfig',
    'apps.client.experience.messaging.apps.MessagingConfig',
    'apps.client.experience.loyalty.apps.LoyaltyConfig',
    # Content
    'apps.client.content.blog.apps.BlogConfig',
    'apps.client.content.banners.apps.BannersConfig',
    'apps.client.content.pages.apps.PagesConfig',
    # Entertainment
    'apps.client.entertainment.broadcasting.apps.BroadcastingConfig',
    'apps.client.entertainment.gamification.apps.GamificationConfig',
    'apps.client.entertainment.social.apps.SocialConfig',

    # -------------------------------------------------------------------------
    # 4. GROWTH PILLAR - Marketing & Intelligence
    # -------------------------------------------------------------------------
    # Marketing
    'apps.growth.marketing.advertisements.apps.AdvertisementsConfig',
    'apps.growth.marketing.campaigns.apps.CampaignsConfig',
    'apps.growth.marketing.affiliates.apps.AffiliatesConfig',
    'apps.growth.marketing.seo.apps.SeoConfig',
    # Intelligence
    'apps.growth.intelligence.search.apps.SearchConfig',
    'apps.growth.intelligence.recommendations.apps.RecommendationsConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# =============================================================================
# MIDDLEWARE CONFIGURATION
# =============================================================================
MIDDLEWARE = [
    # Security & CORS (must be first)
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files
    
    # Session & Common
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    
    # Security
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Third-party Security
    'axes.middleware.AxesMiddleware',  # Brute force protection
    
    # Custom Middleware
    # 'apps.base.core.system.middleware.RequestLoggingMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'
ASGI_APPLICATION = 'backend.asgi.application'

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DATABASES = {
    'default': env.db(),
}

# Database connection pooling (for production)
if not DEBUG:
    DATABASES['default']['CONN_MAX_AGE'] = 60
    DATABASES['default']['CONN_HEALTH_CHECKS'] = True

# =============================================================================
# CACHING CONFIGURATION
# =============================================================================
REDIS_URL = env('REDIS_URL')

# Check if Redis is available
def is_redis_available():
    """Check if Redis server is running."""
    try:
        import redis
        r = redis.from_url(REDIS_URL, socket_timeout=1)
        r.ping()
        return True
    except:
        return False

# Use Redis if available, otherwise fallback to local memory cache
if is_redis_available():
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'IGNORE_EXCEPTIONS': True,
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                },
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
            },
            'KEY_PREFIX': 'owls',
            'TIMEOUT': 300,  # 5 minutes default
        }
    }
    # Session backend using Redis
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
else:
    # Fallback to local memory cache for development
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'owls-cache',
        }
    }
    # Use database sessions when Redis is not available
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# =============================================================================
# AUTHENTICATION CONFIGURATION
# =============================================================================
AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # Brute force protection
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =============================================================================
# REST FRAMEWORK CONFIGURATION
# =============================================================================
REST_FRAMEWORK = {
    # Authentication
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    
    # Permissions
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    
    # Throttling (Rate Limiting)
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'login': '5/minute',
        'register': '3/minute',
    },
    
    # Filtering & Pagination
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    
    # Rendering
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    
    # Parsing
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    
    # Schema & Documentation
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    
    # Exception handling
    'EXCEPTION_HANDLER': 'apps.base.core.system.exceptions.custom_exception_handler',
    
    # Versioning
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1', 'v2'],
}

# =============================================================================
# JWT CONFIGURATION (RS256 - Asymmetric Keys)
# =============================================================================
# RS256 provides better security for distributed systems:
# - Only the backend holds the private key (signing)
# - Other services can verify tokens with public key only
# - No need to share SECRET_KEY across services

def load_key_from_file(path):
    """Load key from file path."""
    from pathlib import Path
    key_path = Path(path)
    if key_path.exists():
        return key_path.read_text()
    return None

# Load RSA keys
JWT_PRIVATE_KEY = env('JWT_PRIVATE_KEY', default='')
JWT_PUBLIC_KEY = env('JWT_PUBLIC_KEY', default='')

# If not in env, try loading from files
if not JWT_PRIVATE_KEY:
    JWT_PRIVATE_KEY = load_key_from_file(BASE_DIR / 'keys' / 'private.pem') or ''
if not JWT_PUBLIC_KEY:
    JWT_PUBLIC_KEY = load_key_from_file(BASE_DIR / 'keys' / 'public.pem') or ''

# Fallback to HS256 if keys not found
USE_RS256 = bool(JWT_PRIVATE_KEY and JWT_PUBLIC_KEY)

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    # RS256 (asymmetric) or HS256 (symmetric) based on key availability
    'ALGORITHM': 'RS256' if USE_RS256 else 'HS256',
    'SIGNING_KEY': JWT_PRIVATE_KEY if USE_RS256 else SECRET_KEY,
    'VERIFYING_KEY': JWT_PUBLIC_KEY if USE_RS256 else None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=30),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
}

# =============================================================================
# SPECTACULAR (API DOCUMENTATION) CONFIGURATION
# =============================================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'Owls E-commerce API',
    'DESCRIPTION': 'Professional E-commerce Platform API Documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/v[0-9]',
    'TAGS': [
        {'name': 'Auth', 'description': 'Authentication & Authorization'},
        {'name': 'Users', 'description': 'User Management'},
        {'name': 'Products', 'description': 'Product Catalog'},
        {'name': 'Cart', 'description': 'Shopping Cart'},
        {'name': 'Orders', 'description': 'Order Management'},
        {'name': 'Payments', 'description': 'Payment Processing'},
        {'name': 'Vendors', 'description': 'Vendor Management'},
    ],
    # Fix enum naming collisions
    'ENUM_NAME_OVERRIDES': {
        'OrderStatusEnum': 'apps.business.commerce.orders.models.Order.Status',
        'PaymentStatusEnum': 'apps.business.commerce.payments.models.Payment.Status',
        'VendorStatusEnum': 'apps.business.partners.vendors.models.Vendor.Status',
        'ProductStatusEnum': 'apps.business.commerce.products.models.Product.Status',
        'OrderItemStatusEnum': 'apps.business.commerce.orders.models.OrderItem.status',
    },
}

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================
LANGUAGE_CODE = env('LANGUAGE_CODE', default='vi')
TIME_ZONE = env('TIME_ZONE', default='Asia/Ho_Chi_Minh')
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [BASE_DIR / 'locale']

# =============================================================================
# STATIC & MEDIA FILES
# =============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# WhiteNoise for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# =============================================================================
# CLOUDFLARE R2 STORAGE CONFIGURATION
# =============================================================================
USE_S3 = env.bool('USE_S3', default=False)

if USE_S3:
    # Cloudflare R2 settings (S3-compatible)
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='auto')
    
    # Cloudflare R2 specific settings
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None  # R2 doesn't support ACLs
    AWS_QUERYSTRING_AUTH = False  # Use public URLs
    AWS_S3_VERIFY = True
    
    # Custom domain for public access (optional)
    AWS_S3_CUSTOM_DOMAIN = env('AWS_S3_CUSTOM_DOMAIN', default='')
    
    # Cache control
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',  # 1 day cache
    }
    
    # Storage backends using custom Cloudflare R2 storage
    STORAGES = {
        'default': {
            'BACKEND': 'apps.base.core.uploads.storage.MediaStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }
    
    # Media URL
    if AWS_S3_CUSTOM_DOMAIN:
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
    else:
        # Use R2 public bucket URL (need to enable public access in R2 dashboard)
        # Or use Workers/Pages for custom domain
        MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/media/'
    
else:
    # Local storage for development
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }

# =============================================================================
# CORS CONFIGURATION
# =============================================================================
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # SECURITY: Load CORS origins from environment variable for flexibility
    # Format: comma-separated list of origins
    # Example: CORS_ALLOWED_ORIGINS=https://owls.asia,https://admin.owls.asia
    CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
        'https://owls.asia',
        'https://www.owls.asia',
        'https://admin.owls.asia',
        'https://seller.owls.asia',
        'https://api.owls.asia',
    ])

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# =============================================================================
# SECURITY SETTINGS (Production)
# =============================================================================
if not DEBUG:
    # HTTPS/SSL
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Session Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 days
    
    # CSRF Security
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = 'Lax'
    CSRF_TRUSTED_ORIGINS = [
        'https://owls.asia',
        'https://www.owls.asia',
        'https://admin.owls.asia',
        'https://seller.owls.asia',
    ]
    
    # Security Headers
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

# =============================================================================
# AXES CONFIGURATION (Brute Force Protection)
# =============================================================================
AXES_FAILURE_LIMIT = 5  # Lock after 5 failed attempts
AXES_COOLOFF_TIME = timedelta(minutes=30)  # Lock duration
# SECURITY FIX: Set to False to prevent low-and-slow brute force attacks
# When True, successful login resets the failure counter, allowing attackers
# to try 4 passwords, login with another account, and repeat indefinitely
AXES_RESET_ON_SUCCESS = False
AXES_LOCKOUT_TEMPLATE = None
AXES_LOCKOUT_URL = None
AXES_VERBOSE = True
# Lock by both username and IP address (prevents account enumeration)
AXES_LOCKOUT_PARAMETERS = ['username', 'ip_address']
# Use cache backend for better performance
AXES_HANDLER = 'axes.handlers.cache.AxesCacheHandler'

# =============================================================================
# CELERY CONFIGURATION (Background Tasks)
# =============================================================================
CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Celery Beat Schedule for periodic tasks
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Cleanup expired sessions daily at 3 AM
    'cleanup-expired-sessions': {
        'task': 'users.cleanup_expired_sessions',
        'schedule': crontab(hour=3, minute=0),
        'options': {'queue': 'maintenance'},
    },
    # Cleanup unverified users weekly on Sunday at 4 AM
    'cleanup-unverified-users': {
        'task': 'users.cleanup_unverified_users',
        'schedule': crontab(hour=4, minute=0, day_of_week='sunday'),
        'options': {'queue': 'maintenance'},
    },
    # Cleanup expired guest carts daily at 2 AM
    'cleanup-expired-carts': {
        'task': 'cart.cleanup_expired_carts',
        'schedule': crontab(hour=2, minute=0),
        'options': {'queue': 'maintenance'},
    },
    # Cancel unpaid orders every 5 minutes
    'cancel-unpaid-orders': {
        'task': 'orders.cancel_unpaid_orders',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
        'options': {'queue': 'maintenance'},
    },
}

# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================
EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='Owls <noreply@owls.asia>')

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'owls.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# =============================================================================
# SITE CONFIGURATION
# =============================================================================
SITE_ID = 1
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# FILE UPLOAD CONFIGURATION
# =============================================================================
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# =============================================================================
# CUSTOM SETTINGS - OWLS E-COMMERCE
# =============================================================================
OWLS_CONFIG = {
    'CURRENCY': 'VND',
    'CURRENCY_SYMBOL': '₫',
    'DEFAULT_COUNTRY': 'VN',
    'TAX_RATE': 0.10,  # 10% VAT
    'FREE_SHIPPING_THRESHOLD': 500000,  # VND
    'DEFAULT_SHIPPING_RATE': 30000,  # VND fallback shipping rate
    'MAX_CART_ITEMS': 50,
    'ORDER_ID_PREFIX': 'OWL',
    'VENDOR_COMMISSION_RATE': 0.15,  # 15%
    'POINTS_PER_VND': 0.001,  # 1 point per 1000 VND
    'PAYMENT_TIMEOUT_MINUTES': 30,  # Auto-cancel unpaid orders after 30 mins
    # Store/Warehouse Address (for shipping calculation)
    'STORE_PROVINCE': 'Hồ Chí Minh',
    'STORE_PROVINCE_CODE': '79',
    'STORE_DISTRICT': 'Quận 1',
    'STORE_DISTRICT_ID': 1442,
    'STORE_WARD_CODE': '21012',
}

# =============================================================================
# PAYMENT GATEWAYS CONFIGURATION
# =============================================================================

# VNPay Configuration
VNPAY_CONFIG = {
    'TMN_CODE': env('VNPAY_TMN_CODE', default=''),
    'HASH_SECRET': env('VNPAY_HASH_SECRET', default=''),
    'PAYMENT_URL': env('VNPAY_URL', default='https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'),
    'RETURN_URL': env('VNPAY_RETURN_URL', default='http://localhost:3000/payment/vnpay/return'),
    'API_URL': env('VNPAY_API_URL', default='https://sandbox.vnpayment.vn/merchant_webapi/api/transaction'),
    'VERSION': '2.1.0',
    'COMMAND': 'pay',
    'CURRENCY_CODE': 'VND',
    'LOCALE': 'vn',
}

# MoMo Configuration
MOMO_CONFIG = {
    'PARTNER_CODE': env('MOMO_PARTNER_CODE', default=''),
    'ACCESS_KEY': env('MOMO_ACCESS_KEY', default=''),
    'SECRET_KEY': env('MOMO_SECRET_KEY', default=''),
    'ENDPOINT': env('MOMO_ENDPOINT', default='https://test-payment.momo.vn/v2/gateway/api'),
    'RETURN_URL': env('MOMO_RETURN_URL', default='http://localhost:3000/payment/momo/return'),
    'NOTIFY_URL': env('MOMO_NOTIFY_URL', default='http://localhost:8000/api/v1/payments/webhook/momo/'),
    'REQUEST_TYPE': 'captureWallet',
}

# ZaloPay Configuration
ZALOPAY_CONFIG = {
    'APP_ID': env('ZALOPAY_APP_ID', default=''),
    'KEY1': env('ZALOPAY_KEY1', default=''),
    'KEY2': env('ZALOPAY_KEY2', default=''),
    'ENDPOINT': env('ZALOPAY_ENDPOINT', default='https://sb-openapi.zalopay.vn/v2'),
    'CALLBACK_URL': env('ZALOPAY_CALLBACK_URL', default='http://localhost:8000/api/v1/payments/webhook/zalopay/'),
}

# =============================================================================
# SHIPPING PROVIDERS CONFIGURATION
# =============================================================================

# Giao Hàng Nhanh (GHN)
GHN_CONFIG = {
    'TOKEN': env('GHN_TOKEN', default=''),
    'SHOP_ID': env('GHN_SHOP_ID', default=''),
    'BASE_URL': env('GHN_BASE_URL', default='https://online-gateway.ghn.vn/shiip/public-api'),
}

# Giao Hàng Tiết Kiệm (GHTK)
GHTK_CONFIG = {
    'TOKEN': env('GHTK_TOKEN', default=''),
    'BASE_URL': env('GHTK_BASE_URL', default='https://services.giaohangtietkiem.vn'),
}
from pathlib import Path
import os

from dotenv import load_dotenv
import dj_database_url

try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass


# Load environment variables from .env locally
load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent


# =========================
# SECURITY SETTINGS
# =========================

SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-local-dev-key")

DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".vercel.app",
]

# Add your real domain later if you have one:
# ALLOWED_HOSTS += [
#     "yourdomain.com",
#     "www.yourdomain.com",
# ]

CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
]

# Add your real domain later if you have one:
# CSRF_TRUSTED_ORIGINS += [
#     "https://yourdomain.com",
#     "https://www.yourdomain.com",
# ]

# Helps Django detect HTTPS correctly behind Vercel/proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# =========================
# DATABASE
# =========================

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# =========================
# FLUTTERWAVE
# =========================

FLUTTERWAVE_PUBLIC_KEY = os.environ.get("FLUTTERWAVE_PUBLIC_KEY")
FLUTTERWAVE_SECRET_KEY = os.environ.get("FLUTTERWAVE_SECRET_KEY")
FLUTTERWAVE_REDIRECT_URL = os.environ.get("FLUTTERWAVE_REDIRECT_URL")


# =========================
# EMAIL SETTINGS
# =========================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER or "webmaster@localhost",
)

EMAIL_TIMEOUT = 20


# =========================
# APPLICATIONS
# =========================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Project apps
    "customers",
    "cart",
    "payment.apps.PaymentConfig",

    # Third-party apps
    "social_django",
]


# =========================
# WEB PUSH / VAPID
# =========================

VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY", "")
VAPID_PUBLIC_KEY = os.environ.get("VAPID_PUBLIC_KEY", "")

VAPID_CLAIMS = {
    "sub": os.environ.get("VAPID_SUB", "mailto:abiolad267@gmail.com"),
}


# =========================
# MIDDLEWARE
# =========================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise must stay directly after SecurityMiddleware
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "social_django.middleware.SocialAuthExceptionMiddleware",
]


# =========================
# URLS / WSGI
# =========================

ROOT_URLCONF = "bridal_app.urls"

WSGI_APPLICATION = "bridal_app.wsgi.application"


# =========================
# TEMPLATES
# =========================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        # Your templates are inside app/template folders based on your structure,
        # so APP_DIRS=True is enough.
        "DIRS": [],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",

                "cart.context_processors.cart",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "customers.context_processors.unshipped_orders",
                "payment.context_processors.nav_notifications",
            ],
        },
    },
]


# =========================
# PASSWORD VALIDATION
# =========================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# =========================
# INTERNATIONALIZATION
# =========================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# =========================
# STATIC FILES
# =========================

STATIC_URL = "/static/"

# This is your source static folder:
# bridal_app/static/
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# collectstatic will copy files here
STATIC_ROOT = BASE_DIR / "staticfiles"

# Important:
# Use CompressedStaticFilesStorage for now, not Manifest storage.
# Manifest storage crashes when a template references a missing file like:
# {% static 'assets/img/favicon.png' %}
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}


# =========================
# MEDIA FILES
# =========================

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# =========================
# DEFAULT PRIMARY KEY
# =========================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================
# SOCIAL AUTH
# =========================

AUTHENTICATION_BACKENDS = [
    "social_core.backends.facebook.FacebookOAuth2",
    "social_core.backends.instagram.InstagramOAuth2",
    "django.contrib.auth.backends.ModelBackend",
]

LOGIN_URL = "signin"
LOGIN_REDIRECT_URL = "home"
LOGOUT_URL = "signout"
LOGOUT_REDIRECT_URL = "login"


# Facebook login
SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get("SOCIAL_AUTH_FACEBOOK_KEY")
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get("SOCIAL_AUTH_FACEBOOK_SECRET")

SOCIAL_AUTH_FACEBOOK_SCOPE = [
    "email",
    "user_link",
]

SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    "fields": "id, name, email, picture.type(large), link",
}

SOCIAL_AUTH_FACEBOOK_EXTRA_DATA = [
    ("name", "name"),
    ("email", "email"),
    ("picture", "picture"),
    ("link", "profile_url"),
]


# Instagram login
SOCIAL_AUTH_INSTAGRAM_KEY = os.environ.get("SOCIAL_AUTH_INSTAGRAM_KEY")
SOCIAL_AUTH_INSTAGRAM_SECRET = os.environ.get("SOCIAL_AUTH_INSTAGRAM_SECRET")

SOCIAL_AUTH_INSTAGRAM_EXTRA_DATA = [
    ("user", "user"),
]
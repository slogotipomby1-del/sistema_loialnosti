from pathlib import Path
import os
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parent.parent


def parse_env_list(raw_value: str) -> list[str]:
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def parse_database_url(database_url: str, base_dir: Path | None = None) -> dict:
    current_base_dir = base_dir or BASE_DIR
    if not database_url:
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": current_base_dir / "db.sqlite3",
        }

    parsed = urlparse(database_url)
    if parsed.scheme not in {"postgres", "postgresql"}:
        raise ValueError(f"Unsupported database scheme: {parsed.scheme}")

    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": parsed.path.lstrip("/"),
        "USER": parsed.username or "",
        "PASSWORD": parsed.password or "",
        "HOST": parsed.hostname or "",
        "PORT": parsed.port or 5432,
    }


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = parse_env_list(os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost"))
CSRF_TRUSTED_ORIGINS = parse_env_list(os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", ""))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.adminpanel",
    "apps.users",
    "apps.referrals",
    "apps.bonuses",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": parse_database_url(os.getenv("DATABASE_URL", ""), base_dir=BASE_DIR)
}

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Minsk"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

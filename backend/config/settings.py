import os
import re
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() == "true"


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-insecure-key")
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = [host.strip() for host in os.getenv(
    "DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "rest_framework",
    "trips",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# The app is stateless: routes and weather come from APIs, so there is no database.
DATABASES = {}

TIME_ZONE = "UTC"
USE_TZ = True

STATIC_URL = "static/"

# In production the built React app lives in backend/frontend_dist and is served at "/".
FRONTEND_DIST = BASE_DIR / "frontend_dist"
if FRONTEND_DIST.exists():
    WHITENOISE_ROOT = FRONTEND_DIST
    WHITENOISE_INDEX_FILE = True


def WHITENOISE_IMMUTABLE_FILE_TEST(path, url):
    # Vite puts a content hash in asset names (index-a1b2c3d4.js), so those can be cached forever.
    return re.match(r"^.+[.-][0-9a-zA-Z_-]{8,12}\..+$", url)


REDIS_URL = os.getenv("REDIS_URL", "")
if REDIS_URL:
    CACHES = {"default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": REDIS_URL}}
else:
    CACHES = {"default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "UNAUTHENTICATED_USER": None,
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"anon": "120/min"},
    "EXCEPTION_HANDLER": "trips.exception_handler.api_exception_handler",
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"trips": {"handlers": ["console"], "level": "INFO"}},
}

# --- App settings ---
TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY", "")
# optional; the free tier needs no key
OPEN_METEO_API_KEY = os.getenv("OPEN_METEO_API_KEY", "")
GEOCODE_COUNTRY_SET = os.getenv("GEOCODE_COUNTRY_SET", "US,CA")
USE_FAKE_PROVIDERS = env_bool("USE_FAKE_PROVIDERS", False)
WEATHER_FROM_BROWSER = env_bool("WEATHER_FROM_BROWSER", False)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

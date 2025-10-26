# config.py
import os
from datetime import timedelta

class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # DB: local uses SQLite; Render sets DATABASE_URL to Postgres
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or (
        "sqlite:///" + os.path.join(os.getcwd(), "instance", "app.sqlite")
    )

    # CORS for /api only; set comma-separated origins in env
    CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "*").split(",")]

    # Flask-Limiter (simple memory store is fine for single instance)
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")

    # Caching
    CACHE_TYPE = os.environ.get("CACHE_TYPE", "SimpleCache")  # "SimpleCache" / "NullCache" / "RedisCache"
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", "300"))

    # Security headers (Talisman)
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Content Security Policy — relax if you use inline scripts/styles
    CSP = {
        "default-src": ["'self'"],
        "img-src": ["'self'", "data:"],
        "style-src": ["'self'", "'unsafe-inline'"],
        "script-src": ["'self'", "'unsafe-inline'"],
        "font-src": ["'self'", "data:"],
    }

class DevelopmentConfig(BaseConfig):
    DEBUG = True

class ProductionConfig(BaseConfig):
    DEBUG = False

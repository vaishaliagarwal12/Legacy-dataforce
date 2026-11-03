import os
import secrets
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Explicitly load .env from the project root directory
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)


class Config:
    """Base application configuration loaded strictly from environment variables."""

    # Flask Settings
    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = False
    PORT = int(os.getenv("PORT", 5000))

    # Secret Key for session signing & CSRF protection
    # Dynamically generates a secure random key if not explicitly set via environment
    _secret_key = os.getenv("SECRET_KEY")
    if not _secret_key:
        _secret_key = secrets.token_hex(32)
        if ENV == "production":
            logger.warning("SECRET_KEY not set in environment! Generated ephemeral key for session security.")
    SECRET_KEY = _secret_key

    # Session & Cookie Security (OWASP Recommended)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "0") in ("1", "true", "True")
    PERMANENT_SESSION_LIFETIME = int(os.getenv("SESSION_LIFETIME_SECONDS", 7200))  # 2 hours default

    # MySQL Settings
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "placement_db")
    MYSQL_CHARSET = os.getenv("MYSQL_CHARSET", "utf8mb4")
    MYSQL_CONNECT_TIMEOUT = int(os.getenv("MYSQL_CONNECT_TIMEOUT", 5))

    # Dedicated Read-Only User for Custom SQL Execution
    MYSQL_READONLY_USER = os.getenv("MYSQL_READONLY_USER", "placement_readonly")
    MYSQL_READONLY_PASSWORD = os.getenv("MYSQL_READONLY_PASSWORD", "")

    # CSRF Protection toggle
    CSRF_ENABLED = True

    @classmethod
    def get_db_config(cls) -> dict:
        """Returns database connection parameters as a dictionary for PyMySQL."""
        return {
            "host": cls.MYSQL_HOST,
            "port": cls.MYSQL_PORT,
            "user": cls.MYSQL_USER,
            "password": cls.MYSQL_PASSWORD,
            "database": cls.MYSQL_DB,
            "charset": cls.MYSQL_CHARSET,
            "connect_timeout": cls.MYSQL_CONNECT_TIMEOUT,
            "autocommit": False,
        }

    @classmethod
    def get_readonly_db_config(cls) -> dict:
        """Returns database connection parameters for dedicated read-only execution."""
        return {
            "host": cls.MYSQL_HOST,
            "port": cls.MYSQL_PORT,
            "user": cls.MYSQL_READONLY_USER,
            "password": cls.MYSQL_READONLY_PASSWORD,
            "database": cls.MYSQL_DB,
            "charset": cls.MYSQL_CHARSET,
            "connect_timeout": cls.MYSQL_CONNECT_TIMEOUT,
            "autocommit": False,
        }


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    SESSION_COOKIE_SECURE = False
    CSRF_ENABLED = False
    MYSQL_DB = os.getenv("MYSQL_TEST_DB", "placement_db")


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

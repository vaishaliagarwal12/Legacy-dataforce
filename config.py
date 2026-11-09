import os
import secrets
import logging
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Explicitly load .env from the project root directory
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)


def get_env_int(
    key: str,
    default: int,
    min_val: Optional[int] = None,
    max_val: Optional[int] = None,
) -> int:
    """Safely retrieves an integer from environment variables with bounds checking."""
    val = os.getenv(key)
    if val is None or not str(val).strip():
        return default
    try:
        parsed = int(str(val).strip())
        if min_val is not None and parsed < min_val:
            logger.warning(
                "Config %s=%s below minimum %s; defaulting to %s",
                key,
                parsed,
                min_val,
                default,
            )
            return default
        if max_val is not None and parsed > max_val:
            logger.warning(
                "Config %s=%s exceeds maximum %s; defaulting to %s",
                key,
                parsed,
                max_val,
                default,
            )
            return default
        return parsed
    except (ValueError, TypeError):
        logger.warning(
            "Config %s invalid integer '%s'; defaulting to %s",
            key,
            val,
            default,
        )
        return default


def get_env_float(
    key: str,
    default: float,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
) -> float:
    """Safely retrieves a float from environment variables with bounds checking."""
    val = os.getenv(key)
    if val is None or not str(val).strip():
        return default
    try:
        parsed = float(str(val).strip())
        if min_val is not None and parsed < min_val:
            logger.warning(
                "Config %s=%s below minimum %s; defaulting to %s",
                key,
                parsed,
                min_val,
                default,
            )
            return default
        if max_val is not None and parsed > max_val:
            logger.warning(
                "Config %s=%s exceeds maximum %s; defaulting to %s",
                key,
                parsed,
                max_val,
                default,
            )
            return default
        return parsed
    except (ValueError, TypeError):
        logger.warning(
            "Config %s invalid float '%s'; defaulting to %s",
            key,
            val,
            default,
        )
        return default


class Config:
    """Base application configuration loaded strictly from environment variables."""

    # Flask Settings
    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = False
    PORT = int(os.getenv("PORT", "5000"))

    # Database Health Indicator Cache TTL (seconds)
    DB_HEALTH_CACHE_TTL = get_env_float(
        "DB_HEALTH_CACHE_TTL_SECONDS", 10.0, min_val=0.5, max_val=3600.0
    )

    # Custom SQL Execution Limits
    SQL_REPORT_MAX_ROWS = get_env_int("SQL_REPORT_MAX_ROWS", 500, min_val=1, max_val=10000)
    SQL_REPORT_TIMEOUT_MS = get_env_int("SQL_REPORT_TIMEOUT_MS", 3000, min_val=100, max_val=60000)

    # Export Row Limits
    EXPORT_ROW_LIMIT = get_env_int("EXPORT_ROW_LIMIT", 10000, min_val=1, max_val=100000)
    EXPORT_PDF_ROW_LIMIT = get_env_int("EXPORT_PDF_ROW_LIMIT", 150, min_val=1, max_val=2000)

    # Pagination Defaults & Boundaries
    DEFAULT_PAGE_SIZE = get_env_int("DEFAULT_PAGE_SIZE", 10, min_val=1, max_val=100)
    MAX_PAGE_SIZE = get_env_int("MAX_PAGE_SIZE", 100, min_val=10, max_val=500)

    # Placement Package Reporting Bands / Brackets (in LPA)
    PACKAGE_BRACKET_TIER_1_MAX = get_env_float("PACKAGE_BRACKET_TIER_1_MAX", 6.0, min_val=0.1)
    PACKAGE_BRACKET_TIER_2_MAX = get_env_float("PACKAGE_BRACKET_TIER_2_MAX", 10.0, min_val=0.1)
    PACKAGE_BRACKET_TIER_3_MAX = get_env_float("PACKAGE_BRACKET_TIER_3_MAX", 15.0, min_val=0.1)

    # Secret Key for session signing & CSRF protection
    # Dynamically generates a secure random key if not explicitly set via environment
    _secret_key = os.getenv("SECRET_KEY")
    if not _secret_key:
        _secret_key = secrets.token_hex(32)
        if ENV == "production":
            logger.warning(
                "SECRET_KEY not set in environment! Generated ephemeral key for session security."
            )
    SECRET_KEY = _secret_key

    # Session & Cookie Security (OWASP Recommended)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "0") in ("1", "true", "True")
    PERMANENT_SESSION_LIFETIME = int(
        os.getenv("SESSION_LIFETIME_SECONDS", "7200")
    )  # 2 hours default

    # MySQL Settings
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "placement_db")
    MYSQL_CHARSET = os.getenv("MYSQL_CHARSET", "utf8mb4")
    MYSQL_CONNECT_TIMEOUT = int(os.getenv("MYSQL_CONNECT_TIMEOUT", "5"))

    # Dedicated Read-Only User for Custom SQL Execution
    MYSQL_READONLY_USER = os.getenv("MYSQL_READONLY_USER", "placement_readonly")
    MYSQL_READONLY_PASSWORD = os.getenv("MYSQL_READONLY_PASSWORD", "")

    # CSRF Protection toggle
    CSRF_ENABLED = True

    @classmethod
    def get_db_config(cls) -> dict:
        """Returns database connection parameters as a dictionary for PyMySQL.

        Prioritizes Flask current_app configuration (e.g. isolated test databases)
        and testing environment variables to prevent accidental mutation of production.
        """
        try:
            from flask import current_app, has_app_context

            if has_app_context() and current_app:
                return {
                    "host": current_app.config.get("MYSQL_HOST", cls.MYSQL_HOST),
                    "port": current_app.config.get("MYSQL_PORT", cls.MYSQL_PORT),
                    "user": current_app.config.get("MYSQL_USER", cls.MYSQL_USER),
                    "password": current_app.config.get("MYSQL_PASSWORD", cls.MYSQL_PASSWORD),
                    "database": current_app.config.get("MYSQL_DB", cls.MYSQL_DB),
                    "charset": current_app.config.get("MYSQL_CHARSET", cls.MYSQL_CHARSET),
                    "connect_timeout": current_app.config.get(
                        "MYSQL_CONNECT_TIMEOUT", cls.MYSQL_CONNECT_TIMEOUT
                    ),
                    "autocommit": False,
                }
        except Exception:
            pass

        target_db = cls.MYSQL_DB
        if os.getenv("FLASK_ENV") == "testing" and os.getenv("MYSQL_TEST_DB"):
            target_db = os.getenv("MYSQL_TEST_DB")

        return {
            "host": cls.MYSQL_HOST,
            "port": cls.MYSQL_PORT,
            "user": cls.MYSQL_USER,
            "password": cls.MYSQL_PASSWORD,
            "database": target_db,
            "charset": cls.MYSQL_CHARSET,
            "connect_timeout": cls.MYSQL_CONNECT_TIMEOUT,
            "autocommit": False,
        }

    @classmethod
    def get_readonly_db_config(cls) -> dict:
        """Returns database connection parameters for dedicated read-only execution."""
        try:
            from flask import current_app, has_app_context

            if has_app_context() and current_app:
                return {
                    "host": current_app.config.get("MYSQL_HOST", cls.MYSQL_HOST),
                    "port": current_app.config.get("MYSQL_PORT", cls.MYSQL_PORT),
                    "user": current_app.config.get("MYSQL_READONLY_USER", cls.MYSQL_READONLY_USER),
                    "password": current_app.config.get(
                        "MYSQL_READONLY_PASSWORD", cls.MYSQL_READONLY_PASSWORD
                    ),
                    "database": current_app.config.get("MYSQL_DB", cls.MYSQL_DB),
                    "charset": current_app.config.get("MYSQL_CHARSET", cls.MYSQL_CHARSET),
                    "connect_timeout": current_app.config.get(
                        "MYSQL_CONNECT_TIMEOUT", cls.MYSQL_CONNECT_TIMEOUT
                    ),
                    "autocommit": False,
                }
        except Exception:
            pass

        target_db = cls.MYSQL_DB
        if os.getenv("FLASK_ENV") == "testing" and os.getenv("MYSQL_TEST_DB"):
            target_db = os.getenv("MYSQL_TEST_DB")

        return {
            "host": cls.MYSQL_HOST,
            "port": cls.MYSQL_PORT,
            "user": cls.MYSQL_READONLY_USER,
            "password": cls.MYSQL_READONLY_PASSWORD,
            "database": target_db,
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

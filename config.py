import os
from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env from the project root directory
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)


class Config:
    """Base application configuration loaded from environment variables."""

    # Flask Settings
    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = os.getenv("FLASK_DEBUG", "0") in ("1", "true", "True")
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback_default_secret_key")
    PORT = int(os.getenv("PORT", 5000))

    # MySQL Settings
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "placement_db")
    MYSQL_CHARSET = os.getenv("MYSQL_CHARSET", "utf8mb4")
    MYSQL_CONNECT_TIMEOUT = int(os.getenv("MYSQL_CONNECT_TIMEOUT", 5))

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


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    MYSQL_DB = os.getenv("MYSQL_TEST_DB", "placement_db")


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

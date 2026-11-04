import time
import logging
from typing import Tuple, Dict, Any
from db import ping_db, DatabaseError

logger = logging.getLogger(__name__)


def check_system_health() -> Tuple[Dict[str, Any], int]:
    """Evaluates the live health of the application and its MySQL database connection.

    Returns:
        Tuple of (response_dict, http_status_code)
    """
    start_time = time.time()
    try:
        db_info = ping_db()
        latency_ms = round((time.time() - start_time) * 1000, 2)

        response = {
            "status": "healthy",
            "service": "Placement & Internship Management API",
            "database": {
                "connection": "connected",
                "engine": "MySQL",
                "version": db_info["mysql_version"],
                "active_database": db_info["database_name"],
                "server_time": db_info["server_time"],
                "latency_ms": latency_ms,
            },
        }
        return response, 200
    except DatabaseError as err:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        logger.error("Health check database failure: %s", err)
        try:
            from flask import current_app

            is_prod = bool(current_app and current_app.config.get("ENV") == "production")
        except Exception:
            is_prod = False
        raw_err = str(err)
        has_sensitive_data = any(
            k in raw_err.lower()
            for k in (
                "password",
                "access denied",
                "user '",
                "identified by",
                "select ",
                "insert ",
                "update ",
                "delete ",
                "table ",
            )
        )
        if is_prod or has_sensitive_data:
            err_output = "Database connection unavailable"
        else:
            err_output = raw_err

        response = {
            "status": "unhealthy",
            "service": "Placement & Internship Management API",
            "database": {
                "connection": "disconnected",
                "engine": "MySQL",
                "error": err_output,
                "latency_ms": latency_ms,
            },
        }
        return response, 503
    except Exception as exc:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        logger.error("Unexpected health check failure: %s", exc)
        response = {
            "status": "error",
            "service": "Placement & Internship Management API",
            "error": "Internal service error during health check",
            "latency_ms": latency_ms,
        }
        return response, 500

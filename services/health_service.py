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
        response = {
            "status": "unhealthy",
            "service": "Placement & Internship Management API",
            "database": {
                "connection": "disconnected",
                "engine": "MySQL",
                "error": str(err),
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
            "error": str(exc),
            "latency_ms": latency_ms,
        }
        return response, 500

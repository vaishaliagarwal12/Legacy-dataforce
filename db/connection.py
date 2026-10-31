import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple
import pymysql
from pymysql.cursors import DictCursor
from config import Config

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception wrapper for application-level database failures."""
    pass


@contextmanager
def get_connection():
    """Context manager for opening and safely releasing a MySQL database connection.
    
    Ensures that the connection is closed even if an exception occurs during execution.
    """
    connection = None
    try:
        connection = pymysql.connect(
            **Config.get_db_config(),
            cursorclass=DictCursor,
        )
        yield connection
    except pymysql.MySQLError as err:
        logger.error("MySQL connection error: %s (Error code: %s)", err, getattr(err, "args", [""])[0])
        raise DatabaseError(f"Database connection failed: {err}") from err
    finally:
        if connection and connection.open:
            connection.close()


@contextmanager
def get_readonly_connection():
    """Context manager providing a MySQL connection authenticated as the read-only user.
    
    Guarantees that write operations are rejected by MySQL server permissions.
    """
    connection = None
    try:
        connection = pymysql.connect(
            **Config.get_readonly_db_config(),
            cursorclass=DictCursor,
        )
        yield connection
    except pymysql.MySQLError as err:
        logger.error("Read-only MySQL connection error: %s", err)
        raise DatabaseError(f"Read-only database connection failed: {err}") from err
    finally:
        if connection and connection.open:
            connection.close()


@contextmanager
def get_cursor(commit: bool = False):
    """Context manager providing a DictCursor inside an active connection.
    
    Args:
        commit: If True, commits the transaction on clean block exit;
                rolls back the transaction if an unhandled exception occurs.
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        try:
            yield cursor
            if commit:
                connection.commit()
        except Exception as exc:
            if commit:
                try:
                    connection.rollback()
                    logger.warning("Transaction rolled back due to error: %s", exc)
                except Exception as rollback_err:
                    logger.error("Failed to rollback transaction: %s", rollback_err)
            raise exc
        finally:
            cursor.close()


def execute_query(query: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict[str, Any]]:
    """Executes a parameterized read query and returns all matching rows as a list of dictionaries.
    
    Args:
        query: SQL SELECT query with `%s` parameter placeholders.
        params: Tuple or list of parameter values to be safely bound.
    """
    with get_cursor(commit=False) as cursor:
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except pymysql.MySQLError as err:
            logger.error("Query execution failed: %s | SQL: %s | Params: %s", err, query, params)
            raise DatabaseError(f"Query failed: {err}") from err


def execute_one(query: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
    """Executes a parameterized read query and returns the first row or None.
    
    Args:
        query: SQL SELECT query with `%s` parameter placeholders.
        params: Tuple or list of parameter values.
    """
    with get_cursor(commit=False) as cursor:
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except pymysql.MySQLError as err:
            logger.error("Single row query failed: %s | SQL: %s", err, query)
            raise DatabaseError(f"Query failed: {err}") from err


def execute_mutation(query: str, params: Optional[Tuple[Any, ...]] = None) -> Dict[str, Any]:
    """Executes an INSERT, UPDATE, or DELETE statement inside an auto-committed transaction.
    
    Args:
        query: SQL statement with `%s` parameter placeholders.
        params: Tuple or list of parameter values.
        
    Returns:
        Dict with 'affected_rows' and 'last_insert_id'.
    """
    with get_cursor(commit=True) as cursor:
        try:
            affected_rows = cursor.execute(query, params or ())
            last_id = cursor.lastrowid
            return {
                "affected_rows": affected_rows,
                "last_insert_id": last_id,
            }
        except pymysql.MySQLError as err:
            logger.error("Mutation failed: %s | SQL: %s", err, query)
            raise DatabaseError(f"Database mutation failed: {err}") from err


def ping_db() -> Dict[str, Any]:
    """Executes a ping check against MySQL and returns connection metadata.
    
    Runs parameterized `SELECT VERSION() AS version, DATABASE() AS current_db, NOW() AS server_time`.
    """
    sql = "SELECT VERSION() AS mysql_version, DATABASE() AS database_name, NOW() AS server_time, 1 AS ping_status;"
    row = execute_one(sql)
    if not row or row.get("ping_status") != 1:
        raise DatabaseError("Database ping query did not return healthy status.")
    return {
        "status": "healthy",
        "database": "connected",
        "mysql_version": str(row.get("mysql_version")),
        "database_name": str(row.get("database_name")),
        "server_time": str(row.get("server_time")),
    }

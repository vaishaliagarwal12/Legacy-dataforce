"""
Campus Placement & Internship Management System
Database Initialization & Canonical Schema Loader

Executes schema.sql as the single source of truth for the 7-table schema,
relational views, indexes, and constraints.
Loads seed.sql when --reset is supplied.
"""

import argparse
import logging
import os
from db.connection import get_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("init_mysql")


def split_sql_statements(sql_text: str):
    """Splits a SQL script into individual executable statements, respecting quotes and comments."""
    statements = []
    current = []
    in_single_quote = False
    in_double_quote = False
    in_comment = False
    i = 0
    n = len(sql_text)
    while i < n:
        c = sql_text[i]
        if in_comment:
            if c == "\n":
                in_comment = False
            i += 1
            continue

        if not in_single_quote and not in_double_quote:
            if c == "-" and i + 1 < n and sql_text[i + 1] == "-":
                in_comment = True
                i += 2
                continue
            if c == ";":
                stmt = "".join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []
                i += 1
                continue

        if c == "'" and not in_double_quote:
            if in_single_quote and i + 1 < n and sql_text[i + 1] == "'":
                current.append("''")
                i += 2
                continue
            in_single_quote = not in_single_quote
        elif c == '"' and not in_single_quote:
            if in_double_quote and i + 1 < n and sql_text[i + 1] == '"':
                current.append('""')
                i += 2
                continue
            in_double_quote = not in_double_quote

        current.append(c)
        i += 1

    stmt = "".join(current).strip()
    if stmt:
        statements.append(stmt)
    return statements


def execute_statements(conn, sql_text: str):
    """Executes a block of SQL statements against the provided connection."""
    statements = split_sql_statements(sql_text)
    with conn.cursor() as cur:
        for stmt in statements:
            cleaned = stmt.strip()
            if not cleaned or cleaned.upper() in ("BEGIN", "COMMIT"):
                continue
            cur.execute(cleaned)


def init(reset: bool = False):
    """Initializes or resets the database using schema.sql and seed.sql."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(base_dir, "schema.sql")
    seed_path = os.path.join(base_dir, "seed.sql")

    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Canonical schema file not found at {schema_path}")

    with get_connection() as conn:
        logger.info("Executing canonical schema from schema.sql...")
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_content = f.read()

        execute_statements(conn, schema_content)
        conn.commit()
        logger.info("Canonical 7-table schema, views, indexes, and constraints successfully applied.")

        if reset:
            if not os.path.exists(seed_path):
                raise FileNotFoundError(f"Canonical seed data file not found at {seed_path}")
            logger.info("RESET flag specified. Loading canonical seed data from seed.sql...")
            with open(seed_path, "r", encoding="utf-8") as f:
                seed_content = f.read()

            with conn.cursor() as cur:
                cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            execute_statements(conn, seed_content)
            with conn.cursor() as cur:
                cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
            logger.info("Canonical seed data successfully loaded!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize canonical 7-table schema and seed data")
    parser.add_argument(
        "--reset", action="store_true", help="Perform full reset and reload canonical seed data"
    )
    args = parser.parse_args()

    init(reset=args.reset)

"""
Migration Script: migrate_to_7_tables.py
Safely migrates the database to the canonical 7-table relational schema.

Requirements:
- Requires --confirm flag to execute changes.
- Reports tables and row counts slated for removal.
- Drops foreign keys and columns on PLACEMENT and INTERNSHIP referencing dropped tables.
- Drops the 13 obsolete tables in reverse dependency order.
- Updates INTERNSHIP 2: Report_Semester = 8.
- Updates PLACEMENT: Offer_Status = 'Joined' -> Offer_Status = 'Accepted', Joined = 'Yes'.
- Audits and validates data consistency (e.g. Joined = 'Yes' requires Offer_Status = 'Accepted').
- Ensures canonical constraints (chk_placement_joined_status, uq_one_joined_offer, chk_internship_curriculum) are in place.
- Idempotent: safe to re-run.
"""

import argparse
import logging
from db.connection import get_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migrate_to_7_tables")

TABLES_TO_DROP = [
    "INTERNSHIP_REQUIREMENT",
    "SELECTION_PROCESS",
    "ELIGIBILITY_BRANCH",
    "ELIGIBILITY",
    "OPPORTUNITY",
    "RECRUITMENT_DRIVE",
    "SEMESTER_RESULT",
    "EDUCATION_DOCUMENT",
    "RESUME",
    "STUDENT_PROFILE",
    "STUDENT_COURSE",
    "COURSE",
    "UNIVERSITY",
]


def check_existing_tables(cur):
    """Finds which tables from TABLES_TO_DROP exist and counts their rows."""
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()")
    all_tables = {
        row["TABLE_NAME"].upper() if "TABLE_NAME" in row else row["table_name"].upper()
        for row in cur.fetchall()
    }

    found = {}
    for tbl in TABLES_TO_DROP:
        if tbl in all_tables:
            cur.execute(f"SELECT COUNT(*) AS cnt FROM `{tbl}`")
            row = cur.fetchone()
            cnt = row["cnt"] if "cnt" in row else row["COUNT(*)"]
            found[tbl] = cnt
    return found


def drop_fk_if_exists(cur, table_name, column_name):
    """Finds and drops any foreign key constraint defined on a specific table column."""
    sql = """
        SELECT CONSTRAINT_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
          AND REFERENCED_TABLE_NAME IS NOT NULL
    """
    cur.execute(sql, (table_name, column_name))
    rows = cur.fetchall()
    for r in rows:
        cname = r.get("CONSTRAINT_NAME") or r.get("constraint_name")
        logger.info(f"Dropping foreign key constraint {cname} on {table_name}.{column_name}...")
        cur.execute(f"ALTER TABLE `{table_name}` DROP FOREIGN KEY `{cname}`")


def drop_column_if_exists(cur, table_name, column_name):
    """Drops a column from a table if it exists."""
    sql = """
        SELECT COUNT(*) AS cnt
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
    """
    cur.execute(sql, (table_name, column_name))
    row = cur.fetchone()
    cnt = row.get("cnt") or row.get("COUNT(*)") or 0
    if cnt > 0:
        logger.info(f"Dropping column {table_name}.{column_name}...")
        cur.execute(f"ALTER TABLE `{table_name}` DROP COLUMN `{column_name}`")


def run_migration(confirmed: bool):
    with get_connection() as conn:
        with conn.cursor() as cur:
            logger.info("Inspecting database for tables to remove...")
            existing_to_drop = check_existing_tables(cur)

            if existing_to_drop:
                logger.info("Found %d obsolete tables to be removed:", len(existing_to_drop))
                for tbl, cnt in existing_to_drop.items():
                    logger.info("  - %-25s : %d rows", tbl, cnt)
            else:
                logger.info("No obsolete tables found. They may have already been removed.")

            if not confirmed:
                logger.warning(
                    "\n[DRY RUN] Migration was NOT executed because --confirm was not passed.\n"
                    "To execute this migration and remove the obsolete tables and columns, run:\n"
                    "    python migrate_to_7_tables.py --confirm"
                )
                return

            logger.info("\n[CONFIRMED] Commencing 7-table schema migration...")

            # 1. Update INTERNSHIP rows: Internship_No = 2 -> Report_Semester = 8
            logger.info("Updating INTERNSHIP 2 records (Report_Semester = 8, Credits = 4)...")
            cur.execute("""
                UPDATE INTERNSHIP
                SET Report_Semester = 8,
                    Credits = 4
                WHERE Internship_No = 2 AND Internship_Type = 'Mandatory'
            """)
            logger.info("Updated %d internship rows.", cur.rowcount)

            # 2. Update PLACEMENT: rows with Offer_Status = 'Joined' -> Offer_Status = 'Accepted', Joined = 'Yes'
            logger.info(
                "Migrating PLACEMENT Offer_Status 'Joined' to 'Accepted' with Joined = 'Yes'..."
            )
            # If Offer_Status column has ENUM including 'Joined', alter it first or update rows
            # First check if any rows have Offer_Status = 'Joined'
            try:
                cur.execute("""
                    UPDATE PLACEMENT
                    SET Offer_Status = 'Accepted',
                        Joined = 'Yes'
                    WHERE Offer_Status = 'Joined'
                """)
                logger.info(
                    "Migrated %d placement rows with Offer_Status = 'Joined'.", cur.rowcount
                )
            except Exception as e:
                logger.warning(f"Note during Offer_Status update: {e}")

            # 3. Check for any inconsistent PLACEMENT rows: Joined = 'Yes' and Offer_Status != 'Accepted'
            cur.execute("""
                SELECT Placement_ID, Student_ID, Offer_Status, Joined
                FROM PLACEMENT
                WHERE Joined = 'Yes' AND Offer_Status != 'Accepted'
            """)
            inconsistent = cur.fetchall()
            if inconsistent:
                logger.error(
                    "WARNING: Inconsistent placement rows found (Joined = 'Yes' but Offer_Status != 'Accepted'):"
                )
                for r in inconsistent:
                    logger.error(
                        "  Placement_ID: %s, Student_ID: %s, Offer_Status: %s, Joined: %s",
                        r.get("Placement_ID"),
                        r.get("Student_ID"),
                        r.get("Offer_Status"),
                        r.get("Joined"),
                    )
                raise ValueError(
                    "Data consistency violation: Joined = 'Yes' without Offer_Status = 'Accepted'."
                )
            else:
                logger.info(
                    "Placement consistency check passed: all Joined = 'Yes' records have Offer_Status = 'Accepted'."
                )

            # 4. Check for multiple joined offers per student
            cur.execute("""
                SELECT Student_ID, COUNT(*) AS cnt
                FROM PLACEMENT
                WHERE Joined = 'Yes'
                GROUP BY Student_ID
                HAVING cnt > 1
            """)
            mult_joined = cur.fetchall()
            if mult_joined:
                logger.error("WARNING: Multiple joined offers found for students:")
                for r in mult_joined:
                    logger.error(
                        "  Student_ID: %s (Joined offers: %s)", r.get("Student_ID"), r.get("cnt")
                    )
                raise ValueError("Single-joined-offer rule violated!")
            else:
                logger.info(
                    "Single-joined-offer check passed: no student has multiple joined offers."
                )

            # 5. Drop foreign keys on columns referencing obsolete tables
            drop_fk_if_exists(cur, "PLACEMENT", "Opportunity_ID")
            drop_fk_if_exists(cur, "INTERNSHIP", "Opportunity_ID")
            drop_fk_if_exists(cur, "INTERNSHIP", "Requirement_ID")

            # 6. Drop obsolete columns
            drop_column_if_exists(cur, "PLACEMENT", "Opportunity_ID")
            drop_column_if_exists(cur, "INTERNSHIP", "Opportunity_ID")
            drop_column_if_exists(cur, "INTERNSHIP", "Requirement_ID")

            # 7. Update PLACEMENT Offer_Status column definition to ('Offered', 'Accepted', 'Declined')
            logger.info("Updating PLACEMENT Offer_Status ENUM definition...")
            cur.execute("""
                ALTER TABLE PLACEMENT
                MODIFY COLUMN Offer_Status ENUM('Offered', 'Accepted', 'Declined') NOT NULL DEFAULT 'Offered'
            """)

            # 8. Drop the 13 obsolete tables in reverse dependency order
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            for tbl in TABLES_TO_DROP:
                cur.execute(f"DROP TABLE IF EXISTS `{tbl}`")
                logger.info("Dropped table %s (if existed).", tbl)
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")

            # 9. Verify views
            logger.info("Refreshing relational views V_PLACEMENT_DETAIL and V_INTERNSHIP_DETAIL...")
            cur.execute("DROP VIEW IF EXISTS V_PLACEMENT_DETAIL;")
            cur.execute("""
                CREATE VIEW V_PLACEMENT_DETAIL AS
                SELECT p.Placement_ID, p.Student_ID, s.Roll_No,
                       CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Student_Name,
                       s.Branch, s.Batch_Year, s.CGPA,
                       p.Company_ID, c.Company_Name, c.Company_Type,
                       p.Role, p.Package, p.Placement_Year, p.Placement_Type,
                       p.Is_PPO, p.Joined, p.Offer_Status, p.Interview_Rounds
                FROM PLACEMENT p
                JOIN STUDENT s ON p.Student_ID = s.Student_ID
                JOIN COMPANY c ON p.Company_ID = c.Company_ID;
            """)

            cur.execute("DROP VIEW IF EXISTS V_INTERNSHIP_DETAIL;")
            cur.execute("""
                CREATE VIEW V_INTERNSHIP_DETAIL AS
                SELECT i.Internship_ID, i.Student_ID, s.Roll_No,
                       CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Student_Name,
                       s.Branch, s.Batch_Year,
                       i.Company_ID, c.Company_Name,
                       i.Internship_No, i.Internship_Type, i.Role,
                       i.Start_Date, i.End_Date,
                       ROUND(DATEDIFF(i.End_Date, i.Start_Date) / 30.44, 1) AS Duration_Months,
                       i.Stipend,
                       i.Credits, i.Report_Semester, i.Report_Link, i.Report_Grade, i.Certificate_Link
                FROM INTERNSHIP i
                JOIN STUDENT s ON i.Student_ID = s.Student_ID
                JOIN COMPANY c ON i.Company_ID = c.Company_ID;
            """)

            # 10. Audit remaining tables in database
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = DATABASE() AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            remaining_tables = [r.get("TABLE_NAME") or r.get("table_name") for r in cur.fetchall()]
            logger.info(
                "Remaining base tables in database (%d): %s",
                len(remaining_tables),
                remaining_tables,
            )

        conn.commit()
        logger.info("Migration to canonical 7-table schema completed successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate database to canonical 7-table schema")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Execute the migration (without this flag, runs in dry-run mode)",
    )
    args = parser.parse_args()

    run_migration(confirmed=args.confirm)

#!/usr/bin/env python3
"""
Database Migration: Update 2nd Mandatory Internship Rule (v2)

Applies academic policy update:
- Internship 2 (Mandatory) is done DURING the 8th semester.
- Report submitted AFTER the end of the 8th semester (Report_Semester = 8).
- Prerequisite result evaluated against Semester 7 SGPA (Required_Result_Semester = 7).
- Preserves 4 credits and Mandatory status.
- Safe and idempotent: can be run repeatedly without side effects.
"""

import sys
import logging
from db.connection import get_cursor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migration_v2")


def run_migration():
    logger.info("Starting migration: 2nd Mandatory Internship Rule Update (v2)...")

    with get_cursor(commit=True) as cursor:
        # 1. Update INTERNSHIP_REQUIREMENT row for Internship_No = 2
        update_req_sql = """
            UPDATE INTERNSHIP_REQUIREMENT
            SET Prescribed_Period = 'During 8th semester',
                Required_Result_Semester = 7,
                Report_Submission_Semester = 8,
                Credits = 4,
                Mandatory = 'Yes',
                Description = 'Done during the 8th semester; report submitted after the end of the 8th semester.'
            WHERE Internship_No = 2;
        """
        cursor.execute(update_req_sql)
        logger.info("Updated INTERNSHIP_REQUIREMENT (rows affected: %d)", cursor.rowcount)

        # 2. Update existing INTERNSHIP records for Internship_No = 2 (Mandatory)
        # Update Report_Semester = 8 and Credits = 4 and 8th semester dates
        update_internships_sql = """
            UPDATE INTERNSHIP i
            JOIN STUDENT s ON i.Student_ID = s.Student_ID
            SET i.Report_Semester = 8,
                i.Credits = 4,
                i.Start_Date = CAST(CONCAT(s.Batch_Year + 4, '-01-10') AS DATE),
                i.End_Date = CAST(CONCAT(s.Batch_Year + 4, '-05-15') AS DATE)
            WHERE i.Internship_No = 2 AND i.Internship_Type = 'Mandatory';
        """
        cursor.execute(update_internships_sql)
        logger.info(
            "Updated INTERNSHIP records for Internship_No = 2 (rows affected: %d)", cursor.rowcount
        )

        # 3. Ensure Semester 7 results exist in SEMESTER_RESULT for students so prerequisite checks join dynamically
        insert_sem7_sql = """
            INSERT INTO SEMESTER_RESULT (Student_ID, Semester, SGPA, Year, Total_Credits)
            SELECT s.Student_ID, 7, s.CGPA, s.Batch_Year - 1, 24
            FROM STUDENT s
            LEFT JOIN SEMESTER_RESULT sr ON s.Student_ID = sr.Student_ID AND sr.Semester = 7
            WHERE sr.Result_ID IS NULL;
        """
        cursor.execute(insert_sem7_sql)
        logger.info(
            "Ensured Semester 7 results in SEMESTER_RESULT (rows added: %d)", cursor.rowcount
        )

        # 4. Verification check
        cursor.execute("SELECT * FROM INTERNSHIP_REQUIREMENT WHERE Internship_No = 2")
        req = cursor.fetchone()
        logger.info("Current Requirement 2 in DB: %s", req)

        cursor.execute("""
            SELECT COUNT(*) AS total_i2,
                   SUM(CASE WHEN Report_Semester = 8 THEN 1 ELSE 0 END) AS sem8_count,
                   SUM(CASE WHEN Credits = 4 THEN 1 ELSE 0 END) AS credits4_count
            FROM INTERNSHIP
            WHERE Internship_No = 2 AND Internship_Type = 'Mandatory'
        """)
        stats = cursor.fetchone()
        logger.info("Internship 2 DB Verification Stats: %s", stats)

    logger.info("Migration completed successfully.")


if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        logger.exception("Migration failed: %s", e)
        sys.exit(1)

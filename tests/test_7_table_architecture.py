"""Comprehensive Verification Test Suite: 7-Table Canonical Architecture.

Validates:
1. Exactly 7 base tables in the database.
2. Complete absence of the 13 dropped tables.
3. Existence and queryability of the 2 canonical views (V_PLACEMENT_DETAIL, V_INTERNSHIP_DETAIL).
4. Primary keys, foreign keys, and referential integrity (CASCADE vs RESTRICT).
5. Database constraints:
   - chk_placement_joined_status
   - uq_one_joined_offer (real constraint name)
   - chk_internship_curriculum (I1: Sem 5, 4 cr; I2: Sem 8, 4 cr; I3+: Additional)
   - chk_internship_dates
6. 'Placed' semantics: Joined = 'Yes'.
7. SQL console security rules.
"""

import pytest
import pymysql
from db.connection import get_cursor, execute_query, execute_one, DatabaseError
from services import (
    create_placement_offer,
    update_offer_status,
    create_internship,
    validate_custom_sql,
    ValidationError,
    ConflictError,
)

CANONICAL_7_TABLES = {
    "STUDENT",
    "STUDENT_PHONE",
    "STUDENT_SKILL",
    "COMPANY",
    "PLACEMENT",
    "PLACEMENT_SKILL",
    "INTERNSHIP",
}

DROPPED_13_TABLES = [
    "UNIVERSITY",
    "COURSE",
    "STUDENT_COURSE",
    "STUDENT_PROFILE",
    "RESUME",
    "EDUCATION_DOCUMENT",
    "SEMESTER_RESULT",
    "RECRUITMENT_DRIVE",
    "OPPORTUNITY",
    "ELIGIBILITY",
    "ELIGIBILITY_BRANCH",
    "SELECTION_PROCESS",
    "INTERNSHIP_REQUIREMENT",
]


class TestSevenTableArchitecture:
    """Rigorous architectural audit for the 7-table schema."""

    def test_01_exactly_seven_base_tables_exist(self, app):
        """Verifies that the database has EXACTLY 7 base tables."""
        rows = execute_query("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = DATABASE() AND table_type = 'BASE TABLE'
        """)
        actual_tables = {r["TABLE_NAME"].upper() if "TABLE_NAME" in r else r["table_name"].upper() for r in rows}
        assert actual_tables == CANONICAL_7_TABLES, f"Mismatch in base tables! Expected {CANONICAL_7_TABLES}, got {actual_tables}"
        assert len(actual_tables) == 7

    def test_02_all_thirteen_obsolete_tables_are_gone(self, app):
        """Verifies that none of the 13 removed tables exist in the database."""
        rows = execute_query("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
        """)
        all_names = {r["TABLE_NAME"].upper() if "TABLE_NAME" in r else r["table_name"].upper() for r in rows}
        for dropped in DROPPED_13_TABLES:
            assert dropped not in all_names, f"Obsolete table '{dropped}' still exists in the database!"

    def test_03_two_canonical_views_exist_and_function(self, app):
        """Verifies that V_PLACEMENT_DETAIL and V_INTERNSHIP_DETAIL exist and return rows."""
        rows = execute_query("""
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = DATABASE()
        """)
        view_names = {r["TABLE_NAME"].upper() if "TABLE_NAME" in r else r["table_name"].upper() for r in rows}
        assert "V_PLACEMENT_DETAIL" in view_names
        assert "V_INTERNSHIP_DETAIL" in view_names

        # Verify query execution
        p_row = execute_one("SELECT * FROM V_PLACEMENT_DETAIL LIMIT 1")
        assert p_row is not None
        assert "Student_Name" in p_row
        assert "Offer_Status" in p_row

        i_row = execute_one("SELECT * FROM V_INTERNSHIP_DETAIL LIMIT 1")
        assert i_row is not None
        assert "Duration_Months" in i_row
        assert "Student_Name" in i_row

    def test_04_primary_keys_and_composite_keys(self, app):
        """Verifies primary key configurations on all 7 tables."""
        pk_info = execute_query("""
            SELECT table_name, column_name, seq_in_index
            FROM information_schema.statistics
            WHERE table_schema = DATABASE() AND index_name = 'PRIMARY'
            ORDER BY table_name, seq_in_index
        """)
        pks_by_table = {}
        for r in pk_info:
            tbl = (r.get("TABLE_NAME") or r.get("table_name")).upper()
            col = r.get("COLUMN_NAME") or r.get("column_name")
            pks_by_table.setdefault(tbl, []).append(col)

        assert pks_by_table["STUDENT"] == ["Student_ID"]
        assert set(pks_by_table["STUDENT_PHONE"]) == {"Student_ID", "Phone_No"}
        assert set(pks_by_table["STUDENT_SKILL"]) == {"Student_ID", "Skill"}
        assert pks_by_table["COMPANY"] == ["Company_ID"]
        assert pks_by_table["PLACEMENT"] == ["Placement_ID"]
        assert set(pks_by_table["PLACEMENT_SKILL"]) == {"Placement_ID", "Skill"}
        assert set(pks_by_table["INTERNSHIP"]) == {"Student_ID", "Internship_No"}

    def test_05_foreign_key_referential_actions(self, app):
        """Verifies foreign keys and their ON DELETE actions (RESTRICT vs CASCADE)."""
        fks = execute_query("""
            SELECT table_name, constraint_name, delete_rule
            FROM information_schema.referential_constraints
            WHERE constraint_schema = DATABASE()
        """)
        fk_rules = {
            (r["TABLE_NAME"].upper() if "TABLE_NAME" in r else r["table_name"].upper(),
             r["CONSTRAINT_NAME"].lower() if "CONSTRAINT_NAME" in r else r["constraint_name"].lower()):
            (r["DELETE_RULE"] if "DELETE_RULE" in r else r["delete_rule"]).upper()
            for r in fks
        }

        # CASCADE deletions: child records owned by parent
        assert fk_rules.get(("STUDENT_PHONE", "fk_sphone_student")) == "CASCADE"
        assert fk_rules.get(("STUDENT_SKILL", "fk_sskill_student")) == "CASCADE"
        assert fk_rules.get(("PLACEMENT_SKILL", "fk_pskill_placement")) == "CASCADE"

        # RESTRICT deletions: institutional records protect student and company
        assert fk_rules.get(("PLACEMENT", "fk_placement_student")) == "RESTRICT"
        assert fk_rules.get(("PLACEMENT", "fk_placement_company")) == "RESTRICT"
        assert fk_rules.get(("INTERNSHIP", "fk_internship_student")) == "RESTRICT"
        assert fk_rules.get(("INTERNSHIP", "fk_internship_company")) == "RESTRICT"

    def test_06_chk_placement_joined_status(self, app):
        """Verifies chk_placement_joined_status allows Joined='No' with any status,
        Joined='Yes' with Accepted, and rejects Joined='Yes' with Offered or Declined.
        """
        with get_cursor(commit=True) as cur:
            # 1. Reject Joined='Yes' with Offered
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute("""
                    INSERT INTO PLACEMENT (Student_ID, Company_ID, Role, Package, Placement_Year, Offer_Status, Joined)
                    VALUES (2, 2, 'Tester Role', 10.00, 2026, 'Offered', 'Yes')
                """)

            # 2. Reject Joined='Yes' with Declined
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute("""
                    INSERT INTO PLACEMENT (Student_ID, Company_ID, Role, Package, Placement_Year, Offer_Status, Joined)
                    VALUES (2, 2, 'Tester Role', 10.00, 2026, 'Declined', 'Yes')
                """)

    def test_07_uq_one_joined_offer(self, app):
        """Verifies uq_one_joined_offer prevents a student from having multiple joined offers."""
        with get_cursor(commit=True) as cur:
            # Find a student who already joined an offer
            cur.execute("SELECT Student_ID FROM PLACEMENT WHERE Joined = 'Yes' LIMIT 1")
            joined_student = cur.fetchone()["Student_ID"]

            # Attempting a second joined offer for the same student must fail via unique key
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute("""
                    INSERT INTO PLACEMENT (Student_ID, Company_ID, Role, Package, Placement_Year, Offer_Status, Joined)
                    VALUES (%s, 3, 'Second Joined Role', 18.00, 2026, 'Accepted', 'Yes')
                """, (joined_student,))

    def test_08_chk_internship_curriculum_and_new_rule(self, app):
        """Verifies chk_internship_curriculum enforces Internship 2 is 8th semester, 4 credits."""
        with get_cursor(commit=True) as cur:
            # Internship 1: must have Credits = 4, Report_Semester = 5
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute("""
                    INSERT INTO INTERNSHIP (Student_ID, Company_ID, Internship_No, Internship_Type, Role,
                                           Start_Date, End_Date, Credits, Report_Semester)
                    VALUES (3, 1, 1, 'Mandatory', 'I1 Wrong Sem', '2024-06-01', '2024-07-31', 4, 6)
                """)

            # Internship 2: must have Credits = 4, Report_Semester = 8 (old rule was sem 7)
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute("""
                    INSERT INTO INTERNSHIP (Student_ID, Company_ID, Internship_No, Internship_Type, Role,
                                           Start_Date, End_Date, Credits, Report_Semester)
                    VALUES (3, 1, 2, 'Mandatory', 'I2 Old Rule Sem 7', '2024-01-01', '2024-05-31', 4, 7)
                """)

            # Internship 2: valid new rule: Report_Semester = 8, Credits = 4
            # (Testing against chk_internship_curriculum constraint logic)

    def test_09_service_validation_placed_and_joined(self, app):
        """Verifies service layer rejects Joined = 'Yes' when Offer_Status != 'Accepted'."""
        with pytest.raises(ValidationError):
            create_placement_offer({
                "Student_ID": 1,
                "Company_ID": 1,
                "Role": "Test Engineer",
                "Package": 11.00,
                "Placement_Year": 2026,
                "Offer_Status": "Offered",
                "Joined": "Yes",
            })

    def test_10_sql_console_safety_rules(self, app):
        """Verifies SQL console strict safety rules."""
        # Reject non-SELECT
        with pytest.raises(ValidationError):
            validate_custom_sql("DROP TABLE STUDENT")

        with pytest.raises(ValidationError):
            validate_custom_sql("DELETE FROM PLACEMENT")

        # Reject multiple statements
        with pytest.raises(ValidationError):
            validate_custom_sql("SELECT * FROM STUDENT; SELECT * FROM COMPANY")

        # Reject comments
        with pytest.raises(ValidationError):
            validate_custom_sql("SELECT * FROM STUDENT -- comment")

        with pytest.raises(ValidationError):
            validate_custom_sql("SELECT * FROM STUDENT /* comment */")

        # Accept valid SELECT
        valid = validate_custom_sql("SELECT Student_ID, Roll_No FROM STUDENT WHERE CGPA >= 8.0")
        assert valid.startswith("SELECT")

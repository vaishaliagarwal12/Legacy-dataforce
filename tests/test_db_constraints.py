"""Legacy DataForce - Database Constraint & Relational Integrity Tests.

Verifies MySQL 8.0 CHECK constraints, NOT NULL enforcement, UNIQUE indexes,
composite keys, and Foreign Key CASCADE / RESTRICT rules on the canonical 7-table schema.
"""

import pytest
import pymysql
from db.connection import get_cursor, DatabaseError


class TestDatabaseConstraints:
    """Tests that MySQL server-side schema constraints reject illegal mutations."""

    def test_check_constraint_cgpa_bounds(self, app):
        """Verifies chk_student_cgpa rejects CGPA > 10.0 and CGPA < 0.0."""
        with get_cursor(commit=True) as cur:
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute(
                    """INSERT INTO STUDENT (Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs, Email)
                       VALUES ('TEST_CHK_CGPA_HI', 'Check', 'High', 'CSE', 2024, 10.50, 0, 'chk_hi@univ.edu')"""
                )

        with get_cursor(commit=True) as cur:
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute(
                    """INSERT INTO STUDENT (Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs, Email)
                       VALUES ('TEST_CHK_CGPA_LO', 'Check', 'Low', 'CSE', 2024, -0.50, 0, 'chk_lo@univ.edu')"""
                )

    def test_check_constraint_backlogs_non_negative(self, app):
        """Verifies chk_student_backlogs rejects negative backlog count."""
        with get_cursor(commit=True) as cur:
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute(
                    """INSERT INTO STUDENT (Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs, Email)
                       VALUES ('TEST_CHK_BL_NEG', 'Check', 'Neg', 'CSE', 2024, 8.00, -2, 'chk_neg@univ.edu')"""
                )

    def test_check_constraint_placement_joined_status(self, app):
        """Verifies chk_placement_joined_status enforces (Joined = 'No' OR Offer_Status = 'Accepted')."""
        with get_cursor(commit=True) as cur:
            # Cannot join an offer that is only 'Offered'
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute(
                    """INSERT INTO PLACEMENT (Student_ID, Company_ID, Role, Package, Placement_Year, Offer_Status, Joined)
                       VALUES (1, 1, 'Illegal Joined Role', 12.00, 2024, 'Offered', 'Yes')"""
                )

        with get_cursor(commit=True) as cur:
            # Cannot join an offer that is 'Declined'
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute(
                    """INSERT INTO PLACEMENT (Student_ID, Company_ID, Role, Package, Placement_Year, Offer_Status, Joined)
                       VALUES (1, 1, 'Illegal Joined Role 2', 12.00, 2024, 'Declined', 'Yes')"""
                )

    def test_unique_constraint_uq_one_joined_offer(self, app):
        """Verifies uq_one_joined_offer enforces at most one Joined = 'Yes' offer per student."""
        # Find a student who already joined an offer
        with get_cursor(commit=True) as cur:
            cur.execute("SELECT Student_ID FROM PLACEMENT WHERE Joined = 'Yes' LIMIT 1")
            row = cur.fetchone()
            assert row is not None
            student_id = row["Student_ID"]

            # Attempting to insert a SECOND offer with Joined = 'Yes' for the same student must fail
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute(
                    """INSERT INTO PLACEMENT (Student_ID, Company_ID, Role, Package, Placement_Year, Offer_Status, Joined)
                       VALUES (%s, 2, 'Second Joined Offer', 15.00, 2024, 'Accepted', 'Yes')""",
                    (student_id,),
                )

    def test_check_constraint_internship_curriculum(self, app):
        """Verifies chk_internship_curriculum enforces I1 (Sem 5, 4 cr) and I2 (Sem 8, 4 cr)."""
        with get_cursor(commit=True) as cur:
            # Internship 1 with wrong Report_Semester (e.g. 7 instead of 5)
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute(
                    """INSERT INTO INTERNSHIP (Student_ID, Company_ID, Internship_No, Internship_Type, Role,
                                               Start_Date, End_Date, Credits, Report_Semester)
                       VALUES (1, 1, 1, 'Mandatory', 'Invalid I1', '2024-06-01', '2024-07-31', 4, 7)"""
                )

            # Internship 2 with wrong Report_Semester (e.g. 7 instead of 8)
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute(
                    """INSERT INTO INTERNSHIP (Student_ID, Company_ID, Internship_No, Internship_Type, Role,
                                               Start_Date, End_Date, Credits, Report_Semester)
                       VALUES (1, 1, 2, 'Mandatory', 'Invalid I2', '2024-01-01', '2024-05-31', 4, 7)"""
                )

    def test_check_constraint_internship_chronological_dates(self, app):
        """Verifies chk_internship_dates rejects Start_Date > End_Date."""
        with get_cursor(commit=True) as cur:
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute(
                    """INSERT INTO INTERNSHIP (Student_ID, Company_ID, Internship_No, Internship_Type, Role,
                                               Start_Date, End_Date, Stipend)
                       VALUES (1, 1, 99, 'Additional', 'Summer Intern', '2024-08-01', '2024-06-01', 25000)"""
                )

    def test_unique_constraint_student_roll_no(self, app, clean_test_student):
        """Verifies UNIQUE constraint on STUDENT(Roll_No)."""
        existing_roll = clean_test_student["Roll_No"]
        with get_cursor(commit=True) as cur:
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute(
                    """INSERT INTO STUDENT (Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs, Email)
                       VALUES (%s, 'Dup', 'Roll', 'IT', 2024, 7.50, 0, 'unique_diff_email@univ.edu')""",
                    (existing_roll,),
                )

    def test_unique_constraint_student_email(self, app, clean_test_student):
        """Verifies UNIQUE constraint on STUDENT(Email)."""
        existing_email = clean_test_student["Email"]
        with get_cursor(commit=True) as cur:
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute(
                    """INSERT INTO STUDENT (Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs, Email)
                       VALUES ('SYN_DIFF_ROLL_99', 'Dup', 'Email', 'IT', 2024, 7.50, 0, %s)""",
                    (existing_email,),
                )

    def test_unique_constraint_company_name(self, app, clean_test_company):
        """Verifies UNIQUE constraint on COMPANY(Company_Name)."""
        existing_name = clean_test_company["Company_Name"]
        with get_cursor(commit=True) as cur:
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute(
                    """INSERT INTO COMPANY (Company_Name, Company_Type, Industry)
                       VALUES (%s, 'Startup', 'Software')""",
                    (existing_name,),
                )

    def test_restrict_delete_company_with_placements(self, app):
        """Verifies RESTRICT prevents deleting a company that has existing placement records."""
        # Company 1 has placement offers registered in seed data
        with get_cursor(commit=True) as cur:
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute("DELETE FROM COMPANY WHERE Company_ID = 1")

    def test_restrict_delete_student_with_placements(self, app):
        """Verifies RESTRICT prevents deleting a student who has placement records."""
        with get_cursor(commit=True) as cur:
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute("DELETE FROM STUDENT WHERE Student_ID = 1")

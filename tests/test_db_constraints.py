"""Legacy DataForce - Database Constraint & Relational Integrity Tests.

Verifies MySQL 8.0 CHECK constraints, NOT NULL enforcement, UNIQUE indexes,
composite keys, and Foreign Key CASCADE / RESTRICT rules.
"""

import pytest
import pymysql
from db.connection import get_cursor, DatabaseError


class TestDatabaseConstraints:
    """Tests that MySQL server-side schema constraints reject illegal mutations."""

    def test_check_constraint_cgpa_bounds(self, app):
        """Verifies student_chk_2 rejects CGPA > 10.0 and CGPA < 0.0."""
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
        """Verifies student_chk_3 rejects negative backlog count."""
        with get_cursor(commit=True) as cur:
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute(
                    """INSERT INTO STUDENT (Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs, Email)
                       VALUES ('TEST_CHK_BL_NEG', 'Check', 'Neg', 'CSE', 2024, 8.00, -2, 'chk_neg@univ.edu')"""
                )

    def test_check_constraint_course_semester_and_credits(self, app):
        """Verifies course_chk_1 rejects Semester outside 1-8 and course_chk_2 rejects Credits < 1."""
        with get_cursor(commit=True) as cur:
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute(
                    """INSERT INTO COURSE (University_ID, Course_Name, Department, Semester, Credits, Course_Type)
                       VALUES (1, 'Invalid Sem Course', 'CSE', 9, 4, 'Core')"""
                )

        with get_cursor(commit=True) as cur:
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute(
                    """INSERT INTO COURSE (University_ID, Course_Name, Department, Semester, Credits, Course_Type)
                       VALUES (1, 'Zero Credit Course', 'CSE', 4, 0, 'Core')"""
                )

    def test_check_constraint_internship_chronological_dates(self, app):
        """Verifies chk_internship_dates rejects Start_Date > End_Date."""
        with get_cursor(commit=True) as cur:
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute(
                    """INSERT INTO INTERNSHIP (Student_ID, Company_ID, Internship_No, Internship_Type, Role,
                                               Start_Date, End_Date, Stipend)
                       VALUES (1, 1, 999, 'Additional', 'Summer Intern', '2024-08-01', '2024-06-01', 25000)"""
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

    def test_restrict_delete_company_with_active_drives(self, app):
        """Verifies RESTRICT prevents deleting a company that has active recruitment drives."""
        # Company 1 has drives registered in seed data
        with get_cursor(commit=True) as cur:
            with pytest.raises((DatabaseError, pymysql.MySQLError)):
                cur.execute("DELETE FROM COMPANY WHERE Company_ID = 1")

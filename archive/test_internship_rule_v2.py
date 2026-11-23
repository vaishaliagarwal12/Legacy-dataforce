"""
Unit & Integration Tests for Updated 2nd Mandatory Internship Rule (v2)

Verifies:
1. Internship 2 (Mandatory) with Report_Semester = 8 is accepted.
2. Internship 2 (Mandatory) with Report_Semester = 7 is rejected (ValidationError).
3. Internship 1 (Mandatory) is unchanged (Report_Semester = 5, prerequisite = Semester 3).
4. Additional internships (No. 3 and above) remain optional and allowed without requirement linkage.
5. INTERNSHIP_REQUIREMENT metadata matches the approved academic governance policy.
6. Dynamic prerequisite join uses Semester 7 SGPA for Internship 2.
"""

import unittest
from datetime import date
from db.connection import get_cursor, execute_one
from services.internship_service import (
    create_internship,
    update_internship,
    check_internship_eligibility,
    get_mandatory_internships_with_prerequisite_sgpa,
)
from services.internship_requirement_service import list_requirements, get_requirement
from services.exceptions import ValidationError, ConflictError


class TestInternshipRuleV2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a test student and company for testing
        with get_cursor(commit=True) as cur:
            cur.execute("""
                INSERT INTO STUDENT (Roll_No, First_Name, Last_Name, Email, Branch, Batch_Year, CGPA, Backlogs)
                VALUES ('TEST_V2_001', 'TestRule', 'Student', 'testrule.student@fictional.edu', 'CSE', 2021, 8.50, 0)
                ON DUPLICATE KEY UPDATE Student_ID = LAST_INSERT_ID(Student_ID)
            """)
            cls.student_id = cur.lastrowid or execute_one("SELECT Student_ID FROM STUDENT WHERE Roll_No = 'TEST_V2_001'")["Student_ID"]

            # Insert Sem 3, Sem 7 results
            cur.execute("""
                INSERT INTO SEMESTER_RESULT (Student_ID, Semester, SGPA, Year, Total_Credits)
                VALUES (%s, 3, 8.20, 2022, 24)
                ON DUPLICATE KEY UPDATE SGPA = 8.20
            """, (cls.student_id,))
            cur.execute("""
                INSERT INTO SEMESTER_RESULT (Student_ID, Semester, SGPA, Year, Total_Credits)
                VALUES (%s, 7, 8.75, 2024, 24)
                ON DUPLICATE KEY UPDATE SGPA = 8.75
            """, (cls.student_id,))

            cls.company_id = execute_one("SELECT Company_ID FROM COMPANY LIMIT 1")["Company_ID"]

    @classmethod
    def tearDownClass(cls):
        with get_cursor(commit=True) as cur:
            cur.execute("DELETE FROM INTERNSHIP WHERE Student_ID = %s", (cls.student_id,))
            cur.execute("DELETE FROM SEMESTER_RESULT WHERE Student_ID = %s", (cls.student_id,))
            cur.execute("DELETE FROM STUDENT WHERE Student_ID = %s", (cls.student_id,))

    def tearDown(self):
        with get_cursor(commit=True) as cur:
            cur.execute("DELETE FROM INTERNSHIP WHERE Student_ID = %s", (self.student_id,))

    def test_01_internship_requirement_metadata(self):
        """Verify Requirement 2 metadata matches the new 8th semester rule."""
        req2 = get_requirement(2)
        self.assertEqual(req2["Internship_No"], 2)
        self.assertEqual(req2["Mandatory"], "Yes")
        self.assertEqual(req2["Prescribed_Period"], "During 8th semester")
        self.assertEqual(req2["Required_Result_Semester"], 7)
        self.assertEqual(req2["Report_Submission_Semester"], 8)
        self.assertEqual(req2["Credits"], 4)
        self.assertIn("Done during the 8th semester", req2["Description"])

    def test_02_internship_2_report_semester_8_accepted(self):
        """Internship 2 (Mandatory) with Report_Semester = 8 is accepted."""
        payload = {
            "Student_ID": self.student_id,
            "Company_ID": self.company_id,
            "Requirement_ID": 2,
            "Internship_No": 2,
            "Internship_Type": "Mandatory",
            "Role": "SDE Intern 8th Sem",
            "Start_Date": "2025-01-15",
            "End_Date": "2025-05-15",
            "Credits": 4,
            "Report_Semester": 8,
            "Stipend": 45000.0,
        }
        res = create_internship(payload)
        self.assertIsNotNone(res["Internship_ID"])
        self.assertEqual(res["Report_Semester"], 8)
        self.assertEqual(res["Credits"], 4)

    def test_03_internship_2_report_semester_7_rejected(self):
        """Internship 2 (Mandatory) with old Report_Semester = 7 must be rejected with ValidationError."""
        payload = {
            "Student_ID": self.student_id,
            "Company_ID": self.company_id,
            "Requirement_ID": 2,
            "Internship_No": 2,
            "Internship_Type": "Mandatory",
            "Role": "SDE Intern Old Sem",
            "Start_Date": "2025-01-15",
            "End_Date": "2025-05-15",
            "Credits": 4,
            "Report_Semester": 7,
            "Stipend": 45000.0,
        }
        with self.assertRaises(ValidationError) as ctx:
            create_internship(payload)
        self.assertIn("8th semester", str(ctx.exception))
        self.assertIn("Report_Semester must be 8", str(ctx.exception))

    def test_04_internship_1_unchanged(self):
        """Internship 1 (Mandatory) is unchanged: Report_Semester must be 5, prerequisite is Sem 3."""
        payload_ok = {
            "Student_ID": self.student_id,
            "Company_ID": self.company_id,
            "Requirement_ID": 1,
            "Internship_No": 1,
            "Internship_Type": "Mandatory",
            "Role": "Summer Trainee I1",
            "Start_Date": "2023-06-01",
            "End_Date": "2023-07-31",
            "Credits": 4,
            "Report_Semester": 5,
            "Stipend": 20000.0,
        }
        res = create_internship(payload_ok)
        self.assertIsNotNone(res["Internship_ID"])
        self.assertEqual(res["Report_Semester"], 5)

        # Invalid Report_Semester for I1 (e.g. 8) must be rejected
        payload_bad = {
            "Student_ID": self.student_id,
            "Company_ID": self.company_id,
            "Requirement_ID": 1,
            "Internship_No": 1,
            "Internship_Type": "Mandatory",
            "Role": "Summer Trainee Bad",
            "Start_Date": "2023-06-01",
            "End_Date": "2023-07-31",
            "Credits": 4,
            "Report_Semester": 8,
            "Stipend": 20000.0,
        }
        # First clean up I1 from student
        with get_cursor(commit=True) as cur:
            cur.execute("DELETE FROM INTERNSHIP WHERE Student_ID = %s", (self.student_id,))

        with self.assertRaises(ValidationError) as ctx:
            create_internship(payload_bad)
        self.assertIn("Semester 5", str(ctx.exception))

    def test_05_additional_internship_allowed_and_optional(self):
        """Additional internship (No. 3) is allowed without requirement linkage."""
        payload = {
            "Student_ID": self.student_id,
            "Company_ID": self.company_id,
            "Requirement_ID": None,
            "Internship_No": 3,
            "Internship_Type": "Additional",
            "Role": "Winter Research Fellow",
            "Start_Date": "2024-12-01",
            "End_Date": "2025-01-10",
            "Credits": 3,
            "Report_Semester": 8,
            "Stipend": 35000.0,
        }
        res = create_internship(payload)
        self.assertIsNotNone(res["Internship_ID"])
        self.assertEqual(res["Internship_Type"], "Additional")
        self.assertIsNone(res["Requirement_ID"])

    def test_06_eligibility_uses_semester_7_sgpa_for_internship_2(self):
        """Verifies eligibility check for Internship 2 dynamically evaluates Semester 7 SGPA."""
        elig = check_internship_eligibility(self.student_id, 2, min_sgpa=6.00)
        self.assertTrue(elig["is_eligible"])
        self.assertEqual(elig["required_result_semester"], 7)
        self.assertEqual(elig["prerequisite_sgpa"], 8.75)


if __name__ == "__main__":
    unittest.main()

import unittest
from app import create_app
from db.connection import execute_one, execute_query


class Phase7AcademicInternshipsTestCase(unittest.TestCase):
    """Test suite for Phase 7: Semester results, Internship requirements, Mandatory/Additional constraints,
    dynamic prerequisite SGPA joins, and missing mandatory queries."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()

    # -------------------------------------------------------------------------
    # 1. SEMESTER RESULTS TESTS & CONSTRAINTS
    # -------------------------------------------------------------------------
    def test_01_create_semester_result_success(self):
        """Tests recording an official verified semester result."""
        payload = {
            "Student_ID": 5,  # Rohan
            "Semester": 4,
            "SGPA": 7.20,
            "Year": 2022,
            "Total_Credits": 24
        }
        res = self.client.post("/api/semester-results", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()["data"]
        self.assertEqual(data["Student_ID"], 5)
        self.assertEqual(data["Semester"], 4)
        self.assertEqual(data["SGPA"], 7.20)

    def test_02_duplicate_semester_result_rejected(self):
        """CRITICAL: Enforces (Student_ID, Semester) uniqueness -> HTTP 409."""
        payload = {
            "Student_ID": 5,
            "Semester": 4,
            "SGPA": 8.00,
            "Year": 2022,
            "Total_Credits": 24
        }
        res = self.client.post("/api/semester-results", json=payload)
        self.assertEqual(res.status_code, 409)
        self.assertIn("Duplicate result rejected", res.get_json()["message"])

    def test_03_invalid_sgpa_rejected(self):
        """Tests that SGPA > 10.00 is rejected with HTTP 400."""
        payload = {
            "Student_ID": 5,
            "Semester": 6,
            "SGPA": 11.50,  # Invalid
            "Year": 2023,
            "Total_Credits": 24
        }
        res = self.client.post("/api/semester-results", json=payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("SGPA must be a decimal number between 0.00 and 10.00", res.get_json()["message"])

    # -------------------------------------------------------------------------
    # 2. ACADEMIC POLICY INTERNSHIP REQUIREMENTS
    # -------------------------------------------------------------------------
    def test_04_verify_the_two_internship_requirements(self):
        """CRITICAL: Verifies official Academic Policy Requirements 1 and 2."""
        res = self.client.get("/api/internships/requirements")
        self.assertEqual(res.status_code, 200)
        reqs = res.get_json()["data"]
        self.assertEqual(len(reqs), 2)

        # Requirement 1: Summer after 2nd year -> Requires Sem 3 result, defended in Sem 5
        req1 = next(r for r in reqs if r["Internship_No"] == 1)
        self.assertEqual(req1["Required_Result_Semester"], 3)
        self.assertEqual(req1["Report_Submission_Semester"], 5)
        self.assertEqual(req1["Credits"], 4)

        # Requirement 2: Summer after 3rd year -> Requires Sem 5 result, defended in Sem 7
        req2 = next(r for r in reqs if r["Internship_No"] == 2)
        self.assertEqual(req2["Required_Result_Semester"], 5)
        self.assertEqual(req2["Report_Submission_Semester"], 7)
        self.assertEqual(req2["Credits"], 4)

    # -------------------------------------------------------------------------
    # 3. MANDATORY INTERNSHIPS & BAD CASE CONSTRAINT TESTING
    # -------------------------------------------------------------------------
    def test_05_bad_case_mandatory_missing_requirement_id(self):
        """CRITICAL BAD CASE: Mandatory internship without Requirement_ID must be rejected (HTTP 400)."""
        payload = {
            "Student_ID": 5,
            "Company_ID": 6,
            "Internship_No": 1,
            "Internship_Type": "Mandatory",
            "Requirement_ID": None,  # ILLEGAL: Mandatory requires Requirement_ID
            "Start_Date": "2022-06-01",
            "End_Date": "2022-07-31"
        }
        res = self.client.post("/api/internships", json=payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("must link to a valid INTERNSHIP_REQUIREMENT", res.get_json()["message"])

    def test_06_bad_case_mandatory_mismatched_requirement_number(self):
        """CRITICAL BAD CASE: Mandatory Internship #1 linking to Requirement #2 must be rejected (HTTP 400)."""
        payload = {
            "Student_ID": 5,
            "Company_ID": 6,
            "Internship_No": 1,
            "Internship_Type": "Mandatory",
            "Requirement_ID": 2,  # ILLEGAL: Internship 1 cannot link to Requirement 2
            "Start_Date": "2022-06-01",
            "End_Date": "2022-07-31"
        }
        res = self.client.post("/api/internships", json=payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Requirement number mismatch", res.get_json()["message"])

    def test_07_bad_case_additional_with_requirement_id(self):
        """CRITICAL BAD CASE: Additional internship linking to a requirement must be rejected (HTTP 400)."""
        payload = {
            "Student_ID": 5,
            "Company_ID": 6,
            "Internship_No": 3,
            "Internship_Type": "Additional",
            "Requirement_ID": 1,  # ILLEGAL: Additional internships must have Requirement_ID = NULL
            "Start_Date": "2023-12-01",
            "End_Date": "2024-01-15"
        }
        res = self.client.post("/api/internships", json=payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Additional internships cannot be linked to mandatory academic requirements", res.get_json()["message"])

    def test_08_bad_case_invalid_date_ordering(self):
        """CRITICAL BAD CASE: End_Date earlier than Start_Date must be rejected (HTTP 400)."""
        payload = {
            "Student_ID": 5,
            "Company_ID": 6,
            "Internship_No": 1,
            "Internship_Type": "Mandatory",
            "Requirement_ID": 1,
            "Start_Date": "2022-07-31",
            "End_Date": "2022-06-01"  # ILLEGAL: End earlier than Start
        }
        res = self.client.post("/api/internships", json=payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("End_Date", res.get_json()["message"])
        self.assertIn("cannot be earlier than Start_Date", res.get_json()["message"])

    def test_09_legitimate_mandatory_and_additional_creation(self):
        """Tests creating a legitimate Mandatory Internship (linked to Req 1) and an Additional Internship (Req = None)."""
        # Create Mandatory Internship 1
        m1_payload = {
            "Student_ID": 5,
            "Company_ID": 8,  # Tata Motors
            "Internship_No": 1,
            "Internship_Type": "Mandatory",
            "Requirement_ID": 1,
            "Role": "Automotive Engineering Trainee",
            "Stipend": 15000.00,
            "Start_Date": "2022-06-01",
            "End_Date": "2022-07-31"
        }
        res_m1 = self.client.post("/api/internships", json=m1_payload)
        self.assertEqual(res_m1.status_code, 201)
        data_m1 = res_m1.get_json()["data"]
        self.assertEqual(data_m1["Internship_Type"], "Mandatory")
        self.assertEqual(data_m1["Requirement_ID"], 1)

        # Create Additional Internship 3 (Requirement_ID = None)
        a3_payload = {
            "Student_ID": 5,
            "Company_ID": 4,  # Razorpay
            "Internship_No": 3,
            "Internship_Type": "Additional",
            "Requirement_ID": None,
            "Role": "Winter Open Source Fellow",
            "Stipend": 20000.00,
            "Start_Date": "2023-12-01",
            "End_Date": "2024-01-15"
        }
        res_a3 = self.client.post("/api/internships", json=a3_payload)
        self.assertEqual(res_a3.status_code, 201)
        data_a3 = res_a3.get_json()["data"]
        self.assertEqual(data_a3["Internship_Type"], "Additional")
        self.assertIsNone(data_a3["Requirement_ID"])

    def test_10_bad_case_duplicate_internship_number(self):
        """CRITICAL BAD CASE: Duplicate Internship_No for the same student must be rejected (HTTP 409 Conflict)."""
        dup_payload = {
            "Student_ID": 5,
            "Company_ID": 1,
            "Internship_No": 1,  # Already used in test_09
            "Internship_Type": "Mandatory",
            "Requirement_ID": 1,
            "Start_Date": "2022-06-01",
            "End_Date": "2022-07-31"
        }
        res = self.client.post("/api/internships", json=dup_payload)
        self.assertEqual(res.status_code, 409)
        self.assertIn("already has an internship recorded with number 1", res.get_json()["message"])

    # -------------------------------------------------------------------------
    # 4. ZERO REDUNDANCY DYNAMIC PREREQUISITE SGPA JOIN
    # -------------------------------------------------------------------------
    def test_11_demonstrate_prerequisite_sgpa_join_without_storing_twice(self):
        """CRITICAL: Demonstrates that Semester 3 SGPA (for Internship 1) and Semester 5 SGPA (for Internship 2)
        are fetched dynamically via INTERNSHIP -> INTERNSHIP_REQUIREMENT -> SEMESTER_RESULT with zero redundancy."""
        res = self.client.get("/api/internships/analytics/prerequisite-sgpa")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        self.assertTrue(len(data) >= 1)

        for record in data:
            self.assertEqual(record["Internship_Type"], "Mandatory")
            self.assertIn(record["Internship_No"], (1, 2))
            if record["Internship_No"] == 1:
                self.assertEqual(record["Required_Result_Semester"], 3)
            elif record["Internship_No"] == 2:
                self.assertEqual(record["Required_Result_Semester"], 5)
            self.assertIsNotNone(record["Prerequisite_Semester_SGPA"])
            self.assertGreater(record["Prerequisite_Semester_SGPA"], 0.0)

    # -------------------------------------------------------------------------
    # 5. QUERY FOR STUDENTS MISSING A MANDATORY INTERNSHIP
    # -------------------------------------------------------------------------
    def test_12_query_students_missing_mandatory_internships(self):
        """CRITICAL: Tests query reporting students who have NOT completed mandatory internships."""
        res = self.client.get("/api/internships/analytics/missing-mandatory")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        self.assertTrue(len(data) >= 1)

        for s in data:
            self.assertTrue(
                s["Mandatory_I1_Status"] == "MISSING" or s["Mandatory_I2_Status"] == "MISSING"
            )

    # -------------------------------------------------------------------------
    # 6. CLEANUP
    # -------------------------------------------------------------------------
    def test_13_cleanup(self):
        """Cleans up test records created for student 5."""
        internships = execute_query("SELECT Internship_ID FROM INTERNSHIP WHERE Student_ID = 5")
        for i in internships:
            self.client.delete(f"/api/internships/{i['Internship_ID']}")

        sem_res = execute_one("SELECT Result_ID FROM SEMESTER_RESULT WHERE Student_ID = 5 AND Semester = 4")
        if sem_res:
            self.client.delete(f"/api/semester-results/{sem_res['Result_ID']}")


if __name__ == "__main__":
    unittest.main()

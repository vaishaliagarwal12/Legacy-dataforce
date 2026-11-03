import io
import csv
import unittest
from app import create_app
from db.connection import execute_one, execute_query, execute_mutation, get_cursor
from services.internship_service import (
    create_internship,
    get_internship,
    list_internships,
    update_internship,
    delete_internship,
    check_internship_eligibility,
    calculate_internship_duration,
    determine_internship_status,
    get_branch_internship_statistics,
    get_batch_compliance_reports,
    get_internship_dashboard_analytics,
    get_pending_internship_reports,
    get_mandatory_internships_with_prerequisite_sgpa,
    get_students_missing_mandatory_internships,
    ValidationError,
    ConflictError,
    NotFoundError,
)


class InternshipUpgradeTestCase(unittest.TestCase):
    """Comprehensive test suite verifying the upgraded Internship Management module."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()

        # Clean up any leftover test student from previous aborted runs
        with get_cursor(commit=True) as cur:
            cur.execute("DELETE FROM INTERNSHIP WHERE Student_ID IN (SELECT Student_ID FROM STUDENT WHERE Roll_No = 'TEST_INT_STUDENT')")
            cur.execute("DELETE FROM SEMESTER_RESULT WHERE Student_ID IN (SELECT Student_ID FROM STUDENT WHERE Roll_No = 'TEST_INT_STUDENT')")
            cur.execute("DELETE FROM STUDENT WHERE Roll_No = 'TEST_INT_STUDENT'")

    @classmethod
    def tearDownClass(cls):
        with get_cursor(commit=True) as cur:
            cur.execute("DELETE FROM INTERNSHIP WHERE Student_ID IN (SELECT Student_ID FROM STUDENT WHERE Roll_No = 'TEST_INT_STUDENT')")
            cur.execute("DELETE FROM SEMESTER_RESULT WHERE Student_ID IN (SELECT Student_ID FROM STUDENT WHERE Roll_No = 'TEST_INT_STUDENT')")
            cur.execute("DELETE FROM STUDENT WHERE Roll_No = 'TEST_INT_STUDENT'")

    def _create_test_student(self):
        """Helper to create an isolated test student for eligibility tests."""
        with get_cursor(commit=True) as cur:
            cur.execute("""
                INSERT INTO STUDENT (Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs, Email)
                VALUES ('TEST_INT_STUDENT', 'Academic', 'TestStudent', 'CSE', 2024, 8.50, 0, 'test_int_student@example.com')
            """)
            return cur.lastrowid

    def _cleanup_test_student(self, student_id):
        """Helper to clean up isolated test student and records."""
        with get_cursor(commit=True) as cur:
            cur.execute("DELETE FROM INTERNSHIP WHERE Student_ID = %s", (student_id,))
            cur.execute("DELETE FROM SEMESTER_RESULT WHERE Student_ID = %s", (student_id,))
            cur.execute("DELETE FROM STUDENT WHERE Student_ID = %s", (student_id,))

    # -------------------------------------------------------------------------
    # 1. DASHBOARD ANALYTICS & EXECUTIVE KPIS
    # -------------------------------------------------------------------------
    def test_01_internship_dashboard_analytics_and_kpis(self):
        """Verifies get_internship_dashboard_analytics aggregates accurate KPIs, grade and type distributions."""
        analytics = get_internship_dashboard_analytics()
        self.assertIn("kpis", analytics)
        kpis = analytics["kpis"]

        self.assertEqual(kpis["total_internships"], 62)
        self.assertEqual(kpis["mandatory_i1_completed"], 29)
        self.assertEqual(kpis["mandatory_i2_completed"], 29)
        self.assertEqual(kpis["additional_internships"], 4)
        self.assertEqual(kpis["total_students"], 30)
        self.assertEqual(kpis["fully_compliant_students"], 29)
        self.assertAlmostEqual(kpis["compliance_rate"], 96.7, places=1)
        self.assertGreater(kpis["avg_stipend"], 0.0)

        # Grade distribution
        self.assertIn("grade_distribution", analytics)
        grades = [g["grade"] for g in analytics["grade_distribution"]]
        self.assertIn("A", grades)
        self.assertIn("A+", grades)

        # Type distribution
        self.assertEqual(analytics["type_distribution"]["mandatory_1"], 29)
        self.assertEqual(analytics["type_distribution"]["mandatory_2"], 29)
        self.assertEqual(analytics["type_distribution"]["additional"], 4)

    # -------------------------------------------------------------------------
    # 2. MULTI-FIELD SEARCH FUNCTIONALITY
    # -------------------------------------------------------------------------
    def test_02_internship_search_functionality(self):
        """Verifies searching internships by student name, roll number, company, and role."""
        # 1. By student first name
        res_name = list_internships(search="Aarav")
        self.assertTrue(len(res_name) > 0)
        self.assertTrue(all("Aarav" in r["Student_Name"] for r in res_name))

        # 2. By roll number
        res_roll = list_internships(search="CS202001")
        self.assertTrue(len(res_roll) > 0)
        self.assertTrue(all(r["Roll_No"] == "CS202001" for r in res_roll))

        # 3. By company name
        res_comp = list_internships(search="Nexus Software")
        self.assertTrue(len(res_comp) > 0)
        self.assertTrue(all("Nexus Software" in r["Company_Name"] for r in res_comp))

        # 4. By role
        res_role = list_internships(search="Engineering Intern")
        self.assertTrue(len(res_role) > 0)
        self.assertTrue(any("Engineering Intern" in (r["Role"] or "") for r in res_role))

    # -------------------------------------------------------------------------
    # 3. MULTI-DIMENSIONAL FILTERING
    # -------------------------------------------------------------------------
    def test_03_internship_filters(self):
        """Verifies filtering internships by branch, batch year, company, status, and grade."""
        # 1. By Branch (CSE)
        res_cse = list_internships(branch="CSE")
        self.assertTrue(len(res_cse) > 0)
        self.assertTrue(all(r["Branch"] == "CSE" for r in res_cse))

        # 2. By Batch Year (2022)
        res_batch = list_internships(batch_year=2022)
        self.assertTrue(len(res_batch) > 0)
        self.assertTrue(all(r["Batch_Year"] == 2022 for r in res_batch))

        # 3. By Internship Type (Mandatory vs Additional)
        res_mand = list_internships(internship_type="Mandatory")
        self.assertEqual(len(res_mand), 58)  # 29 I1 + 29 I2
        self.assertTrue(all(r["Internship_Type"] == "Mandatory" for r in res_mand))

        res_add = list_internships(internship_type="Additional")
        self.assertEqual(len(res_add), 4)
        self.assertTrue(all(r["Internship_Type"] == "Additional" for r in res_add))

        # 4. By Report Grade (A)
        res_grade = list_internships(report_grade="A")
        self.assertTrue(len(res_grade) > 0)
        self.assertTrue(all(r["Report_Grade"] == "A" for r in res_grade))

    # -------------------------------------------------------------------------
    # 4. DURATION & OPERATIONAL STATUS TRACKING
    # -------------------------------------------------------------------------
    def test_04_duration_and_status_tracking(self):
        """Verifies calculate_internship_duration and determine_internship_status logic."""
        # 61 days: 2024-06-01 to 2024-07-31
        dur = calculate_internship_duration("2024-06-01", "2024-07-31")
        self.assertEqual(dur["days"], 61)
        self.assertEqual(dur["weeks"], 8.7)
        self.assertIn("weeks", dur["duration_str"])

        # Completed status
        status_completed = determine_internship_status("2022-06-01", "2022-07-31", "https://rep.pdf", "A", "https://cert.pdf")
        self.assertEqual(status_completed, "Completed")

        # Pending Report status
        status_pending = determine_internship_status("2022-06-01", "2022-07-31", None, None, None)
        self.assertEqual(status_pending, "Pending Report")

        # Upcoming status (future dates)
        status_upcoming = determine_internship_status("2030-06-01", "2030-07-31", None, None, None)
        self.assertEqual(status_upcoming, "Upcoming")

    # -------------------------------------------------------------------------
    # 5. ZERO REDUNDANCY DYNAMIC PREREQUISITE SGPA JOIN
    # -------------------------------------------------------------------------
    def test_05_prerequisite_sgpa_dynamic_join_zero_redundancy(self):
        """Verifies Mandatory I1 uses Sem 3 SGPA and Mandatory I2 uses Sem 5 SGPA dynamically."""
        mandatory = get_mandatory_internships_with_prerequisite_sgpa()
        self.assertTrue(len(mandatory) > 0)

        for m in mandatory:
            self.assertEqual(m["Internship_Type"], "Mandatory")
            if m["Internship_No"] == 1:
                self.assertEqual(m["Required_Result_Semester"], 3)
            elif m["Internship_No"] == 2:
                self.assertEqual(m["Required_Result_Semester"], 5)
            self.assertIsNotNone(m["Prerequisite_Semester_SGPA"])
            self.assertGreater(m["Prerequisite_Semester_SGPA"], 0.0)

    # -------------------------------------------------------------------------
    # 6. ACADEMIC RULE: ELIGIBLE SCENARIO
    # -------------------------------------------------------------------------
    def test_06_academic_rule_eligible_scenario(self):
        """Verifies a candidate with verified Sem 3 SGPA >= 6.00 is evaluated as Eligible for I1."""
        student_id = self._create_test_student()
        try:
            # Record Sem 3 result with SGPA 8.40 for test student
            with get_cursor(commit=True) as cur:
                cur.execute("""
                    INSERT INTO SEMESTER_RESULT (Student_ID, Semester, SGPA, Year, Total_Credits)
                    VALUES (%s, 3, 8.40, 2021, 24)
                """, (student_id,))

            res_i1 = check_internship_eligibility(student_id, 1, min_sgpa=6.00)
            self.assertTrue(res_i1["is_eligible"])
            self.assertEqual(res_i1["status"], "Eligible")
            self.assertEqual(res_i1["required_result_semester"], 3)
            self.assertEqual(res_i1["prerequisite_sgpa"], 8.40)
            self.assertIn("is eligible", res_i1["message"])

            # Also record Sem 5 result with SGPA 8.60 for test student -> Eligible for I2
            with get_cursor(commit=True) as cur:
                cur.execute("""
                    INSERT INTO SEMESTER_RESULT (Student_ID, Semester, SGPA, Year, Total_Credits)
                    VALUES (%s, 5, 8.60, 2022, 24)
                """, (student_id,))

            res_i2 = check_internship_eligibility(student_id, 2, min_sgpa=6.00)
            self.assertTrue(res_i2["is_eligible"])
            self.assertEqual(res_i2["status"], "Eligible")
            self.assertEqual(res_i2["required_result_semester"], 5)
            self.assertEqual(res_i2["prerequisite_sgpa"], 8.60)
        finally:
            self._cleanup_test_student(student_id)

    # -------------------------------------------------------------------------
    # 7. ACADEMIC RULE: INELIGIBLE SCENARIO (LOW SGPA)
    # -------------------------------------------------------------------------
    def test_07_academic_rule_ineligible_scenario_low_sgpa(self):
        """Verifies a candidate whose prerequisite semester SGPA is below minimum threshold is Ineligible."""
        student_id = self._create_test_student()
        try:
            # Update Sem 3 result to SGPA 5.40 (< 6.00)
            with get_cursor(commit=True) as cur:
                cur.execute("""
                    INSERT INTO SEMESTER_RESULT (Student_ID, Semester, SGPA, Year, Total_Credits)
                    VALUES (%s, 3, 5.40, 2021, 24)
                """, (student_id,))

            res_low = check_internship_eligibility(student_id, 1, min_sgpa=6.00)
            self.assertFalse(res_low["is_eligible"])
            self.assertEqual(res_low["status"], "Ineligible")
            self.assertEqual(res_low["prerequisite_sgpa"], 5.40)
            self.assertIn("below minimum requirement", res_low["message"])
        finally:
            self._cleanup_test_student(student_id)

    # -------------------------------------------------------------------------
    # 8. ACADEMIC RULE: INCOMPLETE / MISSING PREREQUISITE SCENARIO
    # -------------------------------------------------------------------------
    def test_08_academic_rule_incomplete_missing_prerequisite_scenario(self):
        """Verifies a candidate with NO recorded prerequisite semester result is flagged as Prerequisite Missing."""
        student_id = self._create_test_student()
        try:
            res_missing = check_internship_eligibility(student_id, 1, min_sgpa=6.00)
            self.assertFalse(res_missing["is_eligible"])
            self.assertEqual(res_missing["status"], "Prerequisite Missing")
            self.assertFalse(res_missing["semester_result_found"])
            self.assertIsNone(res_missing["prerequisite_sgpa"])
            self.assertIn("no recorded result for Semester 3", res_missing["message"])
        finally:
            self._cleanup_test_student(student_id)

    # -------------------------------------------------------------------------
    # 9. ACADEMIC RULE: OPTIONAL ADDITIONAL INTERNSHIP SCENARIO
    # -------------------------------------------------------------------------
    def test_09_optional_additional_internship_scenario(self):
        """Verifies additional internships (Sequence >= 3) are optional without prerequisite semester blockages."""
        student_id = self._create_test_student()
        try:
            res_opt = check_internship_eligibility(student_id, 3)
            self.assertTrue(res_opt["is_eligible"])
            self.assertEqual(res_opt["status"], "Optional")
            self.assertEqual(res_opt["internship_type"], "Additional")
            self.assertIsNone(res_opt["required_result_semester"])
            self.assertIn("optional", res_opt["message"])
        finally:
            self._cleanup_test_student(student_id)

    # -------------------------------------------------------------------------
    # 10. PENDING INTERNSHIP REPORTS DETECTION
    # -------------------------------------------------------------------------
    def test_10_pending_reports_detection(self):
        """Verifies get_pending_internship_reports detects internships with missing reports or grades."""
        student_id = self._create_test_student()
        try:
            # Create an internship with missing report for test student
            comp = execute_one("SELECT Company_ID FROM COMPANY LIMIT 1")
            test_intern = create_internship({
                "Student_ID": student_id,
                "Company_ID": comp["Company_ID"],
                "Internship_No": 3,
                "Internship_Type": "Additional",
                "Role": "Summer Research Trainee",
                "Start_Date": "2023-06-01",
                "End_Date": "2023-07-31",
                "Report_Link": None,
                "Report_Grade": None,
            })
            intern_id = test_intern["Internship_ID"]

            pending_list = get_pending_internship_reports()
            matching = [p for p in pending_list if p["Internship_ID"] == intern_id]
            self.assertEqual(len(matching), 1)
            self.assertEqual(matching[0]["Status"], "Pending Report")

            # Cleanup test internship
            delete_internship(intern_id)
        finally:
            self._cleanup_test_student(student_id)

    # -------------------------------------------------------------------------
    # 11. BRANCH-WISE INTERNSHIP COMPLETION STATISTICS
    # -------------------------------------------------------------------------
    def test_11_branch_wise_internship_statistics(self):
        """Verifies get_branch_internship_statistics aggregates student counts, I1, I2, and compliance rates."""
        stats = get_branch_internship_statistics()
        self.assertTrue(len(stats) >= 4)  # CSE, ECE, IT, ME

        branches = [b["Branch"] for b in stats]
        self.assertIn("CSE", branches)
        self.assertIn("ECE", branches)
        self.assertIn("IT", branches)
        self.assertIn("ME", branches)

        for b in stats:
            self.assertGreater(b["total_students"], 0)
            self.assertGreaterEqual(b["compliance_rate"], 0.0)
            self.assertLessEqual(b["compliance_rate"], 100.0)

    # -------------------------------------------------------------------------
    # 12. BATCH-WISE COMPLIANCE REPORTS
    # -------------------------------------------------------------------------
    def test_12_batch_wise_compliance_reports(self):
        """Verifies get_batch_compliance_reports tracks degree progress across graduation cohorts."""
        reports = get_batch_compliance_reports()
        self.assertTrue(len(reports) >= 4)  # 2022, 2023, 2024, 2025

        batches = [r["Batch_Year"] for r in reports]
        self.assertIn(2022, batches)
        self.assertIn(2023, batches)
        self.assertIn(2024, batches)
        self.assertIn(2025, batches)

        for r in reports:
            self.assertGreater(r["total_students"], 0)
            self.assertGreaterEqual(r["compliance_rate"], 0.0)
            self.assertLessEqual(r["compliance_rate"], 100.0)

    # -------------------------------------------------------------------------
    # 13. CSV EXPORT ENDPOINT
    # -------------------------------------------------------------------------
    def test_13_csv_export_endpoint(self):
        """Verifies /internships/export-csv streams downloadable RFC 4180 CSV with complete headers."""
        res = self.client.get("/internships/export-csv")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/csv", res.content_type)
        self.assertIn("attachment; filename=", res.headers.get("Content-Disposition", ""))

        csv_text = res.get_data(as_text=True)
        reader = csv.reader(io.StringIO(csv_text))
        rows = list(reader)
        self.assertTrue(len(rows) > 1)

        header = rows[0]
        expected_cols = [
            "Internship ID", "Roll No", "Student Name", "Branch", "Batch Year",
            "Company Name", "Designated Role", "Category", "Sequence No",
            "Prerequisite Sem SGPA", "Duration Weeks", "Monthly Stipend (INR)", "Credits",
            "Report Semester", "Report Grade", "Operational Status"
        ]
        for col in expected_cols:
            self.assertIn(col, header)

    # -------------------------------------------------------------------------
    # 14. WEB ROUTES & TEMPLATE RENDERING
    # -------------------------------------------------------------------------
    def test_14_web_routes_and_views(self):
        """Verifies HTML routes for directory, detail dossier, create form, and edit view."""
        # 1. Main Directory
        res_index = self.client.get("/internships")
        self.assertEqual(res_index.status_code, 200)
        html_index = res_index.get_data(as_text=True)
        self.assertIn("Academic Compliance", html_index)
        self.assertIn("All Student Internships", html_index)
        self.assertIn("Mandatory I1", html_index)

        # 2. Detail Dossier View
        res_detail = self.client.get("/internships/1")
        self.assertEqual(res_detail.status_code, 200)
        html_detail = res_detail.get_data(as_text=True)
        self.assertIn("Student Candidate Profile", html_detail)
        self.assertIn("Academic Policy & Eligibility Audit", html_detail)
        self.assertIn("Host Corporate Partner", html_detail)

        # 3. Create Form
        res_create = self.client.get("/internships/new")
        self.assertEqual(res_create.status_code, 200)
        html_create = res_create.get_data(as_text=True)
        self.assertIn("Record Student Internship", html_create)
        self.assertIn("Academic Degree Requirement", html_create)

        # 4. Edit Form
        res_edit = self.client.get("/internships/1/edit")
        self.assertEqual(res_edit.status_code, 200)
        html_edit = res_edit.get_data(as_text=True)
        self.assertIn("Edit Internship Record #1", html_edit)


if __name__ == "__main__":
    unittest.main()

import unittest
from app import create_app
from services import list_students, list_companies


class Phase8FrontendTestCase(unittest.TestCase):
    """Automated test suite verifying Phase 8 Bootstrap 5 and Jinja2 frontend routes."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()

    def test_01_dashboard_page(self):
        """Verify the executive dashboard renders with KPI cards, Chart.js canvases, and 200 OK."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Academic Internship Dashboard", html)
        self.assertIn("Active Students", html)
        self.assertIn("Placement Rate", html)
        self.assertIn("yearwisePlacementChart", html)
        self.assertIn("branchwiseChart", html)
        self.assertIn("offerStatusChart", html)
        self.assertIn("internshipBreakdownChart", html)

    def test_02_students_list_and_filters(self):
        """Verify students list page renders and supports search and branch filters."""
        # Unfiltered
        response = self.client.get("/students")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Student Career Profiles", html)
        self.assertIn("Quick Search", html)

        # Filtered by branch
        response_cse = self.client.get("/students?branch=Computer+Science")
        self.assertEqual(response_cse.status_code, 200)
        self.assertIn("Computer Science", response_cse.get_data(as_text=True))

    def test_03_student_create_form_and_submission(self):
        """Verify adding a student via GET /students/new and POST /students/new with validation."""
        # GET form
        res_get = self.client.get("/students/new")
        self.assertEqual(res_get.status_code, 200)
        self.assertIn("Register New Student", res_get.get_data(as_text=True))

        # POST form
        unique_roll = "P8_TEST_99"
        res_post = self.client.post("/students/new", data={
            "Roll_No": unique_roll,
            "First_Name": "Phase8",
            "Last_Name": "Tester",
            "Email": "p8.tester@university.edu",
            "Branch": "Information Tech",
            "Batch_Year": "2024",
            "Section": "A",
            "CGPA": "8.75",
            "Backlogs": "0",
        }, follow_redirects=True)
        self.assertEqual(res_post.status_code, 200)
        html = res_post.get_data(as_text=True)
        self.assertIn(unique_roll, html)
        self.assertIn("Phase8 Tester", html)

    def test_04_student_detail_page(self):
        """Verify student detail page shows semester results, course registrations, and career records."""
        # Fetch an existing student
        res_st = list_students(limit=1)
        students = res_st.get("results", []) if isinstance(res_st, dict) else res_st
        self.assertTrue(len(students) > 0)
        student_id = students[0]["Student_ID"]

        response = self.client.get(f"/students/{student_id}")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn(students[0]["Roll_No"], html)
        self.assertIn("Official Semester Results", html)
        self.assertIn("Emergency", html)
        self.assertIn("Enrolled Courses", html)

    def test_05_companies_list_and_detail(self):
        """Verify corporate directory and company detail view with drives and opportunities."""
        # List view
        res_list = self.client.get("/companies")
        self.assertEqual(res_list.status_code, 200)
        self.assertIn("Corporate Recruiting Partners", res_list.get_data(as_text=True))

        # Detail view
        companies = list_companies()
        self.assertTrue(len(companies) > 0)
        cid = companies[0]["Company_ID"]
        res_detail = self.client.get(f"/companies/{cid}")
        self.assertEqual(res_detail.status_code, 200)
        html = res_detail.get_data(as_text=True)
        self.assertIn(companies[0]["Company_Name"], html)
        self.assertIn("Campus Recruitment Drives", html)

    def test_06_internships_tabs_and_audit(self):
        """Verify internships page displays All, Mandatory (with dynamic SGPA), Additional, and Missing Audit."""
        # All
        res_all = self.client.get("/internships?type=All")
        self.assertEqual(res_all.status_code, 200)
        self.assertIn("All Student Internships", res_all.get_data(as_text=True))

        # Mandatory
        res_mand = self.client.get("/internships?type=Mandatory")
        self.assertEqual(res_mand.status_code, 200)
        self.assertIn("Mandatory Internships", res_mand.get_data(as_text=True))

        # Additional
        res_add = self.client.get("/internships?type=Additional")
        self.assertEqual(res_add.status_code, 200)
        self.assertIn("Additional Voluntary Internships", res_add.get_data(as_text=True))

        # Missing Mandatory Audit
        res_miss = self.client.get("/internships?type=Missing")
        self.assertEqual(res_miss.status_code, 200)
        self.assertIn("Missing Mandatory Internships", res_miss.get_data(as_text=True))

    def test_07_internship_create_form(self):
        """Verify GET /internships/new loads students and academic requirements."""
        response = self.client.get("/internships/new")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Record Student Internship", html)
        self.assertIn("Academic Degree Requirement", html)
        self.assertIn("internship_type_select", html)

    def test_08_placements_offers_and_multi_view(self):
        """Verify placements view renders offers and multi-offer star performers view."""
        # All offers
        res_offers = self.client.get("/placements")
        self.assertEqual(res_offers.status_code, 200)
        self.assertIn("Campus Placement Offers", res_offers.get_data(as_text=True))
        self.assertIn("issueOfferModal", res_offers.get_data(as_text=True))

        # Multi-offer view
        res_multi = self.client.get("/placements?view=multiple")
        self.assertEqual(res_multi.status_code, 200)
        self.assertIn("Star Performers", res_multi.get_data(as_text=True))

    def test_09_reports_page_and_csv_export(self):
        """Verify reports page filters work and /reports/export streams valid CSV data."""
        # HTML Report view
        res_report = self.client.get("/reports?branch=Computer+Science&placement_status=Placed")
        self.assertEqual(res_report.status_code, 200)
        html = res_report.get_data(as_text=True)
        self.assertIn("Placement Analytics Reports", html)
        self.assertIn("Detailed Student Cohort Report", html)

        # CSV Export
        res_csv = self.client.get("/reports/export?branch=Computer+Science")
        self.assertEqual(res_csv.status_code, 200)
        self.assertEqual(res_csv.mimetype, "text/csv")
        self.assertIn("attachment; filename=placement_internship_report.csv", res_csv.headers.get("Content-Disposition", ""))
        csv_text = res_csv.get_data(as_text=True)
        self.assertIn("Roll No,Student Name,Email,Branch", csv_text)

    def test_10_analytics_json_api(self):
        """Verify JSON endpoints for Chart.js and external analytics."""
        res_dash = self.client.get("/api/analytics/dashboard")
        self.assertEqual(res_dash.status_code, 200)
        json_data = res_dash.get_json()
        self.assertIn("students", json_data["data"])
        self.assertIn("placements", json_data["data"])

        res_year = self.client.get("/api/analytics/charts/yearwise")
        self.assertEqual(res_year.status_code, 200)
        self.assertIn("labels", res_year.get_json()["data"])

    @classmethod
    def tearDownClass(cls):
        """Clean up test student created in test_03."""
        from db.connection import get_cursor
        with get_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM STUDENT WHERE Roll_No = 'P8_TEST_99'")


if __name__ == "__main__":
    unittest.main()

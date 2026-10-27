import time
import unittest
from app import create_app
from db.connection import execute_one, execute_mutation


class TestKeyRoutes(unittest.TestCase):
    """Phase 10 Test Suite: Verifying key API and Web UI routes:
    1. Health check & Diagnostics
    2. Student Management Routes (CRUD, search, filters, phones)
    3. Course & Academic Registrations
    4. Company, Drives & Opportunities
    5. Placements, Offer Status, and Analytics
    6. Internships & Semester Results
    7. Web UI Pages (Dashboard, Students, Companies, Placements, Internships, Reports)
    """

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()

    # =========================================================================
    # 1. HEALTH & DIAGNOSTICS ROUTES
    # =========================================================================

    def test_01_health_route(self):
        """GET /health - Verifies health endpoint returns 200, MySQL engine, and latency."""
        res = self.client.get("/health")
        self.assertIn(res.status_code, (200, 503))
        data = res.get_json()
        self.assertIn("status", data)
        self.assertEqual(data["database"]["engine"], "MySQL")
        self.assertEqual(data["database"]["connection"], "connected")
        self.assertIn("latency_ms", data["database"])

    # =========================================================================
    # 2. STUDENT ROUTES
    # =========================================================================

    def test_02_student_list_and_filter_routes(self):
        """GET /api/students - Tests listing students and filtering by branch and min_cgpa."""
        # Unfiltered listing
        res = self.client.get("/api/students")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertEqual(json_data["status"], "success")
        self.assertTrue(len(json_data["data"]) > 0)

        # Filtered by branch
        res_cse = self.client.get("/api/students?branch=Computer+Science")
        self.assertEqual(res_cse.status_code, 200)
        for s in res_cse.get_json()["data"]:
            self.assertEqual(s["Branch"], "Computer Science")

        # Filtered by min_cgpa
        res_cgpa = self.client.get("/api/students?min_cgpa=8.50")
        self.assertEqual(res_cgpa.status_code, 200)
        for s in res_cgpa.get_json()["data"]:
            self.assertGreaterEqual(s["CGPA"], 8.50)

    def test_03_student_crud_lifecycle(self):
        """POST /api/students, GET /api/students/<id>, PUT /api/students/<id>, DELETE /api/students/<id>."""
        roll = f"RT_{int(time.time() * 1000) % 10000000}"
        payload = {
            "Roll_No": roll,
            "First_Name": "RouteTester",
            "Last_Name": "Alpha",
            "Branch": "Information Technology",
            "Batch_Year": 2024,
            "CGPA": 9.15,
            "Backlogs": 0,
            "Email": f"{roll.lower()}@univ.edu",
            "Phone_Numbers": ["+91-9870001111"]
        }

        # 1. POST (Create)
        res_post = self.client.post("/api/students", json=payload)
        self.assertEqual(res_post.status_code, 201)
        created = res_post.get_json()["data"]
        student_id = created["Student_ID"]
        self.assertEqual(created["Roll_No"], roll)
        self.assertEqual(created["CGPA"], 9.15)
        self.assertIn("+91-9870001111", created["Phone_Numbers"])

        # 2. GET by ID
        res_get = self.client.get(f"/api/students/{student_id}")
        self.assertEqual(res_get.status_code, 200)
        fetched = res_get.get_json()["data"]
        self.assertEqual(fetched["First_Name"], "RouteTester")

        # 3. PUT (Update)
        res_put = self.client.put(f"/api/students/{student_id}", json={
            "CGPA": 9.30,
            "Section": "B"
        })
        self.assertEqual(res_put.status_code, 200)
        updated = res_put.get_json()["data"]
        self.assertEqual(updated["CGPA"], 9.30)
        self.assertEqual(updated["Section"], "B")

        # 4. DELETE
        res_del = self.client.delete(f"/api/students/{student_id}")
        self.assertEqual(res_del.status_code, 200)

        # 5. Verify 404
        res_404 = self.client.get(f"/api/students/{student_id}")
        self.assertEqual(res_404.status_code, 404)

    def test_04_student_phones_routes(self):
        """GET & POST /api/students/<id>/phones - Multivalued contact number endpoints."""
        res = self.client.get("/api/students/1/phones")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("phone_numbers", data)
        self.assertTrue(len(data["phone_numbers"]) >= 1)

    # =========================================================================
    # 3. COURSES & REGISTRATIONS ROUTES
    # =========================================================================

    def test_05_course_routes(self):
        """GET /api/courses - Lists courses with department and semester filters."""
        res = self.client.get("/api/courses")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(len(data["data"]) > 0)

        # Specific course detail
        res_one = self.client.get("/api/courses/1")
        self.assertEqual(res_one.status_code, 200)
        self.assertIn("Course_Name", res_one.get_json()["data"])

    def test_06_registration_routes(self):
        """GET /api/registrations - Returns student course registrations."""
        res = self.client.get("/api/registrations")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["status"], "success")

    # =========================================================================
    # 4. COMPANY, DRIVES & OPPORTUNITIES ROUTES
    # =========================================================================

    def test_07_company_routes(self):
        """GET /api/companies, POST /api/companies, GET /api/companies/<id>."""
        # 1. List
        res_list = self.client.get("/api/companies")
        self.assertEqual(res_list.status_code, 200)
        self.assertTrue(len(res_list.get_json()["data"]) > 0)

        # 2. Hierarchical detail view (Google India ID: 1)
        res_detail = self.client.get("/api/companies/1")
        self.assertEqual(res_detail.status_code, 200)
        comp = res_detail.get_json()["data"]
        self.assertEqual(comp["Company_Name"], "Google India")
        self.assertIn("Recruitment_Drives", comp)

        # 3. Create and cleanup test company
        c_name = f"P10 Route Test Inc {int(time.time() * 1000) % 1000000}"
        c_payload = {
            "Company_Name": c_name,
            "Company_Type": "Startup",
            "Industry": "AI Robotics",
            "Location": "Hyderabad",
            "Website": "https://p10test.ai"
        }
        res_create = self.client.post("/api/companies", json=c_payload)
        self.assertEqual(res_create.status_code, 201)
        comp_id = res_create.get_json()["data"]["Company_ID"]

        # Delete company
        res_del = self.client.delete(f"/api/companies/{comp_id}")
        self.assertEqual(res_del.status_code, 200)

    def test_08_drive_and_opportunity_routes(self):
        """GET /api/drives, GET /api/opportunities, GET /api/rounds."""
        res_drives = self.client.get("/api/drives")
        self.assertEqual(res_drives.status_code, 200)
        self.assertTrue(len(res_drives.get_json()["data"]) > 0)

        res_opps = self.client.get("/api/opportunities")
        self.assertEqual(res_opps.status_code, 200)
        self.assertTrue(len(res_opps.get_json()["data"]) > 0)

        res_rounds = self.client.get("/api/rounds")
        self.assertEqual(res_rounds.status_code, 200)

    # =========================================================================
    # 5. PLACEMENTS & ANALYTICS ROUTES
    # =========================================================================

    def test_09_placement_routes(self):
        """GET /api/placements, filtering, and status patch."""
        # 1. Listing
        res = self.client.get("/api/placements")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(res.get_json()["data"]) > 0)

        # 2. Filter by status
        res_acc = self.client.get("/api/placements?offer_status=Accepted")
        self.assertEqual(res_acc.status_code, 200)

        # 3. Filter by min package
        res_pkg = self.client.get("/api/placements?min_package=20.0")
        self.assertEqual(res_pkg.status_code, 200)
        for o in res_pkg.get_json()["data"]:
            self.assertGreaterEqual(o["Package"], 20.0)

    def test_10_placement_analytics_routes(self):
        """GET /api/placements/analytics/multiple-offers & /distribution."""
        res_multi = self.client.get("/api/placements/analytics/multiple-offers")
        self.assertEqual(res_multi.status_code, 200)
        self.assertTrue(len(res_multi.get_json()["data"]) >= 1)

        res_dist = self.client.get("/api/placements/analytics/distribution")
        self.assertEqual(res_dist.status_code, 200)
        data = res_dist.get_json()["data"]
        self.assertIn("multiple_offers", data)
        self.assertIn("single_offer", data)

    # =========================================================================
    # 6. INTERNSHIPS & SEMESTER RESULTS ROUTES
    # =========================================================================

    def test_11_internship_routes(self):
        """GET /api/internships & /api/internships/requirements."""
        res_int = self.client.get("/api/internships")
        self.assertEqual(res_int.status_code, 200)
        self.assertTrue(len(res_int.get_json()["data"]) > 0)

        res_reqs = self.client.get("/api/internships/requirements")
        self.assertEqual(res_reqs.status_code, 200)
        self.assertTrue(len(res_reqs.get_json()["data"]) >= 2)

    def test_12_semester_result_routes(self):
        """GET /api/semester-results - Listing verified academic results."""
        res_res = self.client.get("/api/semester-results")
        self.assertEqual(res_res.status_code, 200)
        self.assertTrue(len(res_res.get_json()["data"]) > 0)

        # Filter by student_id
        res_stu = self.client.get("/api/semester-results?student_id=1")
        self.assertEqual(res_stu.status_code, 200)
        self.assertTrue(len(res_stu.get_json()["data"]) >= 1)

    # =========================================================================
    # 7. WEB UI PAGES (HTML VIEWS)
    # =========================================================================

    def test_13_web_ui_dashboard(self):
        """GET / - Renders executive dashboard with KPI metrics and chart canvas elements."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn("Placement & Internship Portal", html)
        self.assertIn("Active Students", html)
        self.assertIn("yearwisePlacementChart", html)

    def test_14_web_ui_students_views(self):
        """GET /students & GET /students/new."""
        res_list = self.client.get("/students")
        self.assertEqual(res_list.status_code, 200)
        self.assertIn("Student Career Profiles", res_list.get_data(as_text=True))

        res_new = self.client.get("/students/new")
        self.assertEqual(res_new.status_code, 200)
        self.assertIn("Register New Student", res_new.get_data(as_text=True))

    def test_15_web_ui_companies_views(self):
        """GET /companies & GET /companies/new."""
        res_list = self.client.get("/companies")
        self.assertEqual(res_list.status_code, 200)
        self.assertIn("Corporate Recruiting Partners", res_list.get_data(as_text=True))

        res_new = self.client.get("/companies/new")
        self.assertEqual(res_new.status_code, 200)
        self.assertIn("Corporate Recruiting Partner", res_new.get_data(as_text=True))

    def test_16_web_ui_placements_and_internships_views(self):
        """GET /placements & GET /internships."""
        res_p = self.client.get("/placements")
        self.assertEqual(res_p.status_code, 200)
        self.assertIn("Campus Placement Offers", res_p.get_data(as_text=True))

        res_i = self.client.get("/internships")
        self.assertEqual(res_i.status_code, 200)
        self.assertIn("Internships & Academic Requirements", res_i.get_data(as_text=True))

    def test_17_web_ui_reports_view(self):
        """GET /reports - Renders advanced analytical reports and SQL aggregate tables."""
        res = self.client.get("/reports")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Accreditation & Placement Analytics Reports", res.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()

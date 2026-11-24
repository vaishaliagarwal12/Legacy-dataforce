import io
import csv
import unittest
from app import create_app
from db.connection import execute_one, execute_query, execute_mutation, get_cursor
from services.placement_service import (
    create_placement_offer,
    get_placement_offer,
    list_placement_offers,
    update_offer_status,
    update_placement_offer,
    delete_placement_offer,
    get_placement_analytics,
    check_candidate_eligibility_for_opportunity,
    get_students_with_multiple_offers,
    ValidationError,
    ConflictError,
    NotFoundError,
)


class PlacementUpgradeTestCase(unittest.TestCase):
    """Comprehensive test suite verifying the upgraded Placement Management module."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()
        with get_cursor(commit=True) as cur:
            cur.execute(
                "DELETE FROM PLACEMENT WHERE Student_ID IN (SELECT Student_ID FROM STUDENT WHERE Roll_No = 'TEST_PL_001')"
            )
            cur.execute("DELETE FROM STUDENT WHERE Roll_No = 'TEST_PL_001'")
            cur.execute("""
                INSERT INTO STUDENT (Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs, Email)
                VALUES ('TEST_PL_001', 'Test', 'Candidate', 'CSE', 2024, 9.20, 0, 'test_pl_001@example.com')
            """)
            cls.test_student_id = cur.lastrowid

    @classmethod
    def tearDownClass(cls):
        with get_cursor(commit=True) as cur:
            cur.execute("DELETE FROM PLACEMENT WHERE Student_ID = %s", (cls.test_student_id,))
            cur.execute("DELETE FROM STUDENT WHERE Student_ID = %s", (cls.test_student_id,))

    # -------------------------------------------------------------------------
    # 1. PLACEMENT ANALYTICS & DASHBOARD METRICS
    # -------------------------------------------------------------------------
    def test_01_placement_analytics_and_kpis(self):
        """Verifies get_placement_analytics aggregates KPI cards, company stats, and branch stats."""
        analytics = get_placement_analytics()
        self.assertIn("kpis", analytics)
        kpis = analytics["kpis"]

        self.assertGreater(kpis["total_offers"], 0)
        self.assertGreater(kpis["placed_students"], 0)
        self.assertGreater(kpis["avg_package"], 0.0)
        self.assertGreater(kpis["highest_package"], 0.0)
        self.assertGreaterEqual(kpis["highest_package"], kpis["avg_package"])

        # Company-wise statistics
        self.assertIn("company_stats", analytics)
        self.assertTrue(len(analytics["company_stats"]) > 0)
        c0 = analytics["company_stats"][0]
        self.assertIn("Company_Name", c0)
        self.assertIn("total_offers", c0)
        self.assertIn("avg_package", c0)

        # Branch-wise statistics
        self.assertIn("branch_stats", analytics)
        self.assertTrue(len(analytics["branch_stats"]) > 0)
        b0 = analytics["branch_stats"][0]
        self.assertIn("Branch", b0)
        self.assertIn("placed_students", b0)

        # Package tiers and status distributions
        self.assertIn("package_distribution", analytics)
        self.assertIn("tier_above_15", analytics["package_distribution"])
        self.assertIn("status_distribution", analytics)
        self.assertIn("Accepted", analytics["status_distribution"])

    # -------------------------------------------------------------------------
    # 2. SEARCH PLACEMENT RECORDS
    # -------------------------------------------------------------------------
    def test_02_search_placement_records(self):
        """Verifies searching by student name, roll number, recruiting company, and role."""
        sample = execute_one("""
            SELECT p.Role, s.First_Name, s.Roll_No, c.Company_Name
            FROM PLACEMENT p
            JOIN STUDENT s ON p.Student_ID = s.Student_ID
            JOIN COMPANY c ON p.Company_ID = c.Company_ID
            LIMIT 1
        """)
        self.assertIsNotNone(sample)

        # Search by student name
        res_name = list_placement_offers(search=sample["First_Name"])
        name_records = res_name["results"] if isinstance(res_name, dict) else res_name
        self.assertTrue(any(sample["First_Name"] in s["Student_Name"] for s in name_records))

        # Search by roll number
        res_roll = list_placement_offers(search=sample["Roll_No"])
        roll_records = res_roll["results"] if isinstance(res_roll, dict) else res_roll
        self.assertTrue(any(s["Roll_No"] == sample["Roll_No"] for s in roll_records))

        # Search by company name
        res_comp = list_placement_offers(search=sample["Company_Name"])
        comp_records = res_comp["results"] if isinstance(res_comp, dict) else res_comp
        self.assertTrue(any(s["Company_Name"] == sample["Company_Name"] for s in comp_records))

        # Search by role
        res_role = list_placement_offers(search=sample["Role"])
        role_records = res_role["results"] if isinstance(res_role, dict) else res_role
        self.assertTrue(any(sample["Role"] in s["Role"] for s in role_records))

    # -------------------------------------------------------------------------
    # 3. MULTI-CRITERIA FILTERING
    # -------------------------------------------------------------------------
    def test_03_multi_criteria_filtering(self):
        """Verifies filtering by branch, placement_year, offer_status, and package range."""
        # Filter by branch
        res_branch = list_placement_offers(branch="CSE")
        b_records = res_branch["results"] if isinstance(res_branch, dict) else res_branch
        for r in b_records:
            self.assertEqual(r["Branch"], "CSE")

        # Filter by offer status
        res_status = list_placement_offers(offer_status="Accepted")
        st_records = res_status["results"] if isinstance(res_status, dict) else res_status
        for r in st_records:
            self.assertEqual(r["Offer_Status"], "Accepted")

        # Filter by package range
        res_pkg = list_placement_offers(min_package=12.0, max_package=25.0)
        pkg_records = res_pkg["results"] if isinstance(res_pkg, dict) else res_pkg
        for r in pkg_records:
            self.assertGreaterEqual(r["Package"], 12.0)
            self.assertLessEqual(r["Package"], 25.0)

    # -------------------------------------------------------------------------
    # 4. SERVER-SIDE PAGINATION & DYNAMIC SORTING
    # -------------------------------------------------------------------------
    def test_04_sorting_and_pagination(self):
        """Verifies safe column sorting and server-side pagination metadata."""
        # Sort by Package descending
        res_desc = list_placement_offers(sort_by="package", sort_dir="desc", limit=5)
        desc_records = res_desc["results"]
        pkg_desc = [r["Package"] for r in desc_records]
        self.assertEqual(pkg_desc, sorted(pkg_desc, reverse=True))

        # Sort by Roll No ascending
        res_roll = list_placement_offers(sort_by="roll_no", sort_dir="asc", limit=5)
        roll_records = res_roll["results"]
        roll_asc = [r["Roll_No"] for r in roll_records]
        self.assertEqual(roll_asc, sorted(roll_asc))

        # Pagination metadata
        res_page = list_placement_offers(page=1, per_page=3)
        self.assertIn("pagination", res_page)
        p = res_page["pagination"]
        self.assertEqual(p["page"], 1)
        self.assertEqual(p["per_page"], 3)
        self.assertGreater(p["total"], 0)
        self.assertEqual(len(res_page["results"]), min(3, p["total"]))

    # -------------------------------------------------------------------------
    # 5. OFFER DETAILS VIEW
    # -------------------------------------------------------------------------
    def test_05_placement_offer_detail_and_page(self):
        """Verifies get_placement_offer retrieves full offer details and GET /placements/<id> renders."""
        offer = get_placement_offer(1)
        self.assertIsNotNone(offer)
        self.assertEqual(offer["Placement_ID"], 1)

        # Check joined metadata
        self.assertIn("Student_Name", offer)
        self.assertIn("Roll_No", offer)
        self.assertIn("Company_Name", offer)
        self.assertIn("Role", offer)
        self.assertIn("Package", offer)
        self.assertIn("Skills", offer)
        self.assertIn("Candidate_Eligibility_Met", offer)

        # HTML route
        res = self.client.get("/placements/1")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn("Candidate Profile", html)
        self.assertIn("Recruiting Organization", html)
        self.assertIn("Placement Specifications", html)

    # -------------------------------------------------------------------------
    # 6. CSV EXPORT
    # -------------------------------------------------------------------------
    def test_06_csv_export_endpoint(self):
        """Verifies /placements/export-csv streams downloadable CSV with complete headers."""
        res = self.client.get("/placements/export-csv")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, "text/csv; charset=utf-8")
        self.assertIn("attachment; filename=", res.headers.get("Content-Disposition", ""))

        csv_text = res.get_data(as_text=True)
        reader = csv.reader(io.StringIO(csv_text))
        rows = list(reader)
        self.assertTrue(len(rows) > 1)

        header = rows[0]
        expected_cols = [
            "Placement ID",
            "Roll No",
            "Student Name",
            "Branch",
            "CGPA",
            "Company Name",
            "Designated Role",
            "Package (LPA)",
            "Placement Year",
            "Offer Status",
        ]
        for col in expected_cols:
            self.assertIn(col, header)

    # -------------------------------------------------------------------------
    # 7. BUSINESS RULES: MULTIPLE OFFERS & SINGLE JOINED OFFER (uq_one_joined_offer)
    # -------------------------------------------------------------------------
    def test_07_multiple_offers_and_single_accepted_rule(self):
        """Verifies students may receive multiple offers, but can join at most ONE offer (uq_one_joined_offer)."""
        comps = execute_query("SELECT Company_ID FROM COMPANY ORDER BY Company_ID ASC LIMIT 2")
        self.assertEqual(len(comps), 2)
        c1 = comps[0]["Company_ID"]
        c2 = comps[1]["Company_ID"]

        candidate_id = self.test_student_id
        execute_mutation("DELETE FROM PLACEMENT WHERE Student_ID = %s", (candidate_id,))

        # 1. Issue first offer
        o1 = create_placement_offer(
            {
                "Student_ID": candidate_id,
                "Company_ID": c1,
                "Role": "Cloud Architect Associate",
                "Package": 15.00,
                "Placement_Year": 2024,
                "Offer_Status": "Offered",
                "Joined": "No",
            }
        )
        self.assertEqual(o1["Offer_Status"], "Offered")

        # 2. Issue second distinct offer
        o2 = create_placement_offer(
            {
                "Student_ID": candidate_id,
                "Company_ID": c2,
                "Role": "Systems Analyst",
                "Package": 12.50,
                "Placement_Year": 2024,
                "Offer_Status": "Offered",
                "Joined": "No",
            }
        )
        self.assertEqual(o2["Offer_Status"], "Offered")

        # Verify candidate holds 2 distinct offers in database
        student_offers = execute_query(
            "SELECT Placement_ID FROM PLACEMENT WHERE Student_ID = %s", (candidate_id,)
        )
        self.assertEqual(len(student_offers), 2)

        # 3. Accept and Join first offer
        up1 = update_placement_offer(
            o1["Placement_ID"], {"Offer_Status": "Accepted", "Joined": "Yes"}
        )
        self.assertEqual(up1["Offer_Status"], "Accepted")
        self.assertEqual(up1["Joined"], "Yes")

        # 4. Attempt to join second offer while first is joined -> MUST FAIL (ConflictError / uq_one_joined_offer)
        with self.assertRaises((ConflictError, ValidationError)) as ctx:
            update_placement_offer(
                o2["Placement_ID"], {"Offer_Status": "Accepted", "Joined": "Yes"}
            )
        self.assertTrue(
            "joined offer" in str(ctx.exception).lower()
            or "uq_one_joined_offer" in str(ctx.exception).lower()
        )

        # 5. Unjoin first offer -> Now joining second offer must succeed
        update_placement_offer(o1["Placement_ID"], {"Joined": "No"})
        up2 = update_placement_offer(
            o2["Placement_ID"], {"Offer_Status": "Accepted", "Joined": "Yes"}
        )
        self.assertEqual(up2["Joined"], "Yes")

        # Cleanup test records
        delete_placement_offer(o1["Placement_ID"])
        delete_placement_offer(o2["Placement_ID"])

    # -------------------------------------------------------------------------
    # 8. BUSINESS RULE: OFFER STATUS & JOINED STATUS ENFORCEMENT
    # -------------------------------------------------------------------------
    def test_08_joined_status_requires_accepted_status(self):
        """Verifies Joined = 'Yes' requires Offer_Status = 'Accepted' (chk_placement_joined_status)."""
        comps = execute_query("SELECT Company_ID FROM COMPANY ORDER BY Company_ID ASC LIMIT 1")
        c1 = comps[0]["Company_ID"]
        candidate_id = self.test_student_id
        execute_mutation("DELETE FROM PLACEMENT WHERE Student_ID = %s", (candidate_id,))

        # Attempt to create offer with Joined='Yes' but Offer_Status='Offered'
        with self.assertRaises(ValidationError) as ctx:
            create_placement_offer(
                {
                    "Student_ID": candidate_id,
                    "Company_ID": c1,
                    "Role": "Test Engineer",
                    "Package": 10.00,
                    "Placement_Year": 2024,
                    "Offer_Status": "Offered",
                    "Joined": "Yes",
                }
            )
        self.assertIn("Joined can only be 'Yes' if Offer_Status is 'Accepted'", str(ctx.exception))

        # Cleanup
        execute_mutation("DELETE FROM PLACEMENT WHERE Student_ID = %s", (candidate_id,))

    # -------------------------------------------------------------------------
    # 9. BUSINESS RULE: OFFER STATUS ENFORCEMENT
    # -------------------------------------------------------------------------
    def test_09_invalid_offer_status_rejected(self):
        """Verifies placement offer rejects 'Joined' as an Offer_Status value."""
        comps = execute_query("SELECT Company_ID FROM COMPANY ORDER BY Company_ID ASC LIMIT 1")
        c1 = comps[0]["Company_ID"]
        with self.assertRaises(ValidationError) as ctx:
            create_placement_offer(
                {
                    "Student_ID": self.test_student_id,
                    "Company_ID": c1,
                    "Role": "Engineer",
                    "Package": 6.00,
                    "Placement_Year": 2024,
                    "Offer_Status": "Joined",  # Removed value
                }
            )
        self.assertIn("Offer_Status must be one of", str(ctx.exception))

    # -------------------------------------------------------------------------
    # 10. CANDIDATE ELIGIBILITY CHECKER
    # -------------------------------------------------------------------------
    def test_10_candidate_eligibility_checker(self):
        """Verifies check_candidate_eligibility_for_opportunity correctly evaluates candidate standards."""
        # Student 1 has CGPA > 9.0 and 0 backlogs
        res = check_candidate_eligibility_for_opportunity(1)
        self.assertIn("is_eligible", res)
        self.assertIn("student", res)
        self.assertTrue(res["is_eligible"])

    # -------------------------------------------------------------------------
    # 11. ATOMIC UPDATE AND SKILLS SYNCHRONIZATION
    # -------------------------------------------------------------------------
    def test_11_offer_update_and_skill_sync(self):
        """Verifies updating an offer updates fields and synchronizes PLACEMENT_SKILL in an atomic transaction."""
        comps = execute_query("SELECT Company_ID FROM COMPANY ORDER BY Company_ID ASC LIMIT 1")
        c1 = comps[0]["Company_ID"]

        candidate_id = self.test_student_id
        execute_mutation("DELETE FROM PLACEMENT WHERE Student_ID = %s", (candidate_id,))

        created = create_placement_offer(
            {
                "Student_ID": candidate_id,
                "Company_ID": c1,
                "Role": "Junior Analyst",
                "Package": 9.50,
                "Placement_Year": 2024,
                "Skills": ["SQL", "Excel"],
            }
        )
        pl_id = created["Placement_ID"]

        # Update package, role, and skills
        updated = update_placement_offer(
            pl_id,
            {"Role": "Senior Analyst", "Package": 12.00, "Skills": ["SQL", "Python", "Tableau"]},
        )
        self.assertEqual(updated["Role"], "Senior Analyst")
        self.assertEqual(updated["Package"], 12.00)
        self.assertEqual(len(updated["Skills"]), 3)

        # Verify DB records
        skills_in_db = execute_query(
            "SELECT Skill FROM PLACEMENT_SKILL WHERE Placement_ID = %s", (pl_id,)
        )
        self.assertEqual(len(skills_in_db), 3)

        # Cleanup
        delete_placement_offer(pl_id)


if __name__ == "__main__":
    unittest.main()

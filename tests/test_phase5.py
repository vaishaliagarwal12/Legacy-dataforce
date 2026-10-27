import unittest
from app import create_app
from db.connection import execute_one, execute_query


class Phase5RecruitmentPipelineTestCase(unittest.TestCase):
    """Test suite for Phase 5: Companies, Drives, Opportunities (with Branches Transaction), Rounds, and FK chain."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()

    # -------------------------------------------------------------------------
    # 1. COMPANY TESTS
    # -------------------------------------------------------------------------
    def test_01_create_company(self):
        """Tests creating a new recruiting organization."""
        payload = {
            "Company_Name": "Atlassian Software Systems",
            "Company_Type": "Product",
            "Industry": "Enterprise Software",
            "Location": "Bengaluru",
            "Website": "https://careers.atlassian.com"
        }
        res = self.client.post("/api/companies", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()["data"]
        self.assertEqual(data["Company_Name"], "Atlassian Software Systems")
        self.assertEqual(data["Company_Type"], "Product")

    def test_02_company_detail_view_hierarchical(self):
        """CRITICAL: Verifies company detail view lists all drives, opportunities, branches, and rounds."""
        # Google India (ID: 1) has multiple drives and opportunities in seed.sql
        res = self.client.get("/api/companies/1")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        self.assertEqual(data["Company_Name"], "Google India")
        self.assertIn("Recruitment_Drives", data)
        self.assertTrue(len(data["Recruitment_Drives"]) >= 1)

        # Inspect opportunities inside first drive
        drive = data["Recruitment_Drives"][0]
        self.assertIn("Opportunities", drive)
        self.assertTrue(len(drive["Opportunities"]) >= 1)

        opp = drive["Opportunities"][0]
        self.assertIn("Eligible_Branches", opp)
        self.assertIn("Selection_Rounds", opp)

    def test_03_company_delete_blocking_with_active_drives_or_offers(self):
        """Verifies deleting a company with registered drives or placement history is BLOCKED (HTTP 409)."""
        res = self.client.delete("/api/companies/1")
        self.assertEqual(res.status_code, 409)
        self.assertIn("recruitment drive(s) are registered", res.get_json()["message"])

    # -------------------------------------------------------------------------
    # 2. RECRUITMENT DRIVE TESTS
    # -------------------------------------------------------------------------
    def test_04_create_and_filter_recruitment_drives(self):
        """Tests recruitment drive scheduling and filtering by season/type."""
        company = execute_one("SELECT Company_ID FROM COMPANY WHERE Company_Name = 'Atlassian Software Systems'")
        comp_id = company["Company_ID"]

        drive_payload = {
            "Company_ID": comp_id,
            "Drive_Year": 2026,
            "Drive_Type": "Both",
            "Season": "Autumn",
            "Drive_Date": "2026-09-15"
        }
        res = self.client.post("/api/drives", json=drive_payload)
        self.assertEqual(res.status_code, 201)
        drive_id = res.get_json()["data"]["Drive_ID"]

        # Filter drives
        filter_res = self.client.get(f"/api/drives?company_id={comp_id}&season=Autumn")
        self.assertEqual(filter_res.status_code, 200)
        drives = filter_res.get_json()["data"]
        self.assertEqual(len(drives), 1)
        self.assertEqual(drives[0]["Drive_ID"], drive_id)

    # -------------------------------------------------------------------------
    # 3. OPPORTUNITY + ELIGIBILITY + MULTIPLE BRANCHES (TRANSACTION)
    # -------------------------------------------------------------------------
    def test_05_create_opportunity_with_branches_in_atomic_transaction(self):
        """CRITICAL: Verifies Opportunity, Eligibility, and multiple ELIGIBILITY_BRANCH rows are saved atomically."""
        company = execute_one("SELECT Company_ID FROM COMPANY WHERE Company_Name = 'Atlassian Software Systems'")
        drive = execute_one("SELECT Drive_ID FROM RECRUITMENT_DRIVE WHERE Company_ID = %s", (company["Company_ID"],))
        drive_id = drive["Drive_ID"]

        opp_payload = {
            "Drive_ID": drive_id,
            "Role": "Site Reliability Engineer I",
            "Opportunity_Type": "Placement",
            "Package_Stipend": 26.50,
            "Duration_Months": None,
            "Minimum_CGPA": 8.00,
            "Max_Backlogs": 0,
            "Other_Criteria": "Solid Unix & networking fundamentals",
            "Eligible_Branches": ["CSE", "IT", "ECE"]
        }
        res = self.client.post("/api/opportunities", json=opp_payload)
        self.assertEqual(res.status_code, 201)
        opp_data = res.get_json()["data"]
        opp_id = opp_data["Opportunity_ID"]
        self.assertEqual(opp_data["Role"], "Site Reliability Engineer I")
        self.assertEqual(opp_data["Package_Stipend"], 26.50)
        self.assertEqual(opp_data["Minimum_CGPA"], 8.00)

        # Verify branches in response
        self.assertCountEqual(opp_data["Eligible_Branches"], ["CSE", "IT", "ECE"])

        # Directly verify database tables to guarantee transaction persisted all 3 tables
        opp_row = execute_one("SELECT * FROM OPPORTUNITY WHERE Opportunity_ID = %s", (opp_id,))
        self.assertIsNotNone(opp_row)

        elig_row = execute_one("SELECT * FROM ELIGIBILITY WHERE Opportunity_ID = %s", (opp_id,))
        self.assertIsNotNone(elig_row)
        self.assertEqual(float(elig_row["Minimum_CGPA"]), 8.00)

        branch_rows = execute_query("SELECT Branch FROM ELIGIBILITY_BRANCH WHERE Eligibility_ID = %s", (elig_row["Eligibility_ID"],))
        saved_branches = [b["Branch"] for b in branch_rows]
        self.assertCountEqual(saved_branches, ["CSE", "IT", "ECE"])

    def test_06_update_opportunity_and_branches_transaction(self):
        """Verifies updating opportunity details and synchronizing the multiple branches table."""
        opp = execute_one("SELECT Opportunity_ID FROM OPPORTUNITY WHERE Role = 'Site Reliability Engineer I'")
        opp_id = opp["Opportunity_ID"]

        update_payload = {
            "Package_Stipend": 28.00,
            "Minimum_CGPA": 8.25,
            "Eligible_Branches": ["CSE", "IT"]  # Removed ECE
        }
        res = self.client.put(f"/api/opportunities/{opp_id}", json=update_payload)
        self.assertEqual(res.status_code, 200)
        opp_data = res.get_json()["data"]
        self.assertEqual(opp_data["Package_Stipend"], 28.00)
        self.assertEqual(opp_data["Minimum_CGPA"], 8.25)
        self.assertCountEqual(opp_data["Eligible_Branches"], ["CSE", "IT"])

    # -------------------------------------------------------------------------
    # 4. SELECTION ROUNDS TESTS
    # -------------------------------------------------------------------------
    def test_07_selection_rounds_lifecycle_and_uniqueness(self):
        """Tests adding selection process rounds, validating round order, and handling duplicate round numbers."""
        opp = execute_one("SELECT Opportunity_ID FROM OPPORTUNITY WHERE Role = 'Site Reliability Engineer I'")
        opp_id = opp["Opportunity_ID"]

        # Round 1
        r1 = self.client.post("/api/rounds", json={
            "Opportunity_ID": opp_id,
            "Round_Number": 1,
            "Round_Type": "Coding Round",
            "Description": "Online coding screen on HackerRank"
        })
        self.assertEqual(r1.status_code, 201)

        # Duplicate Round 1 -> Conflict (409)
        r1_dup = self.client.post("/api/rounds", json={
            "Opportunity_ID": opp_id,
            "Round_Number": 1,
            "Round_Type": "Technical Interview"
        })
        self.assertEqual(r1_dup.status_code, 409)

        # Round 2
        r2 = self.client.post("/api/rounds", json={
            "Opportunity_ID": opp_id,
            "Round_Number": 2,
            "Round_Type": "Technical Interview",
            "Description": "Systems and Concurrency Architecture"
        })
        self.assertEqual(r2.status_code, 201)

        # List rounds for opportunity
        list_res = self.client.get(f"/api/rounds?opportunity_id={opp_id}")
        self.assertEqual(list_res.status_code, 200)
        rounds = list_res.get_json()["data"]
        self.assertEqual(len(rounds), 2)
        self.assertEqual(rounds[0]["Round_Number"], 1)
        self.assertEqual(rounds[1]["Round_Number"], 2)

    # -------------------------------------------------------------------------
    # 5. FOREIGN KEY CHAIN INTEGRITY TESTS
    # -------------------------------------------------------------------------
    def test_08_foreign_key_chain_company_drive_opportunity_round(self):
        """Tests foreign key integrity across company -> drive -> opportunity -> round."""
        # 1. Drive creation fails if Company does not exist
        bad_drive = self.client.post("/api/drives", json={
            "Company_ID": 999999,
            "Drive_Year": 2026,
            "Drive_Type": "Placement",
            "Season": "Autumn"
        })
        self.assertEqual(bad_drive.status_code, 404)

        # 2. Opportunity creation fails if Drive does not exist
        bad_opp = self.client.post("/api/opportunities", json={
            "Drive_ID": 999999,
            "Role": "Ghost Role",
            "Opportunity_Type": "Placement",
            "Package_Stipend": 15.0
        })
        self.assertEqual(bad_opp.status_code, 404)

        # 3. Round creation fails if Opportunity does not exist
        bad_round = self.client.post("/api/rounds", json={
            "Opportunity_ID": 999999,
            "Round_Number": 1,
            "Round_Type": "Coding Round"
        })
        self.assertEqual(bad_round.status_code, 404)

    def test_09_clean_teardown_of_test_hierarchy(self):
        """Tests clean top-to-bottom teardown of unreferenced test hierarchy."""
        opp = execute_one("SELECT Opportunity_ID FROM OPPORTUNITY WHERE Role = 'Site Reliability Engineer I'")
        drive = execute_one("SELECT rd.Drive_ID, rd.Company_ID FROM RECRUITMENT_DRIVE rd JOIN OPPORTUNITY o ON rd.Drive_ID = o.Drive_ID WHERE o.Opportunity_ID = %s", (opp["Opportunity_ID"],))

        # Delete Opportunity (cascades to Eligibility, Eligibility_Branch, Rounds)
        del_opp = self.client.delete(f"/api/opportunities/{opp['Opportunity_ID']}")
        self.assertEqual(del_opp.status_code, 200)

        # Delete Drive
        del_drive = self.client.delete(f"/api/drives/{drive['Drive_ID']}")
        self.assertEqual(del_drive.status_code, 200)

        # Delete Company
        del_comp = self.client.delete(f"/api/companies/{drive['Company_ID']}")
        self.assertEqual(del_comp.status_code, 200)


if __name__ == "__main__":
    unittest.main()

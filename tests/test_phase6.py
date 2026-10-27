import unittest
from app import create_app
from db.connection import execute_one, execute_query


class Phase6PlacementOffersTestCase(unittest.TestCase):
    """Test suite for Phase 6: Placement offers, status updates, duplicate rejection, and single-accepted-offer rule."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()

    # -------------------------------------------------------------------------
    # 1. OPPORTUNITY TYPE ENFORCEMENT (RULE 3)
    # -------------------------------------------------------------------------
    def test_01_block_placement_offer_for_internship_opportunity(self):
        """CRITICAL: Enforces that placement offers CANNOT be issued for 'Internship' opportunity types."""
        # Opportunity 1 is an Internship ('System Engineer Intern' in seed.sql)
        intern_opp = execute_one("SELECT Opportunity_ID FROM OPPORTUNITY WHERE Opportunity_Type = 'Internship' LIMIT 1")
        self.assertIsNotNone(intern_opp)

        payload = {
            "Student_ID": 5,  # Rohan (ME) has 0 offers
            "Company_ID": 6,  # TCS
            "Opportunity_ID": intern_opp["Opportunity_ID"],
            "Package": 12.00,
            "Placement_Year": 2024,
            "Offer_Status": "Offered"
        }
        res = self.client.post("/api/placements", json=payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("is of type 'Internship'", res.get_json()["message"])

    # -------------------------------------------------------------------------
    # 2. PRESERVE EVERY OFFER AS ITS OWN RECORD & DUPLICATE BLOCKING (RULE 1)
    # -------------------------------------------------------------------------
    def test_02_create_first_offer_for_opportunity(self):
        """Tests issuing a legitimate placement offer for an opportunity of type 'Placement'."""
        placement_opp = execute_one("SELECT Opportunity_ID, Drive_ID FROM OPPORTUNITY WHERE Opportunity_Type = 'Placement' LIMIT 1")
        drive = execute_one("SELECT Company_ID FROM RECRUITMENT_DRIVE WHERE Drive_ID = %s", (placement_opp["Drive_ID"],))

        # Use Student 8 (Pooja, ECE) who has zero offers
        payload = {
            "Student_ID": 8,
            "Company_ID": drive["Company_ID"],
            "Opportunity_ID": placement_opp["Opportunity_ID"],
            "Role": "Digital Specialist Engineer",
            "Package": 8.50,
            "Placement_Year": 2024,
            "Offer_Status": "Offered",
            "Skills": ["Java", "SQL"]
        }
        res = self.client.post("/api/placements", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()["data"]
        self.assertEqual(data["Student_ID"], 8)
        self.assertEqual(data["Package"], 8.50)
        self.assertEqual(data["Offer_Status"], "Offered")
        self.assertIn("Java", data["Skills"])

    def test_03_block_duplicate_offer_for_same_opportunity(self):
        """CRITICAL: Enforces that duplicate placement offers for the same opportunity to the same student are BLOCKED (HTTP 409)."""
        placement_opp = execute_one("SELECT Opportunity_ID, Drive_ID FROM OPPORTUNITY WHERE Opportunity_Type = 'Placement' LIMIT 1")
        drive = execute_one("SELECT Company_ID FROM RECRUITMENT_DRIVE WHERE Drive_ID = %s", (placement_opp["Drive_ID"],))

        # Attempt to issue the SAME opportunity to Student 8 a second time
        dup_payload = {
            "Student_ID": 8,
            "Company_ID": drive["Company_ID"],
            "Opportunity_ID": placement_opp["Opportunity_ID"],
            "Role": "Digital Specialist Engineer",
            "Package": 9.00,
            "Placement_Year": 2024,
            "Offer_Status": "Offered"
        }
        res = self.client.post("/api/placements", json=dup_payload)
        self.assertEqual(res.status_code, 409)
        self.assertIn("Duplicate offer rejected", res.get_json()["message"])

    # -------------------------------------------------------------------------
    # 3. SINGLE ACCEPTED OFFER RULE (RULE 2)
    # -------------------------------------------------------------------------
    def test_04_multiple_offers_preserved_as_separate_records(self):
        """Verifies a student can receive a distinct second offer from a different company/opportunity."""
        # Find another company and distinct placement opportunity
        diff_opp = execute_query("SELECT Opportunity_ID, Drive_ID FROM OPPORTUNITY WHERE Opportunity_Type = 'Placement' LIMIT 2")[1]
        drive = execute_one("SELECT Company_ID FROM RECRUITMENT_DRIVE WHERE Drive_ID = %s", (diff_opp["Drive_ID"],))

        second_payload = {
            "Student_ID": 8,
            "Company_ID": drive["Company_ID"],
            "Opportunity_ID": diff_opp["Opportunity_ID"],
            "Role": "Associate Cloud Engineer",
            "Package": 11.00,
            "Placement_Year": 2024,
            "Offer_Status": "Offered"
        }
        res = self.client.post("/api/placements", json=second_payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()["data"]
        self.assertEqual(data["Package"], 11.00)

        # Confirm student 8 now has 2 distinct offers preserved in database
        offers = execute_query("SELECT Placement_ID, Package, Offer_Status FROM PLACEMENT WHERE Student_ID = 8")
        self.assertEqual(len(offers), 2)

    def test_05_accept_first_offer_and_block_accepting_second_offer(self):
        """CRITICAL: Enforces that at most ONE Accepted offer is allowed per student."""
        offers = execute_query("SELECT Placement_ID FROM PLACEMENT WHERE Student_ID = 8 ORDER BY Placement_ID ASC")
        offer_id_1 = offers[0]["Placement_ID"]
        offer_id_2 = offers[1]["Placement_ID"]

        # Accept Offer 1 -> Must succeed (200)
        res_accept_1 = self.client.patch(f"/api/placements/{offer_id_1}/status", json={"Offer_Status": "Accepted"})
        self.assertEqual(res_accept_1.status_code, 200)
        self.assertEqual(res_accept_1.get_json()["data"]["Offer_Status"], "Accepted")

        # Attempt to accept Offer 2 while Offer 1 is still Accepted -> MUST FAIL (HTTP 409 Conflict)
        res_accept_2 = self.client.patch(f"/api/placements/{offer_id_2}/status", json={"Offer_Status": "Accepted"})
        self.assertEqual(res_accept_2.status_code, 409)
        self.assertIn("already has an accepted offer", res_accept_2.get_json()["message"])

    def test_06_decline_first_offer_allows_accepting_second_offer(self):
        """Verifies declining the previously accepted offer frees the student to accept another offer."""
        offers = execute_query("SELECT Placement_ID FROM PLACEMENT WHERE Student_ID = 8 ORDER BY Placement_ID ASC")
        offer_id_1 = offers[0]["Placement_ID"]
        offer_id_2 = offers[1]["Placement_ID"]

        # Decline Offer 1
        res_decline_1 = self.client.patch(f"/api/placements/{offer_id_1}/status", json={"Offer_Status": "Declined"})
        self.assertEqual(res_decline_1.status_code, 200)
        self.assertEqual(res_decline_1.get_json()["data"]["Offer_Status"], "Declined")
        self.assertEqual(res_decline_1.get_json()["data"]["Joined"], "No")

        # Now accept Offer 2 -> Must succeed (200)
        res_accept_2 = self.client.patch(f"/api/placements/{offer_id_2}/status", json={"Offer_Status": "Accepted"})
        self.assertEqual(res_accept_2.status_code, 200)
        self.assertEqual(res_accept_2.get_json()["data"]["Offer_Status"], "Accepted")

    # -------------------------------------------------------------------------
    # 4. STATUS UPDATES & JOINED SYNCHRONIZATION
    # -------------------------------------------------------------------------
    def test_07_status_joined_synchronization(self):
        """Verifies setting status to 'Joined' sets Joined = 'Yes'."""
        offers = execute_query("SELECT Placement_ID FROM PLACEMENT WHERE Student_ID = 8 ORDER BY Placement_ID ASC")
        offer_id_2 = offers[1]["Placement_ID"]

        res = self.client.patch(f"/api/placements/{offer_id_2}/status", json={"Offer_Status": "Joined"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        self.assertEqual(data["Offer_Status"], "Joined")
        self.assertEqual(data["Joined"], "Yes")

    # -------------------------------------------------------------------------
    # 5. ANALYTICAL QUERIES FOR STUDENTS WITH SEVERAL OFFERS
    # -------------------------------------------------------------------------
    def test_08_query_students_with_several_offers(self):
        """Tests analytical endpoint retrieving all students holding multiple offers."""
        res = self.client.get("/api/placements/analytics/multiple-offers?min_offers=2")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        self.assertTrue(len(data) >= 10)  # Seed data has 10 students with 2 or 3 offers

        # Verify Student 1 (Aarav) who has 3 offers
        aarav = next((s for s in data if s["Roll_No"] == "CS202001"), None)
        self.assertIsNotNone(aarav)
        self.assertEqual(aarav["Total_Offers"], 3)
        self.assertEqual(aarav["Accepted_Company"], "Google India")
        self.assertEqual(aarav["Highest_Package"], 32.50)

    def test_09_query_offer_distribution(self):
        """Tests offer distribution summary across student population."""
        res = self.client.get("/api/placements/analytics/distribution")
        self.assertEqual(res.status_code, 200)
        summary = res.get_json()["data"]
        self.assertIn("zero_offers", summary)
        self.assertIn("single_offer", summary)
        self.assertIn("multiple_offers", summary)
        self.assertGreater(summary["multiple_offers"], 0)

    # -------------------------------------------------------------------------
    # 6. TEARDOWN TEST PLACEMENTS
    # -------------------------------------------------------------------------
    def test_10_cleanup_test_offers(self):
        """Cleans up temporary offers created for Student 8."""
        offers = execute_query("SELECT Placement_ID FROM PLACEMENT WHERE Student_ID = 8")
        for o in offers:
            del_res = self.client.delete(f"/api/placements/{o['Placement_ID']}")
            self.assertEqual(del_res.status_code, 200)


if __name__ == "__main__":
    unittest.main()

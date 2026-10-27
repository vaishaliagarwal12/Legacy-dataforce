import unittest
import json
from app import create_app
from db.connection import execute_one, execute_query


class Phase4APITestCase(unittest.TestCase):
    """Comprehensive test suite for Phase 4 CRUD, Search, Filter, and Safe Deletion."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()

    # -------------------------------------------------------------------------
    # 1. STUDENT TESTS
    # -------------------------------------------------------------------------
    def test_01_create_student_with_phones(self):
        """Tests student creation with phone numbers in the separate table."""
        payload = {
            "Roll_No": "TEST2026_01",
            "First_Name": "Riddhima",
            "Last_Name": "Sen",
            "Branch": "CSE",
            "Batch_Year": 2026,
            "Section": "A",
            "CGPA": 9.25,
            "Backlogs": 0,
            "Email": "riddhima.sen@test.edu",
            "Resume_Link": "https://storage.test.edu/resumes/riddhima.pdf",
            "Phone_Numbers": ["+91 9876543210", "+91 9876543211"]
        }
        res = self.client.post("/api/students", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()["data"]
        self.assertEqual(data["Roll_No"], "TEST2026_01")
        self.assertEqual(data["CGPA"], 9.25)
        self.assertIn("+91 9876543210", data["Phone_Numbers"])
        self.assertIn("+91 9876543211", data["Phone_Numbers"])

    def test_02_create_student_duplicate_roll_conflict(self):
        """Tests that creating a student with an existing Roll_No returns HTTP 409."""
        payload = {
            "Roll_No": "TEST2026_01",
            "First_Name": "Duplicate",
            "Branch": "CSE",
            "Batch_Year": 2026,
            "CGPA": 8.0,
            "Email": "duplicate.roll@test.edu",
        }
        res = self.client.post("/api/students", json=payload)
        self.assertEqual(res.status_code, 409)
        self.assertIn("already exists", res.get_json()["message"])

    def test_03_create_student_validation_failure(self):
        """Tests that invalid CGPA or invalid email triggers HTTP 400 validation error."""
        payload = {
            "Roll_No": "INVALID_01",
            "First_Name": "Invalid",
            "Branch": "CSE",
            "Batch_Year": 2026,
            "CGPA": 14.50,  # Invalid: > 10.0
            "Email": "invalid-email-format",
        }
        res = self.client.post("/api/students", json=payload)
        self.assertEqual(res.status_code, 400)

    def test_04_get_student_detail(self):
        """Tests viewing single student with rich related entities."""
        res = self.client.get("/api/students/1")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        self.assertEqual(data["Roll_No"], "CS202001")
        self.assertGreater(data["Placement_Count"], 0)
        self.assertGreater(data["Internship_Count"], 0)
        self.assertFalse(data["Is_Deletable"])

    def test_05_search_and_filter_students(self):
        """Tests dynamic student filtering by branch and minimum CGPA."""
        res = self.client.get("/api/students?branch=CSE&min_cgpa=9.0&limit=10")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(len(json_data["data"]) > 0)
        for s in json_data["data"]:
            self.assertEqual(s["Branch"], "CSE")
            self.assertGreaterEqual(s["CGPA"], 9.0)

    def test_06_update_student(self):
        """Tests updating student details and modifying phone numbers."""
        student_id = execute_one("SELECT Student_ID FROM STUDENT WHERE Roll_No = 'TEST2026_01'")["Student_ID"]
        update_payload = {
            "First_Name": "Riddhima Updated",
            "CGPA": 9.40,
            "Phone_Numbers": ["+91 9999988888"]
        }
        res = self.client.put(f"/api/students/{student_id}", json=update_payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        self.assertEqual(data["First_Name"], "Riddhima Updated")
        self.assertEqual(data["CGPA"], 9.40)
        self.assertEqual(data["Phone_Numbers"], ["+91 9999988888"])

    def test_07_block_safe_delete_for_student_with_placement_or_internship(self):
        """CRITICAL: Verifies that deleting a student with placements/internships is BLOCKED (HTTP 409)."""
        # Student 1 (Aarav) has 3 placement offers and 3 internship records in seed.sql
        res = self.client.delete("/api/students/1")
        self.assertEqual(res.status_code, 409)
        msg = res.get_json()["message"]
        self.assertIn("Active career history detected", msg)
        self.assertIn("placement offer(s)", msg)
        self.assertIn("internship record(s)", msg)

    def test_08_safe_delete_allowed_for_student_without_history(self):
        """Tests that a student with NO placements or internships can be safely deleted."""
        student_id = execute_one("SELECT Student_ID FROM STUDENT WHERE Roll_No = 'TEST2026_01'")["Student_ID"]
        res = self.client.delete(f"/api/students/{student_id}")
        self.assertEqual(res.status_code, 200)
        self.assertIn("safely deleted", res.get_json()["message"])

        # Verify no longer in database
        check = execute_one("SELECT * FROM STUDENT WHERE Student_ID = %s", (student_id,))
        self.assertIsNone(check)

    # -------------------------------------------------------------------------
    # 2. COURSE TESTS
    # -------------------------------------------------------------------------
    def test_09_create_view_and_filter_courses(self):
        """Tests course creation, filtering by department, and viewing enrolled students."""
        payload = {
            "University_ID": 1,
            "Course_Name": "Cloud Distributed Systems",
            "Department": "Computer Science",
            "Semester": 6,
            "Credits": 4,
            "Course_Type": "Elective"
        }
        res = self.client.post("/api/courses", json=payload)
        self.assertEqual(res.status_code, 201)
        course_id = res.get_json()["data"]["Course_ID"]

        # View course
        get_res = self.client.get(f"/api/courses/{course_id}")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.get_json()["data"]["Course_Name"], "Cloud Distributed Systems")

        # Filter courses
        filter_res = self.client.get("/api/courses?department=Computer Science&course_type=Elective")
        self.assertEqual(filter_res.status_code, 200)
        self.assertTrue(len(filter_res.get_json()["data"]) >= 1)

    # -------------------------------------------------------------------------
    # 3. REGISTRATION TESTS
    # -------------------------------------------------------------------------
    def test_10_register_student_course_and_update_grade(self):
        """Tests enrolling a student in a course, viewing enrollment, and updating grade."""
        course = execute_one("SELECT Course_ID FROM COURSE WHERE Course_Name = 'Cloud Distributed Systems'")
        course_id = course["Course_ID"]

        reg_payload = {
            "Student_ID": 2,
            "Course_ID": course_id,
            "Enrollment_Year": 2024,
            "Grade": "A"
        }
        res = self.client.post("/api/registrations", json=reg_payload)
        self.assertEqual(res.status_code, 201)

        # Update grade
        put_res = self.client.put(f"/api/registrations/2/{course_id}", json={"Grade": "A+"})
        self.assertEqual(put_res.status_code, 200)
        self.assertEqual(put_res.get_json()["data"]["Grade"], "A+")

        # Block course deletion when student is registered
        del_course_res = self.client.delete(f"/api/courses/{course_id}")
        self.assertEqual(del_course_res.status_code, 409)
        self.assertIn("active student registration", del_course_res.get_json()["message"])

        # Unregister student
        unreg_res = self.client.delete(f"/api/registrations/2/{course_id}")
        self.assertEqual(unreg_res.status_code, 200)

        # Now deleting course succeeds
        del_course_ok = self.client.delete(f"/api/courses/{course_id}")
        self.assertEqual(del_course_ok.status_code, 200)

    # -------------------------------------------------------------------------
    # 4. STUDENT PROFILE TESTS
    # -------------------------------------------------------------------------
    def test_11_student_profile_lifecycle(self):
        """Tests creating, searching, updating, and deleting student profile items."""
        profile_payload = {
            "Student_ID": 2,
            "Profile_Type": "Project",
            "Title": "Autonomous Warehouse Robot",
            "Description": "ROS2 based obstacle avoidance and swarm dispatching",
            "Link": "https://github.com/fictional/warehouse-robot",
            "Year": 2024,
            "Proficiency_Level": "Advanced"
        }
        res = self.client.post("/api/profiles", json=profile_payload)
        self.assertEqual(res.status_code, 201)
        profile_id = res.get_json()["data"]["Profile_ID"]

        # Filter by profile type
        filter_res = self.client.get(f"/api/profiles?student_id=2&profile_type=Project")
        self.assertEqual(filter_res.status_code, 200)
        self.assertTrue(len(filter_res.get_json()["data"]) >= 1)

        # Update profile
        update_res = self.client.put(f"/api/profiles/{profile_id}", json={"Proficiency_Level": "Expert"})
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.get_json()["data"]["Proficiency_Level"], "Expert")

        # Delete profile
        del_res = self.client.delete(f"/api/profiles/{profile_id}")
        self.assertEqual(del_res.status_code, 200)

    # -------------------------------------------------------------------------
    # 5. PHONE NUMBERS SEPARATE TABLE ENDPOINTS
    # -------------------------------------------------------------------------
    def test_12_student_phones_management(self):
        """Tests managing contact numbers via dedicated separate table routes."""
        add_res = self.client.post("/api/students/2/phones", json={"phone_no": "+91 9123456789"})
        self.assertEqual(add_res.status_code, 201)

        # List phones
        list_res = self.client.get("/api/students/2/phones")
        self.assertEqual(list_res.status_code, 200)
        self.assertIn("+91 9123456789", list_res.get_json()["phone_numbers"])

        # Delete phone
        del_res = self.client.delete("/api/students/2/phones/+91 9123456789")
        self.assertEqual(del_res.status_code, 200)


if __name__ == "__main__":
    unittest.main()

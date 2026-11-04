import io
import csv
import unittest
from app import create_app
from db.connection import execute_one, execute_query
from services.student_service import (
    get_student,
    list_students,
    create_student,
    update_student,
    delete_student,
    ValidationError,
    ConflictError,
    ProtectedDeleteError,
    NotFoundError,
)


class StudentUpgradeTestCase(unittest.TestCase):
    """Comprehensive test suite for the upgraded Student Management module."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()

    # -------------------------------------------------------------------------
    # 1. ADVANCED SEARCH
    # -------------------------------------------------------------------------
    def test_01_search_by_first_and_last_name(self):
        """Verifies advanced search matches first name, last name, and full concatenated name."""
        # Find an existing student to test with
        student = execute_one("SELECT First_Name, Last_Name, Roll_No, Email FROM STUDENT LIMIT 1")
        self.assertIsNotNone(student)

        # Search by First Name
        res_first = list_students(search=student["First_Name"])
        first_records = res_first["results"] if isinstance(res_first, dict) else res_first
        self.assertTrue(any(s["First_Name"] == student["First_Name"] for s in first_records))

        # Search by Full Name
        if student.get("Last_Name"):
            full_name = f"{student['First_Name']} {student['Last_Name']}"
            res_full = list_students(search=full_name)
            full_records = res_full["results"] if isinstance(res_full, dict) else res_full
            self.assertTrue(any(s["Roll_No"] == student["Roll_No"] for s in full_records))

    def test_02_search_by_roll_and_email(self):
        """Verifies searching by exact or partial roll number and email address."""
        student = execute_one("SELECT Roll_No, Email FROM STUDENT LIMIT 1")
        self.assertIsNotNone(student)

        # Search by Roll Number
        res_roll = list_students(search=student["Roll_No"])
        roll_records = res_roll["results"] if isinstance(res_roll, dict) else res_roll
        self.assertTrue(any(s["Roll_No"] == student["Roll_No"] for s in roll_records))

        # Search by Email username
        email_prefix = student["Email"].split("@")[0]
        res_email = list_students(search=email_prefix)
        email_records = res_email["results"] if isinstance(res_email, dict) else res_email
        self.assertTrue(any(s["Email"] == student["Email"] for s in email_records))

    # -------------------------------------------------------------------------
    # 2. FILTERS (BRANCH, BATCH YEAR, CGPA RANGE, PLACEMENT STATUS)
    # -------------------------------------------------------------------------
    def test_03_filter_by_branch_and_batch_year(self):
        """Verifies filtering student records by department branch and batch year."""
        sample = execute_one("SELECT Branch, Batch_Year FROM STUDENT LIMIT 1")
        branch = sample["Branch"]
        batch = sample["Batch_Year"]

        res = list_students(branch=branch, batch_year=batch)
        records = res["results"] if isinstance(res, dict) else res
        self.assertTrue(len(records) > 0)
        for s in records:
            self.assertEqual(s["Branch"], branch)
            self.assertEqual(s["Batch_Year"], batch)

    def test_04_filter_by_cgpa_range(self):
        """Verifies filtering students within min_cgpa and max_cgpa boundaries."""
        res_min = list_students(min_cgpa=8.0)
        min_records = res_min["results"] if isinstance(res_min, dict) else res_min
        for s in min_records:
            self.assertGreaterEqual(s["CGPA"], 8.0)

        res_max = list_students(max_cgpa=8.5)
        max_records = res_max["results"] if isinstance(res_max, dict) else res_max
        for s in max_records:
            self.assertLessEqual(s["CGPA"], 8.5)

        res_range = list_students(min_cgpa=7.5, max_cgpa=9.0)
        range_records = res_range["results"] if isinstance(res_range, dict) else res_range
        for s in range_records:
            self.assertGreaterEqual(s["CGPA"], 7.5)
            self.assertLessEqual(s["CGPA"], 9.0)

    def test_05_filter_by_placement_status(self):
        """Verifies filtering by Placed, Unplaced, and Multiple offer statuses."""
        # Placed
        res_placed = list_students(placement_status="Placed")
        placed_records = res_placed["results"] if isinstance(res_placed, dict) else res_placed
        for s in placed_records:
            self.assertGreater(s["Placement_Offers"], 0)

        # Unplaced
        res_unplaced = list_students(placement_status="Unplaced")
        unplaced_records = (
            res_unplaced["results"] if isinstance(res_unplaced, dict) else res_unplaced
        )
        for s in unplaced_records:
            self.assertEqual(s["Placement_Offers"], 0)

        # Multiple Offers
        res_multi = list_students(placement_status="Multiple")
        multi_records = res_multi["results"] if isinstance(res_multi, dict) else res_multi
        for s in multi_records:
            self.assertGreaterEqual(s["Placement_Offers"], 2)

    # -------------------------------------------------------------------------
    # 3. PAGINATION AND SORTING
    # -------------------------------------------------------------------------
    def test_06_sorting_and_pagination(self):
        """Verifies column sorting and server-side pagination metadata."""
        # Sort by CGPA descending
        res_desc = list_students(sort_by="cgpa", sort_dir="desc", limit=10)
        records_desc = res_desc["results"] if isinstance(res_desc, dict) else res_desc
        cgpa_vals = [s["CGPA"] for s in records_desc]
        self.assertEqual(cgpa_vals, sorted(cgpa_vals, reverse=True))

        # Sort by Roll No ascending
        res_roll = list_students(sort_by="roll_no", sort_dir="asc", limit=10)
        records_roll = res_roll["results"] if isinstance(res_roll, dict) else res_roll
        roll_vals = [s["Roll_No"] for s in records_roll]
        self.assertEqual(roll_vals, sorted(roll_vals))

        # Pagination metadata
        res_page = list_students(page=1, per_page=3)
        self.assertIn("pagination", res_page)
        p = res_page["pagination"]
        self.assertEqual(p["page"], 1)
        self.assertEqual(p["per_page"], 3)
        self.assertGreater(p["total"], 0)
        self.assertEqual(len(res_page["results"]), min(3, p["total"]))

    # -------------------------------------------------------------------------
    # 4. COMPLETE STUDENT PROFILE (9 SECTIONS)
    # -------------------------------------------------------------------------
    def test_07_student_profile_retrieval_all_nine_sections(self):
        """Verifies get_student retrieves data across all 9 required sections."""
        # Student 1 is a seeded student with rich academic and career records
        student = get_student(1)
        self.assertIsNotNone(student)

        # 1. Personal details
        self.assertIn("Roll_No", student)
        self.assertIn("First_Name", student)
        self.assertIn("Email", student)
        self.assertIn("Phone_Numbers", student)
        self.assertIsInstance(student["Phone_Numbers"], list)

        # 2. Academic details
        self.assertIn("Branch", student)
        self.assertIn("Batch_Year", student)
        self.assertIn("CGPA", student)
        self.assertIn("Backlogs", student)
        self.assertIn("Is_Eligible", student)

        # 3. Semester results
        self.assertIn("Semester_Results", student)
        self.assertIsInstance(student["Semester_Results"], list)
        if student["Semester_Results"]:
            sr = student["Semester_Results"][0]
            self.assertIn("Semester", sr)
            self.assertIn("SGPA", sr)
            self.assertIn("Total_Credits", sr)

        # 4. Registered courses
        self.assertIn("Registered_Courses", student)
        self.assertIsInstance(student["Registered_Courses"], list)

        # 5. Technical skills
        self.assertIn("Skills", student)
        self.assertIsInstance(student["Skills"], list)

        # 6. Projects and achievements
        self.assertIn("Projects", student)
        self.assertIn("Achievements", student)
        self.assertIn("Profiles", student)

        # 7. Resume and education documents
        self.assertIn("Resumes", student)
        self.assertIn("Education_Documents", student)

        # 8. Internship history
        self.assertIn("Internships", student)
        self.assertIsInstance(student["Internships"], list)

        # 9. Placement offers
        self.assertIn("Placements", student)
        self.assertIsInstance(student["Placements"], list)

    def test_08_student_detail_page_renders_all_sections(self):
        """Verifies GET /students/<id> HTML view renders all 9 profile sections."""
        res = self.client.get("/students/1")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        # Verify all 9 sections appear in the page
        self.assertIn("Personal Details", html)
        self.assertIn("Academic Details", html)
        self.assertIn("Official Semester Results", html)
        self.assertIn("Enrolled Courses", html)
        self.assertIn("Technical Skills", html)
        self.assertIn("Projects and Achievements", html)
        self.assertIn("Resume Repository", html)
        self.assertIn("Education Documents", html)
        self.assertIn("Internship History", html)
        self.assertIn("Placement Offers History", html)

    # -------------------------------------------------------------------------
    # 5. CSV EXPORT FOR FILTERED STUDENT RECORDS
    # -------------------------------------------------------------------------
    def test_09_csv_export_endpoint(self):
        """Verifies /students/export-csv returns valid CSV with header and filtered records."""
        # Unfiltered export
        res = self.client.get("/students/export-csv")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, "text/csv; charset=utf-8")
        self.assertIn("attachment; filename=", res.headers.get("Content-Disposition", ""))

        csv_text = res.get_data(as_text=True)
        reader = csv.reader(io.StringIO(csv_text))
        rows = list(reader)
        self.assertTrue(len(rows) > 1)  # Header + at least one student

        header = rows[0]
        expected_cols = [
            "Roll No",
            "First Name",
            "Last Name",
            "Branch",
            "Batch Year",
            "CGPA",
            "Backlogs",
            "Email",
            "Placement Status",
            "Placement Offers",
            "Internships Count",
        ]
        for col in expected_cols:
            self.assertIn(col, header)

        # Filtered export by branch
        res_filtered = self.client.get("/students/export-csv?branch=CSE")
        self.assertEqual(res_filtered.status_code, 200)
        reader_filtered = csv.reader(io.StringIO(res_filtered.get_data(as_text=True)))
        rows_filtered = list(reader_filtered)
        header_f = rows_filtered[0]
        branch_idx = header_f.index("Branch")
        for row in rows_filtered[1:]:
            self.assertEqual(row[branch_idx], "CSE")

    # -------------------------------------------------------------------------
    # 6. FORM VALIDATION AND DUPLICATE RECORD HANDLING
    # -------------------------------------------------------------------------
    def test_10_duplicate_roll_number_conflict(self):
        """Verifies attempting to create a student with existing Roll_No raises ConflictError."""
        existing = execute_one("SELECT Roll_No FROM STUDENT LIMIT 1")
        with self.assertRaises(ConflictError) as ctx:
            create_student(
                {
                    "Roll_No": existing["Roll_No"],
                    "First_Name": "Duplicate",
                    "Branch": "CSE",
                    "Batch_Year": 2025,
                    "CGPA": 8.0,
                    "Email": "unique_email_999@test.edu",
                }
            )
        self.assertIn("already exists", str(ctx.exception))

    def test_11_duplicate_email_conflict(self):
        """Verifies attempting to create a student with existing Email raises ConflictError."""
        existing = execute_one("SELECT Email FROM STUDENT LIMIT 1")
        with self.assertRaises(ConflictError) as ctx:
            create_student(
                {
                    "Roll_No": "UNIQUE_ROLL_999",
                    "First_Name": "Duplicate",
                    "Branch": "CSE",
                    "Batch_Year": 2025,
                    "CGPA": 8.0,
                    "Email": existing["Email"],
                }
            )
        self.assertIn("already exists", str(ctx.exception))

    def test_12_validation_bounds_and_types(self):
        """Verifies that invalid CGPA, negative backlogs, or malformed email raise ValidationError."""
        # Negative CGPA
        with self.assertRaises(ValidationError):
            create_student(
                {
                    "Roll_No": "VAL_TEST_1",
                    "First_Name": "Val",
                    "Branch": "CSE",
                    "Batch_Year": 2025,
                    "CGPA": -1.0,
                    "Email": "val1@test.edu",
                }
            )

        # CGPA > 10.0
        with self.assertRaises(ValidationError):
            create_student(
                {
                    "Roll_No": "VAL_TEST_2",
                    "First_Name": "Val",
                    "Branch": "CSE",
                    "Batch_Year": 2025,
                    "CGPA": 11.5,
                    "Email": "val2@test.edu",
                }
            )

        # Negative Backlogs
        with self.assertRaises(ValidationError):
            create_student(
                {
                    "Roll_No": "VAL_TEST_3",
                    "First_Name": "Val",
                    "Branch": "CSE",
                    "Batch_Year": 2025,
                    "CGPA": 8.0,
                    "Backlogs": -2,
                    "Email": "val3@test.edu",
                }
            )

    # -------------------------------------------------------------------------
    # 7. CONFIRMATION & SAFE DELETION
    # -------------------------------------------------------------------------
    def test_13_block_deletion_with_active_career_records(self):
        """Verifies delete_student blocks deletion of students with placement or internship history."""
        # Student 1 has placements and internships
        with self.assertRaises(ProtectedDeleteError) as ctx:
            delete_student(1)
        self.assertIn("Active career history detected", str(ctx.exception))

    # -------------------------------------------------------------------------
    # 8. DATABASE TRANSACTIONS FOR MULTI-TABLE OPERATIONS
    # -------------------------------------------------------------------------
    def test_14_atomic_create_and_update_with_related_tables(self):
        """Verifies atomic multi-table operations spanning STUDENT, STUDENT_PHONE, and STUDENT_SKILL."""
        roll = "ATOMIC_TX_2026"
        email = "atomic_tx@university.edu"

        # Clean up if leftover from previous run
        execute_one("DELETE FROM STUDENT WHERE Roll_No = %s", (roll,))

        created = create_student(
            {
                "Roll_No": roll,
                "First_Name": "Aadi",
                "Last_Name": "Verma",
                "Branch": "CSE",
                "Batch_Year": 2026,
                "Section": "A",
                "CGPA": 9.10,
                "Backlogs": 0,
                "Email": email,
                "Phone_Numbers": ["+91 9111122222", "+91 9333344444"],
                "Skills": ["Python", "Docker", "FastAPI"],
            }
        )

        st_id = created["Student_ID"]
        self.assertIsNotNone(st_id)
        self.assertEqual(len(created["Phone_Numbers"]), 2)
        self.assertEqual(len(created["Skills"]), 3)

        # Verify DB records
        phone_rows = execute_query(
            "SELECT Phone_No FROM STUDENT_PHONE WHERE Student_ID = %s", (st_id,)
        )
        self.assertEqual(len(phone_rows), 2)

        skill_rows = execute_query(
            "SELECT Skill FROM STUDENT_SKILL WHERE Student_ID = %s", (st_id,)
        )
        self.assertEqual(len(skill_rows), 3)

        # Update student atomically
        updated = update_student(
            st_id,
            {"CGPA": 9.35, "Phone_Numbers": ["+91 9888877777"], "Skills": ["Python", "Kubernetes"]},
        )
        self.assertEqual(updated["CGPA"], 9.35)
        self.assertEqual(updated["Phone_Numbers"], ["+91 9888877777"])
        self.assertEqual(updated["Skills"], ["Kubernetes", "Python"])

        # Delete student cleanly since no placements/internships exist
        del_res = delete_student(st_id)
        self.assertTrue(del_res)

        # Verify cascade/cleanup
        self.assertIsNone(execute_one("SELECT * FROM STUDENT WHERE Student_ID = %s", (st_id,)))
        self.assertEqual(
            len(execute_query("SELECT * FROM STUDENT_PHONE WHERE Student_ID = %s", (st_id,))), 0
        )
        self.assertEqual(
            len(execute_query("SELECT * FROM STUDENT_SKILL WHERE Student_ID = %s", (st_id,))), 0
        )


if __name__ == "__main__":
    unittest.main()

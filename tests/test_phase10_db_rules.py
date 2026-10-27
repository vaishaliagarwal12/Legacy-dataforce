import unittest
from app import create_app
from db.connection import (
    get_cursor,
    execute_one,
    execute_query,
    execute_mutation,
    DatabaseError,
)
from services.placement_service import create_placement_offer, update_offer_status
from services.exceptions import ConflictError, ValidationError


class TestDatabaseRules(unittest.TestCase):
    """Phase 10 Test Suite: Verifying core Database Rules:
    1. Integrity Constraints (CHECK, NOT NULL, Range, Enum)
    2. Uniqueness Constraints (Primary, Candidate, Alternate, Composite Unique)
    3. Referential Actions & Cascades (ON DELETE CASCADE, RESTRICT, SET NULL)
    4. Business Integrity Rules (The Single-Accepted-Offer Rule, Multi-offer tracking, Duplicate Offer rejection)
    """

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()

    # =========================================================================
    # PART 1: INTEGRITY CONSTRAINTS (CHECK & NOT NULL)
    # =========================================================================

    def test_01_check_constraint_student_cgpa_bounds(self):
        """Database Rule: STUDENT.CGPA must be between 0.00 and 10.00."""
        # Test CGPA > 10.00 directly at database level
        with self.assertRaises(DatabaseError) as ctx:
            execute_mutation(
                """INSERT INTO STUDENT (Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs, Email)
                   VALUES ('TEST_CGPA_HIGH', 'Test', 'User', 'CSE', 2024, 10.50, 0, 'test_high@univ.edu')"""
            )
        self.assertTrue(
            "Check constraint" in str(ctx.exception) or "CONSTRAINT" in str(ctx.exception) or "10.50" in str(ctx.exception)
        )

        # Test CGPA < 0.00
        with self.assertRaises(DatabaseError) as ctx2:
            execute_mutation(
                """INSERT INTO STUDENT (Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs, Email)
                   VALUES ('TEST_CGPA_LOW', 'Test', 'User', 'CSE', 2024, -1.00, 0, 'test_low@univ.edu')"""
            )
        self.assertTrue("Check constraint" in str(ctx2.exception) or "CONSTRAINT" in str(ctx2.exception))

    def test_02_check_constraint_student_backlogs_non_negative(self):
        """Database Rule: STUDENT.Backlogs must be >= 0."""
        with self.assertRaises(DatabaseError) as ctx:
            execute_mutation(
                """INSERT INTO STUDENT (Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs, Email)
                   VALUES ('TEST_BL_NEG', 'Test', 'User', 'CSE', 2024, 8.00, -2, 'test_bl_neg@univ.edu')"""
            )
        self.assertTrue("Check constraint" in str(ctx.exception) or "CONSTRAINT" in str(ctx.exception))

    def test_03_check_constraint_course_semester_and_credits(self):
        """Database Rule: COURSE.Semester must be 1-8 and Credits > 0."""
        # Semester = 9 (invalid)
        with self.assertRaises(DatabaseError):
            execute_mutation(
                """INSERT INTO COURSE (University_ID, Course_Name, Department, Semester, Credits, Course_Type)
                   VALUES (1, 'Advanced Quantum Comp', 'CSE', 9, 4, 'Core')"""
            )
        # Credits = 0 (invalid)
        with self.assertRaises(DatabaseError):
            execute_mutation(
                """INSERT INTO COURSE (University_ID, Course_Name, Department, Semester, Credits, Course_Type)
                   VALUES (1, 'Zero Credit Lab', 'CSE', 5, 0, 'Core')"""
            )

    def test_04_check_constraint_internship_chronological_dates(self):
        """Database Rule: INTERNSHIP.End_Date must be >= Start_Date (chk_internship_dates)."""
        with self.assertRaises(DatabaseError) as ctx:
            execute_mutation(
                """INSERT INTO INTERNSHIP (Student_ID, Company_ID, Internship_No, Internship_Type, Role,
                                           Start_Date, End_Date, Stipend)
                   VALUES (1, 1, 99, 'Additional', 'Backend Intern', '2024-07-01', '2024-05-01', 25000)"""
            )
        self.assertTrue("chk_internship_dates" in str(ctx.exception) or "Check constraint" in str(ctx.exception))

    def test_05_check_constraint_enum_course_type(self):
        """Database Rule: COURSE.Course_Type must be in ('Core', 'Elective', 'Lab', 'Seminar')."""
        with self.assertRaises(DatabaseError):
            execute_mutation(
                """INSERT INTO COURSE (University_ID, Course_Name, Department, Semester, Credits, Course_Type)
                   VALUES (1, 'Invalid Type Course', 'CSE', 4, 3, 'InvalidType')"""
            )

    def test_06_not_null_constraints(self):
        """Database Rule: Mandatory columns reject NULL inserts."""
        # Student Roll_No cannot be NULL
        with self.assertRaises(DatabaseError):
            execute_mutation(
                """INSERT INTO STUDENT (Roll_No, First_Name, Branch, Batch_Year, CGPA, Email)
                   VALUES (NULL, 'NullRoll', 'CSE', 2024, 8.50, 'null_roll@univ.edu')"""
            )
        # Company Company_Name cannot be NULL
        with self.assertRaises(DatabaseError):
            execute_mutation(
                """INSERT INTO COMPANY (Company_Name, Company_Type, Industry)
                   VALUES (NULL, 'Product', 'Software')"""
            )

    # =========================================================================
    # PART 2: UNIQUENESS & CANDIDATE KEYS
    # =========================================================================

    def test_07_unique_student_roll_no(self):
        """Database Rule: STUDENT.Roll_No is unique."""
        # CS202001 already exists in seed data (Aarav Sharma)
        with self.assertRaises(DatabaseError) as ctx:
            execute_mutation(
                """INSERT INTO STUDENT (Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Email)
                   VALUES ('CS202001', 'Clone', 'Student', 'CSE', 2024, 8.50, 'clone1@univ.edu')"""
            )
        self.assertIn("Duplicate entry", str(ctx.exception))

    def test_08_unique_student_email(self):
        """Database Rule: STUDENT.Email is unique."""
        # Aarav Sharma has email 'aarav.sharma@fictional.edu' in seed data
        with self.assertRaises(DatabaseError) as ctx:
            execute_mutation(
                """INSERT INTO STUDENT (Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Email)
                   VALUES ('DIFF_ROLL_999', 'Clone', 'Email', 'CSE', 2024, 8.50, 'aarav.sharma@fictional.edu')"""
            )
        self.assertIn("Duplicate entry", str(ctx.exception))

    def test_09_unique_company_name(self):
        """Database Rule: COMPANY.Company_Name is unique."""
        # 'Google India' already exists
        with self.assertRaises(DatabaseError) as ctx:
            execute_mutation(
                """INSERT INTO COMPANY (Company_Name, Company_Type, Industry)
                   VALUES ('Google India', 'Product', 'Tech')"""
            )
        self.assertIn("Duplicate entry", str(ctx.exception))

    def test_10_composite_unique_course_dept_semester(self):
        """Database Rule: COURSE (University_ID, Course_Name, Semester) composite uniqueness."""
        # 'Computer Networks', Semester 5, University 1 exists
        with self.assertRaises(DatabaseError) as ctx:
            execute_mutation(
                """INSERT INTO COURSE (University_ID, Course_Name, Department, Semester, Credits, Course_Type)
                   VALUES (1, 'Computer Networks', 'CSE', 5, 4, 'Core')"""
            )
        self.assertIn("Duplicate entry", str(ctx.exception))

    def test_11_composite_unique_semester_result(self):
        """Database Rule: SEMESTER_RESULT (Student_ID, Semester) composite uniqueness."""
        # Student 1 already has Semester 1 in seed data
        with self.assertRaises(DatabaseError) as ctx:
            execute_mutation(
                """INSERT INTO SEMESTER_RESULT (Student_ID, Semester, SGPA, Year, Total_Credits)
                   VALUES (1, 1, 9.50, 2021, 24)"""
            )
        self.assertIn("Duplicate entry", str(ctx.exception))

    def test_12_composite_unique_internship_no(self):
        """Database Rule: INTERNSHIP (Student_ID, Internship_No) composite uniqueness."""
        # Student 1 already has Internship_No = 1
        with self.assertRaises(DatabaseError) as ctx:
            execute_mutation(
                """INSERT INTO INTERNSHIP (Student_ID, Company_ID, Internship_No, Internship_Type,
                                           Role, Start_Date, End_Date, Stipend)
                   VALUES (1, 1, 1, 'Mandatory', 'Duplicate Intern', '2023-06-01', '2023-08-01', 50000)"""
            )
        self.assertIn("Duplicate entry", str(ctx.exception))

    def test_13_composite_primary_keys(self):
        """Database Rule: Composite PKs reject duplicate combination inserts."""
        # 1. STUDENT_PHONE (Student_ID, Phone_No)
        with self.assertRaises(DatabaseError) as ctx_phone:
            execute_mutation(
                """INSERT INTO STUDENT_PHONE (Student_ID, Phone_No) VALUES (1, '+91-9876543201')"""
            )
        self.assertIn("Duplicate entry", str(ctx_phone.exception))

        # 2. STUDENT_SKILL (Student_ID, Skill)
        with self.assertRaises(DatabaseError) as ctx_skill:
            execute_mutation(
                """INSERT INTO STUDENT_SKILL (Student_ID, Skill) VALUES (1, 'Java')"""
            )
        self.assertIn("Duplicate entry", str(ctx_skill.exception))

        # 3. STUDENT_COURSE (Student_ID, Course_ID)
        # Create a dedicated enrollment and then attempt duplicate
        res_stu = execute_mutation(
            """INSERT INTO STUDENT (Roll_No, First_Name, Branch, Batch_Year, CGPA, Email)
               VALUES ('P10_COMP_TEST', 'Comp', 'CSE', 2024, 8.0, 'p10comp@univ.edu')"""
        )
        temp_stu_id = res_stu["last_insert_id"]
        try:
            execute_mutation(
                "INSERT INTO STUDENT_COURSE (Student_ID, Course_ID, Enrollment_Year, Grade) VALUES (%s, 1, 2021, 'A')",
                (temp_stu_id,)
            )
            with self.assertRaises(DatabaseError) as ctx_course:
                execute_mutation(
                    "INSERT INTO STUDENT_COURSE (Student_ID, Course_ID, Enrollment_Year, Grade) VALUES (%s, 1, 2021, 'A')",
                    (temp_stu_id,)
                )
            self.assertIn("Duplicate entry", str(ctx_course.exception))
        finally:
            execute_mutation("DELETE FROM STUDENT WHERE Student_ID = %s", (temp_stu_id,))

    # =========================================================================
    # PART 3: REFERENTIAL INTEGRITY & CASCADING ACTIONS
    # =========================================================================

    def test_14_cascade_delete_student_purges_all_dependent_records(self):
        """Database Rule: Deleting a STUDENT cascades to phones, skills, profiles, results, and offers."""
        # 1. Create a dedicated test student
        res_stu = execute_mutation(
            """INSERT INTO STUDENT (Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs, Email)
               VALUES ('CASCADE_STU_01', 'Cascade', 'Tester', 'IT', 2024, 8.80, 0, 'cascade.test@univ.edu')"""
        )
        test_student_id = res_stu["last_insert_id"]

        # 2. Attach phone, skill, profile, semester result, and a placement offer
        execute_mutation("INSERT INTO STUDENT_PHONE (Student_ID, Phone_No) VALUES (%s, '+91-9999900001')", (test_student_id,))
        execute_mutation("INSERT INTO STUDENT_SKILL (Student_ID, Skill) VALUES (%s, 'Rust')", (test_student_id,))
        execute_mutation(
            """INSERT INTO STUDENT_PROFILE (Student_ID, Profile_Type, Title, Year)
               VALUES (%s, 'Project', 'Cascade Research', 2023)""",
            (test_student_id,)
        )
        execute_mutation(
            """INSERT INTO SEMESTER_RESULT (Student_ID, Semester, SGPA, Year, Total_Credits)
               VALUES (%s, 1, 8.80, 2021, 24)""",
            (test_student_id,)
        )
        res_offer = execute_mutation(
            """INSERT INTO PLACEMENT (Student_ID, Company_ID, Role, Package, Placement_Year, Offer_Status)
               VALUES (%s, 1, 'Systems Developer', 18.00, 2024, 'Offered')""",
            (test_student_id,)
        )
        offer_id = res_offer["last_insert_id"]
        execute_mutation("INSERT INTO PLACEMENT_SKILL (Placement_ID, Skill) VALUES (%s, 'Rust')", (offer_id,))

        # Verify all children exist
        self.assertIsNotNone(execute_one("SELECT * FROM STUDENT_PHONE WHERE Student_ID = %s", (test_student_id,)))
        self.assertIsNotNone(execute_one("SELECT * FROM STUDENT_SKILL WHERE Student_ID = %s", (test_student_id,)))
        self.assertIsNotNone(execute_one("SELECT * FROM STUDENT_PROFILE WHERE Student_ID = %s", (test_student_id,)))
        self.assertIsNotNone(execute_one("SELECT * FROM SEMESTER_RESULT WHERE Student_ID = %s", (test_student_id,)))
        self.assertIsNotNone(execute_one("SELECT * FROM PLACEMENT WHERE Placement_ID = %s", (offer_id,)))
        self.assertIsNotNone(execute_one("SELECT * FROM PLACEMENT_SKILL WHERE Placement_ID = %s", (offer_id,)))

        # 3. DELETE the Student
        execute_mutation("DELETE FROM STUDENT WHERE Student_ID = %s", (test_student_id,))

        # 4. Verify ON DELETE CASCADE has purged all child records completely
        self.assertIsNone(execute_one("SELECT * FROM STUDENT_PHONE WHERE Student_ID = %s", (test_student_id,)))
        self.assertIsNone(execute_one("SELECT * FROM STUDENT_SKILL WHERE Student_ID = %s", (test_student_id,)))
        self.assertIsNone(execute_one("SELECT * FROM STUDENT_PROFILE WHERE Student_ID = %s", (test_student_id,)))
        self.assertIsNone(execute_one("SELECT * FROM SEMESTER_RESULT WHERE Student_ID = %s", (test_student_id,)))
        self.assertIsNone(execute_one("SELECT * FROM PLACEMENT WHERE Placement_ID = %s", (offer_id,)))
        self.assertIsNone(execute_one("SELECT * FROM PLACEMENT_SKILL WHERE Placement_ID = %s", (offer_id,)))

    def test_15_cascade_delete_course_purges_enrollments(self):
        """Database Rule: Deleting a COURSE cascades to STUDENT_COURSE."""
        # Create a course
        res_course = execute_mutation(
            """INSERT INTO COURSE (University_ID, Course_Name, Department, Semester, Credits, Course_Type)
               VALUES (1, 'Cascade Test Course', 'ECE', 6, 3, 'Elective')"""
        )
        course_id = res_course["last_insert_id"]

        # Enroll Student 2
        execute_mutation(
            "INSERT INTO STUDENT_COURSE (Student_ID, Course_ID, Enrollment_Year, Grade) VALUES (2, %s, 2023, 'A')",
            (course_id,)
        )
        self.assertIsNotNone(execute_one("SELECT * FROM STUDENT_COURSE WHERE Course_ID = %s", (course_id,)))

        # Delete course
        execute_mutation("DELETE FROM COURSE WHERE Course_ID = %s", (course_id,))
        self.assertIsNone(execute_one("SELECT * FROM STUDENT_COURSE WHERE Course_ID = %s", (course_id,)))

    def test_16_cascade_delete_opportunity_purges_eligibility_and_rounds(self):
        """Database Rule: Deleting an OPPORTUNITY cascades to ELIGIBILITY and SELECTION_PROCESS."""
        # Create opportunity under drive 1
        res_opp = execute_mutation(
            """INSERT INTO OPPORTUNITY (Drive_ID, Role, Opportunity_Type, Package_Stipend)
               VALUES (1, 'Cascade Test Role', 'Placement', 14.50)"""
        )
        opp_id = res_opp["last_insert_id"]

        # Insert eligibility and selection process round
        execute_mutation("INSERT INTO ELIGIBILITY (Opportunity_ID, Minimum_CGPA, Eligible_Branch) VALUES (%s, 7.50, 'CSE')", (opp_id,))
        execute_mutation("INSERT INTO SELECTION_PROCESS (Opportunity_ID, Round_Number, Round_Type) VALUES (%s, 1, 'Technical Interview')", (opp_id,))

        self.assertIsNotNone(execute_one("SELECT * FROM ELIGIBILITY WHERE Opportunity_ID = %s", (opp_id,)))
        self.assertIsNotNone(execute_one("SELECT * FROM SELECTION_PROCESS WHERE Opportunity_ID = %s", (opp_id,)))

        # Delete opportunity
        execute_mutation("DELETE FROM OPPORTUNITY WHERE Opportunity_ID = %s", (opp_id,))

        self.assertIsNone(execute_one("SELECT * FROM ELIGIBILITY WHERE Opportunity_ID = %s", (opp_id,)))
        self.assertIsNone(execute_one("SELECT * FROM SELECTION_PROCESS WHERE Opportunity_ID = %s", (opp_id,)))

    def test_17_restrict_delete_company_with_active_relationships(self):
        """Database Rule: ON DELETE RESTRICT prevents deleting a company with recruitment drives or offers."""
        # Company 1 (Google India) has recruitment drives, placements, internships
        with self.assertRaises(DatabaseError) as ctx:
            execute_mutation("DELETE FROM COMPANY WHERE Company_ID = 1")
        self.assertIn("foreign key constraint fails", str(ctx.exception).lower())

    def test_18_set_null_opportunity_on_placement_deletion(self):
        """Database Rule: ON DELETE SET NULL on OPPORTUNITY nullifies Opportunity_ID in PLACEMENT."""
        # Create a temporary opportunity
        res_opp = execute_mutation(
            """INSERT INTO OPPORTUNITY (Drive_ID, Role, Opportunity_Type, Package_Stipend)
               VALUES (1, 'SetNull Test Role', 'Placement', 16.00)"""
        )
        opp_id = res_opp["last_insert_id"]

        # Create placement offer referencing this opportunity for Student 2
        res_offer = execute_mutation(
            """INSERT INTO PLACEMENT (Student_ID, Company_ID, Opportunity_ID, Role, Package, Placement_Year, Offer_Status)
               VALUES (2, 1, %s, 'SetNull Role', 16.00, 2024, 'Offered')""",
            (opp_id,)
        )
        offer_id = res_offer["last_insert_id"]

        # Delete the opportunity
        execute_mutation("DELETE FROM OPPORTUNITY WHERE Opportunity_ID = %s", (opp_id,))

        # Verify placement offer record still exists, and its Opportunity_ID was set to NULL
        offer = execute_one("SELECT Placement_ID, Opportunity_ID FROM PLACEMENT WHERE Placement_ID = %s", (offer_id,))
        self.assertIsNotNone(offer)
        self.assertIsNone(offer["Opportunity_ID"])

        # Clean up offer
        execute_mutation("DELETE FROM PLACEMENT WHERE Placement_ID = %s", (offer_id,))

    # =========================================================================
    # PART 4: THE ONE-ACCEPTED-OFFER RULE & OFFER CONSTRAINTS
    # =========================================================================

    def test_19_student_can_hold_multiple_offered_status_offers(self):
        """Policy Rule: A student can receive multiple offers in 'Offered' status without conflict."""
        # Create clean dedicated test student
        res_stu = execute_mutation(
            """INSERT INTO STUDENT (Roll_No, First_Name, Branch, Batch_Year, CGPA, Email)
               VALUES ('P10_OFFER_STU_19', 'MultiOffer', 'CSE', 2024, 8.50, 'multi19@univ.edu')"""
        )
        stu_id = res_stu["last_insert_id"]
        try:
            # Issue Offer A
            offer_a = create_placement_offer({
                "Student_ID": stu_id,
                "Company_ID": 3,
                "Role": "Robotics Engineer",
                "Package": 12.00,
                "Placement_Year": 2024,
                "Offer_Status": "Offered"
            })
            # Issue Offer B
            offer_b = create_placement_offer({
                "Student_ID": stu_id,
                "Company_ID": 4,
                "Role": "Systems Analyst",
                "Package": 14.00,
                "Placement_Year": 2024,
                "Offer_Status": "Offered"
            })

            self.assertIsNotNone(offer_a)
            self.assertIsNotNone(offer_b)
            self.assertEqual(offer_a["Offer_Status"], "Offered")
            self.assertEqual(offer_b["Offer_Status"], "Offered")
        finally:
            execute_mutation("DELETE FROM STUDENT WHERE Student_ID = %s", (stu_id,))

    def test_20_the_one_accepted_offer_rule_strictly_enforced(self):
        """CRITICAL: Enforces that at most ONE Accepted or Joined offer is allowed per student."""
        res_stu = execute_mutation(
            """INSERT INTO STUDENT (Roll_No, First_Name, Branch, Batch_Year, CGPA, Email)
               VALUES ('P10_OFFER_STU_20', 'AcceptRule', 'ECE', 2024, 8.90, 'rule20@univ.edu')"""
        )
        stu_id = res_stu["last_insert_id"]
        try:
            # Create Offer 1 & Offer 2 in 'Offered' status
            offer_1 = create_placement_offer({
                "Student_ID": stu_id,
                "Company_ID": 3,
                "Role": "Hardware Specialist",
                "Package": 11.50,
                "Placement_Year": 2024,
                "Offer_Status": "Offered"
            })
            offer_2 = create_placement_offer({
                "Student_ID": stu_id,
                "Company_ID": 4,
                "Role": "Industrial Consultant",
                "Package": 13.00,
                "Placement_Year": 2024,
                "Offer_Status": "Offered"
            })
            o1_id = offer_1["Placement_ID"]
            o2_id = offer_2["Placement_ID"]

            # Step 1: Accept Offer 1 -> Must succeed
            updated_1 = update_offer_status(o1_id, "Accepted")
            self.assertEqual(updated_1["Offer_Status"], "Accepted")

            # Step 2: Attempt to accept Offer 2 while Offer 1 is still Accepted -> MUST RAISE ConflictError!
            with self.assertRaises(ConflictError) as conflict_ctx:
                update_offer_status(o2_id, "Accepted")
            self.assertIn("already has an accepted offer", str(conflict_ctx.exception))

            # Step 3: Attempt to set Offer 2 to 'Joined' while Offer 1 is Accepted -> MUST RAISE ConflictError!
            with self.assertRaises(ConflictError) as join_conflict_ctx:
                update_offer_status(o2_id, "Joined")
            self.assertIn("already has an accepted offer", str(join_conflict_ctx.exception))

            # Step 4: Decline Offer 1
            declined_1 = update_offer_status(o1_id, "Declined")
            self.assertEqual(declined_1["Offer_Status"], "Declined")
            self.assertEqual(declined_1["Joined"], "No")

            # Step 5: Now accept Offer 2 -> Must succeed smoothly!
            updated_2 = update_offer_status(o2_id, "Accepted")
            self.assertEqual(updated_2["Offer_Status"], "Accepted")
        finally:
            execute_mutation("DELETE FROM STUDENT WHERE Student_ID = %s", (stu_id,))

    def test_21_cannot_create_directly_accepted_offer_if_one_already_exists(self):
        """Rule: Attempting to insert a new offer directly as 'Accepted' fails if student already has one."""
        res_stu = execute_mutation(
            """INSERT INTO STUDENT (Roll_No, First_Name, Branch, Batch_Year, CGPA, Email)
               VALUES ('P10_OFFER_STU_21', 'DirectAcc', 'IT', 2024, 8.20, 'rule21@univ.edu')"""
        )
        stu_id = res_stu["last_insert_id"]
        try:
            offer_acc = create_placement_offer({
                "Student_ID": stu_id,
                "Company_ID": 2,
                "Role": "Direct Accepted Offer",
                "Package": 15.00,
                "Placement_Year": 2024,
                "Offer_Status": "Accepted"
            })
            self.assertEqual(offer_acc["Offer_Status"], "Accepted")

            # Try to insert another offer with Offer_Status='Accepted'
            with self.assertRaises(ConflictError) as ctx:
                create_placement_offer({
                    "Student_ID": stu_id,
                    "Company_ID": 5,
                    "Role": "Second Accepted Offer",
                    "Package": 18.00,
                    "Placement_Year": 2024,
                    "Offer_Status": "Accepted"
                })
            self.assertIn("already holds an accepted offer", str(ctx.exception))
        finally:
            execute_mutation("DELETE FROM STUDENT WHERE Student_ID = %s", (stu_id,))

    def test_22_duplicate_offer_for_same_opportunity_rejected(self):
        """Rule: Duplicate offer for the exact same Opportunity to the same student is rejected."""
        # Find placement opportunity
        opp = execute_one("SELECT Opportunity_ID, Drive_ID FROM OPPORTUNITY WHERE Opportunity_Type = 'Placement' LIMIT 1")
        drive = execute_one("SELECT Company_ID FROM RECRUITMENT_DRIVE WHERE Drive_ID = %s", (opp["Drive_ID"],))
        
        res_stu = execute_mutation(
            """INSERT INTO STUDENT (Roll_No, First_Name, Branch, Batch_Year, CGPA, Email)
               VALUES ('P10_OFFER_STU_22', 'DupOpp', 'CSE', 2024, 8.40, 'rule22@univ.edu')"""
        )
        stu_id = res_stu["last_insert_id"]
        try:
            # First offer succeeds
            off1 = create_placement_offer({
                "Student_ID": stu_id,
                "Company_ID": drive["Company_ID"],
                "Opportunity_ID": opp["Opportunity_ID"],
                "Role": "Test Engineer",
                "Package": 10.00,
                "Placement_Year": 2024,
                "Offer_Status": "Offered"
            })

            # Second offer for the identical opportunity must raise ConflictError
            with self.assertRaises(ConflictError) as ctx:
                create_placement_offer({
                    "Student_ID": stu_id,
                    "Company_ID": drive["Company_ID"],
                    "Opportunity_ID": opp["Opportunity_ID"],
                    "Role": "Test Engineer 2",
                    "Package": 11.00,
                    "Placement_Year": 2024,
                    "Offer_Status": "Offered"
                })
            self.assertIn("Duplicate offer rejected", str(ctx.exception))
        finally:
            execute_mutation("DELETE FROM STUDENT WHERE Student_ID = %s", (stu_id,))

    def test_23_block_placement_offer_for_internship_opportunity(self):
        """Rule: Placement offers CANNOT be created for an opportunity of type 'Internship'."""
        intern_opp = execute_one("SELECT Opportunity_ID, Drive_ID FROM OPPORTUNITY WHERE Opportunity_Type = 'Internship' LIMIT 1")
        drive = execute_one("SELECT Company_ID FROM RECRUITMENT_DRIVE WHERE Drive_ID = %s", (intern_opp["Drive_ID"],))
        
        res_stu = execute_mutation(
            """INSERT INTO STUDENT (Roll_No, First_Name, Branch, Batch_Year, CGPA, Email)
               VALUES ('P10_OFFER_STU_23', 'InternOpp', 'ME', 2024, 7.80, 'rule23@univ.edu')"""
        )
        stu_id = res_stu["last_insert_id"]
        try:
            with self.assertRaises(ValidationError) as ctx:
                create_placement_offer({
                    "Student_ID": stu_id,
                    "Company_ID": drive["Company_ID"],
                    "Opportunity_ID": intern_opp["Opportunity_ID"],
                    "Role": "Intern as Placement Role",
                    "Package": 12.00,
                    "Placement_Year": 2024,
                    "Offer_Status": "Offered"
                })
            self.assertIn("is of type 'Internship'", str(ctx.exception))
        finally:
            execute_mutation("DELETE FROM STUDENT WHERE Student_ID = %s", (stu_id,))


if __name__ == "__main__":
    unittest.main()

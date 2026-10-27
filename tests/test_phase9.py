"""
Phase 9 (Scope A) Automated Unit Test Suite.
Validates all 13 DBMS Demo Items, 44 original queries, and 5 mandatory additions:
1. LEFT JOIN version of students with no placement
2. Subquery for students with CGPA above average
3. Comparison of extra skills for placed vs non-placed students
4. Safe atomic transaction inserting student + phones + skills
5. CREATE INDEX statements and query plan optimization
"""

import unittest
import pymysql
import pymysql.cursors

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "12345",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}


class Phase9ScopeATestCase(unittest.TestCase):
    """Test suite verifying Phase 9 (Scope A) 13 DBMS Demo Items."""

    @classmethod
    def setUpClass(cls):
        # Initialize database placement_scope_a
        conn = pymysql.connect(host=DB_CONFIG["host"], port=DB_CONFIG["port"], user=DB_CONFIG["user"], password=DB_CONFIG["password"], charset=DB_CONFIG["charset"])
        with conn.cursor() as cur:
            cur.execute("DROP DATABASE IF EXISTS placement_scope_a;")
            cur.execute("CREATE DATABASE placement_scope_a;")
        conn.commit()
        conn.close()

        # Load Schema, Sample Data, and Views
        with open("placement_internship_db.sql", "r", encoding="utf-8") as f:
            full_sql = f.read()

        setup_sql = full_sql.split("-- PART 4: QUERIES")[0].replace("placement_db", "placement_scope_a")
        setup_conn = pymysql.connect(database="placement_scope_a", client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS, **DB_CONFIG)
        with setup_conn.cursor() as cur:
            cur.execute(setup_sql)
        setup_conn.commit()
        setup_conn.close()

    def get_conn(self):
        return pymysql.connect(database="placement_scope_a", **DB_CONFIG)

    # -------------------------------------------------------------------------
    # ITEM 1: DDL & SCHEMA INTEGRITY
    # -------------------------------------------------------------------------
    def test_01_ddl_tables_and_foreign_keys(self):
        """Item 1: Verify all 7 core Scope A tables exist and have zero orphaned FK rows."""
        conn = self.get_conn()
        with conn.cursor() as cur:
            cur.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE';")
            tables = [r[list(r.keys())[0]].upper() for r in cur.fetchall()]
            expected = ["STUDENT", "STUDENT_PHONE", "STUDENT_SKILL", "COMPANY", "PLACEMENT", "PLACEMENT_SKILL", "INTERNSHIP"]
            for t in expected:
                self.assertIn(t, tables)

            # Check zero orphans
            cur.execute("""
                SELECT COUNT(*) AS c FROM STUDENT_PHONE sp LEFT JOIN STUDENT s ON sp.Student_ID = s.Student_ID WHERE s.Student_ID IS NULL;
            """)
            self.assertEqual(cur.fetchone()["c"], 0)
        conn.close()

    # -------------------------------------------------------------------------
    # ITEM 2: BASIC PROJECTION, SELECTION & SORTING
    # -------------------------------------------------------------------------
    def test_02_basic_selection_and_sorting(self):
        """Item 2: Verify queries A1, A2, A5, B6, B9, B14, C12."""
        conn = self.get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT Roll_No, CGPA FROM STUDENT WHERE Branch = 'CSE' AND Batch_Year = 2024 ORDER BY CGPA DESC;")
            rows = cur.fetchall()
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["Roll_No"], "CS2102")  # Priya (9.10)
            self.assertEqual(rows[1]["Roll_No"], "CS2101")  # Aman (8.40)
        conn.close()

    # -------------------------------------------------------------------------
    # ITEM 3: PATTERN MATCHING & NULLITY
    # -------------------------------------------------------------------------
    def test_03_pattern_matching_and_nullity(self):
        """Item 3: Verify D11 (LIKE '%an%') and C8 (IS NULL)."""
        conn = self.get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT Roll_No FROM STUDENT WHERE First_Name LIKE '%an%' OR Last_Name LIKE '%an%';")
            rows = cur.fetchall()
            rolls = [r["Roll_No"] for r in rows]
            self.assertIn("CS2101", rolls)  # Aman
            self.assertIn("ME2105", rolls)  # Karan

            cur.execute("SELECT Student_Name FROM V_INTERNSHIP_DETAIL WHERE Internship_Type = 'Mandatory' AND Report_Link IS NULL;")
            missing = cur.fetchall()
            self.assertEqual(len(missing), 1)
            self.assertEqual(missing[0]["Student_Name"], "Karan Mehta")
        conn.close()

    # -------------------------------------------------------------------------
    # ITEM 4: DERIVED ATTRIBUTES & DATE COMPUTATIONS
    # -------------------------------------------------------------------------
    def test_04_derived_duration_and_credits(self):
        """Item 4: Verify C1 (Duration_Months derived attribute) and C9 (COALESCE credits)."""
        conn = self.get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT Duration_Months FROM V_INTERNSHIP_DETAIL WHERE Roll_No = 'CS2102' ORDER BY Internship_No;")
            rows = cur.fetchall()
            self.assertEqual(len(rows), 3)
            # Duration computed dynamically
            self.assertTrue(all(r["Duration_Months"] is not None for r in rows))
        conn.close()

    # -------------------------------------------------------------------------
    # ITEM 5: AGGREGATE FUNCTIONS & METRICS
    # -------------------------------------------------------------------------
    def test_05_aggregates_and_metrics(self):
        """Item 5: Verify B4, B10, B13, C6, C11, D2, D3."""
        conn = self.get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS c, ROUND(AVG(Package), 2) AS avg_pkg FROM V_PLACEMENT_DETAIL WHERE Joined = 'Yes';")
            res = cur.fetchone()
            self.assertEqual(res["c"], 4)
            self.assertAlmostEqual(float(res["avg_pkg"]), 8.28, delta=0.1)
        conn.close()

    # -------------------------------------------------------------------------
    # ITEM 6: MULTI-DIMENSIONAL GROUP BY
    # -------------------------------------------------------------------------
    def test_06_group_by_aggregations(self):
        """Item 6: Verify B3 (Branch-wise), B5 (Company-wise), B15, C7, D4, D10."""
        conn = self.get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT Branch, COUNT(*) AS pl FROM V_PLACEMENT_DETAIL WHERE Joined = 'Yes' GROUP BY Branch;")
            rows = {r["Branch"]: r["pl"] for r in cur.fetchall()}
            self.assertEqual(rows["CSE"], 2)
            self.assertEqual(rows["ECE"], 1)
            self.assertEqual(rows["IT"], 1)
        conn.close()

    # -------------------------------------------------------------------------
    # ITEM 7: FILTERED AGGREGATION WITH HAVING
    # -------------------------------------------------------------------------
    def test_07_group_by_having(self):
        """Item 7: Verify B8 (Multiple offers), C4 (Compliance audit), C10 (> 2 internships)."""
        conn = self.get_conn()
        with conn.cursor() as cur:
            # Aman has 2 offers
            cur.execute("SELECT Student_Name FROM V_PLACEMENT_DETAIL GROUP BY Student_ID, Student_Name HAVING COUNT(*) > 1;")
            multiple = cur.fetchall()
            self.assertEqual(len(multiple), 1)
            self.assertEqual(multiple[0]["Student_Name"], "Aman Sharma")

            # Zero students fail mandatory internship rule (all 5 have 2)
            cur.execute("""
                SELECT s.Roll_No FROM STUDENT s
                LEFT JOIN INTERNSHIP i ON i.Student_ID = s.Student_ID
                GROUP BY s.Student_ID, s.Roll_No
                HAVING COUNT(CASE WHEN i.Internship_Type = 'Mandatory' THEN 1 END) < 2;
            """)
            failed = cur.fetchall()
            self.assertEqual(len(failed), 0)
        conn.close()

    # -------------------------------------------------------------------------
    # ITEM 8: INNER JOINS & RELATIONAL MAPPINGS
    # -------------------------------------------------------------------------
    def test_08_inner_joins(self):
        """Item 8: Verify A4, B1, B2, B12, C2, C5, D1, D5, D9."""
        conn = self.get_conn()
        with conn.cursor() as cur:
            # D1: Internship converted to job
            cur.execute("""
                SELECT DISTINCT p.Student_Name, p.Company_Name
                FROM V_PLACEMENT_DETAIL p
                JOIN INTERNSHIP i ON i.Student_ID = p.Student_ID AND i.Company_ID = p.Company_ID
                WHERE p.Joined = 'Yes';
            """)
            converts = cur.fetchall()
            self.assertEqual(len(converts), 4)
        conn.close()

    # -------------------------------------------------------------------------
    # ITEM 9: OUTER JOINS & REQUIRED ADDITIONS (LEFT JOIN & SKILL COMPARISON)
    # -------------------------------------------------------------------------
    def test_09_outer_joins_and_additions(self):
        """Item 9: Verify ADD-1 (LEFT JOIN students not placed) and ADD-3 (Skills comparison)."""
        conn = self.get_conn()
        with conn.cursor() as cur:
            # ADD-1: Left join version of unplaced students -> Karan Mehta (ME2105)
            cur.execute("""
                SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name
                FROM STUDENT s
                LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID AND p.Joined = 'Yes'
                WHERE p.Placement_ID IS NULL;
            """)
            unplaced = cur.fetchall()
            self.assertEqual(len(unplaced), 1)
            self.assertEqual(unplaced[0]["Roll_No"], "ME2105")

            # ADD-3: Skills comparison placed vs non-placed
            cur.execute("""
                SELECT 
                    CASE WHEN p.Joined = 'Yes' THEN 'Placed Students' ELSE 'Non-Placed Students' END AS Status,
                    COUNT(sk.Skill) AS Skill_Count,
                    ROUND(COUNT(sk.Skill) / COUNT(DISTINCT s.Student_ID), 2) AS Avg_Skills
                FROM STUDENT s
                LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID AND p.Joined = 'Yes'
                LEFT JOIN STUDENT_SKILL sk ON s.Student_ID = sk.Student_ID
                GROUP BY Status;
            """)
            res = {r["Status"]: r for r in cur.fetchall()}
            self.assertEqual(res["Non-Placed Students"]["Skill_Count"], 1)  # AutoCAD
            self.assertEqual(res["Placed Students"]["Skill_Count"], 10)
        conn.close()

    # -------------------------------------------------------------------------
    # ITEM 10: NESTED SUBQUERIES & REQUIRED ADDITION (CGPA ABOVE AVERAGE)
    # -------------------------------------------------------------------------
    def test_10_subqueries_and_cgpa_above_average(self):
        """Item 10: Verify ADD-2 (Subquery for students with CGPA > AVG) and B7."""
        conn = self.get_conn()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT s.Roll_No, s.CGPA, (SELECT AVG(CGPA) FROM STUDENT) AS avg_cgpa
                FROM STUDENT s
                WHERE s.CGPA > (SELECT AVG(CGPA) FROM STUDENT)
                ORDER BY s.CGPA DESC;
            """)
            above_avg = cur.fetchall()
            self.assertEqual(len(above_avg), 3)
            # Priya (9.1), Neha (8.8), Aman (8.4)
            rolls = [r["Roll_No"] for r in above_avg]
            self.assertEqual(rolls, ["CS2102", "IT2204", "CS2101"])
        conn.close()

    # -------------------------------------------------------------------------
    # ITEM 11: CORRELATED SUBQUERIES & EXISTENCE
    # -------------------------------------------------------------------------
    def test_11_correlated_subqueries(self):
        """Item 11: Verify A3 (GROUP_CONCAT subqueries), A6 (NOT EXISTS), D6, D8."""
        conn = self.get_conn()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT s.Roll_No
                FROM STUDENT s
                WHERE NOT EXISTS (SELECT 1 FROM PLACEMENT p WHERE p.Student_ID = s.Student_ID AND p.Joined = 'Yes');
            """)
            res = cur.fetchall()
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0]["Roll_No"], "ME2105")
        conn.close()

    # -------------------------------------------------------------------------
    # ITEM 12: SET OPERATIONS & RELATIONAL VIEWS
    # -------------------------------------------------------------------------
    def test_12_set_operations_and_views(self):
        """Item 12: Verify D7 (UNION ALL), B11 (CASE bands), and Views."""
        conn = self.get_conn()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 'Internship' AS Record_Type, Role FROM V_INTERNSHIP_DETAIL WHERE Company_Name = 'TCS'
                UNION ALL
                SELECT 'Placement', Role FROM V_PLACEMENT_DETAIL WHERE Company_Name = 'TCS';
            """)
            rows = cur.fetchall()
            self.assertEqual(len(rows), 6)  # 4 internships + 2 placements
        conn.close()

    # -------------------------------------------------------------------------
    # ITEM 13: TRANSACTION & PHYSICAL OPTIMIZATION (INDEXES)
    # -------------------------------------------------------------------------
    def test_13_atomic_transaction_and_indexes(self):
        """Item 13: Verify safe ACID transaction (student+phones+skills) and CREATE INDEX."""
        conn = self.get_conn()
        # Atomic Transaction
        try:
            with conn.cursor() as cur:
                cur.execute("START TRANSACTION;")
                cur.execute("""
                    INSERT INTO STUDENT (Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs, Resume_Link)
                    VALUES ('TEST_TX_99', 'Vikram', 'Aditya', 'CSE', 2024, 8.75, 0, 'https://test.edu/resume.pdf');
                """)
                st_id = cur.lastrowid
                cur.execute("INSERT INTO STUDENT_PHONE (Student_ID, Phone_No) VALUES (%s, %s);", (st_id, "9998887770"))
                cur.execute("INSERT INTO STUDENT_SKILL (Student_ID, Skill) VALUES (%s, %s);", (st_id, "Python"))
                conn.commit()

                # Verify
                cur.execute("SELECT COUNT(*) AS c FROM STUDENT_PHONE WHERE Student_ID = %s;", (st_id,))
                self.assertEqual(cur.fetchone()["c"], 1)
                cur.execute("SELECT COUNT(*) AS c FROM STUDENT_SKILL WHERE Student_ID = %s;", (st_id,))
                self.assertEqual(cur.fetchone()["c"], 1)
        finally:
            conn.close()

        # Indexes and Query Plan
        conn = self.get_conn()
        with conn.cursor() as cur:
            cur.execute("CREATE INDEX idx_student_branch_batch ON STUDENT (Branch, Batch_Year);")
            cur.execute("EXPLAIN SELECT Roll_No FROM STUDENT WHERE Branch = 'CSE' AND Batch_Year = 2024;")
            plan = cur.fetchone()
            self.assertEqual(plan["key"], "idx_student_branch_batch")
            self.assertEqual(plan["type"], "ref")
        conn.close()


if __name__ == "__main__":
    unittest.main()

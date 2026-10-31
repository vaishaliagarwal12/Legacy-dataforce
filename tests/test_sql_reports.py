import os
import io
import csv
import unittest
import pymysql
from app import create_app
from config import Config
from services.sql_report_service import validate_custom_sql, execute_custom_query, list_saved_queries
from services.exceptions import ValidationError


class SqlReportsFeatureTests(unittest.TestCase):
    """Comprehensive test suite verifying Part 1 (Saved DBMS Queries)
    and Part 2 (Custom Read-Only SQL Console with Server-Side Safety Rules).
    """

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()

    # =========================================================================
    # Part 1: Saved Queries Verification
    # =========================================================================

    def test_sql_reports_page_loads(self):
        """Verify that GET /sql-reports renders HTTP 200 and displays both Part 1 and Part 2."""
        response = self.client.get("/sql-reports")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")
        self.assertIn("Part 1: Saved DBMS Queries", content)
        self.assertIn("Part 2: Custom SQL Box", content)
        self.assertIn("placement_readonly", content)
        self.assertIn("Saved DBMS Query", content)

    def test_saved_queries_catalog_groups(self):
        """Verify saved queries are categorized into Students, Placements, Internships, Combined."""
        queries = list_saved_queries()
        self.assertGreaterEqual(len(queries), 30)

        groups = {q["group"] for q in queries}
        self.assertIn("Students", groups)
        self.assertIn("Placements", groups)
        self.assertIn("Internships", groups)
        self.assertIn("Combined", groups)

        for q in queries:
            self.assertTrue(len(q["dbms_concept"]) > 10, f"Query {q['id']} missing DBMS explanation.")
            self.assertTrue("SELECT" in q["sql"].upper(), f"Query {q['id']} is not a SELECT query.")

    def test_run_saved_query_students(self):
        """Verify executing saved query from Students group returns columns and rows."""
        payload = {"query_id": "students_all", "params": {}}
        resp = self.client.post("/api/sql-reports/run-saved", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()["data"]
        self.assertIn("columns", data)
        self.assertIn("Roll_No", data["columns"])
        self.assertGreater(data["row_count"], 0)
        self.assertGreater(data["execution_time_ms"], 0)

    def test_run_saved_query_with_parameters(self):
        """Verify parameterization: passing branch and batch_year filters correctly via %s without string injection."""
        payload = {
            "query_id": "students_branch_batch",
            "params": {"branch": "CSE", "batch_year": 2024},
        }
        resp = self.client.post("/api/sql-reports/run-saved", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()["data"]
        self.assertEqual(data["params_used"], ["CSE", 2024])
        for row in data["rows"]:
            self.assertEqual(row["Branch"], "CSE")
            self.assertEqual(row["Batch_Year"], 2024)

    def test_run_saved_query_placements(self):
        """Verify executing saved query from Placements group (B1 - Placed students)."""
        payload = {"query_id": "placements_all_joined", "params": {}}
        resp = self.client.post("/api/sql-reports/run-saved", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()["data"]
        self.assertIn("Company_Name", data["columns"])
        self.assertIn("Package", data["columns"])
        self.assertGreater(data["row_count"], 0)

    def test_run_saved_query_internships(self):
        """Verify executing saved query from Internships group (C3 - Compliance audit)."""
        payload = {"query_id": "internships_mandatory_compliance", "params": {}}
        resp = self.client.post("/api/sql-reports/run-saved", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()["data"]
        self.assertIn("Mandatory_Done", data["columns"])
        self.assertGreater(data["row_count"], 0)

    def test_run_saved_query_combined(self):
        """Verify executing saved query from Combined group (D1 - Internships converted to jobs)."""
        payload = {"query_id": "combined_internship_to_job", "params": {}}
        resp = self.client.post("/api/sql-reports/run-saved", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()["data"]
        self.assertIn("Student_Name", data["columns"])
        self.assertIn("Company_Name", data["columns"])
        self.assertGreater(data["row_count"], 0)

    def test_export_saved_query_csv(self):
        """Verify GET /sql-reports/export-saved streams a valid CSV document."""
        resp = self.client.get("/sql-reports/export-saved?query_id=students_all")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/csv", resp.headers["Content-Type"])
        self.assertIn("filename=students_all_export.csv", resp.headers["Content-Disposition"])
        reader = csv.reader(io.StringIO(resp.data.decode("utf-8")))
        rows = list(reader)
        self.assertGreater(len(rows), 1)  # header + data
        self.assertIn("Roll_No", rows[0])

    # =========================================================================
    # Part 2: Custom SQL Box & Server-Side Security Enforcement
    # =========================================================================

    def test_safety_reject_drop_table(self):
        """Requirement: Reject DROP TABLE on the server."""
        malicious_sqls = [
            "DROP TABLE STUDENT;",
            "drop table company",
            "DROP TABLE IF EXISTS PLACEMENT;",
        ]
        for sql in malicious_sqls:
            with self.assertRaises(ValidationError) as ctx:
                validate_custom_sql(sql)
            self.assertIn("DROP", ctx.exception.message)

            # Test via Flask API endpoint as well
            resp = self.client.post("/api/sql-reports/run-custom", json={"sql": sql})
            self.assertEqual(resp.status_code, 400)
            json_data = resp.get_json()
            self.assertEqual(json_data["status"], "error")
            self.assertIn("DROP", json_data["message"])

    def test_safety_reject_second_statement(self):
        """Requirement: Reject multiple statements / stacked queries."""
        stacked_sqls = [
            "SELECT * FROM STUDENT; DROP TABLE COMPANY;",
            "SELECT * FROM STUDENT; SELECT * FROM COMPANY;",
            "SELECT 1; UPDATE STUDENT SET CGPA = 10.0;",
            "SELECT * FROM PLACEMENT; TRUNCATE TABLE STUDENT;",
        ]
        for sql in stacked_sqls:
            with self.assertRaises(ValidationError) as ctx:
                validate_custom_sql(sql)
            self.assertIn("Multiple statements", ctx.exception.message)

            resp = self.client.post("/api/sql-reports/run-custom", json={"sql": sql})
            self.assertEqual(resp.status_code, 400)
            json_data = resp.get_json()
            self.assertEqual(json_data["status"], "error")
            self.assertIn("Multiple statements", json_data["message"])

    def test_safety_reject_missing_select(self):
        """Requirement: Reject statements that do not start with SELECT."""
        non_select_sqls = [
            "INSERT INTO STUDENT (Roll_No, First_Name) VALUES ('X1', 'Test');",
            "UPDATE STUDENT SET CGPA = 9.5 WHERE Student_ID = 1;",
            "DELETE FROM STUDENT WHERE Student_ID = 1;",
            "ALTER TABLE STUDENT ADD COLUMN Hacked INT;",
            "TRUNCATE TABLE STUDENT;",
            "CREATE TABLE NewTable (id INT);",
        ]
        for sql in non_select_sqls:
            with self.assertRaises(ValidationError) as ctx:
                validate_custom_sql(sql)
            self.assertTrue("SELECT" in ctx.exception.message or "Forbidden" in ctx.exception.message)

            resp = self.client.post("/api/sql-reports/run-custom", json={"sql": sql})
            self.assertEqual(resp.status_code, 400)
            json_data = resp.get_json()
            self.assertEqual(json_data["status"], "error")

    def test_safety_reject_comments_hiding_statements(self):
        """Requirement: Reject SQL comments (-- , /* */, #) that could hide statements."""
        comment_sqls = [
            "SELECT * FROM STUDENT -- hiding extra commands",
            "SELECT * FROM STUDENT /* block comment */",
            "SELECT * FROM STUDENT # hash comment",
            "/* bypass */ SELECT * FROM STUDENT",
        ]
        for sql in comment_sqls:
            with self.assertRaises(ValidationError) as ctx:
                validate_custom_sql(sql)
            self.assertIn("comment", ctx.exception.message.lower())

            resp = self.client.post("/api/sql-reports/run-custom", json={"sql": sql})
            self.assertEqual(resp.status_code, 400)
            json_data = resp.get_json()
            self.assertEqual(json_data["status"], "error")
            self.assertIn("comment", json_data["message"].lower())

    def test_custom_query_runs_as_readonly_user(self):
        """Requirement: Run custom queries using separate MySQL user with SELECT permission only."""
        sql = "SELECT USER() AS active_user, CURRENT_USER() AS authenticated_user;"
        res = execute_custom_query(sql)
        self.assertEqual(res["status"], "success")
        self.assertIn("placement_readonly", str(res["rows"][0]["authenticated_user"]))

        # Verify engine-level block: direct attempt to execute write under placement_readonly
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_READONLY_USER,
            password=Config.MYSQL_READONLY_PASSWORD,
            database=Config.MYSQL_DB,
        )
        cur = conn.cursor()
        with self.assertRaises((pymysql.err.ProgrammingError, pymysql.err.OperationalError)) as cm:
            cur.execute("CREATE TABLE engine_security_test (id INT);")
        self.assertEqual(cm.exception.args[0], 1142)  # 1142: command denied
        cur.close()
        conn.close()

    def test_custom_query_row_limit_and_timeout(self):
        """Requirement: Limit results to 500 rows and enforce query timeout."""
        # Check automatic LIMIT 500 append
        unlimited_sql = "SELECT Student_ID FROM STUDENT"
        validated = validate_custom_sql(unlimited_sql)
        self.assertTrue("LIMIT 500" in validated)

        # Check clamping if user requests > 500
        excessive_sql = "SELECT Student_ID FROM STUDENT LIMIT 10000"
        clamped = validate_custom_sql(excessive_sql)
        self.assertTrue("LIMIT 500" in clamped)
        self.assertNotIn("10000", clamped)

    def test_custom_query_shows_columns_rows_count_and_execution_time(self):
        """Requirement: Show column names, rows, row count and execution time."""
        sql = "SELECT Branch, COUNT(*) AS Headcount, ROUND(AVG(CGPA), 2) AS Mean_CGPA FROM STUDENT GROUP BY Branch ORDER BY Headcount DESC"
        resp = self.client.post("/api/sql-reports/run-custom", json={"sql": sql})
        self.assertEqual(resp.status_code, 200)
        json_data = resp.get_json()
        self.assertEqual(json_data["status"], "success")
        res = json_data["data"]

        # Columns
        self.assertEqual(res["columns"], ["Branch", "Headcount", "Mean_CGPA"])
        # Rows
        self.assertIsInstance(res["rows"], list)
        self.assertGreater(len(res["rows"]), 0)
        # Row count
        self.assertEqual(res["row_count"], len(res["rows"]))
        # Execution time
        self.assertGreater(res["execution_time_ms"], 0)

    def test_custom_query_readable_error_instead_of_crash(self):
        """Requirement: Database errors show a readable message instead of a crash."""
        sql = "SELECT Non_Existent_Column_XYZ FROM STUDENT"
        resp = self.client.post("/api/sql-reports/run-custom", json={"sql": sql})
        # Handled gracefully, returns readable error message
        self.assertEqual(resp.status_code, 200)
        json_data = resp.get_json()
        self.assertEqual(json_data["status"], "error")
        self.assertIn("Non_Existent_Column_XYZ", json_data["message"])
        self.assertEqual(json_data["data"]["row_count"], 0)

    def test_export_custom_query_csv(self):
        """Verify POST /sql-reports/export-custom returns valid CSV attachment."""
        sql = "SELECT Student_ID, Roll_No, Branch, CGPA FROM STUDENT LIMIT 5"
        resp = self.client.post("/sql-reports/export-custom", data={"sql": sql})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/csv", resp.headers["Content-Type"])
        self.assertIn("filename=custom_sql_results.csv", resp.headers["Content-Disposition"])
        reader = csv.reader(io.StringIO(resp.data.decode("utf-8")))
        rows = list(reader)
        self.assertEqual(len(rows), 6)  # header + 5 rows
        self.assertEqual(rows[0], ["Student_ID", "Roll_No", "Branch", "CGPA"])


if __name__ == "__main__":
    unittest.main()

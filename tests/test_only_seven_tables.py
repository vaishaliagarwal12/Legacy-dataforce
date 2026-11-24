import os
import re
import glob
import pytest
from db.connection import get_connection, execute_query
import services.sql_report_service as srs

FORBIDDEN_TABLES = [
    "UNIVERSITY",
    "COURSE",
    "STUDENT_COURSE",
    "STUDENT_PROFILE",
    "RESUME",
    "EDUCATION_DOCUMENT",
    "SEMESTER_RESULT",
    "RECRUITMENT_DRIVE",
    "OPPORTUNITY",
    "ELIGIBILITY",
    "ELIGIBILITY_BRANCH",
    "SELECTION_PROCESS",
    "INTERNSHIP_REQUIREMENT",
]

FORBIDDEN_COLUMNS = [
    "Opportunity_ID",
    "Requirement_ID",
]

CANONICAL_7_BASE_TABLES = {
    "STUDENT",
    "STUDENT_PHONE",
    "STUDENT_SKILL",
    "COMPANY",
    "PLACEMENT",
    "PLACEMENT_SKILL",
    "INTERNSHIP",
}

CANONICAL_2_VIEWS = {
    "V_PLACEMENT_DETAIL",
    "V_INTERNSHIP_DETAIL",
}


def _extract_sql_queries_from_services():
    """Extracts all SQL query string literals from Python service modules."""
    sql_regex = re.compile(
        r'"""([\s\S]*?)"""|\'\'\'([\s\S]*?)\'\'\'|"((?:SELECT|INSERT|UPDATE|DELETE|WITH)\b[\s\S]*?)"|\'((?:SELECT|INSERT|UPDATE|DELETE|WITH)\b[\s\S]*?)\'',
        re.IGNORECASE,
    )
    service_files = sorted(glob.glob("services/*.py"))
    extracted = []

    for sf in service_files:
        with open(sf, "r", encoding="utf-8") as f:
            content = f.read()
        for m in sql_regex.finditer(content):
            raw = next(s for s in m.groups() if s)
            cleaned = raw.strip()
            first_word = cleaned.split()[0].upper() if cleaned.split() else ""
            if first_word in ["SELECT", "INSERT", "UPDATE", "DELETE", "WITH"] and len(cleaned.split()) > 2:
                start_pos = m.start()
                line_no = content[:start_pos].count("\n") + 1
                extracted.append((sf, line_no, cleaned))

    return extracted


class TestOnlySevenTablesArchitecture:
    """Rigorous test suite guaranteeing the system runs EXCLUSIVELY on the canonical 7-table schema."""

    def test_01_information_schema_exactly_seven_base_tables_and_two_views(self):
        """Verifies that the database contains strictly 7 base tables and 2 views."""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT TABLE_NAME, TABLE_TYPE 
                    FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = DATABASE()
                    ORDER BY TABLE_NAME ASC
                    """
                )
                rows = cur.fetchall()

        base_tables = {r["TABLE_NAME"].upper() for r in rows if r["TABLE_TYPE"] == "BASE TABLE"}
        views = {r["TABLE_NAME"].upper() for r in rows if r["TABLE_TYPE"] == "VIEW"}

        assert base_tables == CANONICAL_7_BASE_TABLES, (
            f"Base tables mismatch. Expected {CANONICAL_7_BASE_TABLES}, found {base_tables}"
        )
        assert views == CANONICAL_2_VIEWS, (
            f"Views mismatch. Expected {CANONICAL_2_VIEWS}, found {views}"
        )
        assert len(rows) == 9, f"Total tables + views must be exactly 9, found {len(rows)}"

    def test_02_service_layer_queries_contain_no_removed_tables(self):
        """Verifies that no SQL query in services/*.py references any dropped table."""
        queries = _extract_sql_queries_from_services()
        assert len(queries) > 50, "Expected at least 50 SQL queries extracted from services"

        violations = []
        for sf, line, sql in queries:
            for ft in FORBIDDEN_TABLES:
                if re.search(rf"\b{ft}\b", sql, re.IGNORECASE):
                    violations.append(f"{sf}:{line} references dropped table '{ft}' in: {sql[:100]}...")

        assert not violations, f"Found {len(violations)} dropped table references in services:\n" + "\n".join(violations)

    def test_03_service_layer_queries_contain_no_removed_columns(self):
        """Verifies that no SQL query in services/*.py references dropped columns or forbidden values."""
        queries = _extract_sql_queries_from_services()
        violations = []
        for sf, line, sql in queries:
            for fc in FORBIDDEN_COLUMNS:
                if re.search(rf"\b{fc}\b", sql, re.IGNORECASE):
                    violations.append(f"{sf}:{line} references dropped column '{fc}' in: {sql[:100]}...")
            if re.search(r"Offer_Status\s*=\s*['\"]Joined['\"]", sql, re.IGNORECASE):
                violations.append(f"{sf}:{line} uses forbidden value Offer_Status='Joined' in: {sql[:100]}...")

        assert not violations, f"Found {len(violations)} forbidden column/value references in services:\n" + "\n".join(violations)

    def test_04_saved_queries_contain_no_removed_tables_or_columns(self):
        """Verifies that all SAVED_QUERIES in sql_report_service use only the 7 tables and 2 views."""
        violations = []
        for q in srs.SAVED_QUERIES:
            sql = q["sql"]
            qid = q["id"]
            for ft in FORBIDDEN_TABLES:
                if re.search(rf"\b{ft}\b", sql, re.IGNORECASE):
                    violations.append(f"Saved query '{qid}' mentions dropped table '{ft}'")
            for fc in FORBIDDEN_COLUMNS:
                if re.search(rf"\b{fc}\b", sql, re.IGNORECASE):
                    violations.append(f"Saved query '{qid}' mentions dropped column '{fc}'")
            if re.search(r"Offer_Status\s*=\s*['\"]Joined['\"]", sql, re.IGNORECASE):
                violations.append(f"Saved query '{qid}' uses forbidden value Offer_Status='Joined'")

        assert not violations, f"Found {len(violations)} violations in SAVED_QUERIES:\n" + "\n".join(violations)

    def test_05_saved_queries_categories_cover_seven_required_groups(self):
        """Verifies that SAVED_QUERIES covers the required 7 categories."""
        expected_groups = {
            "Students",
            "Companies",
            "Placements",
            "Internships",
            "Dashboard KPIs",
            "Compliance (Mandatory Internship 1 and 2)",
            "Analytics",
        }
        actual_groups = {q["group"] for q in srs.SAVED_QUERIES}
        assert actual_groups == expected_groups, (
            f"Saved query categories mismatch. Expected {expected_groups}, found {actual_groups}"
        )

    def test_06_explain_all_saved_queries_on_mysql(self):
        """Executes EXPLAIN on every saved query to confirm MySQL schema validity."""
        with get_connection() as conn:
            with conn.cursor() as cur:
                for q in srs.SAVED_QUERIES:
                    sql = q["sql"]
                    # Replace placeholders with valid dummy values for EXPLAIN
                    if any(k in sql.lower() for k in ["start_date", "end_date", "date"]):
                        test_sql = sql.replace("%s", "'2024-01-01'")
                    else:
                        test_sql = sql.replace("%s", "'1'")
                    
                    try:
                        cur.execute(f"EXPLAIN {test_sql}")
                        cur.fetchall()
                    except Exception as err:
                        pytest.fail(f"EXPLAIN failed for saved query '{q['id']}': {err}\nSQL:\n{sql}")

    def test_07_execute_all_saved_queries_with_parameters(self):
        """Executes every saved query with sample parameters via execute_saved_query to ensure zero runtime errors."""
        sample_params = {
            "branch": "Computer Science and Engineering",
            "batch_year": 2024,
            "roll_no": "20CS001",
            "skill": "Python",
            "min_cgpa": 8.0,
            "company_name": "Google India",
            "min_package": 10.0,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "search_name": "A",
            "student_id": 1,
        }

        for q in srs.SAVED_QUERIES:
            qid = q["id"]
            pvals = {}
            for p in q.get("params", []):
                pname = p["name"]
                if pname in sample_params:
                    pvals[pname] = sample_params[pname]
                elif p.get("default") is not None:
                    pvals[pname] = p["default"]
                elif p.get("type") == "number":
                    pvals[pname] = 10
                elif p.get("type") == "date":
                    pvals[pname] = "2024-01-01"
                else:
                    pvals[pname] = "Test"

            if qid == "students_name_search":
                pvals["search_name"] = "A"
            elif qid == "combined_company_polymorphic":
                pvals["company_name"] = "Google India"

            result = srs.execute_saved_query(qid, pvals)
            assert "rows" in result, f"Result for query '{qid}' missing 'rows' key"
            assert "columns" in result, f"Result for query '{qid}' missing 'columns' key"
            assert result["execution_time_ms"] >= 0, f"Query '{qid}' returned invalid execution time"

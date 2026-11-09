"""Tests for Phase 4: Dynamic SQL Report Parameter Defaults, Database-Driven Options,
and Centralized Branch Labels Metadata.
"""

from unittest.mock import patch
import pytest

from services.dashboard_service import get_dashboard_filter_options
from services.exceptions import ValidationError
from services.sql_report_service import (
    SAVED_QUERIES,
    get_report_dynamic_options,
    get_saved_query,
    list_saved_queries,
    execute_saved_query,
)


class TestPhase4SqlReportDynamicity:
    """Verifies that SQL report parameter defaults, options, and execution are fully dynamic."""

    def test_saved_queries_catalog_has_no_demo_data_defaults(self):
        """Task 1: Verify that SAVED_QUERIES definitions do not hardcode arbitrary demo values as defaults."""
        forbidden_demo_defaults = {
            2024,
            "2024",
            "CS201802",
            "Python",
            "Infosys Technologies",
            "Aarav",
            10.0,
            8.0,
            "2023-01-01",
            "2024-12-31",
        }

        for q in SAVED_QUERIES:
            for p in q.get("params", []):
                default_val = p.get("default")
                assert default_val not in forbidden_demo_defaults, (
                    f"Query '{q['id']}' param '{p['name']}' still has hardcoded demo default '{default_val}'"
                )

    def test_saved_queries_preserve_helpful_placeholders(self):
        """Task 1: Explanatory placeholders must remain present for UI guidance without acting as hidden query values."""
        q_map = {q["id"]: q for q in SAVED_QUERIES}

        # students_profile
        profile_params = {p["name"]: p for p in q_map["students_profile"]["params"]}
        assert "placeholder" in profile_params["roll_no"]
        assert "CS201802" in profile_params["roll_no"]["placeholder"]
        assert "default" not in profile_params["roll_no"]

        # students_name_search
        search_params = {p["name"]: p for p in q_map["students_name_search"]["params"]}
        assert "placeholder" in search_params["search_name"]
        assert "Aarav" in search_params["search_name"]["placeholder"]
        assert "default" not in search_params["search_name"]

        # placements_above_threshold
        threshold_params = {p["name"]: p for p in q_map["placements_above_threshold"]["params"]}
        assert "placeholder" in threshold_params["min_package"]
        assert "default" not in threshold_params["min_package"]

    def test_dynamic_report_parameter_options_retrieved_from_database(self, app):
        """Task 2: Dynamic parameter options must query live database tables."""
        opts = get_report_dynamic_options()
        assert isinstance(opts, dict)
        assert "branches" in opts
        assert "batch_years" in opts
        assert "companies" in opts
        assert "students" in opts
        assert "skills" in opts

        # Verify live database content is populated
        assert len(opts["branches"]) >= 4
        assert "CSE" in opts["branches"]
        assert len(opts["companies"]) >= 10
        assert len(opts["students"]) >= 20
        assert len(opts["skills"]) >= 20

    def test_list_saved_queries_injects_dynamic_options(self, app):
        """Task 2: list_saved_queries() must dynamically populate options for select parameters."""
        queries = list_saved_queries()
        q_map = {q["id"]: q for q in queries}

        # Branch & batch query
        branch_batch_p = {p["name"]: p for p in q_map["students_branch_batch"]["params"]}
        assert branch_batch_p["branch"]["type"] == "select"
        assert len(branch_batch_p["branch"]["options"]) >= 4
        assert "CSE" in branch_batch_p["branch"]["options"]
        assert branch_batch_p["batch_year"]["type"] == "select"
        assert len(branch_batch_p["batch_year"]["options"]) >= 3

        # Company parameters
        by_company_p = {p["name"]: p for p in q_map["placements_by_company"]["params"]}
        assert by_company_p["company_name"]["type"] == "select"
        assert len(by_company_p["company_name"]["options"]) >= 10

        # Student parameter
        student_history_p = {p["name"]: p for p in q_map["internships_student_history"]["params"]}
        assert student_history_p["roll_no"]["type"] == "select"
        assert len(student_history_p["roll_no"]["options"]) >= 20

        # Skill parameter
        skill_p = {p["name"]: p for p in q_map["students_by_skill"]["params"]}
        assert skill_p["skill"]["type"] == "select"
        assert len(skill_p["skill"]["options"]) >= 20

    def test_empty_database_options_handled_gracefully(self):
        """Task 2: If database is empty or connection fails, options return empty lists without 500 error."""
        with patch("services.sql_report_service.get_cursor", side_effect=Exception("DB Down")):
            opts = get_report_dynamic_options()
            assert opts == {
                "branches": [],
                "batch_years": [],
                "companies": [],
                "students": [],
                "skills": [],
            }

            # list_saved_queries continues to work with empty options
            queries = list_saved_queries()
            assert len(queries) >= 30
            for q in queries:
                for p in q.get("params", []):
                    if p.get("dynamic_source"):
                        assert p["options"] == []

    def test_execute_saved_query_blocks_execution_without_required_parameters(self, app):
        """Task 1: Verify execution fails with clear ValidationError if required parameter is omitted."""
        # students_profile requires roll_no
        with pytest.raises(ValidationError) as exc1:
            execute_saved_query("students_profile", {})
        assert "Parameter 'Roll Number' is required" in str(exc1.value)

        # placements_by_company requires company_name
        with pytest.raises(ValidationError) as exc2:
            execute_saved_query("placements_by_company", {})
        assert "Parameter 'Company Name' is required" in str(exc2.value)

        # students_name_search requires search_name
        with pytest.raises(ValidationError) as exc3:
            execute_saved_query("students_name_search", {})
        assert "Parameter 'Name Keyword' is required" in str(exc3.value)

        # placements_above_threshold requires min_package
        with pytest.raises(ValidationError) as exc4:
            execute_saved_query("placements_above_threshold", {})
        assert "Parameter 'Minimum Package (LPA)' is required" in str(exc4.value)

        # combined_company_polymorphic requires company_name
        with pytest.raises(ValidationError) as exc5:
            execute_saved_query("combined_company_polymorphic", {})
        assert "Parameter 'Company Name' is required" in str(exc5.value)

    def test_execute_saved_query_validates_parameter_ranges_and_formats(self, app):
        """Task 1 & 2: Strict parameter validation checks values and constraints."""
        # Invalid min_cgpa (> 10.0)
        with pytest.raises(ValidationError) as exc1:
            execute_saved_query("students_high_cgpa_nobacklogs", {"min_cgpa": 12.0})
        assert "between 0.0 and 10.0" in str(exc1.value)

        # Invalid min_package (< 0)
        with pytest.raises(ValidationError) as exc2:
            execute_saved_query("placements_above_threshold", {"min_package": -3.5})
        assert "cannot be negative" in str(exc2.value)

        # Invalid batch_year (out of bounds)
        with pytest.raises(ValidationError) as exc3:
            execute_saved_query(
                "students_branch_batch", {"branch": "CSE", "batch_year": 1850}
            )
        assert "between 2000 and 2100" in str(exc3.value)

        # Invalid date format
        with pytest.raises(ValidationError) as exc4:
            execute_saved_query(
                "internships_date_range",
                {"start_date": "not-a-date", "end_date": "2024-12-31"},
            )
        assert "YYYY-MM-DD" in str(exc4.value)

        # Chronological dates check: start > end
        with pytest.raises(ValidationError) as exc5:
            execute_saved_query(
                "internships_date_range",
                {"start_date": "2024-12-31", "end_date": "2023-01-01"},
            )
        assert "Start Date cannot be later than End Date" in str(exc5.value)

    def test_execute_saved_query_success_with_valid_parameters(self, app):
        """Verify saved queries execute correctly when supplied with legitimate parameters."""
        res = execute_saved_query(
            "students_branch_batch", {"branch": "CSE", "batch_year": 2024}
        )
        assert res["id"] == "students_branch_batch"
        assert res["params_used"] == ["CSE", 2024]
        assert "rows" in res
        assert res["row_count"] >= 0

    def test_api_run_saved_query_returns_validation_error_status(self, client):
        """Verify HTTP API returns 400 JSON when parameters are missing."""
        resp = client.post(
            "/api/sql-reports/run-saved",
            json={"query_id": "students_profile", "params": {}},
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["status"] == "error"
        assert "Roll Number" in data["message"]


class TestPhase4BranchLabelsMetadata:
    """Verifies that branch display label metadata is centralized and database-driven."""

    def test_dashboard_filter_options_provides_branch_labels(self, app):
        """Task 3: get_dashboard_filter_options must return branch_labels mapping dictionary."""
        opts = get_dashboard_filter_options()
        assert "branch_labels" in opts
        labels = opts["branch_labels"]
        assert isinstance(labels, dict)
        assert labels.get("CSE") == "Computer Science (CSE)"
        assert labels.get("ECE") == "Electronics & Comm (ECE)"
        assert labels.get("ME") == "Mechanical (ME)"
        assert labels.get("IT") == "Information Tech (IT)"

    def test_students_index_renders_friendly_branch_labels(self, client):
        """Task 3: /students template must render friendly department names sourced from filter_options."""
        res = client.get("/students")
        assert res.status_code == 200
        html = res.get_data(as_text=True)
        assert "Computer Science (CSE)" in html
        assert "Electronics &amp; Comm (ECE)" in html or "Electronics & Comm (ECE)" in html

    def test_placements_index_renders_friendly_branch_labels(self, client):
        """Task 3: /placements template must render friendly department names sourced from filter_options."""
        res = client.get("/placements")
        assert res.status_code == 200
        html = res.get_data(as_text=True)
        assert "Computer Science (CSE)" in html
        assert "Electronics &amp; Comm (ECE)" in html or "Electronics & Comm (ECE)" in html

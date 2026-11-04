"""Legacy DataForce - Unit Tests for Service Layer Logic.

Tests student_service, placement_service, internship_service, company_service,
and sql_report_service without reliance on HTTP routing layers.
"""

import pytest
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
from services.placement_service import (
    get_placement_analytics,
    check_candidate_eligibility_for_opportunity,
    get_students_with_multiple_offers,
    list_placement_offers,
)
from services.internship_service import (
    get_internship_dashboard_analytics,
    calculate_internship_duration,
    determine_internship_status,
    check_internship_eligibility,
    list_internships,
)
from services.company_service import (
    list_companies,
    get_company,
    create_company,
    update_company,
    delete_company,
)
from services.sql_report_service import (
    validate_custom_sql,
    list_saved_queries,
    execute_saved_query,
)


class TestStudentServiceUnit:
    """Unit tests for student management service functions."""

    def test_list_students_pagination_and_structure(self, app):
        """Verifies list_students returns paginated records with total counts."""
        result = list_students(page=1, limit=5)
        assert "results" in result
        assert "total" in result
        assert "page" in result
        assert "total_pages" in result
        assert result["page"] == 1
        assert len(result["results"]) <= 5
        assert result["total"] >= len(result["results"])

    def test_get_student_existing_and_non_existing(self, app, clean_test_student):
        """Verifies retrieving an existing student and raising NotFoundError for non-existing."""
        student_id = clean_test_student["Student_ID"]
        fetched = get_student(student_id)
        assert fetched is not None
        assert fetched["Roll_No"] == clean_test_student["Roll_No"]
        assert fetched["Email"] == clean_test_student["Email"]

        with pytest.raises(NotFoundError):
            get_student(999999)

    def test_create_student_duplicate_roll_rejection(self, app, clean_test_student):
        """Verifies attempting to create a student with duplicate Roll_No raises ConflictError."""
        payload = {
            "Roll_No": clean_test_student["Roll_No"],
            "First_Name": "Duplicate",
            "Last_Name": "Tester",
            "Email": "unique_email_duplicate@university.edu",
            "Branch": "Mechanical",
            "Batch_Year": 2024,
            "CGPA": 8.00,
            "Backlogs": 0,
        }
        with pytest.raises(ConflictError):
            create_student(payload)

    def test_create_student_validation_bounds(self, app):
        """Verifies validation catches invalid CGPA and negative backlogs."""
        invalid_cgpa_payload = {
            "Roll_No": "SYN_VAL_TEST_1",
            "First_Name": "Val",
            "Last_Name": "Test",
            "Email": "val1@university.edu",
            "Branch": "Civil",
            "Batch_Year": 2024,
            "CGPA": 11.5,  # Exceeds max 10.0
            "Backlogs": 0,
        }
        with pytest.raises(ValidationError):
            create_student(invalid_cgpa_payload)

        negative_backlogs_payload = {
            "Roll_No": "SYN_VAL_TEST_2",
            "First_Name": "Val",
            "Last_Name": "Test",
            "Email": "val2@university.edu",
            "Branch": "Civil",
            "Batch_Year": 2024,
            "CGPA": 8.0,
            "Backlogs": -1,  # Negative backlogs
        }
        with pytest.raises(ValidationError):
            create_student(negative_backlogs_payload)


class TestPlacementServiceUnit:
    """Unit tests for placement business logic."""

    def test_get_placement_analytics_structure(self, app):
        """Verifies get_placement_analytics returns all required KPI cards and metrics."""
        analytics = get_placement_analytics()
        assert "kpis" in analytics
        kpi = analytics["kpis"]
        assert "total_offers" in kpi
        assert "placed_students" in kpi
        assert "avg_package" in kpi
        assert "highest_package" in kpi
        assert float(kpi["highest_package"]) >= float(kpi["avg_package"])

    def test_get_students_with_multiple_offers(self, app):
        """Verifies query returns students holding 2 or more placement offers."""
        multi_offer_students = get_students_with_multiple_offers(min_offers=2)
        assert isinstance(multi_offer_students, list)
        for s in multi_offer_students:
            assert s["Total_Offers"] >= 2
            assert "Highest_Package" in s
            assert "Accepted_Company" in s

    def test_check_candidate_eligibility_for_opportunity(
        self, app, clean_test_student, clean_test_drive_and_opp
    ):
        """Verifies candidate eligibility checks for branch, CGPA, and backlog thresholds."""
        student = clean_test_student
        opp = clean_test_drive_and_opp["opportunity"]

        # Student CGPA is 8.75, opp Minimum_CGPA is 7.00, branch matches -> Eligible
        eval_result = check_candidate_eligibility_for_opportunity(
            student["Student_ID"], opp["Opportunity_ID"]
        )
        assert eval_result["is_eligible"] is True
        assert len(eval_result["violations"]) == 0


class TestInternshipServiceUnit:
    """Unit tests for academic and additional internship logic."""

    def test_calculate_internship_duration(self):
        """Verifies duration calculation in weeks between start and end dates."""
        duration = calculate_internship_duration("2024-05-01", "2024-07-01")
        assert duration["weeks"] >= 8
        assert calculate_internship_duration(None, "2024-07-01")["weeks"] in (None, 0, 0.0)

    def test_determine_internship_status(self):
        """Verifies automatic status resolution based on dates and certificates."""
        # Completed
        assert (
            determine_internship_status("2023-01-01", "2023-03-01", "https://cert.com/1")
            == "Completed"
        )
        # In Progress (future end date)
        assert determine_internship_status("2026-01-01", "2027-01-01", None) == "In Progress"

    def test_check_internship_academic_eligibility(self, app):
        """Verifies prerequisite SGPA checks for mandatory internships."""
        # Student 1 has Sem 3 SGPA >= 6.0 in seed data
        eval_i1 = check_internship_eligibility(student_id=1, internship_no=1)
        assert "is_eligible" in eval_i1
        assert eval_i1["required_result_semester"] == 3


class TestCompanyServiceUnit:
    """Unit tests for corporate recruiting partner operations."""

    def test_create_and_get_company(self, app, clean_test_company):
        """Verifies creating and fetching company details."""
        comp_id = clean_test_company["Company_ID"]
        fetched = get_company(comp_id)
        assert fetched is not None
        assert fetched["Company_Name"] == clean_test_company["Company_Name"]
        assert fetched["Company_Type"] == clean_test_company["Company_Type"]

    def test_update_company_details(self, app, clean_test_company):
        """Verifies updating an existing company."""
        comp_id = clean_test_company["Company_ID"]
        updated = update_company(comp_id, {"Industry": "AI Technologies"})
        assert updated["Industry"] == "AI Technologies"


class TestSqlReportServiceUnit:
    """Unit tests for SQL report safety validation and catalog."""

    def test_validate_custom_sql_allows_clean_select(self):
        """Verifies safe SELECT queries pass validation."""
        sql = "SELECT Roll_No, First_Name, CGPA FROM STUDENT WHERE CGPA >= 8.0 ORDER BY CGPA DESC"
        validated = validate_custom_sql(sql)
        assert validated.strip().startswith("SELECT")

    def test_validate_custom_sql_rejects_destructive_statements(self):
        """Verifies validation strictly rejects DROP, DELETE, UPDATE, INSERT, ALTER."""
        for bad_sql in [
            "DROP TABLE STUDENT",
            "DELETE FROM STUDENT WHERE 1=1",
            "UPDATE STUDENT SET CGPA = 10.0",
            "INSERT INTO STUDENT VALUES (1, 'Hacked')",
            "ALTER TABLE STUDENT DROP COLUMN CGPA",
        ]:
            with pytest.raises(ValidationError):
                validate_custom_sql(bad_sql)

    def test_validate_custom_sql_rejects_stacked_queries_and_comments(self):
        """Verifies validation blocks multi-statement queries and SQL comments."""
        stacked = "SELECT * FROM STUDENT; SELECT * FROM COMPANY"
        with pytest.raises(ValidationError):
            validate_custom_sql(stacked)

        with_comment = "SELECT * FROM STUDENT -- leak extra rows"
        with pytest.raises(ValidationError):
            validate_custom_sql(with_comment)

    def test_list_saved_queries_catalog(self):
        """Verifies saved queries catalog lists predefined accredited reports."""
        queries = list_saved_queries()
        assert len(queries) >= 10
        groups = {q["group"] for q in queries}
        assert "Students" in groups
        assert "Placements" in groups
        assert "Internships" in groups

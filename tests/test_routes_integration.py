"""Legacy DataForce - Integration Tests for Flask HTTP Routes.

Tests all major web pages and REST endpoints across Dashboard, Students,
Companies, Placements, Internships, Reports, and System Health.
"""

import pytest
import json


class TestRoutesIntegration:
    """Integration test suite testing full HTTP request/response lifecycles."""

    def test_health_endpoint(self, client):
        """Verifies GET /health returns HTTP 200 with service status and MySQL ping."""
        res = client.get("/health")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] in ("healthy", "up")
        assert "database" in data

    def test_dashboard_routes(self, client):
        """Verifies GET / renders HTML dashboard and /api/analytics/dashboard returns JSON metrics."""
        # 1. HTML View
        res_html = client.get("/")
        assert res_html.status_code == 200
        html_text = res_html.get_data(as_text=True)
        assert "Academic Internship Dashboard" in html_text
        assert "Total Students" in html_text
        assert "Placement Rate" in html_text

        # 2. JSON API
        res_api = client.get("/api/analytics/dashboard")
        assert res_api.status_code == 200
        data = res_api.get_json()
        assert data["status"] == "success"
        assert "kpi" in data["data"]
        assert "charts" in data["data"]

        # 3. Filtered JSON API
        res_filter = client.get("/api/analytics/dashboard?branch=Computer+Science&batch_year=2024")
        assert res_filter.status_code == 200
        filtered_data = res_filter.get_json()
        assert filtered_data["status"] == "success"

    def test_student_routes(self, client, clean_test_student):
        """Verifies student management routes: list, detail, and JSON endpoints."""
        student_id = clean_test_student["Student_ID"]

        # 1. HTML List
        res_list = client.get("/students")
        assert res_list.status_code == 200
        assert "Student Career Profiles" in res_list.get_data(as_text=True)

        # 2. HTML Detail
        res_detail = client.get(f"/students/{student_id}")
        assert res_detail.status_code == 200
        assert clean_test_student["Roll_No"] in res_detail.get_data(as_text=True)

        # 3. JSON API List
        res_api = client.get("/api/students")
        assert res_api.status_code == 200
        assert len(res_api.get_json()["data"]) > 0

        # 4. JSON API Detail
        res_api_detail = client.get(f"/api/students/{student_id}")
        assert res_api_detail.status_code == 200
        assert res_api_detail.get_json()["data"]["Roll_No"] == clean_test_student["Roll_No"]

    def test_company_routes(self, client, clean_test_company):
        """Verifies company directory routes: list, detail, and API."""
        cid = clean_test_company["Company_ID"]

        # 1. HTML List
        res_list = client.get("/companies")
        assert res_list.status_code == 200
        assert "Corporate Recruiting Partners" in res_list.get_data(as_text=True)

        # 2. HTML Detail
        res_detail = client.get(f"/companies/{cid}")
        assert res_detail.status_code == 200
        assert clean_test_company["Company_Name"] in res_detail.get_data(as_text=True)

        # 3. JSON API
        res_api = client.get("/api/companies")
        assert res_api.status_code == 200
        assert len(res_api.get_json()["data"]) > 0

    def test_placement_routes(self, client):
        """Verifies placement offers view, detail, and star performers view."""
        # 1. Main View
        res_placements = client.get("/placements")
        assert res_placements.status_code == 200
        assert "Campus Placement Offers" in res_placements.get_data(as_text=True)

        # 2. Multi-offer View
        res_multi = client.get("/placements?view=multiple")
        assert res_multi.status_code == 200
        assert "Star Performers" in res_multi.get_data(as_text=True)

        # 3. API Analytics
        res_analytics = client.get("/api/placements/analytics")
        assert res_analytics.status_code == 200
        assert "kpis" in res_analytics.get_json()["data"]

    def test_internship_routes(self, client):
        """Verifies internship management views across all compliance tabs."""
        # 1. All Internships
        res_all = client.get("/internships?type=All")
        assert res_all.status_code == 200
        assert "All Student Internships" in res_all.get_data(as_text=True)

        # 2. Mandatory Internships
        res_mand = client.get("/internships?type=Mandatory")
        assert res_mand.status_code == 200
        assert "Mandatory Internships" in res_mand.get_data(as_text=True)

        # 3. Additional Internships
        res_add = client.get("/internships?type=Additional")
        assert res_add.status_code == 200
        assert "Additional Voluntary Internships" in res_add.get_data(as_text=True)

        # 4. Missing Mandatory Audit
        res_miss = client.get("/internships?type=Missing")
        assert res_miss.status_code == 200
        assert "Missing Mandatory Internships" in res_miss.get_data(as_text=True)

    def test_report_routes(self, client):
        """Verifies accreditation reports and SQL reporting centre views."""
        # 1. HTML Reports Page
        res_reports = client.get("/reports")
        assert res_reports.status_code == 200
        assert "Reports" in res_reports.get_data(as_text=True)

        # 2. SQL Reports Page
        res_sql = client.get("/sql-reports")
        assert res_sql.status_code == 200
        assert "SQL Reports" in res_sql.get_data(as_text=True)

"""Targeted Feature Verification Tests for Legacy Dataforce.

Verifies:
1. Detailed Student Cohort Report search endpoint and query parameters.
2. Complete Student Profile PDF generation and streaming headers.
3. Individual Mandatory Internship Compliance PDF generation.
4. Student Internship History PDF generation.
5. Missing Mandatory Audit PDF generation.
"""

import pytest


class TestTargetedVerificationFeatures:
    """Tests targeted student cohort searches and PDF generation endpoints."""

    def test_cohort_report_search_kabir_verma(self, client):
        """Verifies searching 'Kabir Verma' on /reports returns only Kabir Verma."""
        res = client.get("/reports?search=Kabir+Verma")
        assert res.status_code == 200
        html = res.get_data(as_text=True)
        assert "Kabir Verma" in html
        assert "EC201803" in html
        # Should NOT include other students like Aarav Sharma
        assert "CS202001" not in html

    def test_cohort_report_search_roll_no(self, client):
        """Verifies searching candidate roll 'EC201803' on /reports returns exact match."""
        res = client.get("/reports?search=EC201803")
        assert res.status_code == 200
        html = res.get_data(as_text=True)
        assert "EC201803" in html
        assert "Kabir Verma" in html
        assert "CS202001" not in html

    def test_cohort_report_search_branch_cse(self, client):
        """Verifies searching branch 'CSE' on /reports returns CSE cohort."""
        res = client.get("/reports?search=CSE")
        assert res.status_code == 200
        html = res.get_data(as_text=True)
        assert "CS202001" in html
        assert "Aarav Sharma" in html
        assert "Diya Patel" in html

    def test_complete_student_profile_pdf_export(self, client):
        """Verifies GET /students/1/export-pdf produces valid PDF."""
        res = client.get("/students/1/export-pdf")
        assert res.status_code == 200
        assert res.content_type == "application/pdf"
        assert "attachment; filename=student_CS202001_profile.pdf" in res.headers.get(
            "Content-Disposition", ""
        )
        data = res.get_data()
        assert data.startswith(b"%PDF-")
        assert len(data) > 1000

    def test_individual_internship_compliance_pdf_export(self, client):
        """Verifies GET /students/1/internship-compliance-pdf produces compliance PDF."""
        res = client.get("/students/1/internship-compliance-pdf")
        assert res.status_code == 200
        assert res.content_type == "application/pdf"
        assert "attachment; filename=internship_compliance_CS202001.pdf" in res.headers.get(
            "Content-Disposition", ""
        )
        data = res.get_data()
        assert data.startswith(b"%PDF-")
        assert len(data) > 1000

    def test_student_internship_history_pdf_export(self, client):
        """Verifies GET /students/1/internships-history-pdf produces history PDF."""
        res = client.get("/students/1/internships-history-pdf")
        assert res.status_code == 200
        assert res.content_type == "application/pdf"
        assert "attachment; filename=internship_history_CS202001.pdf" in res.headers.get(
            "Content-Disposition", ""
        )
        data = res.get_data()
        assert data.startswith(b"%PDF-")
        assert len(data) > 1000

    def test_missing_mandatory_audit_pdf_export(self, client):
        """Verifies GET /internships/missing-mandatory-pdf produces audit PDF."""
        res = client.get("/internships/missing-mandatory-pdf")
        assert res.status_code == 200
        assert res.content_type == "application/pdf"
        assert "attachment; filename=missing_mandatory_audit.pdf" in res.headers.get(
            "Content-Disposition", ""
        )
        data = res.get_data()
        assert data.startswith(b"%PDF-")
        assert len(data) > 1000

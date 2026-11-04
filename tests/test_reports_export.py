"""Legacy DataForce - CSV and PDF Report Export Tests.

Verifies that CSV and PDF report export endpoints generate structurally valid documents
with appropriate HTTP headers, MIME types, and streaming data.
"""

import io
import csv
import pytest


class TestReportsExport:
    """Tests data export endpoints for students, placements, internships, and PDF reports."""

    def test_student_csv_export(self, client):
        """Verifies GET /students/export-csv produces a valid CSV file with expected headers."""
        res = client.get("/students/export-csv")
        assert res.status_code == 200
        assert "text/csv" in res.content_type
        assert "attachment; filename=" in res.headers.get("Content-Disposition", "")

        csv_text = res.get_data(as_text=True)
        reader = csv.reader(io.StringIO(csv_text))
        rows = list(reader)
        assert len(rows) > 1, "CSV should contain a header row and at least one data row"

        header = rows[0]
        assert "Roll No" in header
        assert "First Name" in header
        assert "Branch" in header
        assert "CGPA" in header
        assert "Placement Status" in header

    def test_placement_csv_export(self, client):
        """Verifies GET /placements/export-csv produces valid CSV placement records."""
        res = client.get("/placements/export-csv")
        assert res.status_code == 200
        assert "text/csv" in res.content_type
        assert "attachment; filename=" in res.headers.get("Content-Disposition", "")

        csv_text = res.get_data(as_text=True)
        reader = csv.reader(io.StringIO(csv_text))
        rows = list(reader)
        assert len(rows) > 1

        header = rows[0]
        assert "Roll No" in header
        assert "Company Name" in header
        assert "Package (LPA)" in header
        assert "Offer Status" in header

    def test_internship_csv_export(self, client):
        """Verifies GET /internships/export-csv produces valid CSV internship records."""
        res = client.get("/internships/export-csv")
        assert res.status_code == 200
        assert "text/csv" in res.content_type
        assert "attachment; filename=" in res.headers.get("Content-Disposition", "")

        csv_text = res.get_data(as_text=True)
        reader = csv.reader(io.StringIO(csv_text))
        rows = list(reader)
        assert len(rows) > 1

        header = rows[0]
        assert "Roll No" in header
        assert "Company Name" in header
        assert "Category" in header
        assert "Operational Status" in header

    def test_analytics_report_csv_export(self, client):
        """Verifies GET /reports/export streams cohort placement and internship CSV."""
        res = client.get("/reports/export?branch=Computer+Science")
        assert res.status_code == 200
        assert "text/csv" in res.content_type
        assert "attachment; filename=placement_internship_report.csv" in res.headers.get(
            "Content-Disposition", ""
        )

        csv_text = res.get_data(as_text=True)
        assert "Roll No,Student Name,Email,Branch" in csv_text

    def test_executive_report_pdf_export(self, client):
        """Verifies GET /reports/export-pdf generates a valid binary PDF document."""
        res = client.get("/reports/export-pdf?branch=Computer+Science")
        assert res.status_code == 200
        assert res.content_type == "application/pdf"
        assert "attachment; filename=placement_executive_report.pdf" in res.headers.get(
            "Content-Disposition", ""
        )

        pdf_bytes = res.get_data()
        assert len(pdf_bytes) > 500, "Generated PDF must contain substantial data"
        # Validate standard PDF file header signature
        assert pdf_bytes.startswith(
            b"%PDF-"
        ), "Exported file must start with valid '%PDF-' header signature"

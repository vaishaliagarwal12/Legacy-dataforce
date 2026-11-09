"""Legacy Dataforce - Frontend and Backend Export Truncation Warning Tests.

Tests the complete, limited, empty, and error export workflows across all export endpoints:
1. /students/export-csv
2. /placements/export-csv
3. /internships/export-csv
4. /reports/export (CSV)
5. /reports/export-pdf (PDF)
6. /sql-reports/export-saved (CSV)
7. /sql-reports/export-custom (CSV)

Also validates template export buttons, parameter preservation, alert container presence,
and static JavaScript fetch/blob handling.
"""

import io
import csv
from unittest.mock import patch
import pytest


class TestExportTruncationHeaders:
    """Verifies that all export routes return the standardized X-Export-* headers."""

    def test_student_csv_complete_export(self, client):
        """Verifies full student export sets status=complete and limited=false."""
        resp = client.get("/students/export-csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.content_type
        assert "attachment; filename=" in resp.headers.get("Content-Disposition", "")
        assert resp.headers.get("X-Export-Status") == "complete"
        assert resp.headers.get("X-Export-Limited") == "false"
        assert int(resp.headers.get("X-Export-Count", "0")) > 0
        assert "X-Export-Warning" not in resp.headers

    def test_student_csv_limited_export(self, client):
        """Verifies student export capped by EXPORT_ROW_LIMIT returns truncation headers."""
        with patch.dict(client.application.config, {"EXPORT_ROW_LIMIT": 2}):
            resp = client.get("/students/export-csv")
            assert resp.status_code == 200
            assert resp.headers.get("X-Export-Status") == "limited"
            assert resp.headers.get("X-Export-Limited") == "true"
            assert resp.headers.get("X-Export-Count") == "2"
            assert "X-Export-Warning" in resp.headers
            assert "capped" in resp.headers.get("X-Export-Warning", "").lower()

            reader = csv.reader(io.StringIO(resp.get_data(as_text=True)))
            rows = list(reader)
            # 1 header row + 2 data rows
            assert len(rows) == 3

    def test_student_csv_empty_export(self, client):
        """Verifies student export with zero matches returns status=empty."""
        resp = client.get("/students/export-csv?search=__NON_EXISTENT_QUERY_XYZ_123__")
        assert resp.status_code == 200
        assert resp.headers.get("X-Export-Status") == "empty"
        assert resp.headers.get("X-Export-Limited") == "false"
        assert resp.headers.get("X-Export-Count") == "0"

    def test_placement_csv_complete_and_limited_export(self, client):
        """Verifies placement offers export complete and limited status headers."""
        # Complete
        resp_complete = client.get("/placements/export-csv")
        assert resp_complete.status_code == 200
        assert resp_complete.headers.get("X-Export-Status") == "complete"
        assert resp_complete.headers.get("X-Export-Limited") == "false"

        # Limited
        with patch.dict(client.application.config, {"EXPORT_ROW_LIMIT": 2}):
            resp_limited = client.get("/placements/export-csv")
            assert resp_limited.status_code == 200
            assert resp_limited.headers.get("X-Export-Status") == "limited"
            assert resp_limited.headers.get("X-Export-Limited") == "true"
            assert "X-Export-Warning" in resp_limited.headers

    def test_placement_csv_empty_export(self, client):
        """Verifies placement offers export with no matches returns status=empty."""
        resp = client.get("/placements/export-csv?search=__ZERO_MATCHING_OFFER_XYZ__")
        assert resp.status_code == 200
        assert resp.headers.get("X-Export-Status") == "empty"
        assert resp.headers.get("X-Export-Limited") == "false"

    def test_internship_csv_complete_and_limited_export(self, client):
        """Verifies internships export complete and limited headers."""
        # Complete
        resp_complete = client.get("/internships/export-csv")
        assert resp_complete.status_code == 200
        assert resp_complete.headers.get("X-Export-Status") == "complete"
        assert resp_complete.headers.get("X-Export-Limited") == "false"

        # Limited
        with patch.dict(client.application.config, {"EXPORT_ROW_LIMIT": 2}):
            resp_limited = client.get("/internships/export-csv")
            assert resp_limited.status_code == 200
            assert resp_limited.headers.get("X-Export-Status") == "limited"
            assert resp_limited.headers.get("X-Export-Limited") == "true"
            assert "X-Export-Warning" in resp_limited.headers

    def test_internship_csv_empty_export(self, client):
        """Verifies internships export with no matches returns status=empty."""
        resp = client.get("/internships/export-csv?search=__ZERO_MATCHING_INTERNSHIP_XYZ__")
        assert resp.status_code == 200
        assert resp.headers.get("X-Export-Status") == "empty"
        assert resp.headers.get("X-Export-Limited") == "false"

    def test_reports_csv_and_pdf_export_headers(self, client):
        """Verifies report CSV and PDF exports return correct headers."""
        # Reports CSV Complete
        resp_csv = client.get("/reports/export")
        assert resp_csv.status_code == 200
        assert "text/csv" in resp_csv.content_type
        assert resp_csv.headers.get("X-Export-Status") in ("complete", "limited")

        # Reports CSV Limited
        with patch.dict(client.application.config, {"EXPORT_ROW_LIMIT": 2}):
            resp_csv_ltd = client.get("/reports/export")
            assert resp_csv_ltd.status_code == 200
            assert resp_csv_ltd.headers.get("X-Export-Status") == "limited"
            assert resp_csv_ltd.headers.get("X-Export-Limited") == "true"
            assert "X-Export-Warning" in resp_csv_ltd.headers

        # Reports PDF Complete/Limited
        resp_pdf = client.get("/reports/export-pdf")
        assert resp_pdf.status_code == 200
        assert resp_pdf.content_type == "application/pdf"
        assert "X-Export-Status" in resp_pdf.headers

        # Reports PDF Truncation
        with patch.dict(client.application.config, {"EXPORT_PDF_ROW_LIMIT": 2}):
            resp_pdf_ltd = client.get("/reports/export-pdf")
            assert resp_pdf_ltd.status_code == 200
            assert resp_pdf_ltd.headers.get("X-Export-Status") == "limited"
            assert resp_pdf_ltd.headers.get("X-Export-Limited") == "true"
            assert "X-Export-Warning" in resp_pdf_ltd.headers

    def test_saved_sql_report_csv_headers(self, client):
        """Verifies saved SQL report export sets X-Export headers."""
        resp = client.get("/sql-reports/export-saved?query_id=students_all")
        assert resp.status_code == 200
        assert "text/csv" in resp.content_type
        assert "filename=students_all_export.csv" in resp.headers.get("Content-Disposition", "")
        assert resp.headers.get("X-Export-Status") in ("complete", "limited")
        assert resp.headers.get("X-Export-Limited") in ("true", "false")
        assert "X-Export-Count" in resp.headers

    def test_saved_sql_report_csv_error_handling(self, client):
        """Verifies saved SQL report export handles missing query_id and errors gracefully."""
        # Browser request (no AJAX header): redirects with flash
        resp_browser = client.get("/sql-reports/export-saved")
        assert resp_browser.status_code == 302

        # AJAX request: returns 400 Bad Request
        resp_ajax = client.get(
            "/sql-reports/export-saved",
            headers={"X-Requested-With": "XMLHttpRequest"},
        )
        assert resp_ajax.status_code == 400
        assert "query_id is required" in resp_ajax.get_data(as_text=True)

        # Non-existent query AJAX request: returns 400 Validation Error
        resp_bad = client.get(
            "/sql-reports/export-saved?query_id=non_existent_query_xyz",
            headers={"X-Requested-With": "XMLHttpRequest"},
        )
        assert resp_bad.status_code == 400
        assert "Validation Error" in resp_bad.get_data(as_text=True)

    def test_custom_sql_report_csv_headers_and_errors(self, client):
        """Verifies custom SQL CSV export handles headers and errors."""
        # Valid custom SQL export
        resp = client.post(
            "/sql-reports/export-custom",
            data={"sql": "SELECT Roll_No, First_Name FROM STUDENT LIMIT 5;"},
        )
        assert resp.status_code == 200
        assert resp.headers.get("X-Export-Status") in ("complete", "limited")
        assert "X-Export-Count" in resp.headers

        # Empty SQL via AJAX: returns 400
        resp_empty = client.post(
            "/sql-reports/export-custom",
            data={"sql": ""},
            headers={"X-Requested-With": "XMLHttpRequest"},
        )
        assert resp_empty.status_code == 400
        assert "cannot be empty" in resp_empty.get_data(as_text=True)


class TestExportFrontendIntegrations:
    """Verifies that templates render export links with proper classes, query params, and alerts."""

    def test_base_template_contains_export_alert_container(self, client):
        """Verifies base.html contains #exportAlertContainer for dismissal banners."""
        resp = client.get("/students")
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert 'id="exportAlertContainer"' in html

    def test_students_index_export_button_attributes(self, client):
        """Verifies students index export link has .export-download-btn, data-export-btn, and active filters."""
        resp = client.get("/students?branch=Computer+Science&batch_year=2024")
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert "/students/export-csv?" in html
        assert "export-download-btn" in html
        assert "data-export-btn" in html
        assert "branch=CSE" in html
        assert "batch_year=2024" in html

    def test_placements_index_export_button_attributes(self, client):
        """Verifies placements index export link has .export-download-btn, data-export-btn, and filters."""
        resp = client.get("/placements?branch=Information+Technology&placement_year=2024")
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert "/placements/export-csv?" in html
        assert "export-download-btn" in html
        assert "data-export-btn" in html
        assert "branch=IT" in html
        assert "placement_year=2024" in html

    def test_internships_index_export_button_attributes(self, client):
        """Verifies internships index export link has .export-download-btn and data-export-btn."""
        resp = client.get("/internships?status=Approved")
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert "/internships/export-csv?" in html
        assert "export-download-btn" in html
        assert "data-export-btn" in html
        assert "status=Approved" in html

    def test_reports_index_export_buttons(self, client):
        """Verifies reports page contains BOTH CSV and PDF export buttons with current query params."""
        resp = client.get("/reports?branch=Computer+Science")
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert "/reports/export?" in html
        assert "/reports/export-pdf?" in html
        assert "branch=Computer+Science" in html
        assert "Export to CSV" in html
        assert "Export to PDF" in html

    def test_sql_reports_download_button(self, client):
        """Verifies SQL reports page includes #btnDownloadSavedCsv with export-download-btn."""
        resp = client.get("/sql-reports")
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert 'id="btnDownloadSavedCsv"' in html
        assert "export-download-btn" in html


class TestExportStaticJavaScriptLogic:
    """Verifies that static/js/main.js implements the complete Fetch and Blob export flow."""

    def test_main_js_defines_required_export_functions(self):
        """Verifies main.js exports showExportAlert, handleExportDownload, and initExportDownloadInterceptors."""
        with open("static/js/main.js", "r", encoding="utf-8") as fp:
            js = fp.read()

        assert "window.showExportAlert" in js
        assert "window.handleExportDownload" in js
        assert "window.initExportDownloadInterceptors" in js

    def test_main_js_inspects_truncation_headers(self):
        """Verifies main.js reads X-Export-Limited and X-Export-Warning."""
        with open("static/js/main.js", "r", encoding="utf-8") as fp:
            js = fp.read()

        assert "X-Export-Limited" in js
        assert "X-Export-Warning" in js
        assert "X-Export-Status" in js
        assert "X-Export-Count" in js

    def test_main_js_blob_and_object_url_handling(self):
        """Verifies main.js generates Blob and calls URL.createObjectURL / URL.revokeObjectURL."""
        with open("static/js/main.js", "r", encoding="utf-8") as fp:
            js = fp.read()

        assert "await response.blob()" in js
        assert "window.URL.createObjectURL(blob)" in js
        assert "window.URL.revokeObjectURL" in js
        assert "data-download-bypass" in js

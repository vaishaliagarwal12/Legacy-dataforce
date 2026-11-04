"""Legacy DataForce - Error Handling and Fault Tolerance Tests.

Verifies that HTTP 400, 404, 405, 500, DatabaseError, and ServiceError exceptions
are safely handled and return sanitized JSON responses without exposing internal server details.
"""

import pytest
from db.connection import DatabaseError
from services.exceptions import ValidationError, NotFoundError, ConflictError


class TestErrorHandling:
    """Verifies standard and custom error boundaries across the application."""

    def test_404_not_found_handling(self, client):
        """Verifies accessing a non-existent route returns 404 with standard JSON."""
        res = client.get("/api/non-existent-route-99999")
        assert res.status_code == 404
        data = res.get_json()
        assert data["status"] == "error"
        assert "not found" in data["message"].lower()

    def test_405_method_not_allowed_handling(self, client):
        """Verifies invoking an unsupported HTTP method on a route returns 405."""
        res = client.delete("/health")
        assert res.status_code == 405
        data = res.get_json()
        assert data["status"] == "fail"
        assert "method not allowed" in data["message"].lower()

    def test_service_error_translation_validation_error(self, client):
        """Verifies ValidationError translates to HTTP 400."""
        # POST to /api/students with invalid CGPA
        res = client.post(
            "/api/students",
            json={
                "Roll_No": "ERR_TEST_1",
                "First_Name": "Err",
                "Last_Name": "Test",
                "Email": "err@univ.edu",
                "Branch": "CSE",
                "Batch_Year": 2024,
                "CGPA": 15.0,  # Invalid
            },
        )
        assert res.status_code == 400
        data = res.get_json()
        assert data["status"] == "fail"
        assert "CGPA" in data["message"]

    def test_service_error_translation_not_found(self, client):
        """Verifies NotFoundError translates to HTTP 404."""
        res = client.get("/api/students/9999999")
        assert res.status_code == 404
        data = res.get_json()
        assert data["status"] == "fail"
        assert "not found" in data["message"].lower()

    def test_database_error_sanitization(self):
        """Verifies DatabaseError produces an HTTP 500 without leaking queries or connection details."""
        from app import create_app

        test_app = create_app("testing")
        test_client = test_app.test_client()

        @test_app.route("/_test_db_error")
        def trigger_db_error():
            raise DatabaseError(
                "SELECT * FROM secret_user WHERE password='leak'; Connection to 10.0.0.1 failed"
            )

        res = test_client.get("/_test_db_error")
        assert res.status_code == 500
        text = res.get_data(as_text=True)

        # Confirm sensitive strings are completely concealed
        assert "secret_user" not in text
        assert "password='leak'" not in text
        assert "10.0.0.1" not in text
        data = res.get_json()
        assert data["status"] == "error"
        assert "database error occurred" in data["message"].lower()

    def test_browser_404_html_rendering(self, client):
        """Verifies accessing a non-existent route via browser returns 404 HTML template."""
        res = client.get(
            "/non-existent-web-page", headers={"Accept": "text/html,application/xhtml+xml"}
        )
        assert res.status_code == 404
        text = res.get_data(as_text=True)
        assert "404 - Page Not Found" in text
        assert "Return to Dashboard" in text

    def test_browser_500_html_rendering(self):
        """Verifies database errors on browser visits render friendly 500 HTML template."""
        from app import create_app

        test_app = create_app("testing")
        test_client = test_app.test_client()

        @test_app.route("/_test_browser_db_error")
        def trigger_browser_db_error():
            raise DatabaseError("Query execution failed")

        res = test_client.get(
            "/_test_browser_db_error",
            headers={"Accept": "text/html,application/xhtml+xml"},
        )
        assert res.status_code == 500
        text = res.get_data(as_text=True)
        assert "500 - Database Connection Error" in text
        assert "Retry Request" in text

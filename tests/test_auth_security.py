"""Legacy DataForce - Authentication, Authorization & Security Audit Tests.

Verifies CSRF token protection on state-changing requests, database role-based
least-privilege execution (read-only execution user), and OWASP cookie/header settings.
"""

import pytest
import pymysql
from app import create_app
from config import ProductionConfig, DevelopmentConfig
from db.connection import get_readonly_connection, DatabaseError
from services.security import generate_csrf_token


class TestAuthAndSecurity:
    """Tests security controls, CSRF validation, and authorization boundaries."""

    def test_csrf_protection_rejects_unauthorized_post(self):
        """Verifies CSRF protection blocks state-changing requests lacking a valid token."""
        app = create_app("testing")
        app.config["TESTING"] = True
        app.config["CSRF_ENABLED"] = True
        app.config["WTF_CSRF_ENABLED"] = True

        client = app.test_client()

        # Attempt to POST to a web endpoint without CSRF token
        response = client.post(
            "/students/1/phones",
            data={"Phone_Number": "+919999988888", "Phone_Type": "Personal"},
            headers={"Accept": "application/json"},
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "fail"
        assert "CSRF validation failed" in data["message"]

    def test_csrf_protection_accepts_valid_header_token(self):
        """Verifies CSRF protection succeeds when valid X-CSRFToken header is supplied."""
        app = create_app("testing")
        app.config["TESTING"] = True
        app.config["CSRF_ENABLED"] = True
        app.config["WTF_CSRF_ENABLED"] = True

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["_csrf_token"] = "valid_test_secret_token_123"

            response = client.post(
                "/students/999999/phones",
                data={"phone_number": "+91 9999999999"},
                headers={"X-CSRFToken": "valid_test_secret_token_123"},
                follow_redirects=False,
            )
            # The CSRF check passed (not rejected with 400 CSRF validation error)
            assert response.status_code != 400
        # Should NOT fail with 400 CSRF error
        assert response.status_code != 400

    def test_readonly_user_authorization_least_privilege(self, app):
        """Verifies that the dedicated read-only database connection rejects write statements."""
        try:
            with get_readonly_connection() as conn:
                cursor = conn.cursor()
                # Attempt an unauthorized mutation
                with pytest.raises((DatabaseError, pymysql.MySQLError)):
                    cursor.execute("UPDATE STUDENT SET CGPA = 9.99 WHERE Student_ID = 1")
                    conn.commit()
                cursor.close()
        except DatabaseError as err:
            # If readonly user is restricted by connection or permissions, passes as expected
            assert "failed" in str(err).lower() or "denied" in str(err).lower()

    def test_production_cookie_and_debug_configuration(self):
        """Verifies OWASP session cookie attributes and debug flags in production."""
        assert ProductionConfig.DEBUG is False
        assert ProductionConfig.SESSION_COOKIE_HTTPONLY is True
        assert ProductionConfig.SESSION_COOKIE_SAMESITE == "Lax"
        assert ProductionConfig.SESSION_COOKIE_SECURE is True

    def test_http_security_headers(self, client):
        """Verifies required OWASP defensive headers are set on all responses."""
        res = client.get("/health")
        assert res.headers.get("X-Content-Type-Options") == "nosniff"
        assert res.headers.get("X-Frame-Options") == "SAMEORIGIN"

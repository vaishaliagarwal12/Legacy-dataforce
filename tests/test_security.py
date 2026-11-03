import unittest
from flask import session
from app import create_app
from config import ProductionConfig, DevelopmentConfig, TestingConfig
from db import DatabaseError
from services.security import (
    generate_csrf_token,
    verify_csrf_token,
    validate_safe_url,
)
from services import ValidationError, create_student, update_company
from routes.main import _safe_error_message


class SecurityAuditTestCase(unittest.TestCase):
    """Automated security verification test suite."""

    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()

    def test_http_security_headers(self):
        """Verify that standard OWASP security headers are present on HTTP responses."""
        response = self.client.get("/")
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(response.headers.get("X-Frame-Options"), "SAMEORIGIN")
        self.assertEqual(response.headers.get("X-XSS-Protection"), "1; mode=block")
        self.assertEqual(response.headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")

    def test_production_cookie_and_debug_configuration(self):
        """Verify that ProductionConfig enforces secure cookie policies and disables debug mode."""
        self.assertFalse(ProductionConfig.DEBUG)
        self.assertTrue(ProductionConfig.SESSION_COOKIE_HTTPONLY)
        self.assertTrue(ProductionConfig.SESSION_COOKIE_SECURE)
        self.assertEqual(ProductionConfig.SESSION_COOKIE_SAMESITE, "Lax")

    def test_safe_url_validation(self):
        """Verify that URL scheme validator blocks javascript:, data:, and insecure protocols."""
        # Valid URLs should not raise ValidationError
        try:
            validate_safe_url("https://github.com/student/resume.pdf")
            validate_safe_url("http://example.com")
            validate_safe_url("")
            validate_safe_url(None)
        except ValidationError:
            self.fail("validate_safe_url raised ValidationError unexpectedly on valid URL")

        # Malicious / Insecure URI schemes should raise ValidationError
        for bad_url in [
            "javascript:alert(document.cookie)",
            "data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==",
            "vbscript:MsgBox(1)",
            "file:///etc/passwd",
        ]:
            with self.subTest(bad_url=bad_url):
                with self.assertRaises(ValidationError):
                    validate_safe_url(bad_url)

    def test_student_service_rejects_unsafe_resume_url(self):
        """Verify student_service rejects stored XSS in Resume_Link."""
        payload = {
            "Roll_No": "SEC9999",
            "First_Name": "Security",
            "Last_Name": "Tester",
            "Email": "sectest@example.edu",
            "Branch": "CSE",
            "Batch_Year": 2026,
            "CGPA": 9.0,
            "Resume_Link": "javascript:alert('XSS')",
        }
        with self.assertRaises(ValidationError) as ctx:
            create_student(payload)
        self.assertIn("Only secure HTTP/HTTPS URLs are allowed", str(ctx.exception))

    def test_company_service_rejects_unsafe_website_url(self):
        """Verify company_service rejects stored XSS in Website."""
        with self.assertRaises(ValidationError) as ctx:
            update_company(1, {
                "Company_Name": "Test Org",
                "Company_Type": "Product",
                "Website": "javascript:alert(1)",
            })
        self.assertIn("Only secure HTTP/HTTPS URLs are allowed", str(ctx.exception))

    def test_csrf_protection_rejects_unauthorized_post(self):
        """Verify that state-changing requests without CSRF token are blocked when CSRF is enabled."""
        csrf_app = create_app("testing")
        csrf_app.config["CSRF_ENABLED"] = True
        csrf_app.config["WTF_CSRF_ENABLED"] = True
        csrf_client = csrf_app.test_client()

        # Attempt state-changing POST without CSRF token
        response = csrf_client.post(
            "/students/1/phones",
            data={"phone_number": "+91 9999999999"},
            headers={"Accept": "application/json"},
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data.get("status"), "fail")
        self.assertIn("CSRF validation failed", data.get("message", ""))

    def test_csrf_protection_accepts_valid_header_token(self):
        """Verify that state-changing requests with a valid CSRF token in headers are allowed."""
        csrf_app = create_app("testing")
        csrf_app.config["CSRF_ENABLED"] = True
        csrf_app.config["WTF_CSRF_ENABLED"] = True

        with csrf_app.test_client() as client:
            with client.session_transaction() as sess:
                sess["_csrf_token"] = "valid_test_secret_token_123"

            # Pass token via X-CSRFToken header
            response = client.post(
                "/students/999999/phones",
                data={"phone_number": "+91 9999999999"},
                headers={"X-CSRFToken": "valid_test_secret_token_123"},
                follow_redirects=False,
            )
            # The CSRF check passed (it may redirect or return not found, but NOT 400 CSRF failed)
            self.assertNotEqual(response.status_code, 400)

    def test_database_error_handler_sanitizes_leakage(self):
        """Verify that DatabaseError handler returns generic safe message and 500 status."""
        test_app = create_app("testing")
        test_client = test_app.test_client()

        # Register a temporary test route that triggers a simulated DatabaseError
        @test_app.route("/_test_db_error")
        def trigger_db_error():
            raise DatabaseError("SELECT * FROM secret_table WHERE password='leak'; Connection to 10.0.0.1 failed")

        response = test_client.get("/_test_db_error")
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertEqual(data.get("status"), "error")
        # Ensure raw query, credentials, or host details are NOT in the response
        self.assertNotIn("secret_table", data.get("message", ""))
        self.assertNotIn("password", data.get("message", ""))
        self.assertNotIn("10.0.0.1", data.get("message", ""))
        self.assertEqual(data.get("message"), "A database error occurred. Internal details have been logged securely.")

    def test_safe_error_message_helper_conceals_db_syntax(self):
        """Verify _safe_error_message conceals raw SQL syntax and database exception details."""
        raw_error = DatabaseError("SYNTAX ERROR in SQL: SELECT `Secret_Column` FROM `db_admin`")
        safe_msg = _safe_error_message(raw_error)
        self.assertEqual(safe_msg, "A database error occurred.")
        self.assertNotIn("Secret_Column", safe_msg)
        self.assertNotIn("SELECT", safe_msg)


if __name__ == "__main__":
    unittest.main()

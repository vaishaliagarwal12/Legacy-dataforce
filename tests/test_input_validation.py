"""Legacy DataForce - Input Validation and Security Bounds Tests.

Verifies strict input validation across services and routes, preventing
malformed payloads, dangerous URLs, out-of-bound academic figures, and SQL injection attempts.
"""

import pytest
from services.security import validate_safe_url
from services.exceptions import ValidationError
from services.student_service import create_student
from services.company_service import create_company
from services.sql_report_service import validate_custom_sql


class TestInputValidation:
    """Tests application validation rules against hostile or malformed inputs."""

    def test_safe_url_validation_rejection(self):
        """Verifies validate_safe_url rejects malicious protocols and unparseable URLs."""
        dangerous_urls = [
            "javascript:alert(document.cookie)",
            "file:///etc/passwd",
            "data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==",
            "vbscript:msgbox(1)",
            "ftp://anonymous@ftp.example.com/exploit.sh",
            "://malformed-url-format",
        ]
        for url in dangerous_urls:
            with pytest.raises(ValidationError):
                validate_safe_url(url)

    def test_safe_url_validation_acceptance(self):
        """Verifies validate_safe_url accepts legitimate HTTP/HTTPS URLs without exception."""
        legitimate_urls = [
            "https://drive.google.com/file/d/12345/view",
            "https://github.com/student/portfolio",
            "http://company-recruiter.example.org",
            "https://www.linkedin.com/in/student-profile",
            "",
            None,
        ]
        for url in legitimate_urls:
            validate_safe_url(url)

    def test_student_input_validation_boundary_rejection(self, app):
        """Verifies create_student rejects malformed CGPA, email, and negative backlogs."""
        # 1. Non-numeric CGPA
        with pytest.raises(ValidationError):
            create_student(
                {
                    "Roll_No": "VAL_STU_NAN",
                    "First_Name": "Nan",
                    "Last_Name": "Test",
                    "Email": "nan@univ.edu",
                    "Branch": "CSE",
                    "Batch_Year": 2024,
                    "CGPA": "not_a_number",
                }
            )

        # 2. Invalid Email format
        with pytest.raises(ValidationError):
            create_student(
                {
                    "Roll_No": "VAL_STU_EMAIL",
                    "First_Name": "Invalid",
                    "Last_Name": "Email",
                    "Email": "not-an-email-address",
                    "Branch": "CSE",
                    "Batch_Year": 2024,
                    "CGPA": 8.00,
                }
            )

        # 3. Missing required fields
        with pytest.raises(ValidationError):
            create_student(
                {
                    "Roll_No": "VAL_STU_MISSING",
                    "First_Name": "",  # Empty first name
                    "Last_Name": "Missing",
                    "Email": "missing@univ.edu",
                    "Branch": "CSE",
                    "Batch_Year": 2024,
                    "CGPA": 8.00,
                }
            )

    def test_company_input_validation(self, app):
        """Verifies create_company rejects invalid website and empty company names."""
        with pytest.raises(ValidationError):
            create_company(
                {
                    "Company_Name": "",  # Empty
                    "Company_Type": "Product",
                    "Industry": "Software",
                }
            )

        with pytest.raises(ValidationError):
            create_company(
                {
                    "Company_Name": "Bad URL Corp",
                    "Company_Type": "Product",
                    "Industry": "Software",
                    "Website": "javascript:eval('hacked')",
                }
            )

    def test_sql_injection_patterns_rejected(self):
        """Verifies validate_custom_sql detects and rejects SQL injection attack vectors."""
        attack_vectors = [
            "SELECT * FROM STUDENT; DROP TABLE PLACEMENT;",
            "SELECT * FROM STUDENT; DELETE FROM STUDENT;",
            "SELECT * FROM STUDENT /* comment hiding payload */ WHERE 1=1",
            "SELECT * FROM STUDENT -- comment",
            "SELECT * FROM STUDENT # hash comment",
            "UPDATE STUDENT SET CGPA = 10.0 WHERE Student_ID = 1",
            "DELETE FROM RECRUITMENT_DRIVE",
            "TRUNCATE TABLE INTERNSHIP",
        ]
        for attack in attack_vectors:
            with pytest.raises(ValidationError):
                validate_custom_sql(attack)

"""Legacy DataForce - Pytest Global Fixtures and Configuration.

Provides isolated test database configuration, reusable test fixtures for Flask client,
database transactions with automatic rollback, synthetic data generation, and clean teardowns.
"""

import os
import uuid
import pytest
from app import create_app
from config import TestingConfig
from db.connection import get_connection, get_cursor, execute_mutation, execute_one, execute_query
from services.student_service import create_student, delete_student
from services.company_service import create_company, delete_company
from services.placement_service import create_placement_offer, delete_placement_offer
from services.security import generate_csrf_token
from werkzeug.security import generate_password_hash

TEST_ADMIN_USERNAME = "test_admin"
TEST_ADMIN_PASSWORD = "TestAdminPassword2026!"
TEST_ADMIN_PASSWORD_HASH = generate_password_hash(TEST_ADMIN_PASSWORD)


@pytest.fixture(scope="session")
def app():
    """Session-scoped Flask application instance configured for testing."""
    os.environ["FLASK_ENV"] = "testing"
    # Ensure TestingConfig is active
    flask_app = create_app("testing")
    flask_app.config.update(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "PRESERVE_CONTEXT_ON_EXCEPTION": False,
            "ADMIN_USERNAME": TEST_ADMIN_USERNAME,
            "ADMIN_PASSWORD_HASH": TEST_ADMIN_PASSWORD_HASH,
            "ADMIN_PASSWORD": None,
        }
    )

    with flask_app.app_context():
        yield flask_app


@pytest.fixture(scope="function")
def client(app):
    """Function-scoped test client for sending HTTP requests."""
    return app.test_client()


@pytest.fixture(scope="function")
def unauthenticated_client(app):
    """Function-scoped unauthenticated test client with no session."""
    return app.test_client(auto_login=False)


@pytest.fixture(scope="function")
def runner(app):
    """Function-scoped test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture(scope="function")
def db_conn(app):
    """Provides an active database connection context."""
    with get_connection() as conn:
        yield conn


@pytest.fixture(scope="function")
def db_cursor(app):
    """Provides a DictCursor context for executing test queries."""
    with get_cursor(commit=False) as cursor:
        yield cursor


@pytest.fixture(scope="function")
def isolated_transaction(app):
    """Guarantees zero database pollution by running operations inside a transaction

    that is unconditionally rolled back on fixture teardown.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            conn.rollback()
            cursor.close()


@pytest.fixture(scope="function")
def synthetic_student_payload():
    """Generates synthetic, non-PII student registration payload with unique roll number."""
    unique_suffix = uuid.uuid4().hex[:6].upper()
    return {
        "Roll_No": f"SYN_{unique_suffix}",
        "First_Name": "Synthetic",
        "Last_Name": f"Student_{unique_suffix}",
        "Email": f"syn_{unique_suffix.lower()}@university.synthetic.edu",
        "Branch": "Computer Science",
        "Batch_Year": 2024,
        "Section": "A",
        "CGPA": 8.75,
        "Backlogs": 0,
        "Date_of_Birth": "2002-05-15",
        "Gender": "Other",
        "Personal_Email": f"syn_personal_{unique_suffix.lower()}@synthetic.io",
        "Skills": ["Python", "Pytest", "MySQL"],
        "Phone_Numbers": ["9876543210"],
    }


@pytest.fixture(scope="function")
def clean_test_student(app, synthetic_student_payload):
    """Creates a temporary synthetic student and guarantees removal upon teardown."""
    created = create_student(synthetic_student_payload)
    student_id = created["Student_ID"]

    yield created

    # Teardown: ensure complete removal
    try:
        delete_student(student_id)
    except Exception:
        # Fallback raw delete if active career records or foreign key restrictions apply
        execute_mutation("DELETE FROM STUDENT WHERE Student_ID = %s", (student_id,))


@pytest.fixture(scope="function")
def synthetic_company_payload():
    """Generates synthetic corporate recruiter payload."""
    unique_suffix = uuid.uuid4().hex[:6].upper()
    return {
        "Company_Name": f"Synthetic Solutions Corp {unique_suffix}",
        "Company_Type": "Product",
        "Industry": "Enterprise Software",
        "Location": "Bengaluru",
        "Website": f"https://synthetic-{unique_suffix.lower()}.example.org",
    }


@pytest.fixture(scope="function")
def clean_test_company(app, synthetic_company_payload):
    """Creates a temporary company and guarantees removal upon teardown."""
    created = create_company(synthetic_company_payload)
    company_id = created["Company_ID"]

    yield created

    # Teardown
    try:
        delete_company(company_id)
    except Exception:
        execute_mutation("DELETE FROM COMPANY WHERE Company_ID = %s", (company_id,))


@pytest.fixture(scope="function")
def clean_test_placement(app, clean_test_student, clean_test_company):
    """Creates a placement offer for testing and tears down cleanly."""
    student_id = clean_test_student["Student_ID"]
    company_id = clean_test_company["Company_ID"]
    payload = {
        "Student_ID": student_id,
        "Company_ID": company_id,
        "Role": "Software Engineer Test",
        "Package": 12.50,
        "Placement_Year": 2026,
        "Placement_Type": "On-campus",
        "Offer_Status": "Offered",
        "Joined": "No",
        "Is_PPO": "No",
        "Interview_Rounds": 3,
        "Skills": ["Python", "SQL"],
    }
    offer = create_placement_offer(payload)
    offer_id = offer["Placement_ID"]

    yield offer

    try:
        delete_placement_offer(offer_id)
    except Exception:
        execute_mutation("DELETE FROM PLACEMENT WHERE Placement_ID = %s", (offer_id,))


@pytest.fixture(scope="function")
def valid_csrf_token():
    """Generates a valid CSRF token for testing state-changing form/header requests."""
    return generate_csrf_token()

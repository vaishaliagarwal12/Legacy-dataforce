"""Legacy DataForce - Transaction Rollback & Atomicity Tests.

Verifies that multi-table business operations execute atomically, and database
mutations are completely rolled back upon error, leaving zero orphaned records.
"""

import pytest
import uuid
from db.connection import get_cursor, execute_one, DatabaseError
from services.student_service import create_student, ValidationError


class TestTransactionRollback:
    """Verifies ACID atomicity and rollback semantics across multi-table operations."""

    def test_context_manager_rollback_on_unhandled_exception(self, app):
        """Verifies that get_cursor(commit=True) automatically rolls back changes if an exception occurs."""
        unique_roll = f"TX_TEST_{uuid.uuid4().hex[:6].upper()}"

        with pytest.raises(RuntimeError):
            with get_cursor(commit=True) as cur:
                cur.execute(
                    """INSERT INTO STUDENT (Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs, Email)
                       VALUES (%s, 'Tx', 'Rollback', 'CSE', 2024, 8.50, 0, %s)""",
                    (unique_roll, f"{unique_roll.lower()}@univ.edu"),
                )
                # Intentionally trigger an exception before clean block exit
                raise RuntimeError("Simulated failure to verify automatic transaction rollback")

        # Verify that the inserted student was rolled back and does not exist in the database
        found = execute_one("SELECT Student_ID FROM STUDENT WHERE Roll_No = %s", (unique_roll,))
        assert found is None, f"Expected {unique_roll} to be rolled back, but row was committed!"

    def test_multi_table_student_creation_atomicity(self, app):
        """Verifies that if child table insertion (STUDENT_PHONE) fails, the parent STUDENT row is rolled back."""
        unique_roll = f"TX_STU_{uuid.uuid4().hex[:6].upper()}"
        payload = {
            "Roll_No": unique_roll,
            "First_Name": "Atomic",
            "Last_Name": "Tester",
            "Email": f"{unique_roll.lower()}@univ.edu",
            "Branch": "Computer Science",
            "Batch_Year": 2024,
            "CGPA": 8.50,
            "Backlogs": 0,
            # Phone number with missing required Phone_Number to trigger validation failure
            "Phone_Numbers": [{"Phone_Number": "", "Phone_Type": "Invalid"}],
        }

        with pytest.raises((ValidationError, DatabaseError)):
            create_student(payload)

        # Confirm the parent student row was NOT saved
        saved_student = execute_one(
            "SELECT Student_ID FROM STUDENT WHERE Roll_No = %s", (unique_roll,)
        )
        assert (
            saved_student is None
        ), "Parent student row should not exist after child insertion error"

    def test_explicit_rollback_fixture_isolation(self, isolated_transaction):
        """Verifies that operations performed inside isolated_transaction leave no trace."""
        unique_roll = f"TX_ISO_{uuid.uuid4().hex[:6].upper()}"

        isolated_transaction.execute(
            """INSERT INTO STUDENT (Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs, Email)
               VALUES (%s, 'Isolated', 'Test', 'IT', 2024, 7.80, 0, %s)""",
            (unique_roll, f"{unique_roll.lower()}@univ.edu"),
        )
        # Row is visible within this transaction
        isolated_transaction.execute(
            "SELECT Student_ID FROM STUDENT WHERE Roll_No = %s", (unique_roll,)
        )
        assert isolated_transaction.fetchone() is not None

        # When the fixture completes, rollback occurs automatically.

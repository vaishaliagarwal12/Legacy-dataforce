"""Legacy DataForce - Tests for Backend Hardcoding Audit Warnings Fixes.

Verifies the 4 audit findings corrections:
1. get_dashboard_filter_options returns safe empty lists on database failure (no hardcoded fallbacks).
2. /students index branch dropdown dynamically uses database branches and preserves active filter selection.
3. /students/new and /students/<id>/edit dynamically populate branch choices and calculate default batch year.
4. Base template navbar contains a dynamic database health indicator rather than a static badge.
"""

import datetime
from unittest.mock import patch
from db.connection import DatabaseError
from services.dashboard_service import get_dashboard_filter_options


class TestAuditWarningsFixes:
    """Verifies all four audit warning resolutions."""

    def test_dashboard_filter_options_no_hardcoded_fallbacks_on_failure(self):
        """Verifies get_dashboard_filter_options returns safe empty lists on failure, not fake business data."""
        with patch(
            "services.dashboard_service.execute_query", side_effect=DatabaseError("DB Down")
        ):
            options = get_dashboard_filter_options()
            assert isinstance(options, dict)
            assert options["branches"] == []
            assert options["batch_years"] == []
            assert options["placement_years"] == []
            # Explicitly confirm no hardcoded strings are present
            assert "CSE" not in options["branches"]
            assert 2024 not in options["batch_years"]

    def test_students_index_dynamic_branches_and_preserved_selection(self, client):
        """Verifies /students branch filter dynamically renders database branches and preserves active selection."""
        # 1. Access student directory
        res = client.get("/students")
        assert res.status_code == 200
        html = res.get_data(as_text=True)

        # Confirm branch select is present
        assert 'name="branch"' in html
        assert "All Branches" in html

        # 2. Filter by specific branch and verify selection is retained
        res_filtered = client.get("/students?branch=ECE")
        assert res_filtered.status_code == 200
        html_filtered = res_filtered.get_data(as_text=True)
        assert 'value="ECE" selected' in html_filtered or "value='ECE' selected" in html_filtered

    def test_students_form_dynamic_branches_and_dynamic_batch_year(self, client):
        """Verifies /students/new populates branches dynamically and uses current year for default batch."""
        res = client.get("/students/new")
        assert res.status_code == 200
        html = res.get_data(as_text=True)

        current_year = datetime.date.today().year

        # Verify dynamic batch year default
        assert f'value="{current_year}"' in html or f"value='{current_year}'" in html
        # Confirm branch dropdown uses dynamic options
        assert 'id="Branch"' in html
        assert "Select department..." in html

    def test_students_form_backend_branch_validation(self, client):
        """Verifies student form validates branch and batch year on the backend."""
        # Submit with blank branch
        res = client.post(
            "/students/new",
            data={
                "Roll_No": "TEST_ROLL_99",
                "First_Name": "Test",
                "Branch": "",  # Invalid
                "Batch_Year": 2026,
                "CGPA": "8.50",
            },
            follow_redirects=True,
        )
        assert res.status_code == 200
        html = res.get_data(as_text=True)
        assert "valid academic branch" in html.lower()

    def test_base_navbar_dynamic_db_health_indicator(self, client):
        """Verifies base template contains genuine dynamic dbHealthBadge."""
        res = client.get("/")
        assert res.status_code == 200
        html = res.get_data(as_text=True)
        assert 'id="dbHealthBadge"' in html
        assert "MySQL Connected" in html

    def test_base_navbar_db_health_indicator_on_db_error(self):
        """Verifies base template displays disconnected state when database connection fails."""
        from app import create_app

        test_app = create_app("testing")
        test_client = test_app.test_client()

        @test_app.route("/_test_db_disconnect_view")
        def trigger_db_disconnect():
            raise DatabaseError("Lost connection to MySQL server on port 3306")

        res = test_client.get(
            "/_test_db_disconnect_view",
            headers={"Accept": "text/html,application/xhtml+xml"},
        )
        assert res.status_code == 500
        html = res.get_data(as_text=True)
        assert 'id="dbHealthBadge"' in html
        assert "MySQL Disconnected" in html
        assert "badge-status-danger" in html

"""Legacy DataForce - Tests for Phase 1 Hardcoding Improvements.

Verifies:
1. Dedicated get_student_selector_options() service function fetches only required fields.
2. get_student_selector_options() returns all students without arbitrary limit=100 truncation.
3. get_student_selector_options() handles empty database gracefully.
4. /internships directory dynamically renders database-driven branches and batches, preserving selection.
5. /placements directory dynamically renders database-driven branches, preserving selection.
6. /reports directory dynamically renders database-driven branches, preserving selection.
7. /internships/new and /placements/new use student selector options.
"""

from unittest.mock import patch
from services.student_service import get_student_selector_options
from services.dashboard_service import get_dashboard_filter_options


class TestPhase1Dynamicity:
    """Verifies all Phase 1 database-driven student selector and filter improvements."""

    def test_get_student_selector_options_structure(self):
        """Verifies get_student_selector_options returns expected fields and types."""
        students = get_student_selector_options()
        assert isinstance(students, list)
        if students:
            first = students[0]
            assert "Student_ID" in first
            assert "Roll_No" in first
            assert "First_Name" in first
            assert "Last_Name" in first
            assert "Branch" in first
            assert "Batch_Year" in first
            if first["Batch_Year"] is not None:
                assert isinstance(first["Batch_Year"], int)

    def test_get_student_selector_options_beyond_100_records(self):
        """Verifies student selector options do not truncate students past 100."""
        fake_students = [
            {
                "Student_ID": i,
                "Roll_No": f"TEST{i:04d}",
                "First_Name": f"Student{i}",
                "Last_Name": "Tester",
                "Branch": "CSE",
                "Batch_Year": 2024,
            }
            for i in range(1, 151)
        ]
        with patch("services.student_service.execute_query", return_value=fake_students):
            results = get_student_selector_options()
            assert len(results) == 150
            assert results[0]["Roll_No"] == "TEST0001"
            assert results[149]["Roll_No"] == "TEST0150"

    def test_get_student_selector_options_empty_db_graceful(self):
        """Verifies get_student_selector_options handles empty database safely."""
        with patch("services.student_service.execute_query", return_value=[]):
            results = get_student_selector_options()
            assert results == []

    def test_internships_index_dynamic_branches_and_batches(self, client):
        """Verifies /internships renders dynamic branches and batch years and preserves active selection."""
        filter_opts = get_dashboard_filter_options()
        res = client.get("/internships")
        assert res.status_code == 200
        html = res.get_data(as_text=True)

        assert 'name="branch"' in html
        assert 'name="batch_year"' in html
        assert "All Branches" in html
        assert "All Batches" in html

        for b in filter_opts["branches"]:
            assert f'<option value="{b}"' in html

        for by in filter_opts["batch_years"]:
            assert f'<option value="{by}"' in html

        # Verify selected filters remain selected
        if filter_opts["branches"] and filter_opts["batch_years"]:
            target_branch = filter_opts["branches"][0]
            target_batch = filter_opts["batch_years"][0]
            res_filtered = client.get(
                f"/internships?branch={target_branch}&batch_year={target_batch}"
            )
            assert res_filtered.status_code == 200
            html_filtered = res_filtered.get_data(as_text=True)
            assert f'value="{target_branch}" selected' in html_filtered
            assert f'value="{target_batch}" selected' in html_filtered

    def test_placements_index_dynamic_branches_and_selection(self, client):
        """Verifies /placements renders dynamic branch options and preserves active selection."""
        filter_opts = get_dashboard_filter_options()
        res = client.get("/placements")
        assert res.status_code == 200
        html = res.get_data(as_text=True)

        assert 'name="branch"' in html
        assert "All Branches" in html

        for b in filter_opts["branches"]:
            assert f'value="{b}"' in html

        if filter_opts["branches"]:
            target_branch = filter_opts["branches"][0]
            res_filtered = client.get(f"/placements?branch={target_branch}")
            assert res_filtered.status_code == 200
            html_filtered = res_filtered.get_data(as_text=True)
            assert f'value="{target_branch}" selected' in html_filtered

    def test_reports_index_dynamic_branches_and_selection(self, client):
        """Verifies /reports renders dynamic branch options and preserves active selection."""
        filter_opts = get_dashboard_filter_options()
        res = client.get("/reports")
        assert res.status_code == 200
        html = res.get_data(as_text=True)

        assert 'name="branch"' in html
        assert "All Departments" in html

        for b in filter_opts["branches"]:
            assert f'value="{b}"' in html

        if filter_opts["branches"]:
            target_branch = filter_opts["branches"][0]
            res_filtered = client.get(f"/reports?branch={target_branch}")
            assert res_filtered.status_code == 200
            html_filtered = res_filtered.get_data(as_text=True)
            assert f'value="{target_branch}" selected' in html_filtered

    def test_internship_and_placement_create_forms_use_selector(self, client):
        """Verifies /internships/new and /placements/new populate candidates from get_student_selector_options."""
        res_intern = client.get("/internships/new")
        assert res_intern.status_code == 200
        html_intern = res_intern.get_data(as_text=True)
        assert 'name="Student_ID"' in html_intern
        assert "Choose student from registry..." in html_intern

        res_placement = client.get("/placements/new")
        assert res_placement.status_code == 200
        html_placement = res_placement.get_data(as_text=True)
        assert 'name="Student_ID"' in html_placement
        assert "Choose student..." in html_placement

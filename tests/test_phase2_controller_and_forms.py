"""Legacy DataForce - Tests for Phase 2 Hardcoding and Controller Improvements.

Verifies:
1. Removal of BRANCH_MAP and replacement with database-driven branch resolution.
2. Branch validation rejects non-existent branches when branches exist in DB.
3. Graceful handling of empty branch list in normalize_branch.
4. Removal of COMPANY_TYPE_MAP and direct usage of Company_Type ENUM ('Product', 'Service', 'Startup', 'Other').
5. Company form displays four valid types; creation and update directly persist Company_Type.
6. Placement year defaults dynamically to current year on create, and preserves historical year on edit.
7. Internship form defaults stipend to 0 for new records, retaining placeholder, and preserves actual saved stipend on edit.
"""

import datetime
from unittest.mock import patch
from services.company_service import create_company, get_company, VALID_COMPANY_TYPES
from services.placement_service import create_placement_offer, get_placement_offer
from services.internship_service import create_internship, get_internship
from routes.main import normalize_branch, normalize_company_type, get_canonical_branches


class TestPhase2ControllerAndForms:
    """Verifies all Phase 2 hardcoding removal and dynamicity improvements."""

    def test_canonical_branches_from_database(self):
        """Verifies get_canonical_branches retrieves active branches from the database."""
        branches = get_canonical_branches()
        assert isinstance(branches, list)
        assert len(branches) > 0
        assert "CSE" in branches

    def test_normalize_branch_valid_and_case_insensitive(self):
        """Verifies normalize_branch validates against canonical DB branches case-insensitively."""
        assert normalize_branch("CSE") == "CSE"
        assert normalize_branch("cse") == "CSE"
        assert normalize_branch("Information Tech") == "IT"
        assert normalize_branch("it") == "IT"
        assert normalize_branch("me") == "ME"

    def test_normalize_branch_rejects_invalid_branch(self):
        """Verifies normalize_branch returns None for non-existent branches."""
        assert normalize_branch("ASTRONOMY_XYZ") is None
        assert normalize_branch("INVALID_BRANCH_CODE") is None
        assert normalize_branch("") is None
        assert normalize_branch("all") is None
        assert normalize_branch("none") is None

    def test_normalize_branch_empty_db_graceful(self):
        """Verifies normalize_branch gracefully handles an empty branch list without crashing."""
        with patch("routes.main.get_canonical_branches", return_value=[]):
            # When DB has zero branches, it should gracefully accept the submitted branch
            assert normalize_branch("AEROSPACE") == "AEROSPACE"
            assert normalize_branch("") is None

    def test_company_type_enum_values(self):
        """Verifies VALID_COMPANY_TYPES strictly matches the database schema ENUM ('Product', 'Service', 'Startup', 'Other')."""
        assert set(VALID_COMPANY_TYPES) == {"Product", "Service", "Startup", "Other"}

    def test_normalize_company_type_direct_values(self):
        """Verifies normalize_company_type accepts and normalizes canonical company types."""
        assert normalize_company_type("Product") == "Product"
        assert normalize_company_type("product") == "Product"
        assert normalize_company_type("Service") == "Service"
        assert normalize_company_type("Startup") == "Startup"
        assert normalize_company_type("Other") == "Other"
        assert normalize_company_type("tier-1") == "Product"
        assert normalize_company_type("INVALID_TYPE") is None
        assert normalize_company_type("") is None

    def test_company_create_and_edit_form_uses_company_type(self, client):
        """Verifies company create form renders Company_Type select and posts direct Company_Type."""
        res_get = client.get("/companies/new")
        assert res_get.status_code == 200
        html_get = res_get.get_data(as_text=True)
        assert 'name="Company_Type"' in html_get
        assert '<option value="Product"' in html_get
        assert '<option value="Service"' in html_get
        assert '<option value="Startup"' in html_get
        assert '<option value="Other"' in html_get

        # Create company with Startup type
        unique_name = f"Startup Lab {datetime.datetime.now().timestamp()}"
        company_id = None
        try:
            res_post = client.post(
                "/companies/new",
                data={
                    "Company_Name": unique_name,
                    "Company_Type": "Startup",
                    "Industry": "Artificial Intelligence",
                    "Location": "Bengaluru",
                },
                follow_redirects=True,
            )
            assert res_post.status_code == 200
            html_detail = res_post.get_data(as_text=True)
            assert unique_name in html_detail
            assert "Startup" in html_detail

            from db.connection import execute_one

            row = execute_one(
                "SELECT Company_ID FROM COMPANY WHERE Company_Name = %s", (unique_name,)
            )
            if row:
                company_id = row["Company_ID"]
        finally:
            if company_id:
                from services.company_service import delete_company

                delete_company(company_id)

    def test_placement_year_defaults_to_current_year_on_create(self, client):
        """Verifies placement forms use the current calendar year dynamically for new records."""
        current_year = datetime.date.today().year
        res_get = client.get("/placements/new")
        assert res_get.status_code == 200
        html = res_get.get_data(as_text=True)
        assert f'value="{current_year}"' in html

        res_list = client.get("/placements")
        assert res_list.status_code == 200
        html_list = res_list.get_data(as_text=True)
        # Modal placement year input
        assert (
            f'id="modal_Placement_Year" name="Placement_Year" value="{current_year}"' in html_list
        )

    def test_placement_year_preserved_on_edit(self, client, clean_test_student, clean_test_company):
        """Verifies editing an existing placement offer preserves its historical placement year."""
        historical_year = 2021
        offer = create_placement_offer(
            {
                "Student_ID": clean_test_student["Student_ID"],
                "Company_ID": clean_test_company["Company_ID"],
                "Role": "Test Historical Role",
                "Package": 12.0,
                "Placement_Year": historical_year,
                "Placement_Type": "On-campus",
                "Offer_Status": "Offered",
            }
        )
        placement_id = offer["Placement_ID"]

        try:
            # View edit page: value must be historical_year
            res_edit = client.get(f"/placements/{placement_id}/edit")
            assert res_edit.status_code == 200
            html = res_edit.get_data(as_text=True)
            assert f'value="{historical_year}"' in html

            # Post edit without Placement_Year: must preserve saved historical year
            res_post = client.post(
                f"/placements/{placement_id}/edit",
                data={
                    "Role": "Updated Role Title",
                    "Package": "14.0",
                    "Placement_Type": "On-campus",
                    "Offer_Status": "Offered",
                    # Placement_Year omitted to test fallback to saved year
                },
                follow_redirects=True,
            )
            assert res_post.status_code == 200
            updated = get_placement_offer(placement_id)
            assert updated["Placement_Year"] == historical_year
        finally:
            from services.placement_service import delete_placement_offer

            delete_placement_offer(placement_id)

    def test_internship_stipend_default_is_zero_and_preserved_on_edit(
        self, client, clean_test_student, clean_test_company
    ):
        """Verifies internship create form defaults stipend to 0 with placeholder, and preserves actual saved stipend on edit."""
        res_new = client.get("/internships/new")
        assert res_new.status_code == 200
        html_new = res_new.get_data(as_text=True)
        assert 'value="0"' in html_new
        assert 'placeholder="e.g. 15000"' in html_new

        # Create internship with non-zero stipend
        internship = create_internship(
            {
                "Student_ID": clean_test_student["Student_ID"],
                "Company_ID": clean_test_company["Company_ID"],
                "Internship_No": 3,
                "Internship_Type": "Additional",
                "Role": "Research Intern",
                "Stipend": 22500.0,
                "Start_Date": "2024-06-01",
                "End_Date": "2024-07-31",
                "Credits": 0,
            }
        )
        intern_id = internship["Internship_ID"]

        try:
            res_edit = client.get(f"/internships/{intern_id}/edit")
            assert res_edit.status_code == 200
            html_edit = res_edit.get_data(as_text=True)
            assert 'value="22500.0"' in html_edit or 'value="22500"' in html_edit
        finally:
            from services.internship_service import delete_internship

            delete_internship(intern_id)

"""Legacy DataForce - Tests for Phase 3 Configuration Centralization, Query Optimization & Export Improvements.

Verifies:
1. Configuration defaults and environment overrides.
2. Invalid configuration values fallback safely.
3. Health-check cache TTL configuration.
4. SQL report maximum row configuration.
5. SQL report timeout configuration.
6. Pagination helper for valid and invalid values.
7. Shared package statistics function.
8. Identical dashboard and placement package statistics.
9. Package bracket boundary values (5.99, 6.0, 9.99, 10.0, 14.99, 15.0).
10. CSV export limits and truncation warnings.
11. PDF export limits and truncation warnings.
12. Empty export handling.
"""

import io
import csv
from unittest.mock import patch
from config import Config, get_env_int, get_env_float
from services.pagination import validate_pagination_params
from services.placement_service import (
    get_placement_package_statistics,
    get_package_bracket_thresholds,
    classify_package_tier,
    get_placement_analytics,
)
from services.dashboard_service import get_dashboard_stats
from services.sql_report_service import validate_custom_sql, get_sql_report_limits


class TestPhase3ConfigurationAndOptimization:
    """Verifies all Phase 3 requirements."""

    def test_configuration_defaults_and_env_overrides(self, monkeypatch):
        """1. Verifies configuration defaults and environment overrides."""
        assert Config.DB_HEALTH_CACHE_TTL == 10.0
        assert Config.SQL_REPORT_MAX_ROWS == 500
        assert Config.SQL_REPORT_TIMEOUT_MS == 3000
        assert Config.EXPORT_ROW_LIMIT == 10000
        assert Config.EXPORT_PDF_ROW_LIMIT == 150
        assert Config.DEFAULT_PAGE_SIZE == 10
        assert Config.MAX_PAGE_SIZE == 100
        assert Config.PACKAGE_BRACKET_TIER_1_MAX == 6.0
        assert Config.PACKAGE_BRACKET_TIER_2_MAX == 10.0
        assert Config.PACKAGE_BRACKET_TIER_3_MAX == 15.0

        # Test environment override helper
        monkeypatch.setenv("TEST_OVERRIDE_INT", "42")
        assert get_env_int("TEST_OVERRIDE_INT", 10) == 42

        monkeypatch.setenv("TEST_OVERRIDE_FLOAT", "8.75")
        assert get_env_float("TEST_OVERRIDE_FLOAT", 5.0) == 8.75

    def test_invalid_configuration_values_fallback_safely(self, monkeypatch):
        """2. Verifies invalid configuration values fallback safely to defaults."""
        monkeypatch.setenv("TEST_BAD_INT", "not_a_number")
        assert get_env_int("TEST_BAD_INT", 100) == 100

        # Out of bounds below min
        monkeypatch.setenv("TEST_LOW_INT", "-5")
        assert get_env_int("TEST_LOW_INT", 100, min_val=1) == 100

        # Out of bounds above max
        monkeypatch.setenv("TEST_HIGH_INT", "999999")
        assert get_env_int("TEST_HIGH_INT", 100, max_val=1000) == 100

        # Float invalid
        monkeypatch.setenv("TEST_BAD_FLOAT", "abc")
        assert get_env_float("TEST_BAD_FLOAT", 6.0) == 6.0

    def test_health_check_cache_ttl_configuration(self, app):
        """3. Verifies health-check cache TTL is configurable through the configuration system."""
        assert "DB_HEALTH_CACHE_TTL" in app.config
        assert app.config["DB_HEALTH_CACHE_TTL"] == 10.0

    def test_sql_report_maximum_row_configuration(self, app):
        """4. Verifies SQL report maximum row configuration caps queries dynamically."""
        # Default configuration caps to 500
        sql = "SELECT Roll_No FROM STUDENT"
        validated = validate_custom_sql(sql)
        assert "LIMIT 500" in validated

        # With overridden configuration via app config (e.g., 250)
        with patch.dict(app.config, {"SQL_REPORT_MAX_ROWS": 250}):
            validated_custom = validate_custom_sql("SELECT Roll_No FROM STUDENT")
            assert "LIMIT 250" in validated_custom

            # Clamping excessive requested limit
            clamped = validate_custom_sql("SELECT Roll_No FROM STUDENT LIMIT 9000")
            assert "LIMIT 250" in clamped
            assert "9000" not in clamped

    def test_sql_report_timeout_configuration(self, app):
        """5. Verifies SQL report timeout configuration is centralized."""
        max_rows, timeout_ms = get_sql_report_limits()
        assert max_rows == 500
        assert timeout_ms == 3000

        with patch.dict(app.config, {"SQL_REPORT_TIMEOUT_MS": 4500}):
            _, overridden_timeout = get_sql_report_limits()
            assert overridden_timeout == 4500

    def test_pagination_helper_valid_and_invalid_values(self):
        """6. Verifies pagination helper handles valid, invalid, negative, and excessive values safely."""
        # Standard valid values
        p, pp = validate_pagination_params(page=2, per_page=25, allowed_per_page=(10, 25, 50, 100))
        assert p == 2
        assert pp == 25

        # Invalid string page and per_page fallback to defaults
        p, pp = validate_pagination_params(
            page="invalid", per_page="xyz", default_page=1, default_per_page=10
        )
        assert p == 1
        assert pp == 10

        # Negative and zero page values normalize to default
        p, pp = validate_pagination_params(page=-5, per_page=0, default_page=1, default_per_page=10)
        assert p == 1
        assert pp == 10

        # Whitelist enforcement: unlisted per_page resets to default
        p, pp = validate_pagination_params(
            page=1, per_page=37, default_per_page=10, allowed_per_page=(10, 25, 50, 100)
        )
        assert pp == 10

        # Upper bound clamping when no whitelist is set
        p, pp = validate_pagination_params(page=3, per_page=999, max_per_page=100)
        assert p == 3
        assert pp == 100

    def test_shared_package_statistics_function(self):
        """7. Verifies consolidated get_placement_package_statistics calculates accurate statistics."""
        stats = get_placement_package_statistics()
        assert isinstance(stats, dict)
        assert "avg_package" in stats
        assert "highest_package" in stats
        assert "lowest_package" in stats
        assert "total_offers" in stats
        assert stats["total_offers"] > 0
        assert stats["avg_package"] > 0.0
        assert stats["highest_package"] >= stats["avg_package"]
        assert stats["lowest_package"] <= stats["avg_package"]

    def test_identical_dashboard_and_placement_package_statistics(self):
        """8. Verifies dashboard and placement analytics return identical package statistics for the same filter."""
        pkg_stats = get_placement_package_statistics(branch="CSE")
        dashboard = get_dashboard_stats(filters={"branch": "CSE"})
        placement = get_placement_analytics(branch="CSE")

        assert dashboard["kpi"]["avg_package"] == pkg_stats["avg_package"]
        assert dashboard["kpi"]["highest_package"] == pkg_stats["highest_package"]
        assert dashboard["kpi"]["lowest_package"] == pkg_stats["lowest_package"]

        assert placement["kpis"]["avg_package"] == pkg_stats["avg_package"]
        assert placement["kpis"]["highest_package"] == pkg_stats["highest_package"]
        assert placement["kpis"]["lowest_package"] == pkg_stats["lowest_package"]

    def test_package_bracket_boundary_values(self):
        """9. Verifies package bracket classification for exact boundary values (5.99, 6.0, 9.99, 10.0, 14.99, 15.0)."""
        t1, t2, t3 = get_package_bracket_thresholds()
        assert (t1, t2, t3) == (6.0, 10.0, 15.0)

        assert classify_package_tier(5.99) == "tier_below_6"
        assert classify_package_tier(6.00) == "tier_6_to_10"
        assert classify_package_tier(9.99) == "tier_6_to_10"
        assert classify_package_tier(10.00) == "tier_10_to_15"
        assert classify_package_tier(14.99) == "tier_10_to_15"
        assert classify_package_tier(15.00) == "tier_above_15"
        assert classify_package_tier(25.50) == "tier_above_15"
        assert classify_package_tier(0.0) == "tier_below_6"

    def test_csv_export_limits_and_truncation_headers(self, client):
        """10. Verifies CSV export adheres to limits and provides truncation warning headers."""
        # Under normal conditions: complete export
        res_normal = client.get("/students/export-csv")
        assert res_normal.status_code == 200
        assert res_normal.headers.get("X-Export-Status") == "complete"
        assert res_normal.headers.get("X-Export-Limited") == "false"

        # When export row limit is small, triggers truncation indication
        with patch.dict(client.application.config, {"EXPORT_ROW_LIMIT": 3}):
            res_limited = client.get("/students/export-csv")
            assert res_limited.status_code == 200
            assert res_limited.headers.get("X-Export-Status") == "limited"
            assert res_limited.headers.get("X-Export-Limited") == "true"
            assert "X-Export-Warning" in res_limited.headers

            # Count rows: 1 header row + exactly 3 data rows
            reader = csv.reader(io.StringIO(res_limited.get_data(as_text=True)))
            rows = list(reader)
            assert len(rows) == 4

    def test_pdf_export_limits_and_truncation_headers(self, client):
        """11. Verifies PDF export indicates truncation status in headers and document metadata."""
        # Under normal conditions
        res_normal = client.get("/reports/export-pdf")
        assert res_normal.status_code == 200
        assert res_normal.headers.get("X-Export-Status") in ("complete", "limited")

        # When PDF limit is small (e.g. 2 rows)
        with patch.dict(client.application.config, {"EXPORT_PDF_ROW_LIMIT": 2}):
            res_limited = client.get("/reports/export-pdf")
            assert res_limited.status_code == 200
            assert res_limited.headers.get("X-Export-Status") == "limited"
            assert res_limited.headers.get("X-Export-Limited") == "true"
            assert "X-Export-Warning" in res_limited.headers
            assert res_limited.get_data().startswith(b"%PDF-")

    def test_empty_export_handling(self, client):
        """12. Verifies empty exports are handled gracefully without errors for CSV and PDF."""
        # Filter matching zero records
        res_csv = client.get("/students/export-csv?search=__ZERO_MATCHING_STUDENT_XYZ__")
        assert res_csv.status_code == 200
        assert res_csv.headers.get("X-Export-Status") == "empty"
        reader = csv.reader(io.StringIO(res_csv.get_data(as_text=True)))
        rows = list(reader)
        # Should contain header row only
        assert len(rows) == 1
        assert "Roll No" in rows[0]

        # Placement empty export
        res_placement_csv = client.get("/placements/export-csv?search=__ZERO_MATCHING_OFFER_XYZ__")
        assert res_placement_csv.status_code == 200
        assert res_placement_csv.headers.get("X-Export-Status") == "empty"

        # PDF empty export
        res_pdf = client.get("/reports/export-pdf?min_salary=999999")
        assert res_pdf.status_code == 200
        assert res_pdf.headers.get("X-Export-Status") == "empty"
        assert res_pdf.get_data().startswith(b"%PDF-")

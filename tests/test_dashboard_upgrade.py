import unittest
from app import create_app
from services.dashboard_service import (
    get_dashboard_stats,
    get_branchwise_analytics_chart_data,
    get_yearwise_placement_chart_data,
    get_package_distribution_chart_data,
    get_placement_vs_internship_chart_data,
    get_internship_completion_chart_data,
    get_multiple_offers_chart_data,
    get_dashboard_filter_options,
    get_comprehensive_dashboard_data,
)


class DashboardUpgradeTestCase(unittest.TestCase):
    """Test suite verifying the upgraded enterprise placement dashboard calculations, filters, and charts."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()

    def test_01_unfiltered_kpi_metrics(self):
        """Verify the 8 core KPI cards accurately compute aggregations across the baseline cohort."""
        stats = get_dashboard_stats()
        self.assertIn("kpi", stats)
        kpi = stats["kpi"]

        # 1. Total Students
        self.assertEqual(kpi["total_students"], 30)
        # 2. Eligible Students (0 Backlogs and CGPA >= 6.0)
        self.assertEqual(kpi["eligible_students"], 27)
        # 3. Total Companies
        self.assertEqual(kpi["total_companies"], 11)
        # 4. Active Recruitment Drives
        self.assertEqual(kpi["active_drives"], 21)
        # 5. Total Placement Offers
        self.assertEqual(kpi["total_offers"], 38)
        # 6. Successfully Placed Students
        self.assertEqual(kpi["placed_students"], 20)
        self.assertEqual(kpi["placement_rate"], 66.7)
        # 7. Average Package (12.07 LPA)
        self.assertAlmostEqual(kpi["avg_package"], 12.07, places=2)
        # 8. Highest Package (19.50 LPA)
        self.assertEqual(kpi["highest_package"], 19.50)

        # Legacy backward-compatibility assertions
        self.assertEqual(stats["students"]["total"], 30)
        self.assertEqual(stats["placements"]["total_offers"], 38)
        self.assertEqual(stats["companies"]["total"], 11)
        self.assertEqual(stats["internships"]["total"], 62)

    def test_02_branch_filter_calculations(self):
        """Verify KPI metrics correctly calculate when filtered by engineering discipline (CSE and ME)."""
        # CSE Filter
        cse_stats = get_dashboard_stats(filters={"branch": "CSE"})
        cse_kpi = cse_stats["kpi"]
        self.assertEqual(cse_kpi["total_students"], 14)
        self.assertEqual(cse_kpi["eligible_students"], 14)
        self.assertEqual(cse_kpi["placed_students"], 12)
        self.assertEqual(cse_kpi["total_offers"], 25)
        self.assertEqual(cse_kpi["total_companies"], 8)
        self.assertAlmostEqual(cse_kpi["avg_package"], 13.87, places=2)
        self.assertEqual(cse_kpi["highest_package"], 19.50)

        # Mechanical Engineering (ME) Filter (Cohort with 0 placement offers)
        me_stats = get_dashboard_stats(filters={"branch": "ME"})
        me_kpi = me_stats["kpi"]
        self.assertEqual(me_kpi["total_students"], 4)
        self.assertEqual(me_kpi["eligible_students"], 3)
        self.assertEqual(me_kpi["placed_students"], 0)
        self.assertEqual(me_kpi["total_offers"], 0)
        self.assertEqual(me_kpi["placement_rate"], 0.0)
        self.assertEqual(me_kpi["avg_package"], 0.0)

    def test_03_batch_and_placement_year_filters(self):
        """Verify KPI calculations correctly filter by graduating batch and placement year."""
        stats_2024 = get_dashboard_stats(filters={"batch_year": 2024})
        kpi_2024 = stats_2024["kpi"]
        self.assertTrue(kpi_2024["total_students"] > 0)
        self.assertEqual(kpi_2024["active_drives"], 9)  # Drives in 2024 cycle

        # Placement Year filter
        stats_py2022 = get_dashboard_stats(filters={"placement_year": 2022})
        kpi_py2022 = stats_py2022["kpi"]
        self.assertEqual(kpi_py2022["total_offers"], 10)
        self.assertEqual(kpi_py2022["active_drives"], 4)

    def test_04_chart1_branchwise_placement_distribution(self):
        """Verify Chart 1: Branch-wise placement distribution data structure and accuracy."""
        data = get_branchwise_analytics_chart_data()
        self.assertFalse(data["is_empty"])
        self.assertIn("CSE", data["labels"])
        self.assertIn("ECE", data["labels"])
        self.assertIn("IT", data["labels"])
        self.assertIn("ME", data["labels"])

        self.assertEqual(len(data["labels"]), len(data["student_counts"]))
        self.assertEqual(len(data["labels"]), len(data["placed_students"]))
        self.assertEqual(len(data["labels"]), len(data["eligible_students"]))
        self.assertEqual(len(data["labels"]), len(data["placement_rates"]))

        # Verify CSE values
        cse_idx = data["labels"].index("CSE")
        self.assertEqual(data["student_counts"][cse_idx], 14)
        self.assertEqual(data["placed_students"][cse_idx], 12)
        self.assertEqual(data["eligible_students"][cse_idx], 14)

    def test_05_chart2_yearwise_placement_trends(self):
        """Verify Chart 2: Year-wise placement trends data structure and progression."""
        data = get_yearwise_placement_chart_data()
        self.assertFalse(data["is_empty"])
        self.assertEqual(data["labels"], ["2022", "2023", "2024", "2025"])
        self.assertEqual(data["offer_counts"], [10, 6, 11, 11])
        self.assertEqual(data["accepted_counts"], [6, 3, 5, 6])
        self.assertEqual(len(data["avg_packages"]), 4)

    def test_06_chart3_package_distribution(self):
        """Verify Chart 3: CTC package tiers distribution (< 8, 8-12, 12-16, 16+ LPA)."""
        data = get_package_distribution_chart_data()
        self.assertFalse(data["is_empty"])
        self.assertEqual(len(data["labels"]), 4)
        self.assertEqual(data["total_offers"], 38)
        self.assertEqual(sum(data["counts"]), 38)
        self.assertEqual(data["counts"], [11, 8, 7, 12])

        # Verify percentages sum close to 100%
        self.assertAlmostEqual(sum(data["percentages"]), 100.0, delta=1.0)

    def test_07_chart4_placement_vs_internship(self):
        """Verify Chart 4: Direct branch comparison between placement offers and internships."""
        data = get_placement_vs_internship_chart_data()
        self.assertFalse(data["is_empty"])
        self.assertIn("CSE", data["labels"])
        self.assertIn("ME", data["labels"])
        self.assertEqual(len(data["placement_offers"]), len(data["total_internships"]))

        cse_idx = data["labels"].index("CSE")
        self.assertEqual(data["placement_offers"][cse_idx], 25)
        self.assertEqual(data["total_internships"][cse_idx], 32)

    def test_08_chart5_internship_completion(self):
        """Verify Chart 5: Student curriculum degree internship compliance breakdown."""
        data = get_internship_completion_chart_data()
        self.assertFalse(data["is_empty"])
        self.assertEqual(data["labels"], [
            "Fully Completed (Both)",
            "Partially Completed (1 of 2)",
            "Pending / Incomplete",
        ])
        self.assertEqual(data["total_students"], 30)
        self.assertEqual(data["counts"][0], 29)  # 29 fully completed
        self.assertEqual(data["counts"][2], 1)   # 1 pending
        self.assertEqual(data["completion_rate"], 96.7)

    def test_09_chart6_multiple_offers_distribution(self):
        """Verify Chart 6: Candidate multiple-offer distribution."""
        data = get_multiple_offers_chart_data()
        self.assertFalse(data["is_empty"])
        self.assertEqual(data["labels"], [
            "0 Offers (Unplaced)",
            "1 Offer (Single)",
            "2 Offers (Dual)",
            "3+ Offers (Multiple)",
        ])
        self.assertEqual(data["total_students"], 30)
        self.assertEqual(data["counts"], [7, 10, 11, 2])
        self.assertEqual(data["multiple_offer_students"], 13)

    def test_10_empty_filter_state_handling(self):
        """Verify that out-of-range filters handle zero records gracefully with is_empty flags."""
        empty_stats = get_dashboard_stats(filters={"batch_year": 2099})
        self.assertEqual(empty_stats["kpi"]["total_students"], 0)
        self.assertEqual(empty_stats["kpi"]["total_offers"], 0)
        self.assertEqual(empty_stats["kpi"]["placement_rate"], 0.0)

        empty_chart = get_package_distribution_chart_data(filters={"batch_year": 2099})
        self.assertTrue(empty_chart["is_empty"])
        self.assertEqual(empty_chart["total_offers"], 0)

    def test_11_filter_options_query(self):
        """Verify get_dashboard_filter_options fetches distinct values directly from database."""
        options = get_dashboard_filter_options()
        self.assertIn("branches", options)
        self.assertIn("batch_years", options)
        self.assertIn("placement_years", options)
        self.assertIn("CSE", options["branches"])
        self.assertIn(2024, options["batch_years"])
        self.assertIn(2024, options["placement_years"])

    def test_12_comprehensive_dashboard_data_provider(self):
        """Verify get_comprehensive_dashboard_data bundles all KPIs, all 6 charts, and filter options."""
        dash = get_comprehensive_dashboard_data()
        self.assertIn("stats", dash)
        self.assertIn("kpi", dash)
        self.assertIn("charts", dash)
        self.assertIn("filter_options", dash)

        charts = dash["charts"]
        self.assertIn("branchwise", charts)
        self.assertIn("yearwise", charts)
        self.assertIn("package_distribution", charts)
        self.assertIn("placement_vs_internship", charts)
        self.assertIn("internship_completion", charts)
        self.assertIn("multiple_offers", charts)

    def test_13_api_analytics_dashboard_endpoint(self):
        """Verify GET /api/analytics/dashboard returns HTTP 200 and supports query filters."""
        res = self.client.get("/api/analytics/dashboard")
        self.assertEqual(res.status_code, 200)
        payload = res.get_json()
        self.assertEqual(payload["status"], "success")
        self.assertIn("students", payload["data"])
        self.assertIn("placements", payload["data"])
        self.assertIn("kpi", payload["data"])
        self.assertIn("charts", payload["data"])

        # Filtered request
        res_filtered = self.client.get("/api/analytics/dashboard?branch=CSE&batch_year=2024")
        self.assertEqual(res_filtered.status_code, 200)
        data_filtered = res_filtered.get_json()["data"]
        self.assertEqual(data_filtered["kpi"]["total_students"], 4)

    def test_14_html_dashboard_page_rendering(self):
        """Verify GET / renders the upgraded HTML dashboard with all 8 KPI cards, filters, and 6 charts."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        # 8 KPI Cards
        self.assertIn("Total Students", html)
        self.assertIn("Eligible Students", html)
        self.assertIn("Total Companies", html)
        self.assertIn("Active Recruitment Drives", html)
        self.assertIn("Total Placement Offers", html)
        self.assertIn("Successfully Placed Students", html)
        self.assertIn("Average Package", html)
        self.assertIn("Highest Package", html)

        # Filter Controls
        self.assertIn("filterBatchYear", html)
        self.assertIn("filterBranch", html)
        self.assertIn("filterPlacementYear", html)
        self.assertIn("resetFiltersBtn", html)

        # 6 Interactive Canvases
        self.assertIn("branchwisePlacementChart", html)
        self.assertIn("yearwisePlacementChart", html)
        self.assertIn("packageDistributionChart", html)
        self.assertIn("placementVsInternshipChart", html)
        self.assertIn("internshipCompletionChart", html)
        self.assertIn("multipleOffersChart", html)

        # Backward-compatibility canvases
        self.assertIn("offerStatusChart", html)
        self.assertIn("internshipBreakdownChart", html)


if __name__ == "__main__":
    unittest.main()


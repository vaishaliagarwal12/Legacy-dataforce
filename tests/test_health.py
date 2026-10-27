import unittest
from app import create_app
from db import ping_db, DatabaseError


class HealthRouteTestCase(unittest.TestCase):
    """Test suite for verifying the Flask application and /health endpoint."""

    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()

    def test_health_endpoint_response_structure(self):
        """Tests that GET /health returns expected keys and HTTP 200/503."""
        response = self.client.get("/health")
        self.assertIn(response.status_code, (200, 503))
        data = response.get_json()

        self.assertIsInstance(data, dict)
        self.assertIn("status", data)
        self.assertIn("service", data)
        self.assertIn("database", data)

        db_info = data["database"]
        self.assertEqual(db_info.get("engine"), "MySQL")
        self.assertIn("connection", db_info)
        self.assertIn("latency_ms", db_info)

    def test_direct_database_ping(self):
        """Directly tests the ping_db helper against the configured MySQL server."""
        try:
            result = ping_db()
            self.assertEqual(result["status"], "healthy")
            self.assertEqual(result["database"], "connected")
            self.assertTrue(len(result["mysql_version"]) > 0)
        except DatabaseError as err:
            self.fail(f"Direct database ping failed: {err}")

    def test_parameterized_query_execution(self):
        """Tests that execute_query and execute_one correctly bind parameters safely."""
        from db import execute_query, execute_one

        # Test execute_one with parameterized arithmetic
        row = execute_one("SELECT %s + %s AS sum_val, %s AS tag", (15, 27, "parameter_test"))
        self.assertIsNotNone(row)
        self.assertEqual(row["sum_val"], 42)
        self.assertEqual(row["tag"], "parameter_test")

        # Test execute_query with multiple rows
        rows = execute_query(
            "SELECT %s AS val UNION ALL SELECT %s AS val",
            ("item_alpha", "item_beta")
        )
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["val"], "item_alpha")
        self.assertEqual(rows[1]["val"], "item_beta")

    def test_connection_context_manager_cleanup(self):
        """Verifies that get_connection automatically closes connections upon block exit."""
        from db import get_connection
        conn_ref = None
        with get_connection() as conn:
            conn_ref = conn
            self.assertTrue(conn.open)
        # Connection must be closed after context manager exits
        self.assertFalse(conn_ref.open)

    def test_health_endpoint_db_failure_simulation(self):
        """Tests that /health returns HTTP 503 and status 'unhealthy' if the database is unreachable."""
        from unittest.mock import patch
        with patch("services.health_service.ping_db", side_effect=DatabaseError("Simulated connection timeout")):
            response = self.client.get("/health")
            self.assertEqual(response.status_code, 503)
            data = response.get_json()
            self.assertEqual(data["status"], "unhealthy")
            self.assertEqual(data["database"]["connection"], "disconnected")
            self.assertIn("Simulated connection timeout", data["database"]["error"])

    def test_homepage_render(self):
        """Tests that GET / returns HTTP 200 with HTML content."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Placement & Internship Portal", response.data)


if __name__ == "__main__":
    unittest.main()


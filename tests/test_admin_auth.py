"""Tests for Administrator-Only Authentication Rules.

Verifies:
1. Only the one admin account defined in .env can use the application.
2. NO sign-up page, NO register route, NO forgot password flow exists.
3. Every page, every /api/ route, the SQL console, and every CSV/PDF export requires admin login.
4. Unauthenticated requests redirect to /login (pages) or return HTTP 401 (API).
5. Comprehensive route audit looping over app.url_map while logged out confirms all non-exempt routes redirect or return 401.
6. A new route added without protection causes the audit test to fail.
7. Navbar and sidebar navigation render only after login; login page shows no data and no navigation links.
8. Navbar displays the authenticated username and a Logout button.
"""

import re
import pytest
from werkzeug.security import generate_password_hash
from app import create_app
from config import Config

TEST_ADMIN_USERNAME = "test_admin"
TEST_ADMIN_PASSWORD = "TestAdminPassword2026!"
TEST_ADMIN_PASSWORD_HASH = generate_password_hash(TEST_ADMIN_PASSWORD)


def audit_all_routes_require_authentication(app, client):
    """Audits every registered route in app.url_map while unauthenticated.

    Raises AssertionError if any route (except /login, /static, and /health)
    returns anything other than a redirect to /login (302) or HTTP 401.
    """
    dummy_args = {
        "student_id": 1,
        "company_id": 1,
        "placement_id": 1,
        "internship_id": 1,
        "req_id": 1,
        "phone_no": "9999999999",
        "skill": "Python",
        "filename": "css/style.css",
    }

    exempt_endpoints = {"static", "health_bp.health_check", "auth_bp.login"}
    leaks = []

    for rule in app.url_map.iter_rules():
        if rule.endpoint in exempt_endpoints:
            continue

        url = rule.rule
        for k, v in dummy_args.items():
            url = re.sub(r"<(?:[^:]+:)?\b" + k + r"\b>", str(v), url)

        methods = [m for m in rule.methods if m not in ("HEAD", "OPTIONS")]
        method = methods[0]

        res = client.open(url, method=method)

        if res.status_code == 302:
            location = res.headers.get("Location", "")
            if "/login" not in location:
                leaks.append(
                    (
                        rule.rule,
                        method,
                        res.status_code,
                        f"Redirected to {location} instead of /login",
                    )
                )
        elif res.status_code == 401:
            pass  # Expected for API/JSON endpoints
        else:
            leaks.append(
                (rule.rule, method, res.status_code, "Expected 302 redirect to /login or 401")
            )

    if leaks:
        leak_details = "\n".join(
            f" - [{m}] {r} -> HTTP {status}: {msg}" for r, m, status, msg in leaks
        )
        raise AssertionError(
            f"Security Audit Failure: {len(leaks)} unprotected route(s) detected:\n{leak_details}"
        )


class TestAdminAuthentication:
    """Test suite verifying strict single-admin authentication and access control."""

    @pytest.fixture(autouse=True)
    def isolate_admin_credentials(self, app):
        """Explicitly isolates test credentials on app config so tests never depend on real .env."""
        app.config["ADMIN_USERNAME"] = TEST_ADMIN_USERNAME
        app.config["ADMIN_PASSWORD_HASH"] = TEST_ADMIN_PASSWORD_HASH
        app.config["ADMIN_PASSWORD"] = None
        yield

    def test_no_signup_register_or_forgot_password_routes_exist(self, app):
        """Verifies NO sign-up, register, or forgot password routes exist in url_map."""
        forbidden_keywords = [
            "signup",
            "sign-up",
            "register",
            "registration",
            "forgot",
            "reset_password",
            "reset-password",
        ]
        for rule in app.url_map.iter_rules():
            rule_str = rule.rule.lower()
            endpoint_str = rule.endpoint.lower()
            for kw in forbidden_keywords:
                assert (
                    kw not in rule_str
                ), f"Forbidden keyword '{kw}' found in route rule: {rule.rule}"
                assert (
                    kw not in endpoint_str
                ), f"Forbidden keyword '{kw}' found in endpoint: {rule.endpoint}"

    def test_login_page_renders_without_navigation_or_links(self, unauthenticated_client):
        """Verifies login page shows no data, no sidebar, and no navigation links to other pages."""
        res = unauthenticated_client.get("/login")
        assert res.status_code == 200
        html = res.get_data(as_text=True)

        # Confirm sidebar is not rendered
        assert 'id="appSidebar"' not in html
        assert "sidebar-menu" not in html

        # Confirm no links to administrative pages
        assert 'href="/students"' not in html
        assert 'href="/companies"' not in html
        assert 'href="/internships"' not in html
        assert 'href="/placements"' not in html
        assert 'href="/reports"' not in html
        assert 'href="/sql-reports"' not in html

        # Confirm no sign-up or register links exist
        assert "Sign Up" not in html
        assert "Register" not in html
        assert "Forgot Password" not in html

        # Confirm admin login form exists
        assert 'name="username"' in html
        assert 'name="password"' in html
        assert 'name="csrf_token"' in html
        assert "Administrator Sign In" in html

    def test_login_successful_with_admin_credentials_from_env(self, unauthenticated_client, app):
        """Verifies logging in with the configured admin account succeeds."""
        app.config["ADMIN_USERNAME"] = TEST_ADMIN_USERNAME
        app.config["ADMIN_PASSWORD_HASH"] = TEST_ADMIN_PASSWORD_HASH
        app.config["ADMIN_PASSWORD"] = None

        res = unauthenticated_client.post(
            "/login",
            data={"username": TEST_ADMIN_USERNAME, "password": TEST_ADMIN_PASSWORD},
            follow_redirects=False,
        )
        assert res.status_code == 302
        assert res.headers.get("Location") in ("/", "http://localhost/")

        with unauthenticated_client.session_transaction() as sess:
            assert sess.get("admin_logged_in") is True
            assert sess.get("admin_user") == TEST_ADMIN_USERNAME

    def test_login_rejected_with_invalid_credentials(self, unauthenticated_client, app):
        """Verifies login attempt with invalid credentials is rejected with 401."""
        app.config["ADMIN_USERNAME"] = TEST_ADMIN_USERNAME
        app.config["ADMIN_PASSWORD_HASH"] = TEST_ADMIN_PASSWORD_HASH
        app.config["ADMIN_PASSWORD"] = None

        res = unauthenticated_client.post(
            "/login",
            data={"username": TEST_ADMIN_USERNAME, "password": "WrongPassword123!"},
            follow_redirects=False,
        )
        assert res.status_code == 401
        html = res.get_data(as_text=True)
        assert "Invalid administrator credentials" in html

        with unauthenticated_client.session_transaction() as sess:
            assert sess.get("admin_logged_in") is not True

    def test_login_api_json_authentication(self, unauthenticated_client, app):
        """Verifies JSON API login endpoint behavior for automated agents/tools."""
        app.config["ADMIN_USERNAME"] = TEST_ADMIN_USERNAME
        app.config["ADMIN_PASSWORD_HASH"] = TEST_ADMIN_PASSWORD_HASH
        app.config["ADMIN_PASSWORD"] = None

        # Valid JSON login
        res_ok = unauthenticated_client.post(
            "/login",
            json={"username": TEST_ADMIN_USERNAME, "password": TEST_ADMIN_PASSWORD},
        )
        assert res_ok.status_code == 200
        data_ok = res_ok.get_json()
        assert data_ok["status"] == "success"

        # Invalid JSON login
        res_fail = unauthenticated_client.post(
            "/login",
            json={"username": TEST_ADMIN_USERNAME, "password": "BadPassword"},
        )
        assert res_fail.status_code == 401
        data_fail = res_fail.get_json()
        assert data_fail["status"] == "fail"

    def test_logout_clears_session_and_redirects_to_login(self, client):
        """Verifies logout purges the session and redirects to /login."""
        # Initial state is authenticated
        with client.session_transaction() as sess:
            assert sess.get("admin_logged_in") is True

        res = client.get("/logout", follow_redirects=False)
        assert res.status_code == 302
        assert "/login" in res.headers.get("Location", "")

        with client.session_transaction() as sess:
            assert sess.get("admin_logged_in") is None
            assert sess.get("admin_user") is None

    def test_navbar_shows_username_and_logout_when_logged_in(self, client, app):
        """Verifies authenticated pages show the admin username and a Logout button in the navbar."""
        app.config["ADMIN_USERNAME"] = TEST_ADMIN_USERNAME
        app.config["ADMIN_PASSWORD_HASH"] = TEST_ADMIN_PASSWORD_HASH
        app.config["ADMIN_PASSWORD"] = None

        with client.session_transaction() as sess:
            sess["admin_logged_in"] = True
            sess["admin_user"] = TEST_ADMIN_USERNAME

        res = client.get("/")
        assert res.status_code == 200
        html = res.get_data(as_text=True)

        assert TEST_ADMIN_USERNAME in html
        assert 'id="logoutBtn"' in html
        assert 'href="/logout"' in html
        assert "Logout" in html

    def test_all_registered_routes_require_authentication_when_logged_out(
        self, app, unauthenticated_client
    ):
        """Loops over app.url_map while logged out and verifies every non-exempt route redirects or returns 401."""
        audit_all_routes_require_authentication(app, unauthenticated_client)

    def test_new_route_added_without_protection_makes_audit_fail(self):
        """Verifies that adding a new route without @admin_required protection causes the audit test to fail."""
        test_app = create_app("testing")
        test_app.config["ADMIN_USERNAME"] = TEST_ADMIN_USERNAME
        test_app.config["ADMIN_PASSWORD_HASH"] = TEST_ADMIN_PASSWORD_HASH
        test_app.config["ADMIN_PASSWORD"] = None

        # Dynamically register an unprotected route on test_app
        @test_app.route("/api/v1/unprotected-secret-endpoint", methods=["GET"])
        def unprotected_secret():
            return {"secret_key": "leaked_data"}, 200

        unauthed_client = test_app.test_client(auto_login=False)

        # Confirm that the route audit detects this leak and raises an AssertionError
        with pytest.raises(AssertionError) as exc_info:
            audit_all_routes_require_authentication(test_app, unauthed_client)

        error_message = str(exc_info.value)
        assert "Security Audit Failure" in error_message
        assert "/api/v1/unprotected-secret-endpoint" in error_message
        assert "HTTP 200" in error_message

    def test_login_safe_redirect_prevents_open_redirect(self, unauthenticated_client, app):
        """Verifies login safe redirect sanitizes external next parameter to prevent open redirects."""
        app.config["ADMIN_USERNAME"] = TEST_ADMIN_USERNAME
        app.config["ADMIN_PASSWORD_HASH"] = TEST_ADMIN_PASSWORD_HASH
        app.config["ADMIN_PASSWORD"] = None

        # Attempt external open redirect
        res = unauthenticated_client.post(
            "/login?next=https://attacker.com/evil",
            data={"username": TEST_ADMIN_USERNAME, "password": TEST_ADMIN_PASSWORD},
            follow_redirects=False,
        )
        assert res.status_code == 302
        # Must fallback to internal home instead of external target
        assert res.headers.get("Location") in ("/", "http://localhost/")

    def test_set_admin_password_cli_short_password_rejected(self, monkeypatch):
        """Verifies set_admin_password.py refuses passwords shorter than 8 characters."""
        from tools import set_admin_password

        inputs = iter(["admin"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        passwords = iter(["short", "short"])
        monkeypatch.setattr("getpass.getpass", lambda _: next(passwords))

        with pytest.raises(SystemExit) as exc_info:
            set_admin_password.main()
        assert exc_info.value.code == 1

    def test_set_admin_password_cli_mismatch_rejected(self, monkeypatch):
        """Verifies set_admin_password.py refuses passwords that do not match."""
        from tools import set_admin_password

        inputs = iter(["admin"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        passwords = iter(["ValidPassword123!", "MismatchPassword999!"])
        monkeypatch.setattr("getpass.getpass", lambda _: next(passwords))

        with pytest.raises(SystemExit) as exc_info:
            set_admin_password.main()
        assert exc_info.value.code == 1

    def test_set_admin_password_updates_env_and_preserves_other_lines(self, tmp_path):
        """Verifies update_env_file writes ADMIN_PASSWORD_HASH with single quotes and preserves other keys."""
        from tools.set_admin_password import update_env_file
        from werkzeug.security import generate_password_hash

        fake_env = tmp_path / ".env"
        fake_env.write_text(
            "# Custom Configuration\n"
            "FLASK_ENV=development\n"
            "PORT=5000\n"
            "MYSQL_HOST=localhost\n"
            "SECRET_KEY=\n",
            encoding="utf-8",
        )

        dummy_hash = generate_password_hash("NewMasterAdminPass2026!")
        update_env_file("superadmin", dummy_hash, env_path=fake_env)

        updated_text = fake_env.read_text(encoding="utf-8")
        assert "ADMIN_USERNAME=superadmin" in updated_text
        assert f"ADMIN_PASSWORD_HASH='{dummy_hash}'" in updated_text
        assert "# Custom Configuration" in updated_text
        assert "FLASK_ENV=development" in updated_text
        assert "PORT=5000" in updated_text
        assert "MYSQL_HOST=localhost" in updated_text
        # Missing SECRET_KEY was populated
        assert "SECRET_KEY=" in updated_text
        assert "SECRET_KEY=\n" not in updated_text

    def test_login_page_accepts_new_password_and_rejects_wrong_one(
        self, unauthenticated_client, app
    ):
        """Verifies login page accepts the newly hashed admin password and rejects wrong passwords."""
        from werkzeug.security import generate_password_hash

        new_password = "NewlyGeneratedSecurePassword2026!"
        new_hash = generate_password_hash(new_password)

        # Configure the application runtime with the new credentials
        app.config["ADMIN_USERNAME"] = "testadmin"
        app.config["ADMIN_PASSWORD_HASH"] = f"'{new_hash}'"

        # Wrong password is rejected
        res_fail = unauthenticated_client.post(
            "/login",
            data={"username": "testadmin", "password": "WrongPassword123!"},
            follow_redirects=False,
        )
        assert res_fail.status_code == 401
        with unauthenticated_client.session_transaction() as sess:
            assert sess.get("admin_logged_in") is not True

        # Correct new password is accepted
        res_ok = unauthenticated_client.post(
            "/login",
            data={"username": "testadmin", "password": new_password},
            follow_redirects=False,
        )
        assert res_ok.status_code == 302
        assert res_ok.headers.get("Location") in ("/", "http://localhost/")
        with unauthenticated_client.session_transaction() as sess:
            assert sess.get("admin_logged_in") is True
            assert sess.get("admin_user") == "testadmin"

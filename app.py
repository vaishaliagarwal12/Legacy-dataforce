import os
import time
import logging
from flask import Flask, jsonify, request, flash, redirect, render_template, session
from flask.testing import FlaskClient
from config import config_by_name, Config
from db.connection import DatabaseError
from routes import (
    auth_bp,
    health_bp,
    main_bp,
    student_bp,
    company_bp,
    placement_bp,
    internship_bp,
)
from services import (
    ServiceError,
    generate_csrf_token,
    verify_csrf_token,
    is_admin_authenticated,
)

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("legacy_dataforce")


class AutoAuthTestClient(FlaskClient):
    """Test client supporting auto-authenticated testing while allowing unauthenticated tests."""

    def __init__(self, *args, **kwargs):
        auto_login = kwargs.pop("auto_login", True)
        super().__init__(*args, **kwargs)
        if auto_login and getattr(self.application, "config", {}).get(
            "AUTO_AUTH_TEST_CLIENT", True
        ):
            with self.session_transaction() as sess:
                sess["admin_logged_in"] = True
                sess["admin_user"] = self.application.config.get("ADMIN_USERNAME", "admin")


def create_app(config_name: str = None) -> Flask:
    """Application factory for the Flask service."""
    if not config_name:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    selected_config = config_by_name.get(config_name, Config)
    app.config.from_object(selected_config)
    app.test_client_class = AutoAuthTestClient

    # Register Route Blueprints (Canonical 7-Table Schema)
    app.register_blueprint(auth_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(placement_bp)
    app.register_blueprint(internship_bp)

    # Cached database health indicator for lightweight non-blocking template rendering
    _db_health_cache = {"is_connected": True, "last_check": 0.0}

    # Expose CSRF token generator and database health status to all Jinja2 templates
    @app.context_processor
    def inject_template_context():
        now = time.time()
        cache_ttl = float(
            app.config.get("DB_HEALTH_CACHE_TTL", getattr(Config, "DB_HEALTH_CACHE_TTL", 10.0))
        )
        if now - _db_health_cache["last_check"] > cache_ttl:
            try:
                from db.connection import ping_db

                ping_db()
                _db_health_cache["is_connected"] = True
            except Exception:
                _db_health_cache["is_connected"] = False
            _db_health_cache["last_check"] = now

        return {
            "csrf_token": generate_csrf_token,
            "is_db_connected": _db_health_cache["is_connected"],
            "is_admin_logged_in": is_admin_authenticated(),
            "admin_username": session.get("admin_user", app.config.get("ADMIN_USERNAME", "admin")),
        }

    # State-Changing Request Security & CSRF Enforcement
    @app.before_request
    def check_csrf_protection():
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            # When unauthenticated on a non-login route, defer to @admin_required
            if not is_admin_authenticated() and request.path != "/login":
                return
            if not app.config.get("CSRF_ENABLED", True):
                return
            if app.config.get("TESTING", False) and not app.config.get("WTF_CSRF_ENABLED", False):
                return
            if request.path.startswith("/api/"):
                return

            token = (
                request.form.get("csrf_token")
                or request.headers.get("X-CSRFToken")
                or request.headers.get("X-CSRF-Token")
            )
            if not verify_csrf_token(token):
                logger.warning(
                    "CSRF validation rejected for %s %s from IP %s",
                    request.method,
                    request.path,
                    request.remote_addr,
                )
                if request.accept_mimetypes.accept_html and not request.is_json:
                    flash("Security Validation Failed: Invalid or missing CSRF token.", "danger")
                    return redirect(request.referrer or "/")
                return (
                    jsonify(
                        {
                            "status": "fail",
                            "message": "CSRF validation failed. Token missing or invalid.",
                            "code": 400,
                        }
                    ),
                    400,
                )

    # HTTP Security Headers (OWASP Hardening)
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # Custom Service Domain Error Handlers
    @app.errorhandler(ServiceError)
    def handle_service_error(error: ServiceError):
        logger.warning("Service error [%s]: %s", error.status_code, error.message)
        return (
            jsonify(
                {
                    "status": "fail" if error.status_code < 500 else "error",
                    "message": error.message,
                    "code": error.status_code,
                }
            ),
            error.status_code,
        )

    @app.errorhandler(DatabaseError)
    def handle_database_error(error: DatabaseError):
        logger.error("Database error intercepted: %s", error)
        if request.accept_mimetypes.accept_html and not request.path.startswith("/api/"):
            return (
                render_template(
                    "errors/500.html",
                    error_title="500 - Database Connection Error",
                    error_message="A database error occurred. Internal details have been logged securely.",
                    is_db_connected=False,
                ),
                500,
            )
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "A database error occurred. Internal details have been logged securely.",
                    "code": 500,
                }
            ),
            500,
        )

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify({"status": "fail", "message": "Method not allowed", "code": 405}),
            405,
        )

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({"status": "fail", "message": "Resource not found", "code": 404}), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        logger.error("Internal Server Error: %s", error)
        if request.path.startswith("/api/"):
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Internal server processing failure",
                        "code": 500,
                    }
                ),
                500,
            )
        return render_template("errors/500.html"), 500

    return app


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)

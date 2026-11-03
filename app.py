import os
import logging
from flask import Flask, jsonify, request, flash, redirect, render_template
from config import config_by_name, Config
from db.connection import DatabaseError
from routes import (
    health_bp,
    main_bp,
    student_bp,
    course_bp,
    registration_bp,
    profile_bp,
    company_bp,
    drive_bp,
    opportunity_bp,
    round_bp,
    placement_bp,
    semester_result_bp,
    internship_bp,
)
from services import ServiceError, generate_csrf_token, verify_csrf_token

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("legacy_dataforce")


def create_app(config_name: str = None) -> Flask:
    """Application factory for the Flask service."""
    if not config_name:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    selected_config = config_by_name.get(config_name, Config)
    app.config.from_object(selected_config)

    # Register Route Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(registration_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(drive_bp)
    app.register_blueprint(opportunity_bp)
    app.register_blueprint(round_bp)
    app.register_blueprint(placement_bp)
    app.register_blueprint(semester_result_bp)
    app.register_blueprint(internship_bp)

    # Expose CSRF token generator to all Jinja2 templates
    @app.context_processor
    def inject_csrf_token():
        return {"csrf_token": generate_csrf_token}

    # State-Changing Request Security & CSRF Enforcement
    @app.before_request
    def check_csrf_protection():
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            # Check if CSRF enforcement is active
            if not app.config.get("CSRF_ENABLED", True):
                return
            # In testing mode, bypass CSRF unless explicitly enabled (e.g. WTF_CSRF_ENABLED)
            if app.config.get("TESTING", False) and not app.config.get("WTF_CSRF_ENABLED", False):
                return
            # Allow purely stateless /api/ requests unless originating from form or cookie session
            if request.path.startswith("/api/"):
                return

            # Validate CSRF token from Form data or HTTP Request Headers
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
                return jsonify({
                    "status": "fail",
                    "message": "CSRF validation failed. Token missing or invalid.",
                    "code": 400,
                }), 400

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
        return jsonify({
            "status": "fail" if error.status_code < 500 else "error",
            "message": error.message,
            "code": error.status_code,
        }), error.status_code

    # Database Error Handler - Never leaks internal query syntax or database connection strings
    @app.errorhandler(DatabaseError)
    def handle_database_error(error: DatabaseError):
        logger.error("Internal database error: %s", error)
        return jsonify({
            "status": "error",
            "message": "A database error occurred. Internal details have been logged securely.",
            "code": 500,
        }), 500

    # Global HTTP Error Handlers
    @app.errorhandler(400)
    def handle_bad_request(error):
        return jsonify({"status": "fail", "message": "Bad request", "code": 400}), 400

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"status": "error", "message": "Endpoint not found", "code": 404}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({"status": "fail", "message": "Method not allowed for requested URL", "code": 405}), 405

    @app.errorhandler(500)
    def handle_server_error(error):
        logger.error("Unhandled internal server error: %s", error)
        return jsonify({"status": "error", "message": "Internal server error", "code": 500}), 500

    logger.info("Flask application initialized under '%s' mode with all blueprints registered.", config_name)
    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug_mode = app.config.get("DEBUG", False)
    logger.info("Starting Flask application server on http://localhost:%s (debug=%s)", port, debug_mode)
    app.run(host="0.0.0.0", port=port, debug=debug_mode)

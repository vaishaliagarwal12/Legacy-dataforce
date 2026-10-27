import os
import logging
from flask import Flask, jsonify
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
from services import ServiceError

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


    # Custom Service Domain Error Handlers
    @app.errorhandler(ServiceError)
    def handle_service_error(error: ServiceError):
        logger.warning("Service error [%s]: %s", error.status_code, error.message)
        return jsonify({
            "status": "fail" if error.status_code < 500 else "error",
            "message": error.message,
            "code": error.status_code,
        }), error.status_code

    @app.errorhandler(DatabaseError)
    def handle_database_error(error: DatabaseError):
        logger.error("Database failure: %s", error)
        return jsonify({
            "status": "error",
            "message": str(error),
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
    debug_mode = os.getenv("FLASK_DEBUG", "0") in ("1", "true", "True")
    logger.info("Starting Flask development server on http://localhost:%s", port)
    app.run(host="0.0.0.0", port=port, debug=debug_mode)

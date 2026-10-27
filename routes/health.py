from flask import jsonify
from . import health_bp
from services import check_system_health


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint demonstrating live Flask-to-MySQL connectivity.
    
    Returns HTTP 200 with JSON details when MySQL is connected.
    Returns HTTP 503 with diagnostic error if MySQL is disconnected.
    """
    payload, status_code = check_system_health()
    return jsonify(payload), status_code

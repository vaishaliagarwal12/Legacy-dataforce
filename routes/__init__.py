from flask import Blueprint

health_bp = Blueprint("health_bp", __name__)
main_bp = Blueprint("main_bp", __name__)
student_bp = Blueprint("student_bp", __name__, url_prefix="/api/students")
company_bp = Blueprint("company_bp", __name__, url_prefix="/api/companies")
placement_bp = Blueprint("placement_bp", __name__, url_prefix="/api/placements")
internship_bp = Blueprint("internship_bp", __name__, url_prefix="/api/internships")

from . import (
    health,
    main,
    students,
    companies,
    placements,
    internships,
)

__all__ = [
    "health_bp",
    "main_bp",
    "student_bp",
    "company_bp",
    "placement_bp",
    "internship_bp",
]

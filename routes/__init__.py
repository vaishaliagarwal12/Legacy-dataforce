from flask import Blueprint

health_bp = Blueprint("health_bp", __name__)
main_bp = Blueprint("main_bp", __name__)
student_bp = Blueprint("student_bp", __name__, url_prefix="/api/students")
course_bp = Blueprint("course_bp", __name__, url_prefix="/api/courses")
registration_bp = Blueprint("registration_bp", __name__, url_prefix="/api/registrations")
profile_bp = Blueprint("profile_bp", __name__, url_prefix="/api/profiles")
company_bp = Blueprint("company_bp", __name__, url_prefix="/api/companies")
drive_bp = Blueprint("drive_bp", __name__, url_prefix="/api/drives")
opportunity_bp = Blueprint("opportunity_bp", __name__, url_prefix="/api/opportunities")
round_bp = Blueprint("round_bp", __name__, url_prefix="/api/rounds")
placement_bp = Blueprint("placement_bp", __name__, url_prefix="/api/placements")
semester_result_bp = Blueprint("semester_result_bp", __name__, url_prefix="/api/semester-results")
internship_bp = Blueprint("internship_bp", __name__, url_prefix="/api/internships")

from . import (
    health,
    main,
    students,
    courses,
    registrations,
    profiles,
    companies,
    drives,
    opportunities,
    rounds,
    placements,
    semester_results,
    internships,
)

__all__ = [
    "health_bp",
    "main_bp",
    "student_bp",
    "course_bp",
    "registration_bp",
    "profile_bp",
    "company_bp",
    "drive_bp",
    "opportunity_bp",
    "round_bp",
    "placement_bp",
    "semester_result_bp",
    "internship_bp",
]

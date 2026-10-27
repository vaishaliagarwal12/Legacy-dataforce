from flask import request, jsonify
from . import registration_bp
from services import (
    register_student_course,
    get_registration,
    list_registrations,
    update_registration,
    unregister_student_course,
)


@registration_bp.route("", methods=["POST"])
def api_register_student_course():
    """Enrolls a student in a course."""
    payload = request.get_json() or {}
    reg = register_student_course(payload)
    return jsonify({
        "status": "success",
        "message": "Student successfully registered for course",
        "data": reg
    }), 201


@registration_bp.route("", methods=["GET"])
def api_list_registrations():
    """Lists and filters student-course enrollments."""
    student_id = request.args.get("student_id", type=int)
    course_id = request.args.get("course_id", type=int)
    enrollment_year = request.args.get("enrollment_year", type=int)
    grade = request.args.get("grade")

    registrations = list_registrations(
        student_id=student_id,
        course_id=course_id,
        enrollment_year=enrollment_year,
        grade=grade,
    )
    return jsonify({
        "status": "success",
        "total": len(registrations),
        "data": registrations
    }), 200


@registration_bp.route("/<int:student_id>/<int:course_id>", methods=["GET"])
def api_get_registration(student_id: int, course_id: int):
    """Retrieves a specific enrollment record."""
    reg = get_registration(student_id, course_id)
    return jsonify({
        "status": "success",
        "data": reg
    }), 200


@registration_bp.route("/<int:student_id>/<int:course_id>", methods=["PUT"])
def api_update_registration(student_id: int, course_id: int):
    """Updates enrollment grade or year."""
    payload = request.get_json() or {}
    reg = update_registration(student_id, course_id, payload)
    return jsonify({
        "status": "success",
        "message": "Registration updated successfully",
        "data": reg
    }), 200


@registration_bp.route("/<int:student_id>/<int:course_id>", methods=["DELETE"])
def api_unregister_student_course(student_id: int, course_id: int):
    """Unregisters a student from a course."""
    result = unregister_student_course(student_id, course_id)
    return jsonify({
        "status": "success",
        "message": result["message"],
        "student_id": result["student_id"],
        "course_id": result["course_id"]
    }), 200

from flask import request, jsonify
from . import course_bp
from services import (
    create_course,
    get_course,
    list_courses,
    update_course,
    delete_course,
)


@course_bp.route("", methods=["POST"])
def api_create_course():
    """Creates a new academic course."""
    payload = request.get_json() or {}
    course = create_course(payload)
    return jsonify({
        "status": "success",
        "message": "Course created successfully",
        "data": course
    }), 201


@course_bp.route("", methods=["GET"])
def api_list_courses():
    """Lists, searches, and filters courses."""
    search = request.args.get("search")
    department = request.args.get("department")
    semester = request.args.get("semester", type=int)
    course_type = request.args.get("course_type")

    courses = list_courses(
        search=search,
        department=department,
        semester=semester,
        course_type=course_type,
    )
    return jsonify({
        "status": "success",
        "total": len(courses),
        "data": courses
    }), 200


@course_bp.route("/<int:course_id>", methods=["GET"])
def api_get_course(course_id: int):
    """Retrieves course details with enrolled students list."""
    course = get_course(course_id)
    return jsonify({
        "status": "success",
        "data": course
    }), 200


@course_bp.route("/<int:course_id>", methods=["PUT"])
def api_update_course(course_id: int):
    """Updates course curriculum attributes."""
    payload = request.get_json() or {}
    updated_course = update_course(course_id, payload)
    return jsonify({
        "status": "success",
        "message": "Course updated successfully",
        "data": updated_course
    }), 200


@course_bp.route("/<int:course_id>", methods=["DELETE"])
def api_delete_course(course_id: int):
    """Safely deletes a course; blocks if students are enrolled."""
    result = delete_course(course_id)
    return jsonify({
        "status": "success",
        "message": result["message"],
        "deleted_course_id": result["deleted_course_id"]
    }), 200

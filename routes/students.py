from flask import request, jsonify
from . import student_bp
from services import (
    create_student,
    get_student,
    list_students,
    update_student,
    delete_student,
    add_student_phone,
    list_student_phones,
    delete_student_phone,
)


@student_bp.route("", methods=["POST"])
def api_create_student():
    """Creates a new student along with multivalued phone numbers."""
    payload = request.get_json() or {}
    student = create_student(payload)
    return jsonify({
        "status": "success",
        "message": "Student created successfully",
        "data": student
    }), 201


@student_bp.route("", methods=["GET"])
def api_list_students():
    """Lists, searches, and filters students with pagination."""
    search = request.args.get("search")
    branch = request.args.get("branch")
    batch_year = request.args.get("batch_year", type=int)
    min_cgpa = request.args.get("min_cgpa", type=float)
    max_cgpa = request.args.get("max_cgpa", type=float)
    max_backlogs = request.args.get("max_backlogs", type=int)
    limit = request.args.get("limit", default=50, type=int)
    offset = request.args.get("offset", default=0, type=int)

    result = list_students(
        search=search,
        branch=branch,
        batch_year=batch_year,
        min_cgpa=min_cgpa,
        max_cgpa=max_cgpa,
        max_backlogs=max_backlogs,
        limit=limit,
        offset=offset,
    )
    return jsonify({
        "status": "success",
        "data": result["results"],
        "pagination": {
            "total": result["total"],
            "limit": result["limit"],
            "offset": result["offset"],
        }
    }), 200


@student_bp.route("/<int:student_id>", methods=["GET"])
def api_get_student(student_id: int):
    """Retrieves full details of a single student."""
    student = get_student(student_id)
    return jsonify({
        "status": "success",
        "data": student
    }), 200


@student_bp.route("/<int:student_id>", methods=["PUT"])
def api_update_student(student_id: int):
    """Updates student fields and/or contact numbers."""
    payload = request.get_json() or {}
    updated_student = update_student(student_id, payload)
    return jsonify({
        "status": "success",
        "message": "Student updated successfully",
        "data": updated_student
    }), 200


@student_bp.route("/<int:student_id>", methods=["DELETE"])
def api_delete_student(student_id: int):
    """Safely deletes a student; BLOCKS if placement or internship history exists."""
    result = delete_student(student_id)
    return jsonify({
        "status": "success",
        "message": result["message"],
        "deleted_student_id": result["deleted_student_id"]
    }), 200


# Multivalued Phone Number Routes
@student_bp.route("/<int:student_id>/phones", methods=["GET"])
def api_list_student_phones(student_id: int):
    """Lists all phone numbers for a student."""
    phones = list_student_phones(student_id)
    return jsonify({
        "status": "success",
        "student_id": student_id,
        "phone_numbers": phones
    }), 200


@student_bp.route("/<int:student_id>/phones", methods=["POST"])
def api_add_student_phone(student_id: int):
    """Adds a contact number to a student's phone table."""
    payload = request.get_json() or {}
    phone_no = payload.get("phone_no")
    result = add_student_phone(student_id, phone_no)
    return jsonify({
        "status": "success",
        "message": result["message"],
        "data": result
    }), 201


@student_bp.route("/<int:student_id>/phones/<path:phone_no>", methods=["DELETE"])
def api_delete_student_phone(student_id: int, phone_no: str):
    """Removes a specific phone number from a student's phone table."""
    result = delete_student_phone(student_id, phone_no)
    return jsonify({
        "status": "success",
        "message": result["message"]
    }), 200

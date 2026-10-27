from flask import request, jsonify
from . import semester_result_bp
from services import (
    create_semester_result,
    get_semester_result,
    list_semester_results,
    update_semester_result,
    delete_semester_result,
)


@semester_result_bp.route("", methods=["POST"])
def api_create_semester_result():
    """Records an official verified semester result for a student."""
    payload = request.get_json() or {}
    result = create_semester_result(payload)
    return jsonify({
        "status": "success",
        "message": "Semester result recorded successfully",
        "data": result
    }), 201


@semester_result_bp.route("", methods=["GET"])
def api_list_semester_results():
    """Lists, filters, and searches verified semester results."""
    student_id = request.args.get("student_id", type=int)
    semester = request.args.get("semester", type=int)
    year = request.args.get("year", type=int)

    results = list_semester_results(
        student_id=student_id,
        semester=semester,
        year=year,
    )
    return jsonify({
        "status": "success",
        "total": len(results),
        "data": results
    }), 200


@semester_result_bp.route("/<int:result_id>", methods=["GET"])
def api_get_semester_result(result_id: int):
    """Retrieves a single semester result."""
    result = get_semester_result(result_id)
    return jsonify({
        "status": "success",
        "data": result
    }), 200


@semester_result_bp.route("/<int:result_id>", methods=["PUT"])
def api_update_semester_result(result_id: int):
    """Updates an official semester result."""
    payload = request.get_json() or {}
    result = update_semester_result(result_id, payload)
    return jsonify({
        "status": "success",
        "message": "Semester result updated successfully",
        "data": result
    }), 200


@semester_result_bp.route("/<int:result_id>", methods=["DELETE"])
def api_delete_semester_result(result_id: int):
    """Deletes an official semester result."""
    result = delete_semester_result(result_id)
    return jsonify({
        "status": "success",
        "message": result["message"],
        "deleted_result_id": result["deleted_result_id"]
    }), 200

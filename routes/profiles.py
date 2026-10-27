from flask import request, jsonify
from . import profile_bp
from services import (
    create_profile,
    get_profile,
    list_profiles,
    update_profile,
    delete_profile,
)


@profile_bp.route("", methods=["POST"])
def api_create_profile():
    """Creates a new student profile entry (project, hackathon, certification, skill, coding profile)."""
    payload = request.get_json() or {}
    profile = create_profile(payload)
    return jsonify({
        "status": "success",
        "message": "Student profile created successfully",
        "data": profile
    }), 201


@profile_bp.route("", methods=["GET"])
def api_list_profiles():
    """Lists, searches, and filters student profile differentiators."""
    student_id = request.args.get("student_id", type=int)
    profile_type = request.args.get("profile_type")
    year = request.args.get("year", type=int)
    search = request.args.get("search")

    profiles = list_profiles(
        student_id=student_id,
        profile_type=profile_type,
        year=year,
        search=search,
    )
    return jsonify({
        "status": "success",
        "total": len(profiles),
        "data": profiles
    }), 200


@profile_bp.route("/<int:profile_id>", methods=["GET"])
def api_get_profile(profile_id: int):
    """Retrieves a specific student profile by ID."""
    profile = get_profile(profile_id)
    return jsonify({
        "status": "success",
        "data": profile
    }), 200


@profile_bp.route("/<int:profile_id>", methods=["PUT"])
def api_update_profile(profile_id: int):
    """Updates a student profile entry."""
    payload = request.get_json() or {}
    profile = update_profile(profile_id, payload)
    return jsonify({
        "status": "success",
        "message": "Profile updated successfully",
        "data": profile
    }), 200


@profile_bp.route("/<int:profile_id>", methods=["DELETE"])
def api_delete_profile(profile_id: int):
    """Deletes a student profile."""
    result = delete_profile(profile_id)
    return jsonify({
        "status": "success",
        "message": result["message"],
        "deleted_profile_id": result["deleted_profile_id"]
    }), 200

from flask import request, jsonify
from . import drive_bp
from services import (
    create_drive,
    get_drive,
    list_drives,
    update_drive,
    delete_drive,
)


@drive_bp.route("", methods=["POST"])
def api_create_drive():
    """Creates a recruitment drive."""
    payload = request.get_json() or {}
    drive = create_drive(payload)
    return jsonify({
        "status": "success",
        "message": "Recruitment drive created successfully",
        "data": drive
    }), 201


@drive_bp.route("", methods=["GET"])
def api_list_drives():
    """Lists, filters, and searches recruitment drives."""
    company_id = request.args.get("company_id", type=int)
    drive_year = request.args.get("drive_year", type=int)
    drive_type = request.args.get("drive_type")
    season = request.args.get("season")

    drives = list_drives(
        company_id=company_id,
        drive_year=drive_year,
        drive_type=drive_type,
        season=season,
    )
    return jsonify({
        "status": "success",
        "total": len(drives),
        "data": drives
    }), 200


@drive_bp.route("/<int:drive_id>", methods=["GET"])
def api_get_drive(drive_id: int):
    """Retrieves drive details with registered opportunities."""
    drive = get_drive(drive_id)
    return jsonify({
        "status": "success",
        "data": drive
    }), 200


@drive_bp.route("/<int:drive_id>", methods=["PUT"])
def api_update_drive(drive_id: int):
    """Updates recruitment drive schedule and type."""
    payload = request.get_json() or {}
    drive = update_drive(drive_id, payload)
    return jsonify({
        "status": "success",
        "message": "Recruitment drive updated successfully",
        "data": drive
    }), 200


@drive_bp.route("/<int:drive_id>", methods=["DELETE"])
def api_delete_drive(drive_id: int):
    """Safely deletes a recruitment drive; blocks if bound to active career offers."""
    result = delete_drive(drive_id)
    return jsonify({
        "status": "success",
        "message": result["message"],
        "deleted_drive_id": result["deleted_drive_id"]
    }), 200

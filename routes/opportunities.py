from flask import request, jsonify
from . import opportunity_bp
from services import (
    create_opportunity,
    get_opportunity,
    list_opportunities,
    update_opportunity,
    delete_opportunity,
)


@opportunity_bp.route("", methods=["POST"])
def api_create_opportunity():
    """Creates an opportunity along with eligibility criteria and multiple branches inside a transaction."""
    payload = request.get_json() or {}
    opportunity = create_opportunity(payload)
    return jsonify({
        "status": "success",
        "message": "Opportunity created successfully with eligibility and branches",
        "data": opportunity
    }), 201


@opportunity_bp.route("", methods=["GET"])
def api_list_opportunities():
    """Lists, searches, and filters recruitment opportunities."""
    drive_id = request.args.get("drive_id", type=int)
    opportunity_type = request.args.get("opportunity_type")
    min_package = request.args.get("min_package", type=float)
    branch = request.args.get("branch")
    search = request.args.get("search")

    opportunities = list_opportunities(
        drive_id=drive_id,
        opportunity_type=opportunity_type,
        min_package=min_package,
        branch=branch,
        search=search,
    )
    return jsonify({
        "status": "success",
        "total": len(opportunities),
        "data": opportunities
    }), 200


@opportunity_bp.route("/<int:opportunity_id>", methods=["GET"])
def api_get_opportunity(opportunity_id: int):
    """Retrieves opportunity details with eligibility, multiple branches, and selection rounds."""
    opportunity = get_opportunity(opportunity_id)
    return jsonify({
        "status": "success",
        "data": opportunity
    }), 200


@opportunity_bp.route("/<int:opportunity_id>", methods=["PUT"])
def api_update_opportunity(opportunity_id: int):
    """Updates opportunity, eligibility criteria, and eligible branches atomically in a transaction."""
    payload = request.get_json() or {}
    opportunity = update_opportunity(opportunity_id, payload)
    return jsonify({
        "status": "success",
        "message": "Opportunity and eligibility updated successfully",
        "data": opportunity
    }), 200


@opportunity_bp.route("/<int:opportunity_id>", methods=["DELETE"])
def api_delete_opportunity(opportunity_id: int):
    """Safely deletes an opportunity; blocks if bound to student placement/internship records."""
    result = delete_opportunity(opportunity_id)
    return jsonify({
        "status": "success",
        "message": result["message"],
        "deleted_opportunity_id": result["deleted_opportunity_id"]
    }), 200

from flask import request, jsonify
from . import placement_bp
from services import (
    create_placement_offer,
    get_placement_offer,
    list_placement_offers,
    update_offer_status,
    update_placement_offer,
    delete_placement_offer,
    get_students_with_multiple_offers,
    get_offer_distribution_summary,
)


@placement_bp.route("", methods=["POST"])
def api_create_placement():
    """Records a new placement offer, enforcing duplicate blocking, single-acceptance, and opportunity type rules."""
    payload = request.get_json() or {}
    offer = create_placement_offer(payload)
    return jsonify({
        "status": "success",
        "message": "Placement offer successfully recorded",
        "data": offer
    }), 201


@placement_bp.route("", methods=["GET"])
def api_list_placements():
    """Lists, searches, and filters placement offers."""
    student_id = request.args.get("student_id", type=int)
    company_id = request.args.get("company_id", type=int)
    opportunity_id = request.args.get("opportunity_id", type=int)
    placement_year = request.args.get("placement_year", type=int)
    offer_status = request.args.get("offer_status")
    placement_type = request.args.get("placement_type")
    is_ppo = request.args.get("is_ppo")
    joined = request.args.get("joined")
    min_package = request.args.get("min_package", type=float)
    search = request.args.get("search")
    limit = request.args.get("limit", default=50, type=int)
    offset = request.args.get("offset", default=0, type=int)

    result = list_placement_offers(
        student_id=student_id,
        company_id=company_id,
        opportunity_id=opportunity_id,
        placement_year=placement_year,
        offer_status=offer_status,
        placement_type=placement_type,
        is_ppo=is_ppo,
        joined=joined,
        min_package=min_package,
        search=search,
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


@placement_bp.route("/<int:placement_id>", methods=["GET"])
def api_get_placement(placement_id: int):
    """Retrieves single placement offer with related student, company, and evaluated skills."""
    offer = get_placement_offer(placement_id)
    return jsonify({
        "status": "success",
        "data": offer
    }), 200


@placement_bp.route("/<int:placement_id>/status", methods=["PATCH", "PUT"])
def api_update_offer_status(placement_id: int):
    """Updates offer status (Offered -> Accepted / Declined / Joined) enforcing the single-acceptance rule."""
    payload = request.get_json() or {}
    new_status = payload.get("Offer_Status") or payload.get("status")
    joined = payload.get("Joined") or payload.get("joined")
    updated_offer = update_offer_status(placement_id, new_status, joined)
    return jsonify({
        "status": "success",
        "message": f"Offer status successfully updated to '{updated_offer['Offer_Status']}'",
        "data": updated_offer
    }), 200


@placement_bp.route("/<int:placement_id>", methods=["PUT"])
def api_update_placement(placement_id: int):
    """Full update of placement offer fields."""
    payload = request.get_json() or {}
    updated_offer = update_placement_offer(placement_id, payload)
    return jsonify({
        "status": "success",
        "message": "Placement offer successfully updated",
        "data": updated_offer
    }), 200


@placement_bp.route("/<int:placement_id>", methods=["DELETE"])
def api_delete_placement(placement_id: int):
    """Deletes a placement offer."""
    result = delete_placement_offer(placement_id)
    return jsonify({
        "status": "success",
        "message": result["message"],
        "deleted_placement_id": result["deleted_placement_id"]
    }), 200


# ==============================================================================
# Analytical Routes for Students with Several Offers
# ==============================================================================

@placement_bp.route("/analytics/multiple-offers", methods=["GET"])
def api_students_with_multiple_offers():
    """Returns all students holding multiple (2 or more) placement offers."""
    min_offers = request.args.get("min_offers", default=2, type=int)
    students = get_students_with_multiple_offers(min_offers=min_offers)
    return jsonify({
        "status": "success",
        "total_students_with_multiple_offers": len(students),
        "data": students
    }), 200


@placement_bp.route("/analytics/distribution", methods=["GET"])
def api_offer_distribution():
    """Returns distribution summary: students with 0, 1, or multiple placement offers."""
    summary = get_offer_distribution_summary()
    return jsonify({
        "status": "success",
        "data": summary
    }), 200

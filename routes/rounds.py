from flask import request, jsonify
from . import round_bp
from services import (
    create_round,
    get_round,
    list_rounds,
    update_round,
    delete_round,
)


@round_bp.route("", methods=["POST"])
def api_create_round():
    """Creates a recruitment round for an opportunity."""
    payload = request.get_json() or {}
    round_item = create_round(payload)
    return jsonify({
        "status": "success",
        "message": "Selection round created successfully",
        "data": round_item
    }), 201


@round_bp.route("", methods=["GET"])
def api_list_rounds():
    """Lists selection rounds, optionally filtered by opportunity."""
    opportunity_id = request.args.get("opportunity_id", type=int)
    rounds = list_rounds(opportunity_id=opportunity_id)
    return jsonify({
        "status": "success",
        "total": len(rounds),
        "data": rounds
    }), 200


@round_bp.route("/<int:round_id>", methods=["GET"])
def api_get_round(round_id: int):
    """Retrieves round details."""
    round_item = get_round(round_id)
    return jsonify({
        "status": "success",
        "data": round_item
    }), 200


@round_bp.route("/<int:round_id>", methods=["PUT"])
def api_update_round(round_id: int):
    """Updates selection round number, type, or description."""
    payload = request.get_json() or {}
    round_item = update_round(round_id, payload)
    return jsonify({
        "status": "success",
        "message": "Selection round updated successfully",
        "data": round_item
    }), 200


@round_bp.route("/<int:round_id>", methods=["DELETE"])
def api_delete_round(round_id: int):
    """Deletes a selection round."""
    result = delete_round(round_id)
    return jsonify({
        "status": "success",
        "message": result["message"],
        "deleted_round_id": result["deleted_round_id"]
    }), 200

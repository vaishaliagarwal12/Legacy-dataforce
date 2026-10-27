from flask import request, jsonify
from . import company_bp
from services import (
    create_company,
    get_company,
    list_companies,
    update_company,
    delete_company,
)


@company_bp.route("", methods=["POST"])
def api_create_company():
    """Creates a recruiting organization."""
    payload = request.get_json() or {}
    company = create_company(payload)
    return jsonify({
        "status": "success",
        "message": "Company created successfully",
        "data": company
    }), 201


@company_bp.route("", methods=["GET"])
def api_list_companies():
    """Lists, searches, and filters recruiting companies."""
    search = request.args.get("search")
    company_type = request.args.get("company_type")
    industry = request.args.get("industry")
    location = request.args.get("location")

    companies = list_companies(
        search=search,
        company_type=company_type,
        industry=industry,
        location=location,
    )
    return jsonify({
        "status": "success",
        "total": len(companies),
        "data": companies
    }), 200


@company_bp.route("/<int:company_id>", methods=["GET"])
def api_get_company(company_id: int):
    """Company detail view listing all its recruitment drives and opportunities."""
    company = get_company(company_id)
    return jsonify({
        "status": "success",
        "data": company
    }), 200


@company_bp.route("/<int:company_id>", methods=["PUT"])
def api_update_company(company_id: int):
    """Updates company details."""
    payload = request.get_json() or {}
    company = update_company(company_id, payload)
    return jsonify({
        "status": "success",
        "message": "Company updated successfully",
        "data": company
    }), 200


@company_bp.route("/<int:company_id>", methods=["DELETE"])
def api_delete_company(company_id: int):
    """Safely deletes a company; blocks if drives or placements depend on it."""
    result = delete_company(company_id)
    return jsonify({
        "status": "success",
        "message": result["message"],
        "deleted_company_id": result["deleted_company_id"]
    }), 200

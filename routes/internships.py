from flask import request, jsonify
from . import internship_bp
from services import (
    create_internship,
    get_internship,
    list_internships,
    update_internship,
    delete_internship,
    list_requirements,
    get_requirement,
    get_mandatory_internships_with_prerequisite_sgpa,
    get_students_missing_mandatory_internships,
    check_internship_eligibility,
    get_branch_internship_statistics,
    get_batch_compliance_reports,
    get_internship_dashboard_analytics,
    get_pending_internship_reports,
)


@internship_bp.route("", methods=["POST"])
def api_create_internship():
    """Records an internship, enforcing mandatory requirement linkages and additional isolation."""
    payload = request.get_json() or {}
    internship = create_internship(payload)
    return jsonify({
        "status": "success",
        "message": "Internship successfully recorded",
        "data": internship
    }), 201


@internship_bp.route("", methods=["GET"])
def api_list_internships():
    """Lists, filters, and searches student internships."""
    search = request.args.get("search") or request.args.get("q")
    student_id = request.args.get("student_id", type=int)
    company_id = request.args.get("company_id", type=int)
    branch = request.args.get("branch")
    batch_year = request.args.get("batch_year", type=int)
    internship_type = request.args.get("internship_type")
    internship_no = request.args.get("internship_no", type=int)
    status = request.args.get("status")
    report_grade = request.args.get("report_grade")
    report_sem = request.args.get("report_semester", type=int)
    sort_by = request.args.get("sort_by", "student_id")
    sort_dir = request.args.get("sort_dir", "asc")
    page = request.args.get("page", type=int)
    per_page = request.args.get("per_page", type=int)

    if page is not None and per_page is not None:
        res = list_internships(
            search=search,
            student_id=student_id,
            company_id=company_id,
            branch=branch,
            batch_year=batch_year,
            internship_type=internship_type,
            internship_no=internship_no,
            status=status,
            report_grade=report_grade,
            report_semester=report_sem,
            sort_by=sort_by,
            sort_dir=sort_dir,
            page=page,
            per_page=per_page,
            as_dict=True,
        )
        return jsonify({
            "status": "success",
            "total": res["total"],
            "pagination": res["pagination"],
            "data": res["results"]
        }), 200

    internships = list_internships(
        search=search,
        student_id=student_id,
        company_id=company_id,
        branch=branch,
        batch_year=batch_year,
        internship_type=internship_type,
        internship_no=internship_no,
        status=status,
        report_grade=report_grade,
        report_semester=report_sem,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return jsonify({
        "status": "success",
        "total": len(internships),
        "data": internships
    }), 200


@internship_bp.route("/<int:internship_id>", methods=["GET"])
def api_get_internship(internship_id: int):
    """Retrieves full internship details including dynamically joined prerequisite semester SGPA."""
    internship = get_internship(internship_id)
    return jsonify({
        "status": "success",
        "data": internship
    }), 200


@internship_bp.route("/<int:internship_id>", methods=["PUT"])
def api_update_internship(internship_id: int):
    """Updates internship attributes with constraint validation."""
    payload = request.get_json() or {}
    internship = update_internship(internship_id, payload)
    return jsonify({
        "status": "success",
        "message": "Internship successfully updated",
        "data": internship
    }), 200


@internship_bp.route("/<int:internship_id>", methods=["DELETE"])
def api_delete_internship(internship_id: int):
    """Deletes an internship record."""
    result = delete_internship(internship_id)
    return jsonify({
        "status": "success",
        "message": result["message"],
        "deleted_internship_id": result["deleted_internship_id"]
    }), 200


# ==============================================================================
# Academic Policy Requirements Routes
# ==============================================================================

@internship_bp.route("/requirements", methods=["GET"])
def api_list_requirements():
    """Lists the official mandatory internship requirements."""
    requirements = list_requirements()
    return jsonify({
        "status": "success",
        "total": len(requirements),
        "data": requirements
    }), 200


@internship_bp.route("/requirements/<int:req_id>", methods=["GET"])
def api_get_requirement(req_id: int):
    """Retrieves an official internship requirement by ID."""
    req = get_requirement(req_id)
    return jsonify({
        "status": "success",
        "data": req
    }), 200


# ==============================================================================
# Analytical Routes: Prerequisite SGPA Joins & Missing Mandatory Compliance
# ==============================================================================

@internship_bp.route("/analytics/prerequisite-sgpa", methods=["GET"])
def api_prerequisite_sgpa_join():
    """Demonstrates 3NF normalization: dynamically fetches Sem 3 SGPA (Internship 1)
    and Sem 5 SGPA (Internship 2) by joining internship -> requirement -> semester result
    without redundant SGPA storage.
    """
    records = get_mandatory_internships_with_prerequisite_sgpa()
    return jsonify({
        "status": "success",
        "description": "Prerequisite SGPA fetched dynamically via INTERNSHIP -> INTERNSHIP_REQUIREMENT -> SEMESTER_RESULT (Zero redundancy)",
        "total": len(records),
        "data": records
    }), 200


@internship_bp.route("/analytics/missing-mandatory", methods=["GET"])
def api_missing_mandatory_internships():
    """Identifies students who are missing Mandatory Internship 1, Mandatory Internship 2, or both."""
    target_no = request.args.get("internship_no", type=int)
    branch = request.args.get("branch")
    batch_year = request.args.get("batch_year", type=int)
    missing_students = get_students_missing_mandatory_internships(
        target_internship_no=target_no,
        branch=branch,
        batch_year=batch_year,
    )
    return jsonify({
        "status": "success",
        "target_internship_evaluated": f"Internship #{target_no}" if target_no else "All Mandatory (1 & 2)",
        "total_missing_students": len(missing_students),
        "data": missing_students
    }), 200


@internship_bp.route("/analytics/dashboard", methods=["GET"])
def api_internship_dashboard_analytics():
    """Returns aggregated executive analytics for the Internship Management Dashboard."""
    analytics = get_internship_dashboard_analytics()
    return jsonify({
        "status": "success",
        "data": analytics
    }), 200


@internship_bp.route("/analytics/branch-statistics", methods=["GET"])
def api_branch_internship_statistics():
    """Returns branch-wise internship completion statistics."""
    stats = get_branch_internship_statistics()
    return jsonify({
        "status": "success",
        "total_branches": len(stats),
        "data": stats
    }), 200


@internship_bp.route("/analytics/batch-compliance", methods=["GET"])
def api_batch_compliance_reports():
    """Returns batch-wise internship compliance reports."""
    reports = get_batch_compliance_reports()
    return jsonify({
        "status": "success",
        "total_batches": len(reports),
        "data": reports
    }), 200


@internship_bp.route("/analytics/pending-reports", methods=["GET"])
def api_pending_internship_reports():
    """Returns internships with pending report submissions or pending grades."""
    pending = get_pending_internship_reports()
    return jsonify({
        "status": "success",
        "total_pending": len(pending),
        "data": pending
    }), 200


@internship_bp.route("/check-eligibility", methods=["GET"])
def api_check_internship_eligibility():
    """Evaluates student academic eligibility for an internship using actual SEMESTER_RESULT records."""
    student_id = request.args.get("student_id", type=int)
    internship_no = request.args.get("internship_no", default=1, type=int)
    min_sgpa = request.args.get("min_sgpa", default=6.00, type=float)

    if not student_id:
        return jsonify({"status": "error", "message": "Query parameter 'student_id' is required."}), 400

    result = check_internship_eligibility(student_id, internship_no, min_sgpa)
    return jsonify({
        "status": "success",
        "data": result
    }), 200

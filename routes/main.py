import io
import csv
import logging
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    Response,
)
from . import main_bp
from services import (
    check_system_health,
    ValidationError,
    NotFoundError,
    ConflictError,
    ProtectedDeleteError,
    # Dashboard & Reports
    get_dashboard_stats,
    get_yearwise_placement_chart_data,
    get_branchwise_analytics_chart_data,
    get_offer_status_chart_data,
    get_internship_breakdown_chart_data,
    get_comprehensive_report_data,
    # Students & Profiles
    list_students,
    get_student,
    create_student,
    update_student,
    delete_student,
    list_student_phones,
    add_student_phone,
    delete_student_phone,
    list_profiles,
    # Academic & Courses
    list_semester_results,
    list_registrations,
    # Companies & Drives
    list_companies,
    get_company,
    create_company,
    update_company,
    delete_company,
    list_drives,
    get_drive,
    list_opportunities,
    # Internships
    list_internships,
    create_internship,
    delete_internship,
    list_requirements,
    get_mandatory_internships_with_prerequisite_sgpa,
    get_students_missing_mandatory_internships,
    # Placements
    list_placement_offers,
    create_placement_offer,
    update_offer_status,
    delete_placement_offer,
    get_students_with_multiple_offers,
)

logger = logging.getLogger(__name__)


# ==============================================================================
# 1. Executive Dashboard (Home)
# ==============================================================================

@main_bp.route("/", methods=["GET"])
def index():
    """Renders the executive dashboard with KPI cards, Chart.js visual charts, and recent activity."""
    health_info, status_code = check_system_health()
    stats = get_dashboard_stats()
    chart_yearwise = get_yearwise_placement_chart_data()
    chart_branchwise = get_branchwise_analytics_chart_data()
    chart_status = get_offer_status_chart_data()
    chart_internships = get_internship_breakdown_chart_data()

    offers_res = list_placement_offers(limit=6)
    recent_offers = offers_res.get("results", []) if isinstance(offers_res, dict) else offers_res

    return render_template(
        "dashboard.html",
        active_page="dashboard",
        health=health_info,
        status_code=status_code,
        stats=stats,
        chart_yearwise=chart_yearwise,
        chart_branchwise=chart_branchwise,
        chart_status=chart_status,
        chart_internships=chart_internships,
        recent_offers=recent_offers,
    )


# ==============================================================================
# 2. Student Directory, Detail & CRUD Views
# ==============================================================================

@main_bp.route("/students", methods=["GET"])
def students_list():
    """Displays searchable and filterable table of students."""
    search = request.args.get("search", "").strip() or None
    branch = request.args.get("branch", "").strip() or None
    min_cgpa = request.args.get("min_cgpa", "").strip() or None

    res = list_students(
        search=search,
        branch=branch,
        min_cgpa=float(min_cgpa) if min_cgpa else None,
        limit=100,
    )
    students = res.get("results", []) if isinstance(res, dict) else res

    return render_template(
        "students/index.html",
        active_page="students",
        students=students,
        search_query=search,
        selected_branch=branch,
        selected_min_cgpa=min_cgpa,
    )


@main_bp.route("/students/new", methods=["GET", "POST"])
def student_create():
    """Handles adding a new student to the institution directory."""
    if request.method == "POST":
        try:
            payload = {
                "Roll_No": request.form.get("Roll_No", "").strip().upper(),
                "First_Name": request.form.get("First_Name", "").strip(),
                "Last_Name": request.form.get("Last_Name", "").strip() or None,
                "Email": request.form.get("Email", "").strip().lower(),
                "Branch": request.form.get("Branch", "").strip(),
                "Batch_Year": int(request.form.get("Batch_Year", 2024)),
                "Section": request.form.get("Section", "A").strip() or None,
                "CGPA": float(request.form.get("CGPA", 0.0)),
                "Backlogs": int(request.form.get("Backlogs", 0)),
                "Resume_Link": request.form.get("Resume_Link", "").strip() or None,
            }
            res = create_student(payload)
            flash(f"Student {payload['First_Name']} {payload['Last_Name'] or ''} ({payload['Roll_No']}) registered successfully!", "success")
            return redirect(f"/students/{res['Student_ID']}")
        except (ValidationError, ConflictError) as err:
            flash(err.message, "danger")
            return render_template("students/form.html", active_page="students", mode="create", student=request.form)

    return render_template("students/form.html", active_page="students", mode="create", student=None)


@main_bp.route("/students/<int:student_id>", methods=["GET"])
def student_detail(student_id: int):
    """Displays comprehensive student profile including academic results, placements, and internships."""
    try:
        student = get_student(student_id)
    except NotFoundError:
        flash(f"Student with ID {student_id} not found.", "warning")
        return redirect("/students")

    phones = list_student_phones(student_id)
    profiles = list_profiles(student_id=student_id)
    semester_results = list_semester_results(student_id=student_id)
    registrations = list_registrations(student_id=student_id)

    placements_res = list_placement_offers(student_id=student_id)
    placements = placements_res.get("results", []) if isinstance(placements_res, dict) else placements_res

    internships = list_internships(student_id=student_id)

    return render_template(
        "students/detail.html",
        active_page="students",
        student=student,
        phones=phones,
        profiles=profiles,
        semester_results=semester_results,
        registrations=registrations,
        placements=placements,
        internships=internships,
    )


@main_bp.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
def student_edit(student_id: int):
    """Handles updating student details."""
    try:
        student = get_student(student_id)
    except NotFoundError:
        flash(f"Student with ID {student_id} not found.", "warning")
        return redirect("/students")

    if request.method == "POST":
        try:
            payload = {
                "First_Name": request.form.get("First_Name", "").strip(),
                "Last_Name": request.form.get("Last_Name", "").strip() or None,
                "Email": request.form.get("Email", "").strip().lower(),
                "Branch": request.form.get("Branch", "").strip(),
                "Batch_Year": int(request.form.get("Batch_Year", student["Batch_Year"])),
                "Section": request.form.get("Section", "A").strip() or None,
                "CGPA": float(request.form.get("CGPA", student["CGPA"])),
                "Backlogs": int(request.form.get("Backlogs", 0)),
                "Resume_Link": request.form.get("Resume_Link", "").strip() or None,
            }
            update_student(student_id, payload)
            flash(f"Student profile for {student['Roll_No']} updated successfully!", "success")
            return redirect(f"/students/{student_id}")
        except (ValidationError, ConflictError) as err:
            flash(err.message, "danger")
            return render_template("students/form.html", active_page="students", mode="edit", student=request.form)

    return render_template("students/form.html", active_page="students", mode="edit", student=student)


@main_bp.route("/students/<int:student_id>/delete", methods=["POST"])
def student_delete(student_id: int):
    """Safely deletes student, respecting institutional career history protection."""
    try:
        res = delete_student(student_id)
        flash(res["message"], "success")
    except ProtectedDeleteError as err:
        flash(f"Cannot Delete Student: {err.message}", "danger")
    except (NotFoundError, ConflictError) as err:
        flash(err.message, "danger")
    return redirect("/students")


@main_bp.route("/students/<int:student_id>/phones", methods=["POST"])
def student_phone_add(student_id: int):
    """Adds a phone number to a student in the dedicated phone table."""
    phone_number = request.form.get("phone_number", "").strip()
    try:
        add_student_phone(student_id, phone_number)
        flash(f"Added phone number {phone_number} successfully.", "success")
    except (ValidationError, ConflictError) as err:
        flash(err.message, "danger")
    return redirect(f"/students/{student_id}")


@main_bp.route("/students/<int:student_id>/phones/<string:phone_no>/delete", methods=["POST"])
def student_phone_delete(student_id: int, phone_no: str):
    """Deletes a phone number from the separate phone table."""
    try:
        delete_student_phone(student_id, phone_no)
        flash("Phone number removed successfully.", "success")
    except NotFoundError as err:
        flash(err.message, "danger")
    return redirect(f"/students/{student_id}")


# ==============================================================================
# 3. Corporate Partners & Recruitment Drives Views
# ==============================================================================

@main_bp.route("/companies", methods=["GET"])
def companies_list():
    """Displays searchable and filterable company partners."""
    search = request.args.get("search", "").strip() or None
    tier = request.args.get("tier", "").strip() or None

    companies = list_companies(search=search, company_type=tier)
    return render_template(
        "companies/index.html",
        active_page="companies",
        companies=companies,
        search_query=search,
        selected_tier=tier,
    )


@main_bp.route("/companies/new", methods=["GET", "POST"])
def company_create():
    """Registers a new corporate partner."""
    if request.method == "POST":
        try:
            payload = {
                "Company_Name": request.form.get("Company_Name", "").strip(),
                "Company_Type": request.form.get("Company_Type", "Product").strip(),
                "Industry": request.form.get("Industry", "").strip(),
                "Location": request.form.get("Location", "").strip() or None,
                "Website": request.form.get("Website", "").strip() or None,
            }
            res = create_company(payload)
            flash(f"Company '{payload['Company_Name']}' registered successfully!", "success")
            return redirect(f"/companies/{res['Company_ID']}")
        except (ValidationError, ConflictError) as err:
            flash(err.message, "danger")
            return render_template("companies/form.html", active_page="companies", mode="create", company=request.form)

    return render_template("companies/form.html", active_page="companies", mode="create", company=None)


@main_bp.route("/companies/<int:company_id>", methods=["GET"])
def company_detail(company_id: int):
    """Displays company profile, recruitment drives, opportunities, and recruited students."""
    try:
        company = get_company(company_id)
    except NotFoundError:
        flash(f"Company with ID {company_id} not found.", "warning")
        return redirect("/companies")

    drives = list_drives(company_id=company_id)
    drive_opportunities = {}
    for d in drives:
        full_drive = get_drive(d["Drive_ID"])
        drive_opportunities[d["Drive_ID"]] = full_drive.get("Opportunities", [])

    placements_res = list_placement_offers(company_id=company_id)
    placements = placements_res.get("results", []) if isinstance(placements_res, dict) else placements_res

    return render_template(
        "companies/detail.html",
        active_page="companies",
        company=company,
        drives=drives,
        drive_opportunities=drive_opportunities,
        placements=placements,
    )


@main_bp.route("/companies/<int:company_id>/edit", methods=["GET", "POST"])
def company_edit(company_id: int):
    """Handles updating company details."""
    try:
        company = get_company(company_id)
    except NotFoundError:
        flash(f"Company with ID {company_id} not found.", "warning")
        return redirect("/companies")

    if request.method == "POST":
        try:
            payload = {
                "Company_Name": request.form.get("Company_Name", "").strip(),
                "Company_Type": request.form.get("Company_Type", company["Company_Type"]).strip(),
                "Industry": request.form.get("Industry", "").strip(),
                "Location": request.form.get("Location", "").strip() or None,
                "Website": request.form.get("Website", "").strip() or None,
            }
            update_company(company_id, payload)
            flash(f"Company '{payload['Company_Name']}' updated successfully!", "success")
            return redirect(f"/companies/{company_id}")
        except (ValidationError, ConflictError) as err:
            flash(err.message, "danger")
            return render_template("companies/form.html", active_page="companies", mode="edit", company=request.form)

    return render_template("companies/form.html", active_page="companies", mode="edit", company=company)


@main_bp.route("/companies/<int:company_id>/delete", methods=["POST"])
def company_delete(company_id: int):
    """Handles company deletion with relationship integrity protection."""
    try:
        res = delete_company(company_id)
        flash(res["message"], "success")
    except ConflictError as err:
        flash(f"Cannot Delete Company: {err.message}", "danger")
    except NotFoundError as err:
        flash(err.message, "danger")
    return redirect("/companies")


# ==============================================================================
# 4. Internships (Mandatory vs Additional & Prerequisite SGPA) Views
# ==============================================================================

@main_bp.route("/internships", methods=["GET"])
def internships_list():
    """Displays internships with tabs for Mandatory (prerequisite SGPA dynamic join), Additional, and Missing Audit."""
    active_tab = request.args.get("type", "All").strip()
    if active_tab not in ("All", "Mandatory", "Additional", "Missing"):
        active_tab = "All"

    all_internships = list_internships()
    mandatory_internships = get_mandatory_internships_with_prerequisite_sgpa()
    additional_internships = [i for i in all_internships if i.get("Internship_Type") == "Additional"]
    missing_students = get_students_missing_mandatory_internships()

    return render_template(
        "internships/index.html",
        active_page="internships",
        active_tab=active_tab,
        all_internships=all_internships,
        mandatory_internships=mandatory_internships,
        additional_internships=additional_internships,
        missing_students=missing_students,
    )


@main_bp.route("/internships/new", methods=["GET", "POST"])
def internship_create():
    """Handles recording a student internship enforcing academic policy constraints."""
    if request.method == "POST":
        try:
            itype = request.form.get("Internship_Type", "Mandatory").strip()
            req_id_raw = request.form.get("Requirement_ID")
            req_id = int(req_id_raw) if (itype == "Mandatory" and req_id_raw) else None

            payload = {
                "Student_ID": int(request.form.get("Student_ID")),
                "Company_ID": int(request.form.get("Company_ID")),
                "Internship_Type": itype,
                "Requirement_ID": req_id,
                "Internship_No": int(request.form.get("Internship_No", 1)),
                "Role": request.form.get("Role", "").strip(),
                "Start_Date": request.form.get("Start_Date", "").strip(),
                "End_Date": request.form.get("End_Date", "").strip(),
            }
            res = create_internship(payload)
            flash(f"Recorded {itype} Internship #{payload['Internship_No']} successfully!", "success")
            return redirect(f"/internships?type={itype}")
        except (ValidationError, ConflictError) as err:
            flash(err.message, "danger")

    students_res = list_students(limit=100)
    students = students_res.get("results", []) if isinstance(students_res, dict) else students_res
    companies = list_companies()
    requirements = list_requirements()
    preselected_student_id = request.args.get("student_id")

    return render_template(
        "internships/form.html",
        active_page="internships",
        students=students,
        companies=companies,
        requirements=requirements,
        preselected_student_id=preselected_student_id,
    )


@main_bp.route("/internships/<int:internship_id>/delete", methods=["POST"])
def internship_delete(internship_id: int):
    """Deletes an internship record."""
    try:
        res = delete_internship(internship_id)
        flash(res["message"], "success")
    except NotFoundError as err:
        flash(err.message, "danger")
    return redirect("/internships")


# ==============================================================================
# 5. Placements & Offer Management Views
# ==============================================================================

@main_bp.route("/placements", methods=["GET"])
def placements_list():
    """Displays placement offers with status filter, multi-offer performers view, and modal issuance."""
    view_type = request.args.get("view", "all")
    show_multi = (view_type == "multiple")

    search = request.args.get("search", "").strip() or None
    status = request.args.get("status", "").strip() or None

    offers_res = list_placement_offers(offer_status=status, search=search, limit=150)
    offers = offers_res.get("results", []) if isinstance(offers_res, dict) else offers_res

    multi_offer_students = get_students_with_multiple_offers(min_offers=2)

    students_res = list_students(limit=100)
    all_students = students_res.get("results", []) if isinstance(students_res, dict) else students_res
    all_companies = list_companies()
    all_opportunities = list_opportunities(opportunity_type="Placement")

    return render_template(
        "placements/index.html",
        active_page="placements",
        offers=offers,
        show_multi=show_multi,
        multi_offer_students=multi_offer_students,
        all_students=all_students,
        all_companies=all_companies,
        all_opportunities=all_opportunities,
        search_query=search,
        selected_status=status,
    )


@main_bp.route("/placements/new", methods=["POST"])
def placement_create():
    """Handles issuing a placement offer enforcing no duplicates and single-accepted offer rules."""
    try:
        opp_id = request.form.get("Opportunity_ID")
        payload = {
            "Student_ID": int(request.form.get("Student_ID")),
            "Company_ID": int(request.form.get("Company_ID")),
            "Opportunity_ID": int(opp_id) if opp_id else None,
            "Role": request.form.get("Role", "").strip(),
            "Package": float(request.form.get("Package", 0.0)),
            "Placement_Year": int(request.form.get("Placement_Year", 2024)),
            "Offer_Status": request.form.get("Offer_Status", "Offered").strip(),
            "Is_PPO": request.form.get("Is_PPO", "No").strip(),
        }
        res = create_placement_offer(payload)
        flash(f"Issued Placement Offer #{res['Placement_ID']} ({payload['Role']} - {payload['Package']} LPA) successfully!", "success")
    except (ValidationError, ConflictError) as err:
        flash(f"Offer Issue Rejected: {err.message}", "danger")

    return redirect("/placements")


@main_bp.route("/placements/<int:placement_id>/status", methods=["POST"])
def placement_status_update(placement_id: int):
    """Updates an offer's status (Accept, Decline, Joined), enforcing the single accepted offer constraint."""
    new_status = request.form.get("status", "").strip()
    try:
        update_offer_status(placement_id, new_status)
        flash(f"Placement Offer #{placement_id} status updated to '{new_status}' successfully!", "success")
    except ConflictError as err:
        flash(f"Status Transition Blocked: {err.message}", "danger")
    except (ValidationError, NotFoundError) as err:
        flash(err.message, "danger")

    return redirect("/placements")


@main_bp.route("/placements/<int:placement_id>/delete", methods=["POST"])
def placement_delete(placement_id: int):
    """Deletes a placement offer record."""
    try:
        res = delete_placement_offer(placement_id)
        flash(res["message"], "success")
    except NotFoundError as err:
        flash(err.message, "danger")
    return redirect("/placements")


# ==============================================================================
# 6. Reports & Multi-Filter Export Views
# ==============================================================================

@main_bp.route("/reports", methods=["GET"])
def reports_view():
    """Renders comprehensive institutional reports with multi-criteria filters."""
    filters = {
        "branch": request.args.get("branch", "").strip() or None,
        "placement_status": request.args.get("placement_status", "").strip() or None,
        "internship_status": request.args.get("internship_status", "").strip() or None,
        "min_cgpa": request.args.get("min_cgpa", "").strip() or None,
        "min_salary": request.args.get("min_salary", "").strip() or None,
    }

    report_data = get_comprehensive_report_data(filters)
    query_string = request.query_string.decode("utf-8")

    return render_template(
        "reports/index.html",
        active_page="reports",
        filters=filters,
        rows=report_data["rows"],
        summary=report_data["summary"],
        current_query_string=query_string,
    )


@main_bp.route("/reports/export", methods=["GET"])
def reports_export_csv():
    """Generates and streams a CSV export of the filtered cohort report."""
    filters = {
        "branch": request.args.get("branch", "").strip() or None,
        "placement_status": request.args.get("placement_status", "").strip() or None,
        "internship_status": request.args.get("internship_status", "").strip() or None,
        "min_cgpa": request.args.get("min_cgpa", "").strip() or None,
        "min_salary": request.args.get("min_salary", "").strip() or None,
    }

    report_data = get_comprehensive_report_data(filters)
    rows = report_data["rows"]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Roll No",
        "Student Name",
        "Email",
        "Branch",
        "Batch Year",
        "CGPA",
        "Total Placement Offers",
        "Placed Company",
        "Placed Package (LPA)",
        "Final Status",
        "Mandatory Internship 1 (Sem 3)",
        "Mandatory Internship 2 (Sem 5)",
        "Additional Internships Count",
    ])

    for r in rows:
        writer.writerow([
            r["Roll_No"],
            r["Full_Name"],
            r["Email"],
            r["Branch"],
            r["Batch_Year"],
            f"{r['CGPA']:.2f}",
            r["Total_Offers"],
            r["Placed_Company"] or "Unplaced",
            f"{r['Placed_Package']:.2f}" if r["Placed_Package"] else "N/A",
            r["Final_Status"] or "N/A",
            "Completed" if r["Has_Mandatory_1"] > 0 else "Missing",
            "Completed" if r["Has_Mandatory_2"] > 0 else "Missing",
            r["Additional_Internship_Count"],
        ])

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=placement_internship_report.csv"},
    )


# ==============================================================================
# 7. Analytics JSON Endpoints (Supporting Live Chart Queries)
# ==============================================================================

@main_bp.route("/api/analytics/dashboard", methods=["GET"])
def api_dashboard_stats():
    """Returns aggregated dashboard statistics JSON."""
    return jsonify({"status": "success", "data": get_dashboard_stats()}), 200


@main_bp.route("/api/analytics/charts/yearwise", methods=["GET"])
def api_chart_yearwise():
    """Returns year-wise placement trends JSON."""
    return jsonify({"status": "success", "data": get_yearwise_placement_chart_data()}), 200


@main_bp.route("/api/analytics/charts/branchwise", methods=["GET"])
def api_chart_branchwise():
    """Returns branch-wise distribution JSON."""
    return jsonify({"status": "success", "data": get_branchwise_analytics_chart_data()}), 200

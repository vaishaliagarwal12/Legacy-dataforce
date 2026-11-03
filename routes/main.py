import io
import csv
import logging
from typing import Optional
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    Response,
)
from db.connection import DatabaseError
from . import main_bp
from services import (
    check_system_health,
    ServiceError,
    ValidationError,
    NotFoundError,
    ConflictError,
    ProtectedDeleteError,
    # Dashboard & Reports
    get_dashboard_stats,
    get_yearwise_placement_chart_data,
    get_branchwise_analytics_chart_data,
    get_package_distribution_chart_data,
    get_placement_vs_internship_chart_data,
    get_internship_completion_chart_data,
    get_multiple_offers_chart_data,
    get_offer_status_chart_data,
    get_internship_breakdown_chart_data,
    get_dashboard_filter_options,
    get_comprehensive_dashboard_data,
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
    get_internship,
    create_internship,
    update_internship,
    delete_internship,
    list_requirements,
    get_mandatory_internships_with_prerequisite_sgpa,
    get_students_missing_mandatory_internships,
    check_internship_eligibility,
    get_branch_internship_statistics,
    get_batch_compliance_reports,
    get_internship_dashboard_analytics,
    get_pending_internship_reports,
    # Placements
    list_placement_offers,
    get_placement_offer,
    create_placement_offer,
    update_offer_status,
    update_placement_offer,
    delete_placement_offer,
    get_students_with_multiple_offers,
    get_placement_analytics,
    check_candidate_eligibility_for_opportunity,
    # SQL Reports & DBMS Queries
    list_saved_queries,
    get_saved_query,
    execute_saved_query,
    validate_custom_sql,
    execute_custom_query,
)

logger = logging.getLogger(__name__)

BRANCH_MAP = {
    "computer science": "CSE",
    "cse": "CSE",
    "electronics & comm": "ECE",
    "electronics & communication": "ECE",
    "electronics": "ECE",
    "ece": "ECE",
    "mechanical": "ME",
    "mechanical engineering": "ME",
    "me": "ME",
    "information tech": "IT",
    "information technology": "IT",
    "it": "IT",
    "civil": "Civil",
    "electrical": "Electrical",
}

COMPANY_TYPE_MAP = {
    "tier-1": "Product",
    "tier-2": "Service",
    "tier-3": "Startup",
    "product": "Product",
    "service": "Service",
    "startup": "Startup",
    "other": "Other",
}


def normalize_branch(val: Optional[str]) -> Optional[str]:
    """Normalizes department names or abbreviations to canonical database codes."""
    if not val:
        return None
    val_clean = val.strip()
    return BRANCH_MAP.get(val_clean.lower(), val_clean)


def normalize_company_type(val: Optional[str]) -> Optional[str]:
    """Normalizes company category filters."""
    if not val:
        return None
    val_clean = val.strip().lower()
    return COMPANY_TYPE_MAP.get(val_clean, val.strip())


def parse_float(val, field_name: str, min_val: float = None, max_val: float = None) -> float:
    """Safely converts string to float without unhandled ValueError crashes."""
    if val is None or str(val).strip() == "":
        raise ValidationError(f"Missing required numeric value for '{field_name}'")
    try:
        f = float(str(val).strip())
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid numeric input for '{field_name}'. Value must be a valid number.")
    if min_val is not None and f < min_val:
        raise ValidationError(f"{field_name} must be greater than or equal to {min_val}")
    if max_val is not None and f > max_val:
        raise ValidationError(f"{field_name} cannot exceed {max_val}")
    return f


def parse_int(val, field_name: str, min_val: int = None, max_val: int = None) -> int:
    """Safely converts string to int without unhandled ValueError crashes."""
    if val is None or str(val).strip() == "":
        raise ValidationError(f"Missing required integer value for '{field_name}'")
    try:
        i = int(str(val).strip())
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid integer input for '{field_name}'. Value must be a whole number.")
    if min_val is not None and i < min_val:
        raise ValidationError(f"{field_name} must be greater than or equal to {min_val}")
    if max_val is not None and i > max_val:
        raise ValidationError(f"{field_name} cannot exceed {max_val}")
    return i


def _safe_error_message(err: Exception, default_msg: str = "A database error occurred.") -> str:
    """Extract safe error message for user presentation, concealing raw database errors."""
    if isinstance(err, DatabaseError):
        logger.error("Database error in route handler: %s", err, exc_info=True)
        return default_msg
    if hasattr(err, "message") and err.message:
        return str(err.message)
    return default_msg


# ==============================================================================
# 1. Executive Dashboard (Home)
# ==============================================================================

@main_bp.route("/", methods=["GET"])
def index():
    """Renders the executive dashboard with KPI cards, Chart.js visual charts, and recent activity."""
    health_info, status_code = check_system_health()

    raw_batch = request.args.get("batch_year")
    raw_branch = request.args.get("branch", "").strip() or None
    raw_placement_year = request.args.get("placement_year")

    filters = {}
    if raw_batch and str(raw_batch).strip().lower() not in ("all", "none"):
        try:
            filters["batch_year"] = int(raw_batch)
        except (ValueError, TypeError):
            pass

    if raw_branch and raw_branch.lower() not in ("all", "none"):
        filters["branch"] = normalize_branch(raw_branch)

    if raw_placement_year and str(raw_placement_year).strip().lower() not in ("all", "none"):
        try:
            filters["placement_year"] = int(raw_placement_year)
        except (ValueError, TypeError):
            pass

    dash_data = get_comprehensive_dashboard_data(filters)
    stats = dash_data["stats"]
    kpi = dash_data["kpi"]
    charts = dash_data["charts"]
    filter_options = dash_data["filter_options"]

    offer_year = filters.get("placement_year") or filters.get("batch_year")
    offers_res = list_placement_offers(placement_year=offer_year, limit=8)
    recent_offers = offers_res.get("results", []) if isinstance(offers_res, dict) else offers_res

    return render_template(
        "dashboard.html",
        active_page="dashboard",
        health=health_info,
        status_code=status_code,
        stats=stats,
        kpi=kpi,
        charts=charts,
        filter_options=filter_options,
        active_filters=filters,
        # Direct chart bindings for template convenience & backward compatibility
        chart_branchwise=charts["branchwise"],
        chart_yearwise=charts["yearwise"],
        chart_package=charts["package_distribution"],
        chart_vs=charts["placement_vs_internship"],
        chart_completion=charts["internship_completion"],
        chart_multiple=charts["multiple_offers"],
        chart_status=charts["offer_status"],
        chart_internships=charts["internships_breakdown"],
        recent_offers=recent_offers,
    )


# ==============================================================================
# 2. Student Directory, Detail & CRUD Views
# ==============================================================================

@main_bp.route("/students", methods=["GET"])
def students_list():
    """Displays searchable, filterable, sortable, and paginated directory of students."""
    search = request.args.get("search", "").strip() or None
    raw_branch = request.args.get("branch", "").strip() or None
    branch = normalize_branch(raw_branch)
    raw_batch = request.args.get("batch_year")
    batch_year = None
    if raw_batch and str(raw_batch).strip().lower() not in ("all", "none"):
        try:
            batch_year = int(raw_batch)
        except (ValueError, TypeError):
            pass

    min_cgpa = request.args.get("min_cgpa", "").strip() or None
    parsed_min_cgpa = None
    if min_cgpa:
        try:
            parsed_min_cgpa = float(min_cgpa)
        except (ValueError, TypeError):
            pass

    max_cgpa = request.args.get("max_cgpa", "").strip() or None
    parsed_max_cgpa = None
    if max_cgpa:
        try:
            parsed_max_cgpa = float(max_cgpa)
        except (ValueError, TypeError):
            pass

    placement_status = request.args.get("placement_status", "").strip() or None
    sort_by = request.args.get("sort_by", "roll_no").strip()
    sort_dir = request.args.get("sort_dir", "asc").strip().lower()

    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    if per_page not in (10, 25, 50, 100):
        per_page = 10

    res = list_students(
        search=search,
        branch=branch,
        batch_year=batch_year,
        min_cgpa=parsed_min_cgpa,
        max_cgpa=parsed_max_cgpa,
        placement_status=placement_status,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        limit=per_page,
    )
    students = res.get("results", [])

    filter_options = get_dashboard_filter_options()

    active_filters = {
        "search": search or "",
        "branch": branch or raw_branch or "",
        "batch_year": batch_year or "",
        "min_cgpa": min_cgpa or "",
        "max_cgpa": max_cgpa or "",
        "placement_status": placement_status or "",
        "sort_by": sort_by,
        "sort_dir": sort_dir,
        "per_page": per_page,
    }

    return render_template(
        "students/index.html",
        active_page="students",
        students=students,
        pagination=res,
        filter_options=filter_options,
        active_filters=active_filters,
        # Backward compatibility bindings
        search_query=search,
        selected_branch=branch or raw_branch,
        selected_min_cgpa=min_cgpa,
    )


@main_bp.route("/students/export-csv", methods=["GET"])
@main_bp.route("/students/export", methods=["GET"])
def students_export_csv():
    """Generates and downloads a CSV export of filtered student records."""
    search = request.args.get("search", "").strip() or None
    raw_branch = request.args.get("branch", "").strip() or None
    branch = normalize_branch(raw_branch)
    raw_batch = request.args.get("batch_year")
    batch_year = None
    if raw_batch and str(raw_batch).strip().lower() not in ("all", "none"):
        try:
            batch_year = int(raw_batch)
        except (ValueError, TypeError):
            pass

    min_cgpa = request.args.get("min_cgpa", "").strip() or None
    parsed_min_cgpa = None
    if min_cgpa:
        try:
            parsed_min_cgpa = float(min_cgpa)
        except (ValueError, TypeError):
            pass

    max_cgpa = request.args.get("max_cgpa", "").strip() or None
    parsed_max_cgpa = None
    if max_cgpa:
        try:
            parsed_max_cgpa = float(max_cgpa)
        except (ValueError, TypeError):
            pass

    placement_status = request.args.get("placement_status", "").strip() or None
    sort_by = request.args.get("sort_by", "roll_no").strip()
    sort_dir = request.args.get("sort_dir", "asc").strip().lower()

    res = list_students(
        search=search,
        branch=branch,
        batch_year=batch_year,
        min_cgpa=parsed_min_cgpa,
        max_cgpa=parsed_max_cgpa,
        placement_status=placement_status,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=10000,
        offset=0,
    )
    students = res.get("results", [])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Roll No", "First Name", "Last Name", "Full Name", "Email",
        "Branch", "Batch Year", "Section", "CGPA", "Backlogs",
        "Phone Numbers", "Placement Status", "Placement Offers",
        "Placed Company", "Placed Package (LPA)", "Internships Count", "Resume Link"
    ])
    for s in students:
        phones = ", ".join(s.get("Phone_Numbers", [])) if isinstance(s.get("Phone_Numbers"), list) else str(s.get("Phone_Numbers") or "")
        writer.writerow([
            s.get("Roll_No"),
            s.get("First_Name"),
            s.get("Last_Name") or "",
            s.get("Full_Name") or f"{s.get('First_Name')} {s.get('Last_Name') or ''}".strip(),
            s.get("Email"),
            s.get("Branch"),
            s.get("Batch_Year"),
            s.get("Section") or "A",
            s.get("CGPA"),
            s.get("Backlogs", 0),
            phones,
            s.get("Placement_Status") or ("Placed" if s.get("Accepted_Offers", 0) > 0 else "Unplaced"),
            s.get("Placement_Offers", 0),
            s.get("Placed_Company") or "",
            s.get("Placed_Package") or "",
            s.get("Internships", 0),
            s.get("Resume_Link") or "",
        ])

    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=students_directory.csv"},
    )


@main_bp.route("/students/new", methods=["GET", "POST"])
def student_create():
    """Handles adding a new student to the institution directory."""
    if request.method == "POST":
        try:
            roll_no = request.form.get("Roll_No", "").strip().upper()
            first_name = request.form.get("First_Name", "").strip()
            cgpa = parse_float(request.form.get("CGPA"), "CGPA", 0.0, 10.0)
            backlogs = parse_int(request.form.get("Backlogs", 0), "Backlogs", 0)
            batch_year = parse_int(request.form.get("Batch_Year", 2024), "Batch Year", 2000, 2100)
            raw_branch = request.form.get("Branch", "")
            branch = normalize_branch(raw_branch)

            if not branch:
                raise ValidationError("Please select a valid academic branch.")

            payload = {
                "Roll_No": roll_no,
                "First_Name": first_name,
                "Last_Name": request.form.get("Last_Name", "").strip() or None,
                "Email": request.form.get("Email", "").strip().lower(),
                "Branch": branch,
                "Batch_Year": batch_year,
                "Section": request.form.get("Section", "A").strip() or None,
                "CGPA": cgpa,
                "Backlogs": backlogs,
                "Resume_Link": request.form.get("Resume_Link", "").strip() or None,
            }
            res = create_student(payload)
            flash(f"Student {payload['First_Name']} {payload['Last_Name'] or ''} ({payload['Roll_No']}) registered successfully!", "success")
            return redirect(f"/students/{res['Student_ID']}")
        except (ValidationError, ConflictError, DatabaseError, ServiceError) as err:
            err_msg = _safe_error_message(err)
            flash(f"Registration Error: {err_msg}", "danger")
            return render_template("students/form.html", active_page="students", mode="create", student=request.form)

    return render_template("students/form.html", active_page="students", mode="create", student=None)


@main_bp.route("/students/<int:student_id>", methods=["GET"])
def student_detail(student_id: int):
    """Displays comprehensive student profile across all 9 academic & career sections."""
    try:
        student = get_student(student_id)
    except NotFoundError:
        flash(f"Student with ID {student_id} not found.", "warning")
        return redirect("/students")

    phones = student.get("Phone_Numbers", [])
    profiles = student.get("Profiles", [])
    projects = student.get("Projects", [])
    achievements = student.get("Achievements", [])
    semester_results = student.get("Semester_Results", [])
    registrations = student.get("Registered_Courses", [])
    placements = student.get("Placements", [])
    internships = student.get("Internships", [])
    resumes = student.get("Resumes", [])
    education_docs = student.get("Education_Documents", [])
    skills = student.get("Skills", [])

    return render_template(
        "students/detail.html",
        active_page="students",
        student=student,
        phones=phones,
        profiles=profiles,
        projects=projects,
        achievements=achievements,
        semester_results=semester_results,
        registrations=registrations,
        placements=placements,
        internships=internships,
        resumes=resumes,
        education_docs=education_docs,
        skills=skills,
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
            cgpa = parse_float(request.form.get("CGPA", student["CGPA"]), "CGPA", 0.0, 10.0)
            backlogs = parse_int(request.form.get("Backlogs", student["Backlogs"]), "Backlogs", 0)
            batch_year = parse_int(request.form.get("Batch_Year", student["Batch_Year"]), "Batch Year", 2000, 2100)
            branch = normalize_branch(request.form.get("Branch", student["Branch"]))

            if not branch:
                raise ValidationError("Please select a valid academic branch.")

            payload = {
                "First_Name": request.form.get("First_Name", "").strip(),
                "Last_Name": request.form.get("Last_Name", "").strip() or None,
                "Email": request.form.get("Email", "").strip().lower(),
                "Branch": branch,
                "Batch_Year": batch_year,
                "Section": request.form.get("Section", "A").strip() or None,
                "CGPA": cgpa,
                "Backlogs": backlogs,
                "Resume_Link": request.form.get("Resume_Link", "").strip() or None,
            }
            update_student(student_id, payload)
            flash(f"Student profile for {student['Roll_No']} updated successfully!", "success")
            return redirect(f"/students/{student_id}")
        except (ValidationError, ConflictError, DatabaseError, ServiceError) as err:
            err_msg = _safe_error_message(err)
            flash(f"Update Error: {err_msg}", "danger")
            merged_student = dict(student)
            merged_student.update(request.form)
            return render_template("students/form.html", active_page="students", mode="edit", student=merged_student)

    return render_template("students/form.html", active_page="students", mode="edit", student=student)


@main_bp.route("/students/<int:student_id>/delete", methods=["POST"])
def student_delete(student_id: int):
    """Safely deletes student, respecting institutional career history protection."""
    try:
        res = delete_student(student_id)
        flash(res["message"], "success")
    except ProtectedDeleteError as err:
        flash(f"Cannot Delete Student: {err.message}", "danger")
    except (NotFoundError, ConflictError, DatabaseError, ServiceError) as err:
        err_msg = _safe_error_message(err)
        flash(f"Delete Failed: {err_msg}", "danger")
    return redirect("/students")


@main_bp.route("/students/<int:student_id>/phones", methods=["POST"])
def student_phone_add(student_id: int):
    """Adds a phone number to a student in the dedicated phone table."""
    phone_number = request.form.get("phone_number", "").strip()
    try:
        add_student_phone(student_id, phone_number)
        flash(f"Added phone number {phone_number} successfully.", "success")
    except (ValidationError, ConflictError, DatabaseError, ServiceError) as err:
        err_msg = _safe_error_message(err)
        flash(f"Phone Error: {err_msg}", "danger")
    return redirect(f"/students/{student_id}")


@main_bp.route("/students/<int:student_id>/phones/<string:phone_no>/delete", methods=["POST"])
def student_phone_delete(student_id: int, phone_no: str):
    """Deletes a phone number from the separate phone table."""
    try:
        delete_student_phone(student_id, phone_no)
        flash("Phone number removed successfully.", "success")
    except (NotFoundError, DatabaseError, ServiceError) as err:
        err_msg = _safe_error_message(err)
        flash(f"Phone Removal Failed: {err_msg}", "danger")
    return redirect(f"/students/{student_id}")


# ==============================================================================
# 3. Corporate Partners & Recruitment Drives Views
# ==============================================================================

@main_bp.route("/companies", methods=["GET"])
def companies_list():
    """Displays searchable and filterable company partners."""
    search = request.args.get("search", "").strip() or None
    raw_type = request.args.get("type", "").strip() or request.args.get("tier", "").strip() or None
    company_type = normalize_company_type(raw_type)

    companies = list_companies(search=search, company_type=company_type)
    return render_template(
        "companies/index.html",
        active_page="companies",
        companies=companies,
        search_query=search,
        selected_tier=company_type or raw_type,
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
        except (ValidationError, ConflictError, DatabaseError, ServiceError) as err:
            err_msg = _safe_error_message(err)
            flash(f"Company Registration Error: {err_msg}", "danger")
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
        except (ValidationError, ConflictError, DatabaseError, ServiceError) as err:
            err_msg = _safe_error_message(err)
            flash(f"Update Error: {err_msg}", "danger")
            merged = dict(company)
            merged.update(request.form)
            return render_template("companies/form.html", active_page="companies", mode="edit", company=merged)

    return render_template("companies/form.html", active_page="companies", mode="edit", company=company)


@main_bp.route("/companies/<int:company_id>/delete", methods=["POST"])
def company_delete(company_id: int):
    """Handles company deletion with relationship integrity protection."""
    try:
        res = delete_company(company_id)
        flash(res["message"], "success")
    except (ProtectedDeleteError, ConflictError) as err:
        flash(f"Cannot Delete Company: {err.message}", "danger")
    except (NotFoundError, DatabaseError, ServiceError) as err:
        err_msg = _safe_error_message(err)
        flash(f"Delete Company Failed: {err_msg}", "danger")
    return redirect("/companies")


# ==============================================================================
# 4. Internships (Mandatory vs Additional & Prerequisite SGPA) Views
# ==============================================================================

@main_bp.route("/internships", methods=["GET"])
def internships_list():
    """Displays internships with comprehensive dashboard, filtering, search, and compliance audit tabs."""
    active_tab = request.args.get("type", "All").strip()
    if active_tab not in ("All", "Mandatory", "Additional", "Pending", "Missing", "Compliance", "Analytics"):
        active_tab = "All"

    search = request.args.get("q", "").strip() or None
    raw_branch = request.args.get("branch", "").strip() or None
    branch = normalize_branch(raw_branch)
    raw_batch = request.args.get("batch_year")
    batch_year = int(raw_batch) if raw_batch and str(raw_batch).isdigit() else None
    company_id = request.args.get("company_id", type=int)
    status = request.args.get("status", "").strip() or None
    report_grade = request.args.get("report_grade", "").strip() or None
    sort_by = request.args.get("sort_by", "student_id").strip()
    sort_dir = request.args.get("sort_dir", "asc").strip().lower()

    # Pre-load dashboard analytics
    analytics = get_internship_dashboard_analytics()
    branch_stats = get_branch_internship_statistics()
    batch_reports = get_batch_compliance_reports()
    pending_reports = get_pending_internship_reports()
    missing_students = get_students_missing_mandatory_internships(branch=branch, batch_year=batch_year)

    # Filtered lists
    all_internships = list_internships(
        search=search,
        branch=branch,
        batch_year=batch_year,
        company_id=company_id,
        status=status,
        report_grade=report_grade,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    mandatory_internships = get_mandatory_internships_with_prerequisite_sgpa()
    additional_internships = [i for i in all_internships if i.get("Internship_Type") == "Additional"]

    companies = list_companies()

    return render_template(
        "internships/index.html",
        active_page="internships",
        active_tab=active_tab,
        all_internships=all_internships,
        mandatory_internships=mandatory_internships,
        additional_internships=additional_internships,
        missing_students=missing_students,
        pending_reports=pending_reports,
        branch_stats=branch_stats,
        batch_reports=batch_reports,
        analytics=analytics,
        companies=companies,
        search_query=search,
        selected_branch=branch or raw_branch,
        selected_batch=batch_year,
        selected_company_id=company_id,
        selected_status=status,
        selected_grade=report_grade,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@main_bp.route("/internships/export-csv", methods=["GET"])
@main_bp.route("/internships/export", methods=["GET"])
def internships_export_csv():
    """Generates and streams a downloadable RFC 4180 CSV export of filtered internship records."""
    search = request.args.get("q") or request.args.get("search")
    branch = request.args.get("branch")
    raw_batch = request.args.get("batch_year")
    batch_year = int(raw_batch) if raw_batch and str(raw_batch).isdigit() else None
    company_id = request.args.get("company_id", type=int)
    itype = request.args.get("type") or request.args.get("internship_type")
    status = request.args.get("status")
    report_grade = request.args.get("report_grade")

    internships = list_internships(
        search=search,
        branch=branch,
        batch_year=batch_year,
        company_id=company_id,
        internship_type=itype,
        status=status,
        report_grade=report_grade,
        limit=10000,
        offset=0,
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Internship ID", "Roll No", "Student Name", "Branch", "Batch Year", "CGPA",
        "Company Name", "Designated Role", "Category", "Sequence No",
        "Requirement Linked", "Prerequisite Sem SGPA", "Start Date", "End Date",
        "Duration Weeks", "Duration Days", "Monthly Stipend (INR)", "Credits",
        "Report Semester", "Report Grade", "Operational Status",
        "Report Link", "Certificate Link"
    ])
    for r in internships:
        writer.writerow([
            r.get("Internship_ID"),
            r.get("Roll_No"),
            r.get("Student_Name"),
            r.get("Branch"),
            r.get("Batch_Year"),
            r.get("CGPA"),
            r.get("Company_Name"),
            r.get("Role") or "",
            r.get("Internship_Type"),
            r.get("Internship_No"),
            r.get("Prescribed_Period") or ("None (Additional)" if r.get("Internship_Type") == "Additional" else ""),
            f"{r.get('Prerequisite_Semester_SGPA'):.2f}" if r.get("Prerequisite_Semester_SGPA") is not None else "N/A",
            r.get("Start_Date"),
            r.get("End_Date"),
            r.get("Duration_Weeks"),
            r.get("Duration_Days"),
            f"{r.get('Stipend', 0):.2f}",
            r.get("Credits") or 0,
            r.get("Report_Semester") or "",
            r.get("Report_Grade") or "Pending",
            r.get("Status"),
            r.get("Report_Link") or "",
            r.get("Certificate_Link") or "",
        ])

    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=internships_registry.csv"},
    )


@main_bp.route("/internships/<int:internship_id>", methods=["GET"])
def internship_detail(internship_id: int):
    """Displays comprehensive internship dossier view."""
    try:
        internship = get_internship(internship_id)
    except NotFoundError:
        flash(f"Internship with ID {internship_id} not found.", "warning")
        return redirect("/internships")

    eligibility = check_internship_eligibility(internship["Student_ID"], internship["Internship_No"])
    return render_template(
        "internships/detail.html",
        active_page="internships",
        internship=internship,
        eligibility=eligibility,
    )


@main_bp.route("/internships/<int:internship_id>/edit", methods=["GET", "POST"])
def internship_edit(internship_id: int):
    """Handles updating an existing internship record."""
    try:
        internship = get_internship(internship_id)
    except NotFoundError:
        flash(f"Internship with ID {internship_id} not found.", "warning")
        return redirect("/internships")

    if request.method == "POST":
        try:
            payload = {
                "Role": request.form.get("Role", "").strip() or None,
                "Stipend": parse_float(request.form.get("Stipend", 0.0), "Stipend", 0.0),
                "Start_Date": request.form.get("Start_Date", "").strip(),
                "End_Date": request.form.get("End_Date", "").strip(),
                "Credits": parse_int(request.form.get("Credits", 4), "Credits", 0),
                "Report_Semester": parse_int(request.form.get("Report_Semester"), "Report Semester") if request.form.get("Report_Semester") else None,
                "Report_Grade": request.form.get("Report_Grade", "").strip() or None,
                "Report_Link": request.form.get("Report_Link", "").strip() or None,
                "Certificate_Link": request.form.get("Certificate_Link", "").strip() or None,
            }
            res = update_internship(internship_id, payload)
            flash(f"Updated Internship #{res['Internship_No']} successfully!", "success")
            return redirect(f"/internships/{internship_id}")
        except (ValidationError, ConflictError, DatabaseError, ServiceError) as err:
            err_msg = _safe_error_message(err)
            flash(f"Update Failed: {err_msg}", "danger")

    companies = list_companies()
    return render_template(
        "internships/form.html",
        active_page="internships",
        mode="edit",
        internship=internship,
        companies=companies,
    )


@main_bp.route("/internships/new", methods=["GET", "POST"])
def internship_create():
    """Handles recording a student internship enforcing academic policy constraints."""
    if request.method == "POST":
        try:
            itype = request.form.get("Internship_Type", "Mandatory").strip()
            req_id_raw = request.form.get("Requirement_ID")
            req_id = parse_int(req_id_raw, "Requirement ID") if (itype == "Mandatory" and req_id_raw) else None
            internship_no = parse_int(request.form.get("Internship_No", 1), "Internship No", 1)

            stipend_val = parse_float(request.form.get("Stipend", 0.0), "Stipend", 0.0)
            credits_val = parse_int(request.form.get("Credits", 4 if itype == "Mandatory" else 0), "Credits", 0)
            report_sem_raw = request.form.get("Report_Semester")
            report_sem = parse_int(report_sem_raw, "Report Semester") if report_sem_raw else (5 if internship_no == 1 else 7 if internship_no == 2 else None)

            payload = {
                "Student_ID": parse_int(request.form.get("Student_ID"), "Student"),
                "Company_ID": parse_int(request.form.get("Company_ID"), "Company"),
                "Internship_Type": itype,
                "Requirement_ID": req_id,
                "Internship_No": internship_no,
                "Role": request.form.get("Role", "").strip(),
                "Start_Date": request.form.get("Start_Date", "").strip(),
                "End_Date": request.form.get("End_Date", "").strip(),
                "Stipend": stipend_val,
                "Credits": credits_val,
                "Report_Semester": report_sem,
                "Report_Grade": request.form.get("Report_Grade", "").strip() or None,
                "Report_Link": request.form.get("Report_Link", "").strip() or None,
                "Certificate_Link": request.form.get("Certificate_Link", "").strip() or None,
            }
            res = create_internship(payload)
            flash(f"Recorded {itype} Internship #{payload['Internship_No']} successfully!", "success")
            return redirect(f"/internships/{res['Internship_ID']}")
        except (ValidationError, ConflictError, DatabaseError, ServiceError) as err:
            err_msg = _safe_error_message(err)
            flash(f"Internship Creation Rejected: {err_msg}", "danger")

    students_res = list_students(limit=100)
    students = students_res.get("results", []) if isinstance(students_res, dict) else students_res
    companies = list_companies()
    requirements = list_requirements()
    preselected_student_id = request.args.get("student_id")

    return render_template(
        "internships/form.html",
        active_page="internships",
        mode="create",
        students=students,
        companies=companies,
        requirements=requirements,
        preselected_student_id=preselected_student_id,
        internship=None,
    )


@main_bp.route("/internships/<int:internship_id>/delete", methods=["POST"])
def internship_delete(internship_id: int):
    """Deletes an internship record."""
    try:
        res = delete_internship(internship_id)
        flash(res["message"], "success")
    except (NotFoundError, ConflictError, ProtectedDeleteError, DatabaseError, ServiceError) as err:
        err_msg = _safe_error_message(err)
        flash(f"Internship Deletion Failed: {err_msg}", "danger")
    return redirect("/internships")


# ==============================================================================
# 5. Placements & Offer Management Views
# ==============================================================================

@main_bp.route("/placements", methods=["GET"])
def placements_list():
    """Displays placement directory with advanced search, multi-filters, dynamic sorting, server-side pagination, KPI cards, and star performers view."""
    view_type = request.args.get("view", "all").strip().lower()
    show_multi = (view_type == "multiple")
    show_dashboard = (view_type == "dashboard")

    # 1. Extract Filter Parameters
    search = request.args.get("search", "").strip() or None
    raw_branch = request.args.get("branch", "").strip() or None
    branch = normalize_branch(raw_branch)
    
    raw_batch = request.args.get("batch_year")
    batch_year = None
    if raw_batch and str(raw_batch).strip().lower() not in ("all", "none"):
        try:
            batch_year = int(raw_batch)
        except (ValueError, TypeError):
            pass

    raw_placement_year = request.args.get("placement_year")
    placement_year = None
    if raw_placement_year and str(raw_placement_year).strip().lower() not in ("all", "none"):
        try:
            placement_year = int(raw_placement_year)
        except (ValueError, TypeError):
            pass

    raw_company_id = request.args.get("company_id")
    company_id = None
    if raw_company_id and str(raw_company_id).strip().lower() not in ("all", "none"):
        try:
            company_id = int(raw_company_id)
        except (ValueError, TypeError):
            pass

    status = request.args.get("status", "").strip() or None
    if status and status.lower() in ("all", "none"):
        status = None

    placement_type = request.args.get("placement_type", "").strip() or None
    is_ppo = request.args.get("is_ppo", "").strip() or None

    raw_min_pkg = request.args.get("min_package", "").strip() or None
    min_package = None
    if raw_min_pkg:
        try:
            min_package = float(raw_min_pkg)
        except (ValueError, TypeError):
            pass

    raw_max_pkg = request.args.get("max_package", "").strip() or None
    max_package = None
    if raw_max_pkg:
        try:
            max_package = float(raw_max_pkg)
        except (ValueError, TypeError):
            pass

    # 2. Sorting & Pagination Parameters
    sort_by = request.args.get("sort_by", "package").strip().lower()
    sort_dir = request.args.get("sort_dir", "desc").strip().lower()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 15, type=int)

    # 3. Query Placement Offers
    offers_res = list_placement_offers(
        search=search,
        branch=branch,
        batch_year=batch_year,
        placement_year=placement_year,
        company_id=company_id,
        offer_status=status,
        placement_type=placement_type,
        is_ppo=is_ppo,
        min_package=min_package,
        max_package=max_package,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        limit=per_page,
    )
    offers = offers_res.get("results", [])

    # 4. Placement Analytics & KPIs
    analytics = get_placement_analytics(
        placement_year=placement_year,
        batch_year=batch_year,
        branch=branch,
        company_id=company_id,
    )

    # 5. Star Performers (Multiple Offers)
    multi_offer_students = get_students_with_multiple_offers(min_offers=2)

    # 6. Modal / Form Auxiliary Data
    students_res = list_students(limit=100)
    all_students = students_res.get("results", []) if isinstance(students_res, dict) else students_res
    all_companies = list_companies()
    all_opportunities = list_opportunities(opportunity_type="Placement")

    # 7. Distinct Filter Options
    filter_opts = get_dashboard_filter_options()

    active_filters = {
        "search": search or "",
        "branch": branch or raw_branch or "",
        "batch_year": batch_year or "",
        "placement_year": placement_year or "",
        "company_id": company_id or "",
        "status": status or "",
        "min_package": min_package or "",
        "max_package": max_package or "",
        "placement_type": placement_type or "",
        "is_ppo": is_ppo or "",
        "sort_by": sort_by,
        "sort_dir": sort_dir,
        "per_page": per_page,
        "view": view_type,
    }

    return render_template(
        "placements/index.html",
        active_page="placements",
        offers=offers,
        pagination=offers_res,
        analytics=analytics,
        show_multi=show_multi,
        show_dashboard=show_dashboard,
        multi_offer_students=multi_offer_students,
        all_students=all_students,
        all_companies=all_companies,
        all_opportunities=all_opportunities,
        filter_options=filter_opts,
        active_filters=active_filters,
        # Backward compatibility bindings
        search_query=search,
        selected_status=status,
    )


@main_bp.route("/placements/export-csv", methods=["GET"])
@main_bp.route("/placements/export", methods=["GET"])
def placements_export_csv():
    """Generates and streams a downloadable CSV of filtered placement offer records."""
    search = request.args.get("search", "").strip() or None
    raw_branch = request.args.get("branch", "").strip() or None
    branch = normalize_branch(raw_branch)
    
    raw_batch = request.args.get("batch_year")
    batch_year = int(raw_batch) if raw_batch and str(raw_batch).isdigit() else None

    raw_placement_year = request.args.get("placement_year")
    placement_year = int(raw_placement_year) if raw_placement_year and str(raw_placement_year).isdigit() else None

    raw_company_id = request.args.get("company_id")
    company_id = int(raw_company_id) if raw_company_id and str(raw_company_id).isdigit() else None

    status = request.args.get("status", "").strip() or None
    if status and status.lower() in ("all", "none"):
        status = None

    placement_type = request.args.get("placement_type", "").strip() or None
    is_ppo = request.args.get("is_ppo", "").strip() or None

    raw_min_pkg = request.args.get("min_package", "").strip() or None
    min_package = float(raw_min_pkg) if raw_min_pkg else None

    raw_max_pkg = request.args.get("max_package", "").strip() or None
    max_package = float(raw_max_pkg) if raw_max_pkg else None

    sort_by = request.args.get("sort_by", "package").strip().lower()
    sort_dir = request.args.get("sort_dir", "desc").strip().lower()

    res = list_placement_offers(
        search=search,
        branch=branch,
        batch_year=batch_year,
        placement_year=placement_year,
        company_id=company_id,
        offer_status=status,
        placement_type=placement_type,
        is_ppo=is_ppo,
        min_package=min_package,
        max_package=max_package,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=10000,
        offset=0,
    )
    offers = res.get("results", [])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Placement ID", "Roll No", "Student Name", "Branch", "Batch Year", "CGPA",
        "Company Name", "Company Type", "Designated Role", "Package (LPA)",
        "Placement Year", "Placement Type", "Is PPO", "Offer Status", "Joined",
        "Interview Rounds", "Evaluated Skills"
    ])

    for o in offers:
        skills_str = ", ".join(o.get("Evaluated_Skills", [])) if isinstance(o.get("Evaluated_Skills"), list) else str(o.get("Evaluated_Skills") or "")
        writer.writerow([
            o.get("Placement_ID"),
            o.get("Roll_No"),
            o.get("Student_Name") or f"{o.get('First_Name')} {o.get('Last_Name') or ''}".strip(),
            o.get("Branch"),
            o.get("Batch_Year"),
            o.get("CGPA"),
            o.get("Company_Name"),
            o.get("Company_Type") or "",
            o.get("Role"),
            o.get("Package"),
            o.get("Placement_Year"),
            o.get("Placement_Type"),
            o.get("Is_PPO"),
            o.get("Offer_Status"),
            o.get("Joined"),
            o.get("Interview_Rounds", 1),
            skills_str,
        ])

    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=placement_offers_directory.csv"},
    )


@main_bp.route("/placements/<int:placement_id>", methods=["GET"])
def placement_detail(placement_id: int):
    """Displays comprehensive placement offer details including student, company, drive, and eligibility compliance."""
    try:
        offer = get_placement_offer(placement_id)
    except NotFoundError:
        flash(f"Placement Offer #{placement_id} not found.", "warning")
        return redirect("/placements")

    return render_template(
        "placements/detail.html",
        active_page="placements",
        offer=offer,
    )


@main_bp.route("/placements/<int:placement_id>/edit", methods=["GET", "POST"])
def placement_edit(placement_id: int):
    """Handles updating a placement offer's details and evaluated skills."""
    try:
        offer = get_placement_offer(placement_id)
    except NotFoundError:
        flash(f"Placement Offer #{placement_id} not found.", "warning")
        return redirect("/placements")

    if request.method == "POST":
        try:
            package = parse_float(request.form.get("Package", 0.0), "Package", min_val=0.01)
            raw_skills = request.form.get("Skills", "").strip()
            skills_list = [s.strip() for s in raw_skills.split(",") if s.strip()] if raw_skills else []

            payload = {
                "Role": request.form.get("Role", "").strip(),
                "Package": package,
                "Placement_Year": parse_int(request.form.get("Placement_Year", 2024), "Placement Year", 2000, 2100),
                "Placement_Type": request.form.get("Placement_Type", "On-campus").strip(),
                "Offer_Status": request.form.get("Offer_Status", "Offered").strip(),
                "Is_PPO": request.form.get("Is_PPO", "No").strip(),
                "Joined": request.form.get("Joined", "No").strip(),
                "Interview_Rounds": parse_int(request.form.get("Interview_Rounds", 1), "Interview Rounds", min_val=0),
                "Skills": skills_list,
            }

            res = update_placement_offer(placement_id, payload)
            flash(f"Placement Offer #{placement_id} updated successfully!", "success")
            return redirect(f"/placements/{placement_id}")
        except (ValidationError, ConflictError, DatabaseError, ServiceError) as err:
            err_msg = _safe_error_message(err)
            flash(f"Update Failed: {err_msg}", "danger")

    return render_template(
        "placements/form.html",
        active_page="placements",
        mode="edit",
        offer=offer,
    )


@main_bp.route("/placements/new", methods=["GET", "POST"])
def placement_create():
    """Handles issuing a placement offer enforcing no duplicates, opportunity type, and single-accepted offer rules."""
    if request.method == "POST":
        try:
            opp_id_raw = request.form.get("Opportunity_ID")
            opp_id = parse_int(opp_id_raw, "Opportunity Opening") if opp_id_raw else None
            package = parse_float(request.form.get("Package", 0.0), "Package", min_val=0.01)
            student_id = parse_int(request.form.get("Student_ID"), "Student")
            company_id = parse_int(request.form.get("Company_ID"), "Company")

            raw_skills = request.form.get("Skills", "").strip()
            skills_list = [s.strip() for s in raw_skills.split(",") if s.strip()] if raw_skills else []

            payload = {
                "Student_ID": student_id,
                "Company_ID": company_id,
                "Opportunity_ID": opp_id,
                "Role": request.form.get("Role", "").strip(),
                "Package": package,
                "Placement_Year": parse_int(request.form.get("Placement_Year", 2024), "Placement Year", 2000, 2100),
                "Placement_Type": request.form.get("Placement_Type", "On-campus").strip(),
                "Offer_Status": request.form.get("Offer_Status", "Offered").strip(),
                "Is_PPO": request.form.get("Is_PPO", "No").strip(),
                "Interview_Rounds": parse_int(request.form.get("Interview_Rounds", 1), "Interview Rounds", min_val=0),
                "Skills": skills_list,
            }
            res = create_placement_offer(payload)
            flash(f"Issued Placement Offer #{res['Placement_ID']} ({payload['Role']} - {payload['Package']} LPA) successfully!", "success")
            return redirect(f"/placements/{res['Placement_ID']}")
        except (ValidationError, ConflictError, DatabaseError, ServiceError) as err:
            err_msg = _safe_error_message(err)
            flash(f"Offer Issue Rejected: {err_msg}", "danger")
            return redirect("/placements")

    # GET request: render standalone form
    students_res = list_students(limit=100)
    all_students = students_res.get("results", []) if isinstance(students_res, dict) else students_res
    all_companies = list_companies()
    all_opportunities = list_opportunities(opportunity_type="Placement")

    return render_template(
        "placements/form.html",
        active_page="placements",
        mode="create",
        offer=None,
        all_students=all_students,
        all_companies=all_companies,
        all_opportunities=all_opportunities,
    )


@main_bp.route("/placements/<int:placement_id>/status", methods=["POST"])
def placement_status_update(placement_id: int):
    """Updates an offer's status (Accept, Decline, Joined), enforcing the single accepted offer constraint."""
    new_status = request.form.get("status", "").strip()
    try:
        update_offer_status(placement_id, new_status)
        flash(f"Placement Offer #{placement_id} status updated to '{new_status}' successfully!", "success")
    except ConflictError as err:
        flash(f"Status Transition Blocked: {err.message}", "danger")
    except (ValidationError, NotFoundError, DatabaseError, ServiceError) as err:
        err_msg = _safe_error_message(err)
        flash(f"Status Update Failed: {err_msg}", "danger")

    # Check redirect destination
    referer = request.headers.get("Referer", "")
    if f"/placements/{placement_id}" in referer:
        return redirect(f"/placements/{placement_id}")
    return redirect("/placements")


@main_bp.route("/placements/<int:placement_id>/delete", methods=["POST"])
def placement_delete(placement_id: int):
    """Deletes a placement offer record."""
    try:
        res = delete_placement_offer(placement_id)
        flash(res["message"], "success")
    except (NotFoundError, ConflictError, ProtectedDeleteError, DatabaseError, ServiceError) as err:
        err_msg = _safe_error_message(err)
        flash(f"Offer Deletion Failed: {err_msg}", "danger")
    return redirect("/placements")


# ==============================================================================
# 6. Reports & Multi-Filter Export Views
# ==============================================================================

@main_bp.route("/reports", methods=["GET"])
def reports_view():
    """Renders comprehensive institutional reports with multi-criteria filters."""
    raw_branch = request.args.get("branch", "").strip() or None
    branch = normalize_branch(raw_branch)

    filters = {
        "branch": branch,
        "placement_status": request.args.get("placement_status", "").strip() or None,
        "internship_status": request.args.get("internship_status", "").strip() or None,
        "min_cgpa": request.args.get("min_cgpa", "").strip() or None,
        "min_salary": request.args.get("min_salary", "").strip() or None,
    }

    report_data = get_comprehensive_report_data(filters)
    query_string = request.query_string.decode("utf-8")

    # Present selected branch accurately back to template
    filters_display = dict(filters)
    filters_display["branch"] = branch or raw_branch

    return render_template(
        "reports/index.html",
        active_page="reports",
        filters=filters_display,
        rows=report_data["rows"],
        summary=report_data["summary"],
        current_query_string=query_string,
    )


@main_bp.route("/reports/export", methods=["GET"])
def reports_export_csv():
    """Generates and streams a CSV export of the filtered cohort report."""
    raw_branch = request.args.get("branch", "").strip() or None
    branch = normalize_branch(raw_branch)

    filters = {
        "branch": branch,
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
    """Returns aggregated enterprise dashboard statistics and charts JSON."""
    raw_batch = request.args.get("batch_year")
    raw_branch = request.args.get("branch", "").strip() or None
    raw_placement_year = request.args.get("placement_year")

    filters = {}
    if raw_batch and str(raw_batch).strip().lower() not in ("all", "none"):
        try:
            filters["batch_year"] = int(raw_batch)
        except (ValueError, TypeError):
            pass

    if raw_branch and raw_branch.lower() not in ("all", "none"):
        filters["branch"] = normalize_branch(raw_branch)

    if raw_placement_year and str(raw_placement_year).strip().lower() not in ("all", "none"):
        try:
            filters["placement_year"] = int(raw_placement_year)
        except (ValueError, TypeError):
            pass

    return jsonify({"status": "success", "data": get_comprehensive_dashboard_data(filters)}), 200


@main_bp.route("/api/analytics/charts/yearwise", methods=["GET"])
def api_chart_yearwise():
    """Returns year-wise placement trends JSON."""
    raw_branch = request.args.get("branch", "").strip() or None
    raw_batch = request.args.get("batch_year")
    filters = {}
    if raw_branch and raw_branch.lower() not in ("all", "none"):
        filters["branch"] = normalize_branch(raw_branch)
    if raw_batch and str(raw_batch).strip().lower() not in ("all", "none"):
        try:
            filters["batch_year"] = int(raw_batch)
        except (ValueError, TypeError):
            pass
    return jsonify({"status": "success", "data": get_yearwise_placement_chart_data(filters)}), 200


@main_bp.route("/api/analytics/charts/branchwise", methods=["GET"])
def api_chart_branchwise():
    """Returns branch-wise distribution JSON."""
    raw_batch = request.args.get("batch_year")
    raw_placement_year = request.args.get("placement_year")
    filters = {}
    if raw_batch and str(raw_batch).strip().lower() not in ("all", "none"):
        try:
            filters["batch_year"] = int(raw_batch)
        except (ValueError, TypeError):
            pass
    if raw_placement_year and str(raw_placement_year).strip().lower() not in ("all", "none"):
        try:
            filters["placement_year"] = int(raw_placement_year)
        except (ValueError, TypeError):
            pass
    return jsonify({"status": "success", "data": get_branchwise_analytics_chart_data(filters)}), 200


# ==============================================================================
# 8. SQL Reports & Interactive DBMS Console (Saved & Custom Queries)
# ==============================================================================

@main_bp.route("/sql-reports", methods=["GET"])
def sql_reports_view():
    """Displays the two-part SQL Reports page:
    Part 1: Saved queries from placement_internship_db.sql and Phase 9 DBMS demo.
    Part 2: Custom read-only SQL query box with safety enforcement.
    """
    all_queries = list_saved_queries()
    return render_template(
        "reports/sql_reports.html",
        active_page="sql_reports",
        saved_queries=all_queries,
    )


@main_bp.route("/api/sql-reports/run-saved", methods=["POST"])
def api_run_saved_query():
    """Executes a parameterized saved query and returns table data as JSON."""
    data = request.get_json(silent=True) or request.form.to_dict()
    query_id = data.get("query_id")
    params = data.get("params") or {}

    if not query_id:
        return jsonify({"status": "error", "message": "query_id is required"}), 400

    try:
        res = execute_saved_query(query_id, params)
        return jsonify({"status": "success", "data": res}), 200
    except (ValidationError, ServiceError) as err:
        return jsonify({"status": "error", "message": err.message}), 400
    except DatabaseError as err:
        logger.error("Database error executing saved query %s: %s", query_id, err)
        return jsonify({"status": "error", "message": "Database query failed. Internal details have been logged."}), 400
    except Exception as exc:
        logger.error("Unexpected error executing saved query %s: %s", query_id, exc)
        return jsonify({"status": "error", "message": "An internal server error occurred while executing the query."}), 500


@main_bp.route("/sql-reports/export-saved", methods=["GET"])
def export_saved_query_csv():
    """Exports the execution results of a saved query as a downloadable CSV file."""
    query_id = request.args.get("query_id")
    if not query_id:
        flash("Cannot export: query_id is required.", "danger")
        return redirect(url_for("main.sql_reports_view"))

    params = {k: v for k, v in request.args.items() if k != "query_id"}

    try:
        res = execute_saved_query(query_id, params)
        columns = res.get("columns", [])
        rows = res.get("rows", [])

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)

        for r in rows:
            writer.writerow([r.get(c, "") for c in columns])

        csv_content = output.getvalue()
        output.close()

        filename = f"{query_id}_export.csv"
        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except Exception as exc:
        logger.error("Failed to export saved query CSV: %s", exc)
        flash("CSV Export Failed due to an internal processing error.", "danger")
        return redirect(url_for("main.sql_reports_view"))


@main_bp.route("/api/sql-reports/run-custom", methods=["POST"])
def api_run_custom_query():
    """Validates and executes user-provided SQL under read-only MySQL permissions and 500-row limit."""
    data = request.get_json(silent=True) or request.form.to_dict()
    raw_sql = data.get("sql", "").strip()

    if not raw_sql:
        return jsonify({
            "status": "error",
            "message": "SQL statement is empty. Please enter a valid SELECT statement.",
            "data": None,
        }), 400

    try:
        res = execute_custom_query(raw_sql)
        if res.get("status") == "error":
            return jsonify({
                "status": "error",
                "message": res.get("error"),
                "data": res,
            }), 200
        return jsonify({
            "status": "success",
            "message": "Query executed successfully.",
            "data": res,
        }), 200
    except ValidationError as ve:
        return jsonify({
            "status": "error",
            "message": ve.message,
            "data": None,
        }), 400
    except Exception as exc:
        logger.error("Unhandled error running custom query: %s", exc)
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred while executing the query.",
            "data": None,
        }), 500


@main_bp.route("/sql-reports/export-custom", methods=["POST"])
def export_custom_query_csv():
    """Exports custom SQL execution results as a downloadable CSV."""
    raw_sql = request.form.get("sql", "").strip()
    if not raw_sql:
        flash("Cannot export: SQL query cannot be empty.", "warning")
        return redirect(url_for("main.sql_reports_view"))

    try:
        res = execute_custom_query(raw_sql)
        if res.get("status") == "error":
            flash(f"Export Error: {res.get('error')}", "danger")
            return redirect(url_for("main.sql_reports_view"))

        columns = res.get("columns", [])
        rows = res.get("rows", [])

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)

        for r in rows:
            writer.writerow([r.get(c, "") for c in columns])

        csv_content = output.getvalue()
        output.close()

        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=custom_sql_results.csv"},
        )
    except ValidationError as ve:
        flash(f"SQL Validation Error: {ve.message}", "danger")
        return redirect(url_for("main.sql_reports_view"))
    except Exception as exc:
        logger.error("Failed to export custom SQL CSV: %s", exc)
        flash("Custom CSV Export Failed due to an internal server error.", "danger")
        return redirect(url_for("main.sql_reports_view"))

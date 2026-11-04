import logging
import datetime
import math
from typing import Dict, Any, List, Optional
from db.connection import get_cursor, execute_one, execute_query
from services.exceptions import ValidationError, NotFoundError, ConflictError

logger = logging.getLogger(__name__)

VALID_INTERNSHIP_TYPES = ("Mandatory", "Additional")


def calculate_internship_duration(start_date: Any, end_date: Any) -> Dict[str, Any]:
    """Calculates days, weeks, months, and formatted duration string between two dates."""
    try:
        if isinstance(start_date, str):
            s_date = datetime.date.fromisoformat(start_date.strip())
        elif isinstance(start_date, datetime.date):
            s_date = start_date
        else:
            s_date = None

        if isinstance(end_date, str):
            e_date = datetime.date.fromisoformat(end_date.strip())
        elif isinstance(end_date, datetime.date):
            e_date = end_date
        else:
            e_date = None

        if s_date and e_date:
            days = (e_date - s_date).days + 1
            if days < 0:
                days = 0
            weeks = round(days / 7.0, 1)
            months = round(days / 30.4, 1)
            if weeks >= 1:
                duration_str = f"{weeks:.1f} weeks ({days} days)"
            else:
                duration_str = f"{days} days"
            return {
                "days": days,
                "weeks": weeks,
                "months": months,
                "duration_str": duration_str,
            }
    except Exception:
        pass

    return {
        "days": 0,
        "weeks": 0.0,
        "months": 0.0,
        "duration_str": "N/A",
    }


def determine_internship_status(
    start_date: Any,
    end_date: Any,
    report_link: Optional[str] = None,
    report_grade: Optional[str] = None,
    cert_link: Optional[str] = None,
) -> str:
    """Determines internship operational and compliance status:
    - 'Upcoming': Start_Date > today
    - 'In Progress': Start_Date <= today <= End_Date
    - 'Completed': End_Date < today AND (Report_Link or Report_Grade)
    - 'Pending Report': End_Date < today AND (not Report_Link or Report_Grade in (None, '', 'Pending'))
    """
    today = datetime.date.today()
    try:
        s_date = datetime.date.fromisoformat(str(start_date).strip()) if start_date else None
        e_date = datetime.date.fromisoformat(str(end_date).strip()) if end_date else None
    except Exception:
        s_date = start_date if isinstance(start_date, datetime.date) else None
        e_date = end_date if isinstance(end_date, datetime.date) else None

    if s_date and s_date > today:
        return "Upcoming"
    if s_date and e_date and s_date <= today <= e_date:
        return "In Progress"

    has_report = bool(report_link and str(report_link).strip())
    has_grade = bool(
        report_grade
        and str(report_grade).strip()
        and str(report_grade).strip().lower() != "pending"
    )

    if has_report and has_grade:
        return "Completed"
    elif has_report or has_grade:
        return "Completed"
    else:
        return "Pending Report"


def check_internship_eligibility(
    student_id: int,
    internship_no: int,
    min_sgpa: float = 6.00,
) -> Dict[str, Any]:
    """Calculates student academic eligibility for an internship using actual SEMESTER_RESULT records.

    Academic Rules:
    - Mandatory Internship 1: Completed during 2nd year summer break after Sem 4.
      Eligibility is governed by Semester 3 SGPA.
    - Mandatory Internship 2: Completed during 3rd year summer break after Sem 5.
      Eligibility is governed by Semester 5 SGPA.
    - Additional Internships (No >= 3): Optional extracurricular engagements.
      No prerequisite semester SGPA required.
    """
    student = execute_one(
        "SELECT Student_ID, Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs FROM STUDENT WHERE Student_ID = %s",
        (student_id,),
    )
    if not student:
        raise NotFoundError(f"Student with ID {student_id} not found.")

    student_name = f"{student['First_Name']} {student.get('Last_Name') or ''}".strip()

    if internship_no not in (1, 2):
        return {
            "is_eligible": True,
            "student_id": student_id,
            "roll_no": student["Roll_No"],
            "student_name": student_name,
            "internship_no": internship_no,
            "internship_type": "Additional",
            "required_result_semester": None,
            "prerequisite_sgpa": None,
            "min_required_sgpa": min_sgpa,
            "semester_result_found": True,
            "status": "Optional",
            "message": "Additional internships are optional and have no mandatory prerequisite semester SGPA constraint.",
        }

    # Fetch requirement for this mandatory internship
    req = execute_one(
        "SELECT Requirement_ID, Internship_No, Required_Result_Semester, Report_Submission_Semester, Credits, Prescribed_Period FROM INTERNSHIP_REQUIREMENT WHERE Internship_No = %s",
        (internship_no,),
    )
    req_sem = req["Required_Result_Semester"] if req else (3 if internship_no == 1 else 5)
    prescribed_period = (
        req["Prescribed_Period"] if req else f"Mandatory Summer Internship #{internship_no}"
    )

    # Query student's verified semester result
    sem_res = execute_one(
        "SELECT Result_ID, Semester, SGPA, Total_Credits FROM SEMESTER_RESULT WHERE Student_ID = %s AND Semester = %s",
        (student_id, req_sem),
    )

    if not sem_res:
        return {
            "is_eligible": False,
            "student_id": student_id,
            "roll_no": student["Roll_No"],
            "student_name": student_name,
            "internship_no": internship_no,
            "internship_type": "Mandatory",
            "required_result_semester": req_sem,
            "prerequisite_sgpa": None,
            "min_required_sgpa": min_sgpa,
            "semester_result_found": False,
            "status": "Prerequisite Missing",
            "prescribed_period": prescribed_period,
            "message": f"Candidate has no recorded result for Semester {req_sem}. Semester {req_sem} SGPA is required to verify eligibility.",
        }

    sgpa = float(sem_res["SGPA"])
    credits = int(sem_res["Total_Credits"])
    is_eligible = sgpa >= min_sgpa

    if is_eligible:
        status = "Eligible"
        msg = f"Candidate is eligible for Mandatory Internship #{internship_no}. Verified Semester {req_sem} SGPA: {sgpa:.2f} (Required: >= {min_sgpa:.2f})."
    else:
        status = "Ineligible"
        msg = f"Candidate is ineligible for Mandatory Internship #{internship_no}. Verified Semester {req_sem} SGPA: {sgpa:.2f} is below minimum requirement of {min_sgpa:.2f}."

    return {
        "is_eligible": is_eligible,
        "student_id": student_id,
        "roll_no": student["Roll_No"],
        "student_name": student_name,
        "internship_no": internship_no,
        "internship_type": "Mandatory",
        "required_result_semester": req_sem,
        "prerequisite_sgpa": sgpa,
        "prerequisite_credits": credits,
        "min_required_sgpa": min_sgpa,
        "semester_result_found": True,
        "status": status,
        "prescribed_period": prescribed_period,
        "message": msg,
    }


def validate_internship_payload(data: Dict[str, Any], is_update: bool = False) -> None:
    """Validates internship fields, dates, and mandatory/additional requirement constraints."""
    if not is_update:
        required = [
            "Student_ID",
            "Company_ID",
            "Internship_No",
            "Internship_Type",
            "Start_Date",
            "End_Date",
        ]
        for field in required:
            if field not in data or data[field] is None:
                raise ValidationError(f"Missing required field: '{field}'")

    if "Internship_Type" in data and data["Internship_Type"] is not None:
        itype = str(data["Internship_Type"]).strip()
        if itype not in VALID_INTERNSHIP_TYPES:
            raise ValidationError(
                f"Internship_Type must be one of: {', '.join(VALID_INTERNSHIP_TYPES)}"
            )

    if "Internship_No" in data and data["Internship_No"] is not None:
        try:
            num = int(data["Internship_No"])
            if num < 1:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Internship_No must be an integer >= 1")

    # Date ordering check
    if "Start_Date" in data and "End_Date" in data and data["Start_Date"] and data["End_Date"]:
        start_str = str(data["Start_Date"]).strip()
        end_str = str(data["End_Date"]).strip()
        if end_str < start_str:
            raise ValidationError(
                f"Invalid dates: End_Date ({end_str}) cannot be earlier than Start_Date ({start_str})"
            )

    if "Stipend" in data and data["Stipend"] is not None:
        try:
            stipend = float(data["Stipend"])
            if stipend < 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Stipend must be a non-negative number (>= 0)")


def create_internship(data: Dict[str, Any]) -> Dict[str, Any]:
    """Records an internship experience, strictly enforcing requirement linkage constraints.

    Academic Policy Constraints Enforced:
    1. Mandatory Internships:
       - MUST link to an existing INTERNSHIP_REQUIREMENT record (Requirement_ID != None).
       - MUST match the exact requirement number (Requirement 1 <-> Internship 1, Requirement 2 <-> Internship 2).
    2. Additional Internships:
       - MUST NOT link to any requirement (Requirement_ID must be None).
    3. Temporal: End_Date >= Start_Date.
    4. Relational: (Student_ID, Internship_No) must be unique.
    """
    validate_internship_payload(data, is_update=False)

    student_id = int(data["Student_ID"])
    company_id = int(data["Company_ID"])
    opp_id = int(data["Opportunity_ID"]) if data.get("Opportunity_ID") else None
    req_id = int(data["Requirement_ID"]) if data.get("Requirement_ID") else None
    internship_no = int(data["Internship_No"])
    internship_type = str(data["Internship_Type"]).strip()
    role = str(data.get("Role", "") or "").strip() or None
    rounds = int(data.get("Interview_Rounds", 1) or 1)
    stipend = round(float(data.get("Stipend", 0.0) or 0.0), 2)
    start_date = str(data["Start_Date"]).strip()
    end_date = str(data["End_Date"]).strip()
    credits = (
        int(data["Credits"])
        if data.get("Credits") is not None
        else (4 if internship_type == "Mandatory" else 0)
    )
    report_sem = (
        int(data["Report_Semester"])
        if data.get("Report_Semester") is not None
        else (5 if internship_no == 1 else 7 if internship_no == 2 else None)
    )
    report_link = str(data.get("Report_Link", "") or "").strip() or None
    report_grade = str(data.get("Report_Grade", "") or "").strip() or None
    cert_link = str(data.get("Certificate_Link", "") or "").strip() or None

    # 1. Verify Student exists
    student = execute_one(
        "SELECT Student_ID, Roll_No FROM STUDENT WHERE Student_ID = %s", (student_id,)
    )
    if not student:
        raise NotFoundError(f"Student with ID {student_id} does not exist.")

    # 2. Verify Company exists
    company = execute_one(
        "SELECT Company_ID, Company_Name FROM COMPANY WHERE Company_ID = %s", (company_id,)
    )
    if not company:
        raise NotFoundError(f"Company with ID {company_id} does not exist.")

    # 3. Unique (Student_ID, Internship_No) check
    existing_no = execute_one(
        "SELECT Internship_ID, Internship_Type, Role FROM INTERNSHIP WHERE Student_ID = %s AND Internship_No = %s",
        (student_id, internship_no),
    )
    if existing_no:
        raise ConflictError(
            f"Student {student['Roll_No']} already has an internship recorded with number {internship_no} "
            f"('{existing_no['Role']}' - Type: {existing_no['Internship_Type']})."
        )

    # 4. Mandatory vs Additional Requirement Constraints
    if internship_type == "Mandatory":
        if not req_id:
            raise ValidationError(
                f"Mandatory Internship #{internship_no} must link to a valid INTERNSHIP_REQUIREMENT (Requirement_ID cannot be null)."
            )
        requirement = execute_one(
            "SELECT Requirement_ID, Internship_No, Mandatory, Required_Result_Semester FROM INTERNSHIP_REQUIREMENT WHERE Requirement_ID = %s",
            (req_id,),
        )
        if not requirement:
            raise NotFoundError(f"Internship Requirement with ID {req_id} does not exist.")

        # Enforce exact requirement number match
        if requirement["Internship_No"] != internship_no:
            raise ValidationError(
                f"Requirement number mismatch: Mandatory Internship #{internship_no} cannot link to Requirement #{requirement['Internship_No']} "
                f"(Requirement ID {req_id}). Internship #{internship_no} must link to Requirement #{internship_no}."
            )
    else:
        # Additional Internship
        if req_id is not None:
            raise ValidationError(
                f"Additional internships cannot be linked to mandatory academic requirements. Requirement_ID must be null (received {req_id})."
            )

    insert_sql = """
        INSERT INTO INTERNSHIP (
            Student_ID, Company_ID, Opportunity_ID, Requirement_ID, Internship_No,
            Internship_Type, Role, Interview_Rounds, Stipend, Start_Date, End_Date,
            Credits, Report_Semester, Report_Link, Report_Grade, Certificate_Link
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            insert_sql,
            (
                student_id,
                company_id,
                opp_id,
                req_id,
                internship_no,
                internship_type,
                role,
                rounds,
                stipend,
                start_date,
                end_date,
                credits,
                report_sem,
                report_link,
                report_grade,
                cert_link,
            ),
        )
        internship_id = cursor.lastrowid

    logger.info(
        "Created %s Internship #%s (ID: %s) for student %s",
        internship_type,
        internship_no,
        internship_id,
        student["Roll_No"],
    )
    return get_internship(internship_id)


def get_internship(internship_id: int) -> Dict[str, Any]:
    """Retrieves full internship details with dynamic 3NF joins, duration, status, and eligibility."""
    sql = """
        SELECT i.Internship_ID, i.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, s.Batch_Year, s.CGPA, s.Email,
               i.Company_ID, c.Company_Name, c.Company_Type, c.Location AS Company_Location, c.Website AS Company_Website,
               i.Opportunity_ID, o.Role AS Opportunity_Role, o.Opportunity_Type,
               i.Requirement_ID, ir.Prescribed_Period, ir.Required_Result_Semester, ir.Report_Submission_Semester,
               i.Internship_No, i.Internship_Type, i.Role, i.Interview_Rounds, i.Stipend,
               i.Start_Date, i.End_Date, i.Credits, i.Report_Semester, i.Report_Link,
               i.Report_Grade, i.Certificate_Link,
               sr.SGPA AS Prerequisite_Semester_SGPA,
               sr.Total_Credits AS Prerequisite_Credits
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        LEFT JOIN OPPORTUNITY o ON i.Opportunity_ID = o.Opportunity_ID
        LEFT JOIN INTERNSHIP_REQUIREMENT ir ON i.Requirement_ID = ir.Requirement_ID
        LEFT JOIN SEMESTER_RESULT sr ON i.Student_ID = sr.Student_ID 
                                    AND ir.Required_Result_Semester = sr.Semester
        WHERE i.Internship_ID = %s
    """
    row = execute_one(sql, (internship_id,))
    if not row:
        raise NotFoundError(f"Internship with ID {internship_id} not found.")

    row["Stipend"] = float(row["Stipend"])
    row["CGPA"] = float(row["CGPA"])
    row["Start_Date"] = str(row["Start_Date"])
    row["End_Date"] = str(row["End_Date"])
    row["Student_Name"] = f"{row['First_Name']} {row.get('Last_Name') or ''}".strip()
    if row.get("Prerequisite_Semester_SGPA") is not None:
        row["Prerequisite_Semester_SGPA"] = float(row["Prerequisite_Semester_SGPA"])

    # Computed fields
    duration = calculate_internship_duration(row["Start_Date"], row["End_Date"])
    row["Duration_Days"] = duration["days"]
    row["Duration_Weeks"] = duration["weeks"]
    row["Duration_Months"] = duration["months"]
    row["Duration_Str"] = duration["duration_str"]

    row["Status"] = determine_internship_status(
        row["Start_Date"],
        row["End_Date"],
        row.get("Report_Link"),
        row.get("Report_Grade"),
        row.get("Certificate_Link"),
    )

    eligibility = check_internship_eligibility(row["Student_ID"], row["Internship_No"])
    row["Eligibility"] = eligibility
    row["Is_Eligible"] = eligibility["is_eligible"]
    row["Eligibility_Status"] = eligibility["status"]

    return row


def list_internships(
    search: Optional[str] = None,
    student_id: Optional[int] = None,
    company_id: Optional[int] = None,
    branch: Optional[str] = None,
    batch_year: Optional[int] = None,
    internship_type: Optional[str] = None,
    internship_no: Optional[int] = None,
    status: Optional[str] = None,
    report_grade: Optional[str] = None,
    report_semester: Optional[int] = None,
    sort_by: str = "student_id",
    sort_dir: str = "asc",
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    as_dict: bool = False,
) -> Any:
    """Lists, filters, and searches student internships with comprehensive analytical attributes."""
    where_clauses = ["1=1"]
    params: List[Any] = []

    if search:
        search_term = f"%{search.strip()}%"
        where_clauses.append(
            "(s.First_Name LIKE %s OR s.Last_Name LIKE %s OR s.Roll_No LIKE %s OR c.Company_Name LIKE %s OR i.Role LIKE %s)"
        )
        params.extend([search_term, search_term, search_term, search_term, search_term])

    if student_id is not None:
        where_clauses.append("i.Student_ID = %s")
        params.append(int(student_id))

    if company_id is not None:
        where_clauses.append("i.Company_ID = %s")
        params.append(int(company_id))

    if branch and str(branch).strip().lower() not in ("all", "none", ""):
        where_clauses.append("s.Branch = %s")
        params.append(branch.strip())

    if batch_year is not None and str(batch_year).strip().lower() not in ("all", "none", ""):
        try:
            where_clauses.append("s.Batch_Year = %s")
            params.append(int(batch_year))
        except (ValueError, TypeError):
            pass

    if internship_type and str(internship_type).strip().lower() not in ("all", "none", ""):
        where_clauses.append("i.Internship_Type = %s")
        params.append(internship_type.strip())

    if internship_no is not None and str(internship_no).strip().lower() not in ("all", "none", ""):
        try:
            where_clauses.append("i.Internship_No = %s")
            params.append(int(internship_no))
        except (ValueError, TypeError):
            pass

    if report_grade and str(report_grade).strip().lower() not in ("all", "none", ""):
        where_clauses.append("i.Report_Grade = %s")
        params.append(report_grade.strip())

    if report_semester is not None and str(report_semester).strip().lower() not in (
        "all",
        "none",
        "",
    ):
        try:
            where_clauses.append("i.Report_Semester = %s")
            params.append(int(report_semester))
        except (ValueError, TypeError):
            pass

    if status and str(status).strip().lower() not in ("all", "none", ""):
        st = status.strip().lower()
        if st in ("completed", "complete"):
            where_clauses.append(
                "(i.End_Date <= CURDATE() AND (i.Report_Link IS NOT NULL OR i.Report_Grade IS NOT NULL))"
            )
        elif st in ("in_progress", "in progress", "ongoing"):
            where_clauses.append("(i.Start_Date <= CURDATE() AND i.End_Date >= CURDATE())")
        elif st in ("pending_report", "pending report", "pending"):
            where_clauses.append(
                "(i.End_Date <= CURDATE() AND (i.Report_Link IS NULL OR i.Report_Grade IS NULL OR i.Report_Grade = 'Pending'))"
            )
        elif st == "upcoming":
            where_clauses.append("(i.Start_Date > CURDATE())")

    where_sql = " AND ".join(where_clauses)

    # Sorting
    SORT_MAP = {
        "student_id": "i.Student_ID",
        "roll_no": "s.Roll_No",
        "student_name": "s.First_Name",
        "company_name": "c.Company_Name",
        "internship_no": "i.Internship_No",
        "internship_type": "i.Internship_Type",
        "stipend": "i.Stipend",
        "start_date": "i.Start_Date",
        "end_date": "i.End_Date",
        "credits": "i.Credits",
        "report_grade": "i.Report_Grade",
        "report_semester": "i.Report_Semester",
        "branch": "s.Branch",
        "batch_year": "s.Batch_Year",
    }
    col_sql = SORT_MAP.get(sort_by.lower(), "i.Student_ID")
    dir_sql = "DESC" if sort_dir.lower() == "desc" else "ASC"
    order_sql = f"{col_sql} {dir_sql}, i.Internship_No ASC"

    # Count total matching rows
    count_sql = f"""
        SELECT COUNT(*) AS total
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        WHERE {where_sql}
    """
    total_count = int((execute_one(count_sql, tuple(params)) or {}).get("total") or 0)

    # Pagination calculation
    pagination = None
    limit_clause = ""
    if page is not None and per_page is not None:
        p_val = max(1, int(page))
        pp_val = max(1, int(per_page))
        total_pages = max(1, math.ceil(total_count / pp_val)) if total_count > 0 else 1
        curr_offset = (p_val - 1) * pp_val
        limit_clause = f" LIMIT {pp_val} OFFSET {curr_offset}"
        pagination = {
            "total": total_count,
            "page": p_val,
            "per_page": pp_val,
            "pages": total_pages,
            "has_next": p_val < total_pages,
            "has_prev": p_val > 1,
            "start_index": curr_offset + 1 if total_count > 0 else 0,
            "end_index": min(curr_offset + pp_val, total_count),
        }
    elif limit is not None:
        off = int(offset or 0)
        limit_clause = f" LIMIT {int(limit)} OFFSET {off}"

    query_sql = f"""
        SELECT i.Internship_ID, i.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, s.Batch_Year, s.CGPA, s.Email,
               i.Company_ID, c.Company_Name, c.Company_Type,
               i.Opportunity_ID, o.Role AS Opportunity_Role,
               i.Requirement_ID, ir.Prescribed_Period, ir.Required_Result_Semester, ir.Report_Submission_Semester,
               i.Internship_No, i.Internship_Type, i.Role, i.Interview_Rounds, i.Stipend,
               i.Start_Date, i.End_Date, i.Credits, i.Report_Semester, i.Report_Link,
               i.Report_Grade, i.Certificate_Link,
               sr.SGPA AS Prerequisite_Semester_SGPA,
               sr.Total_Credits AS Prerequisite_Credits
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        LEFT JOIN OPPORTUNITY o ON i.Opportunity_ID = o.Opportunity_ID
        LEFT JOIN INTERNSHIP_REQUIREMENT ir ON i.Requirement_ID = ir.Requirement_ID
        LEFT JOIN SEMESTER_RESULT sr ON i.Student_ID = sr.Student_ID 
                                    AND ir.Required_Result_Semester = sr.Semester
        WHERE {where_sql}
        ORDER BY {order_sql}
        {limit_clause}
    """
    rows = execute_query(query_sql, tuple(params))
    for r in rows:
        r["Stipend"] = float(r["Stipend"])
        r["CGPA"] = float(r["CGPA"])
        r["Start_Date"] = str(r["Start_Date"])
        r["End_Date"] = str(r["End_Date"])
        r["Student_Name"] = f"{r['First_Name']} {r.get('Last_Name') or ''}".strip()
        if r.get("Prerequisite_Semester_SGPA") is not None:
            r["Prerequisite_Semester_SGPA"] = float(r["Prerequisite_Semester_SGPA"])

        duration = calculate_internship_duration(r["Start_Date"], r["End_Date"])
        r["Duration_Days"] = duration["days"]
        r["Duration_Weeks"] = duration["weeks"]
        r["Duration_Months"] = duration["months"]
        r["Duration_Str"] = duration["duration_str"]

        r["Status"] = determine_internship_status(
            r["Start_Date"],
            r["End_Date"],
            r.get("Report_Link"),
            r.get("Report_Grade"),
            r.get("Certificate_Link"),
        )

        # Eligibility check using joined prerequisite SGPA (zero extra queries)
        if r["Internship_Type"] == "Additional":
            r["Is_Eligible"] = True
            r["Eligibility_Status"] = "Optional"
        elif r.get("Prerequisite_Semester_SGPA") is not None:
            r["Is_Eligible"] = float(r["Prerequisite_Semester_SGPA"]) >= 6.00
            r["Eligibility_Status"] = "Eligible" if r["Is_Eligible"] else "Ineligible"
        else:
            r["Is_Eligible"] = False
            r["Eligibility_Status"] = "Prerequisite Missing"

    if as_dict:
        return {
            "results": rows,
            "total": total_count,
            "pagination": pagination
            or {
                "total": total_count,
                "page": 1,
                "per_page": total_count or 1,
                "pages": 1,
                "has_next": False,
                "has_prev": False,
                "start_index": 1 if total_count > 0 else 0,
                "end_index": total_count,
            },
        }

    return rows


def update_internship(internship_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Updates internship attributes with constraint validation."""
    existing = get_internship(internship_id)
    validate_internship_payload(data, is_update=True)

    itype = data.get("Internship_Type", existing["Internship_Type"])
    req_id = data.get("Requirement_ID", existing["Requirement_ID"])
    internship_no = data.get("Internship_No", existing["Internship_No"])

    if itype == "Mandatory":
        if not req_id:
            raise ValidationError("Mandatory internships must link to an INTERNSHIP_REQUIREMENT.")
        req = execute_one(
            "SELECT Internship_No FROM INTERNSHIP_REQUIREMENT WHERE Requirement_ID = %s", (req_id,)
        )
        if not req:
            raise NotFoundError(f"Requirement ID {req_id} does not exist.")
        if req["Internship_No"] != internship_no:
            raise ValidationError(
                f"Mismatch: Mandatory Internship #{internship_no} must link to Requirement #{internship_no}."
            )
    else:
        if req_id is not None:
            raise ValidationError(
                "Additional internships cannot link to a requirement (Requirement_ID must be null)."
            )

    updatable = [
        "Company_ID",
        "Opportunity_ID",
        "Requirement_ID",
        "Internship_No",
        "Internship_Type",
        "Role",
        "Interview_Rounds",
        "Stipend",
        "Start_Date",
        "End_Date",
        "Credits",
        "Report_Semester",
        "Report_Link",
        "Report_Grade",
        "Certificate_Link",
    ]
    set_clauses = []
    params: List[Any] = []

    for field in updatable:
        if field in data:
            val = data[field]
            if field == "Stipend" and val is not None:
                val = round(float(val), 2)
            elif (
                field
                in (
                    "Company_ID",
                    "Opportunity_ID",
                    "Requirement_ID",
                    "Internship_No",
                    "Interview_Rounds",
                    "Credits",
                    "Report_Semester",
                )
                and val is not None
            ):
                val = int(val)
            elif val is not None:
                val = str(val).strip()
            set_clauses.append(f"{field} = %s")
            params.append(val)

    if set_clauses:
        update_sql = f"UPDATE INTERNSHIP SET {', '.join(set_clauses)} WHERE Internship_ID = %s"
        params.append(internship_id)
        with get_cursor(commit=True) as cursor:
            cursor.execute(update_sql, tuple(params))

    logger.info("Updated internship ID %s", internship_id)
    return get_internship(internship_id)


def delete_internship(internship_id: int) -> Dict[str, Any]:
    """Deletes an internship record."""
    intern = execute_one(
        "SELECT Internship_ID, Student_ID, Internship_No, Internship_Type FROM INTERNSHIP WHERE Internship_ID = %s",
        (internship_id,),
    )
    if not intern:
        raise NotFoundError(f"Internship with ID {internship_id} not found.")

    with get_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM INTERNSHIP WHERE Internship_ID = %s", (internship_id,))

    logger.info(
        "Deleted %s internship #%s (ID: %s)",
        intern["Internship_Type"],
        intern["Internship_No"],
        internship_id,
    )
    return {
        "success": True,
        "message": f"Internship #{intern['Internship_No']} ({intern['Internship_Type']}) deleted successfully.",
        "deleted_internship_id": internship_id,
    }


def get_mandatory_internships_with_prerequisite_sgpa() -> List[Dict[str, Any]]:
    """Demonstrates 3NF normalization:

    Semester 3 SGPA (for Internship 1) and Semester 5 SGPA (for Internship 2) are dynamically
    fetched by joining:
        INTERNSHIP i
        -> INTERNSHIP_REQUIREMENT ir (on Requirement_ID)
        -> SEMESTER_RESULT sr (on Student_ID AND sr.Semester = ir.Required_Result_Semester)

    Zero redundant SGPA columns stored in the INTERNSHIP table!
    """
    sql = """
        SELECT 
            i.Internship_ID,
            i.Student_ID,
            s.Roll_No,
            CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Student_Name,
            s.Branch,
            s.Batch_Year,
            c.Company_Name,
            i.Internship_No,
            i.Internship_Type,
            i.Role,
            i.Stipend,
            i.Start_Date,
            i.End_Date,
            i.Credits,
            i.Report_Semester,
            i.Report_Link,
            i.Certificate_Link,
            ir.Prescribed_Period,
            ir.Required_Result_Semester,
            sr.SGPA AS Prerequisite_Semester_SGPA,
            sr.Total_Credits AS Prerequisite_Credits,
            i.Report_Grade
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        JOIN INTERNSHIP_REQUIREMENT ir ON i.Requirement_ID = ir.Requirement_ID
        LEFT JOIN SEMESTER_RESULT sr ON i.Student_ID = sr.Student_ID 
                                    AND ir.Required_Result_Semester = sr.Semester
        WHERE i.Internship_Type = 'Mandatory'
        ORDER BY i.Internship_No ASC, sr.SGPA DESC;
    """
    rows = execute_query(sql)
    for r in rows:
        r["Stipend"] = float(r["Stipend"])
        r["Start_Date"] = str(r["Start_Date"])
        r["End_Date"] = str(r["End_Date"])
        if r.get("Prerequisite_Semester_SGPA") is not None:
            r["Prerequisite_Semester_SGPA"] = float(r["Prerequisite_Semester_SGPA"])

        duration = calculate_internship_duration(r["Start_Date"], r["End_Date"])
        r["Duration_Days"] = duration["days"]
        r["Duration_Weeks"] = duration["weeks"]
        r["Duration_Months"] = duration["months"]
        r["Duration_Str"] = duration["duration_str"]

        r["Status"] = determine_internship_status(
            r["Start_Date"],
            r["End_Date"],
            r.get("Report_Link"),
            r.get("Report_Grade"),
            r.get("Certificate_Link"),
        )

        prereq_sgpa = r.get("Prerequisite_Semester_SGPA")
        if prereq_sgpa is not None:
            if prereq_sgpa >= 6.00:
                r["Is_Eligible"] = True
                r["Eligibility_Status"] = "Eligible"
            else:
                r["Is_Eligible"] = False
                r["Eligibility_Status"] = "Ineligible"
        else:
            r["Is_Eligible"] = False
            r["Eligibility_Status"] = "Prerequisite Missing"

    return rows


def get_students_missing_mandatory_internships(
    target_internship_no: Optional[int] = None,
    branch: Optional[str] = None,
    batch_year: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Identifies students who have NOT completed mandatory internships."""
    where_conds = ["(i1.Internship_ID IS NULL OR i2.Internship_ID IS NULL)"]
    params: List[Any] = []

    if branch and str(branch).strip().lower() not in ("all", "none", ""):
        where_conds.append("s.Branch = %s")
        params.append(branch.strip())

    if batch_year is not None and str(batch_year).strip().lower() not in ("all", "none", ""):
        try:
            where_conds.append("s.Batch_Year = %s")
            params.append(int(batch_year))
        except (ValueError, TypeError):
            pass

    clause = " AND ".join(where_conds)
    sql = f"""
        SELECT 
            s.Student_ID,
            s.Roll_No,
            s.First_Name,
            s.Last_Name,
            s.Branch,
            s.Batch_Year,
            s.CGPA,
            s.Email,
            CASE WHEN i1.Internship_ID IS NOT NULL THEN 'Completed' ELSE 'MISSING' END AS Mandatory_I1_Status,
            CASE WHEN i2.Internship_ID IS NOT NULL THEN 'Completed' ELSE 'MISSING' END AS Mandatory_I2_Status,
            COALESCE(c1.Company_Name, 'None') AS I1_Company,
            COALESCE(c2.Company_Name, 'None') AS I2_Company
        FROM STUDENT s
        LEFT JOIN INTERNSHIP i1 ON s.Student_ID = i1.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = 'Mandatory'
        LEFT JOIN COMPANY c1 ON i1.Company_ID = c1.Company_ID
        LEFT JOIN INTERNSHIP i2 ON s.Student_ID = i2.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = 'Mandatory'
        LEFT JOIN COMPANY c2 ON i2.Company_ID = c2.Company_ID
        WHERE {clause}
        ORDER BY s.Batch_Year ASC, s.Roll_No ASC;
    """
    rows = execute_query(sql, tuple(params))
    for r in rows:
        r["CGPA"] = float(r["CGPA"])
        r["Full_Name"] = f"{r['First_Name']} {r.get('Last_Name') or ''}".strip()

    if target_internship_no == 1:
        return [r for r in rows if r["Mandatory_I1_Status"] == "MISSING"]
    elif target_internship_no == 2:
        return [r for r in rows if r["Mandatory_I2_Status"] == "MISSING"]

    return rows


def get_branch_internship_statistics() -> List[Dict[str, Any]]:
    """Computes branch-wise internship completion statistics."""
    sql = """
        SELECT 
            s.Branch,
            COUNT(DISTINCT s.Student_ID) AS total_students,
            COUNT(DISTINCT CASE WHEN i.Internship_No = 1 AND i.Internship_Type = 'Mandatory' THEN s.Student_ID END) AS i1_completed,
            COUNT(DISTINCT CASE WHEN i.Internship_No = 2 AND i.Internship_Type = 'Mandatory' THEN s.Student_ID END) AS i2_completed,
            COUNT(DISTINCT CASE WHEN i.Internship_Type = 'Additional' THEN i.Internship_ID END) AS additional_count,
            ROUND(COALESCE(AVG(i.Stipend), 0), 2) AS avg_stipend,
            ROUND(COALESCE(MAX(i.Stipend), 0), 2) AS max_stipend
        FROM STUDENT s
        LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
        GROUP BY s.Branch
        ORDER BY s.Branch ASC
    """
    rows = execute_query(sql)

    # Students who completed both mandatory internships per branch
    both_sql = """
        SELECT s.Branch, COUNT(DISTINCT s.Student_ID) AS both_completed
        FROM STUDENT s
        JOIN INTERNSHIP i1 ON s.Student_ID = i1.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = 'Mandatory'
        JOIN INTERNSHIP i2 ON s.Student_ID = i2.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = 'Mandatory'
        GROUP BY s.Branch
    """
    both_map = {r["Branch"]: int(r["both_completed"]) for r in execute_query(both_sql)}

    BRANCH_NAMES = {
        "CSE": "Computer Science & Engineering",
        "ECE": "Electronics & Communication Engineering",
        "IT": "Information Technology",
        "ME": "Mechanical Engineering",
        "CE": "Civil Engineering",
        "EE": "Electrical Engineering",
    }

    results = []
    for r in rows:
        branch = r["Branch"]
        total = int(r["total_students"])
        i1 = int(r["i1_completed"])
        i2 = int(r["i2_completed"])
        both = both_map.get(branch, 0)
        compliance_rate = round((both / total * 100), 1) if total > 0 else 0.0
        i1_rate = round((i1 / total * 100), 1) if total > 0 else 0.0
        i2_rate = round((i2 / total * 100), 1) if total > 0 else 0.0

        results.append(
            {
                "Branch": branch,
                "Branch_Name": BRANCH_NAMES.get(branch, branch),
                "total_students": total,
                "i1_completed": i1,
                "i1_rate": i1_rate,
                "i2_completed": i2,
                "i2_rate": i2_rate,
                "both_completed": both,
                "compliance_rate": compliance_rate,
                "additional_count": int(r["additional_count"]),
                "avg_stipend": float(r["avg_stipend"]),
                "max_stipend": float(r["max_stipend"]),
            }
        )
    return results


def get_batch_compliance_reports() -> List[Dict[str, Any]]:
    """Computes batch-wise compliance reports."""
    sql = """
        SELECT 
            s.Batch_Year,
            COUNT(DISTINCT s.Student_ID) AS total_students,
            COUNT(DISTINCT CASE WHEN i.Internship_No = 1 AND i.Internship_Type = 'Mandatory' THEN s.Student_ID END) AS i1_completed,
            COUNT(DISTINCT CASE WHEN i.Internship_No = 2 AND i.Internship_Type = 'Mandatory' THEN s.Student_ID END) AS i2_completed,
            COUNT(DISTINCT CASE WHEN i.Internship_Type = 'Additional' THEN i.Internship_ID END) AS additional_count,
            ROUND(COALESCE(AVG(i.Stipend), 0), 2) AS avg_stipend
        FROM STUDENT s
        LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
        GROUP BY s.Batch_Year
        ORDER BY s.Batch_Year ASC
    """
    rows = execute_query(sql)

    both_sql = """
        SELECT s.Batch_Year, COUNT(DISTINCT s.Student_ID) AS both_completed
        FROM STUDENT s
        JOIN INTERNSHIP i1 ON s.Student_ID = i1.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = 'Mandatory'
        JOIN INTERNSHIP i2 ON s.Student_ID = i2.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = 'Mandatory'
        GROUP BY s.Batch_Year
    """
    both_map = {r["Batch_Year"]: int(r["both_completed"]) for r in execute_query(both_sql)}

    results = []
    for r in rows:
        batch = int(r["Batch_Year"])
        total = int(r["total_students"])
        i1 = int(r["i1_completed"])
        i2 = int(r["i2_completed"])
        both = both_map.get(batch, 0)
        compliance_rate = round((both / total * 100), 1) if total > 0 else 0.0
        missing_count = total - both

        results.append(
            {
                "Batch_Year": batch,
                "total_students": total,
                "i1_completed": i1,
                "i1_rate": round((i1 / total * 100), 1) if total > 0 else 0.0,
                "i2_completed": i2,
                "i2_rate": round((i2 / total * 100), 1) if total > 0 else 0.0,
                "both_completed": both,
                "compliance_rate": compliance_rate,
                "missing_count": missing_count,
                "additional_count": int(r["additional_count"]),
                "avg_stipend": float(r["avg_stipend"]),
            }
        )
    return results


def get_pending_internship_reports() -> List[Dict[str, Any]]:
    """Identifies internships with pending report submissions or pending evaluation grades."""
    return list_internships(status="pending_report")


def get_internship_dashboard_analytics() -> Dict[str, Any]:
    """Computes comprehensive executive analytics for the Internship Management Dashboard."""
    # 1. Total records
    tot_res = (
        execute_one(
            "SELECT COUNT(*) AS total_internships, ROUND(COALESCE(AVG(Stipend), 0), 2) AS avg_stipend, ROUND(COALESCE(MAX(Stipend), 0), 2) AS max_stipend FROM INTERNSHIP"
        )
        or {}
    )
    total_internships = int(tot_res.get("total_internships") or 0)
    avg_stipend = float(tot_res.get("avg_stipend") or 0.0)
    max_stipend = float(tot_res.get("max_stipend") or 0.0)

    # 2. Mandatory I1 and I2 counts
    m_res = execute_one("""
        SELECT 
            COUNT(CASE WHEN Internship_No = 1 AND Internship_Type = 'Mandatory' THEN 1 END) AS i1_count,
            COUNT(CASE WHEN Internship_No = 2 AND Internship_Type = 'Mandatory' THEN 1 END) AS i2_count,
            COUNT(CASE WHEN Internship_Type = 'Additional' THEN 1 END) AS additional_count
        FROM INTERNSHIP
    """) or {}
    i1_count = int(m_res.get("i1_count") or 0)
    i2_count = int(m_res.get("i2_count") or 0)
    additional_count = int(m_res.get("additional_count") or 0)

    # 3. Overall students and compliance
    stud_count_res = execute_one("SELECT COUNT(*) AS total_students FROM STUDENT") or {}
    total_students = int(stud_count_res.get("total_students") or 0)

    both_sql = """
        SELECT COUNT(DISTINCT s.Student_ID) AS fully_compliant
        FROM STUDENT s
        JOIN INTERNSHIP i1 ON s.Student_ID = i1.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = 'Mandatory'
        JOIN INTERNSHIP i2 ON s.Student_ID = i2.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = 'Mandatory'
    """
    comp_res = execute_one(both_sql) or {}
    fully_compliant = int(comp_res.get("fully_compliant") or 0)
    compliance_rate = (
        round((fully_compliant / total_students * 100), 1) if total_students > 0 else 0.0
    )

    # 4. Pending reports
    pending_sql = """
        SELECT COUNT(*) AS pending_count FROM INTERNSHIP
        WHERE End_Date <= CURDATE() AND (Report_Link IS NULL OR Report_Grade IS NULL OR Report_Grade = 'Pending')
    """
    pending_count = int((execute_one(pending_sql) or {}).get("pending_count") or 0)

    # 5. Report Grade Distribution
    grade_sql = """
        SELECT COALESCE(Report_Grade, 'Ungraded') AS grade, COUNT(*) AS count
        FROM INTERNSHIP
        GROUP BY COALESCE(Report_Grade, 'Ungraded')
        ORDER BY count DESC
    """
    grade_distribution = execute_query(grade_sql)

    # 6. Branch Statistics and Batch Reports
    branch_stats = get_branch_internship_statistics()
    batch_reports = get_batch_compliance_reports()

    # 7. Status distribution
    status_counts = {"Completed": 0, "In Progress": 0, "Pending Report": 0, "Upcoming": 0}
    status_sql = """
        SELECT 
            CASE 
                WHEN Start_Date > CURDATE() THEN 'Upcoming'
                WHEN Start_Date <= CURDATE() AND End_Date >= CURDATE() THEN 'In Progress'
                WHEN End_Date <= CURDATE() AND (Report_Link IS NOT NULL OR Report_Grade IS NOT NULL) THEN 'Completed'
                ELSE 'Pending Report'
            END AS status_group,
            COUNT(*) AS count
        FROM INTERNSHIP
        GROUP BY status_group
    """
    for sr in execute_query(status_sql):
        if sr["status_group"] in status_counts:
            status_counts[sr["status_group"]] = int(sr["count"])

    return {
        "kpis": {
            "total_internships": total_internships,
            "mandatory_i1_completed": i1_count,
            "mandatory_i2_completed": i2_count,
            "additional_internships": additional_count,
            "pending_reports": pending_count,
            "total_students": total_students,
            "fully_compliant_students": fully_compliant,
            "compliance_rate": compliance_rate,
            "avg_stipend": avg_stipend,
            "highest_stipend": max_stipend,
        },
        "grade_distribution": grade_distribution,
        "status_distribution": [{"status": k, "count": v} for k, v in status_counts.items()],
        "type_distribution": {
            "mandatory_1": i1_count,
            "mandatory_2": i2_count,
            "additional": additional_count,
        },
        "branch_stats": branch_stats,
        "batch_reports": batch_reports,
    }

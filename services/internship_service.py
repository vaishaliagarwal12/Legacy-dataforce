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
            months = round(days / 30.44, 1)
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
    """Determines internship operational and compliance status."""
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
    """Calculates student academic eligibility for an internship from STUDENT record."""
    student = execute_one(
        "SELECT Student_ID, Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs FROM STUDENT WHERE Student_ID = %s",
        (student_id,),
    )
    if not student:
        raise NotFoundError(f"Student with ID {student_id} not found.")

    student_name = f"{student['First_Name']} {student.get('Last_Name') or ''}".strip()
    cgpa = float(student["CGPA"])
    backlogs = int(student["Backlogs"])
    is_eligible = backlogs == 0 and cgpa >= min_sgpa

    if internship_no == 1:
        prescribed_period = "Summer Vacation after 2nd Year (Semester 5 report, 4 credits)"
        msg = f"Candidate {'is' if is_eligible else 'is not'} eligible for Mandatory Internship #1 (CGPA: {cgpa:.2f}, Backlogs: {backlogs})."
    elif internship_no == 2:
        prescribed_period = "During 8th semester; report submitted after the end of 8th semester (4 credits)"
        msg = f"Candidate {'is' if is_eligible else 'is not'} eligible for Mandatory Internship #2 (CGPA: {cgpa:.2f}, Backlogs: {backlogs})."
    else:
        prescribed_period = "Optional Extracurricular / Voluntary"
        msg = "Additional internships are optional and have no mandatory prerequisite constraints."

    return {
        "is_eligible": is_eligible,
        "student_id": student_id,
        "roll_no": student["Roll_No"],
        "student_name": student_name,
        "internship_no": internship_no,
        "internship_type": "Mandatory" if internship_no in (1, 2) else "Additional",
        "prescribed_period": prescribed_period,
        "min_required_sgpa": min_sgpa,
        "status": "Eligible" if is_eligible else "Ineligible",
        "message": msg,
    }


def validate_internship_payload(data: Dict[str, Any], is_update: bool = False) -> None:
    """Validates internship fields, dates, and curriculum constraints (chk_internship_curriculum)."""
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

    # Date ordering check (chk_internship_dates)
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

    # Enforce curriculum constraint (chk_internship_curriculum)
    if "Internship_No" in data and data["Internship_No"] is not None:
        ino = int(data["Internship_No"])
        itype = str(data.get("Internship_Type") or "").strip()
        cred = int(data["Credits"]) if data.get("Credits") is not None and str(data["Credits"]).strip() != "" else None
        rsem = int(data["Report_Semester"]) if data.get("Report_Semester") is not None and str(data["Report_Semester"]).strip() != "" else None

        if ino == 1:
            if itype and itype != "Mandatory":
                raise ValidationError("Internship #1 must be of type 'Mandatory'.")
            if cred is not None and cred != 4:
                raise ValidationError("Internship #1 must carry exactly 4 credits.")
            if rsem is not None and rsem != 5:
                raise ValidationError("Internship #1 report must be submitted in Semester 5 (Report_Semester = 5).")
        elif ino == 2:
            if itype and itype != "Mandatory":
                raise ValidationError("Internship #2 must be of type 'Mandatory'.")
            if cred is not None and cred != 4:
                raise ValidationError("Internship #2 must carry exactly 4 credits.")
            if rsem is not None and rsem != 8:
                raise ValidationError("Internship #2 report must be submitted after the end of the 8th semester (Report_Semester = 8).")
        elif ino >= 3:
            if itype and itype != "Additional":
                raise ValidationError(f"Internship #{ino} must be of type 'Additional'.")


def create_internship(data: Dict[str, Any]) -> Dict[str, Any]:
    """Records an internship experience enforcing institutional curriculum rules."""
    validate_internship_payload(data, is_update=False)

    student_id = int(data["Student_ID"])
    company_id = int(data["Company_ID"])
    internship_no = int(data["Internship_No"])
    internship_type = str(data["Internship_Type"]).strip()
    role = str(data.get("Role", "") or "Intern").strip() or "Intern"
    rounds = int(data.get("Interview_Rounds", 1) or 1)
    stipend = round(float(data.get("Stipend", 0.0) or 0.0), 2)
    start_date = str(data["Start_Date"]).strip()
    end_date = str(data["End_Date"]).strip()

    if internship_no == 1:
        internship_type = "Mandatory"
        credits = 4
        report_sem = 5
    elif internship_no == 2:
        internship_type = "Mandatory"
        credits = 4
        report_sem = 8
    else:
        internship_type = "Additional"
        credits = int(data["Credits"]) if data.get("Credits") is not None and str(data["Credits"]).strip() != "" else None
        report_sem = int(data["Report_Semester"]) if data.get("Report_Semester") is not None and str(data["Report_Semester"]).strip() != "" else None

    report_link = str(data.get("Report_Link", "") or "").strip() or None
    report_grade = str(data.get("Report_Grade", "") or "").strip() or None
    cert_link = str(data.get("Certificate_Link", "") or "").strip() or None

    # Verify Student exists
    student = execute_one(
        "SELECT Student_ID, Roll_No FROM STUDENT WHERE Student_ID = %s", (student_id,)
    )
    if not student:
        raise NotFoundError(f"Student with ID {student_id} does not exist.")

    # Verify Company exists
    company = execute_one(
        "SELECT Company_ID, Company_Name FROM COMPANY WHERE Company_ID = %s", (company_id,)
    )
    if not company:
        raise NotFoundError(f"Company with ID {company_id} does not exist.")

    # Unique (Student_ID, Internship_No) primary key constraint
    existing_no = execute_one(
        "SELECT Internship_ID, Internship_Type, Role FROM INTERNSHIP WHERE Student_ID = %s AND Internship_No = %s",
        (student_id, internship_no),
    )
    if existing_no:
        raise ConflictError(
            f"Student {student['Roll_No']} already has an internship recorded with number {internship_no} "
            f"('{existing_no['Role']}' - Type: {existing_no['Internship_Type']})."
        )

    insert_sql = """
        INSERT INTO INTERNSHIP (
            Student_ID, Company_ID, Internship_No,
            Internship_Type, Role, Interview_Rounds, Stipend, Start_Date, End_Date,
            Credits, Report_Semester, Report_Link, Report_Grade, Certificate_Link
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            insert_sql,
            (
                student_id,
                company_id,
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
    """Retrieves full internship details with joined student and company metadata."""
    sql = """
        SELECT i.Internship_ID, i.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, s.Batch_Year, s.CGPA, s.Email,
               i.Company_ID, c.Company_Name, c.Company_Type, c.Location AS Company_Location, c.Website AS Company_Website,
               i.Internship_No, i.Internship_Type, i.Role, i.Interview_Rounds, i.Stipend,
               i.Start_Date, i.End_Date, i.Credits, i.Report_Semester, i.Report_Link,
               i.Report_Grade, i.Certificate_Link
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
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
    **kwargs: Any,
) -> Any:
    """Lists, filters, and searches student internships with canonical 7-table schema."""
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

    count_sql = f"""
        SELECT COUNT(*) AS total
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        WHERE {where_sql}
    """
    total_count = int((execute_one(count_sql, tuple(params)) or {}).get("total") or 0)

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
               i.Internship_No, i.Internship_Type, i.Role, i.Interview_Rounds, i.Stipend,
               i.Start_Date, i.End_Date, i.Credits, i.Report_Semester, i.Report_Link,
               i.Report_Grade, i.Certificate_Link
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
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
        r["Is_Eligible"] = r["CGPA"] >= 6.00
        r["Eligibility_Status"] = "Eligible" if r["Is_Eligible"] else "Ineligible"

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
    """Updates internship attributes with curriculum constraint validation."""
    existing = get_internship(internship_id)
    validate_internship_payload(data, is_update=True)

    updatable = [
        "Company_ID",
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
    """Retrieves mandatory internships joined with Student and Company."""
    sql = """
        SELECT 
            i.Internship_ID,
            i.Student_ID,
            s.Roll_No,
            CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Student_Name,
            s.Branch,
            s.Batch_Year,
            s.CGPA,
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
            i.Report_Grade
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        WHERE i.Internship_Type = 'Mandatory'
        ORDER BY i.Internship_No ASC, s.CGPA DESC;
    """
    rows = execute_query(sql)
    for r in rows:
        r["Stipend"] = float(r["Stipend"])
        r["CGPA"] = float(r["CGPA"])
        r["Start_Date"] = str(r["Start_Date"])
        r["End_Date"] = str(r["End_Date"])

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
        r["Is_Eligible"] = r["CGPA"] >= 6.00
        r["Eligibility_Status"] = "Eligible" if r["Is_Eligible"] else "Ineligible"

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
    tot_res = (
        execute_one(
            "SELECT COUNT(*) AS total_internships, ROUND(COALESCE(AVG(Stipend), 0), 2) AS avg_stipend, ROUND(COALESCE(MAX(Stipend), 0), 2) AS max_stipend FROM INTERNSHIP"
        )
        or {}
    )
    total_internships = int(tot_res.get("total_internships") or 0)
    avg_stipend = float(tot_res.get("avg_stipend") or 0.0)
    max_stipend = float(tot_res.get("max_stipend") or 0.0)

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

    pending_sql = """
        SELECT COUNT(*) AS pending_count FROM INTERNSHIP
        WHERE End_Date <= CURDATE() AND (Report_Link IS NULL OR Report_Grade IS NULL OR Report_Grade = 'Pending')
    """
    pending_count = int((execute_one(pending_sql) or {}).get("pending_count") or 0)

    grade_sql = """
        SELECT COALESCE(Report_Grade, 'Ungraded') AS grade, COUNT(*) AS count
        FROM INTERNSHIP
        GROUP BY COALESCE(Report_Grade, 'Ungraded')
        ORDER BY count DESC
    """
    grade_distribution = execute_query(grade_sql)

    branch_stats = get_branch_internship_statistics()
    batch_reports = get_batch_compliance_reports()

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

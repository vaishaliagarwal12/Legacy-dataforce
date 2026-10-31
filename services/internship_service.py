import logging
from typing import Dict, Any, List, Optional
from db.connection import get_cursor, execute_one, execute_query
from services.exceptions import ValidationError, NotFoundError, ConflictError

logger = logging.getLogger(__name__)

VALID_INTERNSHIP_TYPES = ("Mandatory", "Additional")


def validate_internship_payload(data: Dict[str, Any], is_update: bool = False) -> None:
    """Validates internship fields, dates, and mandatory/additional requirement constraints."""
    if not is_update:
        required = ["Student_ID", "Company_ID", "Internship_No", "Internship_Type", "Start_Date", "End_Date"]
        for field in required:
            if field not in data or data[field] is None:
                raise ValidationError(f"Missing required field: '{field}'")

    if "Internship_Type" in data and data["Internship_Type"] is not None:
        itype = str(data["Internship_Type"]).strip()
        if itype not in VALID_INTERNSHIP_TYPES:
            raise ValidationError(f"Internship_Type must be one of: {', '.join(VALID_INTERNSHIP_TYPES)}")

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
            raise ValidationError(f"Invalid dates: End_Date ({end_str}) cannot be earlier than Start_Date ({start_str})")

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
    credits = int(data["Credits"]) if data.get("Credits") is not None else (4 if internship_type == "Mandatory" else 0)
    report_sem = int(data["Report_Semester"]) if data.get("Report_Semester") is not None else (5 if internship_no == 1 else 7 if internship_no == 2 else None)
    report_link = str(data.get("Report_Link", "") or "").strip() or None
    report_grade = str(data.get("Report_Grade", "") or "").strip() or None
    cert_link = str(data.get("Certificate_Link", "") or "").strip() or None

    # 1. Verify Student exists
    student = execute_one("SELECT Student_ID, Roll_No FROM STUDENT WHERE Student_ID = %s", (student_id,))
    if not student:
        raise NotFoundError(f"Student with ID {student_id} does not exist.")

    # 2. Verify Company exists
    company = execute_one("SELECT Company_ID, Company_Name FROM COMPANY WHERE Company_ID = %s", (company_id,))
    if not company:
        raise NotFoundError(f"Company with ID {company_id} does not exist.")

    # 3. Unique (Student_ID, Internship_No) check
    existing_no = execute_one(
        "SELECT Internship_ID, Internship_Type, Role FROM INTERNSHIP WHERE Student_ID = %s AND Internship_No = %s",
        (student_id, internship_no)
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
            (req_id,)
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
            (student_id, company_id, opp_id, req_id, internship_no,
             internship_type, role, rounds, stipend, start_date, end_date,
             credits, report_sem, report_link, report_grade, cert_link)
        )
        internship_id = cursor.lastrowid

    logger.info("Created %s Internship #%s (ID: %s) for student %s", internship_type, internship_no, internship_id, student["Roll_No"])
    return get_internship(internship_id)


def get_internship(internship_id: int) -> Dict[str, Any]:
    """Retrieves full internship details.
    
    Demonstrates zero-redundancy normalization:
    If this is a Mandatory internship, it dynamically queries the prerequisite semester result
    (Sem 3 for Internship 1, Sem 5 for Internship 2) by joining:
    INTERNSHIP -> INTERNSHIP_REQUIREMENT -> SEMESTER_RESULT
    without storing SGPA twice!
    """
    sql = """
        SELECT i.Internship_ID, i.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, s.CGPA,
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
        WHERE i.Internship_ID = %s
    """
    row = execute_one(sql, (internship_id,))
    if not row:
        raise NotFoundError(f"Internship with ID {internship_id} not found.")

    row["Stipend"] = float(row["Stipend"])
    row["CGPA"] = float(row["CGPA"])
    row["Start_Date"] = str(row["Start_Date"])
    row["End_Date"] = str(row["End_Date"])
    if row.get("Prerequisite_Semester_SGPA") is not None:
        row["Prerequisite_Semester_SGPA"] = float(row["Prerequisite_Semester_SGPA"])

    return row


def list_internships(
    student_id: Optional[int] = None,
    company_id: Optional[int] = None,
    internship_type: Optional[str] = None,
    internship_no: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Lists, filters, and searches student internships."""
    where_clauses = ["1=1"]
    params: List[Any] = []

    if student_id is not None:
        where_clauses.append("i.Student_ID = %s")
        params.append(int(student_id))

    if company_id is not None:
        where_clauses.append("i.Company_ID = %s")
        params.append(int(company_id))

    if internship_type:
        where_clauses.append("i.Internship_Type = %s")
        params.append(internship_type.strip())

    if internship_no is not None:
        where_clauses.append("i.Internship_No = %s")
        params.append(int(internship_no))

    where_sql = " AND ".join(where_clauses)
    query_sql = f"""
        SELECT i.Internship_ID, i.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch,
               i.Company_ID, c.Company_Name, i.Internship_No, i.Internship_Type,
               i.Role, i.Stipend, i.Start_Date, i.End_Date, i.Credits, i.Requirement_ID,
               ir.Required_Result_Semester,
               sr.SGPA AS Prerequisite_Semester_SGPA
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        LEFT JOIN INTERNSHIP_REQUIREMENT ir ON i.Requirement_ID = ir.Requirement_ID
        LEFT JOIN SEMESTER_RESULT sr ON i.Student_ID = sr.Student_ID 
                                    AND ir.Required_Result_Semester = sr.Semester
        WHERE {where_sql}
        ORDER BY i.Student_ID ASC, i.Internship_No ASC
    """
    rows = execute_query(query_sql, tuple(params))
    for r in rows:
        r["Stipend"] = float(r["Stipend"])
        r["Start_Date"] = str(r["Start_Date"])
        r["End_Date"] = str(r["End_Date"])
        if r.get("Prerequisite_Semester_SGPA") is not None:
            r["Prerequisite_Semester_SGPA"] = float(r["Prerequisite_Semester_SGPA"])
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
        req = execute_one("SELECT Internship_No FROM INTERNSHIP_REQUIREMENT WHERE Requirement_ID = %s", (req_id,))
        if not req:
            raise NotFoundError(f"Requirement ID {req_id} does not exist.")
        if req["Internship_No"] != internship_no:
            raise ValidationError(
                f"Mismatch: Mandatory Internship #{internship_no} must link to Requirement #{internship_no}."
            )
    else:
        if req_id is not None:
            raise ValidationError("Additional internships cannot link to a requirement (Requirement_ID must be null).")

    updatable = [
        "Company_ID", "Opportunity_ID", "Requirement_ID", "Internship_No", "Internship_Type",
        "Role", "Interview_Rounds", "Stipend", "Start_Date", "End_Date",
        "Credits", "Report_Semester", "Report_Link", "Report_Grade", "Certificate_Link"
    ]
    set_clauses = []
    params: List[Any] = []

    for field in updatable:
        if field in data:
            val = data[field]
            if field == "Stipend" and val is not None:
                val = round(float(val), 2)
            elif field in ("Company_ID", "Opportunity_ID", "Requirement_ID", "Internship_No", "Interview_Rounds", "Credits", "Report_Semester") and val is not None:
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
    intern = execute_one("SELECT Internship_ID, Student_ID, Internship_No, Internship_Type FROM INTERNSHIP WHERE Internship_ID = %s", (internship_id,))
    if not intern:
        raise NotFoundError(f"Internship with ID {internship_id} not found.")

    with get_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM INTERNSHIP WHERE Internship_ID = %s", (internship_id,))

    logger.info("Deleted %s internship #%s (ID: %s)", intern["Internship_Type"], intern["Internship_No"], internship_id)
    return {
        "success": True,
        "message": f"Internship #{intern['Internship_No']} ({intern['Internship_Type']}) deleted successfully.",
        "deleted_internship_id": internship_id,
    }


# ==============================================================================
# Analytical Queries: Prerequisite SGPA Joins & Missing Mandatory Internships
# ==============================================================================

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
            c.Company_Name,
            i.Internship_No,
            i.Internship_Type,
            i.Role,
            ir.Prescribed_Period,
            ir.Required_Result_Semester,
            sr.SGPA AS Prerequisite_Semester_SGPA,
            sr.Total_Credits AS Prerequisite_Credits,
            i.Report_Grade
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        JOIN INTERNSHIP_REQUIREMENT ir ON i.Requirement_ID = ir.Requirement_ID
        JOIN SEMESTER_RESULT sr ON i.Student_ID = sr.Student_ID 
                               AND ir.Required_Result_Semester = sr.Semester
        WHERE i.Internship_Type = 'Mandatory'
        ORDER BY i.Internship_No ASC, sr.SGPA DESC;
    """
    rows = execute_query(sql)
    for r in rows:
        r["Prerequisite_Semester_SGPA"] = float(r["Prerequisite_Semester_SGPA"])
    return rows


def get_students_missing_mandatory_internships(target_internship_no: Optional[int] = None) -> List[Dict[str, Any]]:
    """Identifies students who have NOT completed mandatory internships.
    
    Can evaluate Internship 1 (Summer after 2nd year), Internship 2 (Summer after 3rd year), or both.
    """
    sql = """
        SELECT 
            s.Student_ID,
            s.Roll_No,
            s.First_Name,
            s.Last_Name,
            s.Branch,
            s.Batch_Year,
            s.CGPA,
            CASE WHEN i1.Internship_ID IS NOT NULL THEN 'Completed' ELSE 'MISSING' END AS Mandatory_I1_Status,
            CASE WHEN i2.Internship_ID IS NOT NULL THEN 'Completed' ELSE 'MISSING' END AS Mandatory_I2_Status,
            COALESCE(c1.Company_Name, 'None') AS I1_Company,
            COALESCE(c2.Company_Name, 'None') AS I2_Company
        FROM STUDENT s
        LEFT JOIN INTERNSHIP i1 ON s.Student_ID = i1.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = 'Mandatory'
        LEFT JOIN COMPANY c1 ON i1.Company_ID = c1.Company_ID
        LEFT JOIN INTERNSHIP i2 ON s.Student_ID = i2.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = 'Mandatory'
        LEFT JOIN COMPANY c2 ON i2.Company_ID = c2.Company_ID
        WHERE (i1.Internship_ID IS NULL OR i2.Internship_ID IS NULL)
        ORDER BY s.Batch_Year ASC, s.Roll_No ASC;
    """
    rows = execute_query(sql)
    for r in rows:
        r["CGPA"] = float(r["CGPA"])

    if target_internship_no == 1:
        return [r for r in rows if r["Mandatory_I1_Status"] == "MISSING"]
    elif target_internship_no == 2:
        return [r for r in rows if r["Mandatory_I2_Status"] == "MISSING"]

    return rows

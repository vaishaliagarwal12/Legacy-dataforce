import logging
from typing import Dict, Any, List, Optional
from db.connection import get_cursor, execute_one, execute_query
from services.exceptions import ValidationError, NotFoundError, ConflictError

logger = logging.getLogger(__name__)

VALID_OFFER_STATUSES = ("Offered", "Accepted", "Joined", "Declined")
VALID_PLACEMENT_TYPES = ("On-campus", "Off-campus")
VALID_BOOLEAN_STRINGS = ("Yes", "No")


def validate_placement_payload(data: Dict[str, Any], is_update: bool = False) -> None:
    """Validates placement offer fields."""
    if not is_update:
        required = ["Student_ID", "Company_ID", "Package", "Placement_Year"]
        for field in required:
            if field not in data or data[field] is None:
                raise ValidationError(f"Missing required field: '{field}'")

    if "Package" in data and data["Package"] is not None:
        try:
            pkg = float(data["Package"])
            if pkg <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Package must be a positive decimal number (> 0 LPA)")

    if "Placement_Year" in data and data["Placement_Year"] is not None:
        try:
            year = int(data["Placement_Year"])
            if not (2000 <= year <= 2100):
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Placement_Year must be an integer between 2000 and 2100")

    if "Offer_Status" in data and data["Offer_Status"] is not None:
        status = str(data["Offer_Status"]).strip()
        if status not in VALID_OFFER_STATUSES:
            raise ValidationError(f"Offer_Status must be one of: {', '.join(VALID_OFFER_STATUSES)}")

    if "Placement_Type" in data and data["Placement_Type"] is not None:
        ptype = str(data["Placement_Type"]).strip()
        if ptype not in VALID_PLACEMENT_TYPES:
            raise ValidationError(f"Placement_Type must be one of: {', '.join(VALID_PLACEMENT_TYPES)}")

    if "Is_PPO" in data and data["Is_PPO"] is not None:
        ppo = str(data["Is_PPO"]).strip()
        if ppo not in VALID_BOOLEAN_STRINGS:
            raise ValidationError("Is_PPO must be 'Yes' or 'No'")

    if "Joined" in data and data["Joined"] is not None:
        joined = str(data["Joined"]).strip()
        if joined not in VALID_BOOLEAN_STRINGS:
            raise ValidationError("Joined must be 'Yes' or 'No'")


def create_placement_offer(data: Dict[str, Any]) -> Dict[str, Any]:
    """Issues and records a placement offer, enforcing all business domain constraints.
    
    Business Rules Enforced:
    1. Opportunity must be of type 'Placement' (not 'Internship').
    2. No duplicate offer for the same opportunity to the same student.
    3. At most one 'Accepted' (or 'Joined') offer per student.
    4. Evaluated skills are safely recorded in PLACEMENT_SKILL inside a transaction.
    """
    validate_placement_payload(data, is_update=False)

    student_id = int(data["Student_ID"])
    company_id = int(data["Company_ID"])
    opp_id = int(data["Opportunity_ID"]) if data.get("Opportunity_ID") else None
    role = str(data.get("Role", "") or "").strip() or None
    package_lpa = round(float(data["Package"]), 2)
    placement_year = int(data["Placement_Year"])
    placement_type = str(data.get("Placement_Type", "On-campus") or "On-campus").strip()
    is_ppo = str(data.get("Is_PPO", "No") or "No").strip()
    offer_status = str(data.get("Offer_Status", "Offered") or "Offered").strip()
    joined = str(data.get("Joined", "No") or "No").strip()
    rounds = int(data.get("Interview_Rounds", 1) or 1)
    skills = [str(s).strip() for s in data.get("Skills", []) if str(s).strip()]

    # If joined is Yes, status must be Joined or Accepted
    if joined == "Yes" and offer_status not in ("Accepted", "Joined"):
        offer_status = "Joined"
    elif offer_status == "Joined":
        joined = "Yes"

    # 1. Verify Student Exists
    student = execute_one("SELECT Student_ID, Roll_No, First_Name, Last_Name FROM STUDENT WHERE Student_ID = %s", (student_id,))
    if not student:
        raise NotFoundError(f"Student with ID {student_id} does not exist.")

    # 2. Verify Company Exists
    company = execute_one("SELECT Company_ID, Company_Name FROM COMPANY WHERE Company_ID = %s", (company_id,))
    if not company:
        raise NotFoundError(f"Company with ID {company_id} does not exist.")

    # 3. Rule 3: Check Opportunity is 'Placement' type
    if opp_id:
        opp = execute_one(
            "SELECT Opportunity_ID, Role, Opportunity_Type, Package_Stipend FROM OPPORTUNITY WHERE Opportunity_ID = %s",
            (opp_id,)
        )
        if not opp:
            raise NotFoundError(f"Opportunity with ID {opp_id} does not exist.")
        if opp["Opportunity_Type"] != "Placement":
            raise ValidationError(
                f"Invalid opportunity type: Opportunity ID {opp_id} ('{opp['Role']}') is of type '{opp['Opportunity_Type']}'. "
                "Placement offers can only be issued for opportunities of type 'Placement'."
            )
        if not role:
            role = opp["Role"]

    # 4. Rule 1: Enforce NO duplicate offer for the same opportunity
    if opp_id:
        duplicate_check = execute_one(
            "SELECT Placement_ID, Role, Offer_Status FROM PLACEMENT WHERE Student_ID = %s AND Opportunity_ID = %s",
            (student_id, opp_id)
        )
        if duplicate_check:
            raise ConflictError(
                f"Duplicate offer rejected: Student {student['Roll_No']} already holds placement offer #{duplicate_check['Placement_ID']} "
                f"for Opportunity ID {opp_id} ('{duplicate_check['Role']}' - Status: '{duplicate_check['Offer_Status']}')."
            )

    # 5. Rule 2: Enforce at most ONE Accepted/Joined offer per student
    if offer_status in ("Accepted", "Joined"):
        existing_accepted = execute_one("""
            SELECT p.Placement_ID, p.Role, p.Offer_Status, c.Company_Name
            FROM PLACEMENT p
            JOIN COMPANY c ON p.Company_ID = c.Company_ID
            WHERE p.Student_ID = %s AND p.Offer_Status IN ('Accepted', 'Joined')
        """, (student_id,))
        if existing_accepted:
            raise ConflictError(
                f"Cannot accept offer: Student {student['Roll_No']} already holds an accepted offer "
                f"(Offer #{existing_accepted['Placement_ID']} at {existing_accepted['Company_Name']} - "
                f"Status: '{existing_accepted['Offer_Status']}'). "
                "Institutional placement policy allows at most ONE Accepted offer per student. "
                "Decline the existing accepted offer before accepting another."
            )

    # Insert into PLACEMENT and PLACEMENT_SKILL inside an atomic transaction
    insert_sql = """
        INSERT INTO PLACEMENT (
            Student_ID, Company_ID, Opportunity_ID, Role, Package,
            Placement_Year, Placement_Type, Is_PPO, Joined, Offer_Status, Interview_Rounds
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            insert_sql,
            (student_id, company_id, opp_id, role, package_lpa,
             placement_year, placement_type, is_ppo, joined, offer_status, rounds)
        )
        placement_id = cursor.lastrowid

        if skills:
            skill_insert = "INSERT INTO PLACEMENT_SKILL (Placement_ID, Skill) VALUES (%s, %s)"
            cursor.executemany(skill_insert, [(placement_id, s) for s in set(skills)])

    logger.info("Issued placement offer ID %s to student %s at %s (%s LPA)", placement_id, student["Roll_No"], company["Company_Name"], package_lpa)
    return get_placement_offer(placement_id)


def get_placement_offer(placement_id: int) -> Dict[str, Any]:
    """Retrieves full placement offer record with joined student, company, and opportunity metadata."""
    sql = """
        SELECT p.Placement_ID, p.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, s.CGPA,
               p.Company_ID, c.Company_Name, c.Company_Type, c.Industry,
               p.Opportunity_ID, o.Role AS Opportunity_Role, o.Package_Stipend AS Drive_Package,
               p.Role, p.Package, p.Placement_Year, p.Placement_Type, p.Is_PPO,
               p.Joined, p.Offer_Status, p.Interview_Rounds
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        LEFT JOIN OPPORTUNITY o ON p.Opportunity_ID = o.Opportunity_ID
        WHERE p.Placement_ID = %s
    """
    offer = execute_one(sql, (placement_id,))
    if not offer:
        raise NotFoundError(f"Placement offer with ID {placement_id} not found.")

    offer["Package"] = float(offer["Package"])
    offer["CGPA"] = float(offer["CGPA"])
    if offer.get("Drive_Package") is not None:
        offer["Drive_Package"] = float(offer["Drive_Package"])

    # Fetch evaluated skills
    skills_sql = "SELECT Skill FROM PLACEMENT_SKILL WHERE Placement_ID = %s ORDER BY Skill"
    skills = execute_query(skills_sql, (placement_id,))
    offer["Skills"] = [s["Skill"] for s in skills]

    return offer


def list_placement_offers(
    student_id: Optional[int] = None,
    company_id: Optional[int] = None,
    opportunity_id: Optional[int] = None,
    placement_year: Optional[int] = None,
    offer_status: Optional[str] = None,
    placement_type: Optional[str] = None,
    is_ppo: Optional[str] = None,
    joined: Optional[str] = None,
    min_package: Optional[float] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """Lists, searches, and filters placement offers with pagination."""
    where_clauses = ["1=1"]
    params: List[Any] = []

    if student_id is not None:
        where_clauses.append("p.Student_ID = %s")
        params.append(int(student_id))

    if company_id is not None:
        where_clauses.append("p.Company_ID = %s")
        params.append(int(company_id))

    if opportunity_id is not None:
        where_clauses.append("p.Opportunity_ID = %s")
        params.append(int(opportunity_id))

    if placement_year is not None:
        where_clauses.append("p.Placement_Year = %s")
        params.append(int(placement_year))

    if offer_status:
        where_clauses.append("p.Offer_Status = %s")
        params.append(offer_status.strip())

    if placement_type:
        where_clauses.append("p.Placement_Type = %s")
        params.append(placement_type.strip())

    if is_ppo:
        where_clauses.append("p.Is_PPO = %s")
        params.append(is_ppo.strip())

    if joined:
        where_clauses.append("p.Joined = %s")
        params.append(joined.strip())

    if min_package is not None:
        where_clauses.append("p.Package >= %s")
        params.append(float(min_package))

    if search:
        search_pattern = f"%{search.strip()}%"
        where_clauses.append("(s.Roll_No LIKE %s OR s.First_Name LIKE %s OR c.Company_Name LIKE %s OR p.Role LIKE %s)")
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern])

    where_sql = " AND ".join(where_clauses)

    count_sql = f"""
        SELECT COUNT(*) AS total
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE {where_sql}
    """
    total_count = execute_one(count_sql, tuple(params))["total"]

    query_sql = f"""
        SELECT p.Placement_ID, p.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch,
               p.Company_ID, c.Company_Name, p.Opportunity_ID, p.Role, p.Package,
               p.Placement_Year, p.Placement_Type, p.Is_PPO, p.Joined, p.Offer_Status,
               GROUP_CONCAT(ps.Skill SEPARATOR ', ') AS Evaluated_Skills
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        LEFT JOIN PLACEMENT_SKILL ps ON p.Placement_ID = ps.Placement_ID
        WHERE {where_sql}
        GROUP BY p.Placement_ID
        ORDER BY p.Package DESC, p.Placement_ID DESC
        LIMIT %s OFFSET %s
    """
    exec_params = list(params) + [int(limit), int(offset)]
    rows = execute_query(query_sql, tuple(exec_params))

    for r in rows:
        r["Package"] = float(r["Package"])
        r["Evaluated_Skills"] = r["Evaluated_Skills"].split(", ") if r["Evaluated_Skills"] else []

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "results": rows,
    }


def update_offer_status(placement_id: int, new_status: str, joined: Optional[str] = None) -> Dict[str, Any]:
    """Updates the status of an existing offer (Offered -> Accepted / Declined / Joined).
    
    Enforces Rule 2: At most one Accepted or Joined offer per student across all applications.
    """
    offer = get_placement_offer(placement_id)
    student_id = offer["Student_ID"]

    clean_status = str(new_status).strip()
    if clean_status not in VALID_OFFER_STATUSES:
        raise ValidationError(f"Invalid status: '{clean_status}'. Must be one of: {', '.join(VALID_OFFER_STATUSES)}")

    # Determine joined value
    if clean_status == "Joined":
        joined = "Yes"
    elif clean_status == "Declined":
        joined = "No"
    elif joined is None:
        joined = offer["Joined"]

    # Rule 2: If accepting this offer, verify student has NO OTHER accepted offer
    if clean_status in ("Accepted", "Joined"):
        existing_accepted = execute_one("""
            SELECT p.Placement_ID, p.Role, p.Offer_Status, c.Company_Name
            FROM PLACEMENT p
            JOIN COMPANY c ON p.Company_ID = c.Company_ID
            WHERE p.Student_ID = %s 
              AND p.Offer_Status IN ('Accepted', 'Joined')
              AND p.Placement_ID != %s
        """, (student_id, placement_id))

        if existing_accepted:
            raise ConflictError(
                f"Offer acceptance blocked: Student {offer['Roll_No']} already has an accepted offer "
                f"(Offer #{existing_accepted['Placement_ID']} at {existing_accepted['Company_Name']} - "
                f"Status: '{existing_accepted['Offer_Status']}'). "
                f"The student must decline offer #{existing_accepted['Placement_ID']} before accepting offer #{placement_id}."
            )

    update_sql = "UPDATE PLACEMENT SET Offer_Status = %s, Joined = %s WHERE Placement_ID = %s"
    with get_cursor(commit=True) as cursor:
        cursor.execute(update_sql, (clean_status, joined, placement_id))

    logger.info("Updated placement offer #%s status from '%s' to '%s'", placement_id, offer["Offer_Status"], clean_status)
    return get_placement_offer(placement_id)


def update_placement_offer(placement_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Updates placement offer fields and synchronization of evaluated skills."""
    existing = get_placement_offer(placement_id)
    validate_placement_payload(data, is_update=True)

    updatable = ["Role", "Package", "Placement_Year", "Placement_Type", "Is_PPO", "Offer_Status", "Joined", "Interview_Rounds"]
    set_clauses = []
    params: List[Any] = []

    # Check Rule 2 if status or joined is changing to Accepted/Joined
    new_status = data.get("Offer_Status", existing["Offer_Status"])
    if new_status in ("Accepted", "Joined") and existing["Offer_Status"] not in ("Accepted", "Joined"):
        student_id = existing["Student_ID"]
        existing_acc = execute_one("""
            SELECT p.Placement_ID, p.Role, p.Offer_Status, c.Company_Name
            FROM PLACEMENT p
            JOIN COMPANY c ON p.Company_ID = c.Company_ID
            WHERE p.Student_ID = %s AND p.Offer_Status IN ('Accepted', 'Joined') AND p.Placement_ID != %s
        """, (student_id, placement_id))
        if existing_acc:
            raise ConflictError(
                f"Cannot accept offer: Student already holds accepted offer #{existing_acc['Placement_ID']} at {existing_acc['Company_Name']}."
            )

    for field in updatable:
        if field in data and data[field] is not None:
            val = data[field]
            if field == "Package":
                val = round(float(val), 2)
            elif field in ("Placement_Year", "Interview_Rounds"):
                val = int(val)
            else:
                val = str(val).strip()
            set_clauses.append(f"{field} = %s")
            params.append(val)

    with get_cursor(commit=True) as cursor:
        if set_clauses:
            update_sql = f"UPDATE PLACEMENT SET {', '.join(set_clauses)} WHERE Placement_ID = %s"
            params.append(placement_id)
            cursor.execute(update_sql, tuple(params))

        # Update skills if provided
        if "Skills" in data and data["Skills"] is not None:
            cursor.execute("DELETE FROM PLACEMENT_SKILL WHERE Placement_ID = %s", (placement_id,))
            new_skills = [str(s).strip() for s in data["Skills"] if str(s).strip()]
            if new_skills:
                cursor.executemany(
                    "INSERT INTO PLACEMENT_SKILL (Placement_ID, Skill) VALUES (%s, %s)",
                    [(placement_id, s) for s in set(new_skills)]
                )

    logger.info("Updated placement offer ID %s", placement_id)
    return get_placement_offer(placement_id)


def delete_placement_offer(placement_id: int) -> Dict[str, Any]:
    """Deletes a placement offer record."""
    offer = execute_one("SELECT Placement_ID, Student_ID, Role FROM PLACEMENT WHERE Placement_ID = %s", (placement_id,))
    if not offer:
        raise NotFoundError(f"Placement offer with ID {placement_id} not found.")

    with get_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM PLACEMENT WHERE Placement_ID = %s", (placement_id,))

    logger.info("Deleted placement offer ID %s", placement_id)
    return {
        "success": True,
        "message": f"Placement offer ID {placement_id} ('{offer['Role']}') deleted successfully.",
        "deleted_placement_id": placement_id,
    }


# ==============================================================================
# Analytical Queries for Students with Several Offers
# ==============================================================================

def get_students_with_multiple_offers(min_offers: int = 2) -> List[Dict[str, Any]]:
    """Identifies and aggregates students who received multiple placement offers."""
    sql = """
        SELECT s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, s.CGPA,
               COUNT(p.Placement_ID) AS Total_Offers,
               MAX(p.Package) AS Highest_Package,
               MIN(p.Package) AS Lowest_Package,
               GROUP_CONCAT(CONCAT(c.Company_Name, ' (', p.Package, ' LPA - ', p.Offer_Status, ')') SEPARATOR '; ') AS Offers_Breakdown,
               MAX(CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN c.Company_Name ELSE NULL END) AS Accepted_Company,
               MAX(CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN p.Package ELSE NULL END) AS Accepted_Package
        FROM STUDENT s
        JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        GROUP BY s.Student_ID
        HAVING COUNT(p.Placement_ID) >= %s
        ORDER BY Total_Offers DESC, Highest_Package DESC
    """
    rows = execute_query(sql, (int(min_offers),))
    for r in rows:
        r["CGPA"] = float(r["CGPA"])
        r["Highest_Package"] = float(r["Highest_Package"])
        r["Lowest_Package"] = float(r["Lowest_Package"])
        if r.get("Accepted_Package") is not None:
            r["Accepted_Package"] = float(r["Accepted_Package"])
    return rows


def get_offer_distribution_summary() -> Dict[str, Any]:
    """Provides a breakdown of placement distribution: students with 0, 1, or multiple offers."""
    sql = """
        SELECT 
            SUM(CASE WHEN offer_count = 0 THEN 1 ELSE 0 END) AS zero_offers_count,
            SUM(CASE WHEN offer_count = 1 THEN 1 ELSE 0 END) AS single_offer_count,
            SUM(CASE WHEN offer_count >= 2 THEN 1 ELSE 0 END) AS multiple_offers_count,
            COUNT(*) AS total_students_evaluated
        FROM (
            SELECT s.Student_ID, COUNT(p.Placement_ID) AS offer_count
            FROM STUDENT s
            LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
            GROUP BY s.Student_ID
        ) AS student_offer_counts;
    """
    res = execute_one(sql)
    return {
        "zero_offers": int(res["zero_offers_count"] or 0),
        "single_offer": int(res["single_offer_count"] or 0),
        "multiple_offers": int(res["multiple_offers_count"] or 0),
        "total_students": int(res["total_students_evaluated"] or 0),
    }

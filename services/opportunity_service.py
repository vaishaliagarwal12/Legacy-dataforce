import logging
from typing import Dict, Any, List, Optional
from db.connection import get_cursor, execute_one, execute_query
from services.exceptions import ValidationError, NotFoundError, ProtectedDeleteError

logger = logging.getLogger(__name__)

VALID_OPP_TYPES = ("Placement", "Internship")


def validate_opportunity_payload(data: Dict[str, Any], is_update: bool = False) -> None:
    """Validates opportunity and embedded eligibility fields."""
    if not is_update:
        required = ["Drive_ID", "Role", "Opportunity_Type", "Package_Stipend"]
        for field in required:
            if field not in data or data[field] is None:
                raise ValidationError(f"Missing required field: '{field}'")

    if "Opportunity_Type" in data and data["Opportunity_Type"] is not None:
        op_type = str(data["Opportunity_Type"]).strip()
        if op_type not in VALID_OPP_TYPES:
            raise ValidationError(f"Opportunity_Type must be one of: {', '.join(VALID_OPP_TYPES)}")

    if "Package_Stipend" in data and data["Package_Stipend"] is not None:
        try:
            pkg = float(data["Package_Stipend"])
            if pkg <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Package_Stipend must be a positive number (> 0)")

    if "Duration_Months" in data and data["Duration_Months"] is not None:
        try:
            dur = int(data["Duration_Months"])
            if dur <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Duration_Months must be a positive integer")

    # Eligibility fields validation
    if "Minimum_CGPA" in data and data["Minimum_CGPA"] is not None:
        try:
            cgpa = float(data["Minimum_CGPA"])
            if not (0.0 <= cgpa <= 10.0):
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Minimum_CGPA must be between 0.00 and 10.00")

    if "Max_Backlogs" in data and data["Max_Backlogs"] is not None:
        try:
            backlogs = int(data["Max_Backlogs"])
            if backlogs < 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Max_Backlogs must be a non-negative integer (>= 0)")

    if "Eligible_Branches" in data and data["Eligible_Branches"] is not None:
        if not isinstance(data["Eligible_Branches"], list):
            raise ValidationError("Eligible_Branches must be a list of branch strings (e.g. ['CSE', 'IT'])")


def create_opportunity(data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates an opportunity, its eligibility criteria, and multiple eligible branches within an atomic transaction."""
    validate_opportunity_payload(data, is_update=False)

    drive_id = int(data["Drive_ID"])
    role = str(data["Role"]).strip()
    opp_type = str(data["Opportunity_Type"]).strip()
    package_stipend = round(float(data["Package_Stipend"]), 2)
    duration_months = int(data["Duration_Months"]) if data.get("Duration_Months") is not None else None

    # Eligibility attributes
    min_cgpa = round(float(data.get("Minimum_CGPA", 6.00)), 2)
    max_backlogs = int(data.get("Max_Backlogs", 0))
    other_criteria = str(data.get("Other_Criteria", "") or "").strip() or None
    eligible_branches = [str(b).strip() for b in data.get("Eligible_Branches", []) if str(b).strip()]

    # Verify drive exists
    drive = execute_one("SELECT Drive_ID FROM RECRUITMENT_DRIVE WHERE Drive_ID = %s", (drive_id,))
    if not drive:
        raise NotFoundError(f"Recruitment Drive with ID {drive_id} does not exist.")

    summary_branch = ", ".join(eligible_branches) if eligible_branches else "All Branches"

    # ATOMIC TRANSACTION: Opportunity + Eligibility + Eligibility_Branch
    with get_cursor(commit=True) as cursor:
        # 1. Insert Opportunity
        opp_insert = """
            INSERT INTO OPPORTUNITY (Drive_ID, Role, Opportunity_Type, Package_Stipend, Duration_Months)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(opp_insert, (drive_id, role, opp_type, package_stipend, duration_months))
        opp_id = cursor.lastrowid

        # 2. Insert Eligibility Master
        elig_insert = """
            INSERT INTO ELIGIBILITY (Opportunity_ID, Minimum_CGPA, Eligible_Branch, Max_Backlogs, Other_Criteria)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(elig_insert, (opp_id, min_cgpa, summary_branch, max_backlogs, other_criteria))
        elig_id = cursor.lastrowid

        # 3. Insert Multiple Eligible Branches into decomposed table
        if eligible_branches:
            branch_insert = "INSERT INTO ELIGIBILITY_BRANCH (Eligibility_ID, Branch) VALUES (%s, %s)"
            cursor.executemany(branch_insert, [(elig_id, b) for b in set(eligible_branches)])

    logger.info("Created opportunity ID %s with eligibility ID %s and %s branches", opp_id, elig_id, len(eligible_branches))
    return get_opportunity(opp_id)


def get_opportunity(opportunity_id: int) -> Dict[str, Any]:
    """Retrieves full opportunity details including recruiting drive, company, eligibility, branches, and rounds."""
    sql = """
        SELECT o.Opportunity_ID, o.Drive_ID, rd.Company_ID, c.Company_Name, c.Company_Type,
               rd.Drive_Year, rd.Drive_Type, rd.Season,
               o.Role, o.Opportunity_Type, o.Package_Stipend, o.Duration_Months,
               e.Eligibility_ID, e.Minimum_CGPA, e.Max_Backlogs, e.Other_Criteria, e.Eligible_Branch
        FROM OPPORTUNITY o
        JOIN RECRUITMENT_DRIVE rd ON o.Drive_ID = rd.Drive_ID
        JOIN COMPANY c ON rd.Company_ID = c.Company_ID
        LEFT JOIN ELIGIBILITY e ON o.Opportunity_ID = e.Opportunity_ID
        WHERE o.Opportunity_ID = %s
    """
    opp = execute_one(sql, (opportunity_id,))
    if not opp:
        raise NotFoundError(f"Opportunity with ID {opportunity_id} not found.")

    opp["Package_Stipend"] = float(opp["Package_Stipend"])
    if opp.get("Minimum_CGPA") is not None:
        opp["Minimum_CGPA"] = float(opp["Minimum_CGPA"])

    # Fetch decomposed eligible branches
    if opp.get("Eligibility_ID"):
        branches = execute_query(
            "SELECT Branch FROM ELIGIBILITY_BRANCH WHERE Eligibility_ID = %s ORDER BY Branch",
            (opp["Eligibility_ID"],)
        )
        opp["Eligible_Branches"] = [b["Branch"] for b in branches]
    else:
        opp["Eligible_Branches"] = []

    # Fetch selection rounds
    rounds_sql = """
        SELECT Round_ID, Round_Number, Round_Type, Description
        FROM SELECTION_PROCESS
        WHERE Opportunity_ID = %s
        ORDER BY Round_Number ASC
    """
    opp["Selection_Rounds"] = execute_query(rounds_sql, (opportunity_id,))

    # Placement / Internship binding checks
    bound = execute_one("""
        SELECT 
            (SELECT COUNT(*) FROM PLACEMENT WHERE Opportunity_ID = %s) AS p_count,
            (SELECT COUNT(*) FROM INTERNSHIP WHERE Opportunity_ID = %s) AS i_count
    """, (opportunity_id, opportunity_id))
    opp["Placement_Offers_Count"] = bound["p_count"]
    opp["Internships_Count"] = bound["i_count"]
    opp["Is_Deletable"] = (bound["p_count"] == 0 and bound["i_count"] == 0)

    return opp


def list_opportunities(
    drive_id: Optional[int] = None,
    opportunity_type: Optional[str] = None,
    min_package: Optional[float] = None,
    branch: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Lists, searches, and filters recruitment opportunities."""
    where_clauses = ["1=1"]
    params: List[Any] = []

    if drive_id is not None:
        where_clauses.append("o.Drive_ID = %s")
        params.append(int(drive_id))

    if opportunity_type:
        where_clauses.append("o.Opportunity_Type = %s")
        params.append(opportunity_type.strip())

    if min_package is not None:
        where_clauses.append("o.Package_Stipend >= %s")
        params.append(float(min_package))

    if search:
        search_pattern = f"%{search.strip()}%"
        where_clauses.append("(o.Role LIKE %s OR c.Company_Name LIKE %s)")
        params.extend([search_pattern, search_pattern])

    if branch:
        where_clauses.append("""
            (e.Eligible_Branch LIKE %s 
             OR EXISTS (SELECT 1 FROM ELIGIBILITY_BRANCH eb WHERE eb.Eligibility_ID = e.Eligibility_ID AND eb.Branch = %s))
        """)
        params.extend([f"%{branch.strip()}%", branch.strip()])

    where_sql = " AND ".join(where_clauses)
    query_sql = f"""
        SELECT o.Opportunity_ID, o.Drive_ID, rd.Company_ID, c.Company_Name,
               rd.Drive_Year, o.Role, o.Opportunity_Type, o.Package_Stipend, o.Duration_Months,
               e.Eligibility_ID, e.Minimum_CGPA, e.Max_Backlogs, e.Eligible_Branch,
               COUNT(DISTINCT sp.Round_ID) AS Total_Rounds
        FROM OPPORTUNITY o
        JOIN RECRUITMENT_DRIVE rd ON o.Drive_ID = rd.Drive_ID
        JOIN COMPANY c ON rd.Company_ID = c.Company_ID
        LEFT JOIN ELIGIBILITY e ON o.Opportunity_ID = e.Opportunity_ID
        LEFT JOIN SELECTION_PROCESS sp ON o.Opportunity_ID = sp.Opportunity_ID
        WHERE {where_sql}
        GROUP BY o.Opportunity_ID
        ORDER BY o.Package_Stipend DESC, o.Opportunity_ID ASC
    """
    rows = execute_query(query_sql, tuple(params))
    for r in rows:
        r["Package_Stipend"] = float(r["Package_Stipend"])
        if r.get("Minimum_CGPA") is not None:
            r["Minimum_CGPA"] = float(r["Minimum_CGPA"])

    return rows


def update_opportunity(opportunity_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Updates opportunity and eligibility criteria within an atomic transaction."""
    existing = get_opportunity(opportunity_id)
    validate_opportunity_payload(data, is_update=True)

    with get_cursor(commit=True) as cursor:
        # Update Opportunity fields
        opp_updates = []
        opp_params = []
        if "Role" in data and data["Role"] is not None:
            opp_updates.append("Role = %s")
            opp_params.append(str(data["Role"]).strip())
        if "Opportunity_Type" in data and data["Opportunity_Type"] is not None:
            opp_updates.append("Opportunity_Type = %s")
            opp_params.append(str(data["Opportunity_Type"]).strip())
        if "Package_Stipend" in data and data["Package_Stipend"] is not None:
            opp_updates.append("Package_Stipend = %s")
            opp_params.append(round(float(data["Package_Stipend"]), 2))
        if "Duration_Months" in data:
            opp_updates.append("Duration_Months = %s")
            opp_params.append(int(data["Duration_Months"]) if data["Duration_Months"] is not None else None)

        if opp_updates:
            opp_sql = f"UPDATE OPPORTUNITY SET {', '.join(opp_updates)} WHERE Opportunity_ID = %s"
            opp_params.append(opportunity_id)
            cursor.execute(opp_sql, tuple(opp_params))

        # Update Eligibility fields
        elig_id = existing.get("Eligibility_ID")
        elig_updates = []
        elig_params = []
        if "Minimum_CGPA" in data and data["Minimum_CGPA"] is not None:
            elig_updates.append("Minimum_CGPA = %s")
            elig_params.append(round(float(data["Minimum_CGPA"]), 2))
        if "Max_Backlogs" in data and data["Max_Backlogs"] is not None:
            elig_updates.append("Max_Backlogs = %s")
            elig_params.append(int(data["Max_Backlogs"]))
        if "Other_Criteria" in data:
            elig_updates.append("Other_Criteria = %s")
            elig_params.append(str(data["Other_Criteria"]).strip() if data["Other_Criteria"] is not None else None)

        # Update eligible branches
        if "Eligible_Branches" in data and data["Eligible_Branches"] is not None:
            new_branches = [str(b).strip() for b in data["Eligible_Branches"] if str(b).strip()]
            summary_str = ", ".join(new_branches) if new_branches else "All Branches"
            elig_updates.append("Eligible_Branch = %s")
            elig_params.append(summary_str)

            if elig_id:
                cursor.execute("DELETE FROM ELIGIBILITY_BRANCH WHERE Eligibility_ID = %s", (elig_id,))
                if new_branches:
                    cursor.executemany(
                        "INSERT INTO ELIGIBILITY_BRANCH (Eligibility_ID, Branch) VALUES (%s, %s)",
                        [(elig_id, b) for b in set(new_branches)]
                    )

        if elig_updates and elig_id:
            elig_sql = f"UPDATE ELIGIBILITY SET {', '.join(elig_updates)} WHERE Eligibility_ID = %s"
            elig_params.append(elig_id)
            cursor.execute(elig_sql, tuple(elig_params))

    logger.info("Updated opportunity ID %s inside transaction", opportunity_id)
    return get_opportunity(opportunity_id)


def delete_opportunity(opportunity_id: int) -> Dict[str, Any]:
    """Deletes an opportunity, blocking if student placements or internships reference it."""
    opp = execute_one("SELECT Opportunity_ID, Role FROM OPPORTUNITY WHERE Opportunity_ID = %s", (opportunity_id,))
    if not opp:
        raise NotFoundError(f"Opportunity with ID {opportunity_id} not found.")

    bound = execute_one("""
        SELECT 
            (SELECT COUNT(*) FROM PLACEMENT WHERE Opportunity_ID = %s) AS p_bound,
            (SELECT COUNT(*) FROM INTERNSHIP WHERE Opportunity_ID = %s) AS i_bound
    """, (opportunity_id, opportunity_id))

    if bound["p_bound"] > 0 or bound["i_bound"] > 0:
        raise ProtectedDeleteError(
            f"Cannot delete Opportunity ID {opportunity_id} ('{opp['Role']}'): "
            f"Bound to {bound['p_bound']} active placement offer(s) and {bound['i_bound']} internship record(s)."
        )

    with get_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM OPPORTUNITY WHERE Opportunity_ID = %s", (opportunity_id,))

    logger.info("Deleted opportunity ID %s ('%s')", opportunity_id, opp["Role"])
    return {
        "success": True,
        "message": f"Opportunity '{opp['Role']}' (ID: {opportunity_id}) safely deleted.",
        "deleted_opportunity_id": opportunity_id,
    }

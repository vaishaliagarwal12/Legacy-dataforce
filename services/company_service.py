import logging
from typing import Dict, Any, List, Optional
from db.connection import get_cursor, execute_one, execute_query
from services.exceptions import ValidationError, NotFoundError, ConflictError, ProtectedDeleteError

logger = logging.getLogger(__name__)

VALID_COMPANY_TYPES = ("Product", "Service", "Startup", "PSU", "MNC", "Other")


def validate_company_payload(data: Dict[str, Any], is_update: bool = False) -> None:
    """Validates company attributes."""
    if not is_update:
        if not data.get("Company_Name") or str(data["Company_Name"]).strip() == "":
            raise ValidationError("Missing required field: 'Company_Name'")

    if "Company_Type" in data and data["Company_Type"] is not None:
        ctype = str(data["Company_Type"]).strip()
        if ctype not in VALID_COMPANY_TYPES:
            raise ValidationError(f"Company_Type must be one of: {', '.join(VALID_COMPANY_TYPES)}")


def create_company(data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a recruiting company."""
    validate_company_payload(data, is_update=False)

    name = str(data["Company_Name"]).strip()
    company_type = str(data.get("Company_Type", "Other") or "Other").strip()
    industry = str(data.get("Industry", "") or "").strip() or None
    location = str(data.get("Location", "") or "").strip() or None
    website = str(data.get("Website", "") or "").strip() or None

    existing = execute_one("SELECT Company_ID FROM COMPANY WHERE Company_Name = %s", (name,))
    if existing:
        raise ConflictError(f"A company with name '{name}' already exists.")

    insert_sql = """
        INSERT INTO COMPANY (Company_Name, Company_Type, Industry, Location, Website)
        VALUES (%s, %s, %s, %s, %s)
    """
    with get_cursor(commit=True) as cursor:
        cursor.execute(insert_sql, (name, company_type, industry, location, website))
        company_id = cursor.lastrowid

    logger.info("Created company ID %s ('%s')", company_id, name)
    return get_company(company_id)


def get_company(company_id: int) -> Dict[str, Any]:
    """Retrieves full company detail view listing all its recruitment drives and opportunities."""
    company = execute_one(
        "SELECT Company_ID, Company_Name, Company_Type, Industry, Location, Website FROM COMPANY WHERE Company_ID = %s",
        (company_id,)
    )
    if not company:
        raise NotFoundError(f"Company with ID {company_id} not found.")

    # Fetch recruitment drives
    drives_sql = """
        SELECT Drive_ID, Drive_Year, Drive_Type, Season, Drive_Date
        FROM RECRUITMENT_DRIVE
        WHERE Company_ID = %s
        ORDER BY Drive_Year DESC, Drive_Date DESC
    """
    drives = execute_query(drives_sql, (company_id,))

    # For each drive, attach its opportunities with eligibility, branches, and rounds
    for drive in drives:
        drive_id = drive["Drive_ID"]
        opp_sql = """
            SELECT o.Opportunity_ID, o.Role, o.Opportunity_Type, o.Package_Stipend, o.Duration_Months,
                   e.Minimum_CGPA, e.Max_Backlogs, e.Other_Criteria, e.Eligible_Branch, e.Eligibility_ID
            FROM OPPORTUNITY o
            LEFT JOIN ELIGIBILITY e ON o.Opportunity_ID = e.Opportunity_ID
            WHERE o.Drive_ID = %s
            ORDER BY o.Opportunity_ID ASC
        """
        opportunities = execute_query(opp_sql, (drive_id,))
        for opp in opportunities:
            opp["Package_Stipend"] = float(opp["Package_Stipend"])
            if opp.get("Minimum_CGPA") is not None:
                opp["Minimum_CGPA"] = float(opp["Minimum_CGPA"])

            # Fetch separate branches table
            if opp.get("Eligibility_ID"):
                branches = execute_query(
                    "SELECT Branch FROM ELIGIBILITY_BRANCH WHERE Eligibility_ID = %s ORDER BY Branch",
                    (opp["Eligibility_ID"],)
                )
                opp["Eligible_Branches"] = [b["Branch"] for b in branches]
            else:
                opp["Eligible_Branches"] = []

            # Fetch rounds
            rounds = execute_query(
                "SELECT Round_ID, Round_Number, Round_Type, Description FROM SELECTION_PROCESS WHERE Opportunity_ID = %s ORDER BY Round_Number ASC",
                (opp["Opportunity_ID"],)
            )
            opp["Selection_Rounds"] = rounds

        drive["Opportunities"] = opportunities
        drive["Opportunity_Count"] = len(opportunities)

    company["Recruitment_Drives"] = drives
    company["Total_Drives"] = len(drives)

    # Check Placement / Internship stats
    history = execute_one("""
        SELECT 
            (SELECT COUNT(*) FROM PLACEMENT WHERE Company_ID = %s) AS total_placements,
            (SELECT COUNT(*) FROM INTERNSHIP WHERE Company_ID = %s) AS total_internships
    """, (company_id, company_id))
    company["Placement_Count"] = history["total_placements"]
    company["Internship_Count"] = history["total_internships"]
    company["Is_Deletable"] = (history["total_placements"] == 0 and history["total_internships"] == 0 and len(drives) == 0)

    return company


def list_companies(
    search: Optional[str] = None,
    company_type: Optional[str] = None,
    industry: Optional[str] = None,
    location: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Lists, searches, and filters recruiting companies."""
    where_clauses = ["1=1"]
    params: List[Any] = []

    if search:
        search_pattern = f"%{search.strip()}%"
        where_clauses.append("(c.Company_Name LIKE %s OR c.Industry LIKE %s OR c.Location LIKE %s)")
        params.extend([search_pattern, search_pattern, search_pattern])

    if company_type:
        where_clauses.append("c.Company_Type = %s")
        params.append(company_type.strip())

    if industry:
        where_clauses.append("c.Industry = %s")
        params.append(industry.strip())

    if location:
        where_clauses.append("c.Location = %s")
        params.append(location.strip())

    where_sql = " AND ".join(where_clauses)
    query_sql = f"""
        SELECT c.Company_ID, c.Company_Name, c.Company_Type, c.Industry, c.Location, c.Website,
               COUNT(DISTINCT rd.Drive_ID) AS Total_Drives,
               COUNT(DISTINCT p.Placement_ID) AS Total_Placements,
               COUNT(DISTINCT i.Internship_ID) AS Total_Internships
        FROM COMPANY c
        LEFT JOIN RECRUITMENT_DRIVE rd ON c.Company_ID = rd.Company_ID
        LEFT JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
        LEFT JOIN INTERNSHIP i ON c.Company_ID = i.Company_ID
        WHERE {where_sql}
        GROUP BY c.Company_ID
        ORDER BY c.Company_Name ASC
    """
    return execute_query(query_sql, tuple(params))


def update_company(company_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Updates company attributes."""
    existing = execute_one("SELECT * FROM COMPANY WHERE Company_ID = %s", (company_id,))
    if not existing:
        raise NotFoundError(f"Company with ID {company_id} not found.")

    validate_company_payload(data, is_update=True)

    updatable = ["Company_Name", "Company_Type", "Industry", "Location", "Website"]
    set_clauses = []
    params: List[Any] = []

    for field in updatable:
        if field in data and data[field] is not None:
            val = str(data[field]).strip()
            if field == "Company_Name" and val != existing["Company_Name"]:
                conflict = execute_one("SELECT Company_ID FROM COMPANY WHERE Company_Name = %s AND Company_ID != %s", (val, company_id))
                if conflict:
                    raise ConflictError(f"Company name '{val}' is already in use.")
            set_clauses.append(f"{field} = %s")
            params.append(val)

    if set_clauses:
        update_sql = f"UPDATE COMPANY SET {', '.join(set_clauses)} WHERE Company_ID = %s"
        params.append(company_id)
        with get_cursor(commit=True) as cursor:
            cursor.execute(update_sql, tuple(params))

    logger.info("Updated company ID %s", company_id)
    return get_company(company_id)


def delete_company(company_id: int) -> Dict[str, Any]:
    """Safely deletes a company, checking for dependent recruitment drives or placements."""
    company = execute_one("SELECT Company_ID, Company_Name FROM COMPANY WHERE Company_ID = %s", (company_id,))
    if not company:
        raise NotFoundError(f"Company with ID {company_id} not found.")

    # Check dependent drives
    drive_count = execute_one("SELECT COUNT(*) AS total FROM RECRUITMENT_DRIVE WHERE Company_ID = %s", (company_id,))["total"]
    if drive_count > 0:
        raise ProtectedDeleteError(
            f"Cannot delete company ID {company_id} ('{company['Company_Name']}'): "
            f"{drive_count} recruitment drive(s) are registered. Remove drives first."
        )

    # Check placements or internships (FK is ON DELETE RESTRICT)
    hist = execute_one("""
        SELECT 
            (SELECT COUNT(*) FROM PLACEMENT WHERE Company_ID = %s) AS p_cnt,
            (SELECT COUNT(*) FROM INTERNSHIP WHERE Company_ID = %s) AS i_cnt
    """, (company_id, company_id))
    if hist["p_cnt"] > 0 or hist["i_cnt"] > 0:
        raise ProtectedDeleteError(
            f"Cannot delete company ID {company_id} ('{company['Company_Name']}'): "
            f"Historical placement/internship records exist ({hist['p_cnt']} offers, {hist['i_cnt']} internships)."
        )

    with get_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM COMPANY WHERE Company_ID = %s", (company_id,))

    logger.info("Deleted company ID %s ('%s')", company_id, company["Company_Name"])
    return {
        "success": True,
        "message": f"Company '{company['Company_Name']}' (ID: {company_id}) deleted successfully.",
        "deleted_company_id": company_id,
    }

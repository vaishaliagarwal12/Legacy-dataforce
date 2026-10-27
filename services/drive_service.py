import logging
from typing import Dict, Any, List, Optional
from db.connection import get_cursor, execute_one, execute_query
from services.exceptions import ValidationError, NotFoundError, ProtectedDeleteError

logger = logging.getLogger(__name__)

VALID_DRIVE_TYPES = ("Placement", "Internship", "Both")
VALID_SEASONS = ("Summer", "Winter", "Autumn", "Spring", "Other")


def validate_drive_payload(data: Dict[str, Any], is_update: bool = False) -> None:
    """Validates recruitment drive payload."""
    if not is_update:
        required = ["Company_ID", "Drive_Year", "Drive_Type", "Season"]
        for field in required:
            if field not in data or data[field] is None:
                raise ValidationError(f"Missing required field: '{field}'")

    if "Drive_Year" in data and data["Drive_Year"] is not None:
        try:
            year = int(data["Drive_Year"])
            if not (2000 <= year <= 2100):
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Drive_Year must be an integer between 2000 and 2100")

    if "Drive_Type" in data and data["Drive_Type"] is not None:
        dtype = str(data["Drive_Type"]).strip()
        if dtype not in VALID_DRIVE_TYPES:
            raise ValidationError(f"Drive_Type must be one of: {', '.join(VALID_DRIVE_TYPES)}")

    if "Season" in data and data["Season"] is not None:
        season = str(data["Season"]).strip()
        if season not in VALID_SEASONS:
            raise ValidationError(f"Season must be one of: {', '.join(VALID_SEASONS)}")


def create_drive(data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a recruitment drive mapped to a valid recruiting company."""
    validate_drive_payload(data, is_update=False)

    company_id = int(data["Company_ID"])
    year = int(data["Drive_Year"])
    dtype = str(data["Drive_Type"]).strip()
    season = str(data["Season"]).strip()
    drive_date = str(data.get("Drive_Date", "") or "").strip() or None

    # Verify company exists
    company = execute_one("SELECT Company_ID FROM COMPANY WHERE Company_ID = %s", (company_id,))
    if not company:
        raise NotFoundError(f"Company with ID {company_id} does not exist.")

    insert_sql = """
        INSERT INTO RECRUITMENT_DRIVE (Company_ID, Drive_Year, Drive_Type, Season, Drive_Date)
        VALUES (%s, %s, %s, %s, %s)
    """
    with get_cursor(commit=True) as cursor:
        cursor.execute(insert_sql, (company_id, year, dtype, season, drive_date))
        drive_id = cursor.lastrowid

    logger.info("Created drive ID %s for company ID %s", drive_id, company_id)
    return get_drive(drive_id)


def get_drive(drive_id: int) -> Dict[str, Any]:
    """Retrieves drive details including recruiting company and registered opportunities."""
    drive_sql = """
        SELECT rd.Drive_ID, rd.Company_ID, c.Company_Name, c.Company_Type, c.Industry,
               rd.Drive_Year, rd.Drive_Type, rd.Season, rd.Drive_Date
        FROM RECRUITMENT_DRIVE rd
        JOIN COMPANY c ON rd.Company_ID = c.Company_ID
        WHERE rd.Drive_ID = %s
    """
    drive = execute_one(drive_sql, (drive_id,))
    if not drive:
        raise NotFoundError(f"Recruitment Drive with ID {drive_id} not found.")

    if drive.get("Drive_Date"):
        drive["Drive_Date"] = str(drive["Drive_Date"])

    # Fetch opportunities
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

        # Fetch eligible branches from decomposed table
        if opp.get("Eligibility_ID"):
            branches = execute_query(
                "SELECT Branch FROM ELIGIBILITY_BRANCH WHERE Eligibility_ID = %s ORDER BY Branch",
                (opp["Eligibility_ID"],)
            )
            opp["Eligible_Branches"] = [b["Branch"] for b in branches]
        else:
            opp["Eligible_Branches"] = []

        # Fetch selection rounds
        rounds = execute_query(
            "SELECT Round_ID, Round_Number, Round_Type, Description FROM SELECTION_PROCESS WHERE Opportunity_ID = %s ORDER BY Round_Number ASC",
            (opp["Opportunity_ID"],)
        )
        opp["Selection_Rounds"] = rounds

    drive["Opportunities"] = opportunities
    drive["Opportunity_Count"] = len(opportunities)
    return drive


def list_drives(
    company_id: Optional[int] = None,
    drive_year: Optional[int] = None,
    drive_type: Optional[str] = None,
    season: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Lists, filters, and searches recruitment drives."""
    where_clauses = ["1=1"]
    params: List[Any] = []

    if company_id is not None:
        where_clauses.append("rd.Company_ID = %s")
        params.append(int(company_id))

    if drive_year is not None:
        where_clauses.append("rd.Drive_Year = %s")
        params.append(int(drive_year))

    if drive_type:
        where_clauses.append("rd.Drive_Type = %s")
        params.append(drive_type.strip())

    if season:
        where_clauses.append("rd.Season = %s")
        params.append(season.strip())

    where_sql = " AND ".join(where_clauses)
    query_sql = f"""
        SELECT rd.Drive_ID, rd.Company_ID, c.Company_Name, c.Company_Type,
               rd.Drive_Year, rd.Drive_Type, rd.Season, rd.Drive_Date,
               COUNT(o.Opportunity_ID) AS Opportunity_Count
        FROM RECRUITMENT_DRIVE rd
        JOIN COMPANY c ON rd.Company_ID = c.Company_ID
        LEFT JOIN OPPORTUNITY o ON rd.Drive_ID = o.Drive_ID
        WHERE {where_sql}
        GROUP BY rd.Drive_ID
        ORDER BY rd.Drive_Year DESC, rd.Drive_Date DESC
    """
    rows = execute_query(query_sql, tuple(params))
    for r in rows:
        if r.get("Drive_Date"):
            r["Drive_Date"] = str(r["Drive_Date"])
    return rows


def update_drive(drive_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Updates recruitment drive fields."""
    existing = execute_one("SELECT * FROM RECRUITMENT_DRIVE WHERE Drive_ID = %s", (drive_id,))
    if not existing:
        raise NotFoundError(f"Drive with ID {drive_id} not found.")

    validate_drive_payload(data, is_update=True)

    updatable = ["Drive_Year", "Drive_Type", "Season", "Drive_Date"]
    set_clauses = []
    params: List[Any] = []

    for field in updatable:
        if field in data and data[field] is not None:
            val = data[field]
            if field == "Drive_Year":
                val = int(val)
            else:
                val = str(val).strip()
            set_clauses.append(f"{field} = %s")
            params.append(val)

    if set_clauses:
        update_sql = f"UPDATE RECRUITMENT_DRIVE SET {', '.join(set_clauses)} WHERE Drive_ID = %s"
        params.append(drive_id)
        with get_cursor(commit=True) as cursor:
            cursor.execute(update_sql, tuple(params))

    logger.info("Updated drive ID %s", drive_id)
    return get_drive(drive_id)


def delete_drive(drive_id: int) -> Dict[str, Any]:
    """Deletes a recruitment drive and cascades opportunities unless bound to active placements."""
    drive = execute_one("SELECT Drive_ID, Company_ID FROM RECRUITMENT_DRIVE WHERE Drive_ID = %s", (drive_id,))
    if not drive:
        raise NotFoundError(f"Drive with ID {drive_id} not found.")

    # Check if any opportunities under this drive are referenced in PLACEMENT or INTERNSHIP
    bound_check = execute_one("""
        SELECT 
            (SELECT COUNT(*) FROM PLACEMENT p JOIN OPPORTUNITY o ON p.Opportunity_ID = o.Opportunity_ID WHERE o.Drive_ID = %s) AS p_bound,
            (SELECT COUNT(*) FROM INTERNSHIP i JOIN OPPORTUNITY o ON i.Opportunity_ID = o.Opportunity_ID WHERE o.Drive_ID = %s) AS i_bound
    """, (drive_id, drive_id))

    if bound_check["p_bound"] > 0 or bound_check["i_bound"] > 0:
        raise ProtectedDeleteError(
            f"Cannot delete Drive ID {drive_id}: Contains opportunities with registered career offers "
            f"({bound_check['p_bound']} placements, {bound_check['i_bound']} internships)."
        )

    with get_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM RECRUITMENT_DRIVE WHERE Drive_ID = %s", (drive_id,))

    logger.info("Deleted drive ID %s", drive_id)
    return {
        "success": True,
        "message": f"Recruitment Drive ID {drive_id} safely deleted.",
        "deleted_drive_id": drive_id,
    }

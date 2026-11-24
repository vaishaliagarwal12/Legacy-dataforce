import logging
from typing import Dict, Any, List, Optional
from db.connection import get_cursor, execute_one, execute_query
from services.exceptions import ValidationError, NotFoundError, ConflictError, ProtectedDeleteError
from services.security import validate_safe_url

logger = logging.getLogger(__name__)

VALID_COMPANY_TYPES = ("Product", "Service", "Startup", "Other")


def validate_company_payload(data: Dict[str, Any], is_update: bool = False) -> None:
    """Validates company attributes."""
    if not is_update:
        if not data.get("Company_Name") or str(data["Company_Name"]).strip() == "":
            raise ValidationError("Missing required field: 'Company_Name'")

    if "Company_Type" in data and data["Company_Type"] is not None:
        ctype = str(data["Company_Type"]).strip()
        if ctype not in VALID_COMPANY_TYPES:
            raise ValidationError(f"Company_Type must be one of: {', '.join(VALID_COMPANY_TYPES)}")

    if "Website" in data and data["Website"] is not None and str(data["Website"]).strip():
        validate_safe_url(data["Website"], "Website")


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
    """Retrieves full company detail view with placement and internship counts."""
    company = execute_one(
        "SELECT Company_ID, Company_Name, Company_Type, Industry, Location, Website FROM COMPANY WHERE Company_ID = %s",
        (company_id,),
    )
    if not company:
        raise NotFoundError(f"Company with ID {company_id} not found.")

    company["Recruitment_Drives"] = []
    company["Total_Drives"] = 0

    # Check Placement / Internship stats
    history = execute_one(
        """
        SELECT 
            (SELECT COUNT(*) FROM PLACEMENT WHERE Company_ID = %s) AS total_placements,
            (SELECT COUNT(*) FROM INTERNSHIP WHERE Company_ID = %s) AS total_internships
        """,
        (company_id, company_id),
    )
    company["Placement_Count"] = int(history["total_placements"] or 0)
    company["Internship_Count"] = int(history["total_internships"] or 0)
    company["Total_Offers"] = company["Placement_Count"]
    company["Is_Deletable"] = company["Placement_Count"] == 0 and company["Internship_Count"] == 0

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
               0 AS Total_Drives,
               COUNT(DISTINCT p.Placement_ID) AS Total_Placements,
               COUNT(DISTINCT i.Internship_ID) AS Total_Internships
        FROM COMPANY c
        LEFT JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
        LEFT JOIN INTERNSHIP i ON c.Company_ID = i.Company_ID
        WHERE {where_sql}
        GROUP BY c.Company_ID
        ORDER BY c.Company_Name ASC
    """
    rows = execute_query(query_sql, tuple(params) if params else None)
    for r in rows:
        r["Total_Drives"] = 0
        r["Placement_Count"] = int(r["Total_Placements"] or 0)
        r["Internship_Count"] = int(r["Total_Internships"] or 0)
        r["Is_Deletable"] = r["Placement_Count"] == 0 and r["Internship_Count"] == 0
    return rows


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
                conflict = execute_one(
                    "SELECT Company_ID FROM COMPANY WHERE Company_Name = %s AND Company_ID != %s",
                    (val, company_id),
                )
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
    """Safely deletes a company, checking for dependent placements or internships."""
    company = execute_one(
        "SELECT Company_ID, Company_Name FROM COMPANY WHERE Company_ID = %s", (company_id,)
    )
    if not company:
        raise NotFoundError(f"Company with ID {company_id} not found.")

    # Check placements or internships (FK is ON DELETE RESTRICT)
    hist = execute_one(
        """
        SELECT 
            (SELECT COUNT(*) FROM PLACEMENT WHERE Company_ID = %s) AS p_cnt,
            (SELECT COUNT(*) FROM INTERNSHIP WHERE Company_ID = %s) AS i_cnt
        """,
        (company_id, company_id),
    )
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

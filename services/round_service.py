import logging
from typing import Dict, Any, List, Optional
from db.connection import get_cursor, execute_one, execute_query
from services.exceptions import ValidationError, NotFoundError, ConflictError

logger = logging.getLogger(__name__)

VALID_ROUND_TYPES = (
    "Aptitude Test", "Coding Round", "Technical Interview",
    "HR Interview", "Group Discussion", "Managerial Interview", "Other"
)


def validate_round_payload(data: Dict[str, Any], is_update: bool = False) -> None:
    """Validates selection round fields and round type enum."""
    if not is_update:
        required = ["Opportunity_ID", "Round_Number", "Round_Type"]
        for field in required:
            if field not in data or data[field] is None:
                raise ValidationError(f"Missing required field: '{field}'")

    if "Round_Number" in data and data["Round_Number"] is not None:
        try:
            rnum = int(data["Round_Number"])
            if rnum < 1:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Round_Number must be an integer >= 1")

    if "Round_Type" in data and data["Round_Type"] is not None:
        rtype = str(data["Round_Type"]).strip()
        if rtype not in VALID_ROUND_TYPES:
            raise ValidationError(f"Round_Type must be one of: {', '.join(VALID_ROUND_TYPES)}")


def create_round(data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a selection process stage for an opportunity."""
    validate_round_payload(data, is_update=False)

    opp_id = int(data["Opportunity_ID"])
    rnum = int(data["Round_Number"])
    rtype = str(data["Round_Type"]).strip()
    desc = str(data.get("Description", "") or "").strip() or None

    # Check opportunity exists
    opp = execute_one("SELECT Opportunity_ID FROM OPPORTUNITY WHERE Opportunity_ID = %s", (opp_id,))
    if not opp:
        raise NotFoundError(f"Opportunity with ID {opp_id} does not exist.")

    # Unique check (Opportunity_ID, Round_Number)
    dup = execute_one(
        "SELECT Round_ID FROM SELECTION_PROCESS WHERE Opportunity_ID = %s AND Round_Number = %s",
        (opp_id, rnum)
    )
    if dup:
        raise ConflictError(f"Round number {rnum} already exists for Opportunity ID {opp_id}.")

    insert_sql = """
        INSERT INTO SELECTION_PROCESS (Opportunity_ID, Round_Number, Round_Type, Description)
        VALUES (%s, %s, %s, %s)
    """
    with get_cursor(commit=True) as cursor:
        cursor.execute(insert_sql, (opp_id, rnum, rtype, desc))
        round_id = cursor.lastrowid

    logger.info("Created round ID %s (Round #%s: %s) for Opportunity %s", round_id, rnum, rtype, opp_id)
    return get_round(round_id)


def get_round(round_id: int) -> Dict[str, Any]:
    """Retrieves round details with associated opportunity and company metadata."""
    sql = """
        SELECT sp.Round_ID, sp.Opportunity_ID, o.Role, rd.Company_ID, c.Company_Name,
               sp.Round_Number, sp.Round_Type, sp.Description
        FROM SELECTION_PROCESS sp
        JOIN OPPORTUNITY o ON sp.Opportunity_ID = o.Opportunity_ID
        JOIN RECRUITMENT_DRIVE rd ON o.Drive_ID = rd.Drive_ID
        JOIN COMPANY c ON rd.Company_ID = c.Company_ID
        WHERE sp.Round_ID = %s
    """
    round_item = execute_one(sql, (round_id,))
    if not round_item:
        raise NotFoundError(f"Selection round with ID {round_id} not found.")
    return round_item


def list_rounds(opportunity_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Lists selection rounds, optionally filtered by opportunity."""
    where_clauses = ["1=1"]
    params: List[Any] = []

    if opportunity_id is not None:
        where_clauses.append("sp.Opportunity_ID = %s")
        params.append(int(opportunity_id))

    where_sql = " AND ".join(where_clauses)
    query_sql = f"""
        SELECT sp.Round_ID, sp.Opportunity_ID, o.Role, rd.Company_ID, c.Company_Name,
               sp.Round_Number, sp.Round_Type, sp.Description
        FROM SELECTION_PROCESS sp
        JOIN OPPORTUNITY o ON sp.Opportunity_ID = o.Opportunity_ID
        JOIN RECRUITMENT_DRIVE rd ON o.Drive_ID = rd.Drive_ID
        JOIN COMPANY c ON rd.Company_ID = c.Company_ID
        WHERE {where_sql}
        ORDER BY sp.Opportunity_ID ASC, sp.Round_Number ASC
    """
    return execute_query(query_sql, tuple(params))


def update_round(round_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Updates a selection round attributes."""
    existing = execute_one("SELECT * FROM SELECTION_PROCESS WHERE Round_ID = %s", (round_id,))
    if not existing:
        raise NotFoundError(f"Selection round with ID {round_id} not found.")

    validate_round_payload(data, is_update=True)

    updatable = ["Round_Number", "Round_Type", "Description"]
    set_clauses = []
    params: List[Any] = []

    if "Round_Number" in data and data["Round_Number"] is not None:
        new_rnum = int(data["Round_Number"])
        if new_rnum != existing["Round_Number"]:
            dup = execute_one(
                "SELECT Round_ID FROM SELECTION_PROCESS WHERE Opportunity_ID = %s AND Round_Number = %s AND Round_ID != %s",
                (existing["Opportunity_ID"], new_rnum, round_id)
            )
            if dup:
                raise ConflictError(f"Round number {new_rnum} already exists for this opportunity.")
        set_clauses.append("Round_Number = %s")
        params.append(new_rnum)

    if "Round_Type" in data and data["Round_Type"] is not None:
        set_clauses.append("Round_Type = %s")
        params.append(str(data["Round_Type"]).strip())

    if "Description" in data:
        val = str(data["Description"]).strip() if data["Description"] is not None else None
        set_clauses.append("Description = %s")
        params.append(val)

    if set_clauses:
        update_sql = f"UPDATE SELECTION_PROCESS SET {', '.join(set_clauses)} WHERE Round_ID = %s"
        params.append(round_id)
        with get_cursor(commit=True) as cursor:
            cursor.execute(update_sql, tuple(params))

    logger.info("Updated round ID %s", round_id)
    return get_round(round_id)


def delete_round(round_id: int) -> Dict[str, Any]:
    """Deletes a selection round."""
    round_item = execute_one("SELECT Round_ID, Round_Number, Round_Type FROM SELECTION_PROCESS WHERE Round_ID = %s", (round_id,))
    if not round_item:
        raise NotFoundError(f"Selection round with ID {round_id} not found.")

    with get_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM SELECTION_PROCESS WHERE Round_ID = %s", (round_id,))

    logger.info("Deleted round ID %s", round_id)
    return {
        "success": True,
        "message": f"Selection Round #{round_item['Round_Number']} ({round_item['Round_Type']}) deleted successfully.",
        "deleted_round_id": round_id,
    }

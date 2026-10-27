import logging
from typing import Dict, Any, List
from db.connection import execute_one, execute_query
from services.exceptions import NotFoundError

logger = logging.getLogger(__name__)


def list_requirements() -> List[Dict[str, Any]]:
    """Lists the official mandatory internship requirements."""
    sql = """
        SELECT Requirement_ID, Internship_No, Mandatory, Prescribed_Period,
               Required_Result_Semester, Report_Submission_Semester, Credits, Description
        FROM INTERNSHIP_REQUIREMENT
        ORDER BY Internship_No ASC
    """
    return execute_query(sql)


def get_requirement(requirement_id: int) -> Dict[str, Any]:
    """Retrieves an internship requirement by its primary key ID."""
    sql = """
        SELECT Requirement_ID, Internship_No, Mandatory, Prescribed_Period,
               Required_Result_Semester, Report_Submission_Semester, Credits, Description
        FROM INTERNSHIP_REQUIREMENT
        WHERE Requirement_ID = %s
    """
    row = execute_one(sql, (requirement_id,))
    if not row:
        raise NotFoundError(f"Internship requirement with ID {requirement_id} not found.")
    return row

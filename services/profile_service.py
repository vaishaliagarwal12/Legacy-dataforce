import re
import logging
from typing import Dict, Any, List, Optional
from db.connection import get_cursor, execute_one, execute_query
from services.exceptions import ValidationError, NotFoundError, ConflictError

logger = logging.getLogger(__name__)

VALID_PROFILE_TYPES = (
    "Skill", "Project", "Hackathon", "Certification", "Competitive Coding", "Other"
)
VALID_PROFICIENCY_LEVELS = ("Beginner", "Intermediate", "Advanced", "Expert")
PHONE_REGEX = re.compile(r"^\+?[0-9\s\-()]{7,20}$")


def validate_profile_payload(data: Dict[str, Any], is_update: bool = False) -> None:
    """Validates student profile inputs."""
    if not is_update:
        required = ["Student_ID", "Profile_Type", "Title", "Year"]
        for field in required:
            if field not in data or data[field] is None or str(data[field]).strip() == "":
                raise ValidationError(f"Missing required field: '{field}'")

    if "Profile_Type" in data and data["Profile_Type"] is not None:
        ptype = str(data["Profile_Type"]).strip()
        if ptype not in VALID_PROFILE_TYPES:
            raise ValidationError(f"Profile_Type must be one of: {', '.join(VALID_PROFILE_TYPES)}")

    if "Year" in data and data["Year"] is not None:
        try:
            year = int(data["Year"])
            if not (2000 <= year <= 2100):
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Year must be an integer between 2000 and 2100")

    if "Proficiency_Level" in data and data["Proficiency_Level"] is not None and str(data["Proficiency_Level"]).strip() != "":
        prof = str(data["Proficiency_Level"]).strip()
        if prof not in VALID_PROFICIENCY_LEVELS:
            raise ValidationError(f"Proficiency_Level must be one of: {', '.join(VALID_PROFICIENCY_LEVELS)}")


def create_profile(data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a student profile entry (Project, Hackathon, Certification, etc.)."""
    validate_profile_payload(data, is_update=False)

    student_id = int(data["Student_ID"])
    profile_type = str(data["Profile_Type"]).strip()
    title = str(data["Title"]).strip()
    description = str(data.get("Description", "") or "").strip() or None
    link = str(data.get("Link", "") or "").strip() or None
    year = int(data["Year"])
    proficiency = str(data.get("Proficiency_Level", "") or "").strip() or None

    # Check student exists
    student = execute_one("SELECT Student_ID FROM STUDENT WHERE Student_ID = %s", (student_id,))
    if not student:
        raise NotFoundError(f"Student with ID {student_id} does not exist.")

    insert_sql = """
        INSERT INTO STUDENT_PROFILE (Student_ID, Profile_Type, Title, Description, Link, Year, Proficiency_Level)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    with get_cursor(commit=True) as cursor:
        cursor.execute(insert_sql, (student_id, profile_type, title, description, link, year, proficiency))
        profile_id = cursor.lastrowid

    logger.info("Created profile ID %s for student ID %s", profile_id, student_id)
    return get_profile(profile_id)


def get_profile(profile_id: int) -> Dict[str, Any]:
    """Retrieves a single student profile by Profile_ID."""
    sql = """
        SELECT sp.Profile_ID, sp.Student_ID, s.Roll_No, s.First_Name, s.Last_Name,
               sp.Profile_Type, sp.Title, sp.Description, sp.Link, sp.Year, sp.Proficiency_Level
        FROM STUDENT_PROFILE sp
        JOIN STUDENT s ON sp.Student_ID = s.Student_ID
        WHERE sp.Profile_ID = %s
    """
    profile = execute_one(sql, (profile_id,))
    if not profile:
        raise NotFoundError(f"Profile with ID {profile_id} not found.")
    return profile


def list_profiles(
    student_id: Optional[int] = None,
    profile_type: Optional[str] = None,
    year: Optional[int] = None,
    search: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Lists and filters student profiles with optional search."""
    where_clauses = ["1=1"]
    params: List[Any] = []

    if student_id is not None:
        where_clauses.append("sp.Student_ID = %s")
        params.append(int(student_id))

    if profile_type:
        where_clauses.append("sp.Profile_Type = %s")
        params.append(profile_type.strip())

    if year is not None:
        where_clauses.append("sp.Year = %s")
        params.append(int(year))

    if search:
        search_pattern = f"%{search.strip()}%"
        where_clauses.append("(sp.Title LIKE %s OR sp.Description LIKE %s)")
        params.extend([search_pattern, search_pattern])

    where_sql = " AND ".join(where_clauses)
    query_sql = f"""
        SELECT sp.Profile_ID, sp.Student_ID, s.Roll_No, s.First_Name, s.Last_Name,
               sp.Profile_Type, sp.Title, sp.Description, sp.Link, sp.Year, sp.Proficiency_Level
        FROM STUDENT_PROFILE sp
        JOIN STUDENT s ON sp.Student_ID = s.Student_ID
        WHERE {where_sql}
        ORDER BY sp.Year DESC, sp.Profile_ID DESC
    """
    return execute_query(query_sql, tuple(params))


def update_profile(profile_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Updates an existing student profile."""
    existing = execute_one("SELECT * FROM STUDENT_PROFILE WHERE Profile_ID = %s", (profile_id,))
    if not existing:
        raise NotFoundError(f"Profile with ID {profile_id} not found.")

    validate_profile_payload(data, is_update=True)

    updatable = ["Profile_Type", "Title", "Description", "Link", "Year", "Proficiency_Level"]
    set_clauses = []
    params: List[Any] = []

    for field in updatable:
        if field in data:
            val = data[field]
            if field == "Year" and val is not None:
                val = int(val)
            elif val is not None:
                val = str(val).strip()
            set_clauses.append(f"{field} = %s")
            params.append(val)

    if set_clauses:
        update_sql = f"UPDATE STUDENT_PROFILE SET {', '.join(set_clauses)} WHERE Profile_ID = %s"
        params.append(profile_id)
        with get_cursor(commit=True) as cursor:
            cursor.execute(update_sql, tuple(params))

    logger.info("Updated profile ID %s", profile_id)
    return get_profile(profile_id)


def delete_profile(profile_id: int) -> Dict[str, Any]:
    """Deletes a student profile."""
    profile = execute_one("SELECT Profile_ID, Title FROM STUDENT_PROFILE WHERE Profile_ID = %s", (profile_id,))
    if not profile:
        raise NotFoundError(f"Profile with ID {profile_id} not found.")

    with get_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM STUDENT_PROFILE WHERE Profile_ID = %s", (profile_id,))

    logger.info("Deleted profile ID %s", profile_id)
    return {
        "success": True,
        "message": f"Profile '{profile['Title']}' (ID: {profile_id}) deleted successfully.",
        "deleted_profile_id": profile_id,
    }


# ==============================================================================
# Phone Numbers Decomposition Operations
# ==============================================================================

def add_student_phone(student_id: int, phone_no: str) -> Dict[str, Any]:
    """Adds a phone number for a student."""
    p_str = str(phone_no).strip()
    if not PHONE_REGEX.match(p_str):
        raise ValidationError(f"Invalid phone number format: '{p_str}'")

    student = execute_one("SELECT Student_ID, Roll_No FROM STUDENT WHERE Student_ID = %s", (student_id,))
    if not student:
        raise NotFoundError(f"Student with ID {student_id} does not exist.")

    existing = execute_one(
        "SELECT * FROM STUDENT_PHONE WHERE Student_ID = %s AND Phone_No = %s",
        (student_id, p_str)
    )
    if existing:
        raise ConflictError(f"Phone number '{p_str}' is already associated with student ID {student_id}.")

    with get_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO STUDENT_PHONE (Student_ID, Phone_No) VALUES (%s, %s)",
            (student_id, p_str)
        )

    logger.info("Added phone %s to student ID %s", p_str, student_id)
    return {
        "success": True,
        "message": f"Phone number '{p_str}' added successfully to student {student['Roll_No']}.",
        "student_id": student_id,
        "phone_no": p_str,
    }


def list_student_phones(student_id: int) -> List[str]:
    """Retrieves all phone numbers for a student."""
    student = execute_one("SELECT Student_ID FROM STUDENT WHERE Student_ID = %s", (student_id,))
    if not student:
        raise NotFoundError(f"Student with ID {student_id} does not exist.")

    rows = execute_query(
        "SELECT Phone_No FROM STUDENT_PHONE WHERE Student_ID = %s ORDER BY Phone_No",
        (student_id,)
    )
    return [r["Phone_No"] for r in rows]


def delete_student_phone(student_id: int, phone_no: str) -> Dict[str, Any]:
    """Deletes a phone number for a student."""
    p_str = str(phone_no).strip()
    existing = execute_one(
        "SELECT * FROM STUDENT_PHONE WHERE Student_ID = %s AND Phone_No = %s",
        (student_id, p_str)
    )
    if not existing:
        raise NotFoundError(f"Phone number '{p_str}' not found for student ID {student_id}.")

    with get_cursor(commit=True) as cursor:
        cursor.execute(
            "DELETE FROM STUDENT_PHONE WHERE Student_ID = %s AND Phone_No = %s",
            (student_id, p_str)
        )

    logger.info("Deleted phone %s from student ID %s", p_str, student_id)
    return {
        "success": True,
        "message": f"Phone number '{p_str}' removed from student ID {student_id}.",
        "student_id": student_id,
        "phone_no": p_str,
    }

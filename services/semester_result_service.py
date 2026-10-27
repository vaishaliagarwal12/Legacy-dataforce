import logging
from typing import Dict, Any, List, Optional
from db.connection import get_cursor, execute_one, execute_query
from services.exceptions import ValidationError, NotFoundError, ConflictError

logger = logging.getLogger(__name__)


def validate_semester_result_payload(data: Dict[str, Any], is_update: bool = False) -> None:
    """Validates semester result fields."""
    if not is_update:
        required = ["Student_ID", "Semester", "SGPA", "Year", "Total_Credits"]
        for field in required:
            if field not in data or data[field] is None:
                raise ValidationError(f"Missing required field: '{field}'")

    if "Semester" in data and data["Semester"] is not None:
        try:
            sem = int(data["Semester"])
            if not (1 <= sem <= 8):
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Semester must be an integer between 1 and 8")

    if "SGPA" in data and data["SGPA"] is not None:
        try:
            sgpa = float(data["SGPA"])
            if not (0.0 <= sgpa <= 10.0):
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("SGPA must be a decimal number between 0.00 and 10.00")

    if "Year" in data and data["Year"] is not None:
        try:
            year = int(data["Year"])
            if not (2000 <= year <= 2100):
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Year must be an integer between 2000 and 2100")

    if "Total_Credits" in data and data["Total_Credits"] is not None:
        try:
            credits = int(data["Total_Credits"])
            if credits <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Total_Credits must be a positive integer (> 0)")


def create_semester_result(data: Dict[str, Any]) -> Dict[str, Any]:
    """Records an official verified semester result for a student."""
    validate_semester_result_payload(data, is_update=False)

    student_id = int(data["Student_ID"])
    semester = int(data["Semester"])
    sgpa = round(float(data["SGPA"]), 2)
    year = int(data["Year"])
    credits = int(data["Total_Credits"])

    # Verify student exists
    student = execute_one("SELECT Student_ID, Roll_No FROM STUDENT WHERE Student_ID = %s", (student_id,))
    if not student:
        raise NotFoundError(f"Student with ID {student_id} does not exist.")

    # Unique constraint check (Student_ID, Semester)
    existing = execute_one(
        "SELECT Result_ID FROM SEMESTER_RESULT WHERE Student_ID = %s AND Semester = %s",
        (student_id, semester)
    )
    if existing:
        raise ConflictError(
            f"Duplicate result rejected: Semester {semester} result already exists for Student {student['Roll_No']}."
        )

    insert_sql = """
        INSERT INTO SEMESTER_RESULT (Student_ID, Semester, SGPA, Year, Total_Credits)
        VALUES (%s, %s, %s, %s, %s)
    """
    with get_cursor(commit=True) as cursor:
        cursor.execute(insert_sql, (student_id, semester, sgpa, year, credits))
        result_id = cursor.lastrowid

    logger.info("Recorded Semester %s result for student %s (SGPA: %s)", semester, student["Roll_No"], sgpa)
    return get_semester_result(result_id)


def get_semester_result(result_id: int) -> Dict[str, Any]:
    """Retrieves single verified semester result with student metadata."""
    sql = """
        SELECT sr.Result_ID, sr.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch,
               sr.Semester, sr.SGPA, sr.Year, sr.Total_Credits
        FROM SEMESTER_RESULT sr
        JOIN STUDENT s ON sr.Student_ID = s.Student_ID
        WHERE sr.Result_ID = %s
    """
    row = execute_one(sql, (result_id,))
    if not row:
        raise NotFoundError(f"Semester result with ID {result_id} not found.")

    row["SGPA"] = float(row["SGPA"])
    return row


def list_semester_results(
    student_id: Optional[int] = None,
    semester: Optional[int] = None,
    year: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Lists and filters verified semester results."""
    where_clauses = ["1=1"]
    params: List[Any] = []

    if student_id is not None:
        where_clauses.append("sr.Student_ID = %s")
        params.append(int(student_id))

    if semester is not None:
        where_clauses.append("sr.Semester = %s")
        params.append(int(semester))

    if year is not None:
        where_clauses.append("sr.Year = %s")
        params.append(int(year))

    where_sql = " AND ".join(where_clauses)
    query_sql = f"""
        SELECT sr.Result_ID, sr.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch,
               sr.Semester, sr.SGPA, sr.Year, sr.Total_Credits
        FROM SEMESTER_RESULT sr
        JOIN STUDENT s ON sr.Student_ID = s.Student_ID
        WHERE {where_sql}
        ORDER BY sr.Student_ID ASC, sr.Semester ASC
    """
    rows = execute_query(query_sql, tuple(params))
    for r in rows:
        r["SGPA"] = float(r["SGPA"])
    return rows


def update_semester_result(result_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Updates semester result SGPA, year, or credit tallies."""
    existing = get_semester_result(result_id)
    validate_semester_result_payload(data, is_update=True)

    updatable = ["SGPA", "Year", "Total_Credits"]
    set_clauses = []
    params: List[Any] = []

    if "SGPA" in data and data["SGPA"] is not None:
        set_clauses.append("SGPA = %s")
        params.append(round(float(data["SGPA"]), 2))

    if "Year" in data and data["Year"] is not None:
        set_clauses.append("Year = %s")
        params.append(int(data["Year"]))

    if "Total_Credits" in data and data["Total_Credits"] is not None:
        set_clauses.append("Total_Credits = %s")
        params.append(int(data["Total_Credits"]))

    if set_clauses:
        update_sql = f"UPDATE SEMESTER_RESULT SET {', '.join(set_clauses)} WHERE Result_ID = %s"
        params.append(result_id)
        with get_cursor(commit=True) as cursor:
            cursor.execute(update_sql, tuple(params))

    logger.info("Updated semester result ID %s", result_id)
    return get_semester_result(result_id)


def delete_semester_result(result_id: int) -> Dict[str, Any]:
    """Deletes a semester result."""
    result = execute_one("SELECT Result_ID, Student_ID, Semester FROM SEMESTER_RESULT WHERE Result_ID = %s", (result_id,))
    if not result:
        raise NotFoundError(f"Semester result with ID {result_id} not found.")

    with get_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM SEMESTER_RESULT WHERE Result_ID = %s", (result_id,))

    logger.info("Deleted semester result ID %s", result_id)
    return {
        "success": True,
        "message": f"Semester {result['Semester']} result for student ID {result['Student_ID']} deleted successfully.",
        "deleted_result_id": result_id,
    }

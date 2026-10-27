import logging
from typing import Dict, Any, List, Optional
from db.connection import get_cursor, execute_one, execute_query
from services.exceptions import ValidationError, NotFoundError, ConflictError, ProtectedDeleteError

logger = logging.getLogger(__name__)

VALID_COURSE_TYPES = ("Core", "Elective", "Lab", "Seminar")


def validate_course_payload(data: Dict[str, Any], is_update: bool = False) -> None:
    """Validates course fields and enum bounds."""
    if not is_update:
        required = ["University_ID", "Course_Name", "Department", "Semester", "Credits", "Course_Type"]
        for field in required:
            if field not in data or data[field] is None or str(data[field]).strip() == "":
                raise ValidationError(f"Missing required field: '{field}'")

    if "Semester" in data and data["Semester"] is not None:
        try:
            sem = int(data["Semester"])
            if not (1 <= sem <= 8):
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Semester must be an integer between 1 and 8")

    if "Credits" in data and data["Credits"] is not None:
        try:
            credits = int(data["Credits"])
            if credits <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Credits must be a positive integer (> 0)")

    if "Course_Type" in data and data["Course_Type"] is not None:
        ctype = str(data["Course_Type"]).strip()
        if ctype not in VALID_COURSE_TYPES:
            raise ValidationError(f"Course_Type must be one of: {', '.join(VALID_COURSE_TYPES)}")


def create_course(data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a new course catalog record within an atomic transaction."""
    validate_course_payload(data, is_update=False)

    uni_id = int(data["University_ID"])
    name = str(data["Course_Name"]).strip()
    dept = str(data["Department"]).strip()
    sem = int(data["Semester"])
    credits = int(data["Credits"])
    ctype = str(data["Course_Type"]).strip()

    # Validate University exists
    uni = execute_one("SELECT University_ID FROM UNIVERSITY WHERE University_ID = %s", (uni_id,))
    if not uni:
        raise NotFoundError(f"University with ID {uni_id} does not exist.")

    # Unique constraint check
    dup_check = execute_one(
        "SELECT Course_ID FROM COURSE WHERE University_ID = %s AND Course_Name = %s AND Semester = %s",
        (uni_id, name, sem)
    )
    if dup_check:
        raise ConflictError(f"Course '{name}' in Semester {sem} already exists for this university.")

    insert_sql = """
        INSERT INTO COURSE (University_ID, Course_Name, Department, Semester, Credits, Course_Type)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    with get_cursor(commit=True) as cursor:
        cursor.execute(insert_sql, (uni_id, name, dept, sem, credits, ctype))
        course_id = cursor.lastrowid

    logger.info("Created course ID %s ('%s')", course_id, name)
    return get_course(course_id)


def get_course(course_id: int) -> Dict[str, Any]:
    """Retrieves course details and lists all enrolled students."""
    course_sql = """
        SELECT c.Course_ID, c.University_ID, u.University_Name, c.Course_Name,
               c.Department, c.Semester, c.Credits, c.Course_Type
        FROM COURSE c
        JOIN UNIVERSITY u ON c.University_ID = u.University_ID
        WHERE c.Course_ID = %s
    """
    course = execute_one(course_sql, (course_id,))
    if not course:
        raise NotFoundError(f"Course with ID {course_id} not found.")

    # Fetch enrolled students
    enrollments_sql = """
        SELECT s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch,
               sc.Enrollment_Year, sc.Grade
        FROM STUDENT_COURSE sc
        JOIN STUDENT s ON sc.Student_ID = s.Student_ID
        WHERE sc.Course_ID = %s
        ORDER BY sc.Enrollment_Year DESC, s.Roll_No ASC
    """
    enrolled_students = execute_query(enrollments_sql, (course_id,))
    course["Enrolled_Students"] = enrolled_students
    course["Enrolled_Count"] = len(enrolled_students)

    return course


def list_courses(
    search: Optional[str] = None,
    department: Optional[str] = None,
    semester: Optional[int] = None,
    course_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Lists, searches, and filters courses with enrollment counts."""
    where_clauses = ["1=1"]
    params: List[Any] = []

    if search:
        search_pattern = f"%{search.strip()}%"
        where_clauses.append("(c.Course_Name LIKE %s OR c.Department LIKE %s)")
        params.extend([search_pattern, search_pattern])

    if department:
        where_clauses.append("c.Department = %s")
        params.append(department.strip())

    if semester is not None:
        where_clauses.append("c.Semester = %s")
        params.append(int(semester))

    if course_type:
        where_clauses.append("c.Course_Type = %s")
        params.append(course_type.strip())

    where_sql = " AND ".join(where_clauses)
    query_sql = f"""
        SELECT c.Course_ID, c.University_ID, u.University_Name, c.Course_Name,
               c.Department, c.Semester, c.Credits, c.Course_Type,
               COUNT(sc.Student_ID) AS Enrolled_Count
        FROM COURSE c
        JOIN UNIVERSITY u ON c.University_ID = u.University_ID
        LEFT JOIN STUDENT_COURSE sc ON c.Course_ID = sc.Course_ID
        WHERE {where_sql}
        GROUP BY c.Course_ID
        ORDER BY c.Department ASC, c.Semester ASC, c.Course_Name ASC
    """
    return execute_query(query_sql, tuple(params))


def update_course(course_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Updates course parameters safely with boundary and conflict checks."""
    existing = execute_one("SELECT * FROM COURSE WHERE Course_ID = %s", (course_id,))
    if not existing:
        raise NotFoundError(f"Course with ID {course_id} not found.")

    validate_course_payload(data, is_update=True)

    updatable_fields = ["Course_Name", "Department", "Semester", "Credits", "Course_Type"]
    set_clauses = []
    params: List[Any] = []

    for field in updatable_fields:
        if field in data and data[field] is not None:
            val = data[field]
            if field in ("Semester", "Credits"):
                val = int(val)
            else:
                val = str(val).strip()
            set_clauses.append(f"{field} = %s")
            params.append(val)

    if set_clauses:
        update_sql = f"UPDATE COURSE SET {', '.join(set_clauses)} WHERE Course_ID = %s"
        params.append(course_id)
        with get_cursor(commit=True) as cursor:
            cursor.execute(update_sql, tuple(params))

    logger.info("Updated course ID %s", course_id)
    return get_course(course_id)


def delete_course(course_id: int) -> Dict[str, Any]:
    """Safely deletes a course, blocking if student registrations depend on it."""
    course = execute_one("SELECT Course_ID, Course_Name FROM COURSE WHERE Course_ID = %s", (course_id,))
    if not course:
        raise NotFoundError(f"Course with ID {course_id} not found.")

    # Safe delete check: Verify no enrolled students
    reg_count = execute_one(
        "SELECT COUNT(*) AS total FROM STUDENT_COURSE WHERE Course_ID = %s",
        (course_id,)
    )["total"]

    if reg_count > 0:
        raise ProtectedDeleteError(
            f"Cannot delete course ID {course_id} ('{course['Course_Name']}'): "
            f"{reg_count} active student registration(s) exist. Unregister students first."
        )

    with get_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM COURSE WHERE Course_ID = %s", (course_id,))

    logger.info("Safely deleted course ID %s ('%s')", course_id, course["Course_Name"])
    return {
        "success": True,
        "message": f"Course '{course['Course_Name']}' (ID: {course_id}) safely deleted.",
        "deleted_course_id": course_id,
    }

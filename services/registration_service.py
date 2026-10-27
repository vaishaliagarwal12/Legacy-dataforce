import logging
from typing import Dict, Any, List, Optional
from db.connection import get_cursor, execute_one, execute_query
from services.exceptions import ValidationError, NotFoundError, ConflictError

logger = logging.getLogger(__name__)

VALID_GRADES = ("A+", "A", "B+", "B", "C+", "C", "D", "F", "P", "I", "W")


def validate_registration_payload(data: Dict[str, Any], is_update: bool = False) -> None:
    """Validates registration fields."""
    if not is_update:
        required = ["Student_ID", "Course_ID", "Enrollment_Year"]
        for field in required:
            if field not in data or data[field] is None:
                raise ValidationError(f"Missing required field: '{field}'")

    if "Enrollment_Year" in data and data["Enrollment_Year"] is not None:
        try:
            year = int(data["Enrollment_Year"])
            if not (2000 <= year <= 2100):
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Enrollment_Year must be an integer between 2000 and 2100")

    if "Grade" in data and data["Grade"] is not None and str(data["Grade"]).strip() != "":
        grade = str(data["Grade"]).strip().upper()
        if grade not in VALID_GRADES:
            raise ValidationError(f"Grade must be one of: {', '.join(VALID_GRADES)}")


def register_student_course(data: Dict[str, Any]) -> Dict[str, Any]:
    """Enrolls a student into an academic course."""
    validate_registration_payload(data, is_update=False)

    student_id = int(data["Student_ID"])
    course_id = int(data["Course_ID"])
    year = int(data["Enrollment_Year"])
    grade = str(data.get("Grade", "") or "").strip().upper() or None

    # Check Student exists
    student = execute_one("SELECT Student_ID, Roll_No FROM STUDENT WHERE Student_ID = %s", (student_id,))
    if not student:
        raise NotFoundError(f"Student with ID {student_id} does not exist.")

    # Check Course exists
    course = execute_one("SELECT Course_ID, Course_Name FROM COURSE WHERE Course_ID = %s", (course_id,))
    if not course:
        raise NotFoundError(f"Course with ID {course_id} does not exist.")

    # Check already registered
    existing = execute_one(
        "SELECT * FROM STUDENT_COURSE WHERE Student_ID = %s AND Course_ID = %s",
        (student_id, course_id)
    )
    if existing:
        raise ConflictError(
            f"Student {student['Roll_No']} is already registered for course '{course['Course_Name']}'."
        )

    insert_sql = """
        INSERT INTO STUDENT_COURSE (Student_ID, Course_ID, Enrollment_Year, Grade)
        VALUES (%s, %s, %s, %s)
    """
    with get_cursor(commit=True) as cursor:
        cursor.execute(insert_sql, (student_id, course_id, year, grade))

    logger.info("Enrolled student %s into course %s for year %s", student_id, course_id, year)
    return get_registration(student_id, course_id)


def get_registration(student_id: int, course_id: int) -> Dict[str, Any]:
    """Retrieves an existing registration entry with full student and course context."""
    sql = """
        SELECT sc.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch,
               sc.Course_ID, c.Course_Name, c.Department, c.Semester, c.Credits, c.Course_Type,
               sc.Enrollment_Year, sc.Grade
        FROM STUDENT_COURSE sc
        JOIN STUDENT s ON sc.Student_ID = s.Student_ID
        JOIN COURSE c ON sc.Course_ID = c.Course_ID
        WHERE sc.Student_ID = %s AND sc.Course_ID = %s
    """
    reg = execute_one(sql, (student_id, course_id))
    if not reg:
        raise NotFoundError(f"Registration for Student ID {student_id} and Course ID {course_id} not found.")
    return reg


def list_registrations(
    student_id: Optional[int] = None,
    course_id: Optional[int] = None,
    enrollment_year: Optional[int] = None,
    grade: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Lists and filters student-course enrollments."""
    where_clauses = ["1=1"]
    params: List[Any] = []

    if student_id is not None:
        where_clauses.append("sc.Student_ID = %s")
        params.append(int(student_id))

    if course_id is not None:
        where_clauses.append("sc.Course_ID = %s")
        params.append(int(course_id))

    if enrollment_year is not None:
        where_clauses.append("sc.Enrollment_Year = %s")
        params.append(int(enrollment_year))

    if grade:
        where_clauses.append("sc.Grade = %s")
        params.append(grade.strip().upper())

    where_sql = " AND ".join(where_clauses)
    query_sql = f"""
        SELECT sc.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch,
               sc.Course_ID, c.Course_Name, c.Department, c.Semester, c.Credits, c.Course_Type,
               sc.Enrollment_Year, sc.Grade
        FROM STUDENT_COURSE sc
        JOIN STUDENT s ON sc.Student_ID = s.Student_ID
        JOIN COURSE c ON sc.Course_ID = c.Course_ID
        WHERE {where_sql}
        ORDER BY sc.Enrollment_Year DESC, s.Roll_No ASC
    """
    return execute_query(query_sql, tuple(params))


def update_registration(student_id: int, course_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Updates enrollment grade or year."""
    existing = execute_one(
        "SELECT * FROM STUDENT_COURSE WHERE Student_ID = %s AND Course_ID = %s",
        (student_id, course_id)
    )
    if not existing:
        raise NotFoundError(f"Registration for Student {student_id} in Course {course_id} not found.")

    validate_registration_payload(data, is_update=True)

    set_clauses = []
    params: List[Any] = []

    if "Enrollment_Year" in data and data["Enrollment_Year"] is not None:
        set_clauses.append("Enrollment_Year = %s")
        params.append(int(data["Enrollment_Year"]))

    if "Grade" in data:
        val = str(data["Grade"]).strip().upper() if data["Grade"] else None
        set_clauses.append("Grade = %s")
        params.append(val)

    if set_clauses:
        update_sql = f"UPDATE STUDENT_COURSE SET {', '.join(set_clauses)} WHERE Student_ID = %s AND Course_ID = %s"
        params.extend([student_id, course_id])
        with get_cursor(commit=True) as cursor:
            cursor.execute(update_sql, tuple(params))

    logger.info("Updated registration for student %s and course %s", student_id, course_id)
    return get_registration(student_id, course_id)


def unregister_student_course(student_id: int, course_id: int) -> Dict[str, Any]:
    """Removes a student enrollment from a course safely."""
    existing = execute_one(
        "SELECT * FROM STUDENT_COURSE WHERE Student_ID = %s AND Course_ID = %s",
        (student_id, course_id)
    )
    if not existing:
        raise NotFoundError(f"Registration for Student {student_id} in Course {course_id} not found.")

    with get_cursor(commit=True) as cursor:
        cursor.execute(
            "DELETE FROM STUDENT_COURSE WHERE Student_ID = %s AND Course_ID = %s",
            (student_id, course_id)
        )

    logger.info("Unregistered student %s from course %s", student_id, course_id)
    return {
        "success": True,
        "message": f"Student {student_id} successfully unregistered from course {course_id}.",
        "student_id": student_id,
        "course_id": course_id,
    }

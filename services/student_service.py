import re
import logging
from typing import Dict, Any, List, Optional
from db.connection import get_cursor, execute_one, execute_query
from services.exceptions import ValidationError, NotFoundError, ConflictError, ProtectedDeleteError

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
PHONE_REGEX = re.compile(r"^\+?[0-9\s\-()]{7,20}$")


def validate_student_payload(data: Dict[str, Any], is_update: bool = False) -> None:
    """Validates student data fields and data types."""
    if not is_update:
        required = ["Roll_No", "First_Name", "Branch", "Batch_Year", "CGPA", "Email"]
        for field in required:
            if field not in data or data[field] is None or str(data[field]).strip() == "":
                raise ValidationError(f"Missing required field: '{field}'")

    if "CGPA" in data and data["CGPA"] is not None:
        try:
            cgpa = float(data["CGPA"])
            if not (0.0 <= cgpa <= 10.0):
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("CGPA must be a decimal number between 0.00 and 10.00")

    if "Backlogs" in data and data["Backlogs"] is not None:
        try:
            backlogs = int(data["Backlogs"])
            if backlogs < 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Backlogs must be a non-negative integer (>= 0)")

    if "Batch_Year" in data and data["Batch_Year"] is not None:
        try:
            batch_year = int(data["Batch_Year"])
            if not (2000 <= batch_year <= 2100):
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Batch_Year must be an integer between 2000 and 2100")

    if "Email" in data and data["Email"] is not None:
        email = str(data["Email"]).strip()
        if not EMAIL_REGEX.match(email):
            raise ValidationError(f"Invalid email format: '{email}'")

    if "Phone_Numbers" in data and data["Phone_Numbers"] is not None:
        phones = data["Phone_Numbers"]
        if not isinstance(phones, list):
            raise ValidationError("Phone_Numbers must be a list of phone strings")
        for phone in phones:
            p_str = str(phone).strip()
            if not PHONE_REGEX.match(p_str):
                raise ValidationError(f"Invalid phone number format: '{p_str}'")


def create_student(data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a student and associated phone numbers inside a safe transaction."""
    validate_student_payload(data, is_update=False)

    roll_no = str(data["Roll_No"]).strip()
    first_name = str(data["First_Name"]).strip()
    last_name = str(data.get("Last_Name", "") or "").strip() or None
    branch = str(data["Branch"]).strip()
    batch_year = int(data["Batch_Year"])
    section = str(data.get("Section", "") or "").strip() or None
    cgpa = round(float(data["CGPA"]), 2)
    backlogs = int(data.get("Backlogs", 0))
    email = str(data["Email"]).strip()
    resume_link = str(data.get("Resume_Link", "") or "").strip() or None
    phone_numbers = [str(p).strip() for p in data.get("Phone_Numbers", []) if str(p).strip()]

    # Uniqueness checks
    existing_roll = execute_one("SELECT Student_ID FROM STUDENT WHERE Roll_No = %s", (roll_no,))
    if existing_roll:
        raise ConflictError(f"A student with Roll_No '{roll_no}' already exists.")

    existing_email = execute_one("SELECT Student_ID FROM STUDENT WHERE Email = %s", (email,))
    if existing_email:
        raise ConflictError(f"A student with Email '{email}' already exists.")

    insert_sql = """
        INSERT INTO STUDENT (
            Roll_No, First_Name, Last_Name, Branch, Batch_Year, Section,
            CGPA, Backlogs, Email, Resume_Link
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    with get_cursor(commit=True) as cursor:
        cursor.execute(
            insert_sql,
            (roll_no, first_name, last_name, branch, batch_year, section, cgpa, backlogs, email, resume_link)
        )
        student_id = cursor.lastrowid

        # Insert phone numbers if provided
        if phone_numbers:
            phone_sql = "INSERT INTO STUDENT_PHONE (Student_ID, Phone_No) VALUES (%s, %s)"
            phone_tuples = [(student_id, phone) for phone in set(phone_numbers)]
            cursor.executemany(phone_sql, phone_tuples)

    logger.info("Successfully created student ID %s (Roll: %s)", student_id, roll_no)
    return get_student(student_id)


def get_student(student_id: int) -> Dict[str, Any]:
    """Retrieves full student details including contact numbers, courses, profiles, and placement history."""
    student_sql = """
        SELECT Student_ID, Roll_No, First_Name, Last_Name, Branch, Batch_Year,
               Section, CGPA, Backlogs, Email, Resume_Link
        FROM STUDENT
        WHERE Student_ID = %s
    """
    student = execute_one(student_sql, (student_id,))
    if not student:
        raise NotFoundError(f"Student with ID {student_id} not found.")

    # Convert Decimal CGPA to float for JSON serialization
    student["CGPA"] = float(student["CGPA"])

    # Phone numbers
    phones_sql = "SELECT Phone_No FROM STUDENT_PHONE WHERE Student_ID = %s ORDER BY Phone_No"
    phones = execute_query(phones_sql, (student_id,))
    student["Phone_Numbers"] = [p["Phone_No"] for p in phones]

    # Registered Courses
    courses_sql = """
        SELECT c.Course_ID, c.Course_Name, c.Department, c.Semester, c.Credits, c.Course_Type,
               sc.Enrollment_Year, sc.Grade
        FROM STUDENT_COURSE sc
        JOIN COURSE c ON sc.Course_ID = c.Course_ID
        WHERE sc.Student_ID = %s
        ORDER BY sc.Enrollment_Year DESC, c.Semester ASC
    """
    student["Registered_Courses"] = execute_query(courses_sql, (student_id,))

    # Profiles (Skills, Projects, Hackathons, Certs, Coding profiles)
    profiles_sql = """
        SELECT Profile_ID, Profile_Type, Title, Description, Link, Year, Proficiency_Level
        FROM STUDENT_PROFILE
        WHERE Student_ID = %s
        ORDER BY Year DESC, Profile_Type ASC
    """
    student["Profiles"] = execute_query(profiles_sql, (student_id,))

    # Skills from STUDENT_SKILL
    skills_sql = "SELECT Skill FROM STUDENT_SKILL WHERE Student_ID = %s ORDER BY Skill"
    skills = execute_query(skills_sql, (student_id,))
    student["Skills"] = [s["Skill"] for s in skills]

    # Career history status
    history_sql = """
        SELECT 
            (SELECT COUNT(*) FROM PLACEMENT WHERE Student_ID = %s) AS placement_count,
            (SELECT COUNT(*) FROM INTERNSHIP WHERE Student_ID = %s) AS internship_count
    """
    history = execute_one(history_sql, (student_id, student_id))
    student["Placement_Count"] = history["placement_count"]
    student["Internship_Count"] = history["internship_count"]
    student["Is_Deletable"] = (history["placement_count"] == 0 and history["internship_count"] == 0)

    return student


def list_students(
    search: Optional[str] = None,
    branch: Optional[str] = None,
    batch_year: Optional[int] = None,
    min_cgpa: Optional[float] = None,
    max_cgpa: Optional[float] = None,
    max_backlogs: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """Searches and filters students with parameterized dynamic queries and pagination."""
    where_clauses = ["1=1"]
    params: List[Any] = []

    if search:
        search_pattern = f"%{search.strip()}%"
        where_clauses.append(
            "(s.Roll_No LIKE %s OR s.First_Name LIKE %s OR s.Last_Name LIKE %s OR s.Email LIKE %s)"
        )
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern])

    if branch:
        where_clauses.append("s.Branch = %s")
        params.append(branch.strip())

    if batch_year is not None:
        where_clauses.append("s.Batch_Year = %s")
        params.append(int(batch_year))

    if min_cgpa is not None:
        where_clauses.append("s.CGPA >= %s")
        params.append(float(min_cgpa))

    if max_cgpa is not None:
        where_clauses.append("s.CGPA <= %s")
        params.append(float(max_cgpa))

    if max_backlogs is not None:
        where_clauses.append("s.Backlogs <= %s")
        params.append(int(max_backlogs))

    where_sql = " AND ".join(where_clauses)

    count_sql = f"SELECT COUNT(*) AS total FROM STUDENT s WHERE {where_sql}"
    count_res = execute_one(count_sql, tuple(params))
    total_count = count_res["total"] if count_res else 0

    query_sql = f"""
        SELECT s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch,
               s.Batch_Year, s.Section, s.CGPA, s.Backlogs, s.Email, s.Resume_Link,
               GROUP_CONCAT(DISTINCT sp.Phone_No SEPARATOR ', ') AS Phone_Numbers,
               COUNT(DISTINCT p.Placement_ID) AS Placement_Offers,
               COUNT(DISTINCT i.Internship_ID) AS Internships
        FROM STUDENT s
        LEFT JOIN STUDENT_PHONE sp ON s.Student_ID = sp.Student_ID
        LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
        LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
        WHERE {where_sql}
        GROUP BY s.Student_ID
        ORDER BY s.Student_ID ASC
        LIMIT %s OFFSET %s
    """
    exec_params = list(params) + [int(limit), int(offset)]
    rows = execute_query(query_sql, tuple(exec_params))

    for r in rows:
        r["CGPA"] = float(r["CGPA"])
        r["Phone_Numbers"] = r["Phone_Numbers"].split(", ") if r["Phone_Numbers"] else []

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "results": rows,
    }


def update_student(student_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Updates student fields and updates phone numbers within an atomic transaction."""
    existing = execute_one("SELECT * FROM STUDENT WHERE Student_ID = %s", (student_id,))
    if not existing:
        raise NotFoundError(f"Student with ID {student_id} not found.")

    validate_student_payload(data, is_update=True)

    updatable_fields = [
        "First_Name", "Last_Name", "Branch", "Batch_Year",
        "Section", "CGPA", "Backlogs", "Email", "Resume_Link"
    ]
    set_clauses = []
    params: List[Any] = []

    for field in updatable_fields:
        if field in data:
            val = data[field]
            if field in ("CGPA",):
                val = round(float(val), 2)
            elif field in ("Backlogs", "Batch_Year"):
                val = int(val)
            elif val is not None:
                val = str(val).strip()

            if field == "Email" and val != existing["Email"]:
                conflict = execute_one(
                    "SELECT Student_ID FROM STUDENT WHERE Email = %s AND Student_ID != %s",
                    (val, student_id)
                )
                if conflict:
                    raise ConflictError(f"Email '{val}' is already in use by another student.")

            set_clauses.append(f"{field} = %s")
            params.append(val)

    with get_cursor(commit=True) as cursor:
        if set_clauses:
            update_sql = f"UPDATE STUDENT SET {', '.join(set_clauses)} WHERE Student_ID = %s"
            params.append(student_id)
            cursor.execute(update_sql, tuple(params))

        # Update phone numbers if provided
        if "Phone_Numbers" in data and data["Phone_Numbers"] is not None:
            new_phones = [str(p).strip() for p in data["Phone_Numbers"] if str(p).strip()]
            cursor.execute("DELETE FROM STUDENT_PHONE WHERE Student_ID = %s", (student_id,))
            if new_phones:
                phone_sql = "INSERT INTO STUDENT_PHONE (Student_ID, Phone_No) VALUES (%s, %s)"
                phone_tuples = [(student_id, p) for p in set(new_phones)]
                cursor.executemany(phone_sql, phone_tuples)

    logger.info("Successfully updated student ID %s", student_id)
    return get_student(student_id)


def delete_student(student_id: int) -> Dict[str, Any]:
    """Safely deletes a student record ONLY if no placement or internship records exist.
    
    BLOCKS deletion if the student has placement offers or internship history to ensure
    career reporting integrity and prevent destruction of institutional audit trails.
    """
    student = execute_one(
        "SELECT Student_ID, Roll_No, First_Name, Last_Name FROM STUDENT WHERE Student_ID = %s",
        (student_id,)
    )
    if not student:
        raise NotFoundError(f"Student with ID {student_id} not found.")

    # Check placement and internship history
    history_check_sql = """
        SELECT 
            (SELECT COUNT(*) FROM PLACEMENT WHERE Student_ID = %s) AS placement_count,
            (SELECT COUNT(*) FROM INTERNSHIP WHERE Student_ID = %s) AS internship_count
    """
    history = execute_one(history_check_sql, (student_id, student_id))
    placement_count = history["placement_count"]
    internship_count = history["internship_count"]

    if placement_count > 0 or internship_count > 0:
        details = []
        if placement_count > 0:
            details.append(f"{placement_count} placement offer(s)")
        if internship_count > 0:
            details.append(f"{internship_count} internship record(s)")

        error_msg = (
            f"Cannot delete student ID {student_id} ({student['Roll_No']}): "
            f"Active career history detected ({', '.join(details)}). "
            "Deletion is blocked to maintain institutional compliance and historical records."
        )
        logger.warning("Blocked student deletion: %s", error_msg)
        raise ProtectedDeleteError(error_msg)

    # Safe delete within transaction (cascading phones, skills, registrations, profiles)
    with get_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM STUDENT WHERE Student_ID = %s", (student_id,))

    logger.info("Safely deleted student ID %s (%s)", student_id, student["Roll_No"])
    return {
        "success": True,
        "message": f"Student {student['Roll_No']} ({student['First_Name']} {student['Last_Name']}) safely deleted.",
        "deleted_student_id": student_id,
    }

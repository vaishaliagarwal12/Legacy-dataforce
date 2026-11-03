import re
import math
import logging
from typing import Dict, Any, List, Optional
from db.connection import get_cursor, execute_one, execute_query
from services.exceptions import ValidationError, NotFoundError, ConflictError, ProtectedDeleteError
from services.security import validate_safe_url

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
PHONE_REGEX = re.compile(r"^\+?[0-9\s\-()]{7,20}$")


def validate_student_payload(data: Dict[str, Any], is_update: bool = False) -> None:
    """Validates student data fields, data formats, and business constraints."""
    if not is_update:
        required = ["Roll_No", "First_Name", "Branch", "Batch_Year", "CGPA", "Email"]
        for field in required:
            if field not in data or data[field] is None or str(data[field]).strip() == "":
                raise ValidationError(f"Missing required field: '{field}'")

    if "Roll_No" in data and data["Roll_No"] is not None:
        roll = str(data["Roll_No"]).strip()
        if len(roll) < 3 or len(roll) > 20:
            raise ValidationError("Roll number must be between 3 and 20 characters in length.")

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
        if isinstance(phones, str):
            phones = [p.strip() for p in phones.split(",") if p.strip()]
        if not isinstance(phones, list):
            raise ValidationError("Phone_Numbers must be a list or comma-separated string of phone numbers")
        for phone in phones:
            p_str = str(phone).strip()
            if not PHONE_REGEX.match(p_str):
                raise ValidationError(f"Invalid phone number format: '{p_str}'")

    if "Resume_Link" in data and data["Resume_Link"] is not None and str(data["Resume_Link"]).strip():
        validate_safe_url(data["Resume_Link"], "Resume_Link")


def create_student(data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a new student and associated multivalued phones/skills inside an atomic transaction."""
    validate_student_payload(data, is_update=False)

    roll_no = str(data["Roll_No"]).strip().upper()
    first_name = str(data["First_Name"]).strip()
    last_name = str(data.get("Last_Name", "") or "").strip() or None
    branch = str(data["Branch"]).strip()
    batch_year = int(data["Batch_Year"])
    section = str(data.get("Section", "A") or "A").strip() or "A"
    cgpa = round(float(data["CGPA"]), 2)
    backlogs = int(data.get("Backlogs", 0))
    email = str(data["Email"]).strip().lower()
    resume_link = str(data.get("Resume_Link", "") or "").strip() or None

    raw_phones = data.get("Phone_Numbers", [])
    if isinstance(raw_phones, str):
        raw_phones = [p.strip() for p in raw_phones.split(",") if p.strip()]
    phone_numbers = [str(p).strip() for p in raw_phones if str(p).strip()]

    raw_skills = data.get("Skills", [])
    if isinstance(raw_skills, str):
        raw_skills = [s.strip() for s in raw_skills.split(",") if s.strip()]
    skills = [str(s).strip() for s in raw_skills if str(s).strip()]

    # Uniqueness checks to prevent duplicate records
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

    # ATOMIC TRANSACTION: Insert student + dependent multivalued phones & skills
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            insert_sql,
            (roll_no, first_name, last_name, branch, batch_year, section, cgpa, backlogs, email, resume_link)
        )
        student_id = cursor.lastrowid

        # Multivalued contact numbers
        if phone_numbers:
            phone_sql = "INSERT INTO STUDENT_PHONE (Student_ID, Phone_No) VALUES (%s, %s)"
            phone_tuples = [(student_id, phone) for phone in set(phone_numbers)]
            cursor.executemany(phone_sql, phone_tuples)

        # Multivalued technical skills
        if skills:
            skill_sql = "INSERT INTO STUDENT_SKILL (Student_ID, Skill) VALUES (%s, %s)"
            skill_tuples = [(student_id, skill) for skill in set(skills)]
            cursor.executemany(skill_sql, skill_tuples)

    logger.info("Successfully created student ID %s (Roll: %s)", student_id, roll_no)
    return get_student(student_id)


def get_student(student_id: int) -> Dict[str, Any]:
    """Retrieves full student details across all 9 profile sections:
    1. Personal details
    2. Academic details
    3. Semester results
    4. Registered courses
    5. Technical skills
    6. Projects and achievements
    7. Resume and education documents
    8. Internship history
    9. Placement offers
    """
    student_sql = """
        SELECT Student_ID, Roll_No, First_Name, Last_Name, Branch, Batch_Year,
               Section, CGPA, Backlogs, Email, Resume_Link
        FROM STUDENT
        WHERE Student_ID = %s
    """
    student = execute_one(student_sql, (student_id,))
    if not student:
        raise NotFoundError(f"Student with ID {student_id} not found.")

    student["CGPA"] = float(student["CGPA"])
    student["Full_Name"] = f"{student['First_Name']} {student.get('Last_Name') or ''}".strip()
    student["Is_Eligible"] = (student["Backlogs"] == 0 and student["CGPA"] >= 6.0)

    # 1. Personal Details: Phone Numbers
    phones_sql = "SELECT Phone_No FROM STUDENT_PHONE WHERE Student_ID = %s ORDER BY Phone_No"
    phones = execute_query(phones_sql, (student_id,))
    student["Phone_Numbers"] = [p["Phone_No"] for p in phones]

    # 2. Registered Courses
    courses_sql = """
        SELECT c.Course_ID, c.Course_Name, c.Department, c.Semester, c.Credits, c.Course_Type,
               sc.Enrollment_Year, sc.Grade
        FROM STUDENT_COURSE sc
        JOIN COURSE c ON sc.Course_ID = c.Course_ID
        WHERE sc.Student_ID = %s
        ORDER BY sc.Enrollment_Year DESC, c.Semester ASC
    """
    student["Registered_Courses"] = execute_query(courses_sql, (student_id,))

    # 3. Profiles: Projects, Achievements, Certifications, Hackathons
    profiles_sql = """
        SELECT Profile_ID, Profile_Type, Title, Description, Link, Year, Proficiency_Level
        FROM STUDENT_PROFILE
        WHERE Student_ID = %s
        ORDER BY Year DESC, Profile_Type ASC
    """
    profiles = execute_query(profiles_sql, (student_id,))
    student["Profiles"] = profiles
    student["Projects"] = [
        p for p in profiles 
        if str(p.get("Profile_Type", "")).lower() in ("project", "research")
    ]
    student["Achievements"] = [
        p for p in profiles 
        if str(p.get("Profile_Type", "")).lower() in ("hackathon", "achievement", "award", "certification", "codingprofile", "competitive")
    ]

    # 4. Technical Skills (STUDENT_SKILL + Profiles)
    skills_sql = "SELECT Skill FROM STUDENT_SKILL WHERE Student_ID = %s ORDER BY Skill"
    skills = execute_query(skills_sql, (student_id,))
    student["Skills"] = [s["Skill"] for s in skills]

    # 5. Semester Results (SGPA, Credits, Semester breakdown)
    sem_sql = """
        SELECT Result_ID, Semester, SGPA, Total_Credits, Year
        FROM SEMESTER_RESULT
        WHERE Student_ID = %s
        ORDER BY Semester ASC
    """
    sem_rows = execute_query(sem_sql, (student_id,))
    for sr in sem_rows:
        sr["SGPA"] = float(sr["SGPA"])
    student["Semester_Results"] = sem_rows

    # 6. Uploaded Resumes
    resume_sql = """
        SELECT Resume_ID, File_Name, File_Link, Resume_Year, Upload_Date
        FROM RESUME
        WHERE Student_ID = %s
        ORDER BY Resume_Year DESC, Upload_Date DESC
    """
    student["Resumes"] = execute_query(resume_sql, (student_id,))

    # 7. Education Documents (10th/12th marksheets & certificates)
    doc_sql = """
        SELECT ed.Doc_ID, ed.Document_Type, ed.Board, ed.Percentage_CGPA, ed.Year_of_Passing, ed.File_Link,
               r.File_Name AS Attached_Resume
        FROM EDUCATION_DOCUMENT ed
        JOIN RESUME r ON ed.Resume_ID = r.Resume_ID
        WHERE r.Student_ID = %s
        ORDER BY ed.Year_of_Passing ASC
    """
    doc_rows = execute_query(doc_sql, (student_id,))
    for dr in doc_rows:
        dr["Percentage_CGPA"] = float(dr["Percentage_CGPA"]) if dr.get("Percentage_CGPA") is not None else None
    student["Education_Documents"] = doc_rows

    # 8. Placement Offers (with Recruiting Company details)
    placements_sql = """
        SELECT p.Placement_ID, p.Role, p.Package, p.Placement_Year, p.Placement_Type,
               p.Is_PPO, p.Joined, p.Offer_Status, p.Interview_Rounds,
               c.Company_ID, c.Company_Name, c.Company_Type, c.Location, c.Website
        FROM PLACEMENT p
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE p.Student_ID = %s
        ORDER BY p.Placement_Year DESC, p.Package DESC
    """
    placements = execute_query(placements_sql, (student_id,))
    for pl in placements:
        pl["Package"] = float(pl["Package"])
    student["Placements"] = placements
    student["Placement_Count"] = len(placements)

    # 9. Internships (Mandatory #1, #2, and Additional with Company details)
    internships_sql = """
        SELECT i.Internship_ID, i.Internship_No, i.Internship_Type, i.Role,
               i.Stipend, i.Start_Date, i.End_Date, i.Credits,
               i.Report_Semester, i.Report_Grade, i.Report_Link, i.Certificate_Link,
               c.Company_ID, c.Company_Name, c.Company_Type,
               ir.Required_Result_Semester,
               sr.SGPA AS Prerequisite_Semester_SGPA
        FROM INTERNSHIP i
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        LEFT JOIN INTERNSHIP_REQUIREMENT ir ON i.Requirement_ID = ir.Requirement_ID
        LEFT JOIN SEMESTER_RESULT sr ON i.Student_ID = sr.Student_ID 
                                    AND ir.Required_Result_Semester = sr.Semester
        WHERE i.Student_ID = %s
        ORDER BY i.Internship_No ASC
    """
    internships = execute_query(internships_sql, (student_id,))
    for it in internships:
        it["Stipend"] = float(it["Stipend"])
        if it.get("Prerequisite_Semester_SGPA") is not None:
            it["Prerequisite_Semester_SGPA"] = float(it["Prerequisite_Semester_SGPA"])
        try:
            from services.internship_service import calculate_internship_duration, determine_internship_status
            dur = calculate_internship_duration(it.get("Start_Date"), it.get("End_Date"))
            it["Duration_Str"] = dur["duration_str"]
            it["Status"] = determine_internship_status(it.get("Start_Date"), it.get("End_Date"), it.get("Report_Link"), it.get("Report_Grade"), it.get("Certificate_Link"))
        except Exception:
            it["Duration_Str"] = "N/A"
            it["Status"] = "Completed"
    student["Internships"] = internships
    student["Internship_Count"] = len(internships)

    # Placement Summary & Career Status Classification
    accepted_or_joined = [p for p in placements if p["Offer_Status"] in ("Accepted", "Joined")]
    if accepted_or_joined:
        student["Placement_Status"] = "Placed"
        student["Placed_Company"] = accepted_or_joined[0]["Company_Name"]
        student["Placed_Package"] = accepted_or_joined[0]["Package"]
    elif len(placements) >= 2:
        student["Placement_Status"] = "Multiple Offers"
        student["Placed_Company"] = None
        student["Placed_Package"] = None
    elif len(placements) == 1:
        student["Placement_Status"] = "Offered"
        student["Placed_Company"] = None
        student["Placed_Package"] = None
    else:
        student["Placement_Status"] = "Unplaced"
        student["Placed_Company"] = None
        student["Placed_Package"] = None

    # Relationship integrity safety check
    student["Is_Deletable"] = (len(placements) == 0 and len(internships) == 0)

    return student


def list_students(
    search: Optional[str] = None,
    branch: Optional[str] = None,
    batch_year: Optional[int] = None,
    min_cgpa: Optional[float] = None,
    max_cgpa: Optional[float] = None,
    max_backlogs: Optional[int] = None,
    placement_status: Optional[str] = None,
    sort_by: Optional[str] = "roll_no",
    sort_dir: Optional[str] = "asc",
    page: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    per_page: Optional[int] = None,
) -> Dict[str, Any]:
    """Searches and filters students with advanced criteria, server-side sorting, and pagination."""
    if per_page is not None:
        try:
            limit = int(per_page)
        except (ValueError, TypeError):
            pass

    where_clauses = ["1=1"]
    params: List[Any] = []

    # 1. Advanced Search across name, roll number, and email
    if search and str(search).strip():
        search_pattern = f"%{str(search).strip()}%"
        where_clauses.append(
            "("
            "s.Roll_No LIKE %s OR "
            "s.First_Name LIKE %s OR "
            "s.Last_Name LIKE %s OR "
            "s.Email LIKE %s OR "
            "CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) LIKE %s"
            ")"
        )
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern, search_pattern])

    # 2. Branch Filter
    if branch and str(branch).strip() and str(branch).strip().lower() not in ("all", "none"):
        where_clauses.append("s.Branch = %s")
        params.append(str(branch).strip())

    # 3. Batch Year Filter
    if batch_year is not None:
        try:
            by = int(batch_year)
            where_clauses.append("s.Batch_Year = %s")
            params.append(by)
        except (ValueError, TypeError):
            pass

    # 4. CGPA Range Filter
    if min_cgpa is not None:
        try:
            mc = float(min_cgpa)
            where_clauses.append("s.CGPA >= %s")
            params.append(mc)
        except (ValueError, TypeError):
            pass

    if max_cgpa is not None:
        try:
            xc = float(max_cgpa)
            where_clauses.append("s.CGPA <= %s")
            params.append(xc)
        except (ValueError, TypeError):
            pass

    # 5. Backlogs Filter
    if max_backlogs is not None:
        try:
            mb = int(max_backlogs)
            where_clauses.append("s.Backlogs <= %s")
            params.append(mb)
        except (ValueError, TypeError):
            pass

    # 6. Placement Status Filter (Placed, Unplaced, Multiple)
    if placement_status and str(placement_status).strip().lower() not in ("all", "none"):
        ps = str(placement_status).strip().lower()
        if ps in ("placed", "placed_only"):
            where_clauses.append(
                "EXISTS (SELECT 1 FROM PLACEMENT pl WHERE pl.Student_ID = s.Student_ID AND pl.Offer_Status IN ('Accepted', 'Joined'))"
            )
        elif ps in ("unplaced", "unplaced_only"):
            where_clauses.append(
                "NOT EXISTS (SELECT 1 FROM PLACEMENT pl WHERE pl.Student_ID = s.Student_ID)"
            )
        elif ps in ("multiple", "multiple_offers"):
            where_clauses.append(
                "(SELECT COUNT(*) FROM PLACEMENT pl WHERE pl.Student_ID = s.Student_ID) >= 2"
            )

    where_sql = " AND ".join(where_clauses)

    # 7. Total count query
    count_sql = f"SELECT COUNT(*) AS total FROM STUDENT s WHERE {where_sql}"
    count_res = execute_one(count_sql, tuple(params))
    total_count = int(count_res["total"] if count_res else 0)

    # 8. Safe sorting mapping
    SORT_MAP = {
        "roll_no": "s.Roll_No",
        "name": "s.First_Name, s.Last_Name",
        "first_name": "s.First_Name",
        "last_name": "s.Last_Name",
        "branch": "s.Branch",
        "batch_year": "s.Batch_Year",
        "batch": "s.Batch_Year",
        "cgpa": "s.CGPA",
        "backlogs": "s.Backlogs",
        "student_id": "s.Student_ID",
        "placement_offers": "Placement_Offers",
        "internships": "Internships",
    }
    sort_key = str(sort_by or "roll_no").strip().lower()
    order_col = SORT_MAP.get(sort_key, "s.Roll_No")
    order_dir = "DESC" if str(sort_dir).strip().lower() == "desc" else "ASC"

    # 9. Pagination offset calculation
    if page is not None and int(page) >= 1:
        offset = (int(page) - 1) * int(limit)

    query_sql = f"""
        SELECT 
            s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name,
            CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Full_Name,
            s.Branch, s.Batch_Year, s.Section, s.CGPA, s.Backlogs, s.Email, s.Resume_Link,
            GROUP_CONCAT(DISTINCT sp.Phone_No SEPARATOR ', ') AS Phone_Numbers,
            COUNT(DISTINCT p.Placement_ID) AS Placement_Offers,
            COUNT(DISTINCT CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN p.Placement_ID END) AS Accepted_Offers,
            MAX(CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN c.Company_Name END) AS Placed_Company,
            MAX(CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN p.Package END) AS Placed_Package,
            COUNT(DISTINCT i.Internship_ID) AS Internships
        FROM STUDENT s
        LEFT JOIN STUDENT_PHONE sp ON s.Student_ID = sp.Student_ID
        LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
        LEFT JOIN COMPANY c ON p.Company_ID = c.Company_ID
        LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
        WHERE {where_sql}
        GROUP BY s.Student_ID
        ORDER BY {order_col} {order_dir}
        LIMIT %s OFFSET %s
    """
    exec_params = list(params) + [int(limit), int(offset)]
    rows = execute_query(query_sql, tuple(exec_params))

    for r in rows:
        r["CGPA"] = float(r["CGPA"])
        r["Placed_Package"] = float(r["Placed_Package"]) if r.get("Placed_Package") is not None else None
        r["Phone_Numbers"] = [p.strip() for p in r["Phone_Numbers"].split(", ") if p.strip()] if r.get("Phone_Numbers") else []
        r["Is_Eligible"] = (r["Backlogs"] == 0 and r["CGPA"] >= 6.0)

        # Placement status label
        if r.get("Accepted_Offers", 0) > 0:
            r["Placement_Status"] = "Placed"
        elif r.get("Placement_Offers", 0) >= 2:
            r["Placement_Status"] = "Multiple Offers"
        elif r.get("Placement_Offers", 0) == 1:
            r["Placement_Status"] = "Offered"
        else:
            r["Placement_Status"] = "Unplaced"

    total_pages = math.ceil(total_count / limit) if limit > 0 else 1
    current_page = (offset // limit) + 1 if limit > 0 else 1

    pagination_meta = {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "page": current_page,
        "per_page": limit,
        "total_pages": total_pages,
        "has_prev": current_page > 1,
        "has_next": current_page < total_pages,
        "prev_page": current_page - 1 if current_page > 1 else None,
        "next_page": current_page + 1 if current_page < total_pages else None,
    }

    return {
        **pagination_meta,
        "pagination": pagination_meta,
        "sort_by": sort_key,
        "sort_dir": order_dir.lower(),
        "results": rows,
    }


def update_student(student_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Updates student profile fields, phones, and skills within an atomic transaction."""
    existing = execute_one("SELECT * FROM STUDENT WHERE Student_ID = %s", (student_id,))
    if not existing:
        raise NotFoundError(f"Student with ID {student_id} not found.")

    validate_student_payload(data, is_update=True)

    updatable_fields = [
        "Roll_No", "First_Name", "Last_Name", "Branch", "Batch_Year",
        "Section", "CGPA", "Backlogs", "Email", "Resume_Link"
    ]
    set_clauses = []
    params: List[Any] = []

    for field in updatable_fields:
        if field in data and data[field] is not None:
            val = data[field]
            if field in ("CGPA",):
                val = round(float(val), 2)
            elif field in ("Backlogs", "Batch_Year"):
                val = int(val)
            elif field == "Roll_No":
                val = str(val).strip().upper()
                if val != existing["Roll_No"]:
                    conflict = execute_one(
                        "SELECT Student_ID FROM STUDENT WHERE Roll_No = %s AND Student_ID != %s",
                        (val, student_id)
                    )
                    if conflict:
                        raise ConflictError(f"Roll_No '{val}' is already in use by another student.")
            elif field == "Email":
                val = str(val).strip().lower()
                if val != existing["Email"]:
                    conflict = execute_one(
                        "SELECT Student_ID FROM STUDENT WHERE Email = %s AND Student_ID != %s",
                        (val, student_id)
                    )
                    if conflict:
                        raise ConflictError(f"Email '{val}' is already in use by another student.")
            elif val is not None:
                val = str(val).strip()

            set_clauses.append(f"{field} = %s")
            params.append(val)

    # ATOMIC TRANSACTION: Update master student table + dependent multivalued attributes
    with get_cursor(commit=True) as cursor:
        if set_clauses:
            update_sql = f"UPDATE STUDENT SET {', '.join(set_clauses)} WHERE Student_ID = %s"
            params.append(student_id)
            cursor.execute(update_sql, tuple(params))

        # Synchronize phone numbers
        if "Phone_Numbers" in data and data["Phone_Numbers"] is not None:
            raw_phones = data["Phone_Numbers"]
            if isinstance(raw_phones, str):
                raw_phones = [p.strip() for p in raw_phones.split(",") if p.strip()]
            new_phones = [str(p).strip() for p in raw_phones if str(p).strip()]
            cursor.execute("DELETE FROM STUDENT_PHONE WHERE Student_ID = %s", (student_id,))
            if new_phones:
                phone_sql = "INSERT INTO STUDENT_PHONE (Student_ID, Phone_No) VALUES (%s, %s)"
                phone_tuples = [(student_id, p) for p in set(new_phones)]
                cursor.executemany(phone_sql, phone_tuples)

        # Synchronize technical skills
        if "Skills" in data and data["Skills"] is not None:
            raw_skills = data["Skills"]
            if isinstance(raw_skills, str):
                raw_skills = [s.strip() for s in raw_skills.split(",") if s.strip()]
            new_skills = [str(s).strip() for s in raw_skills if str(s).strip()]
            cursor.execute("DELETE FROM STUDENT_SKILL WHERE Student_ID = %s", (student_id,))
            if new_skills:
                skill_sql = "INSERT INTO STUDENT_SKILL (Student_ID, Skill) VALUES (%s, %s)"
                skill_tuples = [(student_id, s) for s in set(new_skills)]
                cursor.executemany(skill_sql, skill_tuples)

    logger.info("Successfully updated student ID %s", student_id)
    return get_student(student_id)


def delete_student(student_id: int) -> Dict[str, Any]:
    """Safely deletes a student record ONLY if no placement or internship records exist.
    
    BLOCKS deletion if the student has placement offers or internship history to ensure
    career reporting integrity and prevent destruction of institutional audit trails.
    Executes deletion inside a single database transaction.
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
    placement_count = int(history.get("placement_count") or 0)
    internship_count = int(history.get("internship_count") or 0)

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

    # ATOMIC TRANSACTION: Safely delete student (cascading dependent tables)
    with get_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM STUDENT WHERE Student_ID = %s", (student_id,))

    logger.info("Safely deleted student ID %s (%s)", student_id, student["Roll_No"])
    return {
        "success": True,
        "message": f"Student {student['Roll_No']} ({student['First_Name']} {student.get('Last_Name') or ''}) safely deleted.",
        "deleted_student_id": student_id,
    }

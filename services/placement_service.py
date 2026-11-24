import logging
import math
from typing import Dict, Any, List, Optional, Tuple
from config import Config
from db.connection import get_cursor, execute_one, execute_query
from services.exceptions import ValidationError, NotFoundError, ConflictError

logger = logging.getLogger(__name__)

VALID_OFFER_STATUSES = ("Offered", "Accepted", "Declined")
VALID_PLACEMENT_TYPES = ("On-campus", "Off-campus", "Pooled")
VALID_BOOLEAN_STRINGS = ("Yes", "No")


def validate_placement_payload(data: Dict[str, Any], is_update: bool = False) -> None:
    """Validates placement offer fields, allowed statuses, and business integrity rules."""
    if not is_update:
        required = ["Student_ID", "Company_ID", "Role", "Package", "Placement_Year"]
        for field in required:
            if field not in data or data[field] is None:
                raise ValidationError(f"Missing required field: '{field}'")

    if "Role" in data and data["Role"] is not None:
        role = str(data["Role"]).strip()
        if not role or len(role) < 2 or len(role) > 100:
            raise ValidationError("Role designation must be between 2 and 100 characters in length.")

    if "Package" in data and data["Package"] is not None:
        try:
            pkg = float(data["Package"])
            if pkg <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Package must be a positive decimal number (> 0 LPA)")

    if "Placement_Year" in data and data["Placement_Year"] is not None:
        try:
            year = int(data["Placement_Year"])
            if not (2000 <= year <= 2100):
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError("Placement_Year must be an integer between 2000 and 2100")

    if "Offer_Status" in data and data["Offer_Status"] is not None:
        status = str(data["Offer_Status"]).strip()
        if status not in VALID_OFFER_STATUSES:
            raise ValidationError(f"Offer_Status must be one of: {', '.join(VALID_OFFER_STATUSES)}")

    if "Placement_Type" in data and data["Placement_Type"] is not None:
        ptype = str(data["Placement_Type"]).strip()
        if ptype not in VALID_PLACEMENT_TYPES:
            raise ValidationError(
                f"Placement_Type must be one of: {', '.join(VALID_PLACEMENT_TYPES)}"
            )

    if "Is_PPO" in data and data["Is_PPO"] is not None:
        ppo = str(data["Is_PPO"]).strip()
        if ppo not in VALID_BOOLEAN_STRINGS:
            raise ValidationError("Is_PPO must be 'Yes' or 'No'")

    if "Joined" in data and data["Joined"] is not None:
        joined = str(data["Joined"]).strip()
        if joined not in VALID_BOOLEAN_STRINGS:
            raise ValidationError("Joined must be 'Yes' or 'No'")

    # Enforce CHECK constraint logic: Joined = 'Yes' only allowed when Offer_Status = 'Accepted'
    status_val = str(data.get("Offer_Status") or "").strip()
    joined_val = str(data.get("Joined") or "").strip()
    if joined_val == "Yes" and status_val and status_val != "Accepted":
        raise ValidationError("Joined can only be 'Yes' if Offer_Status is 'Accepted'.")
    if status_val in ("Offered", "Declined") and joined_val == "Yes":
        raise ValidationError("A placement offer cannot be marked Joined='Yes' when Offer_Status is not 'Accepted'.")


def create_placement_offer(data: Dict[str, Any]) -> Dict[str, Any]:
    """Issues and records a placement offer, enforcing all business domain constraints.

    Business Rules Enforced:
    1. Joined can only be 'Yes' when Offer_Status = 'Accepted'.
    2. At most one Joined offer per student (uq_one_joined_offer).
    3. Evaluated skills are safely recorded in PLACEMENT_SKILL inside a transaction.
    """
    validate_placement_payload(data, is_update=False)

    student_id = int(data["Student_ID"])
    company_id = int(data["Company_ID"])
    role = str(data["Role"]).strip()
    package_lpa = round(float(data["Package"]), 2)
    placement_year = int(data["Placement_Year"])
    placement_type = str(data.get("Placement_Type", "On-campus") or "On-campus").strip()
    is_ppo = str(data.get("Is_PPO", "No") or "No").strip()
    offer_status = str(data.get("Offer_Status", "Offered") or "Offered").strip()
    joined = str(data.get("Joined", "No") or "No").strip()
    rounds = int(data.get("Interview_Rounds", 1) or 1)
    skills = [str(s).strip() for s in data.get("Skills", []) if str(s).strip()]

    # Integrity verification
    if joined == "Yes" and offer_status != "Accepted":
        raise ValidationError("Joined can only be 'Yes' if Offer_Status is 'Accepted'.")

    # 1. Verify Student Exists
    student = execute_one(
        "SELECT Student_ID, Roll_No, First_Name, Last_Name FROM STUDENT WHERE Student_ID = %s",
        (student_id,),
    )
    if not student:
        raise NotFoundError(f"Student with ID {student_id} does not exist.")

    # 2. Verify Company Exists
    company = execute_one(
        "SELECT Company_ID, Company_Name FROM COMPANY WHERE Company_ID = %s", (company_id,)
    )
    if not company:
        raise NotFoundError(f"Company with ID {company_id} does not exist.")

    # 3. Enforce at most ONE Joined offer per student (uq_one_joined_offer)
    if joined == "Yes":
        existing_joined = execute_one(
            """
            SELECT p.Placement_ID, p.Role, c.Company_Name
            FROM PLACEMENT p
            JOIN COMPANY c ON p.Company_ID = c.Company_ID
            WHERE p.Student_ID = %s AND p.Joined = 'Yes'
        """,
            (student_id,),
        )
        if existing_joined:
            raise ConflictError(
                f"Cannot join offer: Student {student['Roll_No']} already holds a joined offer "
                f"(Offer #{existing_joined['Placement_ID']} at {existing_joined['Company_Name']}). "
                "Institutional policy allows a student to join at most one offer."
            )

    insert_sql = """
        INSERT INTO PLACEMENT (
            Student_ID, Company_ID, Role, Package,
            Placement_Year, Placement_Type, Is_PPO, Joined, Offer_Status, Interview_Rounds
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            insert_sql,
            (
                student_id,
                company_id,
                role,
                package_lpa,
                placement_year,
                placement_type,
                is_ppo,
                joined,
                offer_status,
                rounds,
            ),
        )
        placement_id = cursor.lastrowid

        if skills:
            skill_insert = "INSERT INTO PLACEMENT_SKILL (Placement_ID, Skill) VALUES (%s, %s)"
            cursor.executemany(skill_insert, [(placement_id, s) for s in set(skills)])

    logger.info(
        "Issued placement offer ID %s to student %s at %s (%s LPA)",
        placement_id,
        student["Roll_No"],
        company["Company_Name"],
        package_lpa,
    )
    return get_placement_offer(placement_id)


def get_placement_offer(placement_id: int) -> Dict[str, Any]:
    """Retrieves full placement offer record with joined student, company, and evaluated skills."""
    sql = """
        SELECT p.Placement_ID, p.Student_ID, s.Roll_No, s.First_Name, s.Last_Name,
               CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Student_Name,
               s.Branch, s.Batch_Year, s.Section, s.CGPA, s.Backlogs, s.Email, s.Resume_Link,
               p.Company_ID, c.Company_Name, c.Company_Type, c.Industry, c.Location, c.Website,
               p.Role, p.Package, p.Placement_Year, p.Placement_Type, p.Is_PPO,
               p.Joined, p.Offer_Status, p.Interview_Rounds
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE p.Placement_ID = %s
    """
    offer = execute_one(sql, (placement_id,))
    if not offer:
        raise NotFoundError(f"Placement offer with ID {placement_id} not found.")

    offer["Package"] = float(offer["Package"])
    offer["CGPA"] = float(offer["CGPA"])

    skills_sql = "SELECT Skill FROM PLACEMENT_SKILL WHERE Placement_ID = %s ORDER BY Skill"
    skills = execute_query(skills_sql, (placement_id,))
    offer["Skills"] = [s["Skill"] for s in skills]

    # Compatibility attributes
    offer["Selection_Rounds"] = []
    offer["Eligible_Branches"] = []
    offer["Candidate_Eligibility_Met"] = offer["Backlogs"] == 0 and offer["CGPA"] >= 6.0
    offer["Eligibility_Notes"] = []

    return offer


def list_placement_offers(
    student_id: Optional[int] = None,
    company_id: Optional[int] = None,
    placement_year: Optional[int] = None,
    batch_year: Optional[int] = None,
    branch: Optional[str] = None,
    offer_status: Optional[str] = None,
    placement_type: Optional[str] = None,
    is_ppo: Optional[str] = None,
    joined: Optional[str] = None,
    min_package: Optional[float] = None,
    max_package: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "package",
    sort_dir: Optional[str] = "desc",
    page: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    per_page: Optional[int] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Lists, searches, and filters placement offers with advanced criteria, safe sorting, and server-side pagination."""
    if per_page is not None:
        try:
            limit = int(per_page)
        except (ValueError, TypeError):
            pass

    where_clauses = ["1=1"]
    params: List[Any] = []

    if student_id is not None:
        where_clauses.append("p.Student_ID = %s")
        params.append(int(student_id))

    if company_id is not None:
        where_clauses.append("p.Company_ID = %s")
        params.append(int(company_id))

    if placement_year is not None:
        try:
            py = int(placement_year)
            where_clauses.append("p.Placement_Year = %s")
            params.append(py)
        except (ValueError, TypeError):
            pass

    if batch_year is not None:
        try:
            by = int(batch_year)
            where_clauses.append("s.Batch_Year = %s")
            params.append(by)
        except (ValueError, TypeError):
            pass

    if branch and str(branch).strip() and str(branch).strip().lower() not in ("all", "none"):
        where_clauses.append("s.Branch = %s")
        params.append(str(branch).strip())

    if (
        offer_status
        and str(offer_status).strip()
        and str(offer_status).strip().lower() not in ("all", "none")
    ):
        where_clauses.append("p.Offer_Status = %s")
        params.append(str(offer_status).strip())

    if (
        placement_type
        and str(placement_type).strip()
        and str(placement_type).strip().lower() not in ("all", "none")
    ):
        where_clauses.append("p.Placement_Type = %s")
        params.append(str(placement_type).strip())

    if is_ppo and str(is_ppo).strip() and str(is_ppo).strip().lower() not in ("all", "none"):
        where_clauses.append("p.Is_PPO = %s")
        params.append(str(is_ppo).strip())

    if joined and str(joined).strip() and str(joined).strip().lower() not in ("all", "none"):
        where_clauses.append("p.Joined = %s")
        params.append(str(joined).strip())

    if min_package is not None:
        try:
            min_p = float(min_package)
            where_clauses.append("p.Package >= %s")
            params.append(min_p)
        except (ValueError, TypeError):
            pass

    if max_package is not None:
        try:
            max_p = float(max_package)
            where_clauses.append("p.Package <= %s")
            params.append(max_p)
        except (ValueError, TypeError):
            pass

    if search and str(search).strip():
        search_pattern = f"%{str(search).strip()}%"
        where_clauses.append(
            "("
            "s.Roll_No LIKE %s OR "
            "s.First_Name LIKE %s OR "
            "s.Last_Name LIKE %s OR "
            "CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) LIKE %s OR "
            "c.Company_Name LIKE %s OR "
            "p.Role LIKE %s OR "
            "EXISTS (SELECT 1 FROM PLACEMENT_SKILL ps WHERE ps.Placement_ID = p.Placement_ID AND ps.Skill LIKE %s)"
            ")"
        )
        params.extend([search_pattern] * 7)

    where_sql = " AND ".join(where_clauses)

    count_sql = f"""
        SELECT COUNT(DISTINCT p.Placement_ID) AS total
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE {where_sql}
    """
    count_res = execute_one(count_sql, tuple(params))
    total_count = int(count_res["total"] if count_res else 0)

    SORT_MAP = {
        "package": "p.Package",
        "id": "p.Placement_ID",
        "placement_id": "p.Placement_ID",
        "roll_no": "s.Roll_No",
        "name": "s.First_Name, s.Last_Name",
        "student_name": "s.First_Name, s.Last_Name",
        "branch": "s.Branch",
        "company": "c.Company_Name",
        "company_name": "c.Company_Name",
        "role": "p.Role",
        "year": "p.Placement_Year",
        "placement_year": "p.Placement_Year",
        "batch_year": "s.Batch_Year",
        "status": "p.Offer_Status",
        "offer_status": "p.Offer_Status",
        "joined": "p.Joined",
        "is_ppo": "p.Is_PPO",
        "rounds": "p.Interview_Rounds",
    }
    sort_key = str(sort_by or "package").strip().lower()
    order_col = SORT_MAP.get(sort_key, "p.Package")
    order_dir = "ASC" if str(sort_dir).strip().lower() == "asc" else "DESC"

    if page is not None and int(page) >= 1:
        offset = (int(page) - 1) * int(limit)

    query_sql = f"""
        SELECT p.Placement_ID, p.Student_ID, s.Roll_No, s.First_Name, s.Last_Name,
               CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Student_Name,
               s.Branch, s.Batch_Year, s.CGPA, s.Backlogs, s.Email,
               p.Company_ID, c.Company_Name, c.Company_Type, c.Location, p.Role, p.Package,
               p.Placement_Year, p.Placement_Type, p.Is_PPO, p.Joined, p.Offer_Status, p.Interview_Rounds,
               GROUP_CONCAT(DISTINCT ps.Skill SEPARATOR ', ') AS Evaluated_Skills
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        LEFT JOIN PLACEMENT_SKILL ps ON p.Placement_ID = ps.Placement_ID
        WHERE {where_sql}
        GROUP BY p.Placement_ID
        ORDER BY {order_col} {order_dir}, p.Placement_ID DESC
        LIMIT %s OFFSET %s
    """
    exec_params = list(params) + [int(limit), int(offset)]
    rows = execute_query(query_sql, tuple(exec_params))

    for r in rows:
        r["Package"] = float(r["Package"])
        r["CGPA"] = float(r["CGPA"])
        r["Evaluated_Skills"] = (
            [s.strip() for s in r["Evaluated_Skills"].split(", ") if s.strip()]
            if r.get("Evaluated_Skills")
            else []
        )

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


def get_package_bracket_thresholds() -> Tuple[float, float, float]:
    """Returns centralized placement package reporting thresholds."""
    try:
        from flask import current_app, has_app_context

        if has_app_context() and current_app:
            t1 = float(
                current_app.config.get(
                    "PACKAGE_BRACKET_TIER_1_MAX", Config.PACKAGE_BRACKET_TIER_1_MAX
                )
            )
            t2 = float(
                current_app.config.get(
                    "PACKAGE_BRACKET_TIER_2_MAX", Config.PACKAGE_BRACKET_TIER_2_MAX
                )
            )
            t3 = float(
                current_app.config.get(
                    "PACKAGE_BRACKET_TIER_3_MAX", Config.PACKAGE_BRACKET_TIER_3_MAX
                )
            )
            return t1, t2, t3
    except Exception:
        pass
    return (
        Config.PACKAGE_BRACKET_TIER_1_MAX,
        Config.PACKAGE_BRACKET_TIER_2_MAX,
        Config.PACKAGE_BRACKET_TIER_3_MAX,
    )


def classify_package_tier(package: float) -> str:
    """Classifies a placement package (in LPA) into one of four reporting tiers."""
    t1, t2, t3 = get_package_bracket_thresholds()
    pkg = float(package)
    if pkg < t1:
        return "tier_below_6"
    elif pkg < t2:
        return "tier_6_to_10"
    elif pkg < t3:
        return "tier_10_to_15"
    else:
        return "tier_above_15"


def get_placement_package_statistics(
    placement_year: Optional[int] = None,
    batch_year: Optional[int] = None,
    branch: Optional[str] = None,
    company_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Calculates consolidated average, maximum, and minimum placement packages."""
    where_clauses = ["1=1"]
    params: List[Any] = []

    if placement_year is not None:
        try:
            where_clauses.append("p.Placement_Year = %s")
            params.append(int(placement_year))
        except (ValueError, TypeError):
            pass

    if batch_year is not None:
        try:
            where_clauses.append("s.Batch_Year = %s")
            params.append(int(batch_year))
        except (ValueError, TypeError):
            pass

    if branch and str(branch).strip() and str(branch).strip().lower() not in ("all", "none"):
        where_clauses.append("s.Branch = %s")
        params.append(str(branch).strip())

    if company_id is not None:
        try:
            where_clauses.append("p.Company_ID = %s")
            params.append(int(company_id))
        except (ValueError, TypeError):
            pass

    where_sql = " AND ".join(where_clauses)
    sql = f"""
        SELECT
            COUNT(p.Placement_ID) AS total_offers,
            ROUND(COALESCE(AVG(p.Package), 0), 2) AS avg_package,
            ROUND(COALESCE(MAX(p.Package), 0), 2) AS highest_package,
            ROUND(COALESCE(MIN(p.Package), 0), 2) AS lowest_package
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE {where_sql}
    """
    row = execute_one(sql, tuple(params)) or {}
    return {
        "total_offers": int(row.get("total_offers") or 0),
        "avg_package": float(row.get("avg_package") or 0.0),
        "highest_package": float(row.get("highest_package") or 0.0),
        "lowest_package": float(row.get("lowest_package") or 0.0),
    }


def get_placement_analytics(
    placement_year: Optional[int] = None,
    batch_year: Optional[int] = None,
    branch: Optional[str] = None,
    company_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Computes placement KPI metrics, company-wise statistics, branch-wise statistics,
    package distributions, and status distribution.
    Rule: 'Placed' means Joined = 'Yes'. 'Accepted Offers' tracks Offer_Status = 'Accepted'.
    """
    where_clauses = ["1=1"]
    params: List[Any] = []

    if placement_year is not None:
        try:
            where_clauses.append("p.Placement_Year = %s")
            params.append(int(placement_year))
        except (ValueError, TypeError):
            pass

    if batch_year is not None:
        try:
            where_clauses.append("s.Batch_Year = %s")
            params.append(int(batch_year))
        except (ValueError, TypeError):
            pass

    if branch and str(branch).strip() and str(branch).strip().lower() not in ("all", "none"):
        where_clauses.append("s.Branch = %s")
        params.append(str(branch).strip())

    if company_id is not None:
        try:
            where_clauses.append("p.Company_ID = %s")
            params.append(int(company_id))
        except (ValueError, TypeError):
            pass

    where_sql = " AND ".join(where_clauses)

    pkg_stats = get_placement_package_statistics(
        placement_year=placement_year,
        batch_year=batch_year,
        branch=branch,
        company_id=company_id,
    )

    kpi_sql = f"""
        SELECT 
            COUNT(p.Placement_ID) AS total_offers,
            COUNT(DISTINCT p.Student_ID) AS unique_students_offered,
            COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' THEN p.Student_ID END) AS placed_students,
            COUNT(CASE WHEN p.Offer_Status = 'Accepted' THEN 1 END) AS accepted_offers,
            COUNT(CASE WHEN p.Joined = 'Yes' THEN 1 END) AS joined_offers,
            COUNT(CASE WHEN p.Is_PPO = 'Yes' THEN 1 END) AS ppo_offers,
            COUNT(CASE WHEN p.Placement_Type = 'On-campus' THEN 1 END) AS on_campus_offers,
            COUNT(CASE WHEN p.Placement_Type = 'Off-campus' THEN 1 END) AS off_campus_offers
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE {where_sql}
    """
    kpi_raw = execute_one(kpi_sql, tuple(params)) or {}

    multi_sql = f"""
        SELECT COUNT(*) AS multi_count FROM (
            SELECT p.Student_ID
            FROM PLACEMENT p
            JOIN STUDENT s ON p.Student_ID = s.Student_ID
            JOIN COMPANY c ON p.Company_ID = c.Company_ID
            WHERE {where_sql}
            GROUP BY p.Student_ID
            HAVING COUNT(p.Placement_ID) >= 2
        ) AS multi_sub
    """
    multi_raw = execute_one(multi_sql, tuple(params)) or {}

    kpis = {
        "total_offers": int(kpi_raw.get("total_offers") or 0),
        "unique_students_offered": int(kpi_raw.get("unique_students_offered") or 0),
        "placed_students": int(kpi_raw.get("placed_students") or 0),
        "accepted_offers": int(kpi_raw.get("accepted_offers") or 0),
        "joined_students": int(kpi_raw.get("placed_students") or 0),
        "avg_package": pkg_stats["avg_package"],
        "highest_package": pkg_stats["highest_package"],
        "lowest_package": pkg_stats["lowest_package"],
        "multi_offer_students": int(multi_raw.get("multi_count") or 0),
        "ppo_offers": int(kpi_raw.get("ppo_offers") or 0),
        "on_campus_offers": int(kpi_raw.get("on_campus_offers") or 0),
        "off_campus_offers": int(kpi_raw.get("off_campus_offers") or 0),
    }

    comp_sql = f"""
        SELECT c.Company_ID, c.Company_Name, c.Company_Type, c.Industry,
               COUNT(p.Placement_ID) AS total_offers,
               COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' THEN p.Student_ID END) AS placed_count,
               COUNT(CASE WHEN p.Offer_Status = 'Accepted' THEN 1 END) AS accepted_count,
               ROUND(AVG(p.Package), 2) AS avg_package,
               ROUND(MAX(p.Package), 2) AS highest_package
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE {where_sql}
        GROUP BY c.Company_ID
        ORDER BY total_offers DESC, avg_package DESC
        LIMIT 10
    """
    comp_rows = execute_query(comp_sql, tuple(params))
    for cr in comp_rows:
        cr["avg_package"] = float(cr["avg_package"] or 0.0)
        cr["highest_package"] = float(cr["highest_package"] or 0.0)

    branch_sql = f"""
        SELECT s.Branch,
               COUNT(p.Placement_ID) AS total_offers,
               COUNT(DISTINCT p.Student_ID) AS unique_offered_students,
               COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' THEN p.Student_ID END) AS placed_students,
               COUNT(CASE WHEN p.Offer_Status = 'Accepted' THEN 1 END) AS accepted_offers,
               ROUND(AVG(p.Package), 2) AS avg_package,
               ROUND(MAX(p.Package), 2) AS highest_package
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE {where_sql}
        GROUP BY s.Branch
        ORDER BY placed_students DESC, avg_package DESC
    """
    branch_rows = execute_query(branch_sql, tuple(params))
    for br in branch_rows:
        br["avg_package"] = float(br["avg_package"] or 0.0)
        br["highest_package"] = float(br["highest_package"] or 0.0)

    t1, t2, t3 = get_package_bracket_thresholds()
    pkg_tier_sql = f"""
        SELECT 
            SUM(CASE WHEN p.Package < {t1} THEN 1 ELSE 0 END) AS tier_below_6,
            SUM(CASE WHEN p.Package >= {t1} AND p.Package < {t2} THEN 1 ELSE 0 END) AS tier_6_to_10,
            SUM(CASE WHEN p.Package >= {t2} AND p.Package < {t3} THEN 1 ELSE 0 END) AS tier_10_to_15,
            SUM(CASE WHEN p.Package >= {t3} THEN 1 ELSE 0 END) AS tier_above_15
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE {where_sql}
    """
    pt_raw = execute_one(pkg_tier_sql, tuple(params)) or {}
    package_distribution = {
        "tier_below_6": int(pt_raw.get("tier_below_6") or 0),
        "tier_6_to_10": int(pt_raw.get("tier_6_to_10") or 0),
        "tier_10_to_15": int(pt_raw.get("tier_10_to_15") or 0),
        "tier_above_15": int(pt_raw.get("tier_above_15") or 0),
    }

    status_sql = f"""
        SELECT p.Offer_Status, COUNT(*) AS count
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE {where_sql}
        GROUP BY p.Offer_Status
    """
    status_rows = execute_query(status_sql, tuple(params))
    status_distribution = {"Offered": 0, "Accepted": 0, "Declined": 0}
    for sr in status_rows:
        if sr["Offer_Status"] in status_distribution:
            status_distribution[sr["Offer_Status"]] = int(sr["count"] or 0)

    return {
        "kpis": kpis,
        "company_stats": comp_rows,
        "branch_stats": branch_rows,
        "package_distribution": package_distribution,
        "status_distribution": status_distribution,
    }


def update_offer_status(
    placement_id: int, new_status: str, joined: Optional[str] = None
) -> Dict[str, Any]:
    """Updates the status of an existing offer (Offered / Accepted / Declined).
    Enforces Rule: Joined can only be 'Yes' if Offer_Status is 'Accepted'.
    Enforces uq_one_joined_offer: at most one offer can have Joined = 'Yes'.
    """
    offer = get_placement_offer(placement_id)
    student_id = offer["Student_ID"]

    clean_status = str(new_status).strip()
    if clean_status not in VALID_OFFER_STATUSES:
        raise ValidationError(
            f"Invalid status: '{clean_status}'. Must be one of: {', '.join(VALID_OFFER_STATUSES)}"
        )

    # Determine joined value
    if clean_status in ("Offered", "Declined"):
        joined = "No"
    elif joined is None:
        joined = offer["Joined"]

    if joined == "Yes" and clean_status != "Accepted":
        raise ValidationError("Joined can only be 'Yes' when Offer_Status is 'Accepted'.")

    # If marking as Joined = 'Yes', check if student has any other joined offer
    if joined == "Yes":
        existing_joined = execute_one(
            """
            SELECT p.Placement_ID, p.Role, c.Company_Name
            FROM PLACEMENT p
            JOIN COMPANY c ON p.Company_ID = c.Company_ID
            WHERE p.Student_ID = %s 
              AND p.Joined = 'Yes'
              AND p.Placement_ID != %s
        """,
            (student_id, placement_id),
        )
        if existing_joined:
            raise ConflictError(
                f"Offer joining blocked: Student {offer['Roll_No']} already has joined offer "
                f"#{existing_joined['Placement_ID']} at {existing_joined['Company_Name']}. "
                "A student can join at most one offer."
            )

    update_sql = "UPDATE PLACEMENT SET Offer_Status = %s, Joined = %s WHERE Placement_ID = %s"
    with get_cursor(commit=True) as cursor:
        cursor.execute(update_sql, (clean_status, joined, placement_id))

    logger.info(
        "Updated placement offer #%s status from '%s' to '%s' (Joined: %s)",
        placement_id,
        offer["Offer_Status"],
        clean_status,
        joined,
    )
    return get_placement_offer(placement_id)


def update_placement_offer(placement_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Updates placement offer fields and synchronization of evaluated skills."""
    existing = get_placement_offer(placement_id)
    validate_placement_payload(data, is_update=True)

    updatable = [
        "Role",
        "Package",
        "Placement_Year",
        "Placement_Type",
        "Is_PPO",
        "Offer_Status",
        "Joined",
        "Interview_Rounds",
    ]
    set_clauses = []
    params: List[Any] = []

    new_status = data.get("Offer_Status", existing["Offer_Status"])
    new_joined = data.get("Joined", existing["Joined"])

    if new_joined == "Yes" and new_status != "Accepted":
        raise ValidationError("Joined can only be 'Yes' if Offer_Status is 'Accepted'.")

    if new_joined == "Yes" and existing["Joined"] != "Yes":
        student_id = existing["Student_ID"]
        existing_joined = execute_one(
            """
            SELECT p.Placement_ID, p.Role, c.Company_Name
            FROM PLACEMENT p
            JOIN COMPANY c ON p.Company_ID = c.Company_ID
            WHERE p.Student_ID = %s AND p.Joined = 'Yes' AND p.Placement_ID != %s
        """,
            (student_id, placement_id),
        )
        if existing_joined:
            raise ConflictError(
                f"Cannot mark joined: Student already holds joined offer #{existing_joined['Placement_ID']} at {existing_joined['Company_Name']}."
            )

    for field in updatable:
        if field in data and data[field] is not None:
            val = data[field]
            if field == "Package":
                val = round(float(val), 2)
            elif field in ("Placement_Year", "Interview_Rounds"):
                val = int(val)
            else:
                val = str(val).strip()
            set_clauses.append(f"{field} = %s")
            params.append(val)

    with get_cursor(commit=True) as cursor:
        if set_clauses:
            update_sql = f"UPDATE PLACEMENT SET {', '.join(set_clauses)} WHERE Placement_ID = %s"
            params.append(placement_id)
            cursor.execute(update_sql, tuple(params))

        if "Skills" in data and data["Skills"] is not None:
            cursor.execute("DELETE FROM PLACEMENT_SKILL WHERE Placement_ID = %s", (placement_id,))
            new_skills = [str(s).strip() for s in data["Skills"] if str(s).strip()]
            if new_skills:
                cursor.executemany(
                    "INSERT INTO PLACEMENT_SKILL (Placement_ID, Skill) VALUES (%s, %s)",
                    [(placement_id, s) for s in set(new_skills)],
                )

    logger.info("Updated placement offer ID %s", placement_id)
    return get_placement_offer(placement_id)


def delete_placement_offer(placement_id: int) -> Dict[str, Any]:
    """Deletes a placement offer record."""
    offer = execute_one(
        "SELECT Placement_ID, Student_ID, Role FROM PLACEMENT WHERE Placement_ID = %s",
        (placement_id,),
    )
    if not offer:
        raise NotFoundError(f"Placement offer with ID {placement_id} not found.")

    with get_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM PLACEMENT WHERE Placement_ID = %s", (placement_id,))

    logger.info("Deleted placement offer ID %s", placement_id)
    return {
        "success": True,
        "message": f"Placement offer ID {placement_id} ('{offer['Role']}') deleted successfully.",
        "deleted_placement_id": placement_id,
    }


def get_students_with_multiple_offers(min_offers: int = 2) -> List[Dict[str, Any]]:
    """Identifies and aggregates students who received multiple placement offers."""
    sql = """
        SELECT s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, s.CGPA,
               COUNT(p.Placement_ID) AS Total_Offers,
               MAX(p.Package) AS Highest_Package,
               MIN(p.Package) AS Lowest_Package,
               GROUP_CONCAT(CONCAT(c.Company_Name, ' (', p.Package, ' LPA - ', p.Offer_Status, ', Joined: ', p.Joined, ')') SEPARATOR '; ') AS Offers_Breakdown,
               MAX(CASE WHEN p.Joined = 'Yes' THEN c.Company_Name ELSE NULL END) AS Placed_Company,
               MAX(CASE WHEN p.Joined = 'Yes' THEN p.Package ELSE NULL END) AS Placed_Package,
               MAX(CASE WHEN p.Offer_Status = 'Accepted' THEN c.Company_Name ELSE NULL END) AS Accepted_Company,
               MAX(CASE WHEN p.Offer_Status = 'Accepted' THEN p.Package ELSE NULL END) AS Accepted_Package
        FROM STUDENT s
        JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        GROUP BY s.Student_ID
        HAVING COUNT(p.Placement_ID) >= %s
        ORDER BY Total_Offers DESC, Highest_Package DESC
    """
    rows = execute_query(sql, (int(min_offers),))
    for r in rows:
        r["CGPA"] = float(r["CGPA"])
        r["Highest_Package"] = float(r["Highest_Package"])
        r["Lowest_Package"] = float(r["Lowest_Package"])
        if r.get("Placed_Package") is not None:
            r["Placed_Package"] = float(r["Placed_Package"])
        if r.get("Accepted_Package") is not None:
            r["Accepted_Package"] = float(r["Accepted_Package"])
    return rows


def get_offer_distribution_summary() -> Dict[str, Any]:
    """Provides a breakdown of placement distribution: students with 0, 1, or multiple offers."""
    sql = """
        SELECT 
            SUM(CASE WHEN offer_count = 0 THEN 1 ELSE 0 END) AS zero_offers_count,
            SUM(CASE WHEN offer_count = 1 THEN 1 ELSE 0 END) AS single_offer_count,
            SUM(CASE WHEN offer_count >= 2 THEN 1 ELSE 0 END) AS multiple_offers_count,
            COUNT(*) AS total_students_evaluated
        FROM (
            SELECT s.Student_ID, COUNT(p.Placement_ID) AS offer_count
            FROM STUDENT s
            LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
            GROUP BY s.Student_ID
        ) AS student_offer_counts;
    """
    res = execute_one(sql)
    return {
        "zero_offers": int(res["zero_offers_count"] or 0),
        "single_offer": int(res["single_offer_count"] or 0),
        "multiple_offers": int(res["multiple_offers_count"] or 0),
        "total_students": int(res["total_students_evaluated"] or 0),
    }


def check_candidate_placement_eligibility(student_id: int) -> Dict[str, Any]:
    """Evaluates candidate placement eligibility based on student academic record (CGPA >= 6.0 and 0 backlogs)."""
    student = execute_one(
        "SELECT Student_ID, Roll_No, First_Name, Last_Name, Branch, CGPA, Backlogs FROM STUDENT WHERE Student_ID = %s",
        (student_id,),
    )
    if not student:
        raise NotFoundError(f"Student ID {student_id} not found.")

    student_cgpa = float(student["CGPA"])
    student_backlogs = int(student["Backlogs"])
    is_eligible = student_backlogs == 0 and student_cgpa >= 6.0

    return {
        "is_eligible": is_eligible,
        "student": {
            "Student_ID": student["Student_ID"],
            "Roll_No": student["Roll_No"],
            "Name": f"{student['First_Name']} {student.get('Last_Name') or ''}".strip(),
            "CGPA": student_cgpa,
            "Backlogs": student_backlogs,
            "Branch": student["Branch"],
        },
    }


def check_candidate_eligibility_for_opportunity(student_id: int, opportunity_id: Optional[int] = None) -> Dict[str, Any]:
    """Backward compatibility alias for check_candidate_placement_eligibility."""
    return check_candidate_placement_eligibility(student_id)

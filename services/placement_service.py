import logging
import math
from typing import Dict, Any, List, Optional, Tuple
from config import Config
from db.connection import get_cursor, execute_one, execute_query
from services.exceptions import ValidationError, NotFoundError, ConflictError

logger = logging.getLogger(__name__)

VALID_OFFER_STATUSES = ("Offered", "Accepted", "Joined", "Declined")
VALID_PLACEMENT_TYPES = ("On-campus", "Off-campus")
VALID_BOOLEAN_STRINGS = ("Yes", "No")


def validate_placement_payload(data: Dict[str, Any], is_update: bool = False) -> None:
    """Validates placement offer fields."""
    if not is_update:
        required = ["Student_ID", "Company_ID", "Package", "Placement_Year"]
        for field in required:
            if field not in data or data[field] is None:
                raise ValidationError(f"Missing required field: '{field}'")

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


def create_placement_offer(data: Dict[str, Any]) -> Dict[str, Any]:
    """Issues and records a placement offer, enforcing all business domain constraints.

    Business Rules Enforced:
    1. Opportunity must be of type 'Placement' (not 'Internship').
    2. No duplicate offer for the same opportunity to the same student.
    3. At most one 'Accepted' (or 'Joined') offer per student.
    4. Evaluated skills are safely recorded in PLACEMENT_SKILL inside a transaction.
    """
    validate_placement_payload(data, is_update=False)

    student_id = int(data["Student_ID"])
    company_id = int(data["Company_ID"])
    opp_id = int(data["Opportunity_ID"]) if data.get("Opportunity_ID") else None
    role = str(data.get("Role", "") or "").strip() or None
    package_lpa = round(float(data["Package"]), 2)
    placement_year = int(data["Placement_Year"])
    placement_type = str(data.get("Placement_Type", "On-campus") or "On-campus").strip()
    is_ppo = str(data.get("Is_PPO", "No") or "No").strip()
    offer_status = str(data.get("Offer_Status", "Offered") or "Offered").strip()
    joined = str(data.get("Joined", "No") or "No").strip()
    rounds = int(data.get("Interview_Rounds", 1) or 1)
    skills = [str(s).strip() for s in data.get("Skills", []) if str(s).strip()]

    # If joined is Yes, status must be Joined or Accepted
    if joined == "Yes" and offer_status not in ("Accepted", "Joined"):
        offer_status = "Joined"
    elif offer_status == "Joined":
        joined = "Yes"

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

    # 3. Rule 3: Check Opportunity is 'Placement' type
    if opp_id:
        opp = execute_one(
            "SELECT Opportunity_ID, Role, Opportunity_Type, Package_Stipend FROM OPPORTUNITY WHERE Opportunity_ID = %s",
            (opp_id,),
        )
        if not opp:
            raise NotFoundError(f"Opportunity with ID {opp_id} does not exist.")
        if opp["Opportunity_Type"] != "Placement":
            raise ValidationError(
                f"Invalid opportunity type: Opportunity ID {opp_id} ('{opp['Role']}') is of type '{opp['Opportunity_Type']}'. "
                "Placement offers can only be issued for opportunities of type 'Placement'."
            )
        if not role:
            role = opp["Role"]

    # 4. Rule 1: Enforce NO duplicate offer for the same opportunity
    if opp_id:
        duplicate_check = execute_one(
            "SELECT Placement_ID, Role, Offer_Status FROM PLACEMENT WHERE Student_ID = %s AND Opportunity_ID = %s",
            (student_id, opp_id),
        )
        if duplicate_check:
            raise ConflictError(
                f"Duplicate offer rejected: Student {student['Roll_No']} already holds placement offer #{duplicate_check['Placement_ID']} "
                f"for Opportunity ID {opp_id} ('{duplicate_check['Role']}' - Status: '{duplicate_check['Offer_Status']}')."
            )

    # 5. Rule 2: Enforce at most ONE Accepted/Joined offer per student
    if offer_status in ("Accepted", "Joined"):
        existing_accepted = execute_one(
            """
            SELECT p.Placement_ID, p.Role, p.Offer_Status, c.Company_Name
            FROM PLACEMENT p
            JOIN COMPANY c ON p.Company_ID = c.Company_ID
            WHERE p.Student_ID = %s AND p.Offer_Status IN ('Accepted', 'Joined')
        """,
            (student_id,),
        )
        if existing_accepted:
            raise ConflictError(
                f"Cannot accept offer: Student {student['Roll_No']} already holds an accepted offer "
                f"(Offer #{existing_accepted['Placement_ID']} at {existing_accepted['Company_Name']} - "
                f"Status: '{existing_accepted['Offer_Status']}'). "
                "Institutional placement policy allows at most ONE Accepted offer per student. "
                "Decline the existing accepted offer before accepting another."
            )

    # Insert into PLACEMENT and PLACEMENT_SKILL inside an atomic transaction
    insert_sql = """
        INSERT INTO PLACEMENT (
            Student_ID, Company_ID, Opportunity_ID, Role, Package,
            Placement_Year, Placement_Type, Is_PPO, Joined, Offer_Status, Interview_Rounds
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            insert_sql,
            (
                student_id,
                company_id,
                opp_id,
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
    """Retrieves full placement offer record with joined student, company, opportunity, drive, and eligibility metadata."""
    sql = """
        SELECT p.Placement_ID, p.Student_ID, s.Roll_No, s.First_Name, s.Last_Name,
               CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Student_Name,
               s.Branch, s.Batch_Year, s.Section, s.CGPA, s.Backlogs, s.Email, s.Resume_Link,
               p.Company_ID, c.Company_Name, c.Company_Type, c.Industry, c.Location, c.Website,
               p.Opportunity_ID, o.Role AS Opportunity_Role, o.Package_Stipend AS Drive_Package,
               o.Opportunity_Type, o.Duration_Months,
               rd.Drive_ID, rd.Drive_Year, rd.Drive_Type, rd.Season, rd.Drive_Date,
               e.Eligibility_ID, e.Minimum_CGPA, e.Max_Backlogs, e.Other_Criteria, e.Eligible_Branch,
               p.Role, p.Package, p.Placement_Year, p.Placement_Type, p.Is_PPO,
               p.Joined, p.Offer_Status, p.Interview_Rounds
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        LEFT JOIN OPPORTUNITY o ON p.Opportunity_ID = o.Opportunity_ID
        LEFT JOIN RECRUITMENT_DRIVE rd ON o.Drive_ID = rd.Drive_ID
        LEFT JOIN ELIGIBILITY e ON o.Opportunity_ID = e.Opportunity_ID
        WHERE p.Placement_ID = %s
    """
    offer = execute_one(sql, (placement_id,))
    if not offer:
        raise NotFoundError(f"Placement offer with ID {placement_id} not found.")

    offer["Package"] = float(offer["Package"])
    offer["CGPA"] = float(offer["CGPA"])
    if offer.get("Drive_Package") is not None:
        offer["Drive_Package"] = float(offer["Drive_Package"])
    if offer.get("Minimum_CGPA") is not None:
        offer["Minimum_CGPA"] = float(offer["Minimum_CGPA"])

    # Fetch evaluated skills
    skills_sql = "SELECT Skill FROM PLACEMENT_SKILL WHERE Placement_ID = %s ORDER BY Skill"
    skills = execute_query(skills_sql, (placement_id,))
    offer["Skills"] = [s["Skill"] for s in skills]

    # Fetch selection rounds if linked to an opportunity
    if offer.get("Opportunity_ID"):
        rounds_sql = """
            SELECT Round_ID, Round_Number, Round_Type, Description
            FROM SELECTION_PROCESS
            WHERE Opportunity_ID = %s
            ORDER BY Round_Number ASC
        """
        offer["Selection_Rounds"] = execute_query(rounds_sql, (offer["Opportunity_ID"],))
    else:
        offer["Selection_Rounds"] = []

    # Fetch eligible branches list
    if offer.get("Eligibility_ID"):
        b_sql = "SELECT Branch FROM ELIGIBILITY_BRANCH WHERE Eligibility_ID = %s ORDER BY Branch"
        b_rows = execute_query(b_sql, (offer["Eligibility_ID"],))
        offer["Eligible_Branches"] = [b["Branch"] for b in b_rows]
    else:
        offer["Eligible_Branches"] = []

    # Candidate Opportunity Eligibility Compliance Summary
    is_eligible = True
    eligibility_notes = []
    if offer.get("Minimum_CGPA") is not None and offer["CGPA"] < offer["Minimum_CGPA"]:
        is_eligible = False
        eligibility_notes.append(
            f"CGPA ({offer['CGPA']:.2f}) is below minimum requirement ({offer['Minimum_CGPA']:.2f})"
        )
    if offer.get("Max_Backlogs") is not None and offer["Backlogs"] > offer["Max_Backlogs"]:
        is_eligible = False
        eligibility_notes.append(
            f"Active backlogs ({offer['Backlogs']}) exceed allowance ({offer['Max_Backlogs']})"
        )
    if offer.get("Eligible_Branches") and offer["Branch"] not in offer["Eligible_Branches"]:
        is_eligible = False
        eligibility_notes.append(
            f"Branch '{offer['Branch']}' is not in approved list ({', '.join(offer['Eligible_Branches'])})"
        )

    offer["Candidate_Eligibility_Met"] = is_eligible
    offer["Eligibility_Notes"] = eligibility_notes

    return offer


def list_placement_offers(
    student_id: Optional[int] = None,
    company_id: Optional[int] = None,
    opportunity_id: Optional[int] = None,
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

    if opportunity_id is not None:
        where_clauses.append("p.Opportunity_ID = %s")
        params.append(int(opportunity_id))

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
        params.extend(
            [
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern,
            ]
        )

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
               p.Company_ID, c.Company_Name, c.Company_Type, c.Location, p.Opportunity_ID, p.Role, p.Package,
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
    """Returns centralized placement package reporting thresholds (tier 1, tier 2, tier 3 max in LPA)."""
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
    """Classifies a placement package (in LPA) into one of four reporting tiers.

    Preserves exact existing reporting bands and boundary behavior:
    - package < 6.0: tier_below_6
    - 6.0 <= package < 10.0: tier_6_to_10
    - 10.0 <= package < 15.0: tier_10_to_15
    - package >= 15.0: tier_above_15
    """
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
    """Calculates consolidated average, maximum, and minimum placement packages.

    Applies optional placement_year, batch_year, branch, and company_id filters.
    Preserves exact database semantics: COALESCE(..., 0) and ROUND(..., 2).
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
    """Computes placement KPI metrics, company-wise statistics, branch-wise statistics, package distributions, and status distribution."""
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

    # 1. Overall KPIs & Consolidated Package Statistics
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
            COUNT(DISTINCT CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN p.Student_ID END) AS placed_students,
            COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' OR p.Offer_Status = 'Joined' THEN p.Student_ID END) AS joined_students,
            COUNT(CASE WHEN p.Is_PPO = 'Yes' THEN 1 END) AS ppo_offers,
            COUNT(CASE WHEN p.Placement_Type = 'On-campus' THEN 1 END) AS on_campus_offers,
            COUNT(CASE WHEN p.Placement_Type = 'Off-campus' THEN 1 END) AS off_campus_offers
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE {where_sql}
    """
    kpi_raw = execute_one(kpi_sql, tuple(params)) or {}

    # Multiple offers count
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
        "joined_students": int(kpi_raw.get("joined_students") or 0),
        "avg_package": pkg_stats["avg_package"],
        "highest_package": pkg_stats["highest_package"],
        "lowest_package": pkg_stats["lowest_package"],
        "multi_offer_students": int(multi_raw.get("multi_count") or 0),
        "ppo_offers": int(kpi_raw.get("ppo_offers") or 0),
        "on_campus_offers": int(kpi_raw.get("on_campus_offers") or 0),
        "off_campus_offers": int(kpi_raw.get("off_campus_offers") or 0),
    }

    # 2. Company-wise placement statistics
    comp_sql = f"""
        SELECT c.Company_ID, c.Company_Name, c.Company_Type, c.Industry,
               COUNT(p.Placement_ID) AS total_offers,
               COUNT(DISTINCT CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN p.Student_ID END) AS placed_count,
               COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' OR p.Offer_Status = 'Joined' THEN p.Student_ID END) AS joined_count,
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

    # 3. Branch-wise placement statistics
    branch_sql = f"""
        SELECT s.Branch,
               COUNT(p.Placement_ID) AS total_offers,
               COUNT(DISTINCT p.Student_ID) AS unique_offered_students,
               COUNT(DISTINCT CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN p.Student_ID END) AS placed_students,
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

    # 4. Package distribution tiers
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

    # 5. Status distribution
    status_sql = f"""
        SELECT p.Offer_Status, COUNT(*) AS count
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE {where_sql}
        GROUP BY p.Offer_Status
    """
    status_rows = execute_query(status_sql, tuple(params))
    status_distribution = {"Offered": 0, "Accepted": 0, "Joined": 0, "Declined": 0}
    for sr in status_rows:
        status_distribution[sr["Offer_Status"]] = int(sr["count"] or 0)

    return {
        "kpis": kpis,
        "company_stats": comp_rows,
        "branch_stats": branch_rows,
        "package_distribution": package_distribution,
        "status_distribution": status_distribution,
    }


def check_candidate_eligibility_for_opportunity(
    student_id: int, opportunity_id: int
) -> Dict[str, Any]:
    """Evaluates whether a candidate meets the eligibility criteria of a placement opportunity."""
    student = execute_one(
        "SELECT Student_ID, Roll_No, First_Name, Last_Name, Branch, CGPA, Backlogs FROM STUDENT WHERE Student_ID = %s",
        (student_id,),
    )
    if not student:
        raise NotFoundError(f"Student ID {student_id} not found.")

    opp = execute_one(
        """
        SELECT o.Opportunity_ID, o.Role, o.Package_Stipend,
               e.Eligibility_ID, e.Minimum_CGPA, e.Max_Backlogs, e.Eligible_Branch, e.Other_Criteria
        FROM OPPORTUNITY o
        LEFT JOIN ELIGIBILITY e ON o.Opportunity_ID = e.Opportunity_ID
        WHERE o.Opportunity_ID = %s
    """,
        (opportunity_id,),
    )
    if not opp:
        raise NotFoundError(f"Opportunity ID {opportunity_id} not found.")

    student_cgpa = float(student["CGPA"])
    student_backlogs = int(student["Backlogs"])
    student_branch = student["Branch"]

    eligible_branches = []
    if opp.get("Eligibility_ID"):
        b_rows = execute_query(
            "SELECT Branch FROM ELIGIBILITY_BRANCH WHERE Eligibility_ID = %s ORDER BY Branch",
            (opp["Eligibility_ID"],),
        )
        eligible_branches = [b["Branch"] for b in b_rows]

    min_cgpa = float(opp["Minimum_CGPA"]) if opp.get("Minimum_CGPA") is not None else 0.0
    max_backlogs = int(opp["Max_Backlogs"]) if opp.get("Max_Backlogs") is not None else 99

    violations = []
    if student_cgpa < min_cgpa:
        violations.append(f"CGPA ({student_cgpa:.2f}) is below minimum required ({min_cgpa:.2f})")
    if student_backlogs > max_backlogs:
        violations.append(
            f"Active backlogs ({student_backlogs}) exceed maximum allowed ({max_backlogs})"
        )
    if eligible_branches and student_branch not in eligible_branches:
        violations.append(
            f"Branch '{student_branch}' is not in approved list ({', '.join(eligible_branches)})"
        )

    return {
        "is_eligible": len(violations) == 0,
        "violations": violations,
        "student": {
            "Student_ID": student["Student_ID"],
            "Roll_No": student["Roll_No"],
            "Name": f"{student['First_Name']} {student.get('Last_Name') or ''}".strip(),
            "CGPA": student_cgpa,
            "Backlogs": student_backlogs,
            "Branch": student_branch,
        },
        "criteria": {
            "Minimum_CGPA": min_cgpa,
            "Max_Backlogs": max_backlogs,
            "Eligible_Branches": eligible_branches or [opp.get("Eligible_Branch", "All Branches")],
            "Other_Criteria": opp.get("Other_Criteria"),
        },
    }


def update_offer_status(
    placement_id: int, new_status: str, joined: Optional[str] = None
) -> Dict[str, Any]:
    """Updates the status of an existing offer (Offered -> Accepted / Declined / Joined).

    Enforces Rule 2: At most one Accepted or Joined offer per student across all applications.
    """
    offer = get_placement_offer(placement_id)
    student_id = offer["Student_ID"]

    clean_status = str(new_status).strip()
    if clean_status not in VALID_OFFER_STATUSES:
        raise ValidationError(
            f"Invalid status: '{clean_status}'. Must be one of: {', '.join(VALID_OFFER_STATUSES)}"
        )

    # Determine joined value
    if clean_status == "Joined":
        joined = "Yes"
    elif clean_status == "Declined":
        joined = "No"
    elif joined is None:
        joined = offer["Joined"]

    # Rule 2: If accepting this offer, verify student has NO OTHER accepted offer
    if clean_status in ("Accepted", "Joined"):
        existing_accepted = execute_one(
            """
            SELECT p.Placement_ID, p.Role, p.Offer_Status, c.Company_Name
            FROM PLACEMENT p
            JOIN COMPANY c ON p.Company_ID = c.Company_ID
            WHERE p.Student_ID = %s 
              AND p.Offer_Status IN ('Accepted', 'Joined')
              AND p.Placement_ID != %s
        """,
            (student_id, placement_id),
        )

        if existing_accepted:
            raise ConflictError(
                f"Offer acceptance blocked: Student {offer['Roll_No']} already has an accepted offer "
                f"(Offer #{existing_accepted['Placement_ID']} at {existing_accepted['Company_Name']} - "
                f"Status: '{existing_accepted['Offer_Status']}'). "
                f"The student must decline offer #{existing_accepted['Placement_ID']} before accepting offer #{placement_id}."
            )

    update_sql = "UPDATE PLACEMENT SET Offer_Status = %s, Joined = %s WHERE Placement_ID = %s"
    with get_cursor(commit=True) as cursor:
        cursor.execute(update_sql, (clean_status, joined, placement_id))

    logger.info(
        "Updated placement offer #%s status from '%s' to '%s'",
        placement_id,
        offer["Offer_Status"],
        clean_status,
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

    # Check Rule 2 if status or joined is changing to Accepted/Joined
    new_status = data.get("Offer_Status", existing["Offer_Status"])
    if new_status in ("Accepted", "Joined") and existing["Offer_Status"] not in (
        "Accepted",
        "Joined",
    ):
        student_id = existing["Student_ID"]
        existing_acc = execute_one(
            """
            SELECT p.Placement_ID, p.Role, p.Offer_Status, c.Company_Name
            FROM PLACEMENT p
            JOIN COMPANY c ON p.Company_ID = c.Company_ID
            WHERE p.Student_ID = %s AND p.Offer_Status IN ('Accepted', 'Joined') AND p.Placement_ID != %s
        """,
            (student_id, placement_id),
        )
        if existing_acc:
            raise ConflictError(
                f"Cannot accept offer: Student already holds accepted offer #{existing_acc['Placement_ID']} at {existing_acc['Company_Name']}."
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

        # Update skills if provided
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


# ==============================================================================
# Analytical Queries for Students with Several Offers
# ==============================================================================


def get_students_with_multiple_offers(min_offers: int = 2) -> List[Dict[str, Any]]:
    """Identifies and aggregates students who received multiple placement offers."""
    sql = """
        SELECT s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, s.CGPA,
               COUNT(p.Placement_ID) AS Total_Offers,
               MAX(p.Package) AS Highest_Package,
               MIN(p.Package) AS Lowest_Package,
               GROUP_CONCAT(CONCAT(c.Company_Name, ' (', p.Package, ' LPA - ', p.Offer_Status, ')') SEPARATOR '; ') AS Offers_Breakdown,
               MAX(CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN c.Company_Name ELSE NULL END) AS Accepted_Company,
               MAX(CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN p.Package ELSE NULL END) AS Accepted_Package
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

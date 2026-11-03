import logging
from typing import Dict, Any, List, Optional
from db.connection import execute_one, execute_query

logger = logging.getLogger(__name__)


def _extract_clean_filters(filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Helper to extract and validate filter parameters."""
    if not filters:
        return {}
    clean: Dict[str, Any] = {}
    
    branch = filters.get("branch")
    if branch and str(branch).strip() and str(branch).strip().lower() not in ("all", "none"):
        clean["branch"] = str(branch).strip()
        
    batch_year = filters.get("batch_year")
    if batch_year and str(batch_year).strip() and str(batch_year).strip().lower() not in ("all", "none"):
        try:
            clean["batch_year"] = int(batch_year)
        except (ValueError, TypeError):
            pass

    placement_year = filters.get("placement_year")
    if placement_year and str(placement_year).strip() and str(placement_year).strip().lower() not in ("all", "none"):
        try:
            clean["placement_year"] = int(placement_year)
        except (ValueError, TypeError):
            pass

    return clean


def get_dashboard_filter_options() -> Dict[str, List[Any]]:
    """Retrieves available distinct filter options directly from MySQL for dynamic dropdowns."""
    try:
        branches_raw = execute_query(
            "SELECT DISTINCT Branch FROM STUDENT WHERE Branch IS NOT NULL AND Branch != '' ORDER BY Branch ASC"
        )
        batch_raw = execute_query(
            "SELECT DISTINCT Batch_Year FROM STUDENT WHERE Batch_Year IS NOT NULL ORDER BY Batch_Year DESC"
        )
        placement_raw = execute_query(
            "SELECT DISTINCT Placement_Year FROM PLACEMENT WHERE Placement_Year IS NOT NULL ORDER BY Placement_Year DESC"
        )

        return {
            "branches": [r["Branch"] for r in branches_raw if r.get("Branch")],
            "batch_years": [int(r["Batch_Year"]) for r in batch_raw if r.get("Batch_Year")],
            "placement_years": [int(r["Placement_Year"]) for r in placement_raw if r.get("Placement_Year")],
        }
    except Exception as exc:
        logger.error("Error fetching dashboard filter options: %s", exc)
        return {"branches": ["CSE", "ECE", "IT", "ME"], "batch_years": [2025, 2024, 2023, 2022], "placement_years": [2025, 2024, 2023, 2022]}


def get_dashboard_stats(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Aggregates enterprise university placement KPI metrics for the executive dashboard cards.
    
    Calculates the 8 core KPIs:
    1. Total Students
    2. Eligible Students (0 Backlogs and qualifying CGPA >= 6.0)
    3. Total Participating Companies
    4. Active Recruitment Drives
    5. Total Placement Offers
    6. Successfully Placed Students
    7. Average Package (LPA)
    8. Highest Package (LPA)
    
    Also preserves legacy dictionary keys ('students', 'companies', 'placements', 'internships')
    to prevent breaking existing tests and routes.
    """
    clean_filters = _extract_clean_filters(filters)
    branch = clean_filters.get("branch")
    batch_year = clean_filters.get("batch_year")
    placement_year = clean_filters.get("placement_year")

    # 1. Student Master Statistics
    s_conds, s_params = ["1=1"], []
    if branch:
        s_conds.append("s.Branch = %s")
        s_params.append(branch)
    if batch_year:
        s_conds.append("s.Batch_Year = %s")
        s_params.append(batch_year)
    elif placement_year:
        # Batch year naturally aligns with placement graduation year in curriculum
        s_conds.append("s.Batch_Year = %s")
        s_params.append(placement_year)

    s_clause = " AND ".join(s_conds)
    student_stats = execute_one(f"""
        SELECT 
            COUNT(*) AS total_students,
            COUNT(*) AS active_students,
            COUNT(CASE WHEN s.Backlogs = 0 AND s.CGPA >= 6.00 THEN 1 END) AS eligible_students,
            ROUND(COALESCE(AVG(s.CGPA), 0), 2) AS avg_cgpa
        FROM STUDENT s
        WHERE {s_clause}
    """, tuple(s_params)) or {}

    total_students = int(student_stats.get("total_students") or 0)
    total_active = int(student_stats.get("active_students") or 0)
    eligible_students = int(student_stats.get("eligible_students") or 0)
    avg_cgpa = float(student_stats.get("avg_cgpa") or 0.0)

    # 2. Placement Offers Statistics
    p_conds, p_params = ["1=1"], []
    if placement_year:
        p_conds.append("p.Placement_Year = %s")
        p_params.append(placement_year)
    if branch:
        p_conds.append("s.Branch = %s")
        p_params.append(branch)
    if batch_year:
        p_conds.append("s.Batch_Year = %s")
        p_params.append(batch_year)

    p_clause = " AND ".join(p_conds)
    placement_stats = execute_one(f"""
        SELECT 
            COUNT(p.Placement_ID) AS total_offers,
            COUNT(DISTINCT p.Student_ID) AS distinct_students_offered,
            COUNT(DISTINCT CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN p.Student_ID END) AS placed_students,
            SUM(CASE WHEN p.Offer_Status = 'Accepted' THEN 1 ELSE 0 END) AS accepted_offers,
            SUM(CASE WHEN p.Offer_Status = 'Joined' THEN 1 ELSE 0 END) AS joined_offers,
            ROUND(COALESCE(AVG(p.Package), 0), 2) AS avg_package,
            ROUND(COALESCE(MAX(p.Package), 0), 2) AS highest_package,
            ROUND(COALESCE(MIN(p.Package), 0), 2) AS lowest_package,
            COUNT(DISTINCT p.Company_ID) AS companies_with_offers
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        WHERE {p_clause}
    """, tuple(p_params)) or {}

    total_offers = int(placement_stats.get("total_offers") or 0)
    placed_students = int(placement_stats.get("placed_students") or 0)
    accepted_offers = int(placement_stats.get("accepted_offers") or 0)
    joined_offers = int(placement_stats.get("joined_offers") or 0)
    avg_package = float(placement_stats.get("avg_package") or 0.0)
    highest_package = float(placement_stats.get("highest_package") or 0.0)
    lowest_package = float(placement_stats.get("lowest_package") or 0.0)
    placement_rate = round((placed_students / total_students * 100), 1) if total_students > 0 else 0.0

    # 3. Companies Statistics
    if branch or batch_year or placement_year:
        total_companies = int(placement_stats.get("companies_with_offers") or 0)
    else:
        comp_res = execute_one("SELECT COUNT(*) AS total_companies FROM COMPANY") or {}
        total_companies = int(comp_res.get("total_companies") or 0)

    tier1_res = execute_one("SELECT SUM(CASE WHEN Company_Type = 'Product' THEN 1 ELSE 0 END) AS tier1_companies FROM COMPANY") or {}
    tier1_companies = int(tier1_res.get("tier1_companies") or 0)

    # 4. Recruitment Drives Statistics
    d_conds, d_params = ["1=1"], []
    target_year = placement_year or batch_year
    if target_year:
        d_conds.append("rd.Drive_Year = %s")
        d_params.append(target_year)
    d_clause = " AND ".join(d_conds)
    drive_res = execute_one(f"SELECT COUNT(*) AS active_drives FROM RECRUITMENT_DRIVE rd WHERE {d_clause}", tuple(d_params)) or {}
    active_drives = int(drive_res.get("active_drives") or 0)

    # 5. Internship Statistics
    i_conds, i_params = ["1=1"], []
    if branch:
        i_conds.append("s.Branch = %s")
        i_params.append(branch)
    if batch_year:
        i_conds.append("s.Batch_Year = %s")
        i_params.append(batch_year)
    elif placement_year:
        i_conds.append("s.Batch_Year = %s")
        i_params.append(placement_year)

    i_clause = " AND ".join(i_conds)
    internship_stats = execute_one(f"""
        SELECT 
            COUNT(i.Internship_ID) AS total_internships,
            SUM(CASE WHEN i.Internship_Type = 'Mandatory' THEN 1 ELSE 0 END) AS mandatory_internships,
            SUM(CASE WHEN i.Internship_Type = 'Additional' THEN 1 ELSE 0 END) AS additional_internships,
            COUNT(DISTINCT i.Student_ID) AS distinct_students_interned
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        WHERE {i_clause}
    """, tuple(i_params)) or {}

    total_internships = int(internship_stats.get("total_internships") or 0)
    mandatory_internships = int(internship_stats.get("mandatory_internships") or 0)
    additional_internships = int(internship_stats.get("additional_internships") or 0)
    distinct_students_interned = int(internship_stats.get("distinct_students_interned") or 0)

    # 6. Missing Mandatory Count
    missing_mandatory = execute_one(f"""
        SELECT COUNT(*) AS missing_count
        FROM (
            SELECT s.Student_ID
            FROM STUDENT s
            LEFT JOIN INTERNSHIP i1 ON s.Student_ID = i1.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = 'Mandatory'
            LEFT JOIN INTERNSHIP i2 ON s.Student_ID = i2.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = 'Mandatory'
            WHERE {s_clause} AND (i1.Internship_ID IS NULL OR i2.Internship_ID IS NULL)
        ) AS missing_students
    """, tuple(s_params)) or {}
    missing_count = int(missing_mandatory.get("missing_count") or 0)

    # Build Unified KPI Structure
    kpi_dict = {
        "total_students": total_students,
        "eligible_students": eligible_students,
        "total_companies": total_companies,
        "active_drives": active_drives,
        "total_offers": total_offers,
        "placed_students": placed_students,
        "average_package": avg_package,
        "avg_package": avg_package,
        "highest_package": highest_package,
        "placement_rate": placement_rate,
    }

    return {
        # Top-level KPI dictionary for direct access
        "kpi": kpi_dict,
        # Direct top-level accessors for convenient Jinja expressions
        "total_students": total_students,
        "eligible_students": eligible_students,
        "total_companies": total_companies,
        "active_drives": active_drives,
        "total_offers": total_offers,
        "placed_students": placed_students,
        "avg_package": avg_package,
        "highest_package": highest_package,
        "placement_rate": placement_rate,
        # Legacy preserved dictionaries
        "students": {
            "total": total_students,
            "active": total_active,
            "eligible": eligible_students,
            "avg_cgpa": avg_cgpa,
        },
        "companies": {
            "total": total_companies,
            "tier1": tier1_companies,
            "drives": active_drives,
            "opportunities": int(placement_stats.get("companies_with_offers") or 0),
        },
        "placements": {
            "total_offers": total_offers,
            "accepted_offers": accepted_offers,
            "joined_offers": joined_offers,
            "placed_students": placed_students,
            "placement_rate": placement_rate,
            "avg_package": avg_package,
            "highest_package": highest_package,
            "lowest_package": lowest_package,
        },
        "internships": {
            "total": total_internships,
            "mandatory": mandatory_internships,
            "additional": additional_internships,
            "distinct_students": distinct_students_interned,
            "missing_mandatory_count": missing_count,
        },
    }


def get_branchwise_analytics_chart_data(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Visualization 1: Branch-wise placement distribution.
    Compares registered student counts, eligible students, placed students, and average package by branch.
    """
    clean_filters = _extract_clean_filters(filters)
    batch_year = clean_filters.get("batch_year")
    placement_year = clean_filters.get("placement_year")
    branch = clean_filters.get("branch")

    s_conds, s_params = ["1=1"], []
    if branch:
        s_conds.append("s.Branch = %s")
        s_params.append(branch)
    if batch_year:
        s_conds.append("s.Batch_Year = %s")
        s_params.append(batch_year)
    elif placement_year:
        s_conds.append("s.Batch_Year = %s")
        s_params.append(placement_year)

    p_extra_join = ""
    if placement_year:
        p_extra_join = f" AND p.Placement_Year = {int(placement_year)}"

    s_clause = " AND ".join(s_conds)
    rows = execute_query(f"""
        SELECT 
            s.Branch,
            COUNT(DISTINCT s.Student_ID) AS student_count,
            COUNT(DISTINCT CASE WHEN s.Backlogs = 0 AND s.CGPA >= 6.00 THEN s.Student_ID END) AS eligible_students,
            COUNT(DISTINCT CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN s.Student_ID END) AS placed_students,
            COUNT(DISTINCT p.Placement_ID) AS offer_count,
            COUNT(DISTINCT i.Internship_ID) AS internship_count,
            ROUND(COALESCE(AVG(s.CGPA), 0), 2) AS avg_cgpa,
            ROUND(COALESCE(AVG(p.Package), 0), 2) AS avg_package
        FROM STUDENT s
        LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID {p_extra_join}
        LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
        WHERE {s_clause}
        GROUP BY s.Branch
        ORDER BY student_count DESC, s.Branch ASC
    """, tuple(s_params))

    labels = [r["Branch"] for r in rows]
    student_counts = [int(r["student_count"]) for r in rows]
    eligible_students = [int(r["eligible_students"]) for r in rows]
    placed_students = [int(r["placed_students"]) for r in rows]
    internship_counts = [int(r["internship_count"]) for r in rows]
    avg_packages = [float(r["avg_package"] or 0.0) for r in rows]
    
    placement_rates = []
    for sc, ps in zip(student_counts, placed_students):
        rate = round((ps / sc * 100), 1) if sc > 0 else 0.0
        placement_rates.append(rate)

    is_empty = len(rows) == 0 or all(sc == 0 for sc in student_counts)

    return {
        "labels": labels,
        "student_counts": student_counts,
        "eligible_students": eligible_students,
        "placed_students": placed_students,
        "internship_counts": internship_counts,
        "avg_packages": avg_packages,
        "placement_rates": placement_rates,
        "is_empty": is_empty,
    }


def get_yearwise_placement_chart_data(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Visualization 2: Year-wise placement trends.
    Progression of total offers, accepted placements, and average CTC package over academic years.
    """
    clean_filters = _extract_clean_filters(filters)
    branch = clean_filters.get("branch")
    batch_year = clean_filters.get("batch_year")

    conds, params = ["1=1"], []
    if branch:
        conds.append("s.Branch = %s")
        params.append(branch)
    if batch_year:
        conds.append("s.Batch_Year = %s")
        params.append(batch_year)

    clause = " AND ".join(conds)
    rows = execute_query(f"""
        SELECT 
            p.Placement_Year,
            COUNT(p.Placement_ID) AS offer_count,
            SUM(CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN 1 ELSE 0 END) AS accepted_count,
            ROUND(COALESCE(AVG(p.Package), 0), 2) AS avg_package,
            ROUND(COALESCE(MAX(p.Package), 0), 2) AS max_package
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        WHERE {clause}
        GROUP BY p.Placement_Year
        ORDER BY p.Placement_Year ASC
    """, tuple(params))

    labels = [str(r["Placement_Year"]) for r in rows]
    offer_counts = [int(r["offer_count"]) for r in rows]
    accepted_counts = [int(r["accepted_count"]) for r in rows]
    avg_packages = [float(r["avg_package"]) for r in rows]
    max_packages = [float(r["max_package"]) for r in rows]
    is_empty = len(rows) == 0 or all(oc == 0 for oc in offer_counts)

    return {
        "labels": labels,
        "offer_counts": offer_counts,
        "accepted_counts": accepted_counts,
        "avg_packages": avg_packages,
        "max_packages": max_packages,
        "is_empty": is_empty,
    }


def get_package_distribution_chart_data(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Visualization 3: CTC package distribution.
    Categorizes placement packages into enterprise brackets (< 8 LPA, 8 - 12 LPA, 12 - 16 LPA, 16+ LPA).
    """
    clean_filters = _extract_clean_filters(filters)
    branch = clean_filters.get("branch")
    batch_year = clean_filters.get("batch_year")
    placement_year = clean_filters.get("placement_year")

    conds, params = ["1=1"], []
    if branch:
        conds.append("s.Branch = %s")
        params.append(branch)
    if batch_year:
        conds.append("s.Batch_Year = %s")
        params.append(batch_year)
    if placement_year:
        conds.append("p.Placement_Year = %s")
        params.append(placement_year)

    clause = " AND ".join(conds)
    tiers = [
        {"key": "< 8 LPA", "label": "< 8 LPA (Core / Regular)", "min": 0, "max": 7.99},
        {"key": "8 - 12 LPA", "label": "8 - 12 LPA (Dream)", "min": 8.00, "max": 11.99},
        {"key": "12 - 16 LPA", "label": "12 - 16 LPA (Super Dream)", "min": 12.00, "max": 15.99},
        {"key": "16+ LPA", "label": "16+ LPA (Marquee / Elite)", "min": 16.00, "max": 999.00},
    ]

    tier_counts = {t["key"]: 0 for t in tiers}
    rows = execute_query(f"""
        SELECT p.Package
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        WHERE {clause}
    """, tuple(params))

    total = len(rows)
    for r in rows:
        pkg = float(r["Package"])
        if pkg < 8.0:
            tier_counts["< 8 LPA"] += 1
        elif pkg < 12.0:
            tier_counts["8 - 12 LPA"] += 1
        elif pkg < 16.0:
            tier_counts["12 - 16 LPA"] += 1
        else:
            tier_counts["16+ LPA"] += 1

    labels = [t["label"] for t in tiers]
    counts = [tier_counts[t["key"]] for t in tiers]
    percentages = [round((cnt / total * 100), 1) if total > 0 else 0.0 for cnt in counts]
    is_empty = total == 0

    return {
        "labels": labels,
        "counts": counts,
        "percentages": percentages,
        "total_offers": total,
        "is_empty": is_empty,
    }


def get_placement_vs_internship_chart_data(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Visualization 4: Placement versus internship statistics.
    Direct branch comparison between secured placement offers and completed internships.
    """
    clean_filters = _extract_clean_filters(filters)
    branch = clean_filters.get("branch")
    batch_year = clean_filters.get("batch_year")
    placement_year = clean_filters.get("placement_year")

    s_conds, s_params = ["1=1"], []
    if branch:
        s_conds.append("s.Branch = %s")
        s_params.append(branch)
    if batch_year:
        s_conds.append("s.Batch_Year = %s")
        s_params.append(batch_year)
    elif placement_year:
        s_conds.append("s.Batch_Year = %s")
        s_params.append(placement_year)

    p_extra_join = f" AND p.Placement_Year = {int(placement_year)}" if placement_year else ""

    s_clause = " AND ".join(s_conds)
    rows = execute_query(f"""
        SELECT 
            s.Branch,
            COUNT(DISTINCT p.Placement_ID) AS placement_offers,
            COUNT(DISTINCT i.Internship_ID) AS total_internships,
            COUNT(DISTINCT CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN s.Student_ID END) AS placed_students,
            COUNT(DISTINCT i.Student_ID) AS interned_students
        FROM STUDENT s
        LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID {p_extra_join}
        LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
        WHERE {s_clause}
        GROUP BY s.Branch
        ORDER BY s.Branch ASC
    """, tuple(s_params))

    labels = [r["Branch"] for r in rows]
    placement_offers = [int(r["placement_offers"]) for r in rows]
    total_internships = [int(r["total_internships"]) for r in rows]
    placed_students = [int(r["placed_students"]) for r in rows]
    interned_students = [int(r["interned_students"]) for r in rows]
    is_empty = len(rows) == 0 or (all(po == 0 for po in placement_offers) and all(ti == 0 for ti in total_internships))

    return {
        "labels": labels,
        "placement_offers": placement_offers,
        "total_internships": total_internships,
        "placed_students": placed_students,
        "interned_students": interned_students,
        "is_empty": is_empty,
    }


def get_internship_completion_chart_data(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Visualization 5: Internship completion percentage.
    Analyzes student curriculum degree compliance:
    - Fully Completed (Completed Both Mandatory #1 and #2)
    - Partially Completed (Completed 1 Mandatory internship)
    - Incomplete / Pending (0 Mandatory internships completed)
    """
    clean_filters = _extract_clean_filters(filters)
    branch = clean_filters.get("branch")
    batch_year = clean_filters.get("batch_year")
    placement_year = clean_filters.get("placement_year")

    s_conds, s_params = ["1=1"], []
    if branch:
        s_conds.append("s.Branch = %s")
        s_params.append(branch)
    if batch_year:
        s_conds.append("s.Batch_Year = %s")
        s_params.append(batch_year)
    elif placement_year:
        s_conds.append("s.Batch_Year = %s")
        s_params.append(placement_year)

    s_clause = " AND ".join(s_conds)
    rows = execute_query(f"""
        SELECT 
            status_category,
            COUNT(*) AS student_count
        FROM (
            SELECT 
                s.Student_ID,
                CASE 
                    WHEN COUNT(DISTINCT CASE WHEN i.Internship_Type = 'Mandatory' AND i.Internship_No = 1 THEN i.Internship_ID END) > 0
                     AND COUNT(DISTINCT CASE WHEN i.Internship_Type = 'Mandatory' AND i.Internship_No = 2 THEN i.Internship_ID END) > 0
                    THEN 'Fully Completed (Both)'
                    WHEN COUNT(DISTINCT CASE WHEN i.Internship_Type = 'Mandatory' AND i.Internship_No IN (1, 2) THEN i.Internship_ID END) > 0
                    THEN 'Partially Completed (1 of 2)'
                    ELSE 'Pending / Incomplete'
                END AS status_category
            FROM STUDENT s
            LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
            WHERE {s_clause}
            GROUP BY s.Student_ID
        ) AS student_compliance
        GROUP BY status_category
        ORDER BY FIELD(status_category, 'Fully Completed (Both)', 'Partially Completed (1 of 2)', 'Pending / Incomplete')
    """, tuple(s_params))

    # Standardize categories
    expected_categories = ["Fully Completed (Both)", "Partially Completed (1 of 2)", "Pending / Incomplete"]
    cat_map = {r["status_category"]: int(r["student_count"]) for r in rows}
    counts = [cat_map.get(cat, 0) for cat in expected_categories]
    total_students = sum(counts)
    
    fully_completed_count = counts[0]
    completion_rate = round((fully_completed_count / total_students * 100), 1) if total_students > 0 else 0.0
    is_empty = total_students == 0

    return {
        "labels": expected_categories,
        "counts": counts,
        "total_students": total_students,
        "completion_rate": completion_rate,
        "is_empty": is_empty,
    }


def get_multiple_offers_chart_data(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Visualization 6: Multiple-offer student statistics.
    Breakdown of students by placement outcome:
    - 0 Offers (Unplaced)
    - 1 Offer (Single)
    - 2 Offers (Dual)
    - 3+ Offers (Multiple)
    """
    clean_filters = _extract_clean_filters(filters)
    branch = clean_filters.get("branch")
    batch_year = clean_filters.get("batch_year")
    placement_year = clean_filters.get("placement_year")

    s_conds, s_params = ["1=1"], []
    if branch:
        s_conds.append("s.Branch = %s")
        s_params.append(branch)
    if batch_year:
        s_conds.append("s.Batch_Year = %s")
        s_params.append(batch_year)
    elif placement_year:
        s_conds.append("s.Batch_Year = %s")
        s_params.append(placement_year)

    p_extra_join = f" AND p.Placement_Year = {int(placement_year)}" if placement_year else ""

    s_clause = " AND ".join(s_conds)
    rows = execute_query(f"""
        SELECT 
            offer_tier,
            COUNT(*) AS student_count
        FROM (
            SELECT 
                s.Student_ID,
                CASE 
                    WHEN COUNT(p.Placement_ID) = 0 THEN '0 Offers (Unplaced)'
                    WHEN COUNT(p.Placement_ID) = 1 THEN '1 Offer (Single)'
                    WHEN COUNT(p.Placement_ID) = 2 THEN '2 Offers (Dual)'
                    ELSE '3+ Offers (Multiple)'
                END AS offer_tier
            FROM STUDENT s
            LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID {p_extra_join}
            WHERE {s_clause}
            GROUP BY s.Student_ID
        ) AS student_offers
        GROUP BY offer_tier
        ORDER BY FIELD(offer_tier, '0 Offers (Unplaced)', '1 Offer (Single)', '2 Offers (Dual)', '3+ Offers (Multiple)')
    """, tuple(s_params))

    expected_tiers = ["0 Offers (Unplaced)", "1 Offer (Single)", "2 Offers (Dual)", "3+ Offers (Multiple)"]
    tier_map = {r["offer_tier"]: int(r["student_count"]) for r in rows}
    counts = [tier_map.get(tier, 0) for tier in expected_tiers]
    total_students = sum(counts)
    multiple_offer_students = counts[2] + counts[3]
    is_empty = total_students == 0

    return {
        "labels": expected_tiers,
        "counts": counts,
        "total_students": total_students,
        "multiple_offer_students": multiple_offer_students,
        "is_empty": is_empty,
    }


def get_offer_status_chart_data(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Fetches breakdown of placement statuses (Offered, Accepted, Joined, Declined)."""
    clean_filters = _extract_clean_filters(filters)
    branch = clean_filters.get("branch")
    batch_year = clean_filters.get("batch_year")
    placement_year = clean_filters.get("placement_year")

    conds, params = ["1=1"], []
    if branch:
        conds.append("s.Branch = %s")
        params.append(branch)
    if batch_year:
        conds.append("s.Batch_Year = %s")
        params.append(batch_year)
    if placement_year:
        conds.append("p.Placement_Year = %s")
        params.append(placement_year)

    clause = " AND ".join(conds)
    rows = execute_query(f"""
        SELECT 
            p.Offer_Status,
            COUNT(*) AS count
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        WHERE {clause}
        GROUP BY p.Offer_Status
        ORDER BY FIELD(p.Offer_Status, 'Offered', 'Accepted', 'Joined', 'Declined')
    """, tuple(params))

    labels = [r["Offer_Status"] for r in rows]
    counts = [int(r["count"]) for r in rows]
    is_empty = len(rows) == 0

    return {
        "labels": labels,
        "counts": counts,
        "is_empty": is_empty,
    }


def get_internship_breakdown_chart_data(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Fetches breakdown of internships: Mandatory #1, Mandatory #2, Additional."""
    clean_filters = _extract_clean_filters(filters)
    branch = clean_filters.get("branch")
    batch_year = clean_filters.get("batch_year")
    placement_year = clean_filters.get("placement_year")

    conds, params = ["1=1"], []
    if branch:
        conds.append("s.Branch = %s")
        params.append(branch)
    if batch_year:
        conds.append("s.Batch_Year = %s")
        params.append(batch_year)
    elif placement_year:
        conds.append("s.Batch_Year = %s")
        params.append(placement_year)

    clause = " AND ".join(conds)
    rows = execute_query(f"""
        SELECT 
            CASE 
                WHEN i.Internship_Type = 'Mandatory' AND i.Internship_No = 1 THEN 'Mandatory #1 (Sem 3)'
                WHEN i.Internship_Type = 'Mandatory' AND i.Internship_No = 2 THEN 'Mandatory #2 (Sem 5)'
                ELSE 'Additional Internships'
            END AS category,
            COUNT(*) AS count
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        WHERE {clause}
        GROUP BY category
        ORDER BY category ASC
    """, tuple(params))

    labels = [r["category"] for r in rows]
    counts = [int(r["count"]) for r in rows]
    is_empty = len(rows) == 0

    return {
        "labels": labels,
        "counts": counts,
        "is_empty": is_empty,
    }


def get_comprehensive_dashboard_data(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Aggregates all 8 KPI cards, all 6 interactive charts, filter options, and recent offers.
    
    Serves as the primary enterprise data provider for both server-rendered views
    and dynamic asynchronous AJAX updates.
    """
    clean_filters = _extract_clean_filters(filters)
    stats = get_dashboard_stats(clean_filters)
    filter_options = get_dashboard_filter_options()

    chart_branchwise = get_branchwise_analytics_chart_data(clean_filters)
    chart_yearwise = get_yearwise_placement_chart_data(clean_filters)
    chart_package = get_package_distribution_chart_data(clean_filters)
    chart_vs = get_placement_vs_internship_chart_data(clean_filters)
    chart_completion = get_internship_completion_chart_data(clean_filters)
    chart_multiple = get_multiple_offers_chart_data(clean_filters)
    chart_status = get_offer_status_chart_data(clean_filters)
    chart_internships = get_internship_breakdown_chart_data(clean_filters)

    return {
        "stats": stats,
        "kpi": stats["kpi"],
        # Preserved aliases for legacy test suites
        "students": stats["students"],
        "placements": stats["placements"],
        "companies": stats["companies"],
        "internships": stats["internships"],
        "charts": {
            "branchwise": chart_branchwise,
            "yearwise": chart_yearwise,
            "package_distribution": chart_package,
            "placement_vs_internship": chart_vs,
            "internship_completion": chart_completion,
            "multiple_offers": chart_multiple,
            "offer_status": chart_status,
            "internships_breakdown": chart_internships,
        },
        "filter_options": filter_options,
        "active_filters": clean_filters,
    }


def get_comprehensive_report_data(filters: Dict[str, Any]) -> Dict[str, Any]:
    """Fetches a detailed, multi-dimensional report on students with placement and internship status."""
    conditions = ["1=1"]
    params: List[Any] = []

    if filters.get("branch"):
        conditions.append("s.Branch = %s")
        params.append(filters["branch"])

    if filters.get("min_cgpa"):
        try:
            min_cgpa = float(filters["min_cgpa"])
            conditions.append("s.CGPA >= %s")
            params.append(min_cgpa)
        except (ValueError, TypeError):
            pass

    where_clause = " AND ".join(conditions)

    sql = f"""
        SELECT 
            s.Student_ID,
            s.Roll_No,
            CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Full_Name,
            s.Email,
            s.Branch,
            s.Batch_Year,
            s.CGPA,
            COUNT(DISTINCT p.Placement_ID) AS Total_Offers,
            MAX(CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN c.Company_Name ELSE NULL END) AS Placed_Company,
            MAX(CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN p.Package ELSE NULL END) AS Placed_Package,
            MAX(CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN p.Offer_Status ELSE NULL END) AS Final_Status,
            COUNT(DISTINCT CASE WHEN i.Internship_Type = 'Mandatory' AND i.Internship_No = 1 THEN i.Internship_ID ELSE NULL END) AS Has_Mandatory_1,
            COUNT(DISTINCT CASE WHEN i.Internship_Type = 'Mandatory' AND i.Internship_No = 2 THEN i.Internship_ID ELSE NULL END) AS Has_Mandatory_2,
            COUNT(DISTINCT CASE WHEN i.Internship_Type = 'Additional' THEN i.Internship_ID ELSE NULL END) AS Additional_Internship_Count
        FROM STUDENT s
        LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
        LEFT JOIN COMPANY c ON p.Company_ID = c.Company_ID
        LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
        WHERE {where_clause}
        GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Email, s.Branch, s.Batch_Year, s.CGPA
        ORDER BY s.Batch_Year ASC, s.Roll_No ASC
    """

    rows = execute_query(sql, tuple(params))
    filtered_rows = []

    placement_status_filter = filters.get("placement_status")
    internship_status_filter = filters.get("internship_status")
    min_salary_filter = filters.get("min_salary")

    for r in rows:
        r["CGPA"] = float(r["CGPA"])
        r["Placed_Package"] = float(r["Placed_Package"]) if r.get("Placed_Package") is not None else None

        # Placement status filtering
        is_placed = r["Placed_Company"] is not None
        has_multiple = r["Total_Offers"] >= 2

        if placement_status_filter == "Placed" and not is_placed:
            continue
        if placement_status_filter == "Unplaced" and is_placed:
            continue
        if placement_status_filter == "Multiple" and not has_multiple:
            continue

        # Salary filter
        if min_salary_filter:
            try:
                min_sal = float(min_salary_filter)
                if not r["Placed_Package"] or r["Placed_Package"] < min_sal:
                    continue
            except (ValueError, TypeError):
                pass

        # Internship status filtering
        both_mandatory = (r["Has_Mandatory_1"] > 0 and r["Has_Mandatory_2"] > 0)
        missing_mandatory = not both_mandatory

        if internship_status_filter == "Complete" and not both_mandatory:
            continue
        if internship_status_filter == "Missing_Any" and not missing_mandatory:
            continue
        if internship_status_filter == "Missing_1" and r["Has_Mandatory_1"] > 0:
            continue
        if internship_status_filter == "Missing_2" and r["Has_Mandatory_2"] > 0:
            continue
        if internship_status_filter == "Has_Additional" and r["Additional_Internship_Count"] == 0:
            continue

        filtered_rows.append(r)

    # Calculate summary aggregations over the filtered set
    total_students = len(filtered_rows)
    placed_students = sum(1 for r in filtered_rows if r["Placed_Company"] is not None)
    placement_rate = round((placed_students / total_students * 100), 1) if total_students > 0 else 0.0
    packages = [r["Placed_Package"] for r in filtered_rows if r["Placed_Package"] is not None]
    avg_package = round(sum(packages) / len(packages), 2) if packages else 0.0
    max_package = max(packages) if packages else 0.0

    return {
        "rows": filtered_rows,
        "summary": {
            "total_students": total_students,
            "placed_students": placed_students,
            "placement_rate": placement_rate,
            "avg_package": avg_package,
            "max_package": max_package,
        },
    }

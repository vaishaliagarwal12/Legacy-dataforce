import logging
from typing import Dict, Any, List, Optional
from db.connection import execute_one, execute_query

logger = logging.getLogger(__name__)


def get_dashboard_stats() -> Dict[str, Any]:
    """Aggregates high-level system KPI metrics for the dashboard cards."""
    # 1. Student counts
    student_stats = execute_one("""
        SELECT 
            COUNT(*) AS total_students,
            COUNT(*) AS active_students,
            ROUND(AVG(CGPA), 2) AS avg_cgpa
        FROM STUDENT
    """) or {}

    # 2. Company & Drive counts
    company_stats = execute_one("""
        SELECT 
            COUNT(DISTINCT c.Company_ID) AS total_companies,
            SUM(CASE WHEN c.Company_Type = 'Product' THEN 1 ELSE 0 END) AS tier1_companies,
            (SELECT COUNT(*) FROM RECRUITMENT_DRIVE) AS total_drives,
            (SELECT COUNT(*) FROM OPPORTUNITY) AS total_opportunities
        FROM COMPANY c
    """) or {}

    # 3. Placement Offer counts and CTC metrics
    placement_stats = execute_one("""
        SELECT 
            COUNT(*) AS total_offers,
            SUM(CASE WHEN Offer_Status = 'Accepted' THEN 1 ELSE 0 END) AS accepted_offers,
            SUM(CASE WHEN Offer_Status = 'Joined' THEN 1 ELSE 0 END) AS joined_offers,
            COUNT(DISTINCT Student_ID) AS distinct_students_offered,
            COUNT(DISTINCT CASE WHEN Offer_Status IN ('Accepted', 'Joined') THEN Student_ID ELSE NULL END) AS placed_students,
            ROUND(AVG(Package), 2) AS avg_package,
            MAX(Package) AS highest_package,
            MIN(Package) AS lowest_package
        FROM PLACEMENT
    """) or {}

    # 4. Internship counts
    internship_stats = execute_one("""
        SELECT 
            COUNT(*) AS total_internships,
            SUM(CASE WHEN Internship_Type = 'Mandatory' THEN 1 ELSE 0 END) AS mandatory_internships,
            SUM(CASE WHEN Internship_Type = 'Additional' THEN 1 ELSE 0 END) AS additional_internships,
            COUNT(DISTINCT Student_ID) AS distinct_students_interned
        FROM INTERNSHIP
    """) or {}

    # 5. Missing mandatory count
    missing_mandatory = execute_one("""
        SELECT COUNT(*) AS missing_count
        FROM (
            SELECT s.Student_ID
            FROM STUDENT s
            LEFT JOIN INTERNSHIP i1 ON s.Student_ID = i1.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = 'Mandatory'
            LEFT JOIN INTERNSHIP i2 ON s.Student_ID = i2.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = 'Mandatory'
            WHERE (i1.Internship_ID IS NULL OR i2.Internship_ID IS NULL)
        ) AS missing_students
    """) or {}

    total_active = int(student_stats.get("active_students") or 0)
    placed_count = int(placement_stats.get("placed_students") or 0)
    placement_rate = round((placed_count / total_active * 100), 1) if total_active > 0 else 0.0

    return {
        "students": {
            "total": int(student_stats.get("total_students") or 0),
            "active": total_active,
            "avg_cgpa": float(student_stats.get("avg_cgpa") or 0.0),
        },
        "companies": {
            "total": int(company_stats.get("total_companies") or 0),
            "tier1": int(company_stats.get("tier1_companies") or 0),
            "drives": int(company_stats.get("total_drives") or 0),
            "opportunities": int(company_stats.get("total_opportunities") or 0),
        },
        "placements": {
            "total_offers": int(placement_stats.get("total_offers") or 0),
            "accepted_offers": int(placement_stats.get("accepted_offers") or 0),
            "joined_offers": int(placement_stats.get("joined_offers") or 0),
            "placed_students": placed_count,
            "placement_rate": placement_rate,
            "avg_package": float(placement_stats.get("avg_package") or 0.0),
            "highest_package": float(placement_stats.get("highest_package") or 0.0),
            "lowest_package": float(placement_stats.get("lowest_package") or 0.0),
        },
        "internships": {
            "total": int(internship_stats.get("total_internships") or 0),
            "mandatory": int(internship_stats.get("mandatory_internships") or 0),
            "additional": int(internship_stats.get("additional_internships") or 0),
            "distinct_students": int(internship_stats.get("distinct_students_interned") or 0),
            "missing_mandatory_count": int(missing_mandatory.get("missing_count") or 0),
        },
    }


def get_yearwise_placement_chart_data() -> Dict[str, Any]:
    """Fetches year-wise offer volume and average package for Chart.js."""
    rows = execute_query("""
        SELECT 
            Placement_Year,
            COUNT(*) AS offer_count,
            SUM(CASE WHEN Offer_Status IN ('Accepted', 'Joined') THEN 1 ELSE 0 END) AS accepted_count,
            ROUND(AVG(Package), 2) AS avg_package,
            MAX(Package) AS max_package
        FROM PLACEMENT
        GROUP BY Placement_Year
        ORDER BY Placement_Year ASC
    """)
    labels = [str(r["Placement_Year"]) for r in rows]
    offer_counts = [int(r["offer_count"]) for r in rows]
    accepted_counts = [int(r["accepted_count"]) for r in rows]
    avg_packages = [float(r["avg_package"]) for r in rows]
    max_packages = [float(r["max_package"]) for r in rows]

    return {
        "labels": labels,
        "offer_counts": offer_counts,
        "accepted_counts": accepted_counts,
        "avg_packages": avg_packages,
        "max_packages": max_packages,
    }


def get_branchwise_analytics_chart_data() -> Dict[str, Any]:
    """Fetches branch-wise student, placement, and internship distribution for Chart.js."""
    rows = execute_query("""
        SELECT 
            s.Branch,
            COUNT(DISTINCT s.Student_ID) AS student_count,
            COUNT(DISTINCT CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN s.Student_ID ELSE NULL END) AS placed_students,
            COUNT(DISTINCT i.Internship_ID) AS internship_count,
            ROUND(AVG(s.CGPA), 2) AS avg_cgpa,
            ROUND(AVG(p.Package), 2) AS avg_package
        FROM STUDENT s
        LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
        LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
        GROUP BY s.Branch
        ORDER BY student_count DESC, s.Branch ASC
    """)
    labels = [r["Branch"] for r in rows]
    student_counts = [int(r["student_count"]) for r in rows]
    placed_students = [int(r["placed_students"]) for r in rows]
    internship_counts = [int(r["internship_count"]) for r in rows]
    avg_packages = [float(r["avg_package"] or 0.0) for r in rows]

    return {
        "labels": labels,
        "student_counts": student_counts,
        "placed_students": placed_students,
        "internship_counts": internship_counts,
        "avg_packages": avg_packages,
    }


def get_offer_status_chart_data() -> Dict[str, Any]:
    """Fetches breakdown of placement statuses (Offered, Accepted, Joined, Declined)."""
    rows = execute_query("""
        SELECT 
            Offer_Status,
            COUNT(*) AS count
        FROM PLACEMENT
        GROUP BY Offer_Status
        ORDER BY FIELD(Offer_Status, 'Offered', 'Accepted', 'Joined', 'Declined')
    """)
    labels = [r["Offer_Status"] for r in rows]
    counts = [int(r["count"]) for r in rows]
    return {
        "labels": labels,
        "counts": counts,
    }


def get_internship_breakdown_chart_data() -> Dict[str, Any]:
    """Fetches breakdown of internships: Mandatory #1, Mandatory #2, Additional."""
    rows = execute_query("""
        SELECT 
            CASE 
                WHEN Internship_Type = 'Mandatory' AND Internship_No = 1 THEN 'Mandatory #1 (Sem 3)'
                WHEN Internship_Type = 'Mandatory' AND Internship_No = 2 THEN 'Mandatory #2 (Sem 5)'
                ELSE 'Additional Internships'
            END AS category,
            COUNT(*) AS count
        FROM INTERNSHIP
        GROUP BY category
        ORDER BY category ASC
    """)
    labels = [r["category"] for r in rows]
    counts = [int(r["count"]) for r in rows]
    return {
        "labels": labels,
        "counts": counts,
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

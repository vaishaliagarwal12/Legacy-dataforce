import re
import time
import decimal
import datetime
import logging
from typing import Any, Dict, List, Optional, Tuple
import pymysql
from pymysql.cursors import DictCursor

from db.connection import get_cursor, get_readonly_connection, DatabaseError
from services.exceptions import ValidationError, ServiceError

logger = logging.getLogger(__name__)

# ==============================================================================
# CATALOG OF SAVED DBMS QUERIES
# Categorized into: Students, Placements, Internships, Combined
# ==============================================================================

SAVED_QUERIES: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # 1. STUDENTS
    # -------------------------------------------------------------------------
    {
        "id": "students_all",
        "title": "A1. List All Registered Students",
        "group": "Students",
        "dbms_concept": "Relational projection (π) and lexicographical multi-attribute ordering (ORDER BY Batch_Year, Branch, Student_Name).",
        "sql": """SELECT Student_ID, Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Student_Name,
       Branch, Batch_Year, CGPA, Backlogs
FROM STUDENT
ORDER BY Batch_Year, Branch, Student_Name;""",
        "params": [],
    },
    {
        "id": "students_branch_batch",
        "title": "A2. Students of Specific Branch and Batch",
        "group": "Students",
        "dbms_concept": "Equality selection (σ) on composite index (Branch, Batch_Year) with descending sort on continuous numeric CGPA.",
        "sql": """SELECT Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Student_Name, Branch, Batch_Year, CGPA
FROM STUDENT
WHERE Branch = %s AND Batch_Year = %s
ORDER BY CGPA DESC;""",
        "params": [
            {"name": "branch", "label": "Branch Code", "type": "select", "options": ["CSE", "ECE", "ME", "IT"], "default": "CSE"},
            {"name": "batch_year", "label": "Batch Year", "type": "number", "default": 2024, "placeholder": "e.g. 2024"},
        ],
    },
    {
        "id": "students_profile",
        "title": "A3. Complete Profile of One Student",
        "group": "Students",
        "dbms_concept": "Correlated scalar subqueries in SELECT projection aggregating 1:N multi-valued attributes (phones, skills) without Cartesian row explosion.",
        "sql": """SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       s.Branch, s.Batch_Year, s.CGPA, s.Backlogs, s.Resume_Link,
       (SELECT GROUP_CONCAT(ph.Phone_No SEPARATOR ', ')
          FROM STUDENT_PHONE ph WHERE ph.Student_ID = s.Student_ID) AS Phones,
       (SELECT GROUP_CONCAT(sk.Skill SEPARATOR ', ')
          FROM STUDENT_SKILL sk WHERE sk.Student_ID = s.Student_ID) AS Extra_Skills
FROM STUDENT s
WHERE s.Roll_No = %s;""",
        "params": [
            {"name": "roll_no", "label": "Roll Number", "type": "text", "default": "CS201802", "placeholder": "e.g. CS201802"},
        ],
    },
    {
        "id": "students_by_skill",
        "title": "A4. Students Possessing a Particular Skill",
        "group": "Students",
        "dbms_concept": "Relational equi-join connecting master STUDENT with 1NF child entity STUDENT_SKILL using foreign key traversal.",
        "sql": """SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.CGPA, sk.Skill
FROM STUDENT s
JOIN STUDENT_SKILL sk ON sk.Student_ID = s.Student_ID
WHERE sk.Skill = %s
ORDER BY s.CGPA DESC;""",
        "params": [
            {"name": "skill", "label": "Skill Name", "type": "text", "default": "Python", "placeholder": "e.g. Python, SQL, Java"},
        ],
    },
    {
        "id": "students_high_cgpa_nobacklogs",
        "title": "A5. Students with High CGPA and Zero Backlogs",
        "group": "Students",
        "dbms_concept": "Multi-attribute selection on continuous domain (CGPA >= cutoff) and discrete domain (Backlogs = 0) utilizing secondary B+ tree index.",
        "sql": """SELECT Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Student_Name, Branch, Batch_Year, CGPA, Backlogs
FROM STUDENT
WHERE CGPA >= %s AND Backlogs = 0
ORDER BY CGPA DESC;""",
        "params": [
            {"name": "min_cgpa", "label": "Minimum CGPA", "type": "number", "step": "0.1", "default": 8.0, "placeholder": "e.g. 8.0"},
        ],
    },
    {
        "id": "students_not_placed_antijoin",
        "title": "A6 / ADD-1. Students Not Placed (LEFT OUTER Anti-Join)",
        "group": "Students",
        "dbms_concept": "Relational Outer Anti-Join (R ▷ S): Preserves unmatched master tuples by performing LEFT JOIN on Joined='Yes' and filtering for IS NULL on foreign key.",
        "sql": """SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       s.Branch, s.Batch_Year, s.CGPA
FROM STUDENT s
LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID AND p.Joined = 'Yes'
WHERE p.Placement_ID IS NULL
ORDER BY s.CGPA DESC;""",
        "params": [],
    },
    {
        "id": "students_above_avg_cgpa",
        "title": "ADD-2. Students with CGPA Above Institutional Average",
        "group": "Students",
        "dbms_concept": "Scalar non-correlated subquery dynamically calculating the global mean CGPA and projecting the individual variance delta at runtime.",
        "sql": """SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.Batch_Year, s.CGPA,
       ROUND((SELECT AVG(CGPA) FROM STUDENT), 2) AS Benchmark_Avg_CGPA,
       ROUND(s.CGPA - (SELECT AVG(CGPA) FROM STUDENT), 2) AS Delta_From_Avg
FROM STUDENT s
WHERE s.CGPA > (SELECT AVG(CGPA) FROM STUDENT)
ORDER BY s.CGPA DESC;""",
        "params": [],
    },
    {
        "id": "students_name_search",
        "title": "D11. Search Student by Name (Disjunctive Wildcard)",
        "group": "Students",
        "dbms_concept": "Non-anchored pattern matching (LIKE %...%) disjunctively evaluated across composite names, outer joined to retrieve placement status.",
        "sql": """SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       s.Branch, s.CGPA, COALESCE(c.Company_Name, 'Unplaced') AS Joined_Company, p.Package
FROM STUDENT s
LEFT JOIN PLACEMENT p ON p.Student_ID = s.Student_ID AND p.Joined = 'Yes'
LEFT JOIN COMPANY   c ON c.Company_ID = p.Company_ID
WHERE s.First_Name LIKE %s OR s.Last_Name LIKE %s
ORDER BY s.Student_ID;""",
        "params": [
            {"name": "search_name", "label": "Name Keyword", "type": "text", "default": "Aarav", "placeholder": "e.g. Aarav, Sharma, Neha"},
        ],
    },

    # -------------------------------------------------------------------------
    # 2. PLACEMENTS
    # -------------------------------------------------------------------------
    {
        "id": "placements_all_joined",
        "title": "B1. Placed Students with Company and Compensation",
        "group": "Placements",
        "dbms_concept": "Relational view abstraction (V_PLACEMENT_DETAIL) encapsulating multi-table equi-join filtered by Joined = 'Yes' sorted by package descending.",
        "sql": """SELECT Roll_No, Student_Name, Branch, Batch_Year, Company_Name, Role, Package, Placement_Year
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
ORDER BY Package DESC;""",
        "params": [],
    },
    {
        "id": "placements_by_company",
        "title": "B2. Placements Recruited by Specific Company",
        "group": "Placements",
        "dbms_concept": "Parameterized relational equi-join with point-filter on indexed corporate entity evaluating organization-level hiring yield.",
        "sql": """SELECT Student_Name, Branch, Batch_Year, Role, Package, Placement_Year, Joined
FROM V_PLACEMENT_DETAIL
WHERE Company_Name = %s
ORDER BY Placement_Year, Package DESC;""",
        "params": [
            {"name": "company_name", "label": "Company Name", "type": "text", "default": "Infosys Technologies", "placeholder": "e.g. Infosys Technologies, Apex Cloud Innovations, Google India"},
        ],
    },
    {
        "id": "placements_branch_stats",
        "title": "B3. Branch-Wise Placement Statistics",
        "group": "Placements",
        "dbms_concept": "Categorical aggregate reduction (COUNT, AVG, MAX, MIN) partitioned by academic branch computing headcount and salary spread.",
        "sql": """SELECT Branch,
       COUNT(*)               AS Students_Placed,
       ROUND(AVG(Package), 2) AS Avg_Package,
       MAX(Package)           AS Highest_Package,
       MIN(Package)           AS Lowest_Package
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
GROUP BY Branch
ORDER BY Avg_Package DESC;""",
        "params": [],
    },
    {
        "id": "placements_year_stats",
        "title": "B4. Year-Wise Placement Statistics & Cohort Trends",
        "group": "Placements",
        "dbms_concept": "Temporal aggregation grouping by academic cohort year measuring historical compensation escalation and placement volume.",
        "sql": """SELECT Placement_Year,
       COUNT(*)               AS Students_Placed,
       ROUND(AVG(Package), 2) AS Avg_Package,
       MAX(Package)           AS Highest_Package
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
GROUP BY Placement_Year
ORDER BY Placement_Year;""",
        "params": [],
    },
    {
        "id": "placements_company_hiring",
        "title": "B5. Company-Wise Hiring Volume & Salary Metrics",
        "group": "Placements",
        "dbms_concept": "Multi-column grouping (Company_ID, Company_Name, Company_Type) strictly preserving functional dependencies under ANSI SQL.",
        "sql": """SELECT Company_Name, Company_Type,
       COUNT(*)               AS Students_Joined,
       ROUND(AVG(Package), 2) AS Avg_Package,
       MAX(Package)           AS Highest_Package
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
GROUP BY Company_ID, Company_Name, Company_Type
ORDER BY Students_Joined DESC, Avg_Package DESC;""",
        "params": [],
    },
    {
        "id": "placements_top_packages",
        "title": "B6. Top 5 Highest Placement Packages (Top-K)",
        "group": "Placements",
        "dbms_concept": "Top-K query optimization utilizing sorted index scanning and heap limit buffers to retrieve maximum compensation offers.",
        "sql": """SELECT Student_Name, Branch, Company_Name, Package, Placement_Year
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
ORDER BY Package DESC
LIMIT 5;""",
        "params": [],
    },
    {
        "id": "placements_branch_percent",
        "title": "B7. Placement Percentage by Branch and Batch",
        "group": "Placements",
        "dbms_concept": "Cohort grouping evaluating existential subquery membership (SUM(EXISTS...)) to compute institutional placement success rates.",
        "sql": """SELECT s.Branch, s.Batch_Year,
       COUNT(*) AS Total_Students,
       SUM(EXISTS (SELECT 1 FROM PLACEMENT p
                   WHERE p.Student_ID = s.Student_ID AND p.Joined = 'Yes')) AS Placed,
       ROUND(100 * SUM(EXISTS (SELECT 1 FROM PLACEMENT p
                               WHERE p.Student_ID = s.Student_ID AND p.Joined = 'Yes'))
                 / COUNT(*), 1) AS Placement_Percent
FROM STUDENT s
GROUP BY s.Branch, s.Batch_Year
ORDER BY s.Batch_Year, s.Branch;""",
        "params": [],
    },
    {
        "id": "placements_multiple_offers",
        "title": "B8. Students Receiving Multiple Placement Offers",
        "group": "Placements",
        "dbms_concept": "Post-aggregation cardinality filtering (HAVING COUNT(*) > 1) combined with GROUP_CONCAT offer list and conditional selection.",
        "sql": """SELECT Student_Name, Roll_No,
       COUNT(*) AS Total_Offers,
       GROUP_CONCAT(CONCAT(Company_Name, ' (', Package, ' LPA)') SEPARATOR ', ') AS Offers,
       MAX(CASE WHEN Joined = 'Yes' THEN Company_Name END) AS Joined_Company
FROM V_PLACEMENT_DETAIL
GROUP BY Student_ID, Student_Name, Roll_No
HAVING COUNT(*) > 1;""",
        "params": [],
    },
    {
        "id": "placements_ppo_offers",
        "title": "B9. Students Receiving Pre-Placement Offers (PPO)",
        "group": "Placements",
        "dbms_concept": "Selection on categorical ENUM attribute (Is_PPO = 'Yes') measuring direct conversion yield from internships to corporate placements.",
        "sql": """SELECT Student_Name, Branch, Company_Name, Package, Placement_Year, Joined
FROM V_PLACEMENT_DETAIL
WHERE Is_PPO = 'Yes'
ORDER BY Placement_Year, Package DESC;""",
        "params": [],
    },
    {
        "id": "placements_cgpa_bands",
        "title": "B11. CGPA Performance Bands vs Average Package",
        "group": "Placements",
        "dbms_concept": "Conditional value discretization using CASE WHEN mapping continuous CGPA metrics into academic achievement tiers.",
        "sql": """SELECT CASE WHEN CGPA >= 9 THEN '9.0 and above'
            WHEN CGPA >= 8 THEN '8.0 - 8.99'
            WHEN CGPA >= 7 THEN '7.0 - 7.99'
            ELSE 'Below 7.0' END AS CGPA_Band,
       COUNT(*)               AS Students_Placed,
       ROUND(AVG(Package), 2) AS Avg_Package
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
GROUP BY CGPA_Band
ORDER BY MIN(CGPA) DESC;""",
        "params": [],
    },
    {
        "id": "placements_above_threshold",
        "title": "B14. Placement Packages Above Specified Threshold",
        "group": "Placements",
        "dbms_concept": "Decimal numerical inequality filtering parameterized safely, isolating elite compensation offers across hiring partners.",
        "sql": """SELECT Student_Name, Branch, Company_Name, Role, Package, Placement_Year
FROM V_PLACEMENT_DETAIL
WHERE Package >= %s AND Joined = 'Yes'
ORDER BY Package DESC;""",
        "params": [
            {"name": "min_package", "label": "Minimum Package (LPA)", "type": "number", "step": "0.5", "default": 10.0, "placeholder": "e.g. 10.0"},
        ],
    },

    # -------------------------------------------------------------------------
    # 3. INTERNSHIPS
    # -------------------------------------------------------------------------
    {
        "id": "internships_student_history",
        "title": "C1. All Internships of One Student (Calculated Duration)",
        "group": "Internships",
        "dbms_concept": "Dynamic calculation of derived attribute (Duration_Months via DATEDIFF) at query runtime, preventing physical storage redundancy.",
        "sql": """SELECT Internship_No, Internship_Type, Company_Name, Role,
       Start_Date, End_Date, Duration_Months, Stipend,
       Credits, Report_Semester, Report_Grade
FROM V_INTERNSHIP_DETAIL
WHERE Roll_No = %s
ORDER BY Internship_No;""",
        "params": [
            {"name": "roll_no", "label": "Roll Number", "type": "text", "default": "CS201802", "placeholder": "e.g. CS201802"},
        ],
    },
    {
        "id": "internships_by_company",
        "title": "C2. Internships Hosted by Specific Organization",
        "group": "Internships",
        "dbms_concept": "Weak entity to strong corporate entity relational join filtered by organization name, analyzing internship engagement.",
        "sql": """SELECT Student_Name, Branch, Internship_No, Role, Start_Date, End_Date, Stipend
FROM V_INTERNSHIP_DETAIL
WHERE Company_Name = %s
ORDER BY Start_Date;""",
        "params": [
            {"name": "company_name", "label": "Company Name", "type": "text", "default": "Infosys Technologies", "placeholder": "e.g. Infosys Technologies, Apex Cloud Innovations, Google India"},
        ],
    },
    {
        "id": "internships_mandatory_compliance",
        "title": "C3. Mandatory Internship Completion Audit",
        "group": "Internships",
        "dbms_concept": "Left outer join with conditional aggregation (COUNT(CASE WHEN...)) ensuring students with zero internships are preserved in audit.",
        "sql": """SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       COUNT(CASE WHEN i.Internship_Type = 'Mandatory'  THEN 1 END) AS Mandatory_Done,
       COUNT(CASE WHEN i.Internship_Type = 'Additional' THEN 1 END) AS Additional_Done,
       COUNT(i.Internship_No)                                       AS Total_Internships
FROM STUDENT s
LEFT JOIN INTERNSHIP i ON i.Student_ID = s.Student_ID
GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name
ORDER BY Mandatory_Done ASC, Total_Internships ASC;""",
        "params": [],
    },
    {
        "id": "internships_rule_check_defaulters",
        "title": "C4. Rule Check: Students with Incomplete Mandatory Internships",
        "group": "Internships",
        "dbms_concept": "Integrity rule verification using conditional aggregation inside a HAVING clause (HAVING Mandatory_Done < 2) to flag deficient students.",
        "sql": """SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       COUNT(CASE WHEN i.Internship_Type = 'Mandatory' THEN 1 END) AS Mandatory_Done
FROM STUDENT s
LEFT JOIN INTERNSHIP i ON i.Student_ID = s.Student_ID
GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name
HAVING COUNT(CASE WHEN i.Internship_Type = 'Mandatory' THEN 1 END) < 2;""",
        "params": [],
    },
    {
        "id": "internships_avg_stipend_company",
        "title": "C6. Average Monthly Stipend Across Companies",
        "group": "Internships",
        "dbms_concept": "Aggregate reduction evaluating compensation metrics (mean and maximum monthly stipend) across internship sponsor firms.",
        "sql": """SELECT Company_Name,
       COUNT(*)               AS Interns,
       ROUND(AVG(Stipend), 0) AS Avg_Stipend,
       MAX(Stipend)           AS Highest_Stipend
FROM V_INTERNSHIP_DETAIL
GROUP BY Company_ID, Company_Name
ORDER BY Avg_Stipend DESC;""",
        "params": [],
    },
    {
        "id": "internships_date_range",
        "title": "C12. Internships Active in Date Range",
        "group": "Internships",
        "dbms_concept": "Temporal boundary filtering on calendar date types (Start_Date >= and End_Date <=) isolating seasonal internship batches.",
        "sql": """SELECT Student_Name, Internship_No, Company_Name, Role, Start_Date, End_Date, Stipend
FROM V_INTERNSHIP_DETAIL
WHERE Start_Date >= %s AND End_Date <= %s
ORDER BY Start_Date;""",
        "params": [
            {"name": "start_date", "label": "Start Date", "type": "text", "default": "2023-01-01", "placeholder": "YYYY-MM-DD"},
            {"name": "end_date", "label": "End Date", "type": "text", "default": "2024-12-31", "placeholder": "YYYY-MM-DD"},
        ],
    },

    # -------------------------------------------------------------------------
    # 4. COMBINED
    # -------------------------------------------------------------------------
    {
        "id": "combined_internship_to_job",
        "title": "D1. Internships Converted to Full-Time Placements (PPO Track)",
        "group": "Combined",
        "dbms_concept": "Composite multi-column inner equi-join matching on (Student_ID AND Company_ID) correlating internship history with final placement.",
        "sql": """SELECT DISTINCT p.Student_Name, p.Branch, p.Company_Name, p.Package, p.Is_PPO
FROM V_PLACEMENT_DETAIL p
JOIN INTERNSHIP i
  ON i.Student_ID = p.Student_ID AND i.Company_ID = p.Company_ID
WHERE p.Joined = 'Yes'
ORDER BY p.Package DESC;""",
        "params": [],
    },
    {
        "id": "combined_popular_skills",
        "title": "D2. Most Prevalent Technical Skills Among Students",
        "group": "Combined",
        "dbms_concept": "Frequency distribution across 1NF decomposed multi-valued skill entities ranking student technical capabilities.",
        "sql": """SELECT Skill, COUNT(*) AS Students_With_Skill
FROM STUDENT_SKILL
GROUP BY Skill
ORDER BY Students_With_Skill DESC, Skill;""",
        "params": [],
    },
    {
        "id": "combined_indemand_skills",
        "title": "D3. In-Demand Skills Evaluated for Placement Offers",
        "group": "Combined",
        "dbms_concept": "Demand-side aggregation grouping through bridge relation PLACEMENT_SKILL to determine market skill requirements.",
        "sql": """SELECT ps.Skill, COUNT(*) AS Times_Selected_For
FROM PLACEMENT_SKILL ps
GROUP BY ps.Skill
ORDER BY Times_Selected_For DESC, ps.Skill;""",
        "params": [],
    },
    {
        "id": "combined_skill_avg_package",
        "title": "D4. Average Package by Technical Skill Evaluated",
        "group": "Combined",
        "dbms_concept": "Many-to-many bridge relation traversal connecting technical competencies to realized salary outcomes with mean aggregation.",
        "sql": """SELECT ps.Skill, COUNT(*) AS Students, ROUND(AVG(p.Package), 2) AS Avg_Package
FROM PLACEMENT_SKILL ps
JOIN PLACEMENT p ON p.Placement_ID = ps.Placement_ID
WHERE p.Joined = 'Yes'
GROUP BY ps.Skill
ORDER BY Avg_Package DESC;""",
        "params": [],
    },
    {
        "id": "combined_company_skills",
        "title": "D5. Technical Skills Targeted by Specific Company",
        "group": "Combined",
        "dbms_concept": "Three-table relational equi-join traversing bridge entity PLACEMENT_SKILL to PLACEMENT and COMPANY with selective filter.",
        "sql": """SELECT DISTINCT c.Company_Name, ps.Skill
FROM PLACEMENT_SKILL ps
JOIN PLACEMENT p ON p.Placement_ID = ps.Placement_ID
JOIN COMPANY c   ON c.Company_ID  = p.Company_ID
WHERE c.Company_Name = %s
ORDER BY ps.Skill;""",
        "params": [
            {"name": "company_name", "label": "Company Name", "type": "text", "default": "Infosys Technologies", "placeholder": "e.g. Infosys Technologies, Apex Cloud Innovations, Google India"},
        ],
    },
    {
        "id": "combined_dual_partners",
        "title": "D6. Dual-Role Corporate Partners (Internships + Placements)",
        "group": "Combined",
        "dbms_concept": "Dual correlated existential predicates (EXISTS ... AND EXISTS ...) proving relationship set intersection across distinct operational scopes.",
        "sql": """SELECT c.Company_Name, c.Company_Type,
       (SELECT COUNT(*) FROM INTERNSHIP i WHERE i.Company_ID = c.Company_ID) AS Interns_Taken,
       (SELECT COUNT(*) FROM PLACEMENT  p WHERE p.Company_ID = c.Company_ID) AS Offers_Made
FROM COMPANY c
WHERE EXISTS (SELECT 1 FROM INTERNSHIP i WHERE i.Company_ID = c.Company_ID)
  AND EXISTS (SELECT 1 FROM PLACEMENT  p WHERE p.Company_ID = c.Company_ID);""",
        "params": [],
    },
    {
        "id": "combined_company_polymorphic",
        "title": "D7. Polymorphic Corporate Activity Profile (UNION ALL)",
        "group": "Combined",
        "dbms_concept": "Set Union (UNION ALL) combining distinct activity records into a unified polymorphic schema with synthetic discriminator column.",
        "sql": """SELECT 'Internship' AS Record_Type, Student_Name, Branch, Role, NULL AS Package, Stipend
FROM V_INTERNSHIP_DETAIL
WHERE Company_Name = %s
UNION ALL
SELECT 'Placement' AS Record_Type, Student_Name, Branch, Role, Package, NULL AS Stipend
FROM V_PLACEMENT_DETAIL
WHERE Company_Name = %s
ORDER BY Record_Type, Student_Name;""",
        "params": [
            {"name": "company_name", "label": "Company Name", "type": "text", "default": "Infosys Technologies", "placeholder": "e.g. Infosys Technologies, Apex Cloud Innovations, Google India"},
        ],
    },
    {
        "id": "combined_full_career_report",
        "title": "D8. Comprehensive Student Career Synthesis",
        "group": "Combined",
        "dbms_concept": "Multiple correlated scalar subqueries synthesizing academic performance, technical skills, internship volume, and placement outcomes into a master tuple.",
        "sql": """SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       s.Branch, s.Batch_Year, s.CGPA,
       (SELECT GROUP_CONCAT(sk.Skill SEPARATOR ', ')
          FROM STUDENT_SKILL sk WHERE sk.Student_ID = s.Student_ID)              AS Extra_Skills,
       (SELECT COUNT(*) FROM INTERNSHIP i WHERE i.Student_ID = s.Student_ID)     AS Internships_Done,
       (SELECT c.Company_Name FROM PLACEMENT p JOIN COMPANY c ON c.Company_ID = p.Company_ID
         WHERE p.Student_ID = s.Student_ID AND p.Joined = 'Yes' LIMIT 1)         AS Joined_Company,
       (SELECT p.Package FROM PLACEMENT p
         WHERE p.Student_ID = s.Student_ID AND p.Joined = 'Yes' LIMIT 1)         AS Package
FROM STUDENT s
ORDER BY s.Batch_Year, s.Branch, s.Roll_No;""",
        "params": [],
    },
    {
        "id": "combined_skills_cohort_comparison",
        "title": "ADD-3A. Skill Profile Comparison: Placed vs Non-Placed Cohorts",
        "group": "Combined",
        "dbms_concept": "Multi-way outer join with conditional aggregation comparing total acquired skills, mean skill density, and unique skills acquired across cohorts.",
        "sql": """SELECT 
    CASE WHEN p.Joined = 'Yes' THEN 'Placed Students' ELSE 'Non-Placed Students' END AS Placement_Status,
    COUNT(DISTINCT s.Student_ID) AS Total_Students,
    COUNT(sk.Skill) AS Total_Skills_Reported,
    ROUND(COUNT(sk.Skill) / COUNT(DISTINCT s.Student_ID), 2) AS Avg_Skills_Per_Student,
    GROUP_CONCAT(DISTINCT sk.Skill ORDER BY sk.Skill SEPARATOR ', ') AS Unique_Skills_Acquired
FROM STUDENT s
LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID AND p.Joined = 'Yes'
LEFT JOIN STUDENT_SKILL sk ON s.Student_ID = sk.Student_ID
GROUP BY CASE WHEN p.Joined = 'Yes' THEN 'Placed Students' ELSE 'Non-Placed Students' END;""",
        "params": [],
    },
]

SAVED_QUERIES_BY_ID = {q["id"]: q for q in SAVED_QUERIES}


def list_saved_queries() -> List[Dict[str, Any]]:
    """Returns the catalog of saved queries grouped by category."""
    return SAVED_QUERIES


def get_saved_query(query_id: str) -> Optional[Dict[str, Any]]:
    """Fetches metadata for a single saved query by its ID."""
    return SAVED_QUERIES_BY_ID.get(query_id)


def _serialize_value(val: Any) -> Any:
    """Safely converts DB types (Decimals, dates) into JSON/CSV serializable formats."""
    if isinstance(val, decimal.Decimal):
        return float(val)
    if isinstance(val, (datetime.date, datetime.datetime)):
        return val.isoformat()
    return val


def execute_saved_query(query_id: str, param_values: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Executes a saved query using strict parameterization with %s placeholders.
    
    Never concatenates user input into the SQL string.
    """
    query_meta = get_saved_query(query_id)
    if not query_meta:
        raise ValidationError(f"Saved query '{query_id}' not found.")

    param_values = param_values or {}
    sql = query_meta["sql"]
    param_meta_list = query_meta.get("params", [])

    # Extract and type-cast parameters in strict order
    args_list: List[Any] = []
    
    # Special case: D7 polymorphic query uses company_name twice in UNION ALL
    if query_id == "combined_company_polymorphic":
        default_co = param_meta_list[0]["default"] if param_meta_list else "Infosys Technologies"
        val = str(param_values.get("company_name", default_co)).strip() or default_co
        args_list = [val, val]
    elif query_id == "students_name_search":
        val = str(param_values.get("search_name", "Aarav")).strip() or "Aarav"
        wildcard_val = f"%{val}%"
        args_list = [wildcard_val, wildcard_val]
    else:
        for pm in param_meta_list:
            raw = param_values.get(pm["name"], pm.get("default"))
            if raw is None or str(raw).strip() == "":
                raw = pm.get("default")
            
            p_type = pm.get("type", "text")
            if p_type == "number":
                step = pm.get("step")
                try:
                    casted = float(raw) if (step or "." in str(raw)) else int(raw)
                except (ValueError, TypeError):
                    casted = float(raw) if "." in str(raw) else int(float(raw))
                args_list.append(casted)
            else:
                args_list.append(str(raw).strip())

    start_time = time.perf_counter()
    with get_cursor(commit=False) as cursor:
        try:
            cursor.execute(sql, tuple(args_list))
            raw_rows = cursor.fetchall()
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            
            columns = [col[0] for col in cursor.description] if cursor.description else []
            rows = [
                {k: _serialize_value(v) for k, v in row.items()}
                for row in raw_rows[:500]
            ]

            return {
                "id": query_id,
                "title": query_meta["title"],
                "group": query_meta["group"],
                "dbms_concept": query_meta["dbms_concept"],
                "sql": sql,
                "params_used": args_list,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "execution_time_ms": elapsed_ms,
            }
        except pymysql.MySQLError as err:
            logger.error("Saved query failed: %s | Query ID: %s | Args: %s", err, query_id, args_list)
            raise ServiceError(f"Database query execution failed: {err}") from err


# ==============================================================================
# PART 2: CUSTOM SQL SAFETY VALIDATOR & READ-ONLY EXECUTOR
# ==============================================================================

# Regex for detecting forbidden statements, commands, or data modifications
FORBIDDEN_KEYWORDS_PATTERN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|REPLACE|GRANT|REVOKE|"
    r"LOCK|UNLOCK|CALL|EXECUTE|PREPARE|DEALLOCATE|SET|FLUSH|KILL|RESET|SHUTDOWN|"
    r"LOAD_FILE|OUTFILE|DUMPFILE)\b",
    re.IGNORECASE,
)


def validate_custom_sql(raw_sql: str) -> str:
    """Validates user-submitted SQL against strict security rules on the server.
    
    Safety rules enforced:
    1. Query cannot be empty.
    2. Prohibits comment syntax (-- , /* */, #) to prevent statement hiding.
    3. Exactly ONE statement allowed (semicolons inside statement prohibited).
    4. Must start with SELECT.
    5. Rejects INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, and administrative keywords.
    6. Automatically caps / sets row limit to 500.
    
    Returns the sanitized SQL ready for execution.
    Raises ValidationError if any rule is violated.
    """
    if not raw_sql or not raw_sql.strip():
        raise ValidationError("SQL statement cannot be empty. Please enter a valid SELECT query.")

    sql = raw_sql.strip()

    # Rule 1: Reject comments hiding other statements
    if "--" in sql:
        raise ValidationError("SQL line comments ('--') are prohibited to prevent statement hiding. Please remove all comments.")
    if "/*" in sql or "*/" in sql:
        raise ValidationError("SQL block comments ('/* ... */') are prohibited to prevent statement hiding. Please remove all comments.")
    if "#" in sql:
        raise ValidationError("SQL hash comments ('#') are prohibited to prevent statement hiding. Please remove all comments.")

    # Rule 2: Ensure exactly one statement (reject multiple statements / stacked queries)
    # Strip a single optional trailing semicolon
    if sql.endswith(";"):
        sql = sql[:-1].strip()

    if ";" in sql:
        raise ValidationError("Multiple statements are strictly forbidden. Only exactly one SQL query can be executed.")

    # Rule 3: Allow only statements that start with SELECT
    first_token_match = re.match(r"^\s*([A-Za-z]+)", sql)
    if not first_token_match:
        raise ValidationError("Invalid query syntax. Query must begin with a valid SQL keyword.")

    first_word = first_token_match.group(1).upper()
    if first_word != "SELECT":
        raise ValidationError(f"Forbidden operation: '{first_word}'. Only queries starting with SELECT are permitted in the SQL Console.")

    # Rule 4: Reject forbidden keywords anywhere in the statement
    forbidden_match = FORBIDDEN_KEYWORDS_PATTERN.search(sql)
    if forbidden_match:
        matched_op = forbidden_match.group(1).upper()
        raise ValidationError(f"Forbidden operation detected: '{matched_op}'. Data definition, modification, and execution commands are blocked.")

    # Rule 5: Enforce max 500 rows limit
    limit_match = re.search(r"\bLIMIT\s+(\d+)\b", sql, re.IGNORECASE)
    if limit_match:
        specified_limit = int(limit_match.group(1))
        if specified_limit > 500:
            # Clamp limit down to 500
            sql = sql[:limit_match.start()] + "LIMIT 500" + sql[limit_match.end():]
    else:
        # Append LIMIT 500 safely
        sql = f"{sql} LIMIT 500"

    return sql


def execute_custom_query(raw_sql: str) -> Dict[str, Any]:
    """Executes an ad-hoc SQL query submitted by the user under strict isolation:
    
    1. Validates SQL through `validate_custom_sql`.
    2. Authenticates as the dedicated MySQL user `placement_readonly` (SELECT privilege only).
    3. Enforces session statement timeout `max_execution_time = 3000` (3 seconds).
    4. Fetches at most 500 rows.
    5. Measures execution time in milliseconds.
    6. Formats all database errors into human-readable messages without server crash.
    """
    # Step 1: Server-side validation
    validated_sql = validate_custom_sql(raw_sql)

    start_time = time.perf_counter()
    
    # Step 2: Use dedicated read-only MySQL connection
    try:
        with get_readonly_connection() as connection:
            cursor = connection.cursor(DictCursor)
            try:
                # Step 3: Set query timeout to 3000ms (3 seconds)
                try:
                    cursor.execute("SET SESSION max_execution_time = 3000;")
                except Exception as set_err:
                    logger.debug("Could not set session max_execution_time: %s", set_err)

                # Step 4: Execute query
                cursor.execute(validated_sql)
                raw_rows = cursor.fetchmany(500)
                elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

                columns = [col[0] for col in cursor.description] if cursor.description else []
                rows = [
                    {k: _serialize_value(v) for k, v in row.items()}
                    for row in raw_rows
                ]

                return {
                    "status": "success",
                    "sql": validated_sql,
                    "columns": columns,
                    "rows": rows,
                    "row_count": len(rows),
                    "execution_time_ms": elapsed_ms,
                    "error": None,
                }
            finally:
                cursor.close()

    except pymysql.err.OperationalError as op_err:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        errno = op_err.args[0] if op_err.args else 0
        err_msg = op_err.args[1] if len(op_err.args) > 1 else str(op_err)
        
        # MySQL error code 3024 / 1317 is statement execution time exceeded
        if errno in (3024, 1317) or "execution time exceeded" in err_msg.lower():
            readable_msg = "Query execution timed out: maximum execution time limit of 3,000 ms (3 seconds) was exceeded."
        else:
            readable_msg = f"Operational Error ({errno}): {err_msg}"
            
        logger.warning("Custom query operational error: %s", readable_msg)
        return {
            "status": "error",
            "sql": validated_sql,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "execution_time_ms": elapsed_ms,
            "error": readable_msg,
        }

    except pymysql.err.ProgrammingError as prog_err:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        errno = prog_err.args[0] if prog_err.args else 0
        err_msg = prog_err.args[1] if len(prog_err.args) > 1 else str(prog_err)
        
        # MySQL error code 1142 is permission denied
        if errno == 1142 or "command denied" in err_msg.lower():
            readable_msg = f"Security Violation: Command denied for read-only user 'placement_readonly'. Write or administrative operations are prohibited."
        else:
            readable_msg = f"SQL Syntax / Database Error ({errno}): {err_msg}"
            
        logger.warning("Custom query programming error: %s", readable_msg)
        return {
            "status": "error",
            "sql": validated_sql,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "execution_time_ms": elapsed_ms,
            "error": readable_msg,
        }

    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        readable_msg = f"Database Error: {str(exc)}"
        logger.error("Custom query unhandled database error: %s", exc)
        return {
            "status": "error",
            "sql": validated_sql,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "execution_time_ms": elapsed_ms,
            "error": readable_msg,
        }

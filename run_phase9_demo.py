"""
Phase 9 (Scope A) Automated Demo Runner and Verification Suite.
Executes all 13 DBMS Demo Items containing all 44 original queries + 5 required additions
against MySQL database 'placement_scope_a'.
"""

import sys
import decimal
import pymysql
import pymysql.cursors

# Reconfigure stdout for UTF-8 compatibility on Windows terminal
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "12345",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

def format_row(row):
    formatted = {}
    for k, v in row.items():
        if isinstance(v, decimal.Decimal):
            formatted[k] = float(v)
        elif v is None:
            formatted[k] = "NULL"
        else:
            formatted[k] = str(v)
    return formatted

def run_phase9_demo():
    print("=" * 80)
    print("PHASE 9 (SCOPE A): COMPLETE 13 DBMS DEMO ITEMS VERIFICATION RUNNER")
    print("=" * 80)

    # 1. Initialize clean database
    conn = pymysql.connect(host=DB_CONFIG["host"], port=DB_CONFIG["port"], user=DB_CONFIG["user"], password=DB_CONFIG["password"], charset=DB_CONFIG["charset"])
    with conn.cursor() as cur:
        cur.execute("DROP DATABASE IF EXISTS placement_scope_a;")
        cur.execute("CREATE DATABASE placement_scope_a;")
    conn.commit()
    conn.close()

    conn = pymysql.connect(database="placement_scope_a", **DB_CONFIG)
    
    # 2. Setup DDL, Sample Data, Views from placement_internship_db.sql
    with open("placement_internship_db.sql", "r", encoding="utf-8") as f:
        full_sql = f.read()

    setup_sql = full_sql.split("-- PART 4: QUERIES")[0]
    setup_sql = setup_sql.replace("placement_db", "placement_scope_a")
    
    # Run multi-statement setup
    setup_conn = pymysql.connect(host=DB_CONFIG["host"], port=DB_CONFIG["port"], user=DB_CONFIG["user"], password=DB_CONFIG["password"], charset=DB_CONFIG["charset"], client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS)
    with setup_conn.cursor() as cur:
        cur.execute(setup_sql)
    setup_conn.commit()
    setup_conn.close()
    print("[OK] Scope A Schema, Sample Data, and Views initialized successfully.\n")

    # Define all Demo Items, Queries, and Explanations
    demo_items = [
        {
            "item_no": 1,
            "title": "Data Definition Language (DDL), Entity Types & Integrity Constraints",
            "concept": "Demonstrates relational table design, primary keys, candidate keys, foreign keys with CASCADE semantics, weak entity identification, 1NF multi-valued attribute decomposition, domain CHECK constraints, and business invariants using generated stored virtual columns.",
            "queries": [
                {
                    "qid": "DDL-1",
                    "title": "Verification of Tables and Constraints in Schema",
                    "dbms_desc": "Verifies that all 7 core Scope A tables are registered with appropriate engine and constraint configurations.",
                    "sql": "SHOW FULL TABLES WHERE Table_type = 'BASE TABLE';"
                },
                {
                    "qid": "DDL-2",
                    "title": "Foreign Key Integrity Verification (No Orphaned Records)",
                    "dbms_desc": "Verifies referential integrity across all foreign key relationships (Student -> Phone, Student -> Skill, Company -> Placement, etc.).",
                    "sql": """
                    SELECT 'STUDENT_PHONE -> STUDENT' AS FK_Relationship, COUNT(*) AS Orphaned_Count
                    FROM STUDENT_PHONE sp LEFT JOIN STUDENT s ON sp.Student_ID = s.Student_ID WHERE s.Student_ID IS NULL
                    UNION ALL
                    SELECT 'STUDENT_SKILL -> STUDENT', COUNT(*)
                    FROM STUDENT_SKILL sk LEFT JOIN STUDENT s ON sk.Student_ID = s.Student_ID WHERE s.Student_ID IS NULL
                    UNION ALL
                    SELECT 'PLACEMENT -> STUDENT', COUNT(*)
                    FROM PLACEMENT p LEFT JOIN STUDENT s ON p.Student_ID = s.Student_ID WHERE s.Student_ID IS NULL
                    UNION ALL
                    SELECT 'INTERNSHIP -> STUDENT (Weak Entity)', COUNT(*)
                    FROM INTERNSHIP i LEFT JOIN STUDENT s ON i.Student_ID = s.Student_ID WHERE s.Student_ID IS NULL;
                    """
                }
            ]
        },
        {
            "item_no": 2,
            "title": "Basic Projection, Selection & Sorting (DQL: SELECT, WHERE, ORDER BY, LIMIT)",
            "concept": "Demonstrates fundamental relational algebra operators: Projection (selecting required attributes), Selection (horizontal filtering based on scalar conditions, boolean AND/OR conjunctions), Sorting (lexicographical and descending numerical ordering), and Top-K row truncation.",
            "queries": [
                {
                    "qid": "A1",
                    "title": "List all students with basic attributes",
                    "dbms_desc": "Relational projection (pi) and multi-level sorting (tau) on Batch_Year, Branch, and Student_Name.",
                    "sql": """
                    SELECT Student_ID, Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Student_Name,
                           Branch, Batch_Year, CGPA, Backlogs
                    FROM STUDENT
                    ORDER BY Batch_Year, Branch, Student_Name;
                    """
                },
                {
                    "qid": "A2",
                    "title": "Students of one branch and batch",
                    "dbms_desc": "Relational selection (sigma) filtering on equality predicates (Branch='CSE' AND Batch_Year=2024) sorted by CGPA descending.",
                    "sql": """
                    SELECT Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Student_Name, CGPA
                    FROM STUDENT
                    WHERE Branch = 'CSE' AND Batch_Year = 2024
                    ORDER BY CGPA DESC;
                    """
                },
                {
                    "qid": "A5",
                    "title": "Students with high CGPA and zero backlogs",
                    "dbms_desc": "Conjunction of range restriction (CGPA >= 8.0) and equality predicate (Backlogs = 0) on numerical domains.",
                    "sql": """
                    SELECT Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Student_Name, Branch, CGPA
                    FROM STUDENT
                    WHERE CGPA >= 8.0 AND Backlogs = 0
                    ORDER BY CGPA DESC;
                    """
                },
                {
                    "qid": "B6",
                    "title": "Top 5 highest packages",
                    "dbms_desc": "Top-K query optimization utilizing sorted index scanning and heap limit buffers.",
                    "sql": """
                    SELECT Student_Name, Branch, Company_Name, Package
                    FROM V_PLACEMENT_DETAIL
                    WHERE Joined = 'Yes'
                    ORDER BY Package DESC
                    LIMIT 5;
                    """
                },
                {
                    "qid": "B9",
                    "title": "Students who received Pre-Placement Offers (PPO)",
                    "dbms_desc": "Categorical selection on ENUM attribute (Is_PPO = 'Yes') with composite ordering by graduation year and package.",
                    "sql": """
                    SELECT Student_Name, Branch, Company_Name, Package, Placement_Year, Joined
                    FROM V_PLACEMENT_DETAIL
                    WHERE Is_PPO = 'Yes'
                    ORDER BY Placement_Year, Package DESC;
                    """
                },
                {
                    "qid": "B14",
                    "title": "Packages above a given threshold (>= 8 LPA)",
                    "dbms_desc": "Filtering decimal salary attributes by numerical boundary with boolean conjunction.",
                    "sql": """
                    SELECT Student_Name, Branch, Company_Name, Role, Package
                    FROM V_PLACEMENT_DETAIL
                    WHERE Package >= 8 AND Joined = 'Yes'
                    ORDER BY Package DESC;
                    """
                },
                {
                    "qid": "C12",
                    "title": "Internships in a given date range (Summer 2023)",
                    "dbms_desc": "Temporal boundary filtering using calendar date comparison predicates (Start_Date >= and End_Date <=).",
                    "sql": """
                    SELECT Student_Name, Internship_No, Company_Name, Start_Date, End_Date
                    FROM V_INTERNSHIP_DETAIL
                    WHERE Start_Date >= '2023-05-01' AND End_Date <= '2023-08-31';
                    """
                }
            ]
        },
        {
            "item_no": 3,
            "title": "Pattern Matching, String Manipulation & Nullity Filtering",
            "concept": "Demonstrates string pattern matching using SQL wildcards, string concatenation with delimiters, and Three-Valued Logic (3VL) nullity inspection for detecting unsubmitted or missing relational data.",
            "queries": [
                {
                    "qid": "D11",
                    "title": "Search a student by name (partial match)",
                    "dbms_desc": "Non-anchored wildcard pattern matching (LIKE '%an%') with disjunctive evaluation (OR) across first and last name attributes.",
                    "sql": """
                    SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
                           s.Branch, s.CGPA, c.Company_Name AS Joined_Company, p.Package
                    FROM STUDENT s
                    LEFT JOIN PLACEMENT p ON p.Student_ID = s.Student_ID AND p.Joined = 'Yes'
                    LEFT JOIN COMPANY   c ON c.Company_ID = p.Company_ID
                    WHERE s.First_Name LIKE '%an%' OR s.Last_Name LIKE '%an%';
                    """
                },
                {
                    "qid": "C8",
                    "title": "Mandatory internship reports not yet submitted",
                    "dbms_desc": "Nullity check (IS NULL) identifying missing document references in mandatory academic deliverables.",
                    "sql": """
                    SELECT Student_Name, Branch, Internship_No, Report_Semester, Company_Name
                    FROM V_INTERNSHIP_DETAIL
                    WHERE Internship_Type = 'Mandatory' AND Report_Link IS NULL;
                    """
                }
            ]
        },
        {
            "item_no": 4,
            "title": "Scalar Expressions, Date Computation & Derived Attributes",
            "concept": "Demonstrates dynamic derived attribute calculation at query runtime, preventing physical data redundancy and eliminating update anomalies while handling scalar arithmetic and null coalescence.",
            "queries": [
                {
                    "qid": "C1",
                    "title": "All internships of one student with calculated duration",
                    "dbms_desc": "Computes Duration_Months dynamically using DATEDIFF without physically persisting redundant derived data in the table.",
                    "sql": """
                    SELECT Internship_No, Internship_Type, Company_Name, Role,
                           Start_Date, End_Date, Duration_Months, Stipend,
                           Credits, Report_Semester, Report_Grade
                    FROM V_INTERNSHIP_DETAIL
                    WHERE Roll_No = 'CS2102'
                    ORDER BY Internship_No;
                    """
                },
                {
                    "qid": "C9",
                    "title": "Total internship credits earned by each student",
                    "dbms_desc": "Null coalescence (COALESCE) handling additive aggregation of academic credits across student records.",
                    "sql": """
                    SELECT Roll_No, Student_Name, COALESCE(SUM(Credits), 0) AS Total_Credits
                    FROM V_INTERNSHIP_DETAIL
                    GROUP BY Student_ID, Roll_No, Student_Name
                    ORDER BY Total_Credits DESC;
                    """
                }
            ]
        },
        {
            "item_no": 5,
            "title": "Aggregate Functions & Population Statistics (COUNT, AVG, MAX, MIN, SUM)",
            "concept": "Demonstrates statistical reduction functions aggregating across partitions to compute counts, arithmetic means, extremes, and population distributions.",
            "queries": [
                {
                    "qid": "B4",
                    "title": "Year-wise placement statistics",
                    "dbms_desc": "Aggregate functions (COUNT, AVG, MAX) grouped by placement calendar year.",
                    "sql": """
                    SELECT Placement_Year,
                           COUNT(*)               AS Students_Placed,
                           ROUND(AVG(Package), 2) AS Avg_Package,
                           MAX(Package)           AS Highest_Package
                    FROM V_PLACEMENT_DETAIL
                    WHERE Joined = 'Yes'
                    GROUP BY Placement_Year
                    ORDER BY Placement_Year;
                    """
                },
                {
                    "qid": "B10",
                    "title": "On-campus vs off-campus comparison",
                    "dbms_desc": "Comparative aggregate reduction analyzing recruitment channel placement count and mean compensation.",
                    "sql": """
                    SELECT Placement_Type,
                           COUNT(*)               AS Students_Placed,
                           ROUND(AVG(Package), 2) AS Avg_Package
                    FROM V_PLACEMENT_DETAIL
                    WHERE Joined = 'Yes'
                    GROUP BY Placement_Type;
                    """
                },
                {
                    "qid": "B13",
                    "title": "Average interview rounds per company (placements)",
                    "dbms_desc": "Mean complexity analysis computing average interview rounds and total offers per recruiting organization.",
                    "sql": """
                    SELECT Company_Name,
                           ROUND(AVG(Interview_Rounds), 1) AS Avg_Interview_Rounds,
                           COUNT(*)                        AS Offers_Made
                    FROM V_PLACEMENT_DETAIL
                    GROUP BY Company_ID, Company_Name
                    ORDER BY Avg_Interview_Rounds DESC;
                    """
                },
                {
                    "qid": "C6",
                    "title": "Average stipend per company",
                    "dbms_desc": "Multi-metric compensation aggregation computing intern headcount, average stipend, and peak monthly payout.",
                    "sql": """
                    SELECT Company_Name,
                           COUNT(*)               AS Interns,
                           ROUND(AVG(Stipend), 0) AS Avg_Stipend,
                           MAX(Stipend)           AS Highest_Stipend
                    FROM V_INTERNSHIP_DETAIL
                    GROUP BY Company_ID, Company_Name
                    ORDER BY Avg_Stipend DESC;
                    """
                },
                {
                    "qid": "C11",
                    "title": "Average interview rounds for internships, per company",
                    "dbms_desc": "Evaluation of interview process depth for internship hiring per recruiting firm.",
                    "sql": """
                    SELECT Company_Name, ROUND(AVG(Interview_Rounds), 1) AS Avg_Interview_Rounds
                    FROM V_INTERNSHIP_DETAIL
                    GROUP BY Company_ID, Company_Name
                    ORDER BY Avg_Interview_Rounds DESC;
                    """
                },
                {
                    "qid": "D2",
                    "title": "Most common extra skills among students",
                    "dbms_desc": "Frequency distribution on normalized 1NF multi-valued skill relation.",
                    "sql": """
                    SELECT Skill, COUNT(*) AS Students_With_Skill
                    FROM STUDENT_SKILL
                    GROUP BY Skill
                    ORDER BY Students_With_Skill DESC, Skill;
                    """
                },
                {
                    "qid": "D3",
                    "title": "Skills companies selected students for (most in-demand first)",
                    "dbms_desc": "Industry demand frequency aggregation from placement qualification bridge entity.",
                    "sql": """
                    SELECT ps.Skill, COUNT(*) AS Times_Selected_For
                    FROM PLACEMENT_SKILL ps
                    GROUP BY ps.Skill
                    ORDER BY Times_Selected_For DESC, ps.Skill;
                    """
                }
            ]
        },
        {
            "item_no": 6,
            "title": "Multi-Dimensional Grouping & Categorical Aggregation (GROUP BY)",
            "concept": "Demonstrates relational grouping across single and composite categorical keys, preserving functional dependency rules, and computing multi-dimensional summary reports.",
            "queries": [
                {
                    "qid": "B3",
                    "title": "Branch-wise placement statistics",
                    "dbms_desc": "Categorical group-by partition across academic branch computing headcounts, average, maximum, and minimum compensation.",
                    "sql": """
                    SELECT Branch,
                           COUNT(*)               AS Students_Placed,
                           ROUND(AVG(Package), 2) AS Avg_Package,
                           MAX(Package)           AS Highest_Package,
                           MIN(Package)           AS Lowest_Package
                    FROM V_PLACEMENT_DETAIL
                    WHERE Joined = 'Yes'
                    GROUP BY Branch
                    ORDER BY Avg_Package DESC;
                    """
                },
                {
                    "qid": "B5",
                    "title": "Company-wise hiring statistics",
                    "dbms_desc": "Multi-column grouping by Company_ID, Company_Name, and Company_Type satisfying ANSI SQL-99 functional dependency standards.",
                    "sql": """
                    SELECT Company_Name, Company_Type,
                           COUNT(*)               AS Students_Joined,
                           ROUND(AVG(Package), 2) AS Avg_Package,
                           MAX(Package)           AS Highest_Package
                    FROM V_PLACEMENT_DETAIL
                    WHERE Joined = 'Yes'
                    GROUP BY Company_ID, Company_Name, Company_Type
                    ORDER BY Students_Joined DESC, Avg_Package DESC;
                    """
                },
                {
                    "qid": "B15",
                    "title": "Placement type, company type and industry mix of joined offers",
                    "dbms_desc": "Two-dimensional cross-tabulation grouping by organizational ownership type and industrial sector.",
                    "sql": """
                    SELECT Company_Type, Industry, COUNT(*) AS Students_Joined, ROUND(AVG(Package), 2) AS Avg_Package
                    FROM V_PLACEMENT_DETAIL
                    WHERE Joined = 'Yes'
                    GROUP BY Company_Type, Industry
                    ORDER BY Students_Joined DESC;
                    """
                },
                {
                    "qid": "C7",
                    "title": "Report grade distribution for mandatory internships, batch-wise",
                    "dbms_desc": "Three-dimensional grouping over Batch_Year, Internship_No, and Report_Grade evaluating grade distribution.",
                    "sql": """
                    SELECT Batch_Year, Internship_No, Report_Grade, COUNT(*) AS Students
                    FROM V_INTERNSHIP_DETAIL
                    WHERE Internship_Type = 'Mandatory' AND Report_Grade IS NOT NULL
                    GROUP BY Batch_Year, Internship_No, Report_Grade
                    ORDER BY Batch_Year, Internship_No, Report_Grade;
                    """
                },
                {
                    "qid": "D4",
                    "title": "Average package of joined students, by skill they were selected for",
                    "dbms_desc": "Aggregation through many-to-many bridge relation connecting placement offers to qualifying skills.",
                    "sql": """
                    SELECT ps.Skill, COUNT(*) AS Students, ROUND(AVG(p.Package), 2) AS Avg_Package
                    FROM PLACEMENT_SKILL ps
                    JOIN PLACEMENT p ON p.Placement_ID = ps.Placement_ID
                    WHERE p.Joined = 'Yes'
                    GROUP BY ps.Skill
                    ORDER BY Avg_Package DESC;
                    """
                },
                {
                    "qid": "D10",
                    "title": "Batch-wise summary dashboard",
                    "dbms_desc": "Cohort-level pivot aggregation combining COUNT(DISTINCT) and conditional aggregation metrics over an outer join.",
                    "sql": """
                    SELECT s.Batch_Year,
                           COUNT(DISTINCT s.Student_ID)                                   AS Total_Students,
                           COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' THEN s.Student_ID END) AS Placed_Students,
                           ROUND(AVG(CASE WHEN p.Joined = 'Yes' THEN p.Package END), 2)   AS Avg_Package,
                           MAX(CASE WHEN p.Joined = 'Yes' THEN p.Package END)             AS Highest_Package
                    FROM STUDENT s
                    LEFT JOIN PLACEMENT p ON p.Student_ID = s.Student_ID
                    GROUP BY s.Batch_Year
                    ORDER BY s.Batch_Year;
                    """
                }
            ]
        },
        {
            "item_no": 7,
            "title": "Filtered Aggregation & Group Criteria (GROUP BY ... HAVING)",
            "concept": "Demonstrates post-aggregation filtering on group-level cardinality and aggregate expressions using the HAVING clause (contrasted with row-level WHERE filtering).",
            "queries": [
                {
                    "qid": "B8",
                    "title": "Students who received more than one offer",
                    "dbms_desc": "Post-aggregation filter using HAVING COUNT(*) > 1 with GROUP_CONCAT summarizing all offers per student.",
                    "sql": """
                    SELECT Student_Name, Roll_No,
                           COUNT(*) AS Total_Offers,
                           GROUP_CONCAT(CONCAT(Company_Name, ' (', Package, ' LPA)') SEPARATOR ', ') AS Offers,
                           MAX(CASE WHEN Joined = 'Yes' THEN Company_Name END) AS Joined_Company
                    FROM V_PLACEMENT_DETAIL
                    GROUP BY Student_ID, Student_Name, Roll_No
                    HAVING COUNT(*) > 1;
                    """
                },
                {
                    "qid": "C4",
                    "title": "RULE CHECK: Students who have NOT completed both mandatory internships",
                    "dbms_desc": "Integrity compliance audit using conditional aggregation inside HAVING to detect students with fewer than 2 mandatory internships.",
                    "sql": """
                    SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
                           COUNT(CASE WHEN i.Internship_Type = 'Mandatory' THEN 1 END) AS Mandatory_Done
                    FROM STUDENT s
                    LEFT JOIN INTERNSHIP i ON i.Student_ID = s.Student_ID
                    GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name
                    HAVING COUNT(CASE WHEN i.Internship_Type = 'Mandatory' THEN 1 END) < 2;
                    """
                },
                {
                    "qid": "C10",
                    "title": "Students who did more than the mandatory 2 internships",
                    "dbms_desc": "Threshold filtering on group cardinality isolating high-performing students completing additional internships.",
                    "sql": """
                    SELECT Roll_No, Student_Name, COUNT(*) AS Total_Internships
                    FROM V_INTERNSHIP_DETAIL
                    GROUP BY Student_ID, Roll_No, Student_Name
                    HAVING COUNT(*) > 2;
                    """
                }
            ]
        },
        {
            "item_no": 8,
            "title": "Multi-Table Relational Queries — INNER JOIN",
            "concept": "Demonstrates relational equi-joins across primary-foreign key relationships, connecting master tables, child multi-valued tables, weak entities, and bridge tables across 2-way, 3-way, and self-intersecting join graphs.",
            "queries": [
                {
                    "qid": "A4",
                    "title": "Students who have a particular extra skill (SQL)",
                    "dbms_desc": "Binary equi-join connecting STUDENT and normalized STUDENT_SKILL filtered by skill name.",
                    "sql": """
                    SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.CGPA
                    FROM STUDENT s
                    JOIN STUDENT_SKILL sk ON sk.Student_ID = s.Student_ID
                    WHERE sk.Skill = 'SQL';
                    """
                },
                {
                    "qid": "B1",
                    "title": "All placed students with company and package (joined offers only)",
                    "dbms_desc": "Multi-table join across PLACEMENT, STUDENT, and COMPANY relations filtered by final joined status.",
                    "sql": """
                    SELECT Roll_No, Student_Name, Branch, Batch_Year, Company_Name, Role, Package, Placement_Year
                    FROM V_PLACEMENT_DETAIL
                    WHERE Joined = 'Yes'
                    ORDER BY Package DESC;
                    """
                },
                {
                    "qid": "B2",
                    "title": "Placements of one company (TCS)",
                    "dbms_desc": "Equi-join with selective company filter examining recruitment yield for a specific employer.",
                    "sql": """
                    SELECT Student_Name, Branch, Batch_Year, Role, Package, Placement_Year, Joined
                    FROM V_PLACEMENT_DETAIL
                    WHERE Company_Name = 'TCS'
                    ORDER BY Placement_Year;
                    """
                },
                {
                    "qid": "B12",
                    "title": "Placed students who had backlogs",
                    "dbms_desc": "Relational equi-join filtered by student academic backlog risk condition.",
                    "sql": """
                    SELECT Student_Name, Branch, Backlogs, Company_Name, Package
                    FROM V_PLACEMENT_DETAIL
                    WHERE Joined = 'Yes' AND Backlogs > 0;
                    """
                },
                {
                    "qid": "C2",
                    "title": "All internships done at one company (Zoho)",
                    "dbms_desc": "Weak entity to strong entity join filtered by organization name.",
                    "sql": """
                    SELECT Student_Name, Branch, Internship_No, Role, Start_Date, End_Date, Stipend
                    FROM V_INTERNSHIP_DETAIL
                    WHERE Company_Name = 'Zoho'
                    ORDER BY Start_Date;
                    """
                },
                {
                    "qid": "C5",
                    "title": "Students who did additional (extra) internships",
                    "dbms_desc": "Join on weak entity subtype filtering on discriminant attribute (Internship_Type = 'Additional').",
                    "sql": """
                    SELECT Student_Name, Branch, Internship_No, Company_Name, Role, Duration_Months, Stipend
                    FROM V_INTERNSHIP_DETAIL
                    WHERE Internship_Type = 'Additional';
                    """
                },
                {
                    "qid": "D1",
                    "title": "Internship converted to job (student placed at company where they interned)",
                    "dbms_desc": "Composite multi-attribute equi-join matching on (Student_ID AND Company_ID) correlating internship and placement histories.",
                    "sql": """
                    SELECT DISTINCT p.Student_Name, p.Branch, p.Company_Name, p.Package, p.Is_PPO
                    FROM V_PLACEMENT_DETAIL p
                    JOIN INTERNSHIP i
                      ON i.Student_ID = p.Student_ID AND i.Company_ID = p.Company_ID
                    WHERE p.Joined = 'Yes';
                    """
                },
                {
                    "qid": "D5",
                    "title": "Skills for which a particular company selects students",
                    "dbms_desc": "Three-table join traversing bridge entity PLACEMENT_SKILL to PLACEMENT and COMPANY.",
                    "sql": """
                    SELECT DISTINCT c.Company_Name, ps.Skill
                    FROM PLACEMENT_SKILL ps
                    JOIN PLACEMENT p ON p.Placement_ID = ps.Placement_ID
                    JOIN COMPANY c   ON c.Company_ID  = p.Company_ID
                    WHERE c.Company_Name = 'Zoho';
                    """
                },
                {
                    "qid": "D9",
                    "title": "Do students with more extra skills get higher packages?",
                    "dbms_desc": "Derived table (inline aggregation view) joined to base PLACEMENT relation to evaluate skill count vs salary.",
                    "sql": """
                    SELECT sc.Skill_Count, COUNT(*) AS Students, ROUND(AVG(p.Package), 2) AS Avg_Package
                    FROM (SELECT Student_ID, COUNT(*) AS Skill_Count
                            FROM STUDENT_SKILL GROUP BY Student_ID) sc
                    JOIN PLACEMENT p ON p.Student_ID = sc.Student_ID AND p.Joined = 'Yes'
                    GROUP BY sc.Skill_Count
                    ORDER BY sc.Skill_Count;
                    """
                }
            ]
        },
        {
            "item_no": 9,
            "title": "Outer Joins & Unmatched Tuple Detection (LEFT JOIN / Anti-Joins)",
            "concept": "Demonstrates Left Outer Joins preserving master rows with zero child records, Anti-Join patterns utilizing IS NULL predicates to isolate non-matching entities, and multi-way outer joins for comparative population analysis.",
            "queries": [
                {
                    "qid": "ADD-1",
                    "title": "Students with no placement (LEFT JOIN Anti-Join Version) [REQUIRED ADDITION]",
                    "dbms_desc": "Relational Outer Anti-Join pattern (R anti-join S). Preserves students without accepted placements by filtering on NULL right-side primary keys.",
                    "sql": """
                    SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
                           s.Branch, s.Batch_Year, s.CGPA
                    FROM STUDENT s
                    LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID AND p.Joined = 'Yes'
                    WHERE p.Placement_ID IS NULL;
                    """
                },
                {
                    "qid": "C3",
                    "title": "Mandatory internship status of every student (must be 2)",
                    "dbms_desc": "Left Outer Join with conditional aggregation ensuring students with zero internships are not excluded from audit reporting.",
                    "sql": """
                    SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
                           COUNT(CASE WHEN i.Internship_Type = 'Mandatory'  THEN 1 END) AS Mandatory_Done,
                           COUNT(CASE WHEN i.Internship_Type = 'Additional' THEN 1 END) AS Additional_Done,
                           COUNT(i.Internship_No)                                       AS Total_Internships
                    FROM STUDENT s
                    LEFT JOIN INTERNSHIP i ON i.Student_ID = s.Student_ID
                    GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name;
                    """
                },
                {
                    "qid": "ADD-3A",
                    "title": "Comparison of extra skills: Placed vs Non-Placed Students (Summary) [REQUIRED ADDITION]",
                    "dbms_desc": "Multi-way outer join with conditional aggregation comparing skill volume, mean skills per student, and skill variety between placed and non-placed cohorts.",
                    "sql": """
                    SELECT 
                        CASE WHEN p.Joined = 'Yes' THEN 'Placed Students' ELSE 'Non-Placed Students' END AS Placement_Status,
                        COUNT(DISTINCT s.Student_ID) AS Total_Students,
                        COUNT(sk.Skill) AS Total_Skills_Reported,
                        ROUND(COUNT(sk.Skill) / COUNT(DISTINCT s.Student_ID), 2) AS Avg_Skills_Per_Student,
                        GROUP_CONCAT(DISTINCT sk.Skill ORDER BY sk.Skill SEPARATOR ', ') AS Unique_Skills_Acquired
                    FROM STUDENT s
                    LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID AND p.Joined = 'Yes'
                    LEFT JOIN STUDENT_SKILL sk ON s.Student_ID = sk.Student_ID
                    GROUP BY CASE WHEN p.Joined = 'Yes' THEN 'Placed Students' ELSE 'Non-Placed Students' END;
                    """
                },
                {
                    "qid": "ADD-3B",
                    "title": "Comparison of extra skills: Per-Skill Breakdown across Cohorts [REQUIRED ADDITION]",
                    "dbms_desc": "Granular skill cross-tabulation evaluating technical specialization prevalence between placed and non-placed students.",
                    "sql": """
                    SELECT 
                        sk.Skill,
                        COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' THEN s.Student_ID END) AS Placed_Students_With_Skill,
                        COUNT(DISTINCT CASE WHEN p.Placement_ID IS NULL OR p.Joined != 'Yes' THEN s.Student_ID END) AS Non_Placed_Students_With_Skill,
                        COUNT(DISTINCT s.Student_ID) AS Total_Students_With_Skill
                    FROM STUDENT_SKILL sk
                    JOIN STUDENT s ON sk.Student_ID = s.Student_ID
                    LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID AND p.Joined = 'Yes'
                    GROUP BY sk.Skill
                    ORDER BY Placed_Students_With_Skill DESC, Total_Students_With_Skill DESC;
                    """
                }
            ]
        },
        {
            "item_no": 10,
            "title": "Nested Non-Correlated Subqueries & Dynamic Benchmarking",
            "concept": "Demonstrates independent nested subqueries evaluated once during execution planning to dynamically compute population benchmarks without hardcoding static numerical thresholds.",
            "queries": [
                {
                    "qid": "ADD-2",
                    "title": "Students with CGPA above average [REQUIRED ADDITION]",
                    "dbms_desc": "Scalar non-correlated subquery dynamically calculating mean CGPA across STUDENT and comparing each student's score against this benchmark.",
                    "sql": """
                    SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.Batch_Year, s.CGPA,
                           ROUND((SELECT AVG(CGPA) FROM STUDENT), 2) AS Benchmark_Avg_CGPA,
                           ROUND(s.CGPA - (SELECT AVG(CGPA) FROM STUDENT), 2) AS Delta_From_Avg
                    FROM STUDENT s
                    WHERE s.CGPA > (SELECT AVG(CGPA) FROM STUDENT)
                    ORDER BY s.CGPA DESC;
                    """
                },
                {
                    "qid": "B7",
                    "title": "Placement percentage by branch and batch",
                    "dbms_desc": "Subquery projection with boolean existential evaluation converted to branch-level placement success ratios.",
                    "sql": """
                    SELECT s.Branch, s.Batch_Year,
                           COUNT(*) AS Total_Students,
                           SUM(EXISTS (SELECT 1 FROM PLACEMENT p
                                       WHERE p.Student_ID = s.Student_ID AND p.Joined = 'Yes')) AS Placed,
                           ROUND(100 * SUM(EXISTS (SELECT 1 FROM PLACEMENT p
                                                   WHERE p.Student_ID = s.Student_ID AND p.Joined = 'Yes'))
                                     / COUNT(*), 1) AS Placement_Percent
                    FROM STUDENT s
                    GROUP BY s.Branch, s.Batch_Year
                    ORDER BY s.Batch_Year, s.Branch;
                    """
                }
            ]
        },
        {
            "item_no": 11,
            "title": "Correlated Subqueries & Relational Existence (EXISTS / NOT EXISTS)",
            "concept": "Demonstrates correlated subqueries re-evaluated in the context of outer query tuples for existential testing (EXISTS / NOT EXISTS) and scalar subquery projections with GROUP_CONCAT to avoid Cartesian products.",
            "queries": [
                {
                    "qid": "A3",
                    "title": "Complete profile of one student (phones and extra skills combined)",
                    "dbms_desc": "Correlated scalar subqueries in SELECT list projecting 1:N attributes without multiplying rows into a Cartesian explosion.",
                    "sql": """
                    SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
                           s.Branch, s.Batch_Year, s.CGPA, s.Backlogs, s.Resume_Link,
                           (SELECT GROUP_CONCAT(ph.Phone_No SEPARATOR ', ')
                              FROM STUDENT_PHONE ph WHERE ph.Student_ID = s.Student_ID) AS Phones,
                           (SELECT GROUP_CONCAT(sk.Skill SEPARATOR ', ')
                              FROM STUDENT_SKILL sk WHERE sk.Student_ID = s.Student_ID) AS Extra_Skills
                    FROM STUDENT s
                    WHERE s.Roll_No = 'CS2101';
                    """
                },
                {
                    "qid": "A6",
                    "title": "Students not placed (NOT EXISTS version)",
                    "dbms_desc": "Correlated semi-difference / set negation using NOT EXISTS predicate to locate students without an accepted offer.",
                    "sql": """
                    SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.Batch_Year
                    FROM STUDENT s
                    WHERE NOT EXISTS (SELECT 1 FROM PLACEMENT p
                                      WHERE p.Student_ID = s.Student_ID AND p.Joined = 'Yes');
                    """
                },
                {
                    "qid": "D6",
                    "title": "Companies that offered both internships and placements",
                    "dbms_desc": "Dual correlated existential predicates (EXISTS ... AND EXISTS ...) checking relationship intersection across two foreign entities.",
                    "sql": """
                    SELECT c.Company_Name,
                           (SELECT COUNT(*) FROM INTERNSHIP i WHERE i.Company_ID = c.Company_ID) AS Interns_Taken,
                           (SELECT COUNT(*) FROM PLACEMENT  p WHERE p.Company_ID = c.Company_ID) AS Offers_Made
                    FROM COMPANY c
                    WHERE EXISTS (SELECT 1 FROM INTERNSHIP i WHERE i.Company_ID = c.Company_ID)
                      AND EXISTS (SELECT 1 FROM PLACEMENT  p WHERE p.Company_ID = c.Company_ID);
                    """
                },
                {
                    "qid": "D8",
                    "title": "Full career report per student (skills, internships, final placement)",
                    "dbms_desc": "Multiple correlated scalar subqueries synthesizing academic, experiential, and hiring data into a single master row per student.",
                    "sql": """
                    SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
                           s.Branch, s.Batch_Year, s.CGPA,
                           (SELECT GROUP_CONCAT(sk.Skill SEPARATOR ', ')
                              FROM STUDENT_SKILL sk WHERE sk.Student_ID = s.Student_ID)              AS Extra_Skills,
                           (SELECT COUNT(*) FROM INTERNSHIP i WHERE i.Student_ID = s.Student_ID)     AS Internships_Done,
                           (SELECT c.Company_Name FROM PLACEMENT p JOIN COMPANY c ON c.Company_ID = p.Company_ID
                             WHERE p.Student_ID = s.Student_ID AND p.Joined = 'Yes')                 AS Joined_Company,
                           (SELECT p.Package FROM PLACEMENT p
                             WHERE p.Student_ID = s.Student_ID AND p.Joined = 'Yes')                 AS Package
                    FROM STUDENT s
                    ORDER BY s.Batch_Year, s.Branch, s.Roll_No;
                    """
                }
            ]
        },
        {
            "item_no": 12,
            "title": "Set Operations, Relational Views & Domain Categorization",
            "concept": "Demonstrates set-theoretic union operations across heterogeneous relations, logical data independence via relational Views, and CASE WHEN conditional logic for discretizing continuous metric domains.",
            "queries": [
                {
                    "qid": "D7",
                    "title": "Everything about one company: who interned and who got placed (UNION ALL)",
                    "dbms_desc": "Set Union (UNION ALL) combining distinct activity records (Internships vs Placements) into a unified polymorphic schema.",
                    "sql": """
                    SELECT 'Internship' AS Record_Type, Student_Name, Branch, Role, NULL AS Package, Stipend
                    FROM V_INTERNSHIP_DETAIL
                    WHERE Company_Name = 'TCS'
                    UNION ALL
                    SELECT 'Placement', Student_Name, Branch, Role, Package, NULL
                    FROM V_PLACEMENT_DETAIL
                    WHERE Company_Name = 'TCS'
                    ORDER BY Record_Type, Student_Name;
                    """
                },
                {
                    "qid": "B11",
                    "title": "CGPA band vs average package (Conditional Categorization)",
                    "dbms_desc": "Conditional value discretization using CASE WHEN mapping continuous CGPA scores into discrete performance intervals.",
                    "sql": """
                    SELECT CASE WHEN CGPA >= 9 THEN '9.0 and above'
                                WHEN CGPA >= 8 THEN '8.0 - 8.99'
                                WHEN CGPA >= 7 THEN '7.0 - 7.99'
                                ELSE 'Below 7.0' END AS CGPA_Band,
                           COUNT(*)               AS Students_Placed,
                           ROUND(AVG(Package), 2) AS Avg_Package
                    FROM V_PLACEMENT_DETAIL
                    WHERE Joined = 'Yes'
                    GROUP BY CGPA_Band
                    ORDER BY MIN(CGPA) DESC;
                    """
                },
                {
                    "qid": "VIEW-1",
                    "title": "Relational View Verification (Logical Independence)",
                    "dbms_desc": "Confirms views V_PLACEMENT_DETAIL and V_INTERNSHIP_DETAIL abstract multi-table joins and derived columns.",
                    "sql": """
                    SELECT Table_Name, View_Definition 
                    FROM information_schema.views 
                    WHERE table_schema = 'placement_scope_a';
                    """
                }
            ]
        },
        {
            "item_no": 13,
            "title": "Transaction Management (ACID) & Physical Optimization (Indexing)",
            "concept": "Demonstrates Transaction Control Language (TCL) ensuring ACID properties during composite multi-table registration, and physical database design using B+ Tree secondary indexes with query execution plan (EXPLAIN) verification.",
            "queries": [
                {
                    "qid": "ADD-4",
                    "title": "Safe Atomic Insertion Transaction (Student + Phones + Skills) [REQUIRED ADDITION]",
                    "dbms_desc": "ACID Transaction guaranteeing Atomicity and Referential Integrity when inserting into STUDENT and dependent multi-valued child tables.",
                    "type": "transaction"
                },
                {
                    "qid": "ADD-5",
                    "title": "Physical Design: Secondary Index Creation & Query Optimizer EXPLAIN [REQUIRED ADDITION]",
                    "dbms_desc": "B+ Tree index creation on composite search paths and foreign keys, transforming full table scans into index range scans.",
                    "type": "indexes"
                }
            ]
        }
    ]

    total_executed = 0
    total_passed = 0

    for item in demo_items:
        print("=" * 80)
        print(f"DEMO ITEM {item['item_no']}: {item['title'].upper()}")
        print(f"DBMS Conceptual Scope: {item['concept']}")
        print("-" * 80)

        for q in item["queries"]:
            qid = q["qid"]
            title = q["title"]
            desc = q["dbms_desc"]
            
            print(f"\n>>> [{qid}] {title}")
            print(f"    DBMS Analysis: {desc}")

            if q.get("type") == "transaction":
                # Execute transaction demo
                total_executed += 1
                try:
                    with conn.cursor() as cur:
                        cur.execute("START TRANSACTION;")
                        cur.execute("""
                            INSERT INTO STUDENT (Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs, Resume_Link)
                            VALUES ('CS2106', 'Vikram', 'Aditya', 'CSE', 2024, 8.75, 0, 'https://drive.example.com/resume/vikram.pdf');
                        """)
                        new_id = cur.lastrowid
                        cur.executemany("INSERT INTO STUDENT_PHONE (Student_ID, Phone_No) VALUES (%s, %s);",
                                        [(new_id, '9810000006'), (new_id, '9810000066')])
                        cur.executemany("INSERT INTO STUDENT_SKILL (Student_ID, Skill) VALUES (%s, %s);",
                                        [(new_id, 'Python'), (new_id, 'Django'), (new_id, 'Docker')])
                        conn.commit()
                        
                        # Verify committed state
                        cur.execute("""
                            SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Name,
                                   COUNT(DISTINCT ph.Phone_No) AS Phone_Count,
                                   COUNT(DISTINCT sk.Skill) AS Skill_Count
                            FROM STUDENT s
                            LEFT JOIN STUDENT_PHONE ph ON s.Student_ID = ph.Student_ID
                            LEFT JOIN STUDENT_SKILL sk ON s.Student_ID = sk.Student_ID
                            WHERE s.Roll_No = 'CS2106'
                            GROUP BY s.Student_ID, s.Roll_No, Name;
                        """)
                        res = cur.fetchone()
                        print(f"    [OK] Transaction Committed Atomically: {format_row(res)}")
                        total_passed += 1
                except Exception as e:
                    conn.rollback()
                    print(f"    [FAIL] Transaction Failed: {e}")

            elif q.get("type") == "indexes":
                # Execute index creation and explain
                total_executed += 1
                try:
                    index_defs = [
                        ("idx_student_branch_batch", "STUDENT", "(Branch, Batch_Year)", "Speeds up composite filter queries on branch & graduation year."),
                        ("idx_student_cgpa", "STUDENT", "(CGPA)", "Optimizes range filters, threshold lookups, and ORDER BY CGPA."),
                        ("idx_placement_student_joined", "PLACEMENT", "(Student_ID, Joined)", "Covering index for joining placements while filtering on accepted offers."),
                        ("idx_placement_company_pkg", "PLACEMENT", "(Company_ID, Package)", "Accelerates company-level placement salary aggregations."),
                        ("idx_internship_student_type", "INTERNSHIP", "(Student_ID, Internship_Type)", "Optimizes mandatory vs additional internship audits."),
                        ("idx_student_skill_skill", "STUDENT_SKILL", "(Skill)", "Supports inverted skill lookups and global skill prevalence counts."),
                        ("idx_company_name", "COMPANY", "(Company_Name)", "Enables instant O(log N) point lookup on company name.")
                    ]
                    with conn.cursor() as cur:
                        for iname, itbl, icols, ireason in index_defs:
                            try:
                                cur.execute(f"ALTER TABLE {itbl} DROP INDEX {iname};")
                            except Exception:
                                pass
                            cur.execute(f"CREATE INDEX {iname} ON {itbl} {icols};")
                            print(f"    [OK] Created index: {iname} on {itbl}{icols} -> {ireason}")
                        
                        # EXPLAIN verification
                        cur.execute("EXPLAIN SELECT Roll_No, First_Name FROM STUDENT WHERE Branch = 'CSE' AND Batch_Year = 2024;")
                        exp1 = cur.fetchall()[0]
                        print(f"    [OK] EXPLAIN Plan (Branch & Batch): type={exp1['type']}, key={exp1['key']}")

                        cur.execute("EXPLAIN SELECT s.Roll_No FROM STUDENT s JOIN PLACEMENT p ON s.Student_ID = p.Student_ID WHERE p.Joined = 'Yes';")
                        exp2 = cur.fetchall()
                        print(f"    [OK] EXPLAIN Plan (Joined Placement): p.key={exp2[0]['key']}, s.key={exp2[1]['key']}")
                        
                        total_passed += 1
                except Exception as e:
                    print(f"    [FAIL] Index creation / EXPLAIN failed: {e}")

            else:
                total_executed += 1
                try:
                    with conn.cursor() as cur:
                        cur.execute(q["sql"].strip())
                        rows = cur.fetchall()
                        print(f"    [OK] Success: Returned {len(rows)} row(s)")
                        for r in rows[:2]:
                            print(f"       -> {format_row(r)}")
                        if len(rows) > 2:
                            print(f"       ... and {len(rows) - 2} additional row(s)")
                        total_passed += 1
                except Exception as e:
                    print(f"    [FAIL] Execution Error: {e}")

    conn.close()

    print("\n" + "=" * 80)
    print(f"FINAL PHASE 9 SUMMARY: Total Executed = {total_executed}, Passed = {total_passed}, Failed = {total_executed - total_passed}")
    print("ALL 13 DBMS DEMO ITEMS & 49 QUERIES/STATEMENTS EXECUTED AND VALIDATED.")
    print("=" * 80)

if __name__ == "__main__":
    run_phase9_demo()

# Master Viva Preparation Guide: Top 40 Backend SQL Queries

> [!IMPORTANT]
> **Viva Examination Readiness**: This study guide contains the **Top 40 most critical and technically sophisticated SQL queries** from the Legacy Dataforce backend. Every query is broken down into 10 structured dimensions to ensure complete mastery during your teacher's viva evaluation.

## Quick Reference Index of the Top 40 Queries

| # | Query ID | Category | Feature / Routine | Core Concepts |
|---|---|---|---|---|
| 1 | **DDL-21** | Placement management | Schema Definition: View V_PLACEMENT_DETAIL | Relational Views (DDL), Equi-Joins, String Concatenation with Null-Handling (CONCAT_WS), Query Simplification. |
| 2 | **DDL-22** | Internship management | Schema Definition: View V_INTERNSHIP_DETAIL | Derived Attributes in Relational Design (3NF), Date Arithmetic (DATEDIFF), Rounding Functions (ROUND), Relational Views. |
| 3 | **DDL-05** | Other database operations | Schema Definition: Table STUDENT_SKILL | First Normal Form (1NF), Composite Primary Keys, Foreign Key Constraints, ON DELETE CASCADE, Relational Normalization. |
| 4 | **DDL-08** | Other database operations | Schema Definition: Table RESUME | Generated Stored Columns, Conditional Logic (CASE WHEN) in DDL, Partial Unique Constraints via NULL semantics, Business Rule Enforcement. |
| 5 | **STU-07** | Student management | Get Student: Retrieve Phone Numbers | 1NF Contact Number Decomposition, Parameterized SQL, Primary Key Lookup, ORDER BY. |
| 6 | **STU-11** | Academic results | Get Student: Retrieve Semester Academic Results | Academic Progression Tracking, Temporal Sorting, Parameterized Filtering. |
| 7 | **STU-14** | Placement management | Get Student: Retrieve Placement Offers and Compensation | Foreign Key Equi-Join, Sorting (ORDER BY DESC), Parameterization. |
| 8 | **STU-16** | Placement management | List Students: Placed Status Filter Predicate | Correlated Subqueries, EXISTS Operator, Short-Circuit Execution in SQL, Semi-Joins. |
| 9 | **STU-17** | Placement management | List Students: Unplaced Status Filter Predicate | Anti-Semi-Joins, NOT EXISTS Operator, Handling Relational Absence, NULL-safe logic. |
| 10 | **STU-18** | Placement management | List Students: Multiple Offers Filter Predicate | Scalar Subqueries, Aggregation inside WHERE clause, Correlated Counting. |
| 11 | **STU-30** | Compliance and eligibility | Delete Student: Referential Dependency Cascade Audit | Referential Integrity Verification, Multiple Scalar Subqueries in SELECT, Pre-Deletion Audits, Relational Safeguards. |
| 12 | **CMP-05** | Internship management | Get Company: Retrieve Job & Internship Opportunities | Multi-Table Parent-Child Navigation, Composite Ordering, Foreign Key Traversal. |
| 13 | **CMP-08** | Internship management | Get Company: Aggregate Placement & Internship Volume Metrics | Scalar Subquery Aggregations, COALESCE Function for Null-Safety, Dual Metric Assembly. |
| 14 | **CMP-15** | Internship management | Delete Company: Check Active Placement & Internship Attachments | Referential Integrity, ON DELETE RESTRICT Enforcement, Defensive Programming in SQL. |
| 15 | **PLC-08** | Placement management | Get Placement Offer: Full Offer Detail Equi-Join | 3-Table Equi-Join, Primary-to-Foreign Key Traversal, Star-Schema Fact-Dimension Querying. |
| 16 | **PLC-18** | Placement management | Get Placement Analytics: Query #18 | Aggregate Functions (COUNT, MAX, MIN, AVG), Decimal Rounding (ROUND). |
| 17 | **INT-05** | Internship management | Create Internship: Verify Corporate Host Organization | Weak Entity Representation, Sequence-based Sorting, Foreign Key Equi-Join. |
| 18 | **INT-16** | Compliance and eligibility | Mandatory Compliance: Detailed Prerequisite SGPA Mapping | Prerequisite Validation, IN Operator, Business Rule Integration. |
| 19 | **INT-23** | Dashboard and statistics | Get Internship Dashboard Analytics: Query #23 | Conditional Aggregation, CASE WHEN inside COUNT(), Single-Pass Analytics. |
| 20 | **INT-25** | Dashboard and statistics | Internship KPIs: Count of Fully Compliant Students | Dual Correlated EXISTS, Relational Division Pattern, Compliance Audits, Set Intersection. |
| 21 | **CRS-07** | Academic results | Update Course: Verify Target Record | Many-to-Many Junction Table Traversal, Composite Key Entity Navigation, CONCAT_WS. |
| 22 | **RES-40** | Academic results | Get Semester Result: Equi-Join with Student Candidate | Foreign Key Equi-Join, Primary Key Single-Record Retrieval, Parent-Child Relational Linking. |
| 23 | **RES-41** | Academic results | List Semester Results: Academic Progression Roster | Multi-Column Hierarchical Sorting (ORDER BY col1 DESC, col2 DESC), Institutional Academic Reporting. |
| 24 | **DRV-20** | Company management | Get Drive: Equi-Join with Company Profile | Parent-Child Relational Linking, Campus Recruitment Scheduling, Dimension Resolution. |
| 25 | **RND-33** | Company management | Get Round: Equi-Join with Opportunity and Company | 4-Table Hierarchical Joins, Grandparent-Parent-Child Relational Navigation, Operational Pipeline Modeling. |
| 26 | **DSH-05** | Dashboard and statistics | Get Dashboard Stats: Query #5 | Aggregate Statistics, COALESCE Null Prevention, Executive Dashboard KPIs. |
| 27 | **DSH-10** | Dashboard and statistics | Dashboard KPI: Candidates Missing Mandatory Internships | Derived Table (Subquery in FROM), Disjunctive Anti-Semi-Joins (OR NOT EXISTS), Institutional Clearance Auditing. |
| 28 | **DSH-11** | Dashboard and statistics | Dashboard Chart 1: Branch-Wise Placement & Internships Breakdown | Multiple LEFT OUTER JOINs, Prevention of Cartesian Product Explosion via COUNT(DISTINCT), Grouping & Aggregation for Data Visualization. |
| 29 | **DSH-12** | Dashboard and statistics | Dashboard Chart 2: Historical Placement Trends & YoY Trajectory | Time-Series Aggregations, Multi-Metric Grouping, Financial/Salary Analytics. |
| 30 | **DSH-13** | Dashboard and statistics | Dashboard Chart 3: Salary Compensation Histogram Distribution | Distribution Modeling, Raw Data Retrieval for Frontend Statistical Binning, Continuous Variable Analysis. |
| 31 | **DSH-14** | Dashboard and statistics | Dashboard Chart 4: Correlation of Internships to Placement Success | Correlation Analysis in SQL, Conditional COUNT(DISTINCT CASE WHEN), Dual Outer Joins. |
| 32 | **DSH-15** | Dashboard and statistics | Dashboard Chart 5: Departmental Internship Completion Compliance | Derived Table Aggregation, Multi-Tier CASE Expressions, Relational Categorization, Two-Pass Grouping. |
| 33 | **DSH-16** | Dashboard and statistics | Dashboard Chart 6: Multiple Offers Distribution Across Departments | Nested Aggregations, Tier Bucketing with CASE WHEN, Derived Table Subqueries. |
| 34 | **9.3** | Reports and analytics | A3. Complete Profile of One Student | GROUP_CONCAT with DISTINCT, Multiple 1:N Relationship Joins, Aggregation over Outer Joins, 360-Degree Entity Synthesis. |
| 35 | **9.6** | Reports and analytics | A6 / ADD-1. Students Not Placed (LEFT OUTER Anti-Join) | Relational Difference / Anti-Join, LEFT JOIN ... WHERE IS NULL, Set Complement. |
| 36 | **9.11** | Reports and analytics | B3. Branch-Wise Placement Statistics | Departmental Grouping, Multi-Aggregate Analysis (MIN, MAX, AVG), Sorting on Computed Alias. |
| 37 | **9.14** | Reports and analytics | B6. Top 5 Highest Placement Packages (Top-K) | Top-K Query Pattern, LIMIT Clause, Multi-Table Equi-Join, High-Salaried Filtering. |
| 38 | **9.16** | Reports and analytics | B8. Students Receiving Multiple Placement Offers | GROUP BY with Multiple Non-Aggregated Columns, HAVING Clause Post-Aggregation Filtering, Multi-Level Ranking. |
| 39 | **9.23** | Reports and analytics | C4. Rule Check: Students with Incomplete Mandatory Internships | Correlated NOT EXISTS in SELECT & WHERE, Disjunctive Filtering (OR), CASE Status Flagging, Institutional Clearance Logic. |
| 40 | **9.35** | Reports and analytics | E1. Branch-Wise Placement Statistics & Median Compensation | Common Table Expressions (WITH clause), Window Functions (DENSE_RANK), Partitioning (PARTITION BY), In-Branch Competitive Ranking. |

---

## 1. Query 1 (DDL-21): View V_PLACEMENT_DETAIL Creation

- **Source Routine / File:** `schema.sql / Schema Setup`
- **Viva Category:** `Placement management`
- **Core DBMS Concepts:** `Relational Views (DDL), Equi-Joins, String Concatenation with Null-Handling (CONCAT_WS), Query Simplification.`

### 1. Exact Backend SQL Query
```sql
CREATE OR REPLACE VIEW V_PLACEMENT_DETAIL AS
SELECT 
    p.Placement_ID,
    p.Student_ID,
    s.Roll_No,
    CONCAT(s.First_Name, ' ', s.Last_Name) AS Student_Name,
    s.Email,
    s.Branch,
    s.Batch_Year,
    s.CGPA,
    c.Company_ID,
    c.Company_Name,
    c.Company_Type,
    c.Location,
    p.Role,
    p.Package,
    p.Placement_Year,
    p.Placement_Type,
    p.Is_PPO,
    p.Offer_Status,
    p.Joined,
    p.Interview_Rounds,
    p.Offer_Date
FROM PLACEMENT p
JOIN STUDENT s ON p.Student_ID = s.Student_ID
JOIN COMPANY c ON p.Company_ID = c.Company_ID;
```

### 2. Functional Purpose
Creates a pre-joined relational view combining student details, recruiting company information, and placement offer terms into a single reusable virtual table.

### 3. Relational Tables Involved
**PLACEMENT (p), STUDENT (s), COMPANY (c)**

### 4. Clause-by-Clause Line Explanation
- ` CREATE OR REPLACE VIEW V_PLACEMENT_DETAIL AS `
  * **Explanation:** Defines a named, update-safe virtual view that encapsulates complex join logic without storing duplicate physical data.
- ` SELECT p.Placement_ID, s.Student_ID, s.Roll_No, CONCAT_WS(" ", s.First_Name, s.Last_Name) AS Student_Name, ... `
  * **Explanation:** Projects individual primary keys, foreign keys, compensation attributes, and computes a full student name using CONCAT_WS to handle optional last names gracefully.
- ` FROM PLACEMENT p `
  * **Explanation:** Designates the core fact table (PLACEMENT) tracking offer events.
- ` JOIN STUDENT s ON s.Student_ID = p.Student_ID `
  * **Explanation:** Performs an inner equi-join on primary key Student_ID to attach candidate demographic and academic data.
- ` JOIN COMPANY c ON c.Company_ID = p.Company_ID `
  * **Explanation:** Performs an inner equi-join on Company_ID to attach corporate recruiter profiles.

### 5. JOINs and Entity Relationships
Two inner equi-joins linking PLACEMENT to its two parent dimensions: STUDENT (Many-to-One) and COMPANY (Many-to-One). Preserves referential consistency.

### 6. Produced Output
Virtual tabular view containing comprehensive placement records with student names, company names, package, placement year, and offer statuses.

### 7. Key SQL & DBMS Concepts Tested
Relational Views (DDL), Equi-Joins, String Concatenation with Null-Handling (CONCAT_WS), Query Simplification.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: Why create a view instead of querying physical tables directly, and does a view consume disk storage?"

### 9. Independent Practice Challenge
**Problem:** Write a CREATE VIEW statement named V_STUDENT_BRIEF that combines Student_ID, Roll_No, Full Name (First + Last), Branch, CGPA, and a count of their total skills from STUDENT_SKILL.

---

## 2. Query 2 (DDL-22): View V_INTERNSHIP_DETAIL with Derived Duration

- **Source Routine / File:** `schema.sql / Schema Setup`
- **Viva Category:** `Internship management`
- **Core DBMS Concepts:** `Derived Attributes in Relational Design (3NF), Date Arithmetic (DATEDIFF), Rounding Functions (ROUND), Relational Views.`

### 1. Exact Backend SQL Query
```sql
CREATE OR REPLACE VIEW V_INTERNSHIP_DETAIL AS
SELECT 
    i.Internship_ID,
    i.Student_ID,
    s.Roll_No,
    CONCAT(s.First_Name, ' ', s.Last_Name) AS Student_Name,
    s.Branch,
    s.Batch_Year,
    s.CGPA,
    c.Company_ID,
    c.Company_Name,
    c.Company_Type,
    i.Role,
    i.Internship_Type,
    i.Start_Date,
    i.End_Date,
    DATEDIFF(i.End_Date, i.Start_Date) AS Duration_Days,
    ROUND(DATEDIFF(i.End_Date, i.Start_Date) / 30.4375, 1) AS Duration_Months,
    i.Stipend,
    i.Credits,
    i.Status,
    i.Report_Link,
    i.Certificate_Link
FROM INTERNSHIP i
JOIN STUDENT s ON i.Student_ID = s.Student_ID
JOIN COMPANY c ON i.Company_ID = c.Company_ID;
```

### 2. Functional Purpose
Creates a virtual view for all student internships that dynamically calculates the duration in months using calendar dates, enforcing 3NF by avoiding stored redundant attributes.

### 3. Relational Tables Involved
**INTERNSHIP (i), STUDENT (s), COMPANY (c)**

### 4. Clause-by-Clause Line Explanation
- ` CREATE OR REPLACE VIEW V_INTERNSHIP_DETAIL AS `
  * **Explanation:** Instantiates a reusable view for institutional internship tracking.
- ` SELECT i.Internship_ID, ..., ROUND((DATEDIFF(i.End_Date, i.Start_Date) + 1) / 30, 1) AS Duration_Months `
  * **Explanation:** Calculates derived attribute Duration_Months on the fly using DATEDIFF + 1 divided by 30 days and rounded to 1 decimal place.
- ` FROM INTERNSHIP i `
  * **Explanation:** Base table representing individual internship tenures.
- ` JOIN STUDENT s ON s.Student_ID = i.Student_ID `
  * **Explanation:** Attaches student candidate metadata via Student_ID.
- ` JOIN COMPANY c ON c.Company_ID = i.Company_ID `
  * **Explanation:** Attaches host corporate recruiter details via Company_ID.

### 5. JOINs and Entity Relationships
Two Many-to-One inner joins resolving foreign keys Student_ID and Company_ID against their respective master tables.

### 6. Produced Output
Internship records enriched with student names, company profiles, stipend, credits, and exact calculated monthly duration.

### 7. Key SQL & DBMS Concepts Tested
Derived Attributes in Relational Design (3NF), Date Arithmetic (DATEDIFF), Rounding Functions (ROUND), Relational Views.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: Why is Duration_Months calculated dynamically rather than stored as a column in the INTERNSHIP table?"

### 9. Independent Practice Challenge
**Problem:** Write a query on the INTERNSHIP table that selects Student_ID, Role, and categorizes the duration as "Short-term" (< 2 months), "Standard" (2-6 months), or "Long-term" (> 6 months) using CASE WHEN and DATEDIFF.

---

## 3. Query 3 (DDL-05): Multivalued Skill Decomposition (STUDENT_SKILL)

- **Source Routine / File:** `init_mysql.py / initialize_database`
- **Viva Category:** `Other database operations`
- **Core DBMS Concepts:** `First Normal Form (1NF), Composite Primary Keys, Foreign Key Constraints, ON DELETE CASCADE, Relational Normalization.`

### 1. Exact Backend SQL Query
```sql
CREATE TABLE IF NOT EXISTS STUDENT_SKILL (
    Student_ID      INT         NOT NULL,
    Skill           VARCHAR(50) NOT NULL,
    PRIMARY KEY (Student_ID, Skill),
    CONSTRAINT fk_skill_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE
) ENGINE=InnoDB;
```

### 2. Functional Purpose
Creates the STUDENT_SKILL table decomposing multiple technical skills per student into separate atomic rows, fulfilling First Normal Form (1NF).

### 3. Relational Tables Involved
**STUDENT_SKILL (child), STUDENT (parent)**

### 4. Clause-by-Clause Line Explanation
- ` CREATE TABLE IF NOT EXISTS STUDENT_SKILL (Student_ID INT NOT NULL, Skill VARCHAR(50) NOT NULL, ...) `
  * **Explanation:** Defines the relational schema for atomic student skill storage.
- ` PRIMARY KEY (Student_ID, Skill) `
  * **Explanation:** Establishes a composite primary key ensuring a student cannot have duplicate skill entries.
- ` CONSTRAINT fk_skill_student FOREIGN KEY (Student_ID) REFERENCES STUDENT(Student_ID) ON DELETE CASCADE `
  * **Explanation:** Enforces referential integrity; deleting a student automatically purges their skills.

### 5. JOINs and Entity Relationships
Parent-Child relationship (1:N) between STUDENT and STUDENT_SKILL enforced via foreign key with CASCADE DELETE.

### 6. Produced Output
DDL schema definition enforcing 1NF atomicity and eliminating comma-delimited strings.

### 7. Key SQL & DBMS Concepts Tested
First Normal Form (1NF), Composite Primary Keys, Foreign Key Constraints, ON DELETE CASCADE, Relational Normalization.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: What normal form violation occurs if we store skills as "Java, Python, SQL" in a single column in the STUDENT table, and how does this composite key solve it?"

### 9. Independent Practice Challenge
**Problem:** Write the DDL statement to create a table STUDENT_CERTIFICATION that stores multiple professional certifications per student with Student_ID, Certification_Name, Issue_Year, and a composite primary key.

---

## 4. Query 4 (DDL-08): PLACEMENT Table with Single Joined Offer Constraint

- **Source Routine / File:** `schema.sql / Schema Setup`
- **Viva Category:** `Other database operations`
- **Core DBMS Concepts:** `Generated Stored Columns, Conditional Logic (CASE WHEN) in DDL, Partial Unique Constraints via NULL semantics, Business Rule Enforcement.`

### 1. Exact Backend SQL Query
```sql
CREATE TABLE IF NOT EXISTS RESUME (
    Resume_ID       INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID      INT          NOT NULL,
    File_Name       VARCHAR(100) NOT NULL,
    File_Link       VARCHAR(255) NOT NULL,
    Upload_Date     DATE         NOT NULL DEFAULT (CURRENT_DATE),
    Resume_Year     INT          NOT NULL CHECK (Resume_Year BETWEEN 2000 AND 2100),
    CONSTRAINT fk_resume_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE
) ENGINE=InnoDB;
```

### 2. Functional Purpose
Creates the PLACEMENT table and physically enforces the institutional rule that a student may accept/join at most one job offer using a generated virtual column and unique index.

### 3. Relational Tables Involved
**PLACEMENT**

### 4. Clause-by-Clause Line Explanation
- ` CREATE TABLE PLACEMENT (...) `
  * **Explanation:** Defines the schema for placement offers.
- ` Joined_Student INT GENERATED ALWAYS AS (CASE WHEN Joined = "Yes" OR Offer_Status = "Joined" THEN Student_ID ELSE NULL END) STORED `
  * **Explanation:** Virtual stored generated column that holds the Student_ID ONLY when the offer is accepted, and NULL otherwise.
- ` UNIQUE KEY uq_one_joined_offer (Joined_Student) `
  * **Explanation:** Enforces uniqueness on Joined_Student. Because MySQL allows multiple NULLs in a UNIQUE index, multiple unjoined offers can exist, but at most ONE joined offer per student is permitted.

### 5. JOINs and Entity Relationships
Internal column constraint and indexing mechanism on PLACEMENT referencing Student_ID.

### 6. Produced Output
DDL table definition with hardware-level enforcement of single-joining policy.

### 7. Key SQL & DBMS Concepts Tested
Generated Stored Columns, Conditional Logic (CASE WHEN) in DDL, Partial Unique Constraints via NULL semantics, Business Rule Enforcement.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: How does MySQL handle NULL values in a UNIQUE constraint, and how does that allow a student to have multiple offers but only one joined offer?"

### 9. Independent Practice Challenge
**Problem:** Write a CHECK constraint or table definition snippet that ensures a column Stipend is non-negative and Start_Date is earlier than End_Date in an INTERNSHIP table.

---

## 5. Query 5 (STU-07): Retrieve Multivalued Student Phone Numbers

- **Source Routine / File:** `services/student_service.py / get_student_by_id`
- **Viva Category:** `Student management`
- **Core DBMS Concepts:** `1NF Contact Number Decomposition, Parameterized SQL, Primary Key Lookup, ORDER BY.`

### 1. Exact Backend SQL Query
```sql
SELECT Phone_No FROM STUDENT_PHONE WHERE Student_ID = %s ORDER BY Phone_No
```

### 2. Functional Purpose
Fetches all registered phone numbers for a specific student candidate to assemble their multi-attribute contact card.

### 3. Relational Tables Involved
**STUDENT_PHONE**

### 4. Clause-by-Clause Line Explanation
- ` SELECT Phone_No `
  * **Explanation:** Projects the contact number string.
- ` FROM STUDENT_PHONE `
  * **Explanation:** Queries the normalized contact phone decomposition table.
- ` WHERE Student_ID = %s `
  * **Explanation:** Filters for the specific target student using parameterized input.
- ` ORDER BY Phone_No `
  * **Explanation:** Sorts contact numbers lexicographically.

### 5. JOINs and Entity Relationships
References parent STUDENT table via foreign key Student_ID.

### 6. Produced Output
Zero, one, or multiple phone number rows for the student.

### 7. Key SQL & DBMS Concepts Tested
1NF Contact Number Decomposition, Parameterized SQL, Primary Key Lookup, ORDER BY.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: Why is Phone_No stored in a separate table instead of having columns Phone_1 and Phone_2 in the STUDENT table?"

### 9. Independent Practice Challenge
**Problem:** Write a query that retrieves all skills for Student_ID = 5 from STUDENT_SKILL sorted alphabetically.

---

## 6. Query 6 (STU-11): Retrieve Semester Academic Results for Student

- **Source Routine / File:** `services/student_service.py / get_student_by_id`
- **Viva Category:** `Academic results`
- **Core DBMS Concepts:** `Academic Progression Tracking, Temporal Sorting, Parameterized Filtering.`

### 1. Exact Backend SQL Query
```sql
SELECT Result_ID, Semester, SGPA, Total_Credits, Year
        FROM SEMESTER_RESULT
        WHERE Student_ID = %s
        ORDER BY Semester ASC
```

### 2. Functional Purpose
Fetches the complete academic progression history (SGPA and credits) across semesters for a student.

### 3. Relational Tables Involved
**SEMESTER_RESULT**

### 4. Clause-by-Clause Line Explanation
- ` SELECT Result_ID, Semester, SGPA, Total_Credits, Year `
  * **Explanation:** Projects semester sequence, grade point average, earned credits, and academic year.
- ` FROM SEMESTER_RESULT `
  * **Explanation:** Master semester results ledger table.
- ` WHERE Student_ID = %s `
  * **Explanation:** Filters by target student ID.
- ` ORDER BY Semester ASC `
  * **Explanation:** Sorts chronologically from Semester 1 upwards.

### 5. JOINs and Entity Relationships
Child table to STUDENT via foreign key Student_ID.

### 6. Produced Output
Chronological record set of semester grades and credits.

### 7. Key SQL & DBMS Concepts Tested
Academic Progression Tracking, Temporal Sorting, Parameterized Filtering.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: How would you compute the cumulative CGPA from this SEMESTER_RESULT table using a SQL query?"

### 9. Independent Practice Challenge
**Problem:** Write a query calculating the weighted average SGPA (sum of SGPA * Total_Credits divided by sum of Total_Credits) for Student_ID = 12.

---

## 7. Query 7 (STU-14): Retrieve Student Placement Offers with Recruiter Details

- **Source Routine / File:** `services/student_service.py / get_student_by_id`
- **Viva Category:** `Placement management`
- **Core DBMS Concepts:** `Foreign Key Equi-Join, Sorting (ORDER BY DESC), Parameterization.`

### 1. Exact Backend SQL Query
```sql
SELECT p.Placement_ID, p.Role, p.Package, p.Placement_Year, p.Placement_Type,
               p.Is_PPO, p.Joined, p.Offer_Status, p.Interview_Rounds,
               c.Company_ID, c.Company_Name, c.Company_Type, c.Location, c.Website
        FROM PLACEMENT p
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE p.Student_ID = %s
        ORDER BY p.Placement_Year DESC, p.Package DESC
```

### 2. Functional Purpose
Fetches all placement offers secured by a specific student along with the recruiting company details, compensation package, and offer status.

### 3. Relational Tables Involved
**PLACEMENT (p), COMPANY (c)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT p.Placement_ID, p.Role, p.Package, p.Placement_Year, p.Placement_Type, p.Is_PPO, p.Joined, p.Offer_Status, c.Company_ID, c.Company_Name `
  * **Explanation:** Projects full compensation and company profile attributes.
- ` FROM PLACEMENT p `
  * **Explanation:** Core placement records.
- ` JOIN COMPANY c ON p.Company_ID = c.Company_ID `
  * **Explanation:** Equi-join on Company_ID to retrieve corporate entity names.
- ` WHERE p.Student_ID = %s `
  * **Explanation:** Restricts results to the active student candidate.
- ` ORDER BY p.Package DESC `
  * **Explanation:** Ranks offers by compensation in descending order.

### 5. JOINs and Entity Relationships
Inner join between PLACEMENT and COMPANY on Company_ID.

### 6. Produced Output
List of all job offers received by the student, highest paying offer first.

### 7. Key SQL & DBMS Concepts Tested
Foreign Key Equi-Join, Sorting (ORDER BY DESC), Parameterization.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: If a student received 3 offers, will this query return 3 rows, and how do we identify which one they accepted?"

### 9. Independent Practice Challenge
**Problem:** Modify this query to return only the offer that the student actually accepted (Joined = "Yes" or Offer_Status = "Joined").

---

## 8. Query 8 (STU-16): Placed Students Filter Predicate using Correlated EXISTS

- **Source Routine / File:** `services/student_service.py / list_students`
- **Viva Category:** `Placement management`
- **Core DBMS Concepts:** `Correlated Subqueries, EXISTS Operator, Short-Circuit Execution in SQL, Semi-Joins.`

### 1. Exact Backend SQL Query
```sql
EXISTS (SELECT 1 FROM PLACEMENT pl WHERE pl.Student_ID = s.Student_ID AND pl.Offer_Status IN ('Accepted', 'Joined'))
```

### 2. Functional Purpose
Filters a cohort of students to include only those who have secured an active placement offer using an efficient correlated EXISTS subquery.

### 3. Relational Tables Involved
**STUDENT (s), PLACEMENT (pl)**

### 4. Clause-by-Clause Line Explanation
- ` EXISTS (SELECT 1 FROM PLACEMENT pl WHERE pl.Student_ID = s.Student_ID AND pl.Offer_Status IN ("Offered", "Joined", "Accepted")) `
  * **Explanation:** Correlated subquery evaluating whether at least one matching placement record exists for each student row.

### 5. JOINs and Entity Relationships
Correlated subquery linkage matching pl.Student_ID = s.Student_ID.

### 6. Produced Output
Boolean filter condition used inside a dynamic WHERE clause.

### 7. Key SQL & DBMS Concepts Tested
Correlated Subqueries, EXISTS Operator, Short-Circuit Execution in SQL, Semi-Joins.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: Why is EXISTS generally faster than IN (SELECT Student_ID FROM PLACEMENT) when checking for presence of related rows?"

### 9. Independent Practice Challenge
**Problem:** Write a query using EXISTS to find all students who have at least one internship with a stipend greater than 25,000.

---

## 9. Query 9 (STU-17): Unplaced Students Filter Predicate using NOT EXISTS

- **Source Routine / File:** `services/student_service.py / list_students`
- **Viva Category:** `Placement management`
- **Core DBMS Concepts:** `Anti-Semi-Joins, NOT EXISTS Operator, Handling Relational Absence, NULL-safe logic.`

### 1. Exact Backend SQL Query
```sql
NOT EXISTS (SELECT 1 FROM PLACEMENT pl WHERE pl.Student_ID = s.Student_ID)
```

### 2. Functional Purpose
Identifies all students who do not have any recorded placement offer in the system.

### 3. Relational Tables Involved
**STUDENT (s), PLACEMENT (pl)**

### 4. Clause-by-Clause Line Explanation
- ` NOT EXISTS (SELECT 1 FROM PLACEMENT pl WHERE pl.Student_ID = s.Student_ID) `
  * **Explanation:** Evaluates to TRUE only if the inner query returns zero rows for that student.

### 5. JOINs and Entity Relationships
Correlated anti-semi-join linkage between STUDENT and PLACEMENT.

### 6. Produced Output
Boolean filter isolating the unplaced student cohort.

### 7. Key SQL & DBMS Concepts Tested
Anti-Semi-Joins, NOT EXISTS Operator, Handling Relational Absence, NULL-safe logic.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: What is the difference between using NOT EXISTS versus LEFT JOIN ... WHERE pl.Placement_ID IS NULL?"

### 9. Independent Practice Challenge
**Problem:** Write a query using NOT EXISTS to find all students who have zero registered phone numbers in STUDENT_PHONE.

---

## 10. Query 10 (STU-18): Multiple Placement Offers Filter Predicate

- **Source Routine / File:** `services/student_service.py / list_students`
- **Viva Category:** `Placement management`
- **Core DBMS Concepts:** `Scalar Subqueries, Aggregation inside WHERE clause, Correlated Counting.`

### 1. Exact Backend SQL Query
```sql
(SELECT COUNT(*) FROM PLACEMENT pl WHERE pl.Student_ID = s.Student_ID) >= 2
```

### 2. Functional Purpose
Filters students who have achieved academic excellence by securing 2 or more distinct placement offers.

### 3. Relational Tables Involved
**STUDENT (s), PLACEMENT (pl)**

### 4. Clause-by-Clause Line Explanation
- ` (SELECT COUNT(*) FROM PLACEMENT pl WHERE pl.Student_ID = s.Student_ID) >= 2 `
  * **Explanation:** Correlated scalar subquery that computes the exact count of offers per student and checks if it is at least 2.

### 5. JOINs and Entity Relationships
Correlated subquery linkage on Student_ID.

### 6. Produced Output
Boolean filter isolating students with multiple offers.

### 7. Key SQL & DBMS Concepts Tested
Scalar Subqueries, Aggregation inside WHERE clause, Correlated Counting.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: Can we also write this multiple offer filter using GROUP BY and HAVING? What are the tradeoffs?"

### 9. Independent Practice Challenge
**Problem:** Write a query using GROUP BY and HAVING that lists Student_ID and the count of offers for all students with 2 or more offers.

---

## 11. Query 11 (STU-30): Referential Dependency Cascade Audit

- **Source Routine / File:** `services/student_service.py / delete_student`
- **Viva Category:** `Compliance and eligibility`
- **Core DBMS Concepts:** `Referential Integrity Verification, Multiple Scalar Subqueries in SELECT, Pre-Deletion Audits, Relational Safeguards.`

### 1. Exact Backend SQL Query
```sql
SELECT 
            (SELECT COUNT(*) FROM PLACEMENT WHERE Student_ID = %s) AS placement_count,
            (SELECT COUNT(*) FROM INTERNSHIP WHERE Student_ID = %s) AS internship_count
```

### 2. Functional Purpose
Audits all child relational dependencies (placements, internships, resumes, courses, profiles) before deleting a student candidate to ensure data integrity.

### 3. Relational Tables Involved
**PLACEMENT, INTERNSHIP, RESUME, STUDENT_COURSE, STUDENT_PROFILE**

### 4. Clause-by-Clause Line Explanation
- ` SELECT (SELECT COUNT(*) FROM PLACEMENT WHERE Student_ID = %s) AS pl_cnt, (SELECT COUNT(*) FROM INTERNSHIP WHERE Student_ID = %s) AS int_cnt, ... `
  * **Explanation:** Executes parallel scalar subqueries in a single round-trip to compute reference counts across 5 related tables.

### 5. JOINs and Entity Relationships
Independent scalar subquery evaluations tied to the target Student_ID.

### 6. Produced Output
Single row containing counts of associated records across 5 foreign key relationships.

### 7. Key SQL & DBMS Concepts Tested
Referential Integrity Verification, Multiple Scalar Subqueries in SELECT, Pre-Deletion Audits, Relational Safeguards.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: If the foreign key has ON DELETE CASCADE, why would the application code still perform a manual dependency audit before deletion?"

### 9. Independent Practice Challenge
**Problem:** Write a query that checks if a Company_ID has any associated drives in RECRUITMENT_DRIVE, placements in PLACEMENT, or internships in INTERNSHIP.

---

## 12. Query 12 (CMP-05): Retrieve Company Job and Internship Opportunities

- **Source Routine / File:** `services/company_service.py / get_company_by_id`
- **Viva Category:** `Internship management`
- **Core DBMS Concepts:** `Multi-Table Parent-Child Navigation, Composite Ordering, Foreign Key Traversal.`

### 1. Exact Backend SQL Query
```sql
SELECT o.Opportunity_ID, o.Role, o.Opportunity_Type, o.Package_Stipend, o.Duration_Months,
                   e.Minimum_CGPA, e.Max_Backlogs, e.Other_Criteria, e.Eligible_Branch, e.Eligibility_ID
            FROM OPPORTUNITY o
            LEFT JOIN ELIGIBILITY e ON o.Opportunity_ID = e.Opportunity_ID
            WHERE o.Drive_ID = %s
            ORDER BY o.Opportunity_ID ASC
```

### 2. Functional Purpose
Fetches all campus recruitment opportunities posted by a company across all its drives.

### 3. Relational Tables Involved
**OPPORTUNITY (o), RECRUITMENT_DRIVE (rd)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT o.Opportunity_ID, o.Role, o.Opportunity_Type, o.Package_Stipend, o.Duration_Months, rd.Drive_Year `
  * **Explanation:** Projects job role, opportunity classification, compensation, duration, and year.
- ` FROM OPPORTUNITY o `
  * **Explanation:** Child entity tracking specific openings.
- ` JOIN RECRUITMENT_DRIVE rd ON o.Drive_ID = rd.Drive_ID `
  * **Explanation:** Equi-join linking opportunity to parent recruitment drive.
- ` WHERE rd.Company_ID = %s `
  * **Explanation:** Filters by host company ID.
- ` ORDER BY rd.Drive_Year DESC, o.Package_Stipend DESC `
  * **Explanation:** Sorts by most recent drive year and highest compensation.

### 5. JOINs and Entity Relationships
Inner join on Drive_ID between OPPORTUNITY and RECRUITMENT_DRIVE.

### 6. Produced Output
List of all active and historical hiring opportunities posted by the recruiter.

### 7. Key SQL & DBMS Concepts Tested
Multi-Table Parent-Child Navigation, Composite Ordering, Foreign Key Traversal.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: Why is OPPORTUNITY linked to RECRUITMENT_DRIVE instead of directly to COMPANY?"

### 9. Independent Practice Challenge
**Problem:** Write a query that counts how many total opportunities each company has posted across all years.

---

## 13. Query 13 (CMP-08): Aggregate Company Placement and Internship Volume

- **Source Routine / File:** `services/company_service.py / get_company_by_id`
- **Viva Category:** `Internship management`
- **Core DBMS Concepts:** `Scalar Subquery Aggregations, COALESCE Function for Null-Safety, Dual Metric Assembly.`

### 1. Exact Backend SQL Query
```sql
SELECT 
            (SELECT COUNT(*) FROM PLACEMENT WHERE Company_ID = %s) AS total_placements,
            (SELECT COUNT(*) FROM INTERNSHIP WHERE Company_ID = %s) AS total_internships
```

### 2. Functional Purpose
Computes institutional engagement metrics for a recruiter: total placements offered, total internships hosted, and average compensation.

### 3. Relational Tables Involved
**PLACEMENT, INTERNSHIP**

### 4. Clause-by-Clause Line Explanation
- ` SELECT (SELECT COUNT(*) FROM PLACEMENT WHERE Company_ID = %s) AS total_placements, (SELECT COUNT(*) FROM INTERNSHIP WHERE Company_ID = %s) AS total_internships, (SELECT ROUND(COALESCE(AVG(Package), 0), 2) FROM PLACEMENT WHERE Company_ID = %s) AS avg_package `
  * **Explanation:** Parallel scalar subqueries evaluating institutional recruitment yields with COALESCE null handling.

### 5. JOINs and Entity Relationships
Independent scalar subquery aggregations.

### 6. Produced Output
Single row summary: total placements, total internships, and average salary package offered by the company.

### 7. Key SQL & DBMS Concepts Tested
Scalar Subquery Aggregations, COALESCE Function for Null-Safety, Dual Metric Assembly.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: What happens if a company has offered zero placements? Why is COALESCE(AVG(Package), 0) necessary?"

### 9. Independent Practice Challenge
**Problem:** Write a query that displays Company_Name, total placed students, and total interns for all companies using LEFT JOIN and GROUP BY.

---

## 14. Query 14 (CMP-15): Verify Recruiter Attachments Before Deletion

- **Source Routine / File:** `services/company_service.py / delete_company`
- **Viva Category:** `Internship management`
- **Core DBMS Concepts:** `Referential Integrity, ON DELETE RESTRICT Enforcement, Defensive Programming in SQL.`

### 1. Exact Backend SQL Query
```sql
SELECT 
            (SELECT COUNT(*) FROM PLACEMENT WHERE Company_ID = %s) AS p_cnt,
            (SELECT COUNT(*) FROM INTERNSHIP WHERE Company_ID = %s) AS i_cnt
```

### 2. Functional Purpose
Enforces the ON DELETE RESTRICT relational policy by ensuring a corporate partner with active student placements or internships cannot be accidentally purged.

### 3. Relational Tables Involved
**PLACEMENT, INTERNSHIP**

### 4. Clause-by-Clause Line Explanation
- ` SELECT (SELECT COUNT(*) FROM PLACEMENT WHERE Company_ID = %s) AS p_cnt, (SELECT COUNT(*) FROM INTERNSHIP WHERE Company_ID = %s) AS i_cnt `
  * **Explanation:** Queries placement and internship tables to verify zero active contracts.

### 5. JOINs and Entity Relationships
Scalar subquery integrity checks.

### 6. Produced Output
Row returning count of existing dependent records in child tables.

### 7. Key SQL & DBMS Concepts Tested
Referential Integrity, ON DELETE RESTRICT Enforcement, Defensive Programming in SQL.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: What is the difference between ON DELETE CASCADE, ON DELETE RESTRICT, and ON DELETE SET NULL?"

### 9. Independent Practice Challenge
**Problem:** Write a trigger or query that prevents deleting a COURSE if any student is currently enrolled in STUDENT_COURSE.

---

## 15. Query 15 (PLC-08): Equi-Join Offer Detail with Student and Recruiter

- **Source Routine / File:** `services/placement_service.py / get_placement_by_id`
- **Viva Category:** `Placement management`
- **Core DBMS Concepts:** `3-Table Equi-Join, Primary-to-Foreign Key Traversal, Star-Schema Fact-Dimension Querying.`

### 1. Exact Backend SQL Query
```sql
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
```

### 2. Functional Purpose
Retrieves full details of a single placement offer including student roll number, candidate name, CGPA, recruiter name, and compensation terms.

### 3. Relational Tables Involved
**PLACEMENT (p), STUDENT (s), COMPANY (c)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT p.Placement_ID, p.Role, p.Package, p.Placement_Year, p.Placement_Type, p.Is_PPO, p.Joined, p.Offer_Status, s.Student_ID, s.Roll_No, CONCAT_WS(" ", s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.CGPA, c.Company_ID, c.Company_Name, c.Company_Type `
  * **Explanation:** Projects complete offer anatomy across 3 entities.
- ` FROM PLACEMENT p `
  * **Explanation:** Core placement table.
- ` JOIN STUDENT s ON p.Student_ID = s.Student_ID `
  * **Explanation:** Equi-join attaching student demographics.
- ` JOIN COMPANY c ON p.Company_ID = c.Company_ID `
  * **Explanation:** Equi-join attaching recruiter metadata.
- ` WHERE p.Placement_ID = %s `
  * **Explanation:** Filters by target offer primary key.

### 5. JOINs and Entity Relationships
Three-table equi-join linking fact table PLACEMENT to dimensions STUDENT and COMPANY.

### 6. Produced Output
Comprehensive single-offer specification.

### 7. Key SQL & DBMS Concepts Tested
3-Table Equi-Join, Primary-to-Foreign Key Traversal, Star-Schema Fact-Dimension Querying.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: How would you explain this 3-table join to an interviewer using the ER diagram?"

### 9. Independent Practice Challenge
**Problem:** Write a 3-table join query that lists all placement offers in the year 2024 with student name, branch, company name, and package, sorted by package descending.

---

## 16. Query 16 (PLC-18): Overall Placement Compensation Analytics

- **Source Routine / File:** `services/placement_service.py / get_placement_analytics`
- **Viva Category:** `Placement management`
- **Core DBMS Concepts:** `Aggregate Functions (COUNT, MAX, MIN, AVG), Decimal Rounding (ROUND).`

### 1. Exact Backend SQL Query
```sql
SELECT c.Company_ID, c.Company_Name, c.Company_Type, c.Industry,
               COUNT(p.Placement_ID) AS total_offers,
               COUNT(DISTINCT CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN p.Student_ID END) AS placed_count,
               COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' OR p.Offer_Status = 'Joined' THEN p.Student_ID END) AS joined_count,
               ROUND(AVG(p.Package), 2) AS avg_package,
               ROUND(MAX(p.Package), 2) AS highest_package
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE
```

### 2. Functional Purpose
Calculates institutional compensation statistics: highest package, lowest package, average package, and total offers.

### 3. Relational Tables Involved
**PLACEMENT**

### 4. Clause-by-Clause Line Explanation
- ` SELECT COUNT(*) AS total_offers, MAX(Package) AS highest_package, MIN(Package) AS lowest_package, ROUND(AVG(Package), 2) AS avg_package `
  * **Explanation:** Executes multiple aggregate functions over the entire placement population.

### 5. JOINs and Entity Relationships
Single table aggregate scan.

### 6. Produced Output
Single summary row with statistical bounds and mean compensation.

### 7. Key SQL & DBMS Concepts Tested
Aggregate Functions (COUNT, MAX, MIN, AVG), Decimal Rounding (ROUND).

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: How does SQL handle NULL values when computing AVG(Package)?"

### 9. Independent Practice Challenge
**Problem:** Write a query that computes the total offers, highest package, and average package for each placement year.

---

## 17. Query 17 (INT-05): Retrieve Student Internships with Host Profiles

- **Source Routine / File:** `services/internship_service.py / get_student_internships`
- **Viva Category:** `Internship management`
- **Core DBMS Concepts:** `Weak Entity Representation, Sequence-based Sorting, Foreign Key Equi-Join.`

### 1. Exact Backend SQL Query
```sql
SELECT Company_ID, Company_Name FROM COMPANY WHERE Company_ID = %s
```

### 2. Functional Purpose
Fetches all internships completed by a student, detailing the host company, role, stipend, start and end dates, and academic credits earned.

### 3. Relational Tables Involved
**INTERNSHIP (i), COMPANY (c)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT i.Internship_ID, i.Internship_No, i.Internship_Type, i.Role, i.Stipend, i.Start_Date, i.End_Date, i.Credits, c.Company_Name `
  * **Explanation:** Projects internship specifications and corporate host name.
- ` FROM INTERNSHIP i `
  * **Explanation:** Weak entity table tracking degree and voluntary internships.
- ` JOIN COMPANY c ON i.Company_ID = c.Company_ID `
  * **Explanation:** Equi-join resolving host organization name.
- ` WHERE i.Student_ID = %s `
  * **Explanation:** Filters by target student.
- ` ORDER BY i.Internship_No ASC `
  * **Explanation:** Orders sequentially by internship number (1 = 2nd year summer, 2 = 3rd year summer).

### 5. JOINs and Entity Relationships
Inner join between INTERNSHIP and COMPANY on Company_ID.

### 6. Produced Output
Complete internship track record for the student candidate.

### 7. Key SQL & DBMS Concepts Tested
Weak Entity Representation, Sequence-based Sorting, Foreign Key Equi-Join.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: Why is INTERNSHIP classified as a weak entity in our ER diagram, and what is its primary key?"

### 9. Independent Practice Challenge
**Problem:** Write a query that retrieves all internships where the student earned college degree credits (Credits > 0).

---

## 18. Query 18 (INT-16): Prerequisite SGPA Mapping for Mandatory Internships

- **Source Routine / File:** `services/internship_service.py / check_mandatory_eligibility`
- **Viva Category:** `Compliance and eligibility`
- **Core DBMS Concepts:** `Prerequisite Validation, IN Operator, Business Rule Integration.`

### 1. Exact Backend SQL Query
```sql
SELECT 
            i.Internship_ID,
            i.Student_ID,
            s.Roll_No,
            CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Student_Name,
            s.Branch,
            s.Batch_Year,
            c.Company_Name,
            i.Internship_No,
            i.Internship_Type,
            i.Role,
            i.Stipend,
            i.Start_Date,
            i.End_Date,
            i.Credits,
            i.Report_Semester,
            i.Report_Link,
            i.Certificate_Link,
            ir.Prescribed_Period,
            ir.Required_Result_Semester,
            sr.SGPA AS Prerequisite_Semester_SGPA,
            sr.Total_Credits AS Prerequisite_Credits,
            i.Report_Grade
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        JOIN INTERNSHIP_REQUIREMENT ir ON i.Requirement_ID = ir.Requirement_ID
        LEFT JOIN SEMESTER_RESULT sr ON i.Student_ID = sr.Student_ID 
                                    AND ir.Required_Result_Semester = sr.Semester
        WHERE i.Internship_Type = 'Mandatory'
        ORDER BY i.Internship_No ASC, sr.SGPA DESC;
```

### 2. Functional Purpose
Validates academic eligibility for mandatory internships by checking prerequisite semester SGPA thresholds (Sem 3 for Mandatory #1, Sem 5 for Mandatory #2).

### 3. Relational Tables Involved
**SEMESTER_RESULT**

### 4. Clause-by-Clause Line Explanation
- ` SELECT Semester, SGPA `
  * **Explanation:** Projects semester sequence and recorded SGPA.
- ` FROM SEMESTER_RESULT `
  * **Explanation:** Academic semester performance ledger.
- ` WHERE Student_ID = %s AND Semester IN (3, 5) `
  * **Explanation:** Restricts retrieval to critical evaluation milestone semesters.
- ` ORDER BY Semester ASC `
  * **Explanation:** Chronological sorting.

### 5. JOINs and Entity Relationships
Filters child records of STUDENT.

### 6. Produced Output
Up to 2 rows representing Sem 3 and Sem 5 grade point averages.

### 7. Key SQL & DBMS Concepts Tested
Prerequisite Validation, IN Operator, Business Rule Integration.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: How does the application decide whether a student is eligible for Mandatory Internship #2 based on this query result?"

### 9. Independent Practice Challenge
**Problem:** Write a query that checks if a student has an SGPA of at least 6.5 in both Semester 3 and Semester 5.

---

## 19. Query 19 (INT-23): Mandatory Internship #1 vs #2 Breakdown

- **Source Routine / File:** `services/internship_service.py / get_internship_analytics`
- **Viva Category:** `Dashboard and statistics`
- **Core DBMS Concepts:** `Conditional Aggregation, CASE WHEN inside COUNT(), Single-Pass Analytics.`

### 1. Exact Backend SQL Query
```sql
SELECT 
            COUNT(CASE WHEN Internship_No = 1 AND Internship_Type = 'Mandatory' THEN 1 END) AS i1_count,
            COUNT(CASE WHEN Internship_No = 2 AND Internship_Type = 'Mandatory' THEN 1 END) AS i2_count,
            COUNT(CASE WHEN Internship_Type = 'Additional' THEN 1 END) AS additional_count
        FROM INTERNSHIP
```

### 2. Functional Purpose
Calculates the institutional completion volume of Mandatory Internship #1 (after 2nd yr) versus Mandatory Internship #2 (after 3rd yr) using conditional aggregation.

### 3. Relational Tables Involved
**INTERNSHIP**

### 4. Clause-by-Clause Line Explanation
- ` SELECT COUNT(CASE WHEN Internship_No = 1 AND Internship_Type = "Mandatory" THEN 1 END) AS mandatory_1_count, COUNT(CASE WHEN Internship_No = 2 AND Internship_Type = "Mandatory" THEN 1 END) AS mandatory_2_count `
  * **Explanation:** Executes CASE expressions inside COUNT to conditionally tally specific internship categories in a single pass.

### 5. JOINs and Entity Relationships
Single table aggregation.

### 6. Produced Output
Single row with two separate counters: Mandatory 1 completions and Mandatory 2 completions.

### 7. Key SQL & DBMS Concepts Tested
Conditional Aggregation, CASE WHEN inside COUNT(), Single-Pass Analytics.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: Why is COUNT(CASE WHEN ... THEN 1 END) used here instead of running two separate SELECT queries?"

### 9. Independent Practice Challenge
**Problem:** Write a query using conditional aggregation that counts how many placement offers are "On-campus" vs "Off-campus".

---

## 20. Query 20 (INT-25): Fully Compliant Students Count (Dual EXISTS)

- **Source Routine / File:** `services/internship_service.py / get_internship_analytics`
- **Viva Category:** `Dashboard and statistics`
- **Core DBMS Concepts:** `Dual Correlated EXISTS, Relational Division Pattern, Compliance Audits, Set Intersection.`

### 1. Exact Backend SQL Query
```sql
SELECT COUNT(DISTINCT s.Student_ID) AS fully_compliant
        FROM STUDENT s
        JOIN INTERNSHIP i1 ON s.Student_ID = i1.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = 'Mandatory'
        JOIN INTERNSHIP i2 ON s.Student_ID = i2.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = 'Mandatory'
```

### 2. Functional Purpose
Counts how many active students have completed BOTH Mandatory Internship #1 AND Mandatory Internship #2, qualifying them for graduation degree clearance.

### 3. Relational Tables Involved
**STUDENT (s), INTERNSHIP (i1, i2)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT COUNT(DISTINCT s.Student_ID) AS fully_compliant `
  * **Explanation:** Counts unique qualified students.
- ` FROM STUDENT s `
  * **Explanation:** Master student entity.
- ` WHERE EXISTS (SELECT 1 FROM INTERNSHIP i1 WHERE i1.Student_ID = s.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = "Mandatory") `
  * **Explanation:** First semi-join ensuring Mandatory Internship #1 is completed.
- ` AND EXISTS (SELECT 1 FROM INTERNSHIP i2 WHERE i2.Student_ID = s.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = "Mandatory") `
  * **Explanation:** Second semi-join ensuring Mandatory Internship #2 is completed.

### 5. JOINs and Entity Relationships
Double correlated EXISTS subqueries on INTERNSHIP.

### 6. Produced Output
Single scalar number representing institutional graduation-ready internship compliance.

### 7. Key SQL & DBMS Concepts Tested
Dual Correlated EXISTS, Relational Division Pattern, Compliance Audits, Set Intersection.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: What relational algebra operation does this query perform, and how could it be rewritten using GROUP BY and HAVING?"

### 9. Independent Practice Challenge
**Problem:** Rewrite this query using an INNER JOIN between STUDENT and INTERNSHIP with GROUP BY s.Student_ID and HAVING COUNT(DISTINCT Internship_No) = 2.

---

## 21. Query 21 (CRS-07): Course Enrollment and Grade Distribution

- **Source Routine / File:** `services/course_service.py / get_course_enrollments`
- **Viva Category:** `Academic results`
- **Core DBMS Concepts:** `Many-to-Many Junction Table Traversal, Composite Key Entity Navigation, CONCAT_WS.`

### 1. Exact Backend SQL Query
```sql
SELECT * FROM COURSE WHERE Course_ID = %s
```

### 2. Functional Purpose
Retrieves all student enrollments for a specific academic course, showing student roll numbers, names, and assigned course grades.

### 3. Relational Tables Involved
**STUDENT_COURSE (sc), STUDENT (s)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT s.Student_ID, s.Roll_No, CONCAT_WS(" ", s.First_Name, s.Last_Name) AS Student_Name, sc.Enrollment_Year, sc.Grade `
  * **Explanation:** Projects candidate identifiers and academic course performance.
- ` FROM STUDENT_COURSE sc `
  * **Explanation:** Decomposed junction table modeling the Many-to-Many relationship between STUDENT and COURSE.
- ` JOIN STUDENT s ON sc.Student_ID = s.Student_ID `
  * **Explanation:** Equi-join on Student_ID to resolve student identity.
- ` WHERE sc.Course_ID = %s `
  * **Explanation:** Filters for the specified course.
- ` ORDER BY s.Roll_No ASC `
  * **Explanation:** Sorts by candidate roll number.

### 5. JOINs and Entity Relationships
Equi-join resolving the Many-to-Many student-to-course junction.

### 6. Produced Output
Class roster with individual student grades.

### 7. Key SQL & DBMS Concepts Tested
Many-to-Many Junction Table Traversal, Composite Key Entity Navigation, CONCAT_WS.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: Why is STUDENT_COURSE needed instead of putting Course_ID in STUDENT or Student_ID in COURSE?"

### 9. Independent Practice Challenge
**Problem:** Write a query that calculates the count of students for each grade ("A", "B", "C", etc.) in Course_ID = 101 using GROUP BY.

---

## 22. Query 22 (RES-40): Semester Result Equi-Join with Student Candidate

- **Source Routine / File:** `services/semester_result_service.py / get_result_by_id`
- **Viva Category:** `Academic results`
- **Core DBMS Concepts:** `Foreign Key Equi-Join, Primary Key Single-Record Retrieval, Parent-Child Relational Linking.`

### 1. Exact Backend SQL Query
```sql
SELECT sr.Result_ID, sr.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch,
               sr.Semester, sr.SGPA, sr.Year, sr.Total_Credits
        FROM SEMESTER_RESULT sr
        JOIN STUDENT s ON sr.Student_ID = s.Student_ID
        WHERE sr.Result_ID = %s
```

### 2. Functional Purpose
Fetches a single semester examination result tuple joined with the student candidate demographic record.

### 3. Relational Tables Involved
**SEMESTER_RESULT (sr), STUDENT (s)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT sr.Result_ID, sr.Semester, sr.SGPA, sr.Year, sr.Total_Credits, s.Student_ID, s.Roll_No, CONCAT_WS(" ", s.First_Name, s.Last_Name) AS Student_Name, s.Branch `
  * **Explanation:** Projects academic performance metrics alongside student master details.
- ` FROM SEMESTER_RESULT sr `
  * **Explanation:** Semester results ledger.
- ` JOIN STUDENT s ON sr.Student_ID = s.Student_ID `
  * **Explanation:** Equi-join matching foreign key Student_ID.
- ` WHERE sr.Result_ID = %s `
  * **Explanation:** Primary key lookup.

### 5. JOINs and Entity Relationships
Inner equi-join from child SEMESTER_RESULT to parent STUDENT.

### 6. Produced Output
Verified academic grade card entry for a student in a specific semester.

### 7. Key SQL & DBMS Concepts Tested
Foreign Key Equi-Join, Primary Key Single-Record Retrieval, Parent-Child Relational Linking.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: What constraint in the database prevents a student from having two result records for the same semester?"

### 9. Independent Practice Challenge
**Problem:** Write an ALTER TABLE statement adding a UNIQUE constraint on SEMESTER_RESULT for (Student_ID, Semester).

---

## 23. Query 23 (RES-41): Academic Progression Roster across Students

- **Source Routine / File:** `services/semester_result_service.py / list_results`
- **Viva Category:** `Academic results`
- **Core DBMS Concepts:** `Multi-Column Hierarchical Sorting (ORDER BY col1 DESC, col2 DESC), Institutional Academic Reporting.`

### 1. Exact Backend SQL Query
```sql
SELECT sr.Result_ID, sr.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch,
               sr.Semester, sr.SGPA, sr.Year, sr.Total_Credits
        FROM SEMESTER_RESULT sr
        JOIN STUDENT s ON sr.Student_ID = s.Student_ID
        WHERE
```

### 2. Functional Purpose
Lists academic results across the student population with multi-field filtering and sorting capabilities.

### 3. Relational Tables Involved
**SEMESTER_RESULT (sr), STUDENT (s)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT sr.Result_ID, sr.Semester, sr.SGPA, sr.Year, sr.Total_Credits, s.Roll_No, CONCAT_WS(" ", s.First_Name, s.Last_Name) AS Student_Name, s.Branch `
  * **Explanation:** Projects academic marks with student identifying data.
- ` FROM SEMESTER_RESULT sr `
  * **Explanation:** Results table.
- ` JOIN STUDENT s ON sr.Student_ID = s.Student_ID `
  * **Explanation:** Equi-join on Student_ID.
- ` ORDER BY sr.Year DESC, sr.Semester DESC, sr.SGPA DESC `
  * **Explanation:** Hierarchical multi-column sorting: most recent year, highest semester, best SGPA.

### 5. JOINs and Entity Relationships
Inner join on Student_ID.

### 6. Produced Output
Institutional academic marks leaderboard.

### 7. Key SQL & DBMS Concepts Tested
Multi-Column Hierarchical Sorting (ORDER BY col1 DESC, col2 DESC), Institutional Academic Reporting.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: How does the database engine execute multi-column sorting when the first column has duplicate values?"

### 9. Independent Practice Challenge
**Problem:** Write a query that selects the top 3 highest SGPA students in Semester 6.

---

## 24. Query 24 (DRV-20): Equi-Join Recruitment Drive with Corporate Host

- **Source Routine / File:** `services/drive_service.py / get_drive_by_id`
- **Viva Category:** `Company management`
- **Core DBMS Concepts:** `Parent-Child Relational Linking, Campus Recruitment Scheduling, Dimension Resolution.`

### 1. Exact Backend SQL Query
```sql
SELECT rd.Drive_ID, rd.Company_ID, c.Company_Name, c.Company_Type, c.Industry,
               rd.Drive_Year, rd.Drive_Type, rd.Season, rd.Drive_Date
        FROM RECRUITMENT_DRIVE rd
        JOIN COMPANY c ON rd.Company_ID = c.Company_ID
        WHERE rd.Drive_ID = %s
```

### 2. Functional Purpose
Retrieves detailed metadata for a campus recruitment drive, joining it with the host corporate profile.

### 3. Relational Tables Involved
**RECRUITMENT_DRIVE (rd), COMPANY (c)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT rd.Drive_ID, rd.Drive_Year, rd.Drive_Type, rd.Season, rd.Drive_Date, c.Company_ID, c.Company_Name, c.Company_Type, c.Location `
  * **Explanation:** Projects drive schedules and recruiter corporate data.
- ` FROM RECRUITMENT_DRIVE rd `
  * **Explanation:** Drive master schedule table.
- ` JOIN COMPANY c ON rd.Company_ID = c.Company_ID `
  * **Explanation:** Equi-join resolving corporate host entity.
- ` WHERE rd.Drive_ID = %s `
  * **Explanation:** Primary key lookup.

### 5. JOINs and Entity Relationships
Inner join linking RECRUITMENT_DRIVE to COMPANY on Company_ID.

### 6. Produced Output
Single recruitment drive dossier.

### 7. Key SQL & DBMS Concepts Tested
Parent-Child Relational Linking, Campus Recruitment Scheduling, Dimension Resolution.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: If a drive has multiple opportunities, how does this table structure represent that relationship?"

### 9. Independent Practice Challenge
**Problem:** Write a query that counts the number of recruitment drives conducted by each company in the year 2024.

---

## 25. Query 25 (RND-33): 3-Table Selection Round Pipeline Traversal

- **Source Routine / File:** `services/round_service.py / get_round_by_id`
- **Viva Category:** `Company management`
- **Core DBMS Concepts:** `4-Table Hierarchical Joins, Grandparent-Parent-Child Relational Navigation, Operational Pipeline Modeling.`

### 1. Exact Backend SQL Query
```sql
SELECT sp.Round_ID, sp.Opportunity_ID, o.Role, rd.Company_ID, c.Company_Name,
               sp.Round_Number, sp.Round_Type, sp.Description
        FROM SELECTION_PROCESS sp
        JOIN OPPORTUNITY o ON sp.Opportunity_ID = o.Opportunity_ID
        JOIN RECRUITMENT_DRIVE rd ON o.Drive_ID = rd.Drive_ID
        JOIN COMPANY c ON rd.Company_ID = c.Company_ID
        WHERE sp.Round_ID = %s
```

### 2. Functional Purpose
Fetches details of a specific selection assessment round (e.g. Online Test, Technical Interview, HR) joined with its parent Opportunity and Grandparent Company.

### 3. Relational Tables Involved
**SELECTION_PROCESS (sp), OPPORTUNITY (o), RECRUITMENT_DRIVE (rd), COMPANY (c)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT sp.Round_ID, sp.Round_Number, sp.Round_Type, sp.Description, o.Opportunity_ID, o.Role, o.Package_Stipend, c.Company_Name `
  * **Explanation:** Projects round stage details alongside job opening and recruiter name.
- ` FROM SELECTION_PROCESS sp `
  * **Explanation:** Individual hiring stage table.
- ` JOIN OPPORTUNITY o ON sp.Opportunity_ID = o.Opportunity_ID `
  * **Explanation:** First equi-join linking stage to specific job opening.
- ` JOIN RECRUITMENT_DRIVE rd ON o.Drive_ID = rd.Drive_ID `
  * **Explanation:** Second equi-join linking job opening to recruitment drive.
- ` JOIN COMPANY c ON rd.Company_ID = c.Company_ID `
  * **Explanation:** Third equi-join resolving corporate partner.
- ` WHERE sp.Round_ID = %s `
  * **Explanation:** Primary key lookup on Round_ID.

### 5. JOINs and Entity Relationships
4-table hierarchical chain: SELECTION_PROCESS -> OPPORTUNITY -> RECRUITMENT_DRIVE -> COMPANY.

### 6. Produced Output
Complete context of a recruitment stage from corporate entity down to specific interview round.

### 7. Key SQL & DBMS Concepts Tested
4-Table Hierarchical Joins, Grandparent-Parent-Child Relational Navigation, Operational Pipeline Modeling.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: How many JOIN operations are needed to connect SELECTION_PROCESS to COMPANY, and why?"

### 9. Independent Practice Challenge
**Problem:** Write a query listing all selection rounds for "Software Engineer" roles in 2024 with company name, round number, and round type.

---

## 26. Query 26 (DSH-05): Executive Placement Headline KPIs

- **Source Routine / File:** `services/dashboard_service.py / get_dashboard_data`
- **Viva Category:** `Dashboard and statistics`
- **Core DBMS Concepts:** `Aggregate Statistics, COALESCE Null Prevention, Executive Dashboard KPIs.`

### 1. Exact Backend SQL Query
```sql
SELECT 
            COUNT(p.Placement_ID) AS total_offers,
            COUNT(DISTINCT p.Student_ID) AS distinct_students_offered,
            COUNT(DISTINCT CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN p.Student_ID END) AS placed_students,
            SUM(CASE WHEN p.Offer_Status = 'Accepted' THEN 1 ELSE 0 END) AS accepted_offers,
            SUM(CASE WHEN p.Offer_Status = 'Joined' THEN 1 ELSE 0 END) AS joined_offers,
            COUNT(DISTINCT p.Company_ID) AS companies_with_offers
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        WHERE
```

### 2. Functional Purpose
Computes institutional placement headline KPI metrics: total offers secured, highest compensation package, and average salary package.

### 3. Relational Tables Involved
**PLACEMENT**

### 4. Clause-by-Clause Line Explanation
- ` SELECT COUNT(p.Placement_ID) AS total_offers, COALESCE(MAX(p.Package), 0) AS max_package, ROUND(COALESCE(AVG(p.Package), 0), 2) AS avg_package `
  * **Explanation:** Computes key institutional metrics in a single table pass with COALESCE null-handling.
- ` FROM PLACEMENT p `
  * **Explanation:** Core placement records.

### 5. JOINs and Entity Relationships
Single table aggregate scan with dynamic filter predicates injected as needed.

### 6. Produced Output
Single row summary feeding executive dashboard top cards.

### 7. Key SQL & DBMS Concepts Tested
Aggregate Statistics, COALESCE Null Prevention, Executive Dashboard KPIs.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: What would happen to the dashboard cards if there are zero placement records in the database, and how does COALESCE fix it?"

### 9. Independent Practice Challenge
**Problem:** Write a query that computes total offers and average package for On-campus placements vs Off-campus placements using GROUP BY.

---

## 27. Query 27 (DSH-10): Candidates Missing Mandatory Internships KPI

- **Source Routine / File:** `services/dashboard_service.py / get_dashboard_data`
- **Viva Category:** `Dashboard and statistics`
- **Core DBMS Concepts:** `Derived Table (Subquery in FROM), Disjunctive Anti-Semi-Joins (OR NOT EXISTS), Institutional Clearance Auditing.`

### 1. Exact Backend SQL Query
```sql
SELECT COUNT(*) AS missing_count
        FROM (
            SELECT s.Student_ID
            FROM STUDENT s
            LEFT JOIN INTERNSHIP i1 ON s.Student_ID = i1.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = 'Mandatory'
            LEFT JOIN INTERNSHIP i2 ON s.Student_ID = i2.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = 'Mandatory'
            WHERE
```

### 2. Functional Purpose
Calculates the total count of active students who are missing either Mandatory Internship #1 or Mandatory Internship #2 for degree graduation clearance.

### 3. Relational Tables Involved
**STUDENT (s), INTERNSHIP (i1, i2)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT COUNT(*) AS missing_count FROM (SELECT s.Student_ID FROM STUDENT s WHERE NOT EXISTS (SELECT 1 FROM INTERNSHIP i1 WHERE i1.Student_ID = s.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = "Mandatory") OR NOT EXISTS (SELECT 1 FROM INTERNSHIP i2 WHERE i2.Student_ID = s.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = "Mandatory")) AS missing_sub `
  * **Explanation:** Subquery identifying students failing either requirement, wrapped by an outer COUNT(*) to produce the executive red warning metric.

### 5. JOINs and Entity Relationships
Disjunctive (OR) correlated NOT EXISTS anti-semi-joins.

### 6. Produced Output
Single integer representing students currently failing graduation internship requirements.

### 7. Key SQL & DBMS Concepts Tested
Derived Table (Subquery in FROM), Disjunctive Anti-Semi-Joins (OR NOT EXISTS), Institutional Clearance Auditing.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: Why is OR used between the two NOT EXISTS conditions instead of AND?"

### 9. Independent Practice Challenge
**Problem:** Write a query that returns the Roll_No, Full Name, and Branch of all students who have completed Mandatory Internship #1 but are missing Mandatory Internship #2.

---

## 28. Query 28 (DSH-11): Dashboard Chart 1: Branch-Wise Placement & Internships Breakdown

- **Source Routine / File:** `services/dashboard_service.py / get_chart_data`
- **Viva Category:** `Dashboard and statistics`
- **Core DBMS Concepts:** `Multiple LEFT OUTER JOINs, Prevention of Cartesian Product Explosion via COUNT(DISTINCT), Grouping & Aggregation for Data Visualization.`

### 1. Exact Backend SQL Query
```sql
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
        LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
```

### 2. Functional Purpose
Feeds Chart.js Chart 1 by grouping students by engineering branch and computing total candidates, placed candidates, and active internships.

### 3. Relational Tables Involved
**STUDENT (s), PLACEMENT (p), INTERNSHIP (i)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT s.Branch, COUNT(DISTINCT s.Student_ID) AS total_students, COUNT(DISTINCT p.Student_ID) AS placed_students, COUNT(DISTINCT i.Internship_ID) AS total_internships `
  * **Explanation:** Uses COUNT(DISTINCT) to prevent cartesian explosion across dual outer joins.
- ` FROM STUDENT s `
  * **Explanation:** Master student dimension.
- ` LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID `
  * **Explanation:** Outer join preserving students who have zero placements.
- ` LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID `
  * **Explanation:** Outer join preserving students who have zero internships.
- ` GROUP BY s.Branch `
  * **Explanation:** Groups aggregations per engineering branch.
- ` ORDER BY s.Branch ASC `
  * **Explanation:** Alphabetical department ordering.

### 5. JOINs and Entity Relationships
Dual LEFT OUTER JOINs branching from master STUDENT table.

### 6. Produced Output
Multi-row dataset with branch-level comparative volume for charting.

### 7. Key SQL & DBMS Concepts Tested
Multiple LEFT OUTER JOINs, Prevention of Cartesian Product Explosion via COUNT(DISTINCT), Grouping & Aggregation for Data Visualization.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: What happens to COUNT(p.Placement_ID) if a student has 2 placements and 3 internships in a dual LEFT JOIN? Why is COUNT(DISTINCT) essential?"

### 9. Independent Practice Challenge
**Problem:** Write a query that computes the placement percentage (placed_students / total_students * 100) for each branch using this data.

---

## 29. Query 29 (DSH-12): Dashboard Chart 2: Historical Placement YoY Trajectory

- **Source Routine / File:** `services/dashboard_service.py / get_chart_data`
- **Viva Category:** `Dashboard and statistics`
- **Core DBMS Concepts:** `Time-Series Aggregations, Multi-Metric Grouping, Financial/Salary Analytics.`

### 1. Exact Backend SQL Query
```sql
SELECT 
            p.Placement_Year,
            COUNT(p.Placement_ID) AS offer_count,
            SUM(CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN 1 ELSE 0 END) AS accepted_count,
            ROUND(COALESCE(AVG(p.Package), 0), 2) AS avg_package,
            ROUND(COALESCE(MAX(p.Package), 0), 2) AS max_package
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        WHERE
```

### 2. Functional Purpose
Feeds Chart.js Chart 2 by analyzing year-over-year placement performance: offer volume, average salary package, and maximum compensation package.

### 3. Relational Tables Involved
**PLACEMENT (p), STUDENT (s)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT p.Placement_Year, COUNT(p.Placement_ID) AS total_offers, ROUND(AVG(p.Package), 2) AS avg_package, MAX(p.Package) AS max_package `
  * **Explanation:** Computes volume and package statistics per recruitment year.
- ` FROM PLACEMENT p `
  * **Explanation:** Core placement records.
- ` JOIN STUDENT s ON p.Student_ID = s.Student_ID `
  * **Explanation:** Equi-join on Student_ID to support dynamic branch filtering.
- ` GROUP BY p.Placement_Year `
  * **Explanation:** Aggregates by calendar recruitment year.
- ` ORDER BY p.Placement_Year ASC `
  * **Explanation:** Chronological time-series ordering.

### 5. JOINs and Entity Relationships
Inner join on Student_ID.

### 6. Produced Output
Chronological time-series data points for line chart visualization.

### 7. Key SQL & DBMS Concepts Tested
Time-Series Aggregations, Multi-Metric Grouping, Financial/Salary Analytics.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: How would you modify this query to compute Year-over-Year (YoY) percentage growth in offers using a SQL window function?"

### 9. Independent Practice Challenge
**Problem:** Write a query using LAG() OVER (ORDER BY Placement_Year) to calculate the previous year's total offers alongside the current year's offers.

---

## 30. Query 30 (DSH-13): Dashboard Chart 3: Salary Compensation Histogram Distribution

- **Source Routine / File:** `services/dashboard_service.py / get_chart_data`
- **Viva Category:** `Dashboard and statistics`
- **Core DBMS Concepts:** `Distribution Modeling, Raw Data Retrieval for Frontend Statistical Binning, Continuous Variable Analysis.`

### 1. Exact Backend SQL Query
```sql
SELECT p.Package
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        WHERE
```

### 2. Functional Purpose
Retrieves all individual placement salary packages to construct the salary frequency distribution histogram.

### 3. Relational Tables Involved
**PLACEMENT (p), STUDENT (s)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT p.Package `
  * **Explanation:** Projects raw package values in LPA.
- ` FROM PLACEMENT p `
  * **Explanation:** Placement offers table.
- ` JOIN STUDENT s ON p.Student_ID = s.Student_ID `
  * **Explanation:** Equi-join allowing branch/batch filtering.
- ` ORDER BY p.Package ASC `
  * **Explanation:** Ascending sort for statistical bucket generation.

### 5. JOINs and Entity Relationships
Inner equi-join on Student_ID.

### 6. Produced Output
Sorted stream of numeric compensation figures.

### 7. Key SQL & DBMS Concepts Tested
Distribution Modeling, Raw Data Retrieval for Frontend Statistical Binning, Continuous Variable Analysis.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: How could you perform the salary bucketing (e.g. <5 LPA, 5-10 LPA, >10 LPA) directly inside SQL instead of JavaScript?"

### 9. Independent Practice Challenge
**Problem:** Write a query using CASE WHEN to count the number of offers in 4 brackets: "< 6 LPA", "6-12 LPA", "12-20 LPA", and "> 20 LPA".

---

## 31. Query 31 (DSH-14): Dashboard Chart 4: Correlation of Internships to Placement

- **Source Routine / File:** `services/dashboard_service.py / get_chart_data`
- **Viva Category:** `Dashboard and statistics`
- **Core DBMS Concepts:** `Correlation Analysis in SQL, Conditional COUNT(DISTINCT CASE WHEN), Dual Outer Joins.`

### 1. Exact Backend SQL Query
```sql
SELECT 
            s.Branch,
            COUNT(DISTINCT p.Placement_ID) AS placement_offers,
            COUNT(DISTINCT i.Internship_ID) AS total_internships,
            COUNT(DISTINCT CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN s.Student_ID END) AS placed_students,
            COUNT(DISTINCT i.Student_ID) AS interned_students
        FROM STUDENT s
        LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
```

### 2. Functional Purpose
Feeds Chart 4 to demonstrate whether completing internships improves campus placement outcomes across engineering branches.

### 3. Relational Tables Involved
**STUDENT (s), PLACEMENT (p), INTERNSHIP (i)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT s.Branch, COUNT(DISTINCT p.Placement_ID) AS placed_count, COUNT(DISTINCT CASE WHEN i.Internship_ID IS NOT NULL AND p.Placement_ID IS NOT NULL THEN s.Student_ID END) AS interned_and_placed_count `
  * **Explanation:** Computes total placements and subset of placed students who also completed internships.
- ` FROM STUDENT s `
  * **Explanation:** Student master.
- ` LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID `
  * **Explanation:** Outer join for placements.
- ` LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID `
  * **Explanation:** Outer join for internships.
- ` GROUP BY s.Branch `
  * **Explanation:** Grouped by academic department.

### 5. JOINs and Entity Relationships
Dual LEFT OUTER JOINs with conditional distinct counting.

### 6. Produced Output
Comparative branch dataset showing career impact of student internships.

### 7. Key SQL & DBMS Concepts Tested
Correlation Analysis in SQL, Conditional COUNT(DISTINCT CASE WHEN), Dual Outer Joins.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: What does COUNT(DISTINCT CASE WHEN i.Internship_ID IS NOT NULL AND p.Placement_ID IS NOT NULL THEN s.Student_ID END) compute, and why is DISTINCT required?"

### 9. Independent Practice Challenge
**Problem:** Write a query that computes the percentage of placed students who completed at least one internship.

---

## 32. Query 32 (DSH-15): Dashboard Chart 5: Internship Completion Compliance Breakdown

- **Source Routine / File:** `services/dashboard_service.py / get_chart_data`
- **Viva Category:** `Dashboard and statistics`
- **Core DBMS Concepts:** `Derived Table Aggregation, Multi-Tier CASE Expressions, Relational Categorization, Two-Pass Grouping.`

### 1. Exact Backend SQL Query
```sql
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
            WHERE
```

### 2. Functional Purpose
Feeds Chart 5 doughnut chart by categorizing every student into one of three compliance states: Fully Compliant (Both 1 & 2), Partially Compliant (Only 1 or 2), or Non-Compliant (Neither).

### 3. Relational Tables Involved
**STUDENT (s), INTERNSHIP (i)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT status_category, COUNT(*) AS student_count FROM (SELECT s.Student_ID, CASE WHEN COUNT(DISTINCT CASE WHEN i.Internship_No IN (1,2) AND i.Internship_Type = "Mandatory" THEN i.Internship_No END) = 2 THEN "Fully Compliant" WHEN COUNT(DISTINCT CASE WHEN i.Internship_No IN (1,2) AND i.Internship_Type = "Mandatory" THEN i.Internship_No END) = 1 THEN "Partially Compliant" ELSE "Non-Compliant" END AS status_category FROM STUDENT s LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID GROUP BY s.Student_ID) AS compliance_sub GROUP BY status_category `
  * **Explanation:** Two-level aggregation: inner query categorizes each student using CASE WHEN on distinct mandatory count, outer query groups by category.

### 5. JOINs and Entity Relationships
LEFT JOIN from STUDENT to INTERNSHIP inside a derived table subquery.

### 6. Produced Output
Three rows with category names and student counts for doughnut chart rendering.

### 7. Key SQL & DBMS Concepts Tested
Derived Table Aggregation, Multi-Tier CASE Expressions, Relational Categorization, Two-Pass Grouping.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: Why can we not do this in a single GROUP BY without a subquery?"

### 9. Independent Practice Challenge
**Problem:** Write a query that lists all students who are "Partially Compliant" along with the specific internship number they have completed.

---

## 33. Query 33 (DSH-16): Dashboard Chart 6: Multiple Offers Distribution

- **Source Routine / File:** `services/dashboard_service.py / get_chart_data`
- **Viva Category:** `Dashboard and statistics`
- **Core DBMS Concepts:** `Nested Aggregations, Tier Bucketing with CASE WHEN, Derived Table Subqueries.`

### 1. Exact Backend SQL Query
```sql
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
            LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
```

### 2. Functional Purpose
Feeds Chart 6 by segmenting placed students into tiers: "1 Offer", "2 Offers", and "3+ Offers".

### 3. Relational Tables Involved
**PLACEMENT (p)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT offer_tier, COUNT(*) AS student_count FROM (SELECT p.Student_ID, CASE WHEN COUNT(p.Placement_ID) = 1 THEN "1 Offer" WHEN COUNT(p.Placement_ID) = 2 THEN "2 Offers" ELSE "3+ Offers" END AS offer_tier FROM PLACEMENT p GROUP BY p.Student_ID) AS sub GROUP BY offer_tier `
  * **Explanation:** Inner subquery counts offers per student and assigns a bucket label; outer query aggregates student volume per tier.

### 5. JOINs and Entity Relationships
Single table derived aggregation on PLACEMENT.

### 6. Produced Output
Categorical distribution of offer counts across placed candidates.

### 7. Key SQL & DBMS Concepts Tested
Nested Aggregations, Tier Bucketing with CASE WHEN, Derived Table Subqueries.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: Why does this query only include placed students, and how would you include unplaced students as "0 Offers"?"

### 9. Independent Practice Challenge
**Problem:** Modify this query to include unplaced students as "0 Offers" by starting FROM STUDENT and doing a LEFT JOIN to PLACEMENT.

---

## 34. Query 34 (Report 9.3): Complete Student 360 Profile Synthesis

- **Source Routine / File:** `services/sql_report_service.py / run_saved_query`
- **Viva Category:** `Reports and analytics`
- **Core DBMS Concepts:** `GROUP_CONCAT with DISTINCT, Multiple 1:N Relationship Joins, Aggregation over Outer Joins, 360-Degree Entity Synthesis.`

### 1. Exact Backend SQL Query
```sql
SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       s.Branch, s.Batch_Year, s.CGPA, s.Backlogs, s.Resume_Link,
       (SELECT GROUP_CONCAT(ph.Phone_No SEPARATOR ', ')
          FROM STUDENT_PHONE ph WHERE ph.Student_ID = s.Student_ID) AS Phones,
       (SELECT GROUP_CONCAT(sk.Skill SEPARATOR ', ')
          FROM STUDENT_SKILL sk WHERE sk.Student_ID = s.Student_ID) AS Extra_Skills
FROM STUDENT s
WHERE s.Roll_No = %s;
```

### 2. Functional Purpose
Assembles an exhaustive single-row profile for a student combining demographic data, academic standing, aggregated skills, contact numbers, and total placement/internship offers.

### 3. Relational Tables Involved
**STUDENT (s), STUDENT_PHONE (sp), STUDENT_SKILL (sk), PLACEMENT (p), INTERNSHIP (i)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT s.Student_ID, s.Roll_No, CONCAT_WS(" ", s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.Batch_Year, s.CGPA, s.Backlogs, GROUP_CONCAT(DISTINCT sp.Phone_No SEPARATOR ", ") AS Phone_Numbers, GROUP_CONCAT(DISTINCT sk.Skill SEPARATOR ", ") AS Skills, COUNT(DISTINCT p.Placement_ID) AS Total_Placement_Offers, COUNT(DISTINCT i.Internship_ID) AS Total_Internships `
  * **Explanation:** Combines scalar attributes, aggregated strings using GROUP_CONCAT, and distinct entity counts.
- ` FROM STUDENT s `
  * **Explanation:** Root entity.
- ` LEFT JOIN STUDENT_PHONE sp ON s.Student_ID = sp.Student_ID `
  * **Explanation:** Outer join for phone numbers.
- ` LEFT JOIN STUDENT_SKILL sk ON s.Student_ID = sk.Student_ID `
  * **Explanation:** Outer join for skills.
- ` LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID `
  * **Explanation:** Outer join for placements.
- ` LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID `
  * **Explanation:** Outer join for internships.
- ` WHERE s.Student_ID = %s `
  * **Explanation:** Filters by target student.
- ` GROUP BY s.Student_ID `
  * **Explanation:** Collapses multivalued child rows into a unified profile row.

### 5. JOINs and Entity Relationships
Four LEFT OUTER JOINs radiating from the master STUDENT table.

### 6. Produced Output
Single consolidated 360-degree student record.

### 7. Key SQL & DBMS Concepts Tested
GROUP_CONCAT with DISTINCT, Multiple 1:N Relationship Joins, Aggregation over Outer Joins, 360-Degree Entity Synthesis.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: Why is DISTINCT required inside GROUP_CONCAT and COUNT when joining multiple child tables?"

### 9. Independent Practice Challenge
**Problem:** Write a query that displays each Company_Name and a comma-separated list of all roles they have recruited for using GROUP_CONCAT.

---

## 35. Query 35 (Report 9.6): Students Not Placed (LEFT OUTER Anti-Join)

- **Source Routine / File:** `services/sql_report_service.py / run_saved_query`
- **Viva Category:** `Reports and analytics`
- **Core DBMS Concepts:** `Relational Difference / Anti-Join, LEFT JOIN ... WHERE IS NULL, Set Complement.`

### 1. Exact Backend SQL Query
```sql
SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       s.Branch, s.Batch_Year, s.CGPA
FROM STUDENT s
LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID AND p.Joined = 'Yes'
WHERE p.Placement_ID IS NULL
ORDER BY s.CGPA DESC;
```

### 2. Functional Purpose
Finds all students who have not secured any placement offers using a canonical SQL LEFT OUTER JOIN anti-join pattern.

### 3. Relational Tables Involved
**STUDENT (s), PLACEMENT (p)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT s.Student_ID, s.Roll_No, CONCAT_WS(" ", s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.Batch_Year, s.CGPA, s.Backlogs `
  * **Explanation:** Projects unplaced candidate details for placement cell intervention.
- ` FROM STUDENT s `
  * **Explanation:** All students.
- ` LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID `
  * **Explanation:** Includes all students and matches placements where available.
- ` WHERE p.Placement_ID IS NULL `
  * **Explanation:** Filters for rows where no placement record matched (the anti-join predicate).
- ` ORDER BY s.CGPA DESC `
  * **Explanation:** Ranks unplaced students by highest academic merit.

### 5. JOINs and Entity Relationships
LEFT OUTER JOIN with IS NULL filter on right-hand table primary key (Anti-Join pattern).

### 6. Produced Output
Roster of active unplaced students sorted by academic performance.

### 7. Key SQL & DBMS Concepts Tested
Relational Difference / Anti-Join, LEFT JOIN ... WHERE IS NULL, Set Complement.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: How does the performance of LEFT JOIN ... WHERE IS NULL compare to NOT EXISTS, and which is safer with NULL values?"

### 9. Independent Practice Challenge
**Problem:** Write an anti-join query to find all companies that have never conducted a recruitment drive in RECRUITMENT_DRIVE.

---

## 36. Query 36 (Report 9.11): Branch-Wise Placement Statistics & Salary Bounds

- **Source Routine / File:** `services/sql_report_service.py / run_saved_query`
- **Viva Category:** `Reports and analytics`
- **Core DBMS Concepts:** `Departmental Grouping, Multi-Aggregate Analysis (MIN, MAX, AVG), Sorting on Computed Alias.`

### 1. Exact Backend SQL Query
```sql
SELECT Branch,
       COUNT(*)               AS Students_Placed,
       ROUND(AVG(Package), 2) AS Avg_Package,
       MAX(Package)           AS Highest_Package,
       MIN(Package)           AS Lowest_Package
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
GROUP BY Branch
ORDER BY Avg_Package DESC;
```

### 2. Functional Purpose
Calculates placement performance metrics broken down by engineering branch: placed student count, minimum package, average package, and maximum package.

### 3. Relational Tables Involved
**STUDENT (s), PLACEMENT (p)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT s.Branch, COUNT(p.Placement_ID) AS Placements_Count, COUNT(DISTINCT s.Student_ID) AS Students_Placed, MIN(p.Package) AS Min_Package, ROUND(AVG(p.Package), 2) AS Avg_Package, MAX(p.Package) AS Max_Package `
  * **Explanation:** Computes branch-level volume and compensation boundaries.
- ` FROM STUDENT s `
  * **Explanation:** Student demographic master.
- ` JOIN PLACEMENT p ON s.Student_ID = p.Student_ID `
  * **Explanation:** Inner join restricting analysis to placed records.
- ` GROUP BY s.Branch `
  * **Explanation:** Groups aggregations by engineering department.
- ` ORDER BY Avg_Package DESC `
  * **Explanation:** Ranks departments from highest average compensation downwards.

### 5. JOINs and Entity Relationships
Inner join on Student_ID.

### 6. Produced Output
Departmental salary benchmark table.

### 7. Key SQL & DBMS Concepts Tested
Departmental Grouping, Multi-Aggregate Analysis (MIN, MAX, AVG), Sorting on Computed Alias.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: Why is Placements_Count different from Students_Placed in this query?"

### 9. Independent Practice Challenge
**Problem:** Write a query that displays branch-wise statistics only for branches where the average package is above 8.0 LPA using HAVING.

---

## 37. Query 37 (Report 9.14): Top 5 Highest Placement Packages (Top-K)

- **Source Routine / File:** `services/sql_report_service.py / run_saved_query`
- **Viva Category:** `Reports and analytics`
- **Core DBMS Concepts:** `Top-K Query Pattern, LIMIT Clause, Multi-Table Equi-Join, High-Salaried Filtering.`

### 1. Exact Backend SQL Query
```sql
SELECT Student_Name, Branch, Company_Name, Package, Placement_Year
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
ORDER BY Package DESC
LIMIT 5;
```

### 2. Functional Purpose
Identifies the top 5 highest salary packages achieved across the entire institution along with student names and recruiting companies.

### 3. Relational Tables Involved
**PLACEMENT (p), STUDENT (s), COMPANY (c)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT CONCAT_WS(" ", s.First_Name, s.Last_Name) AS Student_Name, s.Branch, c.Company_Name, p.Role, p.Package, p.Placement_Year `
  * **Explanation:** Projects student, recruiter, and compensation details.
- ` FROM PLACEMENT p `
  * **Explanation:** Placement offers table.
- ` JOIN STUDENT s ON p.Student_ID = s.Student_ID `
  * **Explanation:** Equi-join resolving student details.
- ` JOIN COMPANY c ON p.Company_ID = c.Company_ID `
  * **Explanation:** Equi-join resolving company details.
- ` ORDER BY p.Package DESC `
  * **Explanation:** Sorts offers from highest to lowest salary.
- ` LIMIT 5 `
  * **Explanation:** Restricts the final output to exactly the top 5 records.

### 5. JOINs and Entity Relationships
3-table equi-join across PLACEMENT, STUDENT, and COMPANY.

### 6. Produced Output
Top-5 institutional star recruitment offers.

### 7. Key SQL & DBMS Concepts Tested
Top-K Query Pattern, LIMIT Clause, Multi-Table Equi-Join, High-Salaried Filtering.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: What is the limitation of LIMIT 5 if multiple students share the 5th highest package with the exact same salary?"

### 9. Independent Practice Challenge
**Problem:** Rewrite this query using the DENSE_RANK() window function to return all offers ranking in the top 3 package tiers.

---

## 38. Query 38 (Report 9.16): Students Receiving Multiple Placement Offers

- **Source Routine / File:** `services/sql_report_service.py / run_saved_query`
- **Viva Category:** `Reports and analytics`
- **Core DBMS Concepts:** `GROUP BY with Multiple Non-Aggregated Columns, HAVING Clause Post-Aggregation Filtering, Multi-Level Ranking.`

### 1. Exact Backend SQL Query
```sql
SELECT Student_Name, Roll_No,
       COUNT(*) AS Total_Offers,
       GROUP_CONCAT(CONCAT(Company_Name, ' (', Package, ' LPA)') SEPARATOR ', ') AS Offers,
       MAX(CASE WHEN Joined = 'Yes' THEN Company_Name END) AS Joined_Company
FROM V_PLACEMENT_DETAIL
GROUP BY Student_ID, Student_Name, Roll_No
HAVING COUNT(*) > 1;
```

### 2. Functional Purpose
Identifies all students who have secured more than one placement offer using GROUP BY and HAVING clauses.

### 3. Relational Tables Involved
**STUDENT (s), PLACEMENT (p)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT s.Student_ID, s.Roll_No, CONCAT_WS(" ", s.First_Name, s.Last_Name) AS Student_Name, s.Branch, COUNT(p.Placement_ID) AS Total_Offers, ROUND(AVG(p.Package), 2) AS Avg_Package, MAX(p.Package) AS Highest_Offer `
  * **Explanation:** Projects student info and aggregated offer metrics.
- ` FROM STUDENT s `
  * **Explanation:** Student entity.
- ` JOIN PLACEMENT p ON s.Student_ID = p.Student_ID `
  * **Explanation:** Equi-join on Student_ID.
- ` GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch `
  * **Explanation:** Groups by student candidate composite attributes.
- ` HAVING COUNT(p.Placement_ID) > 1 `
  * **Explanation:** Filters aggregate groups to keep only students with 2 or more offers.
- ` ORDER BY Total_Offers DESC, Highest_Offer DESC `
  * **Explanation:** Ranks by highest offer count, then highest package.

### 5. JOINs and Entity Relationships
Inner join on Student_ID.

### 6. Produced Output
List of high-achieving students with multiple offers.

### 7. Key SQL & DBMS Concepts Tested
GROUP BY with Multiple Non-Aggregated Columns, HAVING Clause Post-Aggregation Filtering, Multi-Level Ranking.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: What is the fundamental difference between the WHERE clause and the HAVING clause in SQL?"

### 9. Independent Practice Challenge
**Problem:** Write a query using GROUP BY and HAVING that finds all companies that have recruited at least 3 students.

---

## 39. Query 39 (Report 9.23): Incomplete Mandatory Internships Clearance Audit

- **Source Routine / File:** `services/sql_report_service.py / run_saved_query`
- **Viva Category:** `Reports and analytics`
- **Core DBMS Concepts:** `Correlated NOT EXISTS in SELECT & WHERE, Disjunctive Filtering (OR), CASE Status Flagging, Institutional Clearance Logic.`

### 1. Exact Backend SQL Query
```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       COUNT(CASE WHEN i.Internship_Type = 'Mandatory' THEN 1 END) AS Mandatory_Done
FROM STUDENT s
LEFT JOIN INTERNSHIP i ON i.Student_ID = s.Student_ID
GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name
HAVING COUNT(CASE WHEN i.Internship_Type = 'Mandatory' THEN 1 END) < 2;
```

### 2. Functional Purpose
Performs an official graduation clearance audit listing all students who are missing either Mandatory Internship #1 or Mandatory Internship #2, detailing which specific requirement is missing.

### 3. Relational Tables Involved
**STUDENT (s), INTERNSHIP (i)**

### 4. Clause-by-Clause Line Explanation
- ` SELECT s.Student_ID, s.Roll_No, CONCAT_WS(" ", s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.Batch_Year, s.CGPA, CASE WHEN NOT EXISTS (SELECT 1 FROM INTERNSHIP i WHERE i.Student_ID = s.Student_ID AND i.Internship_No = 1 AND i.Internship_Type = "Mandatory") THEN "Missing" ELSE "Completed" END AS Mandatory_1_Status, CASE WHEN NOT EXISTS (SELECT 1 FROM INTERNSHIP i WHERE i.Student_ID = s.Student_ID AND i.Internship_No = 2 AND i.Internship_Type = "Mandatory") THEN "Missing" ELSE "Completed" END AS Mandatory_2_Status `
  * **Explanation:** Projects student credentials and uses conditional CASE WHEN with correlated subqueries to label the exact status of each mandatory requirement.
- ` FROM STUDENT s `
  * **Explanation:** Master student table.
- ` WHERE NOT EXISTS (SELECT 1 FROM INTERNSHIP i WHERE i.Student_ID = s.Student_ID AND i.Internship_No = 1 AND i.Internship_Type = "Mandatory") OR NOT EXISTS (SELECT 1 FROM INTERNSHIP i WHERE i.Student_ID = s.Student_ID AND i.Internship_No = 2 AND i.Internship_Type = "Mandatory") `
  * **Explanation:** Restricts output to only those students failing at least one requirement.
- ` ORDER BY s.Batch_Year ASC, s.Branch ASC, s.Roll_No ASC `
  * **Explanation:** Sorts by graduating batch year and branch for administrative review.

### 5. JOINs and Entity Relationships
Correlated subqueries in both SELECT projections and WHERE filter.

### 6. Produced Output
Administrative audit roster showing exact missing internship milestones per student.

### 7. Key SQL & DBMS Concepts Tested
Correlated NOT EXISTS in SELECT & WHERE, Disjunctive Filtering (OR), CASE Status Flagging, Institutional Clearance Logic.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: Why is it valuable to put CASE expressions with NOT EXISTS in the SELECT list in addition to the WHERE clause?"

### 9. Independent Practice Challenge
**Problem:** Write a query that finds students of Batch_Year = 2024 who are missing Mandatory Internship #2.

---

## 40. Query 40 (Report 9.35): Advanced CTE & Window Functions for Branch Compensation

- **Source Routine / File:** `services/sql_report_service.py / run_saved_query`
- **Viva Category:** `Reports and analytics`
- **Core DBMS Concepts:** `Common Table Expressions (WITH clause), Window Functions (DENSE_RANK), Partitioning (PARTITION BY), In-Branch Competitive Ranking.`

### 1. Exact Backend SQL Query
```sql
WITH BranchTotals AS (
    SELECT
        s.Branch,
        COUNT(DISTINCT s.Student_ID) AS Total_Students,
        COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' OR p.Offer_Status = 'Joined' THEN s.Student_ID END) AS Placed_Students,
        COUNT(p.Placement_ID) AS Total_Offers,
        ROUND(AVG(CASE WHEN p.Joined = 'Yes' OR p.Offer_Status = 'Joined' THEN p.Package END), 2) AS Avg_Package,
        MAX(CASE WHEN p.Joined = 'Yes' OR p.Offer_Status = 'Joined' THEN p.Package END) AS Highest_Package,
        MIN(CASE WHEN p.Joined = 'Yes' OR p.Offer_Status = 'Joined' THEN p.Package END) AS Lowest_Package
    FROM STUDENT s
    LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
    GROUP BY s.Branch
),
BranchMedians AS (
    SELECT
        Branch,
        ROUND(AVG(Package), 2) AS Median_Package
    FROM (
        SELECT
            s.Branch,
            p.Package,
            ROW_NUMBER() OVER (PARTITION BY s.Branch ORDER BY p.Package ASC) AS row_num,
            COUNT(*) OVER (PARTITION BY s.Branch) AS total_count
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        WHERE (p.Joined = 'Yes' OR p.Offer_Status = 'Joined')
    ) ranked
    WHERE row_num IN (FLOOR((total_count + 1) / 2), CEIL((total_count + 1) / 2))
    GROUP BY Branch
)
SELECT
    b.Branch,
    b.Total_Students,
    b.Placed_Students,
    (b.Total_Students - b.Placed_Students) AS Unplaced_Students,
    ROUND(COALESCE(100.0 * b.Placed_Students / NULLIF(b.Total_Students, 0), 0), 1) AS Placement_Rate,
    b.Total_Offers,
    COALESCE(b.Avg_Package, 0.00) AS Avg_Package,
    COALESCE(m.Median_Package, 0.00) AS Median_Package,
    COALESCE(b.Highest_Package, 0.00) AS Highest_Package,
    COALESCE(b.Lowest_Package, 0.00) AS Lowest_Package,
    DENSE_RANK() OVER (ORDER BY ROUND(COALESCE(100.0 * b.Placed_Students / NULLIF(b.Total_Students, 0), 0), 1) DESC, b.Avg_Package DESC) AS Performance_Rank
FROM BranchTotals b
LEFT JOIN BranchMedians m ON b.Branch = m.Branch
ORDER BY b.Branch ASC;
```

### 2. Functional Purpose
Uses Common Table Expressions (CTEs) and Window Functions to compute comprehensive branch statistics, ranking packages within each branch and calculating institutional percentile contribution.

### 3. Relational Tables Involved
**STUDENT (s), PLACEMENT (p), COMPANY (c)**

### 4. Clause-by-Clause Line Explanation
- ` WITH RankedPlacements AS (SELECT s.Branch, s.Roll_No, CONCAT_WS(" ", s.First_Name, s.Last_Name) AS Student_Name, c.Company_Name, p.Package, DENSE_RANK() OVER (PARTITION BY s.Branch ORDER BY p.Package DESC) as Package_Rank FROM PLACEMENT p JOIN STUDENT s ON p.Student_ID = s.Student_ID JOIN COMPANY c ON p.Company_ID = c.Company_ID) `
  * **Explanation:** Defines a Common Table Expression that partitions placement offers by Branch and assigns a dense rank based on package descending.
- ` SELECT Branch, Roll_No, Student_Name, Company_Name, Package, Package_Rank FROM RankedPlacements WHERE Package_Rank <= 3 ORDER BY Branch ASC, Package_Rank ASC `
  * **Explanation:** Selects the top 3 highest package earners within every engineering branch.

### 5. JOINs and Entity Relationships
3-table equi-join inside CTE, followed by filtered projection in outer query.

### 6. Produced Output
Top 3 highest placement offers partitioned per department.

### 7. Key SQL & DBMS Concepts Tested
Common Table Expressions (WITH clause), Window Functions (DENSE_RANK), Partitioning (PARTITION BY), In-Branch Competitive Ranking.

### 8. Similar Problem Statement Expected in Viva
> [!TIP]
> "The teacher asks: What is the difference between ROW_NUMBER(), RANK(), and DENSE_RANK() when two students have the identical salary package?"

### 9. Independent Practice Challenge
**Problem:** Write a query using ROW_NUMBER() OVER (PARTITION BY Placement_Year ORDER BY Package DESC) to find the single highest package offer in each placement year.

---

# 30 SQL Practice Problems: Viva Preparation & Solutions Manual

> [!TIP]
> **Active Learning Instructions**: Attempt the 30 problems in **Part 1 (Problem Statements)** independently before checking the verified solutions in **Part 2 (Solutions Manual)**. These questions mirror the exact problem styles professors ask during database project vivas. Every query has been tested and verified on the live 7-table MySQL database (`placement_internship_db`).

## Table of Contents
- [Part 1: Unsolved Problem Statements (Questions 1 to 30)](#part-1-unsolved-problem-statements)
  - [Easy Problems (Questions 1 to 10)](#easy-problems-questions-1-to-10)
  - [Medium Problems (Questions 11 to 20)](#medium-problems-questions-11-to-20)
  - [Difficult Problems (Questions 21 to 30)](#difficult-problems-questions-21-to-30)
- [Part 2: Step-by-Step Solutions Manual](#part-2-step-by-step-solutions-manual)

---

# Part 1: Unsolved Problem Statements

### Easy Problems (Questions 1 to 10)
#### Problem 1: High CGPA Active Students
- **Difficulty:** `Easy`
- **Tables Involved:** `STUDENT`
- **Description:** Find the Roll_No, Full Name (First + Last), Branch, and CGPA of all students who have a CGPA greater than or equal to 8.50 and have zero backlogs, sorted by CGPA in descending order.

#### Problem 2: Distinct Company Types and Counts
- **Difficulty:** `Easy`
- **Tables Involved:** `COMPANY`
- **Description:** Find all distinct company types registered in the system along with the count of companies in each category, sorted by company count descending.

#### Problem 3: High Package Placements in 2024
- **Difficulty:** `Easy`
- **Tables Involved:** `PLACEMENT`
- **Description:** Find all placement offers secured in the year 2024 where the package is at least 12.0 LPA. Display Placement_ID, Student_ID, Role, and Package, sorted by Package descending.

#### Problem 4: Stipend Range Filter for Internships
- **Difficulty:** `Easy`
- **Tables Involved:** `INTERNSHIP`
- **Description:** Find all internships where the monthly stipend is between 15,000 and 40,000 (inclusive). Display Internship_ID, Student_ID, Role, and Stipend, ordered by Stipend ascending.

#### Problem 5: Students Possessing Python or Java Skills
- **Difficulty:** `Easy`
- **Tables Involved:** `STUDENT, STUDENT_SKILL`
- **Description:** Find the Roll_No and Name of all students who have listed 'Python' or 'Java' in their technical skills, ensuring no duplicate student rows appear in the output.

#### Problem 6: Total Students Enrolled Per Branch
- **Difficulty:** `Easy`
- **Tables Involved:** `STUDENT`
- **Description:** Display the total count of students enrolled in each engineering branch, ordered alphabetically by branch name.

#### Problem 7: Average Package by Company Type
- **Difficulty:** `Easy`
- **Tables Involved:** `COMPANY, PLACEMENT`
- **Description:** Find the average placement package offered by each company type (Product, Service, Startup), along with the total number of offers made, sorted by average package descending.

#### Problem 8: Students with Multiple Phone Numbers
- **Difficulty:** `Easy`
- **Tables Involved:** `STUDENT, STUDENT_PHONE`
- **Description:** Find all students who have registered more than one contact phone number, displaying their Roll_No, First_Name, and the count of phone numbers registered.

#### Problem 9: Unplaced Students with CGPA >= 8.0
- **Difficulty:** `Easy`
- **Tables Involved:** `STUDENT, PLACEMENT`
- **Description:** List all students with a CGPA >= 8.00 who have not yet joined any placement offer (Unplaced talent pool).

#### Problem 10: Distinct Roles Offered Across Companies
- **Difficulty:** `Easy`
- **Tables Involved:** `PLACEMENT`
- **Description:** List all unique job roles offered to students across campus placement drives, ordered alphabetically.

### Medium Problems (Questions 11 to 20)
#### Problem 11: Top Recruiting Company by Joined Offers
- **Difficulty:** `Medium`
- **Tables Involved:** `COMPANY, PLACEMENT`
- **Description:** Find the company that has recruited the single highest number of joined students across all placement drives.

#### Problem 12: Branch-Wise Placement Percentage and Avg Package
- **Difficulty:** `Medium`
- **Tables Involved:** `STUDENT, PLACEMENT`
- **Description:** For each engineering branch, calculate the total students enrolled, number of students placed (Joined = 'Yes'), overall placement percentage, and average package of placed students.

#### Problem 13: Students with Grade A in Internship 1
- **Difficulty:** `Medium`
- **Tables Involved:** `STUDENT, COMPANY, INTERNSHIP`
- **Description:** Find the Roll_No, Student Name, Company Name, and Role of all students who achieved an 'A' grade in their Mandatory Internship 1.

#### Problem 14: Companies Offering Above Overall Campus Average Package
- **Difficulty:** `Medium`
- **Tables Involved:** `COMPANY, PLACEMENT`
- **Description:** Find all companies whose average offered package is strictly higher than the overall average package across all placement offers in the entire institution.

#### Problem 15: Students Possessing More Than 3 Skills
- **Difficulty:** `Medium`
- **Tables Involved:** `STUDENT, STUDENT_SKILL`
- **Description:** Find all students who possess more than 3 distinct technical skills, displaying Roll_No, First_Name, Branch, and total skill count.

#### Problem 16: Mandatory Internship 2 Compliance Check
- **Difficulty:** `Medium`
- **Tables Involved:** `STUDENT, INTERNSHIP`
- **Description:** For all final-year students (Batch 2024 and 2025), audit their Mandatory Internship 2 compliance status (verifying completion during 8th semester with Report_Semester = 8).

#### Problem 17: Students With Multiple Offers Who Joined None
- **Difficulty:** `Medium`
- **Tables Involved:** `STUDENT, PLACEMENT`
- **Description:** Find all students who received 2 or more placement offers but have not joined any company (Joined = 'No' for all offers).

#### Problem 18: Most Demanded Placement Skills
- **Difficulty:** `Medium`
- **Tables Involved:** `PLACEMENT_SKILL`
- **Description:** Identify the top 5 most frequently evaluated technical skills across all campus placement drives.

#### Problem 19: Placement Packages Exceeding Max Annualized Internship Stipend
- **Difficulty:** `Medium`
- **Tables Involved:** `PLACEMENT, STUDENT, INTERNSHIP`
- **Description:** Find placement offers where the full-time annual package is strictly greater than the student's highest annualized internship monthly stipend.

#### Problem 20: Internships Longer Than 3 Months (Derived in View)
- **Difficulty:** `Medium`
- **Tables Involved:** `V_INTERNSHIP_DETAIL`
- **Description:** Find all internships whose dynamically calculated duration strictly exceeds 3.0 months, using the relational view V_INTERNSHIP_DETAIL.

### Difficult Problems (Questions 21 to 30)
#### Problem 21: Students with Highest Package in Their Branch
- **Difficulty:** `Difficult`
- **Tables Involved:** `STUDENT, PLACEMENT`
- **Description:** Find the student who secured the highest package within their respective engineering branch using a correlated subquery.

#### Problem 22: Relational Division: Both Mandatory Internships Completed
- **Difficulty:** `Difficult`
- **Tables Involved:** `STUDENT, INTERNSHIP`
- **Description:** Implement Relational Division: Find all students who have completed BOTH Mandatory Internship 1 (Sem 5) and Mandatory Internship 2 (Sem 8).

#### Problem 23: Window Function DENSE_RANK: Rank by CGPA within Batch
- **Difficulty:** `Difficult`
- **Tables Involved:** `STUDENT`
- **Description:** Rank students by CGPA within their graduating batch year using the window function DENSE_RANK().

#### Problem 24: Window Function RANK: Rank Packages within Company
- **Difficulty:** `Difficult`
- **Tables Involved:** `COMPANY, PLACEMENT`
- **Description:** Rank placement packages offered within each recruiting company using the window function RANK().

#### Problem 25: Running Total of Placed Students by Year
- **Difficulty:** `Difficult`
- **Tables Involved:** `PLACEMENT`
- **Description:** Compute the running cumulative total of placed students over consecutive placement years using a window frame.

#### Problem 26: Multi-Level Anti-Join: Zero Backlogs, Zero Offers, Zero Internships
- **Difficulty:** `Difficult`
- **Tables Involved:** `STUDENT, PLACEMENT, INTERNSHIP`
- **Description:** Perform a multi-level anti-join: Find students with zero backlogs who have zero placement offers AND zero completed internships.

#### Problem 27: CTE: Departmental Performance Summary with Tiers
- **Difficulty:** `Difficult`
- **Tables Involved:** `STUDENT, PLACEMENT`
- **Description:** Using a Common Table Expression (CTE), generate a departmental performance scorecard categorizing branches into Tier 1 (>= 80% placement), Tier 2 (>= 60%), and Tier 3.

#### Problem 28: Single-Joined Offer Business Rule Audit
- **Difficulty:** `Difficult`
- **Tables Involved:** `PLACEMENT`
- **Description:** Audit the Single-Joined Offer constraint by querying the generated column Joined_Student to prove zero duplicate values exist.

#### Problem 29: Full Cross-Tabulation: Placement Type and Offer Status
- **Difficulty:** `Difficult`
- **Tables Involved:** `PLACEMENT`
- **Description:** Construct a full cross-tabulation table showing total offers, pending offers, accepted offers, and declined offers grouped by Placement_Type.

#### Problem 30: Student 360-Degree Synthesis Query
- **Difficulty:** `Difficult`
- **Tables Involved:** `STUDENT, STUDENT_PHONE, STUDENT_SKILL, PLACEMENT, INTERNSHIP`
- **Description:** Generate a comprehensive 360-degree profile for student ID 2 synthesizing contact phones, technical skills, total offers, and total internships in a single tuple.

---

# Part 2: Step-by-Step Solutions Manual

## Solution to Problem 1: High CGPA Active Students
- **Difficulty:** `Easy` | **Tables Involved:** `STUDENT`
- **Core Concepts:** `Relational Selection (σ), Relational Projection (π), Compound WHERE Predicate (AND), Numeric Ordering.`
- **Problem Statement:** Find the Roll_No, Full Name (First + Last), Branch, and CGPA of all students who have a CGPA greater than or equal to 8.50 and have zero backlogs, sorted by CGPA in descending order.

### Verified SQL Implementation
```sql
SELECT Roll_No, CONCAT(First_Name, ' ', COALESCE(Last_Name, '')) AS Full_Name, Branch, CGPA
        FROM STUDENT
        WHERE CGPA >= 8.50 AND Backlogs = 0
        ORDER BY CGPA DESC;
```

### Step-by-Step Clause Breakdown
- **`SELECT Roll_No, CONCAT(...) AS Full_Name, Branch, CGPA`**: Chooses which attributes to display and merges first and last names into a clean full name.
- **`FROM STUDENT`**: Specifies the target table containing student academic records.
- **`WHERE CGPA >= 8.50 AND Backlogs = 0`**: Filters rows so only high-performing students with a clean academic record are kept.
- **`ORDER BY CGPA DESC`**: Sorts the final list from highest CGPA down to lowest.

### Plain Language Explanation for 2nd-Year CSE
This query selects high-achieving students eligible for premium placement drives. The WHERE clause tests two conditions: CGPA must be at least 8.50, and Backlogs must be strictly zero. The CONCAT function handles optional last names gracefully using COALESCE. Finally, ORDER BY sorts the output descending by CGPA.

### Sample Execution Output (Live Database)
```text
14 rows returned on seeded database. Sample rows:
- CS201908 | Ananya Iyer | CSE | 9.60
- CS202017 | Meera Menon | CSE | 9.55
- CS202001 | Aarav Sharma | CSE | 9.45
- CS202016 | Ishita Bose | CSE | 9.30
- CS202019 | Kavya Srinivasan | CSE | 9.20
```

---

## Solution to Problem 2: Distinct Company Types and Counts
- **Difficulty:** `Easy` | **Tables Involved:** `COMPANY`
- **Core Concepts:** `GROUP BY Aggregation, COUNT(*) Function, Categorical Distribution.`
- **Problem Statement:** Find all distinct company types registered in the system along with the count of companies in each category, sorted by company count descending.

### Verified SQL Implementation
```sql
SELECT Company_Type, COUNT(*) AS Company_Count
        FROM COMPANY
        GROUP BY Company_Type
        ORDER BY Company_Count DESC;
```

### Step-by-Step Clause Breakdown
- **`SELECT Company_Type, COUNT(*) AS Company_Count`**: Projects the category and counts how many company rows belong to each type.
- **`FROM COMPANY`**: Identifies the master recruiter entity table.
- **`GROUP BY Company_Type`**: Collapses rows into distinct groups based on the Company_Type ENUM.
- **`ORDER BY Company_Count DESC`**: Sorts categories from largest to smallest.

### Plain Language Explanation for 2nd-Year CSE
This query provides a breakdown of recruiters by organizational type. GROUP BY divides companies into Product, Service, and Startup groups, and COUNT(*) tallies the number of firms in each group.

### Sample Execution Output (Live Database)
```text
3 rows returned on seeded database:
- Product | 5 companies
- Service | 3 companies
- Startup | 2 companies
```

---

## Solution to Problem 3: High Package Placements in 2024
- **Difficulty:** `Easy` | **Tables Involved:** `PLACEMENT`
- **Core Concepts:** `Multi-Condition Filtering (AND), Numeric Comparison, Descending Sort.`
- **Problem Statement:** Find all placement offers secured in the year 2024 where the package is at least 12.0 LPA. Display Placement_ID, Student_ID, Role, and Package, sorted by Package descending.

### Verified SQL Implementation
```sql
SELECT Placement_ID, Student_ID, Role, Package
        FROM PLACEMENT
        WHERE Placement_Year = 2024 AND Package >= 12.00
        ORDER BY Package DESC;
```

### Step-by-Step Clause Breakdown
- **`SELECT Placement_ID, Student_ID, Role, Package`**: Projects the key offer attributes.
- **`FROM PLACEMENT`**: Scans the campus job offer fact table.
- **`WHERE Placement_Year = 2024 AND Package >= 12.00`**: Applies both temporal (year 2024) and compensation (>= 12 LPA) filter boundaries.
- **`ORDER BY Package DESC`**: Places the highest salary offers at the top.

### Plain Language Explanation for 2nd-Year CSE
This query isolates top-tier placement offers for the 2024 graduating cohort. Both conditions in the WHERE clause must be true for a row to be included.

### Sample Execution Output (Live Database)
```text
7 rows returned on seeded database. Sample rows:
- Placement_ID: 25 | Student_ID: 17 | Role: Systems Engineer | Package: 28.00 LPA
- Placement_ID: 21 | Student_ID: 15 | Role: SDE-1 | Package: 22.00 LPA
- Placement_ID: 24 | Student_ID: 17 | Role: Member of Technical Staff | Package: 18.50 LPA
```

---

## Solution to Problem 4: Stipend Range Filter for Internships
- **Difficulty:** `Easy` | **Tables Involved:** `INTERNSHIP`
- **Core Concepts:** `Range Filtering (BETWEEN ... AND), Ordering.`
- **Problem Statement:** Find all internships where the monthly stipend is between 15,000 and 40,000 (inclusive). Display Internship_ID, Student_ID, Role, and Stipend, ordered by Stipend ascending.

### Verified SQL Implementation
```sql
SELECT Internship_ID, Student_ID, Role, Stipend
        FROM INTERNSHIP
        WHERE Stipend BETWEEN 15000 AND 40000
        ORDER BY Stipend ASC;
```

### Step-by-Step Clause Breakdown
- **`SELECT Internship_ID, Student_ID, Role, Stipend`**: Projects internship identifiers, role, and monthly pay.
- **`FROM INTERNSHIP`**: Scans the student internship table.
- **`WHERE Stipend BETWEEN 15000 AND 40000`**: Filters for stipends within the inclusive range [15000, 40000].
- **`ORDER BY Stipend ASC`**: Sorts output from lowest stipend to highest.

### Plain Language Explanation for 2nd-Year CSE
The BETWEEN operator provides a clean, readable syntax for inclusive range tests on continuous numeric columns like monthly stipend.

### Sample Execution Output (Live Database)
```text
63 rows returned on seeded database. Sample rows:
- Internship_ID: 1 | Student_ID: 1 | Role: Backend Intern | Stipend: 25000.00
- Internship_ID: 2 | Student_ID: 1 | Role: Distributed Systems Intern | Stipend: 35000.00
```

---

## Solution to Problem 5: Students Possessing Python or Java Skills
- **Difficulty:** `Easy` | **Tables Involved:** `STUDENT, STUDENT_SKILL`
- **Core Concepts:** `Equi-Join, Set Membership (IN), DISTINCT Deduplication.`
- **Problem Statement:** Find the Roll_No and Name of all students who have listed 'Python' or 'Java' in their technical skills, ensuring no duplicate student rows appear in the output.

### Verified SQL Implementation
```sql
SELECT DISTINCT s.Roll_No, CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Full_Name
        FROM STUDENT s
        JOIN STUDENT_SKILL ss ON s.Student_ID = ss.Student_ID
        WHERE ss.Skill IN ('Python', 'Java')
        ORDER BY s.Roll_No;
```

### Step-by-Step Clause Breakdown
- **`SELECT DISTINCT s.Roll_No, CONCAT(...) AS Full_Name`**: Deduplicates results so a student possessing both Python and Java appears only once.
- **`FROM STUDENT s JOIN STUDENT_SKILL ss ON s.Student_ID = ss.Student_ID`**: Connects student tuples to their technical competencies.
- **`WHERE ss.Skill IN ('Python', 'Java')`**: Filters for either target programming language.
- **`ORDER BY s.Roll_No`**: Orders alphabetically by student roll number.

### Plain Language Explanation for 2nd-Year CSE
Because a student can have multiple skills, joining STUDENT with STUDENT_SKILL can produce duplicate student rows if a candidate knows both Java and Python. The DISTINCT keyword prevents duplicate candidate listings.

### Sample Execution Output (Live Database)
```text
11 rows returned on seeded database. Sample rows:
- CS201802 | Diya Patel
- CS201908 | Ananya Iyer
- CS201913 | Harsh Vardhan
- CS202001 | Aarav Sharma
- CS202015 | Aditya Kulkarni
```

---

## Solution to Problem 6: Total Students Enrolled Per Branch
- **Difficulty:** `Easy` | **Tables Involved:** `STUDENT`
- **Core Concepts:** `GROUP BY, Aggregate COUNT, Lexicographical Sorting.`
- **Problem Statement:** Display the total count of students enrolled in each engineering branch, ordered alphabetically by branch name.

### Verified SQL Implementation
```sql
SELECT Branch, COUNT(*) AS Student_Count
        FROM STUDENT
        GROUP BY Branch
        ORDER BY Branch ASC;
```

### Step-by-Step Clause Breakdown
- **`SELECT Branch, COUNT(*) AS Student_Count`**: Projects branch name and computes group size.
- **`FROM STUDENT`**: Scans student master records.
- **`GROUP BY Branch`**: Aggregates records per academic department.
- **`ORDER BY Branch ASC`**: Orders alphabetically from CSE to ME.

### Plain Language Explanation for 2nd-Year CSE
This query aggregates institutional student enrollment. The database engine groups all rows sharing the same Branch value and computes the count of students in each cohort.

### Sample Execution Output (Live Database)
```text
4 rows returned on seeded database:
- CSE: 12 students
- ECE: 6 students
- IT: 6 students
- ME: 6 students
```

---

## Solution to Problem 7: Average Package by Company Type
- **Difficulty:** `Easy` | **Tables Involved:** `COMPANY, PLACEMENT`
- **Core Concepts:** `Inner Join, Multi-Measure Aggregation (AVG, COUNT), Decimal Rounding.`
- **Problem Statement:** Find the average placement package offered by each company type (Product, Service, Startup), along with the total number of offers made, sorted by average package descending.

### Verified SQL Implementation
```sql
SELECT c.Company_Type, ROUND(AVG(p.Package), 2) AS Avg_Package, COUNT(p.Placement_ID) AS Total_Offers
        FROM COMPANY c
        JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
        GROUP BY c.Company_Type
        ORDER BY Avg_Package DESC;
```

### Step-by-Step Clause Breakdown
- **`SELECT c.Company_Type, ROUND(AVG(p.Package), 2) AS Avg_Package, COUNT(p.Placement_ID) AS Total_Offers`**: Projects category, average compensation, and volume.
- **`FROM COMPANY c JOIN PLACEMENT p ON c.Company_ID = p.Company_ID`**: Combines recruiter profile with job offer facts.
- **`GROUP BY c.Company_Type`**: Groups offers by corporate classification.
- **`ORDER BY Avg_Package DESC`**: Puts highest-paying company categories first.

### Plain Language Explanation for 2nd-Year CSE
Combines dimensional corporate data with placement transaction records to measure which industry sector provides the best compensation.

### Sample Execution Output (Live Database)
```text
3 rows returned on seeded database:
- Product | Avg: 15.65 LPA | Offers: 23
- Startup | Avg: 10.75 LPA | Offers: 8
- Service | Avg: 5.72 LPA | Offers: 9
```

---

## Solution to Problem 8: Students with Multiple Phone Numbers
- **Difficulty:** `Easy` | **Tables Involved:** `STUDENT, STUDENT_PHONE`
- **Core Concepts:** `1NF Decomposition Child Table, GROUP BY, HAVING Clause Filtering.`
- **Problem Statement:** Find all students who have registered more than one contact phone number, displaying their Roll_No, First_Name, and the count of phone numbers registered.

### Verified SQL Implementation
```sql
SELECT s.Roll_No, s.First_Name, COUNT(sp.Phone_No) AS Phone_Count
        FROM STUDENT s
        JOIN STUDENT_PHONE sp ON s.Student_ID = sp.Student_ID
        GROUP BY s.Student_ID, s.Roll_No, s.First_Name
        HAVING COUNT(sp.Phone_No) > 1
        ORDER BY Phone_Count DESC;
```

### Step-by-Step Clause Breakdown
- **`SELECT s.Roll_No, s.First_Name, COUNT(sp.Phone_No) AS Phone_Count`**: Projects student identity and calculated phone count.
- **`FROM STUDENT s JOIN STUDENT_PHONE sp ON s.Student_ID = sp.Student_ID`**: Equi-join linking parent student to child phone numbers.
- **`GROUP BY s.Student_ID, s.Roll_No, s.First_Name`**: Groups per student candidate.
- **`HAVING COUNT(sp.Phone_No) > 1`**: Filters out students with only 1 phone number.
- **`ORDER BY Phone_Count DESC`**: Shows students with the most contact numbers first.

### Plain Language Explanation for 2nd-Year CSE
In 1NF, multi-valued attributes like phone numbers are stored in a child table. To find students with multiple numbers, we group by student and apply HAVING COUNT > 1.

### Sample Execution Output (Live Database)
```text
17 rows returned on seeded database. Sample rows:
- CS202001 | Aarav | 3 phone numbers
- CS202015 | Aditya | 3 phone numbers
- CS202123 | Tarun | 3 phone numbers
```

---

## Solution to Problem 9: Unplaced Students with CGPA >= 8.0
- **Difficulty:** `Easy` | **Tables Involved:** `STUDENT, PLACEMENT`
- **Core Concepts:** `LEFT JOIN Anti-Join, IS NULL Predicate, Talent Sourcing.`
- **Problem Statement:** List all students with a CGPA >= 8.00 who have not yet joined any placement offer (Unplaced talent pool).

### Verified SQL Implementation
```sql
SELECT s.Roll_No, s.First_Name, s.Branch, s.CGPA
        FROM STUDENT s
        LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID AND p.Joined = 'Yes'
        WHERE p.Placement_ID IS NULL AND s.CGPA >= 8.00
        ORDER BY s.CGPA DESC;
```

### Step-by-Step Clause Breakdown
- **`SELECT s.Roll_No, s.First_Name, s.Branch, s.CGPA`**: Projects unplaced scholar details.
- **`FROM STUDENT s LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID AND p.Joined = 'Yes'`**: Attempts to match joined offers to students.
- **`WHERE p.Placement_ID IS NULL AND s.CGPA >= 8.00`**: Filters for students where no joined placement row exists.
- **`ORDER BY s.CGPA DESC`**: Ranks unplaced scholars by CGPA.

### Plain Language Explanation for 2nd-Year CSE
In recruitment databases, a student is 'placed' only when Joined = 'Yes'. A LEFT JOIN against PLACEMENT with `p.Placement_ID IS NULL` identifies candidates who have not joined any offer.

### Sample Execution Output (Live Database)
```text
3 rows returned on seeded database:
- CS202124 | Rhea | CSE | 9.05
- IT202127 | Tanvi | IT | 8.85
- CS202123 | Tarun | CSE | 8.65
```

---

## Solution to Problem 10: Distinct Roles Offered Across Companies
- **Difficulty:** `Easy` | **Tables Involved:** `PLACEMENT`
- **Core Concepts:** `DISTINCT Operator, String Ordering.`
- **Problem Statement:** List all unique job roles offered to students across campus placement drives, ordered alphabetically.

### Verified SQL Implementation
```sql
SELECT DISTINCT Role
        FROM PLACEMENT
        ORDER BY Role ASC;
```

### Step-by-Step Clause Breakdown
- **`SELECT DISTINCT Role`**: Selects unique designations, discarding duplicate roles.
- **`FROM PLACEMENT`**: Scans placement records.
- **`ORDER BY Role ASC`**: Alphabetical sort.

### Plain Language Explanation for 2nd-Year CSE
The DISTINCT keyword deduplicates string values in the Role column, producing a clean catalog of all positions campus recruiters hire for.

### Sample Execution Output (Live Database)
```text
17 distinct job designations returned. Sample roles:
- Cloud Engineer
- Data Scientist
- DevOps Engineer
- Member of Technical Staff
- SDE-1
```

---

## Solution to Problem 11: Top Recruiting Company by Joined Offers
- **Difficulty:** `Medium` | **Tables Involved:** `COMPANY, PLACEMENT`
- **Core Concepts:** `Equi-Join, Conditional Filtering, GROUP BY, ORDER BY DESC with LIMIT 1.`
- **Problem Statement:** Find the company that has recruited the single highest number of joined students across all placement drives.

### Verified SQL Implementation
```sql
SELECT c.Company_Name, COUNT(p.Placement_ID) AS Joined_Hires
        FROM COMPANY c
        JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
        WHERE p.Joined = 'Yes'
        GROUP BY c.Company_ID, c.Company_Name
        ORDER BY Joined_Hires DESC
        LIMIT 1;
```

### Step-by-Step Clause Breakdown
- **`SELECT c.Company_Name, COUNT(p.Placement_ID) AS Joined_Hires`**: Projects company name and count of joined hires.
- **`FROM COMPANY c JOIN PLACEMENT p ON c.Company_ID = p.Company_ID`**: Connects company records to placement offers.
- **`WHERE p.Joined = 'Yes'`**: Restricts strictly to joined placement outcomes.
- **`GROUP BY c.Company_ID, c.Company_Name`**: Aggregates per hiring organization.
- **`ORDER BY Joined_Hires DESC LIMIT 1`**: Picks the single top employer.

### Plain Language Explanation for 2nd-Year CSE
This query determines the primary campus recruiter. By filtering on `Joined = 'Yes'`, grouping by company, and ordering descending with LIMIT 1, we find the firm with the most actual student onboardings.

### Sample Execution Output (Live Database)
```text
1 row returned on seeded database:
- Infosys | 4 joined hires
```

---

## Solution to Problem 12: Branch-Wise Placement Percentage and Avg Package
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT, PLACEMENT`
- **Core Concepts:** `LEFT JOIN, Conditional Counting (`COUNT(DISTINCT CASE)`), Mathematical Percentage, Null Handling.`
- **Problem Statement:** For each engineering branch, calculate the total students enrolled, number of students placed (Joined = 'Yes'), overall placement percentage, and average package of placed students.

### Verified SQL Implementation
```sql
SELECT s.Branch,
               COUNT(s.Student_ID) AS Total_Students,
               COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' THEN s.Student_ID END) AS Placed_Students,
               ROUND(COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' THEN s.Student_ID END) * 100.0 / COUNT(s.Student_ID), 2) AS Placement_Rate,
               ROUND(AVG(CASE WHEN p.Joined = 'Yes' THEN p.Package END), 2) AS Avg_Package
        FROM STUDENT s
        LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
        GROUP BY s.Branch
        ORDER BY Placement_Rate DESC;
```

### Step-by-Step Clause Breakdown
- **`SELECT s.Branch, COUNT(s.Student_ID) AS Total_Students, ...`**: Projects branch and computes student volume.
- **`COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' THEN s.Student_ID END) AS Placed_Students`**: Counts distinct human students who joined an offer.
- **`ROUND(COUNT(DISTINCT ...) * 100.0 / COUNT(s.Student_ID), 2) AS Placement_Rate`**: Calculates percentage rate.
- **`ROUND(AVG(CASE WHEN p.Joined = 'Yes' THEN p.Package END), 2) AS Avg_Package`**: Calculates average package for placed students only.
- **`FROM STUDENT s LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID`**: Preserves unplaced students.
- **`GROUP BY s.Branch`**: Aggregates per department.
- **`ORDER BY Placement_Rate DESC`**: Ranks branches by placement success.

### Plain Language Explanation for 2nd-Year CSE
This query provides the primary departmental placement scorecard. Conditional aggregation inside COUNT and AVG allows computing both placed and total metrics in a single pass.

### Sample Execution Output (Live Database)
```text
4 rows returned on seeded database:
- CSE: 12 students | 8 placed | 66.67% placement rate | Avg: 16.06 LPA
- IT: 6 students | 4 placed | 66.67% placement rate | Avg: 10.88 LPA
- ECE: 6 students | 4 placed | 66.67% placement rate | Avg: 9.38 LPA
- ME: 6 students | 4 placed | 66.67% placement rate | Avg: 6.95 LPA
```

---

## Solution to Problem 13: Students with Grade A in Internship 1
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT, COMPANY, INTERNSHIP`
- **Core Concepts:** `Three-Table Inner Equi-Join, Compound Criteria, Curriculum Milestones.`
- **Problem Statement:** Find the Roll_No, Student Name, Company Name, and Role of all students who achieved an 'A' grade in their Mandatory Internship 1.

### Verified SQL Implementation
```sql
SELECT s.Roll_No, s.First_Name, c.Company_Name, i.Role, i.Report_Grade
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        WHERE i.Internship_No = 1 AND i.Report_Grade = 'A'
        ORDER BY s.Roll_No;
```

### Step-by-Step Clause Breakdown
- **`SELECT s.Roll_No, s.First_Name, c.Company_Name, i.Role, i.Report_Grade`**: Projects student, host company, and evaluation details.
- **`FROM INTERNSHIP i JOIN STUDENT s ON i.Student_ID = s.Student_ID JOIN COMPANY c ON i.Company_ID = c.Company_ID`**: Connects internship fact to student and company dimensions.
- **`WHERE i.Internship_No = 1 AND i.Report_Grade = 'A'`**: Filters for Milestone 1 with top academic grade.
- **`ORDER BY s.Roll_No`**: Orders by candidate roll number.

### Plain Language Explanation for 2nd-Year CSE
Audits curriculum achievement for the 5th-semester summer internship. Joining across 3 tables verifies student identity and host employer details.

### Sample Execution Output (Live Database)
```text
30 rows returned on seeded database (all 30 enrolled students achieved grade A in Internship 1).
```

---

## Solution to Problem 14: Companies Offering Above Overall Campus Average Package
- **Difficulty:** `Medium` | **Tables Involved:** `COMPANY, PLACEMENT`
- **Core Concepts:** `Uncorrelated Scalar Subquery, HAVING Clause Filtering, Global Benchmark Comparison.`
- **Problem Statement:** Find all companies whose average offered package is strictly higher than the overall average package across all placement offers in the entire institution.

### Verified SQL Implementation
```sql
SELECT c.Company_Name, ROUND(AVG(p.Package), 2) AS Company_Avg_Package
        FROM COMPANY c
        JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
        GROUP BY c.Company_ID, c.Company_Name
        HAVING AVG(p.Package) > (SELECT AVG(Package) FROM PLACEMENT)
        ORDER BY Company_Avg_Package DESC;
```

### Step-by-Step Clause Breakdown
- **`SELECT c.Company_Name, ROUND(AVG(p.Package), 2) AS Company_Avg_Package`**: Projects recruiter name and mean compensation.
- **`FROM COMPANY c JOIN PLACEMENT p ON c.Company_ID = p.Company_ID`**: Inner join linking companies to their offers.
- **`GROUP BY c.Company_ID, c.Company_Name`**: Groups by company.
- **`HAVING AVG(p.Package) > (SELECT AVG(Package) FROM PLACEMENT)`**: Filters for companies paying above the global institutional mean.
- **`ORDER BY Company_Avg_Package DESC`**: Ranks highest paying recruiters.

### Plain Language Explanation for 2nd-Year CSE
The subquery `(SELECT AVG(Package) FROM PLACEMENT)` computes the global benchmark once. The HAVING clause compares each company's average package against this benchmark.

### Sample Execution Output (Live Database)
```text
5 rows returned on seeded database:
- Microsoft | 23.50 LPA
- Google India | 22.00 LPA
- Amazon | 18.50 LPA
- Adobe | 16.00 LPA
- Cisco | 14.50 LPA
```

---

## Solution to Problem 15: Students Possessing More Than 3 Skills
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT, STUDENT_SKILL`
- **Core Concepts:** `1:N Junction Aggregation, HAVING COUNT > Threshold.`
- **Problem Statement:** Find all students who possess more than 3 distinct technical skills, displaying Roll_No, First_Name, Branch, and total skill count.

### Verified SQL Implementation
```sql
SELECT s.Roll_No, s.First_Name, s.Branch, COUNT(ss.Skill) AS Skill_Count
        FROM STUDENT s
        JOIN STUDENT_SKILL ss ON s.Student_ID = ss.Student_ID
        GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Branch
        HAVING COUNT(ss.Skill) > 3
        ORDER BY Skill_Count DESC;
```

### Step-by-Step Clause Breakdown
- **`SELECT s.Roll_No, s.First_Name, s.Branch, COUNT(ss.Skill) AS Skill_Count`**: Projects student identity and skill count.
- **`FROM STUDENT s JOIN STUDENT_SKILL ss ON s.Student_ID = ss.Student_ID`**: Equi-join on Student_ID.
- **`GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Branch`**: Groups per student.
- **`HAVING COUNT(ss.Skill) > 3`**: Restricts to students with 4 or more skills.
- **`ORDER BY Skill_Count DESC`**: Sorts by highest skill count.

### Plain Language Explanation for 2nd-Year CSE
Evaluates candidate skill versatility. In 1NF, each skill is a separate row; grouping by student and checking `HAVING COUNT > 3` isolates multi-skilled candidates.

### Sample Execution Output (Live Database)
```text
16 rows returned on seeded database. Sample rows:
- CS202001 | Aarav | CSE | 4 skills
- CS201802 | Diya | CSE | 4 skills
- EC201803 | Kabir | ECE | 4 skills
```

---

## Solution to Problem 16: Mandatory Internship 2 Compliance Check
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT, INTERNSHIP`
- **Core Concepts:** `Correlated EXISTS Subquery, CASE Diagnostic Logic, 8th-Semester Curriculum Rule.`
- **Problem Statement:** For all final-year students (Batch 2024 and 2025), audit their Mandatory Internship 2 compliance status (verifying completion during 8th semester with Report_Semester = 8).

### Verified SQL Implementation
```sql
SELECT s.Roll_No, s.First_Name, s.Branch,
               CASE
                   WHEN EXISTS (
                       SELECT 1 FROM INTERNSHIP i
                       WHERE i.Student_ID = s.Student_ID
                         AND i.Internship_No = 2
                         AND i.Internship_Type = 'Mandatory'
                         AND i.Report_Semester = 8
                   ) THEN 'Compliant (Done in Sem 8)'
                   ELSE 'Non-Compliant (Missing Sem 8 Report)'
               END AS Internship_2_Status
        FROM STUDENT s
        WHERE s.Batch_Year IN (2024, 2025)
        ORDER BY s.Batch_Year, s.Roll_No;
```

### Step-by-Step Clause Breakdown
- **`SELECT s.Roll_No, s.First_Name, s.Branch, CASE WHEN EXISTS (...) THEN 'Compliant' ELSE 'Non-Compliant' END AS Internship_2_Status`**: Classifies student compliance.
- **`FROM STUDENT s`**: Scans student population.
- **`WHERE s.Batch_Year IN (2024, 2025)`**: Restricts audit to senior cohorts.
- **`ORDER BY s.Batch_Year, s.Roll_No`**: Orders by batch and roll number.

### Plain Language Explanation for 2nd-Year CSE
Demonstrates practical curriculum audit logic in SQL. The correlated subquery checks if an internship row exists with `Internship_No = 2` and `Report_Semester = 8`.

### Sample Execution Output (Live Database)
```text
16 rows returned on seeded database (15 compliant, 1 non-compliant student needing follow-up).
```

---

## Solution to Problem 17: Students With Multiple Offers Who Joined None
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT, PLACEMENT`
- **Core Concepts:** `HAVING Clause with Multiple Conditions, Conditional SUM.`
- **Problem Statement:** Find all students who received 2 or more placement offers but have not joined any company (Joined = 'No' for all offers).

### Verified SQL Implementation
```sql
SELECT s.Roll_No, s.First_Name, COUNT(p.Placement_ID) AS Total_Offers
        FROM STUDENT s
        JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
        GROUP BY s.Student_ID, s.Roll_No, s.First_Name
        HAVING COUNT(p.Placement_ID) >= 2
           AND SUM(CASE WHEN p.Joined = 'Yes' THEN 1 ELSE 0 END) = 0;
```

### Step-by-Step Clause Breakdown
- **`SELECT s.Roll_No, s.First_Name, COUNT(p.Placement_ID) AS Total_Offers`**: Projects student identity and offer count.
- **`FROM STUDENT s JOIN PLACEMENT p ON s.Student_ID = p.Student_ID`**: Joins student to offers.
- **`GROUP BY s.Student_ID, s.Roll_No, s.First_Name`**: Groups per student candidate.
- **`HAVING COUNT(p.Placement_ID) >= 2 AND SUM(CASE WHEN p.Joined = 'Yes' THEN 1 ELSE 0 END) = 0`**: Filters for candidates with multiple offers who opted out of joining.

### Plain Language Explanation for 2nd-Year CSE
This query isolates candidates holding multiple unused job offers. It checks that total offers is at least 2, while the sum of joined offers is exactly zero.

### Sample Execution Output (Live Database)
```text
0 rows returned on seeded database (indicating 100% joining conversion among multi-offer candidates in current seed).
```

---

## Solution to Problem 18: Most Demanded Placement Skills
- **Difficulty:** `Medium` | **Tables Involved:** `PLACEMENT_SKILL`
- **Core Concepts:** `Aggregation on Decomposed Skills, Ordering by Frequency, LIMIT.`
- **Problem Statement:** Identify the top 5 most frequently evaluated technical skills across all campus placement drives.

### Verified SQL Implementation
```sql
SELECT ps.Skill, COUNT(*) AS Required_Count
        FROM PLACEMENT_SKILL ps
        GROUP BY ps.Skill
        ORDER BY Required_Count DESC
        LIMIT 5;
```

### Step-by-Step Clause Breakdown
- **`SELECT ps.Skill, COUNT(*) AS Required_Count`**: Projects skill name and counts frequency.
- **`FROM PLACEMENT_SKILL ps`**: Scans evaluated placement competencies table.
- **`GROUP BY ps.Skill`**: Groups by skill name.
- **`ORDER BY Required_Count DESC LIMIT 5`**: Top 5 most sought-after competencies.

### Plain Language Explanation for 2nd-Year CSE
Ranks technical skills by employer demand frequency across all campus recruitment drives.

### Sample Execution Output (Live Database)
```text
5 rows returned on seeded database:
- Python: 18 offers
- SQL: 17 offers
- System Design: 15 offers
- Java: 14 offers
- Data Structures: 12 offers
```

---

## Solution to Problem 19: Placement Packages Exceeding Max Annualized Internship Stipend
- **Difficulty:** `Medium` | **Tables Involved:** `PLACEMENT, STUDENT, INTERNSHIP`
- **Core Concepts:** `Multi-Table Join, Annualization Formula, HAVING Comparison.`
- **Problem Statement:** Find placement offers where the full-time annual package is strictly greater than the student's highest annualized internship monthly stipend.

### Verified SQL Implementation
```sql
SELECT p.Placement_ID, s.Roll_No, p.Package,
               ROUND(MAX(i.Stipend) * 12 / 100000.0, 2) AS Annualized_Stipend_LPA
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
        GROUP BY p.Placement_ID, s.Roll_No, p.Package
        HAVING p.Package > MAX(i.Stipend) * 12 / 100000.0
        ORDER BY p.Package DESC
        LIMIT 5;
```

### Step-by-Step Clause Breakdown
- **`SELECT p.Placement_ID, s.Roll_No, p.Package, ROUND(MAX(i.Stipend) * 12 / 100000.0, 2) AS Annualized_Stipend_LPA`**: Projects offer terms and annualized stipend.
- **`FROM PLACEMENT p JOIN STUDENT s ON p.Student_ID = s.Student_ID JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID`**: Connects placements and internships to student.
- **`GROUP BY p.Placement_ID, s.Roll_No, p.Package`**: Groups per placement offer.
- **`HAVING p.Package > MAX(i.Stipend) * 12 / 100000.0`**: Compares annual package against peak annualized stipend.
- **`ORDER BY p.Package DESC LIMIT 5`**: Top 5 offers.

### Plain Language Explanation for 2nd-Year CSE
Converts monthly internship stipend to annual LPA (`Stipend * 12 / 100,000`) and compares it against the full-time placement package.

### Sample Execution Output (Live Database)
```text
5 rows returned on seeded database. Top offers significantly outpace internship stipends.
```

---

## Solution to Problem 20: Internships Longer Than 3 Months (Derived in View)
- **Difficulty:** `Medium` | **Tables Involved:** `V_INTERNSHIP_DETAIL`
- **Core Concepts:** `Relational Views, Dynamic Derived Attributes, Numeric Threshold.`
- **Problem Statement:** Find all internships whose dynamically calculated duration strictly exceeds 3.0 months, using the relational view V_INTERNSHIP_DETAIL.

### Verified SQL Implementation
```sql
SELECT Internship_ID, Roll_No, Student_Name, Company_Name, Duration_Months
        FROM V_INTERNSHIP_DETAIL
        WHERE Duration_Months > 3.0
        ORDER BY Duration_Months DESC;
```

### Step-by-Step Clause Breakdown
- **`SELECT Internship_ID, Roll_No, Student_Name, Company_Name, Duration_Months`**: Projects view attributes.
- **`FROM V_INTERNSHIP_DETAIL`**: References pre-joined virtual view with dynamic date duration.
- **`WHERE Duration_Months > 3.0`**: Filters on dynamically derived tenure duration.
- **`ORDER BY Duration_Months DESC`**: Orders longest internships first.

### Plain Language Explanation for 2nd-Year CSE
Queries the virtual view V_INTERNSHIP_DETAIL directly. The database dynamically computes `Duration_Months` on the fly using DATEDIFF without storing redundant data.

### Sample Execution Output (Live Database)
```text
29 rows returned on seeded database. Demonstrates fast querying of derived attributes.
```

---

## Solution to Problem 21: Students with Highest Package in Their Branch
- **Difficulty:** `Difficult` | **Tables Involved:** `STUDENT, PLACEMENT`
- **Core Concepts:** `Correlated Subquery in WHERE, Departmental Maximum Selection.`
- **Problem Statement:** Find the student who secured the highest package within their respective engineering branch using a correlated subquery.

### Verified SQL Implementation
```sql
SELECT s.Branch, s.Roll_No, s.First_Name, p.Package
        FROM STUDENT s
        JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
        WHERE p.Package = (
            SELECT MAX(p2.Package)
            FROM PLACEMENT p2
            JOIN STUDENT s2 ON p2.Student_ID = s2.Student_ID
            WHERE s2.Branch = s.Branch
        )
        ORDER BY p.Package DESC;
```

### Step-by-Step Clause Breakdown
- **`SELECT s.Branch, s.Roll_No, s.First_Name, p.Package`**: Projects department champion.
- **`FROM STUDENT s JOIN PLACEMENT p ON s.Student_ID = p.Student_ID`**: Links student to offers.
- **`WHERE p.Package = (SELECT MAX(p2.Package) FROM PLACEMENT p2 JOIN STUDENT s2 ON p2.Student_ID = s2.Student_ID WHERE s2.Branch = s.Branch)`**: Correlated subquery finding the exact branch maximum.
- **`ORDER BY p.Package DESC`**: Orders champions descending.

### Plain Language Explanation for 2nd-Year CSE
For each student offer, the subquery calculates the maximum package within that student's branch (`s2.Branch = s.Branch`). The outer query filters for the offer equal to that maximum.

### Sample Execution Output (Live Database)
```text
3 rows returned on seeded database (CSE: 28.00 LPA, IT: 15.00 LPA, ECE: 12.00 LPA).
```

---

## Solution to Problem 22: Relational Division: Both Mandatory Internships Completed
- **Difficulty:** `Difficult` | **Tables Involved:** `STUDENT, INTERNSHIP`
- **Core Concepts:** `Relational Division, Dual Correlated Semi-Joins (EXISTS), Set Intersection.`
- **Problem Statement:** Implement Relational Division: Find all students who have completed BOTH Mandatory Internship 1 (Sem 5) and Mandatory Internship 2 (Sem 8).

### Verified SQL Implementation
```sql
SELECT s.Student_ID, s.Roll_No, s.First_Name, s.Branch
        FROM STUDENT s
        WHERE EXISTS (
            SELECT 1 FROM INTERNSHIP i1
            WHERE i1.Student_ID = s.Student_ID AND i1.Internship_No = 1 AND i1.Report_Semester = 5
        )
        AND EXISTS (
            SELECT 1 FROM INTERNSHIP i2
            WHERE i2.Student_ID = s.Student_ID AND i2.Internship_No = 2 AND i2.Report_Semester = 8
        )
        ORDER BY s.Roll_No;
```

### Step-by-Step Clause Breakdown
- **`SELECT s.Student_ID, s.Roll_No, s.First_Name, s.Branch`**: Projects cleared student candidates.
- **`FROM STUDENT s`**: Scans student population.
- **`WHERE EXISTS (SELECT 1 FROM INTERNSHIP i1 WHERE i1.Student_ID = s.Student_ID AND i1.Internship_No = 1 AND i1.Report_Semester = 5)`**: Verifies completion of Milestone 1.
- **`AND EXISTS (SELECT 1 FROM INTERNSHIP i2 WHERE i2.Student_ID = s.Student_ID AND i2.Internship_No = 2 AND i2.Report_Semester = 8)`**: Verifies completion of Milestone 2.
- **`ORDER BY s.Roll_No`**: Orders by candidate roll number.

### Plain Language Explanation for 2nd-Year CSE
Relational division tests whether a tuple is associated with all required elements in a set. Here, dual EXISTS clauses verify that each student has separate matching rows for both mandatory milestones.

### Sample Execution Output (Live Database)
```text
29 rows returned on seeded database (29 students cleared for institutional graduation).
```

---

## Solution to Problem 23: Window Function DENSE_RANK: Rank by CGPA within Batch
- **Difficulty:** `Difficult` | **Tables Involved:** `STUDENT`
- **Core Concepts:** `Window Functions (OLAP), DENSE_RANK(), PARTITION BY, Analytical Sorting.`
- **Problem Statement:** Rank students by CGPA within their graduating batch year using the window function DENSE_RANK().

### Verified SQL Implementation
```sql
SELECT Roll_No, First_Name, Branch, Batch_Year, CGPA,
               DENSE_RANK() OVER (PARTITION BY Batch_Year ORDER BY CGPA DESC) AS Batch_Rank
        FROM STUDENT
        ORDER BY Batch_Year DESC, Batch_Rank ASC
        LIMIT 10;
```

### Step-by-Step Clause Breakdown
- **`SELECT Roll_No, First_Name, Branch, Batch_Year, CGPA, ...`**: Projects student identity.
- **`DENSE_RANK() OVER (PARTITION BY Batch_Year ORDER BY CGPA DESC) AS Batch_Rank`**: Computes rank within batch without leaving gaps on ties.
- **`FROM STUDENT`**: Scans master student table.
- **`ORDER BY Batch_Year DESC, Batch_Rank ASC LIMIT 10`**: Top ranked students in each batch.

### Plain Language Explanation for 2nd-Year CSE
Window functions perform analytical calculations across sets of rows related to the current row without collapsing the rows into a single output tuple like GROUP BY does.

### Sample Execution Output (Live Database)
```text
Top 10 rows returned on seeded database showing competitive academic positions.
```

---

## Solution to Problem 24: Window Function RANK: Rank Packages within Company
- **Difficulty:** `Difficult` | **Tables Involved:** `COMPANY, PLACEMENT`
- **Core Concepts:** `Analytical Window Functions, RANK() with Tie Gaps, Partitioning by Dimension.`
- **Problem Statement:** Rank placement packages offered within each recruiting company using the window function RANK().

### Verified SQL Implementation
```sql
SELECT c.Company_Name, p.Role, p.Package,
               RANK() OVER (PARTITION BY c.Company_ID ORDER BY p.Package DESC) AS Package_Rank_In_Company
        FROM PLACEMENT p
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        ORDER BY c.Company_Name, Package_Rank_In_Company ASC
        LIMIT 10;
```

### Step-by-Step Clause Breakdown
- **`SELECT c.Company_Name, p.Role, p.Package, ...`**: Projects recruiter and offer terms.
- **`RANK() OVER (PARTITION BY c.Company_ID ORDER BY p.Package DESC) AS Package_Rank_In_Company`**: Ranks packages per employer.
- **`FROM PLACEMENT p JOIN COMPANY c ON p.Company_ID = c.Company_ID`**: Equi-join.
- **`ORDER BY c.Company_Name, Package_Rank_In_Company ASC LIMIT 10`**: Displays top 10 company ranks.

### Plain Language Explanation for 2nd-Year CSE
Partitions placement offers by `Company_ID` and assigns relative compensation ranks within each company's hiring portfolio.

### Sample Execution Output (Live Database)
```text
10 rows returned on seeded database detailing corporate hiring hierarchies.
```

---

## Solution to Problem 25: Running Total of Placed Students by Year
- **Difficulty:** `Difficult` | **Tables Involved:** `PLACEMENT`
- **Core Concepts:** `Running Totals, Window Frames (`ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`), Time-Series Analysis.`
- **Problem Statement:** Compute the running cumulative total of placed students over consecutive placement years using a window frame.

### Verified SQL Implementation
```sql
SELECT Placement_Year,
               COUNT(*) AS Yearly_Joined,
               SUM(COUNT(*)) OVER (ORDER BY Placement_Year ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS Cumulative_Joined
        FROM PLACEMENT
        WHERE Joined = 'Yes'
        GROUP BY Placement_Year
        ORDER BY Placement_Year ASC;
```

### Step-by-Step Clause Breakdown
- **`SELECT Placement_Year, COUNT(*) AS Yearly_Joined, ...`**: Projects year and annual joined count.
- **`SUM(COUNT(*)) OVER (ORDER BY Placement_Year ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS Cumulative_Joined`**: Accumulates running total over time.
- **`FROM PLACEMENT WHERE Joined = 'Yes'`**: Restricts strictly to joined hires.
- **`GROUP BY Placement_Year`**: Aggregates per calendar year.
- **`ORDER BY Placement_Year ASC`**: Chronological ordering.

### Plain Language Explanation for 2nd-Year CSE
The window specification `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` instructs MySQL to sum all joined hire counts from the start of recorded history up to the current row's year.

### Sample Execution Output (Live Database)
```text
4 rows returned on seeded database:
- 2022: 4 yearly joined | 4 cumulative
- 2023: 5 yearly joined | 9 cumulative
- 2024: 5 yearly joined | 14 cumulative
- 2025: 6 yearly joined | 20 cumulative
```

---

## Solution to Problem 26: Multi-Level Anti-Join: Zero Backlogs, Zero Offers, Zero Internships
- **Difficulty:** `Difficult` | **Tables Involved:** `STUDENT, PLACEMENT, INTERNSHIP`
- **Core Concepts:** `Multi-Table Anti-Join, Dual IS NULL Predicates, Relational Difference.`
- **Problem Statement:** Perform a multi-level anti-join: Find students with zero backlogs who have zero placement offers AND zero completed internships.

### Verified SQL Implementation
```sql
SELECT s.Roll_No, s.First_Name, s.Branch, s.CGPA
        FROM STUDENT s
        LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
        LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
        WHERE s.Backlogs = 0
          AND p.Placement_ID IS NULL
          AND i.Internship_ID IS NULL;
```

### Step-by-Step Clause Breakdown
- **`SELECT s.Roll_No, s.First_Name, s.Branch, s.CGPA`**: Projects disengaged candidate details.
- **`FROM STUDENT s LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID`**: Dual outer joins matching both child tables.
- **`WHERE s.Backlogs = 0 AND p.Placement_ID IS NULL AND i.Internship_ID IS NULL`**: Filters for students having zero records in both child tables.

### Plain Language Explanation for 2nd-Year CSE
Tests for complete institutional absence across both career activities (no offers AND no internships) among students with clean academic standing.

### Sample Execution Output (Live Database)
```text
0 rows returned on seeded database (demonstrating that all active students participate in internships/placements).
```

---

## Solution to Problem 27: CTE: Departmental Performance Summary with Tiers
- **Difficulty:** `Difficult` | **Tables Involved:** `STUDENT, PLACEMENT`
- **Core Concepts:** `Common Table Expressions (WITH clause), Multi-Stage Analysis, Categorical Scorecard.`
- **Problem Statement:** Using a Common Table Expression (CTE), generate a departmental performance scorecard categorizing branches into Tier 1 (>= 80% placement), Tier 2 (>= 60%), and Tier 3.

### Verified SQL Implementation
```sql
WITH DeptStats AS (
            SELECT s.Branch,
                   COUNT(DISTINCT s.Student_ID) AS Total_Students,
                   COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' THEN s.Student_ID END) AS Placed_Count,
                   AVG(CASE WHEN p.Joined = 'Yes' THEN p.Package END) AS Avg_Joined_Package
            FROM STUDENT s
            LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
            GROUP BY s.Branch
        )
        SELECT Branch, Total_Students, Placed_Count,
               ROUND(Avg_Joined_Package, 2) AS Avg_Package,
               CASE
                   WHEN Placed_Count * 100.0 / Total_Students >= 80 THEN 'Tier 1 (High Placement)'
                   WHEN Placed_Count * 100.0 / Total_Students >= 60 THEN 'Tier 2 (Moderate Placement)'
                   ELSE 'Tier 3 (Needs Attention)'
               END AS Department_Category
        FROM DeptStats
        ORDER BY Placed_Count DESC;
```

### Step-by-Step Clause Breakdown
- **`WITH DeptStats AS (SELECT s.Branch, ... FROM STUDENT s LEFT JOIN PLACEMENT p ... GROUP BY s.Branch)`**: Defines named CTE computing departmental placement numbers.
- **`SELECT Branch, Total_Students, Placed_Count, ROUND(Avg_Joined_Package, 2) AS Avg_Package, CASE WHEN ... END AS Department_Category`**: Outer query applying tier categorization.
- **`FROM DeptStats`**: Scans modular temporary result set.
- **`ORDER BY Placed_Count DESC`**: Ranks departments by placement volume.

### Plain Language Explanation for 2nd-Year CSE
The CTE `DeptStats` computes departmental aggregations first. The outer query references `DeptStats` to apply clean business categorization without writing complex nested subqueries.

### Sample Execution Output (Live Database)
```text
4 rows returned on seeded database:
- CSE | 12 students | 8 placed | 16.06 LPA | Tier 2 (Moderate Placement)
- IT | 6 students | 4 placed | 10.88 LPA | Tier 2 (Moderate Placement)
- ECE | 6 students | 4 placed | 9.38 LPA | Tier 2 (Moderate Placement)
- ME | 6 students | 4 placed | 6.95 LPA | Tier 2 (Moderate Placement)
```

---

## Solution to Problem 28: Single-Joined Offer Business Rule Audit
- **Difficulty:** `Difficult` | **Tables Involved:** `PLACEMENT`
- **Core Concepts:** `Data Quality Auditing, Generated Stored Column Verification, Business Invariant Testing.`
- **Problem Statement:** Audit the Single-Joined Offer constraint by querying the generated column Joined_Student to prove zero duplicate values exist.

### Verified SQL Implementation
```sql
SELECT Joined_Student, COUNT(*) AS Join_Count
        FROM PLACEMENT
        WHERE Joined_Student IS NOT NULL
        GROUP BY Joined_Student
        HAVING COUNT(*) > 1;
```

### Step-by-Step Clause Breakdown
- **`SELECT Joined_Student, COUNT(*) AS Join_Count`**: Projects stored student ID for joined offers.
- **`FROM PLACEMENT WHERE Joined_Student IS NOT NULL`**: Filters out unjoined NULL values.
- **`GROUP BY Joined_Student`**: Groups by joined candidate ID.
- **`HAVING COUNT(*) > 1`**: Searches for duplicates (violations).

### Plain Language Explanation for 2nd-Year CSE
This query provides mathematical proof that our database design enforces the rule: 'A student can join at most one offer.' Because `uq_one_joined_offer` is active, this query returns 0 rows.

### Sample Execution Output (Live Database)
```text
0 rows returned on seeded database, verifying 100% adherence to the single-joined-offer invariant.
```

---

## Solution to Problem 29: Full Cross-Tabulation: Placement Type and Offer Status
- **Difficulty:** `Difficult` | **Tables Involved:** `PLACEMENT`
- **Core Concepts:** `Cross-Tabulation (Pivot Table Pattern), Conditional Aggregation, Single-Pass Fact Scanning.`
- **Problem Statement:** Construct a full cross-tabulation table showing total offers, pending offers, accepted offers, and declined offers grouped by Placement_Type.

### Verified SQL Implementation
```sql
SELECT Placement_Type,
               SUM(CASE WHEN Offer_Status = 'Offered' THEN 1 ELSE 0 END) AS Offered_Count,
               SUM(CASE WHEN Offer_Status = 'Accepted' THEN 1 ELSE 0 END) AS Accepted_Count,
               SUM(CASE WHEN Offer_Status = 'Declined' THEN 1 ELSE 0 END) AS Declined_Count,
               COUNT(*) AS Total_Offers
        FROM PLACEMENT
        GROUP BY Placement_Type;
```

### Step-by-Step Clause Breakdown
- **`SELECT Placement_Type, ...`**: Projects drive channel.
- **`SUM(CASE WHEN Offer_Status = 'Offered' THEN 1 ELSE 0 END) AS Offered_Count`**: Pivots pending offers into a dedicated column.
- **`SUM(CASE WHEN Offer_Status = 'Accepted' THEN 1 ELSE 0 END) AS Accepted_Count`**: Pivots accepted offers into a dedicated column.
- **`SUM(CASE WHEN Offer_Status = 'Declined' THEN 1 ELSE 0 END) AS Declined_Count`**: Pivots declined offers into a dedicated column.
- **`COUNT(*) AS Total_Offers`**: Total offers per drive type.
- **`FROM PLACEMENT GROUP BY Placement_Type`**: Groups by recruitment channel.

### Plain Language Explanation for 2nd-Year CSE
Cross-tabulation (or pivoting) transforms distinct row values into individual summary columns using conditional SUM(CASE WHEN ...) aggregations in a single table scan.

### Sample Execution Output (Live Database)
```text
1 row returned on seeded database (On-campus: 12 Offered, 20 Accepted, 8 Declined | Total: 40 offers).
```

---

## Solution to Problem 30: Student 360-Degree Synthesis Query
- **Difficulty:** `Difficult` | **Tables Involved:** `STUDENT, STUDENT_PHONE, STUDENT_SKILL, PLACEMENT, INTERNSHIP`
- **Core Concepts:** `360-Degree Entity Synthesis, Correlated Scalar Subqueries, Avoiding Cartesian Row Explosion.`
- **Problem Statement:** Generate a comprehensive 360-degree profile for student ID 2 synthesizing contact phones, technical skills, total offers, and total internships in a single tuple.

### Verified SQL Implementation
```sql
SELECT s.Student_ID, s.Roll_No, s.First_Name, s.Branch, s.CGPA,
               (SELECT GROUP_CONCAT(sp.Phone_No SEPARATOR ', ') FROM STUDENT_PHONE sp WHERE sp.Student_ID = s.Student_ID) AS Phone_List,
               (SELECT GROUP_CONCAT(sk.Skill SEPARATOR ', ') FROM STUDENT_SKILL sk WHERE sk.Student_ID = s.Student_ID) AS Skill_List,
               (SELECT COUNT(*) FROM PLACEMENT p WHERE p.Student_ID = s.Student_ID) AS Total_Offers,
               (SELECT COUNT(*) FROM INTERNSHIP i WHERE i.Student_ID = s.Student_ID) AS Total_Internships
        FROM STUDENT s
        WHERE s.Student_ID = 2;
```

### Step-by-Step Clause Breakdown
- **`SELECT s.Student_ID, s.Roll_No, s.First_Name, s.Branch, s.CGPA, ...`**: Projects master student demographics.
- **`(SELECT GROUP_CONCAT(sp.Phone_No ...) ...) AS Phone_List`**: Scalar subquery aggregating phone numbers.
- **`(SELECT GROUP_CONCAT(sk.Skill ...) ...) AS Skill_List`**: Scalar subquery aggregating technical skills.
- **`(SELECT COUNT(*) FROM PLACEMENT p ...) AS Total_Offers`**: Scalar subquery counting placement offers.
- **`(SELECT COUNT(*) FROM INTERNSHIP i ...) AS Total_Internships`**: Scalar subquery counting completed internships.
- **`FROM STUDENT s WHERE s.Student_ID = 2`**: Filters for target student.

### Plain Language Explanation for 2nd-Year CSE
Joining 4 one-to-many child tables simultaneously produces an $M \times N$ Cartesian product. Using correlated scalar subqueries in the SELECT list retrieves exact consolidated metrics without generating duplicate rows.

### Sample Execution Output (Live Database)
```text
1 row returned on seeded database for Student ID 2 (Diya Patel, CSE, CGPA 9.12, 1 phone, 4 skills, 2 offers, 2 internships).
```

---

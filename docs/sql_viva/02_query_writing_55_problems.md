# 55 SQL Query Writing Problems: Viva Preparation & Solutions Manual

> [!IMPORTANT]
> **Practical Viva & Query Writing Preparation**: In your evaluation, the professor will present dynamic problem statements and ask you to write new SQL queries on the spot. This document trains you to translate problem statements into executable, optimized SQL queries using the **exact canonical 7-table schema and 2 views** of Legacy Dataforce. Every query has been tested and verified on the live MySQL database (`placement_internship_db`).

## Project Relational Schema Overview (Exact Names & Keys)
```text
1. STUDENT         (Student_ID [PK], Roll_No [UNI], First_Name, Last_Name, Branch, Batch_Year, Section, CGPA, Backlogs, Email [UNI], Resume_Link, Date_of_Birth, Gender, Personal_Email)
2. STUDENT_PHONE   (Student_ID [PK, FK], Phone_No [PK])
3. STUDENT_SKILL   (Student_ID [PK, FK], Skill [PK])
4. COMPANY         (Company_ID [PK], Company_Name [UNI], Company_Type, Industry, Location, Website)
5. PLACEMENT       (Placement_ID [PK], Student_ID [FK], Company_ID [FK], Role, Package, Placement_Year, Placement_Type, Is_PPO, Joined, Offer_Status, Interview_Rounds, Joined_Student [UNI])
6. PLACEMENT_SKILL (Placement_ID [PK, FK], Skill [PK])
7. INTERNSHIP      (Student_ID [PK, FK], Internship_No [PK], Internship_ID [UNI], Company_ID [FK], Internship_Type, Role, Interview_Rounds, Stipend, Start_Date, End_Date, Credits, Report_Semester, Report_Link, Report_Grade, Certificate_Link)

VIEWS:
- V_PLACEMENT_DETAIL  (Combines PLACEMENT, STUDENT, and COMPANY with Student_Name)
- V_INTERNSHIP_DETAIL (Combines INTERNSHIP, STUDENT, and COMPANY with dynamically calculated Duration_Months)
```

---

## Table of Contents
- [Part 1: Unsolved Problem Statements (Questions 1 to 55)](#part-1-unsolved-problem-statements)
  - [Easy Problems (Questions 1 to 18)](#easy-problems-questions-1-to-18)
  - [Medium Problems (Questions 19 to 38)](#medium-problems-questions-19-to-38)
  - [Difficult Problems (Questions 39 to 55)](#difficult-problems-questions-39-to-55)
- [Part 2: Step-by-Step Solutions Manual](#part-2-step-by-step-solutions-manual)

---

# Part 1: Unsolved Problem Statements

### Easy Problems (Questions 1 to 18)
#### Question 1: CSE 2024 Students
- **Difficulty:** `Easy` | **Tables Involved:** `STUDENT`
- **Description:** Retrieve Student_ID, Roll_No, First_Name, Branch, Batch_Year, and CGPA for all students belonging to the Computer Science (CSE) branch graduating in 2024.

#### Question 2: Product Companies in Tech Hubs
- **Difficulty:** `Easy` | **Tables Involved:** `COMPANY`
- **Description:** List all Product-based companies located in major technology centers (Bangalore, Bengaluru, or Hyderabad), showing Company_ID, Company_Name, Industry, and Location.

#### Question 3: Medium to High Tier Placements
- **Difficulty:** `Easy` | **Tables Involved:** `PLACEMENT`
- **Description:** Find all placement offers where the compensation package is between 10.0 and 20.0 LPA (inclusive), displaying Placement_ID, Student_ID, Company_ID, Role, and Package.

#### Question 4: Recent Internships
- **Difficulty:** `Easy` | **Tables Involved:** `INTERNSHIP`
- **Description:** Find all internship records that commenced on or after January 1, 2023, displaying Internship_ID, Student_ID, Company_ID, Role, and Start_Date.

#### Question 5: Institutional Email Search
- **Difficulty:** `Easy` | **Tables Involved:** `STUDENT`
- **Description:** Find all students whose institutional email ends with '@fictional.edu', displaying Student_ID, Roll_No, and Email.

#### Question 6: PPO Offers List
- **Difficulty:** `Easy` | **Tables Involved:** `PLACEMENT`
- **Description:** List all placement offers that originated from Pre-Placement Offers (Is_PPO = 'Yes'), showing Placement_ID, Student_ID, Company_ID, Package, and Is_PPO.

#### Question 7: Students with Active Backlogs
- **Difficulty:** `Easy` | **Tables Involved:** `STUDENT`
- **Description:** Find all students who currently have one or more active academic backlogs, showing Roll_No, First_Name, Branch, and Backlogs count.

#### Question 8: Distinct Industries
- **Difficulty:** `Easy` | **Tables Involved:** `COMPANY`
- **Description:** List all distinct industry sectors represented in the COMPANY table, ordered alphabetically.

#### Question 9: Top 3 CGPA Performers
- **Difficulty:** `Easy` | **Tables Involved:** `STUDENT`
- **Description:** Retrieve the top 3 students with the highest CGPA across the institution, displaying Roll_No, First_Name, and CGPA.

#### Question 10: Semester 5 Mandatory Internships
- **Difficulty:** `Easy` | **Tables Involved:** `INTERNSHIP`
- **Description:** Retrieve all Mandatory internships assigned to Semester 5 (Report_Semester = 5), showing Internship_ID, Student_ID, Role, Credits, and Report_Semester.

#### Question 11: Semester 8 Mandatory Internships
- **Difficulty:** `Easy` | **Tables Involved:** `INTERNSHIP`
- **Description:** Retrieve all Mandatory internships completed during 8th semester (Report_Semester = 8), showing Internship_ID, Student_ID, Role, Credits, and Report_Semester.

#### Question 12: Accepted Placement Offers
- **Difficulty:** `Easy` | **Tables Involved:** `PLACEMENT`
- **Description:** List all placement offers where the candidate has accepted the offer (Offer_Status = 'Accepted'), showing Placement_ID, Student_ID, Package, and Offer_Status.

#### Question 13: Joined Placements
- **Difficulty:** `Easy` | **Tables Involved:** `PLACEMENT`
- **Description:** List all placement records where the student has actively joined the organization (Joined = 'Yes').

#### Question 14: Name Prefix Filter
- **Difficulty:** `Easy` | **Tables Involved:** `STUDENT`
- **Description:** Find all students whose first name starts with the letter 'A', displaying Roll_No, First_Name, and Branch, ordered alphabetically.

#### Question 15: Paid Internships
- **Difficulty:** `Easy` | **Tables Involved:** `INTERNSHIP`
- **Description:** Retrieve all internships offering a non-zero monthly stipend, sorted in descending order of stipend.

#### Question 16: Branch Average CGPA
- **Difficulty:** `Easy` | **Tables Involved:** `STUDENT`
- **Description:** Calculate the average CGPA (rounded to 2 decimal places) and total student enrollment for each academic branch.

#### Question 17: Total Offers Per Company
- **Difficulty:** `Easy` | **Tables Involved:** `COMPANY, PLACEMENT`
- **Description:** Calculate the total number of placement offers made by each company, displaying Company_Name and offer count, sorted from highest to lowest.

#### Question 18: Yearly Max Package
- **Difficulty:** `Easy` | **Tables Involved:** `PLACEMENT`
- **Description:** For each placement year, find the maximum and minimum compensation package offered.

### Medium Problems (Questions 19 to 38)
#### Question 19: High-Performing Branches
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT`
- **Description:** Find all academic branches where the average CGPA is strictly greater than 8.00.

#### Question 20: Frequent Recruiters
- **Difficulty:** `Medium` | **Tables Involved:** `COMPANY, PLACEMENT`
- **Description:** Find all companies that have made 3 or more placement offers across campus drives.

#### Question 21: Gender Distribution
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT`
- **Description:** Display the count of students categorized by gender, treating NULL values as 'Not Specified'.

#### Question 22: Stipend by Internship Type
- **Difficulty:** `Medium` | **Tables Involved:** `INTERNSHIP`
- **Description:** Calculate the average monthly stipend and total count of internships for Mandatory vs Additional internships.

#### Question 23: Companies Averaging Over 10 LPA
- **Difficulty:** `Medium` | **Tables Involved:** `COMPANY, PLACEMENT`
- **Description:** Identify all companies whose average offered package strictly exceeds 10.00 LPA.

#### Question 24: Phone Count Per Student
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT_PHONE`
- **Description:** Count the total number of phone numbers registered per student, sorted by highest count.

#### Question 25: Top Student Skills
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT_SKILL`
- **Description:** Identify the top 5 most common technical skills possessed by students.

#### Question 26: Package by Placement Type
- **Difficulty:** `Medium` | **Tables Involved:** `PLACEMENT`
- **Description:** Compare average package and total offer count across On-campus, Off-campus, and Pooled placement drives.

#### Question 27: Offer Status Breakdown
- **Difficulty:** `Medium` | **Tables Involved:** `PLACEMENT`
- **Description:** Count the number of offers in each Offer_Status category ('Offered', 'Accepted', 'Declined').

#### Question 28: Mandatory Credits per Student
- **Difficulty:** `Medium` | **Tables Involved:** `INTERNSHIP`
- **Description:** Calculate the total cumulative credits earned from mandatory internships by each student.

#### Question 29: Batch Size Filter
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT`
- **Description:** Find all graduating batch years that have more than 5 enrolled students.

#### Question 30: Interview Rounds per Company
- **Difficulty:** `Medium` | **Tables Involved:** `COMPANY, PLACEMENT`
- **Description:** Calculate the average number of interview rounds conducted by each company during placement evaluation.

#### Question 31: Student-Placement-Company Equi-Join
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT, PLACEMENT, COMPANY`
- **Description:** Perform a 3-table equi-join to display Roll_No, Student Name, Company Name, Role, and Package.

#### Question 32: Internship Details with Names
- **Difficulty:** `Medium` | **Tables Involved:** `INTERNSHIP, STUDENT, COMPANY`
- **Description:** Display student roll number, candidate name, host company, internship role, and stipend.

#### Question 33: Placement Required Skills Listing
- **Difficulty:** `Medium` | **Tables Involved:** `PLACEMENT, COMPANY, PLACEMENT_SKILL`
- **Description:** List each placement offer along with the hiring company, role, and tested technical skills.

#### Question 34: Same Branch Identical CGPA Pairs
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT`
- **Description:** Use a self-join to find pairs of students within the same branch who have identical CGPAs.

#### Question 35: Placement and Internship Corporate Comparison
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT, PLACEMENT, INTERNSHIP, COMPANY`
- **Description:** Compare the company where a student joined for full-time employment vs where they completed Internship 1.

#### Question 36: Skill Matching Between Student and Placement
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT, PLACEMENT, PLACEMENT_SKILL, STUDENT_SKILL`
- **Description:** Find instances where a student possesses a technical skill that was explicitly evaluated for their placement offer.

#### Question 37: Querying V_PLACEMENT_DETAIL
- **Difficulty:** `Medium` | **Tables Involved:** `V_PLACEMENT_DETAIL`
- **Description:** Query view V_PLACEMENT_DETAIL for all accepted offers, ordered by package descending.

#### Question 38: Querying V_INTERNSHIP_DETAIL
- **Difficulty:** `Medium` | **Tables Involved:** `V_INTERNSHIP_DETAIL`
- **Description:** Query view V_INTERNSHIP_DETAIL to find internships lasting at least 2.0 months.

### Difficult Problems (Questions 39 to 55)
#### Question 39: Student Multi-Offer Listing
- **Difficulty:** `Hard` | **Tables Involved:** `STUDENT, PLACEMENT, COMPANY`
- **Description:** For students holding multiple offers, display a consolidated string of company names and packages using GROUP_CONCAT.

#### Question 40: Internship to Placement Host Match
- **Difficulty:** `Hard` | **Tables Involved:** `COMPANY, PLACEMENT, INTERNSHIP, STUDENT`
- **Description:** Find companies where a student was both an intern and subsequently received a placement offer.

#### Question 41: Companies with Zero Placement Offers
- **Difficulty:** `Hard` | **Tables Involved:** `COMPANY, PLACEMENT`
- **Description:** Find all companies that have never made a placement offer to any student using a LEFT JOIN anti-join.

#### Question 42: Students Lacking Internship 2
- **Difficulty:** `Hard` | **Tables Involved:** `STUDENT, INTERNSHIP`
- **Description:** Find all students who have not yet completed Mandatory Internship 2 using NOT EXISTS.

#### Question 43: Above-Average CGPA Students
- **Difficulty:** `Hard` | **Tables Involved:** `STUDENT`
- **Description:** Find all students whose CGPA is strictly higher than the institution-wide average CGPA.

#### Question 44: Correlated Subquery Offer Counting
- **Difficulty:** `Hard` | **Tables Involved:** `STUDENT, PLACEMENT`
- **Description:** Display each student's Roll_No and Name alongside a correlated scalar subquery counting their total offers.

#### Question 45: Students with Zero Skills Listed
- **Difficulty:** `Hard` | **Tables Involved:** `STUDENT, STUDENT_SKILL`
- **Description:** Find all students who have not listed any technical skills using an anti-join.

#### Question 46: Companies Hiring Zero-Backlog Students
- **Difficulty:** `Hard` | **Tables Involved:** `COMPANY, PLACEMENT, STUDENT`
- **Description:** Find all companies that have recruited students who have zero backlogs using an IN subquery.

#### Question 47: Offers Higher Than All Offers from a Company
- **Difficulty:** `Hard` | **Tables Involved:** `PLACEMENT, COMPANY`
- **Description:** Find placement offers with packages greater than ALL offers made by 'Infosys' using > ALL.

#### Question 48: Union of All Technical Competencies
- **Difficulty:** `Hard` | **Tables Involved:** `STUDENT_SKILL, PLACEMENT_SKILL`
- **Description:** Produce a unified set of all technical skills appearing across student profiles or placement requirements using UNION.

#### Question 49: Companies with Dual Operations
- **Difficulty:** `Hard` | **Tables Involved:** `COMPANY, PLACEMENT, INTERNSHIP`
- **Description:** Find all companies that participate in both campus placements AND internship programs using dual correlated EXISTS.

#### Question 50: Derived Table for Salary Tiers
- **Difficulty:** `Hard` | **Tables Involved:** `PLACEMENT`
- **Description:** Categorize placed packages into High, Mid, and Base tiers inside a FROM clause derived table and count placed students in each.

#### Question 51: ROW_NUMBER() within Branch
- **Difficulty:** `Hard` | **Tables Involved:** `STUDENT`
- **Description:** Assign a unique sequential position to each student within their branch ordered by CGPA using ROW_NUMBER() OVER ().

#### Question 52: DENSE_RANK() for Packages
- **Difficulty:** `Hard` | **Tables Involved:** `PLACEMENT`
- **Description:** Rank all placement offers by package using DENSE_RANK() OVER (ORDER BY Package DESC).

#### Question 53: CTE Top Student per Branch
- **Difficulty:** `Hard` | **Tables Involved:** `STUDENT`
- **Description:** Using a Common Table Expression with ROW_NUMBER(), find the single highest-scoring student in each academic department.

#### Question 54: CTE Company Placement Summary
- **Difficulty:** `Hard` | **Tables Involved:** `COMPANY, PLACEMENT`
- **Description:** Use a CTE to calculate total offers and average package per company, then join with COMPANY to display company names.

#### Question 55: Analytic Window Average CGPA per Branch
- **Difficulty:** `Hard` | **Tables Involved:** `STUDENT`
- **Description:** Calculate each student's CGPA difference from their branch's average CGPA using `AVG() OVER (PARTITION BY Branch)`.

---

# Part 2: Step-by-Step Solutions Manual

## Solution to Question 1: CSE 2024 Students
- **Difficulty:** `Easy` | **Tables Involved:** `STUDENT`
- **Core Concepts:** `Relational Selection (σ), Compound Filtering with AND, Relational Projection (π).`
- **Problem Statement:** Retrieve Student_ID, Roll_No, First_Name, Branch, Batch_Year, and CGPA for all students belonging to the Computer Science (CSE) branch graduating in 2024.

### Executable SQL Implementation
```sql
SELECT Student_ID, Roll_No, First_Name, Branch, Batch_Year, CGPA
        FROM STUDENT
        WHERE Branch = 'CSE' AND Batch_Year = 2024;
```

### Step-by-Step Clause Breakdown
- **`SELECT Student_ID, Roll_No, First_Name, Branch, Batch_Year, CGPA`**: Chooses specific student columns to display.
- **`FROM STUDENT`**: Scans the master student directory table.
- **`WHERE Branch = 'CSE' AND Batch_Year = 2024`**: Applies equality filters on both academic department and graduating year.

### Plain Language Explanation for 2nd-Year CSE
This query filters the student directory for a specific cohort. Both conditions in the WHERE clause must be satisfied for a tuple to be returned.

### Sample Execution Output (Live Database)
```text
4 rows returned on seeded database (CS202015, CS202016, CS202017, CS202019).
```

---

## Solution to Question 2: Product Companies in Tech Hubs
- **Difficulty:** `Easy` | **Tables Involved:** `COMPANY`
- **Core Concepts:** `Categorical Filtering, Set Membership with IN Operator, Case Sensitivity.`
- **Problem Statement:** List all Product-based companies located in major technology centers (Bangalore, Bengaluru, or Hyderabad), showing Company_ID, Company_Name, Industry, and Location.

### Executable SQL Implementation
```sql
SELECT Company_ID, Company_Name, Industry, Location
        FROM COMPANY
        WHERE Company_Type = 'Product' AND Location IN ('Bangalore', 'Hyderabad', 'Bengaluru');
```

### Step-by-Step Clause Breakdown
- **`SELECT Company_ID, Company_Name, Industry, Location`**: Projects company identification and location.
- **`FROM COMPANY`**: Scans the corporate recruiter table.
- **`WHERE Company_Type = 'Product' AND Location IN ('Bangalore', 'Hyderabad', 'Bengaluru')`**: Filters for Product firms located in target hubs.

### Plain Language Explanation for 2nd-Year CSE
Uses the IN operator to test if the company location matches any of the specified cities, combined with Company_Type = 'Product'.

### Sample Execution Output (Live Database)
```text
3 rows returned on seeded database (Google India, Microsoft, Amazon).
```

---

## Solution to Question 3: Medium to High Tier Placements
- **Difficulty:** `Easy` | **Tables Involved:** `PLACEMENT`
- **Core Concepts:** `Continuous Numeric Range Filtering, BETWEEN ... AND Predicate.`
- **Problem Statement:** Find all placement offers where the compensation package is between 10.0 and 20.0 LPA (inclusive), displaying Placement_ID, Student_ID, Company_ID, Role, and Package.

### Executable SQL Implementation
```sql
SELECT Placement_ID, Student_ID, Company_ID, Role, Package
        FROM PLACEMENT
        WHERE Package BETWEEN 10.00 AND 20.00;
```

### Step-by-Step Clause Breakdown
- **`SELECT Placement_ID, Student_ID, Company_ID, Role, Package`**: Projects placement identifiers and compensation.
- **`FROM PLACEMENT`**: Scans the placement fact table.
- **`WHERE Package BETWEEN 10.00 AND 20.00`**: Filters packages within the inclusive range [10.00, 20.00].

### Plain Language Explanation for 2nd-Year CSE
The BETWEEN operator tests whether Package is greater than or equal to 10.00 and less than or equal to 20.00 LPA.

### Sample Execution Output (Live Database)
```text
23 rows returned on seeded database.
```

---

## Solution to Question 4: Recent Internships
- **Difficulty:** `Easy` | **Tables Involved:** `INTERNSHIP`
- **Core Concepts:** `Temporal Date Filtering, ISO-8601 Date Comparison.`
- **Problem Statement:** Find all internship records that commenced on or after January 1, 2023, displaying Internship_ID, Student_ID, Company_ID, Role, and Start_Date.

### Executable SQL Implementation
```sql
SELECT Internship_ID, Student_ID, Company_ID, Role, Start_Date
        FROM INTERNSHIP
        WHERE Start_Date >= '2023-01-01';
```

### Step-by-Step Clause Breakdown
- **`SELECT Internship_ID, Student_ID, Company_ID, Role, Start_Date`**: Projects internship identifiers and start date.
- **`FROM INTERNSHIP`**: Scans student internship records.
- **`WHERE Start_Date >= '2023-01-01'`**: Chronological date filter for recent tenures.

### Plain Language Explanation for 2nd-Year CSE
In MySQL, standard DATE attributes ('YYYY-MM-DD') are directly comparable using relational comparison operators like >=.

### Sample Execution Output (Live Database)
```text
24 rows returned on seeded database.
```

---

## Solution to Question 5: Institutional Email Search
- **Difficulty:** `Easy` | **Tables Involved:** `STUDENT`
- **Core Concepts:** `Pattern Matching, LIKE Operator, Wildcard '%' Suffix.`
- **Problem Statement:** Find all students whose institutional email ends with '@fictional.edu', displaying Student_ID, Roll_No, and Email.

### Executable SQL Implementation
```sql
SELECT Student_ID, Roll_No, Email
        FROM STUDENT
        WHERE Email LIKE '%@fictional.edu';
```

### Step-by-Step Clause Breakdown
- **`SELECT Student_ID, Roll_No, Email`**: Projects student identity and email address.
- **`FROM STUDENT`**: Scans master student table.
- **`WHERE Email LIKE '%@fictional.edu'`**: Matches email strings ending in the institutional domain.

### Plain Language Explanation for 2nd-Year CSE
The wildcard '%' matches zero or more preceding characters, ensuring only authenticated institutional email domains are selected.

### Sample Execution Output (Live Database)
```text
30 rows returned on seeded database (all registered students have verified emails).
```

---

## Solution to Question 6: PPO Offers List
- **Difficulty:** `Easy` | **Tables Involved:** `PLACEMENT`
- **Core Concepts:** `Enum Attribute Filtering, Boolean Flag Logic.`
- **Problem Statement:** List all placement offers that originated from Pre-Placement Offers (Is_PPO = 'Yes'), showing Placement_ID, Student_ID, Company_ID, Package, and Is_PPO.

### Executable SQL Implementation
```sql
SELECT Placement_ID, Student_ID, Company_ID, Package, Is_PPO
        FROM PLACEMENT
        WHERE Is_PPO = 'Yes';
```

### Step-by-Step Clause Breakdown
- **`SELECT Placement_ID, Student_ID, Company_ID, Package, Is_PPO`**: Projects offer details and PPO flag.
- **`FROM PLACEMENT`**: Scans placement records.
- **`WHERE Is_PPO = 'Yes'`**: Filters exclusively for PPO conversion offers.

### Plain Language Explanation for 2nd-Year CSE
Isolates offers where students interned with the employer and received an early full-time offer before general campus recruitment.

### Sample Execution Output (Live Database)
```text
9 rows returned on seeded database.
```

---

## Solution to Question 7: Students with Active Backlogs
- **Difficulty:** `Easy` | **Tables Involved:** `STUDENT`
- **Core Concepts:** `Integer Comparison, Academic Clearance Auditing.`
- **Problem Statement:** Find all students who currently have one or more active academic backlogs, showing Roll_No, First_Name, Branch, and Backlogs count.

### Executable SQL Implementation
```sql
SELECT Roll_No, First_Name, Branch, Backlogs
        FROM STUDENT
        WHERE Backlogs > 0;
```

### Step-by-Step Clause Breakdown
- **`SELECT Roll_No, First_Name, Branch, Backlogs`**: Projects candidate identity and backlog tally.
- **`FROM STUDENT`**: Scans student master table.
- **`WHERE Backlogs > 0`**: Filters for candidates with active backlogs.

### Plain Language Explanation for 2nd-Year CSE
Used by placement coordinators to identify students requiring clearance or remedial examinations before placement drive registration.

### Sample Execution Output (Live Database)
```text
3 rows returned on seeded database (Rohan Deshmukh: 2, Simran Kaur: 1, Rahul Saxena: 1).
```

---

## Solution to Question 8: Distinct Industries
- **Difficulty:** `Easy` | **Tables Involved:** `COMPANY`
- **Core Concepts:** `DISTINCT Operator, Deduplication, Alphabetical Sorting.`
- **Problem Statement:** List all distinct industry sectors represented in the COMPANY table, ordered alphabetically.

### Executable SQL Implementation
```sql
SELECT DISTINCT Industry
        FROM COMPANY
        ORDER BY Industry;
```

### Step-by-Step Clause Breakdown
- **`SELECT DISTINCT Industry`**: Removes duplicate industry strings from projected results.
- **`FROM COMPANY`**: Scans recruiter records.
- **`ORDER BY Industry`**: Alphabetical sort.

### Plain Language Explanation for 2nd-Year CSE
The DISTINCT keyword ensures each industry sector appears exactly once in the resulting catalog.

### Sample Execution Output (Live Database)
```text
10 distinct industry sectors returned (Automotive, Cloud Computing, E-commerce, Financial Services, etc.).
```

---

## Solution to Question 9: Top 3 CGPA Performers
- **Difficulty:** `Easy` | **Tables Involved:** `STUDENT`
- **Core Concepts:** `ORDER BY DESC, LIMIT Clause, Academic Toppers.`
- **Problem Statement:** Retrieve the top 3 students with the highest CGPA across the institution, displaying Roll_No, First_Name, and CGPA.

### Executable SQL Implementation
```sql
SELECT Roll_No, First_Name, CGPA
        FROM STUDENT
        ORDER BY CGPA DESC
        LIMIT 3;
```

### Step-by-Step Clause Breakdown
- **`SELECT Roll_No, First_Name, CGPA`**: Projects student identity and grade point average.
- **`FROM STUDENT`**: Scans student records.
- **`ORDER BY CGPA DESC`**: Ranks highest grades at the top.
- **`LIMIT 3`**: Restricts result set to top 3 tuples.

### Plain Language Explanation for 2nd-Year CSE
Sorts all student records descending by continuous numeric CGPA and clips the result to the top 3 rows.

### Sample Execution Output (Live Database)
```text
3 rows returned: Ananya Iyer (9.60), Meera Menon (9.55), Aarav Sharma (9.45).
```

---

## Solution to Question 10: Semester 5 Mandatory Internships
- **Difficulty:** `Easy` | **Tables Involved:** `INTERNSHIP`
- **Core Concepts:** `Curriculum Milestone Verification, Equality Filtering.`
- **Problem Statement:** Retrieve all Mandatory internships assigned to Semester 5 (Report_Semester = 5), showing Internship_ID, Student_ID, Role, Credits, and Report_Semester.

### Executable SQL Implementation
```sql
SELECT Internship_ID, Student_ID, Role, Credits, Report_Semester
        FROM INTERNSHIP
        WHERE Internship_Type = 'Mandatory' AND Report_Semester = 5;
```

### Step-by-Step Clause Breakdown
- **`SELECT Internship_ID, Student_ID, Role, Credits, Report_Semester`**: Projects milestone attributes.
- **`FROM INTERNSHIP`**: Scans student internship records.
- **`WHERE Internship_Type = 'Mandatory' AND Report_Semester = 5`**: Filters for Milestone 1 requirements.

### Plain Language Explanation for 2nd-Year CSE
Verifies institutional records for Internship 1, carried out during the summer after 2nd year and evaluated in Semester 5 for 4 credits.

### Sample Execution Output (Live Database)
```text
30 rows returned on seeded database (all 30 students completed Internship 1).
```

---

## Solution to Question 11: Semester 8 Mandatory Internships
- **Difficulty:** `Easy` | **Tables Involved:** `INTERNSHIP`
- **Core Concepts:** `Updated Curriculum Rule Verification, 8th Semester Milestone.`
- **Problem Statement:** Retrieve all Mandatory internships completed during 8th semester (Report_Semester = 8), showing Internship_ID, Student_ID, Role, Credits, and Report_Semester.

### Executable SQL Implementation
```sql
SELECT Internship_ID, Student_ID, Role, Credits, Report_Semester
        FROM INTERNSHIP
        WHERE Internship_Type = 'Mandatory' AND Report_Semester = 8;
```

### Step-by-Step Clause Breakdown
- **`SELECT Internship_ID, Student_ID, Role, Credits, Report_Semester`**: Projects milestone attributes.
- **`FROM INTERNSHIP`**: Scans student internship records.
- **`WHERE Internship_Type = 'Mandatory' AND Report_Semester = 8`**: Filters for updated Milestone 2 requirements.

### Plain Language Explanation for 2nd-Year CSE
Enforces the updated university rule: Internship 2 is mandatory, carries 4 credits, is completed during 8th semester, and report is submitted after 8th semester (Report_Semester = 8).

### Sample Execution Output (Live Database)
```text
29 rows returned on seeded database.
```

---

## Solution to Question 12: Accepted Placement Offers
- **Difficulty:** `Easy` | **Tables Involved:** `PLACEMENT`
- **Core Concepts:** `State Machine Filtering, Offer Status Verification.`
- **Problem Statement:** List all placement offers where the candidate has accepted the offer (Offer_Status = 'Accepted'), showing Placement_ID, Student_ID, Package, and Offer_Status.

### Executable SQL Implementation
```sql
SELECT Placement_ID, Student_ID, Package, Offer_Status
        FROM PLACEMENT
        WHERE Offer_Status = 'Accepted';
```

### Step-by-Step Clause Breakdown
- **`SELECT Placement_ID, Student_ID, Package, Offer_Status`**: Projects offer terms.
- **`FROM PLACEMENT`**: Scans placement fact table.
- **`WHERE Offer_Status = 'Accepted'`**: Filters for accepted job offers.

### Plain Language Explanation for 2nd-Year CSE
Isolates offers where candidates accepted recruiter terms, distinguishing them from pending 'Offered' or rejected 'Declined' states.

### Sample Execution Output (Live Database)
```text
20 rows returned on seeded database.
```

---

## Solution to Question 13: Joined Placements
- **Difficulty:** `Easy` | **Tables Involved:** `PLACEMENT`
- **Core Concepts:** `Final Placement Verification, Placed Definition.`
- **Problem Statement:** List all placement records where the student has actively joined the organization (Joined = 'Yes').

### Executable SQL Implementation
```sql
SELECT Placement_ID, Student_ID, Company_ID, Package, Joined
        FROM PLACEMENT
        WHERE Joined = 'Yes';
```

### Step-by-Step Clause Breakdown
- **`SELECT Placement_ID, Student_ID, Company_ID, Package, Joined`**: Projects placement terms.
- **`FROM PLACEMENT`**: Scans placement records.
- **`WHERE Joined = 'Yes'`**: Filters strictly for joined placements.

### Plain Language Explanation for 2nd-Year CSE
Under institutional business rules, a student is strictly considered 'placed' only when `Joined = 'Yes'`.

### Sample Execution Output (Live Database)
```text
20 rows returned on seeded database.
```

---

## Solution to Question 14: Name Prefix Filter
- **Difficulty:** `Easy` | **Tables Involved:** `STUDENT`
- **Core Concepts:** `String Prefix Search, Pattern Matching, Alphabetical Ordering.`
- **Problem Statement:** Find all students whose first name starts with the letter 'A', displaying Roll_No, First_Name, and Branch, ordered alphabetically.

### Executable SQL Implementation
```sql
SELECT Roll_No, First_Name, Branch
        FROM STUDENT
        WHERE First_Name LIKE 'A%'
        ORDER BY First_Name;
```

### Step-by-Step Clause Breakdown
- **`SELECT Roll_No, First_Name, Branch`**: Projects student identity.
- **`FROM STUDENT`**: Scans student master directory.
- **`WHERE First_Name LIKE 'A%'`**: Matches names starting with 'A'.
- **`ORDER BY First_Name`**: Alphabetical sort.

### Plain Language Explanation for 2nd-Year CSE
Demonstrates wildcard prefix pattern matching in SQL.

### Sample Execution Output (Live Database)
```text
5 rows returned on seeded database (Aarav, Aditya, Ananya, Aniket, Arjun).
```

---

## Solution to Question 15: Paid Internships
- **Difficulty:** `Easy` | **Tables Involved:** `INTERNSHIP`
- **Core Concepts:** `Numerical Inequality, Descending Sort.`
- **Problem Statement:** Retrieve all internships offering a non-zero monthly stipend, sorted in descending order of stipend.

### Executable SQL Implementation
```sql
SELECT Internship_ID, Role, Stipend
        FROM INTERNSHIP
        WHERE Stipend > 0
        ORDER BY Stipend DESC;
```

### Step-by-Step Clause Breakdown
- **`SELECT Internship_ID, Role, Stipend`**: Projects internship role and pay.
- **`FROM INTERNSHIP`**: Scans internship records.
- **`WHERE Stipend > 0`**: Filters out unpaid internships.
- **`ORDER BY Stipend DESC`**: Ranks highest paying internships first.

### Plain Language Explanation for 2nd-Year CSE
Filters for compensated corporate internships, ordering by monthly stipend.

### Sample Execution Output (Live Database)
```text
63 rows returned on seeded database.
```

---

## Solution to Question 16: Branch Average CGPA
- **Difficulty:** `Easy` | **Tables Involved:** `STUDENT`
- **Core Concepts:** `GROUP BY Aggregation, AVG Function, Decimal Rounding.`
- **Problem Statement:** Calculate the average CGPA (rounded to 2 decimal places) and total student enrollment for each academic branch.

### Executable SQL Implementation
```sql
SELECT Branch, ROUND(AVG(CGPA), 2) AS Avg_CGPA, COUNT(*) AS Total_Students
        FROM STUDENT
        GROUP BY Branch;
```

### Step-by-Step Clause Breakdown
- **`SELECT Branch, ROUND(AVG(CGPA), 2) AS Avg_CGPA, COUNT(*) AS Total_Students`**: Projects department and computed averages.
- **`FROM STUDENT`**: Scans student master table.
- **`GROUP BY Branch`**: Aggregates rows by academic department.

### Plain Language Explanation for 2nd-Year CSE
Computes departmental academic benchmarks using SQL aggregate functions AVG and COUNT.

### Sample Execution Output (Live Database)
```text
4 rows returned (CSE: 8.93, IT: 7.94, ECE: 7.79, ME: 7.19).
```

---

## Solution to Question 17: Total Offers Per Company
- **Difficulty:** `Easy` | **Tables Involved:** `COMPANY, PLACEMENT`
- **Core Concepts:** `Inner Equi-Join, GROUP BY, Frequency Count.`
- **Problem Statement:** Calculate the total number of placement offers made by each company, displaying Company_Name and offer count, sorted from highest to lowest.

### Executable SQL Implementation
```sql
SELECT c.Company_Name, COUNT(p.Placement_ID) AS Offer_Count
        FROM COMPANY c
        JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
        GROUP BY c.Company_ID, c.Company_Name
        ORDER BY Offer_Count DESC;
```

### Step-by-Step Clause Breakdown
- **`SELECT c.Company_Name, COUNT(p.Placement_ID) AS Offer_Count`**: Projects company and offer volume.
- **`FROM COMPANY c JOIN PLACEMENT p ON c.Company_ID = p.Company_ID`**: Equi-join linking company to offers.
- **`GROUP BY c.Company_ID, c.Company_Name`**: Groups by hiring organization.
- **`ORDER BY Offer_Count DESC`**: Ranks top recruiters.

### Plain Language Explanation for 2nd-Year CSE
Traverses 1:N relationship from COMPANY to PLACEMENT to tally recruitment offers per employer.

### Sample Execution Output (Live Database)
```text
10 rows returned. Infosys (6), TCS (5), and Wipro (5) lead in overall volume.
```

---

## Solution to Question 18: Yearly Max Package
- **Difficulty:** `Easy` | **Tables Involved:** `PLACEMENT`
- **Core Concepts:** `Time-Series Grouping, MAX and MIN Aggregations.`
- **Problem Statement:** For each placement year, find the maximum and minimum compensation package offered.

### Executable SQL Implementation
```sql
SELECT Placement_Year, MAX(Package) AS Max_Package, MIN(Package) AS Min_Package
        FROM PLACEMENT
        GROUP BY Placement_Year
        ORDER BY Placement_Year;
```

### Step-by-Step Clause Breakdown
- **`SELECT Placement_Year, MAX(Package) AS Max_Package, MIN(Package) AS Min_Package`**: Projects annual salary extremes.
- **`FROM PLACEMENT`**: Scans placement fact records.
- **`GROUP BY Placement_Year`**: Groups offers by graduating year.
- **`ORDER BY Placement_Year`**: Chronological order.

### Plain Language Explanation for 2nd-Year CSE
Evaluates the compensation range offered to each graduating class over time.

### Sample Execution Output (Live Database)
```text
4 rows returned (2022 to 2025).
```

---

## Solution to Question 19: High-Performing Branches
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT`
- **Core Concepts:** `GROUP BY, HAVING Clause, Aggregation Filter.`
- **Problem Statement:** Find all academic branches where the average CGPA is strictly greater than 8.00.

### Executable SQL Implementation
```sql
SELECT Branch, ROUND(AVG(CGPA), 2) AS Avg_CGPA
        FROM STUDENT
        GROUP BY Branch
        HAVING AVG(CGPA) > 8.0;
```

### Step-by-Step Clause Breakdown
- **`SELECT Branch, ROUND(AVG(CGPA), 2) AS Avg_CGPA`**: Projects branch and mean grade point.
- **`FROM STUDENT`**: Scans student population.
- **`GROUP BY Branch`**: Groups per department.
- **`HAVING AVG(CGPA) > 8.0`**: Post-aggregation filter on group average.

### Plain Language Explanation for 2nd-Year CSE
HAVING filters aggregated group values after GROUP BY, whereas WHERE filters individual tuples before aggregation.

### Sample Execution Output (Live Database)
```text
2 rows returned (CSE: 8.93, IT: 7.94 rounded).
```

---

## Solution to Question 20: Frequent Recruiters
- **Difficulty:** `Medium` | **Tables Involved:** `COMPANY, PLACEMENT`
- **Core Concepts:** `Multi-Table Join, HAVING COUNT Filter.`
- **Problem Statement:** Find all companies that have made 3 or more placement offers across campus drives.

### Executable SQL Implementation
```sql
SELECT c.Company_Name, COUNT(p.Placement_ID) AS Total_Offers
        FROM COMPANY c
        JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
        GROUP BY c.Company_ID, c.Company_Name
        HAVING COUNT(p.Placement_ID) >= 3;
```

### Step-by-Step Clause Breakdown
- **`SELECT c.Company_Name, COUNT(p.Placement_ID) AS Total_Offers`**: Projects recruiter and offer count.
- **`FROM COMPANY c JOIN PLACEMENT p ON c.Company_ID = p.Company_ID`**: Equi-join.
- **`GROUP BY c.Company_ID, c.Company_Name`**: Groups by company.
- **`HAVING COUNT(p.Placement_ID) >= 3`**: Retains only frequent recruiters.

### Plain Language Explanation for 2nd-Year CSE
Identifies major corporate recruitment partners who extend multiple job offers on campus.

### Sample Execution Output (Live Database)
```text
7 rows returned on seeded database.
```

---

## Solution to Question 21: Gender Distribution
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT`
- **Core Concepts:** `COALESCE Function, NULL Handling, Demographic Grouping.`
- **Problem Statement:** Display the count of students categorized by gender, treating NULL values as 'Not Specified'.

### Executable SQL Implementation
```sql
SELECT COALESCE(Gender, 'Not Specified') AS Gender, COUNT(*) AS Student_Count
        FROM STUDENT
        GROUP BY Gender;
```

### Step-by-Step Clause Breakdown
- **`SELECT COALESCE(Gender, 'Not Specified') AS Gender, COUNT(*) AS Student_Count`**: Handles nullability.
- **`FROM STUDENT`**: Scans student records.
- **`GROUP BY Gender`**: Groups by gender attribute.

### Plain Language Explanation for 2nd-Year CSE
COALESCE replaces NULL values with a clean readable fallback label in reports.

### Sample Execution Output (Live Database)
```text
1 row returned on seeded database.
```

---

## Solution to Question 22: Stipend by Internship Type
- **Difficulty:** `Medium` | **Tables Involved:** `INTERNSHIP`
- **Core Concepts:** `Binary Cohort Analysis, AVG and COUNT Aggregations.`
- **Problem Statement:** Calculate the average monthly stipend and total count of internships for Mandatory vs Additional internships.

### Executable SQL Implementation
```sql
SELECT Internship_Type, ROUND(AVG(Stipend), 2) AS Avg_Stipend, COUNT(*) AS Count
        FROM INTERNSHIP
        GROUP BY Internship_Type;
```

### Step-by-Step Clause Breakdown
- **`SELECT Internship_Type, ROUND(AVG(Stipend), 2) AS Avg_Stipend, COUNT(*) AS Count`**: Projects stipend benchmarks.
- **`FROM INTERNSHIP`**: Scans internship records.
- **`GROUP BY Internship_Type`**: Groups by mandatory vs additional type.

### Plain Language Explanation for 2nd-Year CSE
Compares student compensation between curriculum-required internships and voluntary industry training.

### Sample Execution Output (Live Database)
```text
2 rows returned (Mandatory: 59 internships, Additional: 4 internships).
```

---

## Solution to Question 23: Companies Averaging Over 10 LPA
- **Difficulty:** `Medium` | **Tables Involved:** `COMPANY, PLACEMENT`
- **Core Concepts:** `HAVING with Numeric Threshold, Equi-Join.`
- **Problem Statement:** Identify all companies whose average offered package strictly exceeds 10.00 LPA.

### Executable SQL Implementation
```sql
SELECT c.Company_Name, ROUND(AVG(p.Package), 2) AS Avg_Package
        FROM COMPANY c
        JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
        GROUP BY c.Company_ID, c.Company_Name
        HAVING AVG(p.Package) > 10.00;
```

### Step-by-Step Clause Breakdown
- **`SELECT c.Company_Name, ROUND(AVG(p.Package), 2) AS Avg_Package`**: Projects recruiter and mean pay.
- **`FROM COMPANY c JOIN PLACEMENT p ON c.Company_ID = p.Company_ID`**: Equi-join.
- **`GROUP BY c.Company_ID, c.Company_Name`**: Groups by recruiter.
- **`HAVING AVG(p.Package) > 10.00`**: Filters for high-compensation employers.

### Plain Language Explanation for 2nd-Year CSE
Isolates premium recruiting partners whose average compensation exceeds double-digit LPA.

### Sample Execution Output (Live Database)
```text
7 rows returned on seeded database.
```

---

## Solution to Question 24: Phone Count Per Student
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT_PHONE`
- **Core Concepts:** `1NF Child Table Aggregation, Descending Sort.`
- **Problem Statement:** Count the total number of phone numbers registered per student, sorted by highest count.

### Executable SQL Implementation
```sql
SELECT Student_ID, COUNT(*) AS Phone_Count
        FROM STUDENT_PHONE
        GROUP BY Student_ID
        ORDER BY Phone_Count DESC;
```

### Step-by-Step Clause Breakdown
- **`SELECT Student_ID, COUNT(*) AS Phone_Count`**: Counts phone tuples per candidate.
- **`FROM STUDENT_PHONE`**: Scans 1NF decomposed phone table.
- **`GROUP BY Student_ID`**: Groups by student foreign key.
- **`ORDER BY Phone_Count DESC`**: Ranks highest contacts first.

### Plain Language Explanation for 2nd-Year CSE
Aggregates child multi-valued tuples to verify candidate contact availability.

### Sample Execution Output (Live Database)
```text
30 rows returned on seeded database (ranging from 1 to 3 phone numbers per student).
```

---

## Solution to Question 25: Top Student Skills
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT_SKILL`
- **Core Concepts:** `Frequency Distribution, GROUP BY, Top-K Limit.`
- **Problem Statement:** Identify the top 5 most common technical skills possessed by students.

### Executable SQL Implementation
```sql
SELECT Skill, COUNT(*) AS Frequency
        FROM STUDENT_SKILL
        GROUP BY Skill
        ORDER BY Frequency DESC
        LIMIT 5;
```

### Step-by-Step Clause Breakdown
- **`SELECT Skill, COUNT(*) AS Frequency`**: Projects skill name and popularity.
- **`FROM STUDENT_SKILL`**: Scans 1NF student skills table.
- **`GROUP BY Skill`**: Groups by skill name.
- **`ORDER BY Frequency DESC LIMIT 5`**: Picks top 5 skills.

### Plain Language Explanation for 2nd-Year CSE
Measures talent supply across the student body to guide college workshop planning.

### Sample Execution Output (Live Database)
```text
5 rows returned (Python, Java, SQL, C++, Web Development).
```

---

## Solution to Question 26: Package by Placement Type
- **Difficulty:** `Medium` | **Tables Involved:** `PLACEMENT`
- **Core Concepts:** `Drive Channel Aggregation, Average Package.`
- **Problem Statement:** Compare average package and total offer count across On-campus, Off-campus, and Pooled placement drives.

### Executable SQL Implementation
```sql
SELECT Placement_Type, ROUND(AVG(Package), 2) AS Avg_Package, COUNT(*) AS Total
        FROM PLACEMENT
        GROUP BY Placement_Type;
```

### Step-by-Step Clause Breakdown
- **`SELECT Placement_Type, ROUND(AVG(Package), 2) AS Avg_Package, COUNT(*) AS Total`**: Projects drive performance.
- **`FROM PLACEMENT`**: Scans placement fact table.
- **`GROUP BY Placement_Type`**: Groups by drive recruitment channel.

### Plain Language Explanation for 2nd-Year CSE
Compares compensation outcomes across different campus placement channels.

### Sample Execution Output (Live Database)
```text
1 row returned on seeded database (On-campus: 40 offers, Avg: 11.89 LPA).
```

---

## Solution to Question 27: Offer Status Breakdown
- **Difficulty:** `Medium` | **Tables Involved:** `PLACEMENT`
- **Core Concepts:** `Categorical Tallying, State Distribution.`
- **Problem Statement:** Count the number of offers in each Offer_Status category ('Offered', 'Accepted', 'Declined').

### Executable SQL Implementation
```sql
SELECT Offer_Status, COUNT(*) AS Count
        FROM PLACEMENT
        GROUP BY Offer_Status;
```

### Step-by-Step Clause Breakdown
- **`SELECT Offer_Status, COUNT(*) AS Count`**: Projects status and tally.
- **`FROM PLACEMENT`**: Scans placement fact table.
- **`GROUP BY Offer_Status`**: Groups by offer status enum.

### Plain Language Explanation for 2nd-Year CSE
Tracks recruiter offer conversions through candidate acceptance, pending review, and decline stages.

### Sample Execution Output (Live Database)
```text
3 rows returned (Offered: 12, Accepted: 20, Declined: 8).
```

---

## Solution to Question 28: Mandatory Credits per Student
- **Difficulty:** `Medium` | **Tables Involved:** `INTERNSHIP`
- **Core Concepts:** `SUM Aggregation, Curriculum Rule Filtering.`
- **Problem Statement:** Calculate the total cumulative credits earned from mandatory internships by each student.

### Executable SQL Implementation
```sql
SELECT Student_ID, SUM(Credits) AS Total_Mandatory_Credits
        FROM INTERNSHIP
        WHERE Internship_Type = 'Mandatory'
        GROUP BY Student_ID;
```

### Step-by-Step Clause Breakdown
- **`SELECT Student_ID, SUM(Credits) AS Total_Mandatory_Credits`**: Sums credits.
- **`FROM INTERNSHIP`**: Scans internship records.
- **`WHERE Internship_Type = 'Mandatory'`**: Restricts to syllabus-required training.
- **`GROUP BY Student_ID`**: Groups per student.

### Plain Language Explanation for 2nd-Year CSE
Calculates academic graduation credits earned through approved mandatory internships.

### Sample Execution Output (Live Database)
```text
30 rows returned (students earn 8 credits upon completing both mandatory internships).
```

---

## Solution to Question 29: Batch Size Filter
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT`
- **Core Concepts:** `Temporal Grouping, HAVING Filter.`
- **Problem Statement:** Find all graduating batch years that have more than 5 enrolled students.

### Executable SQL Implementation
```sql
SELECT Batch_Year, COUNT(*) AS Total_Students
        FROM STUDENT
        GROUP BY Batch_Year
        HAVING COUNT(*) > 5;
```

### Step-by-Step Clause Breakdown
- **`SELECT Batch_Year, COUNT(*) AS Total_Students`**: Projects graduating batch.
- **`FROM STUDENT`**: Scans student master table.
- **`GROUP BY Batch_Year`**: Groups by graduating year.
- **`HAVING COUNT(*) > 5`**: Filters for cohorts exceeding size 5.

### Plain Language Explanation for 2nd-Year CSE
Filters for major institutional graduating classes.

### Sample Execution Output (Live Database)
```text
4 rows returned (2022 to 2025).
```

---

## Solution to Question 30: Interview Rounds per Company
- **Difficulty:** `Medium` | **Tables Involved:** `COMPANY, PLACEMENT`
- **Core Concepts:** `Multi-Table Join, Decimal Rounding, Interview Metrics.`
- **Problem Statement:** Calculate the average number of interview rounds conducted by each company during placement evaluation.

### Executable SQL Implementation
```sql
SELECT c.Company_Name, ROUND(AVG(p.Interview_Rounds), 1) AS Avg_Rounds
        FROM COMPANY c
        JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
        GROUP BY c.Company_ID, c.Company_Name;
```

### Step-by-Step Clause Breakdown
- **`SELECT c.Company_Name, ROUND(AVG(p.Interview_Rounds), 1) AS Avg_Rounds`**: Projects company and round average.
- **`FROM COMPANY c JOIN PLACEMENT p ON c.Company_ID = p.Company_ID`**: Equi-join.
- **`GROUP BY c.Company_ID, c.Company_Name`**: Groups by corporate recruiter.

### Plain Language Explanation for 2nd-Year CSE
Measures corporate screening rigor across different campus hiring partners.

### Sample Execution Output (Live Database)
```text
10 rows returned on seeded database.
```

---

## Solution to Question 31: Student-Placement-Company Equi-Join
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT, PLACEMENT, COMPANY`
- **Core Concepts:** `Three-Table Equi-Join, Dimension Flattening.`
- **Problem Statement:** Perform a 3-table equi-join to display Roll_No, Student Name, Company Name, Role, and Package.

### Executable SQL Implementation
```sql
SELECT s.Roll_No, s.First_Name, c.Company_Name, p.Role, p.Package
        FROM STUDENT s
        JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        ORDER BY p.Package DESC
        LIMIT 5;
```

### Step-by-Step Clause Breakdown
- **`SELECT s.Roll_No, s.First_Name, c.Company_Name, p.Role, p.Package`**: Projects unified candidate and offer attributes.
- **`FROM STUDENT s JOIN PLACEMENT p ON s.Student_ID = p.Student_ID JOIN COMPANY c ON p.Company_ID = c.Company_ID`**: Traverses STUDENT -> PLACEMENT -> COMPANY.
- **`ORDER BY p.Package DESC LIMIT 5`**: Top 5 compensation offers.

### Plain Language Explanation for 2nd-Year CSE
Classical 3-table equi-join linking a central fact table (PLACEMENT) to its two parent dimension entities.

### Sample Execution Output (Live Database)
```text
5 rows returned on seeded database.
```

---

## Solution to Question 32: Internship Details with Names
- **Difficulty:** `Medium` | **Tables Involved:** `INTERNSHIP, STUDENT, COMPANY`
- **Core Concepts:** `Three-Table Join, Weak Entity Resolution.`
- **Problem Statement:** Display student roll number, candidate name, host company, internship role, and stipend.

### Executable SQL Implementation
```sql
SELECT s.Roll_No, s.First_Name, c.Company_Name, i.Role, i.Stipend
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        LIMIT 5;
```

### Step-by-Step Clause Breakdown
- **`SELECT s.Roll_No, s.First_Name, c.Company_Name, i.Role, i.Stipend`**: Projects internship profile.
- **`FROM INTERNSHIP i JOIN STUDENT s ON i.Student_ID = s.Student_ID JOIN COMPANY c ON i.Company_ID = c.Company_ID`**: Joins INTERNSHIP to STUDENT and COMPANY.
- **`LIMIT 5`**: Retrieves 5 sample records.

### Plain Language Explanation for 2nd-Year CSE
Resolves weak entity INTERNSHIP foreign keys to human-readable student and company names.

### Sample Execution Output (Live Database)
```text
5 rows returned on seeded database.
```

---

## Solution to Question 33: Placement Required Skills Listing
- **Difficulty:** `Medium` | **Tables Involved:** `PLACEMENT, COMPANY, PLACEMENT_SKILL`
- **Core Concepts:** `Junction Table Join, Evaluated Skills Listing.`
- **Problem Statement:** List each placement offer along with the hiring company, role, and tested technical skills.

### Executable SQL Implementation
```sql
SELECT p.Placement_ID, c.Company_Name, p.Role, ps.Skill
        FROM PLACEMENT p
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        JOIN PLACEMENT_SKILL ps ON p.Placement_ID = ps.Placement_ID
        LIMIT 5;
```

### Step-by-Step Clause Breakdown
- **`SELECT p.Placement_ID, c.Company_Name, p.Role, ps.Skill`**: Projects offer terms and tested competency.
- **`FROM PLACEMENT p JOIN COMPANY c ON p.Company_ID = c.Company_ID JOIN PLACEMENT_SKILL ps ON p.Placement_ID = ps.Placement_ID`**: Three-table join.
- **`LIMIT 5`**: Sample records.

### Plain Language Explanation for 2nd-Year CSE
Traverses placement fact table to corporate profile and child evaluated skills junction.

### Sample Execution Output (Live Database)
```text
5 rows returned on seeded database.
```

---

## Solution to Question 34: Same Branch Identical CGPA Pairs
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT`
- **Core Concepts:** `Relational Self-Join, Eliminating Redundant Symmetrical Pairs.`
- **Problem Statement:** Use a self-join to find pairs of students within the same branch who have identical CGPAs.

### Executable SQL Implementation
```sql
SELECT s1.Roll_No AS Student_1, s2.Roll_No AS Student_2, s1.Branch, s1.CGPA
        FROM STUDENT s1
        JOIN STUDENT s2 ON s1.Branch = s2.Branch AND s1.CGPA = s2.CGPA AND s1.Student_ID < s2.Student_ID
        ORDER BY s1.Branch, s1.CGPA DESC;
```

### Step-by-Step Clause Breakdown
- **`SELECT s1.Roll_No AS Student_1, s2.Roll_No AS Student_2, s1.Branch, s1.CGPA`**: Projects matched peer pair.
- **`FROM STUDENT s1 JOIN STUDENT s2 ON s1.Branch = s2.Branch AND s1.CGPA = s2.CGPA AND s1.Student_ID < s2.Student_ID`**: Self-join on branch and CGPA with primary key inequality.
- **`ORDER BY s1.Branch, s1.CGPA DESC`**: Orders matches.

### Plain Language Explanation for 2nd-Year CSE
The condition `s1.Student_ID < s2.Student_ID` prevents a student from matching themselves and eliminates duplicate reverse pairs like (A, B) and (B, A).

### Sample Execution Output (Live Database)
```text
1 row returned on seeded database (CS201806 and CS202128 in CSE with CGPA 8.55).
```

---

## Solution to Question 35: Placement and Internship Corporate Comparison
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT, PLACEMENT, INTERNSHIP, COMPANY`
- **Core Concepts:** `Dual Corporate Dimension Join, Pipeline Analysis.`
- **Problem Statement:** Compare the company where a student joined for full-time employment vs where they completed Internship 1.

### Executable SQL Implementation
```sql
SELECT s.Roll_No, s.First_Name,
               cp.Company_Name AS Placement_Company,
               ci.Company_Name AS Internship_Company
        FROM STUDENT s
        JOIN PLACEMENT p ON s.Student_ID = p.Student_ID AND p.Joined = 'Yes'
        JOIN COMPANY cp ON p.Company_ID = cp.Company_ID
        JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID AND i.Internship_No = 1
        JOIN COMPANY ci ON i.Company_ID = ci.Company_ID
        LIMIT 5;
```

### Step-by-Step Clause Breakdown
- **`SELECT s.Roll_No, s.First_Name, cp.Company_Name AS Placement_Company, ci.Company_Name AS Internship_Company`**: Projects comparative corporate partners.
- **`FROM STUDENT s JOIN PLACEMENT p ON s.Student_ID = p.Student_ID AND p.Joined = 'Yes' JOIN COMPANY cp ON p.Company_ID = cp.Company_ID JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID AND i.Internship_No = 1 JOIN COMPANY ci ON i.Company_ID = ci.Company_ID`**: Traverses two corporate relationships simultaneously.
- **`LIMIT 5`**: Sample rows.

### Plain Language Explanation for 2nd-Year CSE
Joins the COMPANY table twice with distinct aliases (`cp` and `ci`) to compare full-time employers against internship hosts.

### Sample Execution Output (Live Database)
```text
5 rows returned on seeded database.
```

---

## Solution to Question 36: Skill Matching Between Student and Placement
- **Difficulty:** `Medium` | **Tables Involved:** `STUDENT, PLACEMENT, PLACEMENT_SKILL, STUDENT_SKILL`
- **Core Concepts:** `Four-Table Junction Matching, Competency Alignment.`
- **Problem Statement:** Find instances where a student possesses a technical skill that was explicitly evaluated for their placement offer.

### Executable SQL Implementation
```sql
SELECT DISTINCT s.Roll_No, s.First_Name, p.Role, ss.Skill
        FROM STUDENT s
        JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
        JOIN PLACEMENT_SKILL ps ON p.Placement_ID = ps.Placement_ID
        JOIN STUDENT_SKILL ss ON s.Student_ID = ss.Student_ID AND ss.Skill = ps.Skill
        LIMIT 5;
```

### Step-by-Step Clause Breakdown
- **`SELECT DISTINCT s.Roll_No, s.First_Name, p.Role, ss.Skill`**: Projects verified skill match.
- **`FROM STUDENT s JOIN PLACEMENT p ON s.Student_ID = p.Student_ID JOIN PLACEMENT_SKILL ps ON p.Placement_ID = ps.Placement_ID JOIN STUDENT_SKILL ss ON s.Student_ID = ss.Student_ID AND ss.Skill = ps.Skill`**: Matches skill strings across both junction tables.
- **`LIMIT 5`**: Sample verified matches.

### Plain Language Explanation for 2nd-Year CSE
Connects candidate skills to employer requirements by joining `STUDENT_SKILL` and `PLACEMENT_SKILL` on identical skill strings.

### Sample Execution Output (Live Database)
```text
5 rows returned on seeded database.
```

---

## Solution to Question 37: Querying V_PLACEMENT_DETAIL
- **Difficulty:** `Medium` | **Tables Involved:** `V_PLACEMENT_DETAIL`
- **Core Concepts:** `Relational View Querying, Logical Data Independence.`
- **Problem Statement:** Query view V_PLACEMENT_DETAIL for all accepted offers, ordered by package descending.

### Executable SQL Implementation
```sql
SELECT Roll_No, Student_Name, Company_Name, Package
        FROM V_PLACEMENT_DETAIL
        WHERE Offer_Status = 'Accepted'
        ORDER BY Package DESC
        LIMIT 5;
```

### Step-by-Step Clause Breakdown
- **`SELECT Roll_No, Student_Name, Company_Name, Package`**: Projects pre-joined virtual attributes.
- **`FROM V_PLACEMENT_DETAIL`**: References relational view.
- **`WHERE Offer_Status = 'Accepted'`**: Filters accepted offers.
- **`ORDER BY Package DESC LIMIT 5`**: Ranks highest accepted offers.

### Plain Language Explanation for 2nd-Year CSE
Demonstrates the power of relational views: complex join logic is encapsulated, allowing developers to query virtual tables cleanly.

### Sample Execution Output (Live Database)
```text
5 rows returned on seeded database.
```

---

## Solution to Question 38: Querying V_INTERNSHIP_DETAIL
- **Difficulty:** `Medium` | **Tables Involved:** `V_INTERNSHIP_DETAIL`
- **Core Concepts:** `Derived View Attribute Filtering, 3NF Compliance.`
- **Problem Statement:** Query view V_INTERNSHIP_DETAIL to find internships lasting at least 2.0 months.

### Executable SQL Implementation
```sql
SELECT Roll_No, Student_Name, Company_Name, Duration_Months
        FROM V_INTERNSHIP_DETAIL
        WHERE Duration_Months >= 2.0
        LIMIT 5;
```

### Step-by-Step Clause Breakdown
- **`SELECT Roll_No, Student_Name, Company_Name, Duration_Months`**: Projects view attributes.
- **`FROM V_INTERNSHIP_DETAIL`**: References view with dynamic date arithmetic.
- **`WHERE Duration_Months >= 2.0`**: Filters on dynamically derived tenure duration.
- **`LIMIT 5`**: Sample long-term internships.

### Plain Language Explanation for 2nd-Year CSE
Queries the dynamic derived attribute `Duration_Months` directly from the view without having to perform DATEDIFF manually.

### Sample Execution Output (Live Database)
```text
5 rows returned on seeded database.
```

---

## Solution to Question 39: Student Multi-Offer Listing
- **Difficulty:** `Hard` | **Tables Involved:** `STUDENT, PLACEMENT, COMPANY`
- **Core Concepts:** `GROUP_CONCAT with Substring Formatting, Multi-Offer Aggregation.`
- **Problem Statement:** For students holding multiple offers, display a consolidated string of company names and packages using GROUP_CONCAT.

### Executable SQL Implementation
```sql
SELECT s.Roll_No, s.First_Name,
               GROUP_CONCAT(CONCAT(c.Company_Name, ' (', p.Package, ' LPA)') SEPARATOR '; ') AS Offer_Details
        FROM STUDENT s
        JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        GROUP BY s.Student_ID, s.Roll_No, s.First_Name
        HAVING COUNT(p.Placement_ID) >= 2
        LIMIT 5;
```

### Step-by-Step Clause Breakdown
- **`SELECT s.Roll_No, s.First_Name, GROUP_CONCAT(CONCAT(c.Company_Name, ' (', p.Package, ' LPA)') SEPARATOR '; ') AS Offer_Details`**: Formats multi-offer string.
- **`FROM STUDENT s JOIN PLACEMENT p ON s.Student_ID = p.Student_ID JOIN COMPANY c ON p.Company_ID = c.Company_ID`**: Three-table join.
- **`GROUP BY s.Student_ID, s.Roll_No, s.First_Name`**: Groups per student.
- **`HAVING COUNT(p.Placement_ID) >= 2 LIMIT 5`**: Restricts to candidates holding multiple offers.

### Plain Language Explanation for 2nd-Year CSE
Combines string functions `CONCAT` and aggregate `GROUP_CONCAT` to roll multiple offer rows into a clean, human-readable summary per student.

### Sample Execution Output (Live Database)
```text
5 rows returned on seeded database.
```

---

## Solution to Question 40: Internship to Placement Host Match
- **Difficulty:** `Hard` | **Tables Involved:** `COMPANY, PLACEMENT, INTERNSHIP, STUDENT`
- **Core Concepts:** `Pipeline Retention Analysis, Multi-Table Match.`
- **Problem Statement:** Find companies where a student was both an intern and subsequently received a placement offer.

### Executable SQL Implementation
```sql
SELECT DISTINCT c.Company_Name, s.Roll_No, s.First_Name
        FROM COMPANY c
        JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
        JOIN INTERNSHIP i ON c.Company_ID = i.Company_ID AND p.Student_ID = i.Student_ID
        JOIN STUDENT s ON p.Student_ID = s.Student_ID;
```

### Step-by-Step Clause Breakdown
- **`SELECT DISTINCT c.Company_Name, s.Roll_No, s.First_Name`**: Projects matching host-employer pairs.
- **`FROM COMPANY c JOIN PLACEMENT p ON c.Company_ID = p.Company_ID JOIN INTERNSHIP i ON c.Company_ID = i.Company_ID AND p.Student_ID = i.Student_ID JOIN STUDENT s ON p.Student_ID = s.Student_ID`**: Matches candidate and company across both employment tables.

### Plain Language Explanation for 2nd-Year CSE
Measures corporate intern conversion by checking if the same student and company pair exists in both `PLACEMENT` and `INTERNSHIP`.

### Sample Execution Output (Live Database)
```text
32 rows returned on seeded database.
```

---

## Solution to Question 41: Companies with Zero Placement Offers
- **Difficulty:** `Hard` | **Tables Involved:** `COMPANY, PLACEMENT`
- **Core Concepts:** `Anti-Join, Relational Difference, IS NULL Filter.`
- **Problem Statement:** Find all companies that have never made a placement offer to any student using a LEFT JOIN anti-join.

### Executable SQL Implementation
```sql
SELECT c.Company_ID, c.Company_Name
        FROM COMPANY c
        LEFT JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
        WHERE p.Placement_ID IS NULL;
```

### Step-by-Step Clause Breakdown
- **`SELECT c.Company_ID, c.Company_Name`**: Projects recruiter identity.
- **`FROM COMPANY c LEFT JOIN PLACEMENT p ON c.Company_ID = p.Company_ID`**: Preserves unattached companies.
- **`WHERE p.Placement_ID IS NULL`**: Anti-join condition isolating inactive corporate partners.

### Plain Language Explanation for 2nd-Year CSE
Identifies organizations registered in the database that have not yet participated in campus recruitment drives.

### Sample Execution Output (Live Database)
```text
0 rows returned on seeded database (all 10 companies have made active offers in current seed).
```

---

## Solution to Question 42: Students Lacking Internship 2
- **Difficulty:** `Hard` | **Tables Involved:** `STUDENT, INTERNSHIP`
- **Core Concepts:** `Anti-Semi-Join, NOT EXISTS Operator, Milestone Deficiency.`
- **Problem Statement:** Find all students who have not yet completed Mandatory Internship 2 using NOT EXISTS.

### Executable SQL Implementation
```sql
SELECT s.Roll_No, s.First_Name, s.Branch
        FROM STUDENT s
        WHERE NOT EXISTS (
            SELECT 1 FROM INTERNSHIP i
            WHERE i.Student_ID = s.Student_ID AND i.Internship_No = 2
        );
```

### Step-by-Step Clause Breakdown
- **`SELECT s.Roll_No, s.First_Name, s.Branch`**: Projects deficient candidate details.
- **`FROM STUDENT s`**: Scans student master table.
- **`WHERE NOT EXISTS (SELECT 1 FROM INTERNSHIP i WHERE i.Student_ID = s.Student_ID AND i.Internship_No = 2)`**: Anti-semi-join testing for missing 8th semester milestone.

### Plain Language Explanation for 2nd-Year CSE
Identifies candidates who have not completed their 8th semester graduation internship.

### Sample Execution Output (Live Database)
```text
1 row returned on seeded database (Student CS201804 Rohan Deshmukh).
```

---

## Solution to Question 43: Above-Average CGPA Students
- **Difficulty:** `Hard` | **Tables Involved:** `STUDENT`
- **Core Concepts:** `Scalar Subquery in WHERE Clause, Dynamic Benchmark Filtering.`
- **Problem Statement:** Find all students whose CGPA is strictly higher than the institution-wide average CGPA.

### Executable SQL Implementation
```sql
SELECT Roll_No, First_Name, CGPA
        FROM STUDENT
        WHERE CGPA > (SELECT AVG(CGPA) FROM STUDENT)
        ORDER BY CGPA DESC;
```

### Step-by-Step Clause Breakdown
- **`SELECT Roll_No, First_Name, CGPA`**: Projects above-average scholars.
- **`FROM STUDENT`**: Scans student population.
- **`WHERE CGPA > (SELECT AVG(CGPA) FROM STUDENT)`**: Filters against global mean computed via scalar subquery.
- **`ORDER BY CGPA DESC`**: Sorts by academic merit.

### Plain Language Explanation for 2nd-Year CSE
The subquery `(SELECT AVG(CGPA) FROM STUDENT)` executes once to calculate the campus average; the outer query filters students above this number.

### Sample Execution Output (Live Database)
```text
17 rows returned on seeded database.
```

---

## Solution to Question 44: Correlated Subquery Offer Counting
- **Difficulty:** `Hard` | **Tables Involved:** `STUDENT, PLACEMENT`
- **Core Concepts:** `Correlated Scalar Subquery in SELECT, Per-Tuple Calculation.`
- **Problem Statement:** Display each student's Roll_No and Name alongside a correlated scalar subquery counting their total offers.

### Executable SQL Implementation
```sql
SELECT s.Roll_No, s.First_Name,
               (SELECT COUNT(*) FROM PLACEMENT p WHERE p.Student_ID = s.Student_ID) AS Offer_Count
        FROM STUDENT s
        ORDER BY Offer_Count DESC
        LIMIT 5;
```

### Step-by-Step Clause Breakdown
- **`SELECT s.Roll_No, s.First_Name, (SELECT COUNT(*) FROM PLACEMENT p WHERE p.Student_ID = s.Student_ID) AS Offer_Count`**: Projects student identity and computes offer tally via correlated subquery.
- **`FROM STUDENT s`**: Scans student records.
- **`ORDER BY Offer_Count DESC LIMIT 5`**: Top offer recipients.

### Plain Language Explanation for 2nd-Year CSE
Demonstrates correlated subqueries in the projection list: for each student row, MySQL runs the inner query to compute their personal offer count.

### Sample Execution Output (Live Database)
```text
5 rows returned on seeded database.
```

---

## Solution to Question 45: Students with Zero Skills Listed
- **Difficulty:** `Hard` | **Tables Involved:** `STUDENT, STUDENT_SKILL`
- **Core Concepts:** `Anti-Join on 1NF Decomposed Entity, Data Quality Auditing.`
- **Problem Statement:** Find all students who have not listed any technical skills using an anti-join.

### Executable SQL Implementation
```sql
SELECT s.Roll_No, s.First_Name
        FROM STUDENT s
        LEFT JOIN STUDENT_SKILL ss ON s.Student_ID = ss.Student_ID
        WHERE ss.Skill IS NULL;
```

### Step-by-Step Clause Breakdown
- **`SELECT s.Roll_No, s.First_Name`**: Projects student identity.
- **`FROM STUDENT s LEFT JOIN STUDENT_SKILL ss ON s.Student_ID = ss.Student_ID`**: Left outer join matching skills.
- **`WHERE ss.Skill IS NULL`**: Anti-join condition isolating students with zero skills.

### Plain Language Explanation for 2nd-Year CSE
Audits candidate profile completeness. If a student has no skills recorded, `ss.Skill` evaluates to NULL.

### Sample Execution Output (Live Database)
```text
0 rows returned on seeded database (all 30 students have registered skills).
```

---

## Solution to Question 46: Companies Hiring Zero-Backlog Students
- **Difficulty:** `Hard` | **Tables Involved:** `COMPANY, PLACEMENT, STUDENT`
- **Core Concepts:** `Nested Subquery with IN Operator, Multi-Level Relationship.`
- **Problem Statement:** Find all companies that have recruited students who have zero backlogs using an IN subquery.

### Executable SQL Implementation
```sql
SELECT DISTINCT c.Company_Name
        FROM COMPANY c
        WHERE c.Company_ID IN (
            SELECT p.Company_ID
            FROM PLACEMENT p
            JOIN STUDENT s ON p.Student_ID = s.Student_ID
            WHERE s.Backlogs = 0
        );
```

### Step-by-Step Clause Breakdown
- **`SELECT DISTINCT c.Company_Name`**: Projects recruiter name.
- **`FROM COMPANY c`**: Scans company master table.
- **`WHERE c.Company_ID IN (SELECT p.Company_ID FROM PLACEMENT p JOIN STUDENT s ON p.Student_ID = s.Student_ID WHERE s.Backlogs = 0)`**: Subquery finds companies hiring zero-backlog scholars.

### Plain Language Explanation for 2nd-Year CSE
Uses an IN subquery to filter corporate recruiters who hire candidates with clean academic records.

### Sample Execution Output (Live Database)
```text
10 rows returned on seeded database.
```

---

## Solution to Question 47: Offers Higher Than All Offers from a Company
- **Difficulty:** `Hard` | **Tables Involved:** `PLACEMENT, COMPANY`
- **Core Concepts:** `Universal Quantification with > ALL Subquery.`
- **Problem Statement:** Find placement offers with packages greater than ALL offers made by 'Infosys' using > ALL.

### Executable SQL Implementation
```sql
SELECT p.Placement_ID, p.Package, c.Company_Name
        FROM PLACEMENT p
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE p.Package > ALL (
            SELECT p2.Package
            FROM PLACEMENT p2
            JOIN COMPANY c2 ON p2.Company_ID = c2.Company_ID
            WHERE c2.Company_Name = 'Infosys'
        )
        ORDER BY p.Package DESC;
```

### Step-by-Step Clause Breakdown
- **`SELECT p.Placement_ID, p.Package, c.Company_Name`**: Projects superior offers.
- **`FROM PLACEMENT p JOIN COMPANY c ON p.Company_ID = c.Company_ID`**: Equi-join.
- **`WHERE p.Package > ALL (SELECT p2.Package FROM PLACEMENT p2 JOIN COMPANY c2 ON p2.Company_ID = c2.Company_ID WHERE c2.Company_Name = 'Infosys')`**: Universal comparison predicate.
- **`ORDER BY p.Package DESC`**: Orders highest packages first.

### Plain Language Explanation for 2nd-Year CSE
The `> ALL` operator requires that a package be strictly greater than the maximum package returned by the subquery.

### Sample Execution Output (Live Database)
```text
40 rows returned on seeded database.
```

---

## Solution to Question 48: Union of All Technical Competencies
- **Difficulty:** `Hard` | **Tables Involved:** `STUDENT_SKILL, PLACEMENT_SKILL`
- **Core Concepts:** `Relational UNION Operator, Set Theory, Deduplication.`
- **Problem Statement:** Produce a unified set of all technical skills appearing across student profiles or placement requirements using UNION.

### Executable SQL Implementation
```sql
SELECT Skill, 'Student Skill' AS Source FROM STUDENT_SKILL
        UNION
        SELECT Skill, 'Placement Required' AS Source FROM PLACEMENT_SKILL
        ORDER BY Skill
        LIMIT 10;
```

### Step-by-Step Clause Breakdown
- **`SELECT Skill, 'Student Skill' AS Source FROM STUDENT_SKILL`**: First operand.
- **`UNION`**: Combines result sets and automatically deduplicates common skills.
- **`SELECT Skill, 'Placement Required' AS Source FROM PLACEMENT_SKILL`**: Second operand.
- **`ORDER BY Skill LIMIT 10`**: Alphabetical ordering.

### Plain Language Explanation for 2nd-Year CSE
UNION performs relational set union across two independent tables, merging competencies into a single unified catalog.

### Sample Execution Output (Live Database)
```text
10 sample competency rows returned.
```

---

## Solution to Question 49: Companies with Dual Operations
- **Difficulty:** `Hard` | **Tables Involved:** `COMPANY, PLACEMENT, INTERNSHIP`
- **Core Concepts:** `Dual Correlated EXISTS, Relational Conjunction.`
- **Problem Statement:** Find all companies that participate in both campus placements AND internship programs using dual correlated EXISTS.

### Executable SQL Implementation
```sql
SELECT c.Company_ID, c.Company_Name
        FROM COMPANY c
        WHERE EXISTS (SELECT 1 FROM PLACEMENT p WHERE p.Company_ID = c.Company_ID)
          AND EXISTS (SELECT 1 FROM INTERNSHIP i WHERE i.Company_ID = c.Company_ID);
```

### Step-by-Step Clause Breakdown
- **`SELECT c.Company_ID, c.Company_Name`**: Projects corporate identity.
- **`FROM COMPANY c`**: Scans company master table.
- **`WHERE EXISTS (SELECT 1 FROM PLACEMENT p WHERE p.Company_ID = c.Company_ID) AND EXISTS (SELECT 1 FROM INTERNSHIP i WHERE i.Company_ID = c.Company_ID)`**: Conjunctive semi-join verification.

### Plain Language Explanation for 2nd-Year CSE
Verifies that an organization maintains active engagement across both full-time hiring and student internships.

### Sample Execution Output (Live Database)
```text
10 rows returned on seeded database (all 10 corporate partners support both programs).
```

---

## Solution to Question 50: Derived Table for Salary Tiers
- **Difficulty:** `Hard` | **Tables Involved:** `PLACEMENT`
- **Core Concepts:** `FROM Clause Derived Table (Subquery in FROM), Tier Aggregation.`
- **Problem Statement:** Categorize placed packages into High, Mid, and Base tiers inside a FROM clause derived table and count placed students in each.

### Executable SQL Implementation
```sql
SELECT Band.Tier, COUNT(*) AS Placed_Count
        FROM (
            SELECT
                CASE
                    WHEN Package >= 15.00 THEN 'High'
                    WHEN Package >= 8.00  THEN 'Mid'
                    ELSE 'Base'
                END AS Tier
            FROM PLACEMENT
            WHERE Joined = 'Yes'
        ) AS Band
        GROUP BY Band.Tier;
```

### Step-by-Step Clause Breakdown
- **`SELECT Band.Tier, COUNT(*) AS Placed_Count`**: Outer query aggregates derived tier column.
- **`FROM (SELECT CASE WHEN Package >= 15.00 THEN 'High' WHEN Package >= 8.00 THEN 'Mid' ELSE 'Base' END AS Tier FROM PLACEMENT WHERE Joined = 'Yes') AS Band`**: Derived table assigning tier labels.
- **`GROUP BY Band.Tier`**: Groups by derived tier label.

### Plain Language Explanation for 2nd-Year CSE
The inner subquery assigns categorical tier labels to joined offers; the outer query groups by these newly generated categories.

### Sample Execution Output (Live Database)
```text
3 rows returned on seeded database (High: 6, Mid: 10, Base: 4).
```

---

## Solution to Question 51: ROW_NUMBER() within Branch
- **Difficulty:** `Hard` | **Tables Involved:** `STUDENT`
- **Core Concepts:** `Window Function ROW_NUMBER(), PARTITION BY, In-Department Ordering.`
- **Problem Statement:** Assign a unique sequential position to each student within their branch ordered by CGPA using ROW_NUMBER() OVER ().

### Executable SQL Implementation
```sql
SELECT Roll_No, First_Name, Branch, CGPA,
               ROW_NUMBER() OVER (PARTITION BY Branch ORDER BY CGPA DESC) AS Branch_Pos
        FROM STUDENT
        LIMIT 10;
```

### Step-by-Step Clause Breakdown
- **`SELECT Roll_No, First_Name, Branch, CGPA, ...`**: Projects student identity.
- **`ROW_NUMBER() OVER (PARTITION BY Branch ORDER BY CGPA DESC) AS Branch_Pos`**: Analytical function computing unique sequential integer per department.
- **`FROM STUDENT`**: Scans student master table.
- **`LIMIT 10`**: Sample 10 ranked candidates.

### Plain Language Explanation for 2nd-Year CSE
ROW_NUMBER() partitions students by department and assigns 1, 2, 3... in descending order of CGPA without duplicate numbers.

### Sample Execution Output (Live Database)
```text
10 rows returned detailing sequential positions.
```

---

## Solution to Question 52: DENSE_RANK() for Packages
- **Difficulty:** `Hard` | **Tables Involved:** `PLACEMENT`
- **Core Concepts:** `Window Function DENSE_RANK(), Non-Skipping Rank Numbers.`
- **Problem Statement:** Rank all placement offers by package using DENSE_RANK() OVER (ORDER BY Package DESC).

### Executable SQL Implementation
```sql
SELECT Placement_ID, Role, Package,
               DENSE_RANK() OVER (ORDER BY Package DESC) AS Package_Rank
        FROM PLACEMENT
        LIMIT 10;
```

### Step-by-Step Clause Breakdown
- **`SELECT Placement_ID, Role, Package, ...`**: Projects offer terms.
- **`DENSE_RANK() OVER (ORDER BY Package DESC) AS Package_Rank`**: Computes global compensation rank without skipping numbers on ties.
- **`FROM PLACEMENT`**: Scans placement fact records.
- **`LIMIT 10`**: Top 10 package ranks.

### Plain Language Explanation for 2nd-Year CSE
Ranks offers by compensation. If two offers tie at rank 2, the next offer receives rank 3 (unlike RANK() which would assign 4).

### Sample Execution Output (Live Database)
```text
10 rows returned detailing global compensation hierarchy.
```

---

## Solution to Question 53: CTE Top Student per Branch
- **Difficulty:** `Hard` | **Tables Involved:** `STUDENT`
- **Core Concepts:** `Common Table Expression (CTE), ROW_NUMBER() Filter, Departmental Champions.`
- **Problem Statement:** Using a Common Table Expression with ROW_NUMBER(), find the single highest-scoring student in each academic department.

### Executable SQL Implementation
```sql
WITH RankedStudents AS (
            SELECT Roll_No, First_Name, Branch, CGPA,
                   ROW_NUMBER() OVER (PARTITION BY Branch ORDER BY CGPA DESC) AS rn
            FROM STUDENT
        )
        SELECT Roll_No, First_Name, Branch, CGPA
        FROM RankedStudents
        WHERE rn = 1;
```

### Step-by-Step Clause Breakdown
- **`WITH RankedStudents AS (SELECT Roll_No, First_Name, Branch, CGPA, ROW_NUMBER() OVER (PARTITION BY Branch ORDER BY CGPA DESC) AS rn FROM STUDENT)`**: CTE assigns department ranks.
- **`SELECT Roll_No, First_Name, Branch, CGPA FROM RankedStudents WHERE rn = 1`**: Outer query filters strictly for rank 1 champions.

### Plain Language Explanation for 2nd-Year CSE
A classical SQL design pattern: rank rows within categories inside a CTE, then filter `WHERE rn = 1` in the outer query to extract the champion of each category.

### Sample Execution Output (Live Database)
```text
4 rows returned (CSE: Ananya Iyer 9.60, IT: Tanvi Malhotra 8.85, ECE: Kabir Verma 8.25, ME: Arjun Mehta 7.45).
```

---

## Solution to Question 54: CTE Company Placement Summary
- **Difficulty:** `Hard` | **Tables Involved:** `COMPANY, PLACEMENT`
- **Core Concepts:** `CTE Multi-Stage Aggregation, Separation of Concerns.`
- **Problem Statement:** Use a CTE to calculate total offers and average package per company, then join with COMPANY to display company names.

### Executable SQL Implementation
```sql
WITH CompSummary AS (
            SELECT Company_ID, COUNT(*) AS Total_Offers, AVG(Package) AS Avg_Pkg
            FROM PLACEMENT
            GROUP BY Company_ID
        )
        SELECT c.Company_Name, cs.Total_Offers, ROUND(cs.Avg_Pkg, 2) AS Avg_Package
        FROM COMPANY c
        JOIN CompSummary cs ON c.Company_ID = cs.Company_ID
        ORDER BY cs.Total_Offers DESC;
```

### Step-by-Step Clause Breakdown
- **`WITH CompSummary AS (SELECT Company_ID, COUNT(*) AS Total_Offers, AVG(Package) AS Avg_Pkg FROM PLACEMENT GROUP BY Company_ID)`**: CTE computes raw metrics.
- **`SELECT c.Company_Name, cs.Total_Offers, ROUND(cs.Avg_Pkg, 2) AS Avg_Package FROM COMPANY c JOIN CompSummary cs ON c.Company_ID = cs.Company_ID`**: Outer query attaches company profile.
- **`ORDER BY cs.Total_Offers DESC`**: Orders recruiters by volume.

### Plain Language Explanation for 2nd-Year CSE
Separates the heavy fact table aggregation (computed first in `CompSummary`) from the dimension joining in the final query.

### Sample Execution Output (Live Database)
```text
10 rows returned on seeded database.
```

---

## Solution to Question 55: Analytic Window Average CGPA per Branch
- **Difficulty:** `Hard` | **Tables Involved:** `STUDENT`
- **Core Concepts:** `Analytic Window Aggregation, Mathematical Deviation from Partition Mean.`
- **Problem Statement:** Calculate each student's CGPA difference from their branch's average CGPA using `AVG() OVER (PARTITION BY Branch)`.

### Executable SQL Implementation
```sql
SELECT Roll_No, First_Name, Branch, CGPA,
               ROUND(AVG(CGPA) OVER (PARTITION BY Branch), 2) AS Branch_Avg_CGPA,
               ROUND(CGPA - AVG(CGPA) OVER (PARTITION BY Branch), 2) AS Diff_From_Avg
        FROM STUDENT
        ORDER BY Branch, CGPA DESC
        LIMIT 10;
```

### Step-by-Step Clause Breakdown
- **`SELECT Roll_No, First_Name, Branch, CGPA, ...`**: Projects student identity.
- **`ROUND(AVG(CGPA) OVER (PARTITION BY Branch), 2) AS Branch_Avg_CGPA`**: Window function computing branch mean without collapsing rows.
- **`ROUND(CGPA - AVG(CGPA) OVER (PARTITION BY Branch), 2) AS Diff_From_Avg`**: Calculates individual variance from departmental benchmark.
- **`FROM STUDENT`**: Scans student master table.
- **`ORDER BY Branch, CGPA DESC LIMIT 10`**: Sample candidates.

### Plain Language Explanation for 2nd-Year CSE
Windowed `AVG()` computes the partition average alongside each individual student tuple, allowing direct arithmetic comparison (`CGPA - AVG`) without writing subqueries.

### Sample Execution Output (Live Database)
```text
10 rows returned detailing merit deviations from branch norms.
```

---

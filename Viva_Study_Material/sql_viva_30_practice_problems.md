# 30 SQL Practice Problems: Viva Preparation & Solution Manual

> [!TIP]
> **Active Learning Instructions**: Attempt the 30 problems in **Part 1 (Problem Statements)** independently before checking the verified solutions in **Part 2 (Solutions Manual)**. These questions mirror the exact problem styles professors ask during database project vivas.

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
- **Description:** Find the Roll_No and Name of all students who have listed "Python" or "Java" in their technical skills, ensuring no duplicate student rows appear in the output.

#### Problem 6: Total Students Enrolled Per Branch
- **Difficulty:** `Easy`
- **Tables Involved:** `STUDENT`
- **Description:** Display the total count of students enrolled in each engineering branch, ordered alphabetically by branch name.

#### Problem 7: Courses in Computer Science Department
- **Difficulty:** `Easy`
- **Tables Involved:** `COURSE`
- **Description:** List all courses offered by the "Computer Science" or "CSE" department along with their semester and credits, sorted by semester.

#### Problem 8: Students Without an Uploaded Resume Link
- **Difficulty:** `Easy`
- **Tables Involved:** `STUDENT`
- **Description:** Find the Roll_No, Full Name, and Branch of all students whose Resume_Link is NULL or empty.

#### Problem 9: Recruitment Drives Scheduled for 2024
- **Difficulty:** `Easy`
- **Tables Involved:** `RECRUITMENT_DRIVE, COMPANY`
- **Description:** List all recruitment drives scheduled for the year 2024 with company name, drive type, season, and drive date.

#### Problem 10: Pre-Placement Offers (PPO) Count
- **Difficulty:** `Easy`
- **Tables Involved:** `PLACEMENT`
- **Description:** Count how many total placement offers in the system were generated via Pre-Placement Offers (Is_PPO = "Yes").

### Medium Problems (Questions 11 to 20)
#### Problem 11: Branch-Wise Average and Maximum Package
- **Difficulty:** `Medium`
- **Tables Involved:** `STUDENT, PLACEMENT`
- **Description:** Calculate the average package (rounded to 2 decimals) and maximum package offered to each engineering branch, ordered by average package descending.

#### Problem 12: Students Who Received Multiple Placement Offers
- **Difficulty:** `Medium`
- **Tables Involved:** `STUDENT, PLACEMENT`
- **Description:** Find all students who have secured more than one placement offer. Display Student_ID, Roll_No, Full Name, and the number of offers secured.

#### Problem 13: Companies That Hired 3 or More Students
- **Difficulty:** `Medium`
- **Tables Involved:** `COMPANY, PLACEMENT`
- **Description:** Find all companies that have hired at least 3 students, showing the Company_Name, Industry, total students hired, and average package offered.

#### Problem 14: Unplaced Students using LEFT OUTER JOIN
- **Difficulty:** `Medium`
- **Tables Involved:** `STUDENT, PLACEMENT`
- **Description:** List all students who currently have no placement records in the system, displaying Roll_No, Name, Branch, and CGPA, ordered by CGPA descending.

#### Problem 15: Internship Duration in Days and Months
- **Difficulty:** `Medium`
- **Tables Involved:** `INTERNSHIP, STUDENT, COMPANY`
- **Description:** For all internships, display Student Roll Number, Company Name, Role, Start Date, End Date, Duration in Days (DATEDIFF), and Estimated Duration in Months.

#### Problem 16: Salary Package Bracket Segmentation
- **Difficulty:** `Medium`
- **Tables Involved:** `PLACEMENT`
- **Description:** Categorize placement offers into three compensation brackets: "Tier 3 (< 6 LPA)", "Tier 2 (6 - 12 LPA)", and "Tier 1 (> 12 LPA)", and display the total count of offers in each bracket.

#### Problem 17: Students Who Have Completed Both Mandatory Internships
- **Difficulty:** `Medium`
- **Tables Involved:** `STUDENT, INTERNSHIP`
- **Description:** Find all students who have completed both Mandatory Internship #1 and Mandatory Internship #2 using an aggregation and HAVING approach.

#### Problem 18: Students Without Any Registered Phone Number
- **Difficulty:** `Medium`
- **Tables Involved:** `STUDENT, STUDENT_PHONE`
- **Description:** Find all students who do not have any registered phone numbers in the STUDENT_PHONE table using NOT EXISTS.

#### Problem 19: Average SGPA per Semester across All Students
- **Difficulty:** `Medium`
- **Tables Involved:** `SEMESTER_RESULT`
- **Description:** Calculate the average SGPA across all students for each semester (Semester 1 through 8), showing the semester number and average SGPA rounded to 2 decimal places.

#### Problem 20: Companies Offering Both Placements and Internships
- **Difficulty:** `Medium`
- **Tables Involved:** `COMPANY, PLACEMENT, INTERNSHIP`
- **Description:** Find all companies that have participated in both campus placements AND student internships.

### Difficult Problems (Questions 21 to 30)
#### Problem 21: Second-Highest Package (Without LIMIT/OFFSET)
- **Difficulty:** `Difficult`
- **Tables Involved:** `PLACEMENT`
- **Description:** Find the second-highest salary package offered in the institution using a correlated subquery or MAX() approach rather than LIMIT/OFFSET.

#### Problem 22: Top Highest Paid Student per Branch using Window Functions
- **Difficulty:** `Difficult`
- **Tables Involved:** `STUDENT, PLACEMENT, COMPANY`
- **Description:** For every engineering branch, find the student who secured the highest placement package along with company name and salary.

#### Problem 23: Students Missing Mandatory Internships Audit
- **Difficulty:** `Difficult`
- **Tables Involved:** `STUDENT, INTERNSHIP`
- **Description:** Find all students who are missing either Mandatory Internship #1 or Mandatory Internship #2, indicating which specific internship is missing.

#### Problem 24: Branch Placement Percentage Calculation
- **Difficulty:** `Difficult`
- **Tables Involved:** `STUDENT, PLACEMENT`
- **Description:** Calculate the total students, placed students, and placement percentage for each engineering branch, ordered by placement percentage descending.

#### Problem 25: Company Recruiting the Maximum Number of Students
- **Difficulty:** `Difficult`
- **Tables Involved:** `COMPANY, PLACEMENT`
- **Description:** Find the single company that has recruited the largest number of students across all placement drives.

#### Problem 26: Students with CGPA Above Branch Average
- **Difficulty:** `Difficult`
- **Tables Involved:** `STUDENT`
- **Description:** Find all students whose CGPA is strictly greater than the average CGPA of their respective engineering branch.

#### Problem 27: Students Placed at the Same Company Where They Interned
- **Difficulty:** `Difficult`
- **Tables Involved:** `STUDENT, INTERNSHIP, PLACEMENT, COMPANY`
- **Description:** Find all students who secured a placement offer from the exact same company where they previously completed an internship.

#### Problem 28: Cumulative Running Total of Offers using Window Function
- **Difficulty:** `Difficult`
- **Tables Involved:** `PLACEMENT`
- **Description:** Display each placement year, total offers in that year, and the cumulative running total of placement offers up to that year.

#### Problem 29: Students Eligible for Mandatory Internship #1
- **Difficulty:** `Difficult`
- **Tables Involved:** `STUDENT, SEMESTER_RESULT`
- **Description:** Find all students eligible for Mandatory Internship #1 (Summer after 2nd year). Academic rules require: Batch year indicating 2nd year standing (e.g. Batch 2022/2023), CGPA >= 6.00, Backlogs = 0, and SGPA in Semester 3 >= 6.00.

#### Problem 30: Full Student 360-Degree Synthesis Profile
- **Difficulty:** `Difficult`
- **Tables Involved:** `STUDENT, STUDENT_SKILL, STUDENT_PHONE, PLACEMENT`
- **Description:** Write a comprehensive query that aggregates student demographics, total skills count, comma-separated list of skills, total phone numbers, and total placement offers secured for Student_ID = 1.

---

# Part 2: Step-by-Step Solutions Manual

### Solution 1: High CGPA Active Students (Easy)
**Question Requirement:** Find the Roll_No, Full Name (First + Last), Branch, and CGPA of all students who have a CGPA greater than or equal to 8.50 and have zero backlogs, sorted by CGPA in descending order.

```sql
SELECT Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Full_Name, Branch, CGPA
FROM STUDENT
WHERE CGPA >= 8.50 AND Backlogs = 0
ORDER BY CGPA DESC;
```

- **Tables Used:** `STUDENT`
- **Core SQL Concepts:** `WHERE, Comparison Operators, String Concatenation, ORDER BY DESC`
- **Step-by-Step Explanation:** Filters rows in the STUDENT table where both conditions (CGPA >= 8.50 and Backlogs = 0) are true using the AND logical operator. CONCAT_WS handles optional last names cleanly. ORDER BY sorts the highest CGPA first.

---

### Solution 2: Distinct Company Types and Counts (Easy)
**Question Requirement:** Find all distinct company types registered in the system along with the count of companies in each category, sorted by company count descending.

```sql
SELECT Company_Type, COUNT(*) AS Total_Companies
FROM COMPANY
GROUP BY Company_Type
ORDER BY Total_Companies DESC;
```

- **Tables Used:** `COMPANY`
- **Core SQL Concepts:** `GROUP BY, COUNT(*), ORDER BY DESC`
- **Step-by-Step Explanation:** Groups companies by their ENUM/category column Company_Type ("Product", "Service", "Startup", "Other") and counts the members in each group.

---

### Solution 3: High Package Placements in 2024 (Easy)
**Question Requirement:** Find all placement offers secured in the year 2024 where the package is at least 12.0 LPA. Display Placement_ID, Student_ID, Role, and Package, sorted by Package descending.

```sql
SELECT Placement_ID, Student_ID, Role, Package
FROM PLACEMENT
WHERE Placement_Year = 2024 AND Package >= 12.00
ORDER BY Package DESC;
```

- **Tables Used:** `PLACEMENT`
- **Core SQL Concepts:** `WHERE, Numeric Comparison, ORDER BY`
- **Step-by-Step Explanation:** Restricts records in PLACEMENT using a compound WHERE clause matching the calendar year 2024 and minimum package 12.00 LPA.

---

### Solution 4: Stipend Range Filter for Internships (Easy)
**Question Requirement:** Find all internships where the monthly stipend is between 15,000 and 40,000 (inclusive). Display Internship_ID, Student_ID, Role, and Stipend, ordered by Stipend ascending.

```sql
SELECT Internship_ID, Student_ID, Role, Stipend
FROM INTERNSHIP
WHERE Stipend BETWEEN 15000.00 AND 40000.00
ORDER BY Stipend ASC;
```

- **Tables Used:** `INTERNSHIP`
- **Core SQL Concepts:** `BETWEEN operator, ORDER BY ASC`
- **Step-by-Step Explanation:** The BETWEEN operator checks for inclusion within a closed range [15000, 40000].

---

### Solution 5: Students Possessing Python or Java Skills (Easy)
**Question Requirement:** Find the Roll_No and Name of all students who have listed "Python" or "Java" in their technical skills, ensuring no duplicate student rows appear in the output.

```sql
SELECT DISTINCT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name
FROM STUDENT s
JOIN STUDENT_SKILL sk ON s.Student_ID = sk.Student_ID
WHERE sk.Skill IN ('Python', 'Java')
ORDER BY s.Roll_No ASC;
```

- **Tables Used:** `STUDENT, STUDENT_SKILL`
- **Core SQL Concepts:** `INNER JOIN, IN operator, DISTINCT`
- **Step-by-Step Explanation:** Joins STUDENT with child table STUDENT_SKILL. Uses DISTINCT to prevent a student possessing both skills from appearing twice.

---

### Solution 6: Total Students Enrolled Per Branch (Easy)
**Question Requirement:** Display the total count of students enrolled in each engineering branch, ordered alphabetically by branch name.

```sql
SELECT Branch, COUNT(*) AS Student_Count
FROM STUDENT
GROUP BY Branch
ORDER BY Branch ASC;
```

- **Tables Used:** `STUDENT`
- **Core SQL Concepts:** `GROUP BY, COUNT(*), ORDER BY ASC`
- **Step-by-Step Explanation:** Aggregates students by their department name and outputs the size of each branch.

---

### Solution 7: Courses in Computer Science Department (Easy)
**Question Requirement:** List all courses offered by the "Computer Science" or "CSE" department along with their semester and credits, sorted by semester.

```sql
SELECT Course_ID, Course_Name, Semester, Credits, Course_Type
FROM COURSE
WHERE Department IN ('Computer Science', 'CSE')
ORDER BY Semester ASC, Course_Name ASC;
```

- **Tables Used:** `COURSE`
- **Core SQL Concepts:** `WHERE, IN operator, ORDER BY`
- **Step-by-Step Explanation:** Filters academic curriculum table COURSE by department name.

---

### Solution 8: Students Without an Uploaded Resume Link (Easy)
**Question Requirement:** Find the Roll_No, Full Name, and Branch of all students whose Resume_Link is NULL or empty.

```sql
SELECT Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Student_Name, Branch
FROM STUDENT
WHERE Resume_Link IS NULL OR TRIM(Resume_Link) = ''
ORDER BY Roll_No ASC;
```

- **Tables Used:** `STUDENT`
- **Core SQL Concepts:** `IS NULL, Boolean OR, String Length Check`
- **Step-by-Step Explanation:** Tests for missing optional attributes using both SQL IS NULL and empty string check.

---

### Solution 9: Recruitment Drives Scheduled for 2024 (Easy)
**Question Requirement:** List all recruitment drives scheduled for the year 2024 with company name, drive type, season, and drive date.

```sql
SELECT rd.Drive_ID, c.Company_Name, rd.Drive_Type, rd.Season, rd.Drive_Date
FROM RECRUITMENT_DRIVE rd
JOIN COMPANY c ON rd.Company_ID = c.Company_ID
WHERE rd.Drive_Year = 2024
ORDER BY rd.Drive_Date ASC;
```

- **Tables Used:** `RECRUITMENT_DRIVE, COMPANY`
- **Core SQL Concepts:** `INNER JOIN, WHERE, ORDER BY`
- **Step-by-Step Explanation:** Combines drive schedule with host company profile.

---

### Solution 10: Pre-Placement Offers (PPO) Count (Easy)
**Question Requirement:** Count how many total placement offers in the system were generated via Pre-Placement Offers (Is_PPO = "Yes").

```sql
SELECT COUNT(*) AS Total_PPOs
FROM PLACEMENT
WHERE Is_PPO = 'Yes';
```

- **Tables Used:** `PLACEMENT`
- **Core SQL Concepts:** `COUNT(*), WHERE`
- **Step-by-Step Explanation:** Counts rows in PLACEMENT matching the PPO flag.

---

### Solution 11: Branch-Wise Average and Maximum Package (Medium)
**Question Requirement:** Calculate the average package (rounded to 2 decimals) and maximum package offered to each engineering branch, ordered by average package descending.

```sql
SELECT s.Branch, COUNT(p.Placement_ID) AS Placements_Count, ROUND(AVG(p.Package), 2) AS Avg_Package, MAX(p.Package) AS Max_Package
FROM PLACEMENT p
JOIN STUDENT s ON p.Student_ID = s.Student_ID
GROUP BY s.Branch
ORDER BY Avg_Package DESC;
```

- **Tables Used:** `STUDENT, PLACEMENT`
- **Core SQL Concepts:** `INNER JOIN, GROUP BY, ROUND, AVG, MAX, ORDER BY DESC`
- **Step-by-Step Explanation:** Joins PLACEMENT with STUDENT on Student_ID, groups rows by s.Branch, and applies aggregate statistical functions.

---

### Solution 12: Students Who Received Multiple Placement Offers (Medium)
**Question Requirement:** Find all students who have secured more than one placement offer. Display Student_ID, Roll_No, Full Name, and the number of offers secured.

```sql
SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, COUNT(p.Placement_ID) AS Offer_Count
FROM STUDENT s
JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name
HAVING COUNT(p.Placement_ID) > 1
ORDER BY Offer_Count DESC;
```

- **Tables Used:** `STUDENT, PLACEMENT`
- **Core SQL Concepts:** `INNER JOIN, GROUP BY, HAVING, COUNT`
- **Step-by-Step Explanation:** Aggregates placement rows per student and filters groups using HAVING COUNT(...) > 1.

---

### Solution 13: Companies That Hired 3 or More Students (Medium)
**Question Requirement:** Find all companies that have hired at least 3 students, showing the Company_Name, Industry, total students hired, and average package offered.

```sql
SELECT c.Company_Name, c.Industry, COUNT(p.Placement_ID) AS Total_Hired, ROUND(AVG(p.Package), 2) AS Avg_Package
FROM COMPANY c
JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
GROUP BY c.Company_ID, c.Company_Name, c.Industry
HAVING COUNT(p.Placement_ID) >= 3
ORDER BY Total_Hired DESC;
```

- **Tables Used:** `COMPANY, PLACEMENT`
- **Core SQL Concepts:** `INNER JOIN, GROUP BY, HAVING, Aggregate Functions`
- **Step-by-Step Explanation:** Groups offers by company and filters for recruiters meeting the volume cutoff of 3.

---

### Solution 14: Unplaced Students using LEFT OUTER JOIN (Medium)
**Question Requirement:** List all students who currently have no placement records in the system, displaying Roll_No, Name, Branch, and CGPA, ordered by CGPA descending.

```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.CGPA
FROM STUDENT s
LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
WHERE p.Placement_ID IS NULL
ORDER BY s.CGPA DESC;
```

- **Tables Used:** `STUDENT, PLACEMENT`
- **Core SQL Concepts:** `LEFT OUTER JOIN, IS NULL (Anti-Join), ORDER BY DESC`
- **Step-by-Step Explanation:** Canonical SQL anti-join: LEFT JOIN keeps all students, and WHERE p.Placement_ID IS NULL eliminates those who matched an offer.

---

### Solution 15: Internship Duration in Days and Months (Medium)
**Question Requirement:** For all internships, display Student Roll Number, Company Name, Role, Start Date, End Date, Duration in Days (DATEDIFF), and Estimated Duration in Months.

```sql
SELECT s.Roll_No, c.Company_Name, i.Role, i.Start_Date, i.End_Date,
       DATEDIFF(i.End_Date, i.Start_Date) + 1 AS Duration_Days,
       ROUND((DATEDIFF(i.End_Date, i.Start_Date) + 1) / 30.0, 1) AS Duration_Months
FROM INTERNSHIP i
JOIN STUDENT s ON i.Student_ID = s.Student_ID
JOIN COMPANY c ON i.Company_ID = c.Company_ID
ORDER BY Duration_Days DESC;
```

- **Tables Used:** `INTERNSHIP, STUDENT, COMPANY`
- **Core SQL Concepts:** `3-Table JOIN, DATEDIFF, ROUND, Date Arithmetic`
- **Step-by-Step Explanation:** Computes derived duration attributes on the fly using DATEDIFF + 1 to account for inclusive start and end dates.

---

### Solution 16: Salary Package Bracket Segmentation (Medium)
**Question Requirement:** Categorize placement offers into three compensation brackets: "Tier 3 (< 6 LPA)", "Tier 2 (6 - 12 LPA)", and "Tier 1 (> 12 LPA)", and display the total count of offers in each bracket.

```sql
SELECT 
    CASE 
        WHEN Package < 6.00 THEN 'Tier 3 (< 6 LPA)'
        WHEN Package BETWEEN 6.00 AND 12.00 THEN 'Tier 2 (6 - 12 LPA)'
        ELSE 'Tier 1 (> 12 LPA)'
    END AS Salary_Tier,
    COUNT(*) AS Offer_Count
FROM PLACEMENT
GROUP BY Salary_Tier
ORDER BY MIN(Package) ASC;
```

- **Tables Used:** `PLACEMENT`
- **Core SQL Concepts:** `CASE WHEN, GROUP BY, Derived Categorization`
- **Step-by-Step Explanation:** Uses CASE WHEN in SELECT and GROUP BY to partition continuous package values into discrete reporting tiers.

---

### Solution 17: Students Who Have Completed Both Mandatory Internships (Medium)
**Question Requirement:** Find all students who have completed both Mandatory Internship #1 and Mandatory Internship #2 using an aggregation and HAVING approach.

```sql
SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch
FROM STUDENT s
JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
WHERE i.Internship_Type = 'Mandatory' AND i.Internship_No IN (1, 2)
GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch
HAVING COUNT(DISTINCT i.Internship_No) = 2;
```

- **Tables Used:** `STUDENT, INTERNSHIP`
- **Core SQL Concepts:** `INNER JOIN, GROUP BY, HAVING, COUNT(DISTINCT)`
- **Step-by-Step Explanation:** Filters for mandatory internships 1 and 2, groups by student, and asserts that exactly 2 distinct internship numbers are present.

---

### Solution 18: Students Without Any Registered Phone Number (Medium)
**Question Requirement:** Find all students who do not have any registered phone numbers in the STUDENT_PHONE table using NOT EXISTS.

```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Email
FROM STUDENT s
WHERE NOT EXISTS (
    SELECT 1 FROM STUDENT_PHONE sp WHERE sp.Student_ID = s.Student_ID
);
```

- **Tables Used:** `STUDENT, STUDENT_PHONE`
- **Core SQL Concepts:** `NOT EXISTS, Correlated Subquery`
- **Step-by-Step Explanation:** Correlated subquery evaluates if any phone tuple exists for each student row; NOT EXISTS returns TRUE only for students with none.

---

### Solution 19: Average SGPA per Semester across All Students (Medium)
**Question Requirement:** Calculate the average SGPA across all students for each semester (Semester 1 through 8), showing the semester number and average SGPA rounded to 2 decimal places.

```sql
SELECT Semester, COUNT(*) AS Total_Records, ROUND(AVG(SGPA), 2) AS Average_SGPA
FROM SEMESTER_RESULT
GROUP BY Semester
ORDER BY Semester ASC;
```

- **Tables Used:** `SEMESTER_RESULT`
- **Core SQL Concepts:** `GROUP BY, AVG, ROUND, ORDER BY ASC`
- **Step-by-Step Explanation:** Computes cohort-level academic benchmark SGPA per semester.

---

### Solution 20: Companies Offering Both Placements and Internships (Medium)
**Question Requirement:** Find all companies that have participated in both campus placements AND student internships.

```sql
SELECT c.Company_ID, c.Company_Name, c.Industry
FROM COMPANY c
WHERE EXISTS (SELECT 1 FROM PLACEMENT p WHERE p.Company_ID = c.Company_ID)
  AND EXISTS (SELECT 1 FROM INTERNSHIP i WHERE i.Company_ID = c.Company_ID)
ORDER BY c.Company_Name ASC;
```

- **Tables Used:** `COMPANY, PLACEMENT, INTERNSHIP`
- **Core SQL Concepts:** `EXISTS, Correlated Subqueries, Set Intersection`
- **Step-by-Step Explanation:** Uses dual EXISTS clauses to verify corporate participation in both programs without cartesian joins.

---

### Solution 21: Second-Highest Package (Without LIMIT/OFFSET) (Difficult)
**Question Requirement:** Find the second-highest salary package offered in the institution using a correlated subquery or MAX() approach rather than LIMIT/OFFSET.

```sql
SELECT MAX(Package) AS Second_Highest_Package
FROM PLACEMENT
WHERE Package < (SELECT MAX(Package) FROM PLACEMENT);
```

- **Tables Used:** `PLACEMENT`
- **Core SQL Concepts:** `Subquery, MAX(), Scalar Comparison`
- **Step-by-Step Explanation:** Inner query finds the absolute highest package. The outer query finds the maximum package that is strictly less than that absolute maximum, yielding the exact second-highest.

---

### Solution 22: Top Highest Paid Student per Branch using Window Functions (Difficult)
**Question Requirement:** For every engineering branch, find the student who secured the highest placement package along with company name and salary.

```sql
WITH RankedOffers AS (
    SELECT s.Branch, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
           c.Company_Name, p.Package,
           ROW_NUMBER() OVER (PARTITION BY s.Branch ORDER BY p.Package DESC) AS Rank_In_Branch
    FROM PLACEMENT p
    JOIN STUDENT s ON p.Student_ID = s.Student_ID
    JOIN COMPANY c ON p.Company_ID = c.Company_ID
)
SELECT Branch, Roll_No, Student_Name, Company_Name, Package
FROM RankedOffers
WHERE Rank_In_Branch = 1
ORDER BY Package DESC;
```

- **Tables Used:** `STUDENT, PLACEMENT, COMPANY`
- **Core SQL Concepts:** `Common Table Expressions (WITH), Window Function (DENSE_RANK / ROW_NUMBER), PARTITION BY`
- **Step-by-Step Explanation:** PARTITION BY s.Branch resets the ranking for each department; ORDER BY p.Package DESC ranks offers highest first. Outer query filters for Rank_In_Branch = 1.

---

### Solution 23: Students Missing Mandatory Internships Audit (Difficult)
**Question Requirement:** Find all students who are missing either Mandatory Internship #1 or Mandatory Internship #2, indicating which specific internship is missing.

```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.Batch_Year,
       CASE WHEN NOT EXISTS (SELECT 1 FROM INTERNSHIP i WHERE i.Student_ID = s.Student_ID AND i.Internship_No = 1 AND i.Internship_Type = 'Mandatory') THEN 'Missing' ELSE 'Completed' END AS Mandatory_1,
       CASE WHEN NOT EXISTS (SELECT 1 FROM INTERNSHIP i WHERE i.Student_ID = s.Student_ID AND i.Internship_No = 2 AND i.Internship_Type = 'Mandatory') THEN 'Missing' ELSE 'Completed' END AS Mandatory_2
FROM STUDENT s
WHERE NOT EXISTS (SELECT 1 FROM INTERNSHIP i WHERE i.Student_ID = s.Student_ID AND i.Internship_No = 1 AND i.Internship_Type = 'Mandatory')
   OR NOT EXISTS (SELECT 1 FROM INTERNSHIP i WHERE i.Student_ID = s.Student_ID AND i.Internship_No = 2 AND i.Internship_Type = 'Mandatory')
ORDER BY s.Batch_Year ASC, s.Branch ASC, s.Roll_No ASC;
```

- **Tables Used:** `STUDENT, INTERNSHIP`
- **Core SQL Concepts:** `NOT EXISTS, Correlated Subqueries, CASE WHEN, Disjunctive OR`
- **Step-by-Step Explanation:** The WHERE clause restricts output to students missing at least one mandatory requirement. The SELECT clause uses CASE WHEN with correlated NOT EXISTS to evaluate each requirement individually.

---

### Solution 24: Branch Placement Percentage Calculation (Difficult)
**Question Requirement:** Calculate the total students, placed students, and placement percentage for each engineering branch, ordered by placement percentage descending.

```sql
SELECT s.Branch,
       COUNT(DISTINCT s.Student_ID) AS Total_Students,
       COUNT(DISTINCT p.Student_ID) AS Placed_Students,
       ROUND(COUNT(DISTINCT p.Student_ID) * 100.0 / COUNT(DISTINCT s.Student_ID), 2) AS Placement_Percentage
FROM STUDENT s
LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
GROUP BY s.Branch
ORDER BY Placement_Percentage DESC;
```

- **Tables Used:** `STUDENT, PLACEMENT`
- **Core SQL Concepts:** `LEFT OUTER JOIN, COUNT(DISTINCT), Arithmetic in SQL, ROUND`
- **Step-by-Step Explanation:** Uses LEFT JOIN to ensure all students are counted in the denominator. Multiplies by 100.0 (float) before dividing to avoid integer division truncation.

---

### Solution 25: Company Recruiting the Maximum Number of Students (Difficult)
**Question Requirement:** Find the single company that has recruited the largest number of students across all placement drives.

```sql
SELECT c.Company_ID, c.Company_Name, c.Industry, COUNT(p.Placement_ID) AS Total_Recruited
FROM COMPANY c
JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
GROUP BY c.Company_ID, c.Company_Name, c.Industry
ORDER BY Total_Recruited DESC
LIMIT 1;
```

- **Tables Used:** `COMPANY, PLACEMENT`
- **Core SQL Concepts:** `INNER JOIN, GROUP BY, COUNT, ORDER BY DESC, LIMIT 1`
- **Step-by-Step Explanation:** Aggregates offers per company, orders by recruitment volume descending, and uses LIMIT 1 to isolate the top recruiter.

---

### Solution 26: Students with CGPA Above Branch Average (Difficult)
**Question Requirement:** Find all students whose CGPA is strictly greater than the average CGPA of their respective engineering branch.

```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.CGPA
FROM STUDENT s
WHERE s.CGPA > (
    SELECT AVG(s2.CGPA)
    FROM STUDENT s2
    WHERE s2.Branch = s.Branch
)
ORDER BY s.Branch ASC, s.CGPA DESC;
```

- **Tables Used:** `STUDENT`
- **Core SQL Concepts:** `Correlated Subquery, Branch-Level Average Comparison`
- **Step-by-Step Explanation:** The inner query computes the average CGPA for the specific branch of candidate s. The outer query compares candidate s.CGPA against this dynamic branch threshold.

---

### Solution 27: Students Placed at the Same Company Where They Interned (Difficult)
**Question Requirement:** Find all students who secured a placement offer from the exact same company where they previously completed an internship.

```sql
SELECT DISTINCT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       c.Company_Name, i.Role AS Intern_Role, p.Role AS Placed_Role, p.Package
FROM STUDENT s
JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
JOIN PLACEMENT p ON s.Student_ID = p.Student_ID AND i.Company_ID = p.Company_ID
JOIN COMPANY c ON i.Company_ID = c.Company_ID
ORDER BY p.Package DESC;
```

- **Tables Used:** `STUDENT, INTERNSHIP, PLACEMENT, COMPANY`
- **Core SQL Concepts:** `4-Table Equi-Join, Multi-Entity Association on Same Foreign Key`
- **Step-by-Step Explanation:** Joins both INTERNSHIP and PLACEMENT to STUDENT, and critically asserts i.Company_ID = p.Company_ID to match the employer.

---

### Solution 28: Cumulative Running Total of Offers using Window Function (Difficult)
**Question Requirement:** Display each placement year, total offers in that year, and the cumulative running total of placement offers up to that year.

```sql
WITH YearlyOffers AS (
    SELECT Placement_Year, COUNT(*) AS Offers_In_Year
    FROM PLACEMENT
    GROUP BY Placement_Year
)
SELECT Placement_Year, Offers_In_Year,
       SUM(Offers_In_Year) OVER (ORDER BY Placement_Year ASC) AS Running_Total_Offers
FROM YearlyOffers
ORDER BY Placement_Year ASC;
```

- **Tables Used:** `PLACEMENT`
- **Core SQL Concepts:** `GROUP BY, Window Function, SUM() OVER (ORDER BY ...)`
- **Step-by-Step Explanation:** Aggregates yearly counts inside a CTE, then computes a running cumulative sum using SUM(Offers_In_Year) OVER (ORDER BY Placement_Year ASC).

---

### Solution 29: Students Eligible for Mandatory Internship #1 (Difficult)
**Question Requirement:** Find all students eligible for Mandatory Internship #1 (Summer after 2nd year). Academic rules require: Batch year indicating 2nd year standing (e.g. Batch 2022/2023), CGPA >= 6.00, Backlogs = 0, and SGPA in Semester 3 >= 6.00.

```sql
SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.CGPA, s.Backlogs
FROM STUDENT s
WHERE s.CGPA >= 6.00 
  AND s.Backlogs = 0
  AND EXISTS (
      SELECT 1 FROM SEMESTER_RESULT sr
      WHERE sr.Student_ID = s.Student_ID AND sr.Semester = 3 AND sr.SGPA >= 6.00
  )
  AND NOT EXISTS (
      SELECT 1 FROM INTERNSHIP i
      WHERE i.Student_ID = s.Student_ID AND i.Internship_No = 1 AND i.Internship_Type = 'Mandatory'
  )
ORDER BY s.CGPA DESC;
```

- **Tables Used:** `STUDENT, SEMESTER_RESULT`
- **Core SQL Concepts:** `Subquery, Academic Eligibility Verification, Multiple Prerequisite Criteria`
- **Step-by-Step Explanation:** Enforces all institutional eligibility rules: minimum cumulative CGPA, zero current active backlogs, prerequisite Semester 3 SGPA verification via EXISTS, and ensures the student has not already completed the requirement.

---

### Solution 30: Full Student 360-Degree Synthesis Profile (Difficult)
**Question Requirement:** Write a comprehensive query that aggregates student demographics, total skills count, comma-separated list of skills, total phone numbers, and total placement offers secured for Student_ID = 1.

```sql
SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       s.Branch, s.Batch_Year, s.CGPA,
       COUNT(DISTINCT sp.Phone_No) AS Total_Phones,
       COUNT(DISTINCT sk.Skill) AS Total_Skills,
       GROUP_CONCAT(DISTINCT sk.Skill ORDER BY sk.Skill SEPARATOR ', ') AS Skills_List,
       COUNT(DISTINCT p.Placement_ID) AS Total_Offers
FROM STUDENT s
LEFT JOIN STUDENT_PHONE sp ON s.Student_ID = sp.Student_ID
LEFT JOIN STUDENT_SKILL sk ON s.Student_ID = sk.Student_ID
LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
WHERE s.Student_ID = 1
GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, s.Batch_Year, s.CGPA;
```

- **Tables Used:** `STUDENT, STUDENT_SKILL, STUDENT_PHONE, PLACEMENT`
- **Core SQL Concepts:** `Multiple LEFT JOINs, GROUP_CONCAT, COUNT(DISTINCT), Grouping`
- **Step-by-Step Explanation:** Master relational consolidation combining 3 separate one-to-many child relationships without cross-product distortion using DISTINCT inside aggregate functions.

---

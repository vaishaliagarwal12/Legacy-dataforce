# NEW SQL QUERY GENERATION PRACTICE FOR PROJECT EVALUATION

> [!IMPORTANT]
> **Practical Viva & Query Writing Preparation**: In your evaluation, the professor will present dynamic problem statements and ask you to write new SQL queries on the spot. This document trains you to translate problem statements into executable, optimized SQL queries using the **exact 20-table schema** of Legacy Dataforce.

## Project Relational Schema Overview (Exact Names & Keys)

Every query in this guide strictly uses the actual tables and columns in `placement_db`:

```
1. STUDENT               (Student_ID [PK], Roll_No, First_Name, Last_Name, Branch, Batch_Year, Section, CGPA, Backlogs, Email, Resume_Link)
2. STUDENT_PHONE         (Student_ID [PK, FK], Phone_No [PK])
3. STUDENT_SKILL         (Student_ID [PK, FK], Skill [PK])
4. COMPANY               (Company_ID [PK], Company_Name, Company_Type, Industry, Location, Website)
5. PLACEMENT             (Placement_ID [PK], Student_ID [FK], Company_ID [FK], Opportunity_ID [FK], Role, Package, Placement_Year, Placement_Type, Is_PPO, Joined, Offer_Status, Interview_Rounds)
6. PLACEMENT_SKILL       (Placement_ID [PK, FK], Skill [PK])
7. INTERNSHIP            (Internship_ID [PK], Student_ID [FK], Company_ID [FK], Opportunity_ID [FK], Requirement_ID [FK], Internship_No, Internship_Type, Role, Interview_Rounds, Stipend, Start_Date, End_Date, Credits, Report_Semester, Report_Link, Report_Grade, Certificate_Link)
8. INTERNSHIP_REQUIREMENT(Requirement_ID [PK], Internship_No, Mandatory, Prescribed_Period, Required_Result_Semester, Report_Submission_Semester, Credits, Description)
9. COURSE                (Course_ID [PK], University_ID [FK], Course_Name, Department, Semester, Credits, Course_Type)
10. STUDENT_COURSE       (Student_ID [PK, FK], Course_ID [PK, FK], Enrollment_Year, Grade)
11. SEMESTER_RESULT      (Result_ID [PK], Student_ID [FK], Semester, SGPA, Year, Total_Credits)
12. RECRUITMENT_DRIVE    (Drive_ID [PK], Company_ID [FK], Drive_Year, Drive_Type, Season, Drive_Date)
13. OPPORTUNITY          (Opportunity_ID [PK], Drive_ID [FK], Role, Opportunity_Type, Package_Stipend, Duration_Months)
14. ELIGIBILITY          (Eligibility_ID [PK], Opportunity_ID [FK], Minimum_CGPA, Eligible_Branch, Max_Backlogs, Other_Criteria)
15. ELIGIBILITY_BRANCH   (Eligibility_ID [PK, FK], Branch [PK])
16. SELECTION_PROCESS    (Round_ID [PK], Opportunity_ID [FK], Round_Number, Round_Type, Description)
17. STUDENT_PROFILE      (Profile_ID [PK], Student_ID [FK], Profile_Type, Title, Description, Link, Year, Proficiency_Level)
18. RESUME               (Resume_ID [PK], Student_ID [FK], File_Name, File_Link, Upload_Date, Resume_Year)
19. EDUCATION_DOCUMENT   (Doc_ID [PK], Resume_ID [FK], Document_Type, Percentage_CGPA, Board, Year_of_Passing, File_Link)
20. UNIVERSITY           (University_ID [PK], University_Name, Location, Established_Year)
```

---

## Study Structure
- **Part 1: Question Bank (55 Unsolved Problems)** — Attempt writing the SQL on paper or in your SQL editor first.
  - [Easy Problems (Questions 1 to 18)](#easy-problems-questions-1-to-18)
  - [Medium Problems (Questions 19 to 38)](#medium-problems-questions-19-to-38)
  - [Difficult Problems (Questions 39 to 55)](#difficult-problems-questions-39-to-55)
- **Part 2: Comprehensive Solutions Manual & Walkthrough (Solutions 1 to 55)** — Check the exact query, line-by-line explanation, relational rationale, and sample output format.

---

# Part 1: Question Bank (55 Unsolved Problems)

### Easy Problems (Questions 1 to 18)

#### Question 1: Number of Students in Each Graduating Batch
- **Project Area:** `Branch and Batch` | **Difficulty:** `Easy`
- **Tables Needed:** `STUDENT`
- **Problem Statement:** Find the total count of registered students in each graduating batch year, sorted chronologically by Batch_Year.

#### Question 2: Students with High Academic Standing and Zero Backlogs
- **Project Area:** `Student Information` | **Difficulty:** `Easy`
- **Tables Needed:** `STUDENT`
- **Problem Statement:** Retrieve the Roll_No, Full Name, Branch, and CGPA of all students who have achieved a CGPA of 8.00 or higher with zero backlogs, ordered by CGPA descending.

#### Question 3: Product-Based Companies Located in Bangalore
- **Project Area:** `Company Information` | **Difficulty:** `Easy`
- **Tables Needed:** `COMPANY`
- **Problem Statement:** Find the Company_Name, Industry, and Website of all companies categorized as 'Product' located in 'Bangalore' or 'Bengaluru'.

#### Question 4: On-Campus Placements in 2024 with Packages Exceeding 10 LPA
- **Project Area:** `Placement Records` | **Difficulty:** `Easy`
- **Tables Needed:** `PLACEMENT`
- **Problem Statement:** List the Placement_ID, Student_ID, Role, and Package for all on-campus placements secured in 2024 offering a package of 10.00 LPA or higher.

#### Question 5: Mandatory Internships with Non-Zero Monthly Stipends
- **Project Area:** `Internship Records` | **Difficulty:** `Easy`
- **Tables Needed:** `INTERNSHIP`
- **Problem Statement:** Find all mandatory internships where the monthly stipend is greater than 0. Display Student_ID, Role, Stipend, and Duration in Days.

#### Question 6: Semester 5 Examination Results with SGPA >= 7.50
- **Project Area:** `Academic Records and SGPA` | **Difficulty:** `Easy`
- **Tables Needed:** `SEMESTER_RESULT`
- **Problem Statement:** Find all students who scored an SGPA of 7.50 or higher in Semester 5 examinations, showing Student_ID, SGPA, and Total_Credits, sorted by SGPA descending.

#### Question 7: Distinct Courses Offered in Even Semesters
- **Project Area:** `Course Enrollment` | **Difficulty:** `Easy`
- **Tables Needed:** `COURSE`
- **Problem Statement:** List all distinct courses offered in even semesters (Semesters 2, 4, 6, 8) with their Course_Name, Department, Semester, and Credits.

#### Question 8: Students Registered with Multiple Phone Numbers
- **Project Area:** `Student Information` | **Difficulty:** `Easy`
- **Tables Needed:** `STUDENT_PHONE`
- **Problem Statement:** Find the Student_ID and the count of registered phone numbers for all students who have registered more than 1 contact number in STUDENT_PHONE.

#### Question 9: Highest and Lowest Packages Offered by Service-Based Companies
- **Project Area:** `Salary and Package Analysis` | **Difficulty:** `Easy`
- **Tables Needed:** `PLACEMENT, COMPANY`
- **Problem Statement:** Find the highest, lowest, and average placement packages offered specifically by 'Service' type companies.

#### Question 10: Count of Students Enrolled in Each Course in 2024
- **Project Area:** `Course Enrollment` | **Difficulty:** `Easy`
- **Tables Needed:** `STUDENT_COURSE`
- **Problem Statement:** Find the total number of students enrolled in each course during the academic year 2024, displaying Course_ID and student count.

#### Question 11: Companies Hosting Recruitment Drives in the Fall Season
- **Project Area:** `Company Information` | **Difficulty:** `Easy`
- **Tables Needed:** `COMPANY, RECRUITMENT_DRIVE`
- **Problem Statement:** Find the distinct names of companies that conducted campus recruitment drives during the 'Fall' season.

#### Question 12: Count of Internships Evaluated per Academic Semester
- **Project Area:** `Internship Records` | **Difficulty:** `Easy`
- **Tables Needed:** `INTERNSHIP`
- **Problem Statement:** Find the total number of internships submitted for academic credit evaluation in each Report_Semester.

#### Question 13: Students Who Have Formally Accepted/Joined Their Offer
- **Project Area:** `Placement Records` | **Difficulty:** `Easy`
- **Tables Needed:** `PLACEMENT`
- **Problem Statement:** Retrieve the Student_ID, Role, Package, and Company_ID for all placement offers where Joined = 'Yes' or Offer_Status = 'Joined'.

#### Question 14: Students Registered in Section 'A' with Email Addresses
- **Project Area:** `Student Information` | **Difficulty:** `Easy`
- **Tables Needed:** `STUDENT`
- **Problem Statement:** Find the Roll_No, Full Name, and Email of all students belonging to Section 'A', ordered alphabetically by First_Name.

#### Question 15: Total Placements Categorized by Placement Type
- **Project Area:** `Placement Records` | **Difficulty:** `Easy`
- **Tables Needed:** `PLACEMENT`
- **Problem Statement:** Find the total number of placement offers categorized by Placement_Type ('On-campus' vs 'Off-campus') along with the average package in each category.

#### Question 16: Students with Perfect 10.00 SGPA in Any Semester
- **Project Area:** `Academic Records and SGPA` | **Difficulty:** `Easy`
- **Tables Needed:** `SEMESTER_RESULT`
- **Problem Statement:** Find all records where a student attained an SGPA of 10.00. Display Student_ID, Semester, Year, and Total_Credits.

#### Question 17: Total Internships Completed per Internship Number
- **Project Area:** `Internship Records` | **Difficulty:** `Easy`
- **Tables Needed:** `INTERNSHIP`
- **Problem Statement:** Count how many internships were completed as Internship_No = 1 (2nd yr summer), Internship_No = 2 (3rd yr summer), and additional internships (No >= 3).

#### Question 18: Companies in the Financial and FinTech Industries
- **Project Area:** `Company Information` | **Difficulty:** `Easy`
- **Tables Needed:** `COMPANY`
- **Problem Statement:** Find all companies whose Industry contains 'FinTech', 'Finance', or 'Banking' using the LIKE pattern matching operator.

### Medium Problems (Questions 19 to 38)

#### Question 19: Average Package Branch-Wise
- **Project Area:** `Salary and Package Analysis` | **Difficulty:** `Medium`
- **Tables Needed:** `STUDENT, PLACEMENT`
- **Problem Statement:** Calculate the average placement package (rounded to 2 decimal places), total offers, and highest package secured by each engineering branch.

#### Question 20: Students Who Received Multiple Placement Offers
- **Project Area:** `Placement Records` | **Difficulty:** `Medium`
- **Tables Needed:** `STUDENT, PLACEMENT`
- **Problem Statement:** Find all students who have received 2 or more placement offers. Display Student_ID, Roll_No, Full Name, Branch, and total offers received.

#### Question 21: Companies That Recruited the Maximum Number of Students
- **Project Area:** `Company Information` | **Difficulty:** `Medium`
- **Tables Needed:** `COMPANY, PLACEMENT`
- **Problem Statement:** Find the companies that have hired the largest number of students, showing Company_Name, Company_Type, Industry, and total hires.

#### Question 22: Students Who Have Not Completed Mandatory Internships
- **Project Area:** `Mandatory Internship Completion` | **Difficulty:** `Medium`
- **Tables Needed:** `STUDENT, INTERNSHIP`
- **Problem Statement:** Find all active students who have NOT completed either Mandatory Internship #1 (after 2nd yr) OR Mandatory Internship #2 (after 3rd yr).

#### Question 23: Second-Highest Package (Using Subquery)
- **Project Area:** `Salary and Package Analysis` | **Difficulty:** `Medium`
- **Tables Needed:** `PLACEMENT`
- **Problem Statement:** Find the second-highest placement package offered in the institution using a nested subquery with MAX() rather than LIMIT/OFFSET.

#### Question 24: Students Eligible for Mandatory Internship #1 (Existing Academic Rules)
- **Project Area:** `Internship Eligibility` | **Difficulty:** `Medium`
- **Tables Needed:** `STUDENT, SEMESTER_RESULT, INTERNSHIP`
- **Problem Statement:** Identify all students eligible for Mandatory Internship #1 (Summer after 2nd yr). Institutional rules require: Batch indicating 2nd year standing, CGPA >= 6.00, Backlogs = 0, Semester 3 SGPA >= 6.00, and not already completed.

#### Question 25: Students Eligible for Mandatory Internship #2 (Existing Academic Rules)
- **Project Area:** `Internship Eligibility` | **Difficulty:** `Medium`
- **Tables Needed:** `STUDENT, SEMESTER_RESULT, INTERNSHIP`
- **Problem Statement:** Identify all students eligible for Mandatory Internship #2 (Summer after 3rd yr). Institutional rules require: Completed Mandatory Internship #1, CGPA >= 6.50, Backlogs = 0, and Semester 5 SGPA >= 6.50.

#### Question 26: CGPA Calculation from All Completed Semester Results
- **Project Area:** `Academic Records and SGPA` | **Difficulty:** `Medium`
- **Tables Needed:** `STUDENT, SEMESTER_RESULT`
- **Problem Statement:** Calculate the cumulative average SGPA across all semesters for each student and compare it with the stored CGPA in the STUDENT table.

#### Question 27: Recruiters Who Have Offered Both PPOs and Regular Placements
- **Project Area:** `Company Information` | **Difficulty:** `Medium`
- **Tables Needed:** `COMPANY, PLACEMENT`
- **Problem Statement:** Find all companies that have hired students through both Pre-Placement Offers (Is_PPO = 'Yes') AND standard on-campus offers (Is_PPO = 'No').

#### Question 28: Average Internship Stipend Across Host Companies
- **Project Area:** `Internship Records` | **Difficulty:** `Medium`
- **Tables Needed:** `COMPANY, INTERNSHIP`
- **Problem Statement:** Calculate the total internships hosted and the average monthly stipend provided by each corporate partner (excluding unpaid internships).

#### Question 29: Courses with the Highest Student Enrollment
- **Project Area:** `Course Enrollment` | **Difficulty:** `Medium`
- **Tables Needed:** `COURSE, STUDENT_COURSE`
- **Problem Statement:** Find the top 5 most enrolled courses in the university curriculum across all years, displaying Course_Name, Department, Semester, and total enrolled students.

#### Question 30: Students Possessing Both Python and SQL Skills
- **Project Area:** `Student Information` | **Difficulty:** `Medium`
- **Tables Needed:** `STUDENT, STUDENT_SKILL`
- **Problem Statement:** Find the Roll_No and Full Name of all students who possess BOTH 'Python' AND 'SQL' technical skills.

#### Question 31: Unplaced Students Prioritized by Academic Merit
- **Project Area:** `Placement Records` | **Difficulty:** `Medium`
- **Tables Needed:** `STUDENT, PLACEMENT`
- **Problem Statement:** Generate a prioritized outreach list of unplaced students for the placement cell, displaying Roll_No, Full Name, Branch, CGPA, and Email, sorted with highest CGPA first.

#### Question 32: Package Distribution Across Graduating Batches
- **Project Area:** `Salary and Package Analysis` | **Difficulty:** `Medium`
- **Tables Needed:** `STUDENT, PLACEMENT`
- **Problem Statement:** Calculate the average, highest, and median-approximating salary package offered to each graduating batch year.

#### Question 33: Students with Long-Term Internships (> 3 Months)
- **Project Area:** `Internship Records` | **Difficulty:** `Medium`
- **Tables Needed:** `INTERNSHIP, STUDENT, COMPANY`
- **Problem Statement:** Find all internships where the calculated duration is strictly greater than 3.0 months. Display Roll_No, Student Name, Company Name, Role, and Duration in Months.

#### Question 34: Total Academic Credits Earned by Students
- **Project Area:** `Academic Records and SGPA` | **Difficulty:** `Medium`
- **Tables Needed:** `STUDENT, SEMESTER_RESULT`
- **Problem Statement:** Calculate the total academic credits earned by each student across all completed semesters in SEMESTER_RESULT, displaying Roll_No, Full Name, and Total Credits Earned.

#### Question 35: Count of Selection Rounds Scheduled per Opportunity
- **Project Area:** `Company Information` | **Difficulty:** `Medium`
- **Tables Needed:** `COMPANY, RECRUITMENT_DRIVE, OPPORTUNITY, SELECTION_PROCESS`
- **Problem Statement:** Find the number of selection rounds (aptitude, technical, HR) scheduled for each hiring opportunity, displaying Company_Name, Role, and Total Rounds.

#### Question 36: Students with Placement Package Higher Than Overall College Average
- **Project Area:** `Placement Records` | **Difficulty:** `Medium`
- **Tables Needed:** `STUDENT, PLACEMENT`
- **Problem Statement:** Find all students who secured a placement package strictly greater than the overall college average package.

#### Question 37: Course Grade Distribution ('A' Grades Achieved)
- **Project Area:** `Course Enrollment` | **Difficulty:** `Medium`
- **Tables Needed:** `COURSE, STUDENT_COURSE`
- **Problem Statement:** Count how many students earned an 'A' or 'A+' grade in each academic course, displaying Course_Name, Department, and count of 'A' grades.

#### Question 38: Placement Conversion Percentage by Batch Year
- **Project Area:** `Branch and Batch` | **Difficulty:** `Medium`
- **Tables Needed:** `STUDENT, PLACEMENT`
- **Problem Statement:** Calculate the total student count, placed student count, and placement percentage for each graduating batch year.

### Difficult Problems (Questions 39 to 55)

#### Question 39: Top 3 Highest Placement Packages Within Each Engineering Branch
- **Project Area:** `Salary and Package Analysis` | **Difficulty:** `Difficult`
- **Tables Needed:** `STUDENT, PLACEMENT, COMPANY`
- **Problem Statement:** Find the top 3 highest placement packages within every engineering branch using the DENSE_RANK() window function.

#### Question 40: Departmental Internship Compliance Matrix (Fully vs Partially vs Non-Compliant)
- **Project Area:** `Mandatory Internship Completion` | **Difficulty:** `Difficult`
- **Tables Needed:** `STUDENT, INTERNSHIP`
- **Problem Statement:** For each engineering branch, calculate the total students and break down the count of Fully Compliant students (Both 1 & 2), Partially Compliant (Only 1 or 2), and Non-Compliant (Neither).

#### Question 41: Nth-Highest Package Generic Formulation (3rd Highest Package)
- **Project Area:** `Salary and Package Analysis` | **Difficulty:** `Difficult`
- **Tables Needed:** `PLACEMENT`
- **Problem Statement:** Find the 3rd-highest package offered across the college using a correlated subquery that counts distinct higher packages, avoiding LIMIT/OFFSET.

#### Question 42: Students Placed in the Same Company Where They Did an Internship (PPO Conversion Analysis)
- **Project Area:** `Placement Records` | **Difficulty:** `Difficult`
- **Tables Needed:** `STUDENT, INTERNSHIP, PLACEMENT, COMPANY`
- **Problem Statement:** Find all students who secured a placement offer at the same company where they previously interned. Display Roll_No, Full Name, Company_Name, Intern Role, Placed Role, and Package.

#### Question 43: Students with Monotonically Improving SGPA Across Semesters 1 to 4
- **Project Area:** `Academic Records and SGPA` | **Difficulty:** `Difficult`
- **Tables Needed:** `STUDENT, SEMESTER_RESULT`
- **Problem Statement:** Find all students whose SGPA consistently increased from Semester 1 to Semester 2, Semester 2 to Semester 3, and Semester 3 to Semester 4.

#### Question 44: Year-over-Year (YoY) Percentage Growth in Placements Using LAG()
- **Project Area:** `Salary and Package Analysis` | **Difficulty:** `Difficult`
- **Tables Needed:** `PLACEMENT`
- **Problem Statement:** Calculate the total placement offers in each year and use the LAG() window function to calculate the percentage growth compared to the previous year.

#### Question 45: Drive Eligibility Verification: Students Matching Opportunity Cutoffs
- **Project Area:** `Internship Eligibility` | **Difficulty:** `Difficult`
- **Tables Needed:** `STUDENT, OPPORTUNITY, ELIGIBILITY, ELIGIBILITY_BRANCH`
- **Problem Statement:** For Opportunity_ID = 1, find all students who meet all specified cutoff criteria: minimum CGPA, maximum backlogs, and branch eligibility.

#### Question 46: Comprehensive Student 360-Degree Profile Synthesis
- **Project Area:** `Student Information` | **Difficulty:** `Difficult`
- **Tables Needed:** `STUDENT, STUDENT_PHONE, STUDENT_SKILL, PLACEMENT, INTERNSHIP`
- **Problem Statement:** Construct a full 360-degree profile for Student_ID = 1 consolidating roll number, name, branch, CGPA, total phone numbers, total skills, comma-separated skill list, total placements, and total internships.

#### Question 47: Semester Academic Workload vs Student SGPA Performance Correlation
- **Project Area:** `Course Enrollment` | **Difficulty:** `Difficult`
- **Tables Needed:** `STUDENT, STUDENT_COURSE, COURSE, SEMESTER_RESULT`
- **Problem Statement:** Calculate the total course credits enrolled by each student in Semester 4 and correlate it with the actual SGPA achieved in that semester.

#### Question 48: Placement Salary Percentiles within Departments using NTILE(4)
- **Project Area:** `Placement Records` | **Difficulty:** `Difficult`
- **Tables Needed:** `STUDENT, PLACEMENT`
- **Problem Statement:** Divide placement offers within each engineering branch into 4 salary quartiles (Quartile 1 = lowest 25%, Quartile 4 = top 25%) using the NTILE(4) window function.

#### Question 49: Corporate Hiring Yield: Ratio of Offers to Selection Rounds
- **Project Area:** `Company Information` | **Difficulty:** `Difficult`
- **Tables Needed:** `RECRUITMENT_DRIVE, OPPORTUNITY, SELECTION_PROCESS, PLACEMENT, COMPANY`
- **Problem Statement:** For each recruitment drive in 2024, calculate the total selection rounds conducted, total job opportunities posted, and total resulting placement offers.

#### Question 50: Dual-Requirement Clearance Roster with Individual Requirement Status
- **Project Area:** `Mandatory Internship Completion` | **Difficulty:** `Difficult`
- **Tables Needed:** `STUDENT, INTERNSHIP`
- **Problem Statement:** Produce an administrative degree clearance report for all final-year students (Batch 2022/2023) listing their status for Mandatory Internship 1, Mandatory Internship 2, and overall Clearance Status ('Cleared' vs 'Hold').

#### Question 51: Students with Packages in the Top 10% of the Entire Institution
- **Project Area:** `Salary and Package Analysis` | **Difficulty:** `Difficult`
- **Tables Needed:** `STUDENT, PLACEMENT, COMPANY`
- **Problem Statement:** Find all students whose placement package ranks in the top 10% (90th percentile and above) across the entire university using the PERCENT_RANK() window function.

#### Question 52: Students with Both Digital Profiles and Uploaded Resumes
- **Project Area:** `Student Information` | **Difficulty:** `Difficult`
- **Tables Needed:** `STUDENT, STUDENT_PROFILE, RESUME`
- **Problem Statement:** Find all students who have registered a professional profile (LinkedIn/GitHub in STUDENT_PROFILE) AND uploaded a resume in the RESUME table, listing their profile links.

#### Question 53: Students Who Failed Any Enrolled Course (Grade = 'F')
- **Project Area:** `Course Enrollment` | **Difficulty:** `Difficult`
- **Tables Needed:** `STUDENT, STUDENT_COURSE, COURSE`
- **Problem Statement:** Find all students who received a failing grade ('F') in any course, showing their Roll_No, Full Name, Branch, Failed Course Name, and Semester.

#### Question 44: Companies Recruiter Loyalty Index: Multi-Year Participating Partners
- **Project Area:** `Company Information` | **Difficulty:** `Difficult`
- **Tables Needed:** `COMPANY, PLACEMENT`
- **Problem Statement:** Find all companies that have recruited students across 3 or more distinct calendar years, calculating total students hired and average package.

#### Question 55: Comprehensive Academic Transcript Summary for a Student
- **Project Area:** `Academic Records and SGPA` | **Difficulty:** `Difficult`
- **Tables Needed:** `SEMESTER_RESULT`
- **Problem Statement:** Produce a complete academic transcript ledger for Student_ID = 1 displaying Semester number, SGPA, Total Credits, Cumulative Credits, and Cumulative CGPA progression across semesters.

---

# Part 2: Comprehensive Solutions Manual & Walkthrough

## Solution 1: Number of Students in Each Graduating Batch
- **Project Area:** `Branch and Batch` | **Difficulty Level:** `Easy`
- **What the question is asking in simple terms:** Find the total count of registered students in each graduating batch year, sorted chronologically by Batch_Year.

### 1. Correct Executable SQL Query
```sql
SELECT Batch_Year, COUNT(*) AS Total_Students
FROM STUDENT
GROUP BY Batch_Year
ORDER BY Batch_Year ASC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT Batch_Year, COUNT(*) AS Total_Students `
  * **Explanation:** Projects the batch year and counts the number of student rows falling into each year.
- ` FROM STUDENT `
  * **Explanation:** Specifies the master STUDENT table containing candidate demographic records.
- ` GROUP BY Batch_Year `
  * **Explanation:** Aggregates the individual student tuples by the Batch_Year column.
- ` ORDER BY Batch_Year ASC `
  * **Explanation:** Sorts the resulting groups from the earliest batch to the latest batch.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT`
- **Rationale:** STUDENT table contains the Batch_Year attribute and primary keys for all students.

### 4. Key SQL Concepts Used
`GROUP BY, COUNT(*), ORDER BY ASC`

### 5. Expected Output Format & Sample Output
| Batch_Year | Total_Students |
|---|---|
| 2021 | 18 |
| 2022 | 24 |
| 2023 | 30 |
| 2024 | 28 |

---

## Solution 2: Students with High Academic Standing and Zero Backlogs
- **Project Area:** `Student Information` | **Difficulty Level:** `Easy`
- **What the question is asking in simple terms:** Retrieve the Roll_No, Full Name, Branch, and CGPA of all students who have achieved a CGPA of 8.00 or higher with zero backlogs, ordered by CGPA descending.

### 1. Correct Executable SQL Query
```sql
SELECT Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Full_Name, Branch, CGPA
FROM STUDENT
WHERE CGPA >= 8.00 AND Backlogs = 0
ORDER BY CGPA DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Full_Name, Branch, CGPA `
  * **Explanation:** Projects student roll number, combined full name, department, and CGPA.
- ` FROM STUDENT `
  * **Explanation:** Scans the master student table.
- ` WHERE CGPA >= 8.00 AND Backlogs = 0 `
  * **Explanation:** Filters candidates who meet the dual honors criteria: minimum 8.0 CGPA and no pending backlogs.
- ` ORDER BY CGPA DESC `
  * **Explanation:** Sorts the list with the highest CGPA at the top.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT`
- **Rationale:** All required academic standing attributes (CGPA, Backlogs) reside directly in the STUDENT master table.

### 4. Key SQL Concepts Used
`WHERE, AND, Comparison Operators, CONCAT_WS, ORDER BY DESC`

### 5. Expected Output Format & Sample Output
| Roll_No | Full_Name | Branch | CGPA |
|---|---|---|---|
| CS202201 | Rahul Sharma | CSE | 9.45 |
| EC202203 | Priya Nair | ECE | 9.12 |
| ME202205 | Amit Patel | ME | 8.85 |

---

## Solution 3: Product-Based Companies Located in Bangalore
- **Project Area:** `Company Information` | **Difficulty Level:** `Easy`
- **What the question is asking in simple terms:** Find the Company_Name, Industry, and Website of all companies categorized as 'Product' located in 'Bangalore' or 'Bengaluru'.

### 1. Correct Executable SQL Query
```sql
SELECT Company_Name, Industry, Website
FROM COMPANY
WHERE Company_Type = 'Product' AND Location IN ('Bangalore', 'Bengaluru')
ORDER BY Company_Name ASC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT Company_Name, Industry, Website `
  * **Explanation:** Projects the recruiter corporate name, domain, and web address.
- ` FROM COMPANY `
  * **Explanation:** Queries the corporate recruiter master table.
- ` WHERE Company_Type = 'Product' AND Location IN ('Bangalore', 'Bengaluru') `
  * **Explanation:** Restricts records to product companies in Bangalore using an IN clause for city spelling variations.
- ` ORDER BY Company_Name ASC `
  * **Explanation:** Alphabetical sorting on company name.

### 3. Tables Used and Relational Rationale
- **Tables:** `COMPANY`
- **Rationale:** COMPANY table holds corporate profiles, organizational tier (Company_Type), and geographical location.

### 4. Key SQL Concepts Used
`WHERE, IN, Comparison Operators, ORDER BY`

### 5. Expected Output Format & Sample Output
| Company_Name | Industry | Website |
|---|---|---|
| Cisco Systems | Networking | https://cisco.com |
| Microsoft | Software | https://microsoft.com |

---

## Solution 4: On-Campus Placements in 2024 with Packages Exceeding 10 LPA
- **Project Area:** `Placement Records` | **Difficulty Level:** `Easy`
- **What the question is asking in simple terms:** List the Placement_ID, Student_ID, Role, and Package for all on-campus placements secured in 2024 offering a package of 10.00 LPA or higher.

### 1. Correct Executable SQL Query
```sql
SELECT Placement_ID, Student_ID, Role, Package
FROM PLACEMENT
WHERE Placement_Type = 'On-campus' AND Placement_Year = 2024 AND Package >= 10.00
ORDER BY Package DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT Placement_ID, Student_ID, Role, Package `
  * **Explanation:** Projects the primary offer key, candidate foreign key, designated role, and CTC.
- ` FROM PLACEMENT `
  * **Explanation:** Scans the placement facts table.
- ` WHERE Placement_Type = 'On-campus' AND Placement_Year = 2024 AND Package >= 10.00 `
  * **Explanation:** Applies a 3-part filtering condition on placement mode, year, and compensation.
- ` ORDER BY Package DESC `
  * **Explanation:** Ranks offers by highest compensation package first.

### 3. Tables Used and Relational Rationale
- **Tables:** `PLACEMENT`
- **Rationale:** PLACEMENT contains all compensation terms, offer modes, and recruitment years.

### 4. Key SQL Concepts Used
`WHERE, AND, Numeric Bounds, ORDER BY`

### 5. Expected Output Format & Sample Output
| Placement_ID | Student_ID | Role | Package |
|---|---|---|---|
| 104 | 12 | Systems Engineer | 18.50 |
| 112 | 27 | SDE-1 | 14.00 |

---

## Solution 5: Mandatory Internships with Non-Zero Monthly Stipends
- **Project Area:** `Internship Records` | **Difficulty Level:** `Easy`
- **What the question is asking in simple terms:** Find all mandatory internships where the monthly stipend is greater than 0. Display Student_ID, Role, Stipend, and Duration in Days.

### 1. Correct Executable SQL Query
```sql
SELECT Student_ID, Role, Stipend, DATEDIFF(End_Date, Start_Date) + 1 AS Duration_Days
FROM INTERNSHIP
WHERE Internship_Type = 'Mandatory' AND Stipend > 0.00
ORDER BY Stipend DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT Student_ID, Role, Stipend, DATEDIFF(End_Date, Start_Date) + 1 AS Duration_Days `
  * **Explanation:** Projects student ID, role, stipend, and calculates duration using DATEDIFF + 1.
- ` FROM INTERNSHIP `
  * **Explanation:** Base internship table.
- ` WHERE Internship_Type = 'Mandatory' AND Stipend > 0.00 `
  * **Explanation:** Filters for mandatory degree internships providing monetary compensation.
- ` ORDER BY Stipend DESC `
  * **Explanation:** Sorts by highest paying stipend.

### 3. Tables Used and Relational Rationale
- **Tables:** `INTERNSHIP`
- **Rationale:** INTERNSHIP table stores mandatory classifications, stipends, and tenure dates.

### 4. Key SQL Concepts Used
`WHERE, DATEDIFF, Date Arithmetic, Comparison`

### 5. Expected Output Format & Sample Output
| Student_ID | Role | Stipend | Duration_Days |
|---|---|---|---|
| 14 | ML Intern | 35000.00 | 61 |
| 22 | Cloud Intern | 25000.00 | 60 |

---

## Solution 6: Semester 5 Examination Results with SGPA >= 7.50
- **Project Area:** `Academic Records and SGPA` | **Difficulty Level:** `Easy`
- **What the question is asking in simple terms:** Find all students who scored an SGPA of 7.50 or higher in Semester 5 examinations, showing Student_ID, SGPA, and Total_Credits, sorted by SGPA descending.

### 1. Correct Executable SQL Query
```sql
SELECT Student_ID, SGPA, Total_Credits, Year
FROM SEMESTER_RESULT
WHERE Semester = 5 AND SGPA >= 7.50
ORDER BY SGPA DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT Student_ID, SGPA, Total_Credits, Year `
  * **Explanation:** Projects candidate ID, grade point average, credits, and examination year.
- ` FROM SEMESTER_RESULT `
  * **Explanation:** Academic semester ledger table.
- ` WHERE Semester = 5 AND SGPA >= 7.50 `
  * **Explanation:** Restricts results to Semester 5 records meeting the 7.50 threshold.
- ` ORDER BY SGPA DESC `
  * **Explanation:** Sorts the top academic performers first.

### 3. Tables Used and Relational Rationale
- **Tables:** `SEMESTER_RESULT`
- **Rationale:** SEMESTER_RESULT stores semester-wise SGPA and total credits.

### 4. Key SQL Concepts Used
`WHERE, Comparison, ORDER BY DESC`

### 5. Expected Output Format & Sample Output
| Student_ID | SGPA | Total_Credits | Year |
|---|---|---|---|
| 8 | 9.20 | 24 | 2023 |
| 15 | 8.80 | 24 | 2023 |

---

## Solution 7: Distinct Courses Offered in Even Semesters
- **Project Area:** `Course Enrollment` | **Difficulty Level:** `Easy`
- **What the question is asking in simple terms:** List all distinct courses offered in even semesters (Semesters 2, 4, 6, 8) with their Course_Name, Department, Semester, and Credits.

### 1. Correct Executable SQL Query
```sql
SELECT Course_ID, Course_Name, Department, Semester, Credits
FROM COURSE
WHERE Semester IN (2, 4, 6, 8)
ORDER BY Semester ASC, Course_Name ASC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT Course_ID, Course_Name, Department, Semester, Credits `
  * **Explanation:** Projects course catalog identifiers and attributes.
- ` FROM COURSE `
  * **Explanation:** Curriculum course master table.
- ` WHERE Semester IN (2, 4, 6, 8) `
  * **Explanation:** Filters for even academic semesters.
- ` ORDER BY Semester ASC, Course_Name ASC `
  * **Explanation:** Sorts chronologically by semester, then course title.

### 3. Tables Used and Relational Rationale
- **Tables:** `COURSE`
- **Rationale:** COURSE holds the academic syllabus structure and department mappings.

### 4. Key SQL Concepts Used
`WHERE, IN operator, ORDER BY`

### 5. Expected Output Format & Sample Output
| Course_ID | Course_Name | Department | Semester | Credits |
|---|---|---|---|---|
| 102 | Data Structures | CSE | 4 | 4 |
| 106 | Database Systems | CSE | 4 | 4 |

---

## Solution 8: Students Registered with Multiple Phone Numbers
- **Project Area:** `Student Information` | **Difficulty Level:** `Easy`
- **What the question is asking in simple terms:** Find the Student_ID and the count of registered phone numbers for all students who have registered more than 1 contact number in STUDENT_PHONE.

### 1. Correct Executable SQL Query
```sql
SELECT Student_ID, COUNT(Phone_No) AS Phone_Count
FROM STUDENT_PHONE
GROUP BY Student_ID
HAVING COUNT(Phone_No) > 1
ORDER BY Phone_Count DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT Student_ID, COUNT(Phone_No) AS Phone_Count `
  * **Explanation:** Projects student ID and counts their phone rows.
- ` FROM STUDENT_PHONE `
  * **Explanation:** Decomposed contact phone numbers table.
- ` GROUP BY Student_ID `
  * **Explanation:** Aggregates contacts per individual student.
- ` HAVING COUNT(Phone_No) > 1 `
  * **Explanation:** Filters for candidates with multiple recorded numbers.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT_PHONE`
- **Rationale:** STUDENT_PHONE implements 1NF decomposition of multi-valued contact phone numbers.

### 4. Key SQL Concepts Used
`GROUP BY, HAVING, COUNT(*)`

### 5. Expected Output Format & Sample Output
| Student_ID | Phone_Count |
|---|---|
| 5 | 2 |
| 14 | 2 |

---

## Solution 9: Highest and Lowest Packages Offered by Service-Based Companies
- **Project Area:** `Salary and Package Analysis` | **Difficulty Level:** `Easy`
- **What the question is asking in simple terms:** Find the highest, lowest, and average placement packages offered specifically by 'Service' type companies.

### 1. Correct Executable SQL Query
```sql
SELECT MAX(p.Package) AS Max_Package, MIN(p.Package) AS Min_Package, ROUND(AVG(p.Package), 2) AS Avg_Package
FROM PLACEMENT p
JOIN COMPANY c ON p.Company_ID = c.Company_ID
WHERE c.Company_Type = 'Service';
```

### 2. Line-by-Line Query Explanation
- ` SELECT MAX(p.Package) AS Max_Package, MIN(p.Package) AS Min_Package, ROUND(AVG(p.Package), 2) AS Avg_Package `
  * **Explanation:** Calculates statistical package bounds for service recruiters.
- ` FROM PLACEMENT p `
  * **Explanation:** Placement facts table.
- ` JOIN COMPANY c ON p.Company_ID = c.Company_ID `
  * **Explanation:** Equi-join matching recruiter corporate type.
- ` WHERE c.Company_Type = 'Service' `
  * **Explanation:** Filters for service-oriented firms.

### 3. Tables Used and Relational Rationale
- **Tables:** `PLACEMENT, COMPANY`
- **Rationale:** PLACEMENT has package compensation; COMPANY has the recruiter category (Company_Type).

### 4. Key SQL Concepts Used
`INNER JOIN, Aggregate Functions (MAX, MIN, AVG, ROUND), WHERE`

### 5. Expected Output Format & Sample Output
| Max_Package | Min_Package | Avg_Package |
|---|---|---|
| 9.50 | 3.60 | 5.85 |

---

## Solution 10: Count of Students Enrolled in Each Course in 2024
- **Project Area:** `Course Enrollment` | **Difficulty Level:** `Easy`
- **What the question is asking in simple terms:** Find the total number of students enrolled in each course during the academic year 2024, displaying Course_ID and student count.

### 1. Correct Executable SQL Query
```sql
SELECT Course_ID, COUNT(Student_ID) AS Enrolled_Students
FROM STUDENT_COURSE
WHERE Enrollment_Year = 2024
GROUP BY Course_ID
ORDER BY Enrolled_Students DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT Course_ID, COUNT(Student_ID) AS Enrolled_Students `
  * **Explanation:** Projects course ID and tallies student enrollments.
- ` FROM STUDENT_COURSE `
  * **Explanation:** Junction table linking students to registered courses.
- ` WHERE Enrollment_Year = 2024 `
  * **Explanation:** Filters for the 2024 academic year.
- ` GROUP BY Course_ID `
  * **Explanation:** Groups by course.
- ` ORDER BY Enrolled_Students DESC `
  * **Explanation:** Sorts by highest enrollment count.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT_COURSE`
- **Rationale:** STUDENT_COURSE resolves the Many-to-Many relationship between students and courses.

### 4. Key SQL Concepts Used
`GROUP BY, COUNT(*), WHERE, ORDER BY DESC`

### 5. Expected Output Format & Sample Output
| Course_ID | Enrolled_Students |
|---|---|
| 101 | 45 |
| 104 | 42 |

---

## Solution 11: Companies Hosting Recruitment Drives in the Fall Season
- **Project Area:** `Company Information` | **Difficulty Level:** `Easy`
- **What the question is asking in simple terms:** Find the distinct names of companies that conducted campus recruitment drives during the 'Fall' season.

### 1. Correct Executable SQL Query
```sql
SELECT DISTINCT c.Company_Name, c.Company_Type, c.Location
FROM COMPANY c
JOIN RECRUITMENT_DRIVE rd ON c.Company_ID = rd.Company_ID
WHERE rd.Season = 'Fall'
ORDER BY c.Company_Name ASC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT DISTINCT c.Company_Name, c.Company_Type, c.Location `
  * **Explanation:** Eliminates duplicate company rows if a company had multiple Fall drives.
- ` FROM COMPANY c `
  * **Explanation:** Company master table.
- ` JOIN RECRUITMENT_DRIVE rd ON c.Company_ID = rd.Company_ID `
  * **Explanation:** Equi-join on Company_ID.
- ` WHERE rd.Season = 'Fall' `
  * **Explanation:** Filters for Fall recruitment drives.

### 3. Tables Used and Relational Rationale
- **Tables:** `COMPANY, RECRUITMENT_DRIVE`
- **Rationale:** RECRUITMENT_DRIVE specifies Season; COMPANY specifies corporate identity.

### 4. Key SQL Concepts Used
`DISTINCT, INNER JOIN, WHERE`

### 5. Expected Output Format & Sample Output
| Company_Name | Company_Type | Location |
|---|---|---|
| Amazon | Product | Hyderabad |
| Infosys | Service | Bangalore |

---

## Solution 12: Count of Internships Evaluated per Academic Semester
- **Project Area:** `Internship Records` | **Difficulty Level:** `Easy`
- **What the question is asking in simple terms:** Find the total number of internships submitted for academic credit evaluation in each Report_Semester.

### 1. Correct Executable SQL Query
```sql
SELECT Report_Semester, COUNT(*) AS Total_Evaluated
FROM INTERNSHIP
WHERE Report_Semester IS NOT NULL
GROUP BY Report_Semester
ORDER BY Report_Semester ASC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT Report_Semester, COUNT(*) AS Total_Evaluated `
  * **Explanation:** Projects reporting semester and count of evaluated reports.
- ` FROM INTERNSHIP `
  * **Explanation:** Internship table.
- ` WHERE Report_Semester IS NOT NULL `
  * **Explanation:** Filters out voluntary internships that carry no academic report semester.
- ` GROUP BY Report_Semester `
  * **Explanation:** Groups by semester (typically Sem 5 or Sem 7).
- ` ORDER BY Report_Semester ASC `
  * **Explanation:** Ascending chronological order.

### 3. Tables Used and Relational Rationale
- **Tables:** `INTERNSHIP`
- **Rationale:** Report_Semester attribute in INTERNSHIP identifies the evaluation cycle.

### 4. Key SQL Concepts Used
`GROUP BY, COUNT(*), IS NOT NULL, ORDER BY ASC`

### 5. Expected Output Format & Sample Output
| Report_Semester | Total_Evaluated |
|---|---|
| 5 | 28 |
| 7 | 25 |

---

## Solution 13: Students Who Have Formally Accepted/Joined Their Offer
- **Project Area:** `Placement Records` | **Difficulty Level:** `Easy`
- **What the question is asking in simple terms:** Retrieve the Student_ID, Role, Package, and Company_ID for all placement offers where Joined = 'Yes' or Offer_Status = 'Joined'.

### 1. Correct Executable SQL Query
```sql
SELECT Student_ID, Role, Package, Company_ID
FROM PLACEMENT
WHERE Joined = 'Yes' OR Offer_Status = 'Joined'
ORDER BY Package DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT Student_ID, Role, Package, Company_ID `
  * **Explanation:** Projects key offer attributes.
- ` FROM PLACEMENT `
  * **Explanation:** Placement offers facts table.
- ` WHERE Joined = 'Yes' OR Offer_Status = 'Joined' `
  * **Explanation:** Identifies officially accepted career placements.
- ` ORDER BY Package DESC `
  * **Explanation:** Highest package first.

### 3. Tables Used and Relational Rationale
- **Tables:** `PLACEMENT`
- **Rationale:** Enforces inspection of the single joined offer rule in PLACEMENT.

### 4. Key SQL Concepts Used
`WHERE, OR, Comparison`

### 5. Expected Output Format & Sample Output
| Student_ID | Role | Package | Company_ID |
|---|---|---|---|
| 12 | Software Engineer | 18.50 | 3 |
| 18 | Data Analyst | 12.00 | 5 |

---

## Solution 14: Students Registered in Section 'A' with Email Addresses
- **Project Area:** `Student Information` | **Difficulty Level:** `Easy`
- **What the question is asking in simple terms:** Find the Roll_No, Full Name, and Email of all students belonging to Section 'A', ordered alphabetically by First_Name.

### 1. Correct Executable SQL Query
```sql
SELECT Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Student_Name, Email
FROM STUDENT
WHERE Section = 'A'
ORDER BY First_Name ASC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Student_Name, Email `
  * **Explanation:** Projects roll number, assembled name, and email.
- ` FROM STUDENT `
  * **Explanation:** Master student table.
- ` WHERE Section = 'A' `
  * **Explanation:** Filters for Section A.
- ` ORDER BY First_Name ASC `
  * **Explanation:** Alphabetical sort.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT`
- **Rationale:** Section and Email attributes reside in STUDENT.

### 4. Key SQL Concepts Used
`WHERE, CONCAT_WS, ORDER BY ASC`

### 5. Expected Output Format & Sample Output
| Roll_No | Student_Name | Email |
|---|---|---|
| CS202201 | Aarav Gupta | aarav.g@college.edu |
| CS202204 | Diya Sen | diya.s@college.edu |

---

## Solution 15: Total Placements Categorized by Placement Type
- **Project Area:** `Placement Records` | **Difficulty Level:** `Easy`
- **What the question is asking in simple terms:** Find the total number of placement offers categorized by Placement_Type ('On-campus' vs 'Off-campus') along with the average package in each category.

### 1. Correct Executable SQL Query
```sql
SELECT Placement_Type, COUNT(*) AS Total_Offers, ROUND(AVG(Package), 2) AS Avg_Package
FROM PLACEMENT
GROUP BY Placement_Type;
```

### 2. Line-by-Line Query Explanation
- ` SELECT Placement_Type, COUNT(*) AS Total_Offers, ROUND(AVG(Package), 2) AS Avg_Package `
  * **Explanation:** Projects category and computes offer count and mean salary.
- ` FROM PLACEMENT `
  * **Explanation:** Placement offers facts table.
- ` GROUP BY Placement_Type `
  * **Explanation:** Aggregates by on-campus versus off-campus mode.

### 3. Tables Used and Relational Rationale
- **Tables:** `PLACEMENT`
- **Rationale:** Placement_Type ENUM column in PLACEMENT.

### 4. Key SQL Concepts Used
`GROUP BY, COUNT(*), ROUND(AVG(...), 2)`

### 5. Expected Output Format & Sample Output
| Placement_Type | Total_Offers | Avg_Package |
|---|---|---|
| On-campus | 54 | 9.42 |
| Off-campus | 12 | 11.20 |

---

## Solution 16: Students with Perfect 10.00 SGPA in Any Semester
- **Project Area:** `Academic Records and SGPA` | **Difficulty Level:** `Easy`
- **What the question is asking in simple terms:** Find all records where a student attained an SGPA of 10.00. Display Student_ID, Semester, Year, and Total_Credits.

### 1. Correct Executable SQL Query
```sql
SELECT Student_ID, Semester, Year, Total_Credits
FROM SEMESTER_RESULT
WHERE SGPA = 10.00
ORDER BY Year DESC, Semester ASC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT Student_ID, Semester, Year, Total_Credits `
  * **Explanation:** Projects academic marks record.
- ` FROM SEMESTER_RESULT `
  * **Explanation:** Semester performance table.
- ` WHERE SGPA = 10.00 `
  * **Explanation:** Filters for perfect academic scores.

### 3. Tables Used and Relational Rationale
- **Tables:** `SEMESTER_RESULT`
- **Rationale:** SEMESTER_RESULT tracks semester SGPA.

### 4. Key SQL Concepts Used
`WHERE, Exact Numeric Match, ORDER BY`

### 5. Expected Output Format & Sample Output
| Student_ID | Semester | Year | Total_Credits |
|---|---|---|---|
| 4 | 4 | 2023 | 24 |

---

## Solution 17: Total Internships Completed per Internship Number
- **Project Area:** `Internship Records` | **Difficulty Level:** `Easy`
- **What the question is asking in simple terms:** Count how many internships were completed as Internship_No = 1 (2nd yr summer), Internship_No = 2 (3rd yr summer), and additional internships (No >= 3).

### 1. Correct Executable SQL Query
```sql
SELECT Internship_No, COUNT(*) AS Total_Internships
FROM INTERNSHIP
GROUP BY Internship_No
ORDER BY Internship_No ASC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT Internship_No, COUNT(*) AS Total_Internships `
  * **Explanation:** Projects sequence number and count.
- ` FROM INTERNSHIP `
  * **Explanation:** Internship table.
- ` GROUP BY Internship_No `
  * **Explanation:** Aggregates by milestone number.

### 3. Tables Used and Relational Rationale
- **Tables:** `INTERNSHIP`
- **Rationale:** Internship_No attribute in INTERNSHIP distinguishes graduation requirements from voluntary tenures.

### 4. Key SQL Concepts Used
`GROUP BY, COUNT(*), ORDER BY ASC`

### 5. Expected Output Format & Sample Output
| Internship_No | Total_Internships |
|---|---|
| 1 | 38 |
| 2 | 31 |
| 3 | 7 |

---

## Solution 18: Companies in the Financial and FinTech Industries
- **Project Area:** `Company Information` | **Difficulty Level:** `Easy`
- **What the question is asking in simple terms:** Find all companies whose Industry contains 'FinTech', 'Finance', or 'Banking' using the LIKE pattern matching operator.

### 1. Correct Executable SQL Query
```sql
SELECT Company_ID, Company_Name, Industry, Location
FROM COMPANY
WHERE Industry LIKE '%FinTech%' OR Industry LIKE '%Finance%' OR Industry LIKE '%Banking%'
ORDER BY Company_Name ASC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT Company_ID, Company_Name, Industry, Location `
  * **Explanation:** Projects corporate details.
- ` FROM COMPANY `
  * **Explanation:** Company table.
- ` WHERE Industry LIKE '%FinTech%' OR ... `
  * **Explanation:** Wildcard search on industry string.

### 3. Tables Used and Relational Rationale
- **Tables:** `COMPANY`
- **Rationale:** Industry column in COMPANY holds sectoral descriptions.

### 4. Key SQL Concepts Used
`WHERE, LIKE, Pattern Matching, OR`

### 5. Expected Output Format & Sample Output
| Company_ID | Company_Name | Industry | Location |
|---|---|---|---|
| 8 | Goldman Sachs | Investment Banking | Bangalore |
| 14 | Razorpay | FinTech | Bangalore |

---

## Solution 19: Average Package Branch-Wise
- **Project Area:** `Salary and Package Analysis` | **Difficulty Level:** `Medium`
- **What the question is asking in simple terms:** Calculate the average placement package (rounded to 2 decimal places), total offers, and highest package secured by each engineering branch.

### 1. Correct Executable SQL Query
```sql
SELECT s.Branch, COUNT(p.Placement_ID) AS Total_Offers, ROUND(AVG(p.Package), 2) AS Avg_Package, MAX(p.Package) AS Highest_Package
FROM PLACEMENT p
JOIN STUDENT s ON p.Student_ID = s.Student_ID
GROUP BY s.Branch
ORDER BY Avg_Package DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT s.Branch, COUNT(p.Placement_ID) AS Total_Offers, ... `
  * **Explanation:** Projects branch and computes offer count, average CTC, and peak CTC.
- ` FROM PLACEMENT p `
  * **Explanation:** Placement facts table.
- ` JOIN STUDENT s ON p.Student_ID = s.Student_ID `
  * **Explanation:** Equi-join attaching student academic branch.
- ` GROUP BY s.Branch `
  * **Explanation:** Groups offers by engineering department.
- ` ORDER BY Avg_Package DESC `
  * **Explanation:** Ranks departments with highest average compensation first.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, PLACEMENT`
- **Rationale:** Requires joining PLACEMENT (for Package) to STUDENT (for Branch).

### 4. Key SQL Concepts Used
`INNER JOIN, GROUP BY, ROUND(AVG(...), 2), MAX, COUNT`

### 5. Expected Output Format & Sample Output
| Branch | Total_Offers | Avg_Package | Highest_Package |
|---|---|---|---|
| CSE | 32 | 12.80 | 28.00 |
| ECE | 18 | 9.45 | 16.50 |
| ME | 10 | 6.80 | 10.20 |

---

## Solution 20: Students Who Received Multiple Placement Offers
- **Project Area:** `Placement Records` | **Difficulty Level:** `Medium`
- **What the question is asking in simple terms:** Find all students who have received 2 or more placement offers. Display Student_ID, Roll_No, Full Name, Branch, and total offers received.

### 1. Correct Executable SQL Query
```sql
SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, COUNT(p.Placement_ID) AS Total_Offers
FROM STUDENT s
JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch
HAVING COUNT(p.Placement_ID) >= 2
ORDER BY Total_Offers DESC, s.Roll_No ASC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, ... `
  * **Explanation:** Projects student identity and offer count.
- ` FROM STUDENT s JOIN PLACEMENT p ON s.Student_ID = p.Student_ID `
  * **Explanation:** Joins candidate demographic table to placement offers.
- ` GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch `
  * **Explanation:** Groups candidate records by unique composite attributes.
- ` HAVING COUNT(p.Placement_ID) >= 2 `
  * **Explanation:** Filters out candidates with only 0 or 1 offer.
- ` ORDER BY Total_Offers DESC, s.Roll_No ASC `
  * **Explanation:** Highest achievers first.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, PLACEMENT`
- **Rationale:** Combines candidate identity from STUDENT with offer frequency from PLACEMENT.

### 4. Key SQL Concepts Used
`INNER JOIN, GROUP BY, HAVING, COUNT`

### 5. Expected Output Format & Sample Output
| Student_ID | Roll_No | Student_Name | Branch | Total_Offers |
|---|---|---|---|---|
| 5 | CS202205 | Aditya Sen | CSE | 3 |
| 12 | EC202202 | Neha Roy | ECE | 2 |

---

## Solution 21: Companies That Recruited the Maximum Number of Students
- **Project Area:** `Company Information` | **Difficulty Level:** `Medium`
- **What the question is asking in simple terms:** Find the companies that have hired the largest number of students, showing Company_Name, Company_Type, Industry, and total hires.

### 1. Correct Executable SQL Query
```sql
SELECT c.Company_ID, c.Company_Name, c.Company_Type, c.Industry, COUNT(p.Placement_ID) AS Total_Hires
FROM COMPANY c
JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
GROUP BY c.Company_ID, c.Company_Name, c.Company_Type, c.Industry
ORDER BY Total_Hires DESC
LIMIT 5;
```

### 2. Line-by-Line Query Explanation
- ` SELECT c.Company_ID, c.Company_Name, c.Company_Type, c.Industry, COUNT(p.Placement_ID) AS Total_Hires `
  * **Explanation:** Projects recruiter credentials and calculates total hires.
- ` FROM COMPANY c JOIN PLACEMENT p ON c.Company_ID = p.Company_ID `
  * **Explanation:** Joins corporate entities with secured placement records.
- ` GROUP BY c.Company_ID, c.Company_Name, c.Company_Type, c.Industry `
  * **Explanation:** Aggregates offers per employer.
- ` ORDER BY Total_Hires DESC LIMIT 5 `
  * **Explanation:** Isolates the top 5 recruiting powerhouses.

### 3. Tables Used and Relational Rationale
- **Tables:** `COMPANY, PLACEMENT`
- **Rationale:** Connects recruiter dimension (COMPANY) with hiring events (PLACEMENT).

### 4. Key SQL Concepts Used
`INNER JOIN, GROUP BY, COUNT(*), ORDER BY DESC, LIMIT`

### 5. Expected Output Format & Sample Output
| Company_ID | Company_Name | Company_Type | Industry | Total_Hires |
|---|---|---|---|---|
| 2 | Tata Consultancy Services | Service | IT Consulting | 14 |
| 5 | Infosys | Service | IT Services | 11 |

---

## Solution 22: Students Who Have Not Completed Mandatory Internships
- **Project Area:** `Mandatory Internship Completion` | **Difficulty Level:** `Medium`
- **What the question is asking in simple terms:** Find all active students who have NOT completed either Mandatory Internship #1 (after 2nd yr) OR Mandatory Internship #2 (after 3rd yr).

### 1. Correct Executable SQL Query
```sql
SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.Batch_Year, s.CGPA
FROM STUDENT s
WHERE NOT EXISTS (
    SELECT 1 FROM INTERNSHIP i1 
    WHERE i1.Student_ID = s.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = 'Mandatory'
)
OR NOT EXISTS (
    SELECT 1 FROM INTERNSHIP i2 
    WHERE i2.Student_ID = s.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = 'Mandatory'
)
ORDER BY s.Batch_Year ASC, s.Branch ASC, s.Roll_No ASC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, ... `
  * **Explanation:** Projects student identity and academic status.
- ` FROM STUDENT s `
  * **Explanation:** Master student table.
- ` WHERE NOT EXISTS (SELECT 1 FROM INTERNSHIP i1 ... Internship_No = 1 ...) `
  * **Explanation:** Checks if student lacks Mandatory Internship #1.
- ` OR NOT EXISTS (SELECT 1 FROM INTERNSHIP i2 ... Internship_No = 2 ...) `
  * **Explanation:** Checks if student lacks Mandatory Internship #2 (either missing qualifies the student for audit).
- ` ORDER BY s.Batch_Year ASC, s.Branch ASC, s.Roll_No ASC `
  * **Explanation:** Organizes audit roster by graduating class.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, INTERNSHIP`
- **Rationale:** Requires correlating STUDENT master against INTERNSHIP records on student ID and internship sequence number.

### 4. Key SQL Concepts Used
`NOT EXISTS, Correlated Subqueries, OR (Disjunction), Clearance Audit`

### 5. Expected Output Format & Sample Output
| Student_ID | Roll_No | Student_Name | Branch | Batch_Year | CGPA |
|---|---|---|---|---|---|
| 17 | CS202217 | Sneha Reddy | CSE | 2022 | 8.10 |
| 23 | ME202209 | Vikram Verma | ME | 2022 | 6.75 |

---

## Solution 23: Second-Highest Package (Using Subquery)
- **Project Area:** `Salary and Package Analysis` | **Difficulty Level:** `Medium`
- **What the question is asking in simple terms:** Find the second-highest placement package offered in the institution using a nested subquery with MAX() rather than LIMIT/OFFSET.

### 1. Correct Executable SQL Query
```sql
SELECT MAX(Package) AS Second_Highest_Package
FROM PLACEMENT
WHERE Package < (SELECT MAX(Package) FROM PLACEMENT);
```

### 2. Line-by-Line Query Explanation
- ` SELECT MAX(Package) AS Second_Highest_Package `
  * **Explanation:** Computes the maximum value within the filtered subset.
- ` FROM PLACEMENT `
  * **Explanation:** Scans placement packages.
- ` WHERE Package < (SELECT MAX(Package) FROM PLACEMENT) `
  * **Explanation:** Subquery computes absolute peak package (e.g. 28.00 LPA). The outer WHERE restricts rows to packages strictly less than 28.00 LPA. Outer MAX then picks the highest of the remaining, which is the 2nd highest.

### 3. Tables Used and Relational Rationale
- **Tables:** `PLACEMENT`
- **Rationale:** All placement compensation records reside in PLACEMENT.

### 4. Key SQL Concepts Used
`Nested Subquery, MAX(), Comparison Operator`

### 5. Expected Output Format & Sample Output
| Second_Highest_Package |
|---|
| 24.50 |

---

## Solution 24: Students Eligible for Mandatory Internship #1 (Existing Academic Rules)
- **Project Area:** `Internship Eligibility` | **Difficulty Level:** `Medium`
- **What the question is asking in simple terms:** Identify all students eligible for Mandatory Internship #1 (Summer after 2nd yr). Institutional rules require: Batch indicating 2nd year standing, CGPA >= 6.00, Backlogs = 0, Semester 3 SGPA >= 6.00, and not already completed.

### 1. Correct Executable SQL Query
```sql
SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.CGPA
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

### 2. Line-by-Line Query Explanation
- ` SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.CGPA `
  * **Explanation:** Projects eligible candidates.
- ` FROM STUDENT s `
  * **Explanation:** Master student table.
- ` WHERE s.CGPA >= 6.00 AND s.Backlogs = 0 `
  * **Explanation:** Checks fundamental academic baseline criteria.
- ` AND EXISTS (SELECT 1 FROM SEMESTER_RESULT sr WHERE ... Semester = 3 AND SGPA >= 6.00) `
  * **Explanation:** Verifies prerequisite Semester 3 performance.
- ` AND NOT EXISTS (SELECT 1 FROM INTERNSHIP i WHERE ... Internship_No = 1 ...) `
  * **Explanation:** Ensures the candidate has not already completed this mandatory milestone.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, SEMESTER_RESULT, INTERNSHIP`
- **Rationale:** Coordinates STUDENT (CGPA/backlogs), SEMESTER_RESULT (Sem 3 SGPA), and INTERNSHIP (completion history).

### 4. Key SQL Concepts Used
`EXISTS, NOT EXISTS, Multiple Relational Verification`

### 5. Expected Output Format & Sample Output
| Student_ID | Roll_No | Student_Name | Branch | CGPA |
|---|---|---|---|---|
| 11 | CS202302 | Tanya Shah | CSE | 8.65 |
| 14 | EC202305 | Rohan Das | ECE | 7.80 |

---

## Solution 25: Students Eligible for Mandatory Internship #2 (Existing Academic Rules)
- **Project Area:** `Internship Eligibility` | **Difficulty Level:** `Medium`
- **What the question is asking in simple terms:** Identify all students eligible for Mandatory Internship #2 (Summer after 3rd yr). Institutional rules require: Completed Mandatory Internship #1, CGPA >= 6.50, Backlogs = 0, and Semester 5 SGPA >= 6.50.

### 1. Correct Executable SQL Query
```sql
SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.CGPA
FROM STUDENT s
WHERE s.CGPA >= 6.50 
  AND s.Backlogs = 0
  AND EXISTS (
      SELECT 1 FROM INTERNSHIP i1
      WHERE i1.Student_ID = s.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = 'Mandatory'
  )
  AND EXISTS (
      SELECT 1 FROM SEMESTER_RESULT sr
      WHERE sr.Student_ID = s.Student_ID AND sr.Semester = 5 AND sr.SGPA >= 6.50
  )
  AND NOT EXISTS (
      SELECT 1 FROM INTERNSHIP i2
      WHERE i2.Student_ID = s.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = 'Mandatory'
  )
ORDER BY s.CGPA DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.CGPA `
  * **Explanation:** Projects qualified candidates.
- ` WHERE s.CGPA >= 6.50 AND s.Backlogs = 0 `
  * **Explanation:** Checks academic standing bounds.
- ` AND EXISTS (... i1.Internship_No = 1 ...) `
  * **Explanation:** Ensures Mandatory Internship #1 was successfully achieved.
- ` AND EXISTS (... sr.Semester = 5 AND sr.SGPA >= 6.50) `
  * **Explanation:** Ensures Semester 5 SGPA prerequisite is satisfied.
- ` AND NOT EXISTS (... i2.Internship_No = 2 ...) `
  * **Explanation:** Ensures student has not already completed Internship #2.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, SEMESTER_RESULT, INTERNSHIP`
- **Rationale:** Audits prerequisite chain across STUDENT, SEMESTER_RESULT, and INTERNSHIP.

### 4. Key SQL Concepts Used
`Double EXISTS, NOT EXISTS, Multi-Tier Prerequisite Enforcement`

### 5. Expected Output Format & Sample Output
| Student_ID | Roll_No | Student_Name | Branch | CGPA |
|---|---|---|---|---|
| 6 | CS202206 | Karan Mehta | CSE | 8.40 |
| 9 | EE202201 | Meera Iyer | EEE | 7.90 |

---

## Solution 26: CGPA Calculation from All Completed Semester Results
- **Project Area:** `Academic Records and SGPA` | **Difficulty Level:** `Medium`
- **What the question is asking in simple terms:** Calculate the cumulative average SGPA across all semesters for each student and compare it with the stored CGPA in the STUDENT table.

### 1. Correct Executable SQL Query
```sql
SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       s.CGPA AS Stored_CGPA,
       ROUND(AVG(sr.SGPA), 2) AS Calculated_CGPA,
       ROUND(ABS(s.CGPA - AVG(sr.SGPA)), 2) AS Discrepancy
FROM STUDENT s
JOIN SEMESTER_RESULT sr ON s.Student_ID = sr.Student_ID
GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.CGPA
ORDER BY Discrepancy DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT s.Student_ID, s.Roll_No, ..., s.CGPA AS Stored_CGPA, ROUND(AVG(sr.SGPA), 2) AS Calculated_CGPA `
  * **Explanation:** Projects student identity, stored CGPA, and computes mean SGPA across semester entries.
- ` FROM STUDENT s JOIN SEMESTER_RESULT sr ON s.Student_ID = sr.Student_ID `
  * **Explanation:** Equi-join on Student_ID.
- ` GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.CGPA `
  * **Explanation:** Groups by candidate master attributes.
- ` ORDER BY Discrepancy DESC `
  * **Explanation:** Highlights any data integrity drift.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, SEMESTER_RESULT`
- **Rationale:** Verifies data consistency between aggregate SEMESTER_RESULT records and master STUDENT table.

### 4. Key SQL Concepts Used
`INNER JOIN, GROUP BY, AVG, ROUND, Discrepancy Auditing`

### 5. Expected Output Format & Sample Output
| Student_ID | Roll_No | Student_Name | Stored_CGPA | Calculated_CGPA | Discrepancy |
|---|---|---|---|---|---|
| 1 | CS202201 | Rahul Sharma | 9.45 | 9.45 | 0.00 |

---

## Solution 27: Recruiters Who Have Offered Both PPOs and Regular Placements
- **Project Area:** `Company Information` | **Difficulty Level:** `Medium`
- **What the question is asking in simple terms:** Find all companies that have hired students through both Pre-Placement Offers (Is_PPO = 'Yes') AND standard on-campus offers (Is_PPO = 'No').

### 1. Correct Executable SQL Query
```sql
SELECT c.Company_ID, c.Company_Name, c.Industry
FROM COMPANY c
JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
GROUP BY c.Company_ID, c.Company_Name, c.Industry
HAVING COUNT(DISTINCT p.Is_PPO) = 2
ORDER BY c.Company_Name ASC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT c.Company_ID, c.Company_Name, c.Industry `
  * **Explanation:** Projects corporate identity.
- ` FROM COMPANY c JOIN PLACEMENT p ON c.Company_ID = p.Company_ID `
  * **Explanation:** Joins company with placement offers.
- ` GROUP BY c.Company_ID, c.Company_Name, c.Industry `
  * **Explanation:** Groups offers per employer.
- ` HAVING COUNT(DISTINCT p.Is_PPO) = 2 `
  * **Explanation:** Asserts that both 'Yes' and 'No' distinct values are present for that company.

### 3. Tables Used and Relational Rationale
- **Tables:** `COMPANY, PLACEMENT`
- **Rationale:** Inspects Is_PPO ENUM attribute in PLACEMENT linked to COMPANY.

### 4. Key SQL Concepts Used
`INNER JOIN, GROUP BY, HAVING, COUNT(DISTINCT)`

### 5. Expected Output Format & Sample Output
| Company_ID | Company_Name | Industry |
|---|---|---|
| 1 | Google | Technology |
| 4 | Amazon | E-Commerce |

---

## Solution 28: Average Internship Stipend Across Host Companies
- **Project Area:** `Internship Records` | **Difficulty Level:** `Medium`
- **What the question is asking in simple terms:** Calculate the total internships hosted and the average monthly stipend provided by each corporate partner (excluding unpaid internships).

### 1. Correct Executable SQL Query
```sql
SELECT c.Company_Name, c.Company_Type, COUNT(i.Internship_ID) AS Total_Internships, ROUND(AVG(i.Stipend), 2) AS Avg_Stipend
FROM COMPANY c
JOIN INTERNSHIP i ON c.Company_ID = i.Company_ID
WHERE i.Stipend > 0.00
GROUP BY c.Company_ID, c.Company_Name, c.Company_Type
ORDER BY Avg_Stipend DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT c.Company_Name, c.Company_Type, COUNT(i.Internship_ID) AS Total_Internships, ROUND(AVG(i.Stipend), 2) AS Avg_Stipend `
  * **Explanation:** Projects recruiter credentials, volume, and average monthly pay.
- ` FROM COMPANY c JOIN INTERNSHIP i ON c.Company_ID = i.Company_ID `
  * **Explanation:** Equi-join matching host organization.
- ` WHERE i.Stipend > 0.00 `
  * **Explanation:** Filters out zero-stipend internships.
- ` GROUP BY c.Company_ID, c.Company_Name, c.Company_Type `
  * **Explanation:** Groups by corporate entity.
- ` ORDER BY Avg_Stipend DESC `
  * **Explanation:** Ranks highest paying internship hosts first.

### 3. Tables Used and Relational Rationale
- **Tables:** `COMPANY, INTERNSHIP`
- **Rationale:** Combines host company metadata with compensation in INTERNSHIP.

### 4. Key SQL Concepts Used
`INNER JOIN, WHERE, GROUP BY, ROUND(AVG(...), 2), COUNT`

### 5. Expected Output Format & Sample Output
| Company_Name | Company_Type | Total_Internships | Avg_Stipend |
|---|---|---|---|
| Microsoft | Product | 6 | 45000.00 |
| Goldman Sachs | Product | 4 | 40000.00 |

---

## Solution 29: Courses with the Highest Student Enrollment
- **Project Area:** `Course Enrollment` | **Difficulty Level:** `Medium`
- **What the question is asking in simple terms:** Find the top 5 most enrolled courses in the university curriculum across all years, displaying Course_Name, Department, Semester, and total enrolled students.

### 1. Correct Executable SQL Query
```sql
SELECT c.Course_ID, c.Course_Name, c.Department, c.Semester, COUNT(sc.Student_ID) AS Enrolled_Students
FROM COURSE c
JOIN STUDENT_COURSE sc ON c.Course_ID = sc.Course_ID
GROUP BY c.Course_ID, c.Course_Name, c.Department, c.Semester
ORDER BY Enrolled_Students DESC
LIMIT 5;
```

### 2. Line-by-Line Query Explanation
- ` SELECT c.Course_ID, c.Course_Name, c.Department, c.Semester, COUNT(sc.Student_ID) AS Enrolled_Students `
  * **Explanation:** Projects course syllabus details and enrollment count.
- ` FROM COURSE c JOIN STUDENT_COURSE sc ON c.Course_ID = sc.Course_ID `
  * **Explanation:** Equi-join across Many-to-Many junction table.
- ` GROUP BY c.Course_ID, c.Course_Name, c.Department, c.Semester `
  * **Explanation:** Groups by academic course.
- ` ORDER BY Enrolled_Students DESC LIMIT 5 `
  * **Explanation:** Isolates the 5 largest courses.

### 3. Tables Used and Relational Rationale
- **Tables:** `COURSE, STUDENT_COURSE`
- **Rationale:** COURSE defines the catalog; STUDENT_COURSE tracks individual enrollments.

### 4. Key SQL Concepts Used
`INNER JOIN, GROUP BY, COUNT(*), ORDER BY DESC, LIMIT`

### 5. Expected Output Format & Sample Output
| Course_ID | Course_Name | Department | Semester | Enrolled_Students |
|---|---|---|---|---|
| 101 | Data Structures | CSE | 3 | 58 |
| 103 | Operating Systems | CSE | 4 | 54 |

---

## Solution 30: Students Possessing Both Python and SQL Skills
- **Project Area:** `Student Information` | **Difficulty Level:** `Medium`
- **What the question is asking in simple terms:** Find the Roll_No and Full Name of all students who possess BOTH 'Python' AND 'SQL' technical skills.

### 1. Correct Executable SQL Query
```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch
FROM STUDENT s
JOIN STUDENT_SKILL sk ON s.Student_ID = sk.Student_ID
WHERE sk.Skill IN ('Python', 'SQL')
GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch
HAVING COUNT(DISTINCT sk.Skill) = 2
ORDER BY s.Roll_No ASC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch `
  * **Explanation:** Projects qualified candidate.
- ` FROM STUDENT s JOIN STUDENT_SKILL sk ON s.Student_ID = sk.Student_ID `
  * **Explanation:** Joins student with technical skills.
- ` WHERE sk.Skill IN ('Python', 'SQL') `
  * **Explanation:** Filters rows for either skill.
- ` GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch `
  * **Explanation:** Groups by student.
- ` HAVING COUNT(DISTINCT sk.Skill) = 2 `
  * **Explanation:** Asserts that BOTH skills are present.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, STUDENT_SKILL`
- **Rationale:** Relational division pattern over 1NF STUDENT_SKILL table.

### 4. Key SQL Concepts Used
`INNER JOIN, WHERE, IN, GROUP BY, HAVING, COUNT(DISTINCT)`

### 5. Expected Output Format & Sample Output
| Roll_No | Student_Name | Branch |
|---|---|---|
| CS202201 | Rahul Sharma | CSE |
| CS202208 | Ananya Ray | CSE |

---

## Solution 31: Unplaced Students Prioritized by Academic Merit
- **Project Area:** `Placement Records` | **Difficulty Level:** `Medium`
- **What the question is asking in simple terms:** Generate a prioritized outreach list of unplaced students for the placement cell, displaying Roll_No, Full Name, Branch, CGPA, and Email, sorted with highest CGPA first.

### 1. Correct Executable SQL Query
```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.CGPA, s.Email
FROM STUDENT s
LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
WHERE p.Placement_ID IS NULL
ORDER BY s.CGPA DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.CGPA, s.Email `
  * **Explanation:** Projects unplaced student contact and academic data.
- ` FROM STUDENT s `
  * **Explanation:** Master student table.
- ` LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID `
  * **Explanation:** Preserves all students while matching placements.
- ` WHERE p.Placement_ID IS NULL `
  * **Explanation:** Keeps only students with zero matching placement rows.
- ` ORDER BY s.CGPA DESC `
  * **Explanation:** Ranks highest academic performers first for recruitment outreach.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, PLACEMENT`
- **Rationale:** Anti-join between STUDENT and PLACEMENT.

### 4. Key SQL Concepts Used
`LEFT OUTER JOIN, WHERE ... IS NULL (Anti-Join), ORDER BY DESC`

### 5. Expected Output Format & Sample Output
| Roll_No | Student_Name | Branch | CGPA | Email |
|---|---|---|---|---|
| CS202219 | Pooja Hegde | CSE | 8.80 | pooja.h@college.edu |
| EC202214 | Suresh Kumar | ECE | 8.25 | suresh.k@college.edu |

---

## Solution 32: Package Distribution Across Graduating Batches
- **Project Area:** `Salary and Package Analysis` | **Difficulty Level:** `Medium`
- **What the question is asking in simple terms:** Calculate the average, highest, and median-approximating salary package offered to each graduating batch year.

### 1. Correct Executable SQL Query
```sql
SELECT s.Batch_Year, COUNT(p.Placement_ID) AS Placements_Secured, ROUND(AVG(p.Package), 2) AS Avg_Package, MAX(p.Package) AS Peak_Package
FROM PLACEMENT p
JOIN STUDENT s ON p.Student_ID = s.Student_ID
GROUP BY s.Batch_Year
ORDER BY s.Batch_Year ASC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT s.Batch_Year, COUNT(p.Placement_ID) AS Placements_Secured, ... `
  * **Explanation:** Projects graduating batch year and computes placement metrics.
- ` FROM PLACEMENT p JOIN STUDENT s ON p.Student_ID = s.Student_ID `
  * **Explanation:** Equi-join linking offers to student graduating batch.
- ` GROUP BY s.Batch_Year `
  * **Explanation:** Groups offers by batch.
- ` ORDER BY s.Batch_Year ASC `
  * **Explanation:** Chronological ordering.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, PLACEMENT`
- **Rationale:** Links PLACEMENT compensation to STUDENT Batch_Year.

### 4. Key SQL Concepts Used
`INNER JOIN, GROUP BY, Aggregate Functions, ORDER BY`

### 5. Expected Output Format & Sample Output
| Batch_Year | Placements_Secured | Avg_Package | Peak_Package |
|---|---|---|---|
| 2022 | 22 | 8.90 | 18.00 |
| 2023 | 28 | 10.40 | 24.50 |

---

## Solution 33: Students with Long-Term Internships (> 3 Months)
- **Project Area:** `Internship Records` | **Difficulty Level:** `Medium`
- **What the question is asking in simple terms:** Find all internships where the calculated duration is strictly greater than 3.0 months. Display Roll_No, Student Name, Company Name, Role, and Duration in Months.

### 1. Correct Executable SQL Query
```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       c.Company_Name, i.Role,
       ROUND((DATEDIFF(i.End_Date, i.Start_Date) + 1) / 30.0, 1) AS Duration_Months
FROM INTERNSHIP i
JOIN STUDENT s ON i.Student_ID = s.Student_ID
JOIN COMPANY c ON i.Company_ID = c.Company_ID
WHERE ROUND((DATEDIFF(i.End_Date, i.Start_Date) + 1) / 30.0, 1) > 3.0
ORDER BY Duration_Months DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT s.Roll_No, ..., ROUND((DATEDIFF(i.End_Date, i.Start_Date) + 1) / 30.0, 1) AS Duration_Months `
  * **Explanation:** Projects student and company details alongside calculated duration.
- ` FROM INTERNSHIP i JOIN STUDENT s ... JOIN COMPANY c ... `
  * **Explanation:** 3-table equi-join.
- ` WHERE ROUND((DATEDIFF(...) + 1) / 30.0, 1) > 3.0 `
  * **Explanation:** Filters for internships exceeding 3 months.
- ` ORDER BY Duration_Months DESC `
  * **Explanation:** Longest tenures first.

### 3. Tables Used and Relational Rationale
- **Tables:** `INTERNSHIP, STUDENT, COMPANY`
- **Rationale:** Derives duration dynamically from INTERNSHIP and joins master dimensions.

### 4. Key SQL Concepts Used
`3-Table JOIN, DATEDIFF, ROUND, WHERE on Calculated Expression`

### 5. Expected Output Format & Sample Output
| Roll_No | Student_Name | Company_Name | Role | Duration_Months |
|---|---|---|---|---|
| CS202203 | Rohan Das | Intel | Firmware Intern | 6.0 |

---

## Solution 34: Total Academic Credits Earned by Students
- **Project Area:** `Academic Records and SGPA` | **Difficulty Level:** `Medium`
- **What the question is asking in simple terms:** Calculate the total academic credits earned by each student across all completed semesters in SEMESTER_RESULT, displaying Roll_No, Full Name, and Total Credits Earned.

### 1. Correct Executable SQL Query
```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, SUM(sr.Total_Credits) AS Total_Credits_Earned
FROM STUDENT s
JOIN SEMESTER_RESULT sr ON s.Student_ID = sr.Student_ID
GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch
ORDER BY Total_Credits_Earned DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT s.Roll_No, ..., SUM(sr.Total_Credits) AS Total_Credits_Earned `
  * **Explanation:** Projects candidate details and sums earned semester credits.
- ` FROM STUDENT s JOIN SEMESTER_RESULT sr ON s.Student_ID = sr.Student_ID `
  * **Explanation:** Equi-join matching academic records.
- ` GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch `
  * **Explanation:** Groups by individual student.
- ` ORDER BY Total_Credits_Earned DESC `
  * **Explanation:** Sorts by credits completed towards graduation.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, SEMESTER_RESULT`
- **Rationale:** SEMESTER_RESULT tracks semester credits; STUDENT tracks candidate identity.

### 4. Key SQL Concepts Used
`INNER JOIN, GROUP BY, SUM(), ORDER BY DESC`

### 5. Expected Output Format & Sample Output
| Roll_No | Student_Name | Branch | Total_Credits_Earned |
|---|---|---|---|
| CS202201 | Rahul Sharma | CSE | 120 |
| CS202202 | Sneha Patel | CSE | 120 |

---

## Solution 35: Count of Selection Rounds Scheduled per Opportunity
- **Project Area:** `Company Information` | **Difficulty Level:** `Medium`
- **What the question is asking in simple terms:** Find the number of selection rounds (aptitude, technical, HR) scheduled for each hiring opportunity, displaying Company_Name, Role, and Total Rounds.

### 1. Correct Executable SQL Query
```sql
SELECT c.Company_Name, o.Role, o.Package_Stipend, COUNT(sp.Round_ID) AS Total_Rounds
FROM SELECTION_PROCESS sp
JOIN OPPORTUNITY o ON sp.Opportunity_ID = o.Opportunity_ID
JOIN RECRUITMENT_DRIVE rd ON o.Drive_ID = rd.Drive_ID
JOIN COMPANY c ON rd.Company_ID = c.Company_ID
GROUP BY c.Company_Name, o.Opportunity_ID, o.Role, o.Package_Stipend
ORDER BY Total_Rounds DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT c.Company_Name, o.Role, o.Package_Stipend, COUNT(sp.Round_ID) AS Total_Rounds `
  * **Explanation:** Projects employer, role, compensation, and round count.
- ` FROM SELECTION_PROCESS sp JOIN OPPORTUNITY o ... JOIN RECRUITMENT_DRIVE rd ... JOIN COMPANY c ... `
  * **Explanation:** 4-table hierarchical equi-join chain traversing the recruitment pipeline.
- ` GROUP BY c.Company_Name, o.Opportunity_ID, o.Role, o.Package_Stipend `
  * **Explanation:** Groups by specific job opportunity.
- ` ORDER BY Total_Rounds DESC `
  * **Explanation:** Sorts by most rigorous hiring process.

### 3. Tables Used and Relational Rationale
- **Tables:** `COMPANY, RECRUITMENT_DRIVE, OPPORTUNITY, SELECTION_PROCESS`
- **Rationale:** Traverses the 4-level recruitment pipeline schema.

### 4. Key SQL Concepts Used
`4-Table INNER JOIN, GROUP BY, COUNT(*), ORDER BY DESC`

### 5. Expected Output Format & Sample Output
| Company_Name | Role | Package_Stipend | Total_Rounds |
|---|---|---|---|
| Google | SDE-1 | 24.00 | 5 |
| Amazon | Software Intern | 45000.00 | 4 |

---

## Solution 36: Students with Placement Package Higher Than Overall College Average
- **Project Area:** `Placement Records` | **Difficulty Level:** `Medium`
- **What the question is asking in simple terms:** Find all students who secured a placement package strictly greater than the overall college average package.

### 1. Correct Executable SQL Query
```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, p.Role, p.Package
FROM PLACEMENT p
JOIN STUDENT s ON p.Student_ID = s.Student_ID
WHERE p.Package > (SELECT AVG(Package) FROM PLACEMENT)
ORDER BY p.Package DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT s.Roll_No, ..., p.Role, p.Package `
  * **Explanation:** Projects placed student details and package.
- ` FROM PLACEMENT p JOIN STUDENT s ON p.Student_ID = s.Student_ID `
  * **Explanation:** Equi-join matching candidate.
- ` WHERE p.Package > (SELECT AVG(Package) FROM PLACEMENT) `
  * **Explanation:** Non-correlated subquery calculates institution-wide mean package. Outer query filters for offers exceeding that mean.
- ` ORDER BY p.Package DESC `
  * **Explanation:** Highest offers first.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, PLACEMENT`
- **Rationale:** Compares individual PLACEMENT row against aggregate scalar subquery.

### 4. Key SQL Concepts Used
`INNER JOIN, Non-Correlated Subquery, AVG(), Comparison`

### 5. Expected Output Format & Sample Output
| Roll_No | Student_Name | Branch | Role | Package |
|---|---|---|---|---|
| CS202201 | Rahul Sharma | CSE | SDE-1 | 24.00 |
| CS202207 | Priya Rao | CSE | Data Scientist | 16.50 |

---

## Solution 37: Course Grade Distribution ('A' Grades Achieved)
- **Project Area:** `Course Enrollment` | **Difficulty Level:** `Medium`
- **What the question is asking in simple terms:** Count how many students earned an 'A' or 'A+' grade in each academic course, displaying Course_Name, Department, and count of 'A' grades.

### 1. Correct Executable SQL Query
```sql
SELECT c.Course_Name, c.Department, c.Semester, COUNT(sc.Student_ID) AS Top_Grade_Count
FROM COURSE c
JOIN STUDENT_COURSE sc ON c.Course_ID = sc.Course_ID
WHERE sc.Grade IN ('A', 'A+', 'O')
GROUP BY c.Course_ID, c.Course_Name, c.Department, c.Semester
ORDER BY Top_Grade_Count DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT c.Course_Name, c.Department, c.Semester, COUNT(sc.Student_ID) AS Top_Grade_Count `
  * **Explanation:** Projects course information and tallies honors grades.
- ` FROM COURSE c JOIN STUDENT_COURSE sc ON c.Course_ID = sc.Course_ID `
  * **Explanation:** Equi-join across student course enrollments.
- ` WHERE sc.Grade IN ('A', 'A+', 'O') `
  * **Explanation:** Filters for top academic marks.
- ` GROUP BY c.Course_ID, c.Course_Name, c.Department, c.Semester `
  * **Explanation:** Groups by course.
- ` ORDER BY Top_Grade_Count DESC `
  * **Explanation:** Courses producing highest top grades first.

### 3. Tables Used and Relational Rationale
- **Tables:** `COURSE, STUDENT_COURSE`
- **Rationale:** COURSE holds title; STUDENT_COURSE holds assigned grade.

### 4. Key SQL Concepts Used
`INNER JOIN, WHERE, IN, GROUP BY, COUNT(*), ORDER BY DESC`

### 5. Expected Output Format & Sample Output
| Course_Name | Department | Semester | Top_Grade_Count |
|---|---|---|---|
| Database Systems | CSE | 4 | 22 |
| Computer Networks | CSE | 5 | 18 |

---

## Solution 38: Placement Conversion Percentage by Batch Year
- **Project Area:** `Branch and Batch` | **Difficulty Level:** `Medium`
- **What the question is asking in simple terms:** Calculate the total student count, placed student count, and placement percentage for each graduating batch year.

### 1. Correct Executable SQL Query
```sql
SELECT s.Batch_Year,
       COUNT(DISTINCT s.Student_ID) AS Total_Students,
       COUNT(DISTINCT p.Student_ID) AS Placed_Students,
       ROUND(COUNT(DISTINCT p.Student_ID) * 100.0 / COUNT(DISTINCT s.Student_ID), 2) AS Placement_Rate
FROM STUDENT s
LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
GROUP BY s.Batch_Year
ORDER BY s.Batch_Year ASC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT s.Batch_Year, COUNT(DISTINCT s.Student_ID) AS Total_Students, ... `
  * **Explanation:** Projects batch year and computes denominator and numerator counts.
- ` FROM STUDENT s LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID `
  * **Explanation:** Outer join preserving all students.
- ` GROUP BY s.Batch_Year `
  * **Explanation:** Groups by graduating year.
- ` ORDER BY s.Batch_Year ASC `
  * **Explanation:** Chronological order.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, PLACEMENT`
- **Rationale:** STUDENT holds candidate batch; PLACEMENT tracks offers.

### 4. Key SQL Concepts Used
`LEFT OUTER JOIN, COUNT(DISTINCT), Arithmetic in SQL, ROUND`

### 5. Expected Output Format & Sample Output
| Batch_Year | Total_Students | Placed_Students | Placement_Rate |
|---|---|---|---|
| 2022 | 24 | 20 | 83.33 |
| 2023 | 30 | 25 | 83.33 |

---

## Solution 39: Top 3 Highest Placement Packages Within Each Engineering Branch
- **Project Area:** `Salary and Package Analysis` | **Difficulty Level:** `Difficult`
- **What the question is asking in simple terms:** Find the top 3 highest placement packages within every engineering branch using the DENSE_RANK() window function.

### 1. Correct Executable SQL Query
```sql
WITH BranchRankedOffers AS (
    SELECT s.Branch, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
           c.Company_Name, p.Role, p.Package,
           DENSE_RANK() OVER (PARTITION BY s.Branch ORDER BY p.Package DESC) AS Package_Rank
    FROM PLACEMENT p
    JOIN STUDENT s ON p.Student_ID = s.Student_ID
    JOIN COMPANY c ON p.Company_ID = c.Company_ID
)
SELECT Branch, Roll_No, Student_Name, Company_Name, Role, Package, Package_Rank
FROM BranchRankedOffers
WHERE Package_Rank <= 3
ORDER BY Branch ASC, Package_Rank ASC;
```

### 2. Line-by-Line Query Explanation
- ` WITH BranchRankedOffers AS (...) `
  * **Explanation:** Defines CTE that computes in-branch ranking.
- ` DENSE_RANK() OVER (PARTITION BY s.Branch ORDER BY p.Package DESC) AS Package_Rank `
  * **Explanation:** Partitions offers by Branch and assigns dense rank ordering by Package descending without rank skipping on ties.
- ` SELECT ... FROM BranchRankedOffers WHERE Package_Rank <= 3 `
  * **Explanation:** Outer query filters for top 3 rank positions in each branch.
- ` ORDER BY Branch ASC, Package_Rank ASC `
  * **Explanation:** Organizes output hierarchically by department and rank.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, PLACEMENT, COMPANY`
- **Rationale:** Combines PLACEMENT fact table with STUDENT and COMPANY dimensions inside a CTE window query.

### 4. Key SQL Concepts Used
`Common Table Expression (WITH), Window Function (DENSE_RANK), PARTITION BY, Multi-Table JOIN`

### 5. Expected Output Format & Sample Output
| Branch | Roll_No | Student_Name | Company_Name | Role | Package | Package_Rank |
|---|---|---|---|---|---|---|
| CSE | CS202201 | Rahul Sharma | Google | SDE-1 | 24.00 | 1 |
| CSE | CS202205 | Aditya Sen | Microsoft | Software Eng | 21.00 | 2 |
| CSE | CS202212 | Neha Roy | Amazon | SDE-1 | 18.50 | 3 |

---

## Solution 40: Departmental Internship Compliance Matrix (Fully vs Partially vs Non-Compliant)
- **Project Area:** `Mandatory Internship Completion` | **Difficulty Level:** `Difficult`
- **What the question is asking in simple terms:** For each engineering branch, calculate the total students and break down the count of Fully Compliant students (Both 1 & 2), Partially Compliant (Only 1 or 2), and Non-Compliant (Neither).

### 1. Correct Executable SQL Query
```sql
SELECT Branch,
       COUNT(*) AS Total_Students,
       SUM(CASE WHEN Mandatory_Count = 2 THEN 1 ELSE 0 END) AS Fully_Compliant,
       SUM(CASE WHEN Mandatory_Count = 1 THEN 1 ELSE 0 END) AS Partially_Compliant,
       SUM(CASE WHEN Mandatory_Count = 0 THEN 1 ELSE 0 END) AS Non_Compliant
FROM (
    SELECT s.Student_ID, s.Branch,
           COUNT(DISTINCT CASE WHEN i.Internship_No IN (1, 2) AND i.Internship_Type = 'Mandatory' THEN i.Internship_No END) AS Mandatory_Count
    FROM STUDENT s
    LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
    GROUP BY s.Student_ID, s.Branch
) AS StudentCompliance
GROUP BY Branch
ORDER BY Branch ASC;
```

### 2. Line-by-Line Query Explanation
- ` FROM (SELECT s.Student_ID, s.Branch, COUNT(...) AS Mandatory_Count ... GROUP BY s.Student_ID, s.Branch) AS StudentCompliance `
  * **Explanation:** Inner subquery aggregates each student's distinct mandatory internship count (0, 1, or 2).
- ` SELECT Branch, COUNT(*) AS Total_Students, ... `
  * **Explanation:** Outer query aggregates per branch.
- ` SUM(CASE WHEN Mandatory_Count = 2 THEN 1 ELSE 0 END) AS Fully_Compliant `
  * **Explanation:** Conditionally sums students satisfying both requirements.
- ` SUM(CASE WHEN Mandatory_Count = 1 THEN 1 ELSE 0 END) AS Partially_Compliant `
  * **Explanation:** Conditionally sums students satisfying exactly 1 requirement.
- ` SUM(CASE WHEN Mandatory_Count = 0 THEN 1 ELSE 0 END) AS Non_Compliant `
  * **Explanation:** Conditionally sums students with 0 mandatory internships.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, INTERNSHIP`
- **Rationale:** Evaluates graduation degree compliance across STUDENT and INTERNSHIP entities.

### 4. Key SQL Concepts Used
`Subquery, LEFT JOIN, CASE WHEN, Two-Level Grouping, Conditional Counting`

### 5. Expected Output Format & Sample Output
| Branch | Total_Students | Fully_Compliant | Partially_Compliant | Non_Compliant |
|---|---|---|---|---|
| CSE | 42 | 34 | 6 | 2 |
| ECE | 28 | 20 | 5 | 3 |
| ME | 20 | 12 | 4 | 4 |

---

## Solution 41: Nth-Highest Package Generic Formulation (3rd Highest Package)
- **Project Area:** `Salary and Package Analysis` | **Difficulty Level:** `Difficult`
- **What the question is asking in simple terms:** Find the 3rd-highest package offered across the college using a correlated subquery that counts distinct higher packages, avoiding LIMIT/OFFSET.

### 1. Correct Executable SQL Query
```sql
SELECT DISTINCT p1.Package AS Third_Highest_Package
FROM PLACEMENT p1
WHERE 2 = (
    SELECT COUNT(DISTINCT p2.Package)
    FROM PLACEMENT p2
    WHERE p2.Package > p1.Package
);
```

### 2. Line-by-Line Query Explanation
- ` SELECT DISTINCT p1.Package AS Third_Highest_Package FROM PLACEMENT p1 `
  * **Explanation:** Selects unique package values from the outer scan.
- ` WHERE 2 = (SELECT COUNT(DISTINCT p2.Package) FROM PLACEMENT p2 WHERE p2.Package > p1.Package) `
  * **Explanation:** Correlated subquery: For package p1, counts how many distinct packages are strictly greater than p1. The 3rd highest package will have exactly 2 distinct packages greater than it (N - 1 = 3 - 1 = 2).

### 3. Tables Used and Relational Rationale
- **Tables:** `PLACEMENT`
- **Rationale:** Classic textbook DBMS viva query executed on PLACEMENT table.

### 4. Key SQL Concepts Used
`Correlated Subquery, COUNT(DISTINCT), Scalar Comparison`

### 5. Expected Output Format & Sample Output
| Third_Highest_Package |
|---|
| 21.00 |

---

## Solution 42: Students Placed in the Same Company Where They Did an Internship (PPO Conversion Analysis)
- **Project Area:** `Placement Records` | **Difficulty Level:** `Difficult`
- **What the question is asking in simple terms:** Find all students who secured a placement offer at the same company where they previously interned. Display Roll_No, Full Name, Company_Name, Intern Role, Placed Role, and Package.

### 1. Correct Executable SQL Query
```sql
SELECT DISTINCT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       c.Company_Name, i.Role AS Intern_Role, p.Role AS Placed_Role, p.Package
FROM STUDENT s
JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
JOIN PLACEMENT p ON s.Student_ID = p.Student_ID AND i.Company_ID = p.Company_ID
JOIN COMPANY c ON i.Company_ID = c.Company_ID
ORDER BY p.Package DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT DISTINCT s.Roll_No, ..., c.Company_Name, i.Role AS Intern_Role, p.Role AS Placed_Role, p.Package `
  * **Explanation:** Projects candidate credentials, employer, roles, and compensation.
- ` FROM STUDENT s `
  * **Explanation:** Master student entity.
- ` JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID `
  * **Explanation:** Attaches student internships.
- ` JOIN PLACEMENT p ON s.Student_ID = p.Student_ID AND i.Company_ID = p.Company_ID `
  * **Explanation:** Critical multi-condition join: matches BOTH student ID and identical company ID.
- ` JOIN COMPANY c ON i.Company_ID = c.Company_ID `
  * **Explanation:** Resolves corporate employer name.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, INTERNSHIP, PLACEMENT, COMPANY`
- **Rationale:** Validates the conversion pipeline from student internship to full-time placement offer.

### 4. Key SQL Concepts Used
`4-Table Relational Co-occurrence Join, Equi-Join on Multi-Table Keys`

### 5. Expected Output Format & Sample Output
| Roll_No | Student_Name | Company_Name | Intern_Role | Placed_Role | Package |
|---|---|---|---|---|---|
| CS202201 | Rahul Sharma | Google | SWE Intern | SDE-1 | 24.00 |
| CS202205 | Aditya Sen | Microsoft | Cloud Intern | Software Eng | 21.00 |

---

## Solution 43: Students with Monotonically Improving SGPA Across Semesters 1 to 4
- **Project Area:** `Academic Records and SGPA` | **Difficulty Level:** `Difficult`
- **What the question is asking in simple terms:** Find all students whose SGPA consistently increased from Semester 1 to Semester 2, Semester 2 to Semester 3, and Semester 3 to Semester 4.

### 1. Correct Executable SQL Query
```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch,
       sr1.SGPA AS Sem_1, sr2.SGPA AS Sem_2, sr3.SGPA AS Sem_3, sr4.SGPA AS Sem_4
FROM STUDENT s
JOIN SEMESTER_RESULT sr1 ON s.Student_ID = sr1.Student_ID AND sr1.Semester = 1
JOIN SEMESTER_RESULT sr2 ON s.Student_ID = sr2.Student_ID AND sr2.Semester = 2
JOIN SEMESTER_RESULT sr3 ON s.Student_ID = sr3.Student_ID AND sr3.Semester = 3
JOIN SEMESTER_RESULT sr4 ON s.Student_ID = sr4.Student_ID AND sr4.Semester = 4
WHERE sr2.SGPA > sr1.SGPA
  AND sr3.SGPA > sr2.SGPA
  AND sr4.SGPA > sr3.SGPA
ORDER BY sr4.SGPA DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT s.Roll_No, ..., sr1.SGPA AS Sem_1, sr2.SGPA AS Sem_2, ... `
  * **Explanation:** Projects student identity and individual semester SGPA scores.
- ` FROM STUDENT s JOIN SEMESTER_RESULT sr1 ... JOIN SEMESTER_RESULT sr2 ... JOIN SEMESTER_RESULT sr3 ... JOIN SEMESTER_RESULT sr4 ... `
  * **Explanation:** 4-way self-join on SEMESTER_RESULT isolating Semesters 1, 2, 3, and 4 for the same student.
- ` WHERE sr2.SGPA > sr1.SGPA AND sr3.SGPA > sr2.SGPA AND sr4.SGPA > sr3.SGPA `
  * **Explanation:** Enforces strict monotonic progression (each semester score is higher than the previous).

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, SEMESTER_RESULT`
- **Rationale:** Pivots multiple normalized semester result rows into columns using self-joins.

### 4. Key SQL Concepts Used
`Self-Joins on SEMESTER_RESULT, Temporal Monotonicity Analysis`

### 5. Expected Output Format & Sample Output
| Roll_No | Student_Name | Branch | Sem_1 | Sem_2 | Sem_3 | Sem_4 |
|---|---|---|---|---|---|---|
| CS202208 | Ananya Ray | CSE | 7.80 | 8.20 | 8.65 | 9.10 |

---

## Solution 44: Year-over-Year (YoY) Percentage Growth in Placements Using LAG()
- **Project Area:** `Salary and Package Analysis` | **Difficulty Level:** `Difficult`
- **What the question is asking in simple terms:** Calculate the total placement offers in each year and use the LAG() window function to calculate the percentage growth compared to the previous year.

### 1. Correct Executable SQL Query
```sql
WITH YearlyStats AS (
    SELECT Placement_Year, COUNT(*) AS Total_Offers, ROUND(AVG(Package), 2) AS Avg_Package
    FROM PLACEMENT
    GROUP BY Placement_Year
)
SELECT Placement_Year, Total_Offers, Avg_Package,
       LAG(Total_Offers, 1) OVER (ORDER BY Placement_Year ASC) AS Previous_Year_Offers,
       ROUND((Total_Offers - LAG(Total_Offers, 1) OVER (ORDER BY Placement_Year ASC)) * 100.0 / 
             LAG(Total_Offers, 1) OVER (ORDER BY Placement_Year ASC), 2) AS YoY_Growth_Pct
FROM YearlyStats
ORDER BY Placement_Year ASC;
```

### 2. Line-by-Line Query Explanation
- ` WITH YearlyStats AS (... GROUP BY Placement_Year) `
  * **Explanation:** CTE aggregates totals by year.
- ` LAG(Total_Offers, 1) OVER (ORDER BY Placement_Year ASC) AS Previous_Year_Offers `
  * **Explanation:** Accesses the Total_Offers count from the previous chronological row.
- ` ROUND((Total_Offers - LAG(...)) * 100.0 / LAG(...), 2) AS YoY_Growth_Pct `
  * **Explanation:** Computes the relative growth rate as a percentage.
- ` ORDER BY Placement_Year ASC `
  * **Explanation:** Chronological sequence.

### 3. Tables Used and Relational Rationale
- **Tables:** `PLACEMENT`
- **Rationale:** Evaluates institutional growth trajectory over the PLACEMENT table.

### 4. Key SQL Concepts Used
`Common Table Expression (WITH), Window Function (LAG), Arithmetic in SQL, ROUND`

### 5. Expected Output Format & Sample Output
| Placement_Year | Total_Offers | Avg_Package | Previous_Year_Offers | YoY_Growth_Pct |
|---|---|---|---|---|
| 2022 | 22 | 8.90 | NULL | NULL |
| 2023 | 28 | 10.40 | 22 | 27.27 |
| 2024 | 35 | 11.80 | 28 | 25.00 |

---

## Solution 45: Drive Eligibility Verification: Students Matching Opportunity Cutoffs
- **Project Area:** `Internship Eligibility` | **Difficulty Level:** `Difficult`
- **What the question is asking in simple terms:** For Opportunity_ID = 1, find all students who meet all specified cutoff criteria: minimum CGPA, maximum backlogs, and branch eligibility.

### 1. Correct Executable SQL Query
```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.CGPA, s.Backlogs, o.Role, o.Package_Stipend
FROM STUDENT s
JOIN ELIGIBILITY_BRANCH eb ON s.Branch = eb.Branch
JOIN ELIGIBILITY e ON eb.Eligibility_ID = e.Eligibility_ID
JOIN OPPORTUNITY o ON e.Opportunity_ID = o.Opportunity_ID
WHERE o.Opportunity_ID = 1
  AND s.CGPA >= e.Minimum_CGPA
  AND s.Backlogs <= e.Max_Backlogs
ORDER BY s.CGPA DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT s.Roll_No, ..., o.Role, o.Package_Stipend `
  * **Explanation:** Projects candidate credentials and opening terms.
- ` FROM STUDENT s JOIN ELIGIBILITY_BRANCH eb ON s.Branch = eb.Branch ... `
  * **Explanation:** Joins candidate with department eligibility registry.
- ` JOIN ELIGIBILITY e ON eb.Eligibility_ID = e.Eligibility_ID `
  * **Explanation:** Attaches opportunity eligibility cutoff specifications.
- ` JOIN OPPORTUNITY o ON e.Opportunity_ID = o.Opportunity_ID `
  * **Explanation:** Attaches specific recruitment opening.
- ` WHERE o.Opportunity_ID = 1 AND s.CGPA >= e.Minimum_CGPA AND s.Backlogs <= e.Max_Backlogs `
  * **Explanation:** Enforces all 3 cutoff checks: opening match, CGPA threshold, and backlog maximum.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, OPPORTUNITY, ELIGIBILITY, ELIGIBILITY_BRANCH`
- **Rationale:** Simulates the core campus recruitment drive candidate shortlisting engine.

### 4. Key SQL Concepts Used
`INNER JOIN, Multi-Condition Relational Filtering, Business Rule Enforcement`

### 5. Expected Output Format & Sample Output
| Roll_No | Student_Name | Branch | CGPA | Backlogs | Role | Package_Stipend |
|---|---|---|---|---|---|---|
| CS202201 | Rahul Sharma | CSE | 9.45 | 0 | SDE-1 | 18.00 |
| CS202204 | Diya Sen | CSE | 8.90 | 0 | SDE-1 | 18.00 |

---

## Solution 46: Comprehensive Student 360-Degree Profile Synthesis
- **Project Area:** `Student Information` | **Difficulty Level:** `Difficult`
- **What the question is asking in simple terms:** Construct a full 360-degree profile for Student_ID = 1 consolidating roll number, name, branch, CGPA, total phone numbers, total skills, comma-separated skill list, total placements, and total internships.

### 1. Correct Executable SQL Query
```sql
SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       s.Branch, s.Batch_Year, s.CGPA, s.Backlogs,
       COUNT(DISTINCT sp.Phone_No) AS Total_Phones,
       COUNT(DISTINCT sk.Skill) AS Total_Skills,
       GROUP_CONCAT(DISTINCT sk.Skill ORDER BY sk.Skill SEPARATOR ', ') AS Skills_List,
       COUNT(DISTINCT p.Placement_ID) AS Total_Placements,
       COUNT(DISTINCT i.Internship_ID) AS Total_Internships
FROM STUDENT s
LEFT JOIN STUDENT_PHONE sp ON s.Student_ID = sp.Student_ID
LEFT JOIN STUDENT_SKILL sk ON s.Student_ID = sk.Student_ID
LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
WHERE s.Student_ID = 1
GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, s.Batch_Year, s.CGPA, s.Backlogs;
```

### 2. Line-by-Line Query Explanation
- ` SELECT s.Student_ID, s.Roll_No, ..., GROUP_CONCAT(DISTINCT sk.Skill ...), COUNT(DISTINCT p.Placement_ID) ... `
  * **Explanation:** Projects scalar demographic data, concatenated multivalued skills, and distinct entity counts.
- ` FROM STUDENT s LEFT JOIN ... 4 child tables ... `
  * **Explanation:** Radiates 4 LEFT OUTER JOINs from root student master table.
- ` WHERE s.Student_ID = 1 `
  * **Explanation:** Restricts query to the target student candidate.
- ` GROUP BY s.Student_ID, ... `
  * **Explanation:** Collapses relational Cartesian product into a single comprehensive row.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, STUDENT_PHONE, STUDENT_SKILL, PLACEMENT, INTERNSHIP`
- **Rationale:** Comprehensive master profile query assembling all primary child entities.

### 4. Key SQL Concepts Used
`Multiple LEFT JOINs, GROUP_CONCAT(DISTINCT), COUNT(DISTINCT), GROUP BY`

### 5. Expected Output Format & Sample Output
| Student_ID | Roll_No | Student_Name | Branch | CGPA | Total_Phones | Total_Skills | Skills_List | Total_Placements | Total_Internships |
|---|---|---|---|---|---|---|---|---|---|
| 1 | CS202201 | Rahul Sharma | CSE | 9.45 | 2 | 4 | C++, Java, Python, SQL | 2 | 2 |

---

## Solution 47: Semester Academic Workload vs Student SGPA Performance Correlation
- **Project Area:** `Course Enrollment` | **Difficulty Level:** `Difficult`
- **What the question is asking in simple terms:** Calculate the total course credits enrolled by each student in Semester 4 and correlate it with the actual SGPA achieved in that semester.

### 1. Correct Executable SQL Query
```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch,
       SUM(c.Credits) AS Enrolled_Course_Credits,
       sr.SGPA AS Semester_4_SGPA
FROM STUDENT s
JOIN STUDENT_COURSE sc ON s.Student_ID = sc.Student_ID
JOIN COURSE c ON sc.Course_ID = c.Course_ID AND c.Semester = 4
JOIN SEMESTER_RESULT sr ON s.Student_ID = sr.Student_ID AND sr.Semester = 4
GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, sr.SGPA
ORDER BY sr.SGPA DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT s.Roll_No, ..., SUM(c.Credits) AS Enrolled_Course_Credits, sr.SGPA AS Semester_4_SGPA `
  * **Explanation:** Projects student info, sum of curriculum course credits, and recorded SGPA.
- ` FROM STUDENT s JOIN STUDENT_COURSE sc ... JOIN COURSE c ... JOIN SEMESTER_RESULT sr ... `
  * **Explanation:** 4-table join coordinating registered courses with examination result ledger.
- ` GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, sr.SGPA `
  * **Explanation:** Groups by candidate.
- ` ORDER BY sr.SGPA DESC `
  * **Explanation:** Top academic performers first.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, STUDENT_COURSE, COURSE, SEMESTER_RESULT`
- **Rationale:** Connects curriculum registrations (COURSE/STUDENT_COURSE) with exam outcomes (SEMESTER_RESULT).

### 4. Key SQL Concepts Used
`4-Table JOIN, GROUP BY, SUM(Credits), Correlation`

### 5. Expected Output Format & Sample Output
| Roll_No | Student_Name | Branch | Enrolled_Course_Credits | Semester_4_SGPA |
|---|---|---|---|---|
| CS202201 | Rahul Sharma | CSE | 24 | 9.60 |
| CS202204 | Diya Sen | CSE | 24 | 9.15 |

---

## Solution 48: Placement Salary Percentiles within Departments using NTILE(4)
- **Project Area:** `Placement Records` | **Difficulty Level:** `Difficult`
- **What the question is asking in simple terms:** Divide placement offers within each engineering branch into 4 salary quartiles (Quartile 1 = lowest 25%, Quartile 4 = top 25%) using the NTILE(4) window function.

### 1. Correct Executable SQL Query
```sql
SELECT s.Branch, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       p.Role, p.Package,
       NTILE(4) OVER (PARTITION BY s.Branch ORDER BY p.Package ASC) AS Salary_Quartile
FROM PLACEMENT p
JOIN STUDENT s ON p.Student_ID = s.Student_ID
ORDER BY s.Branch ASC, Salary_Quartile DESC, p.Package DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT s.Branch, s.Roll_No, ..., p.Role, p.Package, ... `
  * **Explanation:** Projects student and offer details.
- ` NTILE(4) OVER (PARTITION BY s.Branch ORDER BY p.Package ASC) AS Salary_Quartile `
  * **Explanation:** Partitions offers by engineering branch and divides ordered packages into 4 equal percentile buckets (1 to 4).
- ` ORDER BY s.Branch ASC, Salary_Quartile DESC, p.Package DESC `
  * **Explanation:** Sorts by department and top quartile first.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, PLACEMENT`
- **Rationale:** Statistical distribution modeling on PLACEMENT and STUDENT.

### 4. Key SQL Concepts Used
`Window Function (NTILE), PARTITION BY, Statistical Quartile Bucketing`

### 5. Expected Output Format & Sample Output
| Branch | Roll_No | Student_Name | Role | Package | Salary_Quartile |
|---|---|---|---|---|---|
| CSE | CS202201 | Rahul Sharma | SDE-1 | 24.00 | 4 |
| CSE | CS202205 | Aditya Sen | Software Eng | 21.00 | 4 |
| CSE | CS202209 | Amit Roy | Systems Eng | 5.50 | 1 |

---

## Solution 49: Corporate Hiring Yield: Ratio of Offers to Selection Rounds
- **Project Area:** `Company Information` | **Difficulty Level:** `Difficult`
- **What the question is asking in simple terms:** For each recruitment drive in 2024, calculate the total selection rounds conducted, total job opportunities posted, and total resulting placement offers.

### 1. Correct Executable SQL Query
```sql
SELECT c.Company_Name, rd.Drive_ID, rd.Season,
       COUNT(DISTINCT o.Opportunity_ID) AS Total_Opportunities,
       COUNT(DISTINCT sp.Round_ID) AS Total_Interview_Rounds,
       COUNT(DISTINCT p.Placement_ID) AS Total_Offers_Made
FROM RECRUITMENT_DRIVE rd
JOIN COMPANY c ON rd.Company_ID = c.Company_ID
LEFT JOIN OPPORTUNITY o ON rd.Drive_ID = o.Drive_ID
LEFT JOIN SELECTION_PROCESS sp ON o.Opportunity_ID = sp.Opportunity_ID
LEFT JOIN PLACEMENT p ON rd.Company_ID = p.Company_ID AND p.Placement_Year = rd.Drive_Year
WHERE rd.Drive_Year = 2024
GROUP BY c.Company_Name, rd.Drive_ID, rd.Season
ORDER BY Total_Offers_Made DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT c.Company_Name, rd.Drive_ID, rd.Season, COUNT(DISTINCT o.Opportunity_ID) ... `
  * **Explanation:** Projects drive context and calculates pipeline entity counts.
- ` FROM RECRUITMENT_DRIVE rd JOIN COMPANY c ... LEFT JOIN ... 3 child tables ... `
  * **Explanation:** Hierarchical multi-table join across drive stages.
- ` COUNT(DISTINCT ...) for each child entity `
  * **Explanation:** Prevents Cartesian multiplication across independent child branches.
- ` WHERE rd.Drive_Year = 2024 `
  * **Explanation:** Restricts to 2024 recruitment season.

### 3. Tables Used and Relational Rationale
- **Tables:** `RECRUITMENT_DRIVE, OPPORTUNITY, SELECTION_PROCESS, PLACEMENT, COMPANY`
- **Rationale:** Audits the complete hiring pipeline from drive scheduling to placement conversion.

### 4. Key SQL Concepts Used
`Multiple LEFT JOINs, COUNT(DISTINCT), Grouping Across Recruitment Hierarchy`

### 5. Expected Output Format & Sample Output
| Company_Name | Drive_ID | Season | Total_Opportunities | Total_Interview_Rounds | Total_Offers_Made |
|---|---|---|---|---|---|
| TCS | 10 | Fall | 2 | 6 | 14 |
| Google | 12 | Fall | 1 | 5 | 3 |

---

## Solution 50: Dual-Requirement Clearance Roster with Individual Requirement Status
- **Project Area:** `Mandatory Internship Completion` | **Difficulty Level:** `Difficult`
- **What the question is asking in simple terms:** Produce an administrative degree clearance report for all final-year students (Batch 2022/2023) listing their status for Mandatory Internship 1, Mandatory Internship 2, and overall Clearance Status ('Cleared' vs 'Hold').

### 1. Correct Executable SQL Query
```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.Batch_Year,
       CASE WHEN EXISTS (SELECT 1 FROM INTERNSHIP i1 WHERE i1.Student_ID = s.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = 'Mandatory') THEN 'Completed' ELSE 'Missing' END AS Mandatory_1,
       CASE WHEN EXISTS (SELECT 1 FROM INTERNSHIP i2 WHERE i2.Student_ID = s.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = 'Mandatory') THEN 'Completed' ELSE 'Missing' END AS Mandatory_2,
       CASE WHEN EXISTS (SELECT 1 FROM INTERNSHIP i1 WHERE i1.Student_ID = s.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = 'Mandatory')
             AND EXISTS (SELECT 1 FROM INTERNSHIP i2 WHERE i2.Student_ID = s.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = 'Mandatory')
            THEN 'CLEARED FOR GRADUATION' ELSE 'DEGREE HOLD' END AS Institutional_Clearance_Status
FROM STUDENT s
ORDER BY s.Batch_Year ASC, s.Branch ASC, s.Roll_No ASC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT s.Roll_No, ..., CASE WHEN EXISTS (...) THEN 'Completed' ELSE 'Missing' END AS Mandatory_1 `
  * **Explanation:** Evaluates Mandatory Internship #1.
- ` CASE WHEN EXISTS (...) THEN 'Completed' ELSE 'Missing' END AS Mandatory_2 `
  * **Explanation:** Evaluates Mandatory Internship #2.
- ` CASE WHEN EXISTS(...) AND EXISTS(...) THEN 'CLEARED' ELSE 'HOLD' END AS Status `
  * **Explanation:** Evaluates final overall institutional clearance.
- ` FROM STUDENT s `
  * **Explanation:** Master student population.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, INTERNSHIP`
- **Rationale:** Implements the core institutional graduation clearance rule of the university.

### 4. Key SQL Concepts Used
`CASE WHEN, Correlated Subqueries, Institutional Clearance Business Logic`

### 5. Expected Output Format & Sample Output
| Roll_No | Student_Name | Branch | Batch_Year | Mandatory_1 | Mandatory_2 | Institutional_Clearance_Status |
|---|---|---|---|---|---|---|
| CS202201 | Rahul Sharma | CSE | 2022 | Completed | Completed | CLEARED FOR GRADUATION |
| CS202217 | Sneha Reddy | CSE | 2022 | Missing | Missing | DEGREE HOLD |

---

## Solution 51: Students with Packages in the Top 10% of the Entire Institution
- **Project Area:** `Salary and Package Analysis` | **Difficulty Level:** `Difficult`
- **What the question is asking in simple terms:** Find all students whose placement package ranks in the top 10% (90th percentile and above) across the entire university using the PERCENT_RANK() window function.

### 1. Correct Executable SQL Query
```sql
WITH OfferPercentiles AS (
    SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
           s.Branch, c.Company_Name, p.Role, p.Package,
           PERCENT_RANK() OVER (ORDER BY p.Package ASC) AS Package_Percentile
    FROM PLACEMENT p
    JOIN STUDENT s ON p.Student_ID = s.Student_ID
    JOIN COMPANY c ON p.Company_ID = c.Company_ID
)
SELECT Roll_No, Student_Name, Branch, Company_Name, Role, Package,
       ROUND(Package_Percentile * 100.0, 1) AS Percentile_Rank
FROM OfferPercentiles
WHERE Package_Percentile >= 0.90
ORDER BY Package DESC;
```

### 2. Line-by-Line Query Explanation
- ` WITH OfferPercentiles AS (...) `
  * **Explanation:** CTE calculating percentile position for each package.
- ` PERCENT_RANK() OVER (ORDER BY p.Package ASC) AS Package_Percentile `
  * **Explanation:** Assigns relative rank between 0.0 and 1.0 based on package.
- ` WHERE Package_Percentile >= 0.90 `
  * **Explanation:** Filters for offers ranking in the 90th percentile or higher.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, PLACEMENT, COMPANY`
- **Rationale:** Statistical percentile ranking on institutional placement compensation.

### 4. Key SQL Concepts Used
`Common Table Expression (WITH), Window Function (PERCENT_RANK), Percentile Filtering`

### 5. Expected Output Format & Sample Output
| Roll_No | Student_Name | Branch | Company_Name | Role | Package | Percentile_Rank |
|---|---|---|---|---|---|---|
| CS202201 | Rahul Sharma | CSE | Google | SDE-1 | 24.00 | 100.0 |
| CS202205 | Aditya Sen | CSE | Microsoft | Software Eng | 21.00 | 96.5 |

---

## Solution 52: Students with Both Digital Profiles and Uploaded Resumes
- **Project Area:** `Student Information` | **Difficulty Level:** `Difficult`
- **What the question is asking in simple terms:** Find all students who have registered a professional profile (LinkedIn/GitHub in STUDENT_PROFILE) AND uploaded a resume in the RESUME table, listing their profile links.

### 1. Correct Executable SQL Query
```sql
SELECT DISTINCT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch,
       sp.Profile_Type, sp.Link AS Profile_Link, r.File_Name AS Resume_File
FROM STUDENT s
JOIN STUDENT_PROFILE sp ON s.Student_ID = sp.Student_ID
JOIN RESUME r ON s.Student_ID = r.Student_ID
WHERE sp.Profile_Type IN ('LinkedIn', 'GitHub')
ORDER BY s.Roll_No ASC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT DISTINCT s.Roll_No, ..., sp.Profile_Type, sp.Link, r.File_Name `
  * **Explanation:** Projects student identity and digital links.
- ` FROM STUDENT s JOIN STUDENT_PROFILE sp ... JOIN RESUME r ... `
  * **Explanation:** Joins student with profile and resume child tables.
- ` WHERE sp.Profile_Type IN ('LinkedIn', 'GitHub') `
  * **Explanation:** Filters for verified digital engineering profiles.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, STUDENT_PROFILE, RESUME`
- **Rationale:** Combines digital footprint attributes from STUDENT_PROFILE and RESUME.

### 4. Key SQL Concepts Used
`3-Table INNER JOIN, DISTINCT, Multi-Attribute Portfolio Aggregation`

### 5. Expected Output Format & Sample Output
| Roll_No | Student_Name | Branch | Profile_Type | Profile_Link | Resume_File |
|---|---|---|---|---|---|
| CS202201 | Rahul Sharma | CSE | LinkedIn | https://linkedin.com/in/rahul | rahul_resume_2024.pdf |

---

## Solution 53: Students Who Failed Any Enrolled Course (Grade = 'F')
- **Project Area:** `Course Enrollment` | **Difficulty Level:** `Difficult`
- **What the question is asking in simple terms:** Find all students who received a failing grade ('F') in any course, showing their Roll_No, Full Name, Branch, Failed Course Name, and Semester.

### 1. Correct Executable SQL Query
```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch,
       c.Course_Name, c.Semester, sc.Grade, sc.Enrollment_Year
FROM STUDENT s
JOIN STUDENT_COURSE sc ON s.Student_ID = sc.Student_ID
JOIN COURSE c ON sc.Course_ID = c.Course_ID
WHERE sc.Grade = 'F'
ORDER BY c.Semester ASC, s.Roll_No ASC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT s.Roll_No, ..., c.Course_Name, c.Semester, sc.Grade `
  * **Explanation:** Projects student identity and failed course details.
- ` FROM STUDENT s JOIN STUDENT_COURSE sc ... JOIN COURSE c ... `
  * **Explanation:** 3-table equi-join traversing student course enrollments.
- ` WHERE sc.Grade = 'F' `
  * **Explanation:** Filters for failed coursework.

### 3. Tables Used and Relational Rationale
- **Tables:** `STUDENT, STUDENT_COURSE, COURSE`
- **Rationale:** Identifies academic backlogs at the individual course level.

### 4. Key SQL Concepts Used
`3-Table INNER JOIN, WHERE, Academic Audit`

### 5. Expected Output Format & Sample Output
| Roll_No | Student_Name | Branch | Course_Name | Semester | Grade | Enrollment_Year |
|---|---|---|---|---|---|---|
| ME202209 | Vikram Verma | ME | Thermodynamics | 3 | F | 2023 |

---

## Solution 44: Companies Recruiter Loyalty Index: Multi-Year Participating Partners
- **Project Area:** `Company Information` | **Difficulty Level:** `Difficult`
- **What the question is asking in simple terms:** Find all companies that have recruited students across 3 or more distinct calendar years, calculating total students hired and average package.

### 1. Correct Executable SQL Query
```sql
SELECT c.Company_ID, c.Company_Name, c.Industry,
       COUNT(DISTINCT p.Placement_Year) AS Years_Active,
       COUNT(p.Placement_ID) AS Total_Students_Hired,
       ROUND(AVG(p.Package), 2) AS Overall_Avg_Package
FROM COMPANY c
JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
GROUP BY c.Company_ID, c.Company_Name, c.Industry
HAVING COUNT(DISTINCT p.Placement_Year) >= 3
ORDER BY Total_Students_Hired DESC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT c.Company_ID, c.Company_Name, COUNT(DISTINCT p.Placement_Year) AS Years_Active, ... `
  * **Explanation:** Projects recruiter data, distinct recruitment years, total hires, and average CTC.
- ` FROM COMPANY c JOIN PLACEMENT p ON c.Company_ID = p.Company_ID `
  * **Explanation:** Equi-join on Company_ID.
- ` GROUP BY c.Company_ID, c.Company_Name, c.Industry `
  * **Explanation:** Groups offers by company.
- ` HAVING COUNT(DISTINCT p.Placement_Year) >= 3 `
  * **Explanation:** Enforces that the recruiter hired in at least 3 distinct calendar years.

### 3. Tables Used and Relational Rationale
- **Tables:** `COMPANY, PLACEMENT`
- **Rationale:** Analyzes recruiter institutional retention and longitudinal partnership.

### 4. Key SQL Concepts Used
`INNER JOIN, GROUP BY, HAVING, COUNT(DISTINCT Placement_Year)`

### 5. Expected Output Format & Sample Output
| Company_ID | Company_Name | Industry | Years_Active | Total_Students_Hired | Overall_Avg_Package |
|---|---|---|---|---|---|
| 2 | TCS | IT Consulting | 3 | 28 | 5.80 |
| 4 | Amazon | E-Commerce | 3 | 12 | 16.50 |

---

## Solution 55: Comprehensive Academic Transcript Summary for a Student
- **Project Area:** `Academic Records and SGPA` | **Difficulty Level:** `Difficult`
- **What the question is asking in simple terms:** Produce a complete academic transcript ledger for Student_ID = 1 displaying Semester number, SGPA, Total Credits, Cumulative Credits, and Cumulative CGPA progression across semesters.

### 1. Correct Executable SQL Query
```sql
SELECT Semester, Year, SGPA, Total_Credits,
       SUM(Total_Credits) OVER (ORDER BY Semester ASC) AS Cumulative_Credits,
       ROUND(AVG(SGPA) OVER (ORDER BY Semester ASC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS Progressive_CGPA
FROM SEMESTER_RESULT
WHERE Student_ID = 1
ORDER BY Semester ASC;
```

### 2. Line-by-Line Query Explanation
- ` SELECT Semester, Year, SGPA, Total_Credits, ... `
  * **Explanation:** Projects semester metrics.
- ` SUM(Total_Credits) OVER (ORDER BY Semester ASC) AS Cumulative_Credits `
  * **Explanation:** Computes cumulative running sum of credits earned.
- ` ROUND(AVG(SGPA) OVER (ORDER BY Semester ASC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS Progressive_CGPA `
  * **Explanation:** Computes progressive running average of SGPA to model cumulative CGPA trajectory semester by semester.
- ` WHERE Student_ID = 1 `
  * **Explanation:** Restricts to candidate.
- ` ORDER BY Semester ASC `
  * **Explanation:** Chronological sequence.

### 3. Tables Used and Relational Rationale
- **Tables:** `SEMESTER_RESULT`
- **Rationale:** Demonstrates advanced window frame specifications on academic performance.

### 4. Key SQL Concepts Used
`Window Functions, SUM() OVER (...), AVG() OVER (...), Cumulative Analytics`

### 5. Expected Output Format & Sample Output
| Semester | Year | SGPA | Total_Credits | Cumulative_Credits | Progressive_CGPA |
|---|---|---|---|---|---|
| 1 | 2021 | 9.10 | 22 | 22 | 9.10 |
| 2 | 2022 | 9.30 | 24 | 46 | 9.20 |
| 3 | 2022 | 9.50 | 24 | 70 | 9.30 |
| 4 | 2023 | 9.60 | 24 | 94 | 9.38 |

---

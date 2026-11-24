

DROP DATABASE IF EXISTS placement_db;
CREATE DATABASE placement_db;
USE placement_db;

-- =====================================================================
-- PART 1: TABLES
-- =====================================================================

-- 1. STUDENT  (Name is composite -> First_Name + Last_Name)
CREATE TABLE STUDENT (
    Student_ID   INT AUTO_INCREMENT PRIMARY KEY,
    Roll_No      VARCHAR(20)  NOT NULL UNIQUE,
    First_Name   VARCHAR(50)  NOT NULL,
    Last_Name    VARCHAR(50),
    Branch       VARCHAR(30)  NOT NULL,
    Batch_Year   SMALLINT     NOT NULL,
    CGPA         DECIMAL(4,2) NOT NULL,
    Backlogs     TINYINT      NOT NULL DEFAULT 0,
    Resume_Link  VARCHAR(255),
    CONSTRAINT chk_cgpa     CHECK (CGPA BETWEEN 0 AND 10),
    CONSTRAINT chk_backlogs CHECK (Backlogs >= 0)
);

-- 2. STUDENT_PHONE  (Phone_No is multivalued)
CREATE TABLE STUDENT_PHONE (
    Student_ID INT         NOT NULL,
    Phone_No   VARCHAR(15) NOT NULL,
    PRIMARY KEY (Student_ID, Phone_No),
    FOREIGN KEY (Student_ID) REFERENCES STUDENT(Student_ID) ON DELETE CASCADE
);

-- 3. STUDENT_SKILL  (Extra_Skills is multivalued)
CREATE TABLE STUDENT_SKILL (
    Student_ID INT         NOT NULL,
    Skill      VARCHAR(50) NOT NULL,
    PRIMARY KEY (Student_ID, Skill),
    FOREIGN KEY (Student_ID) REFERENCES STUDENT(Student_ID) ON DELETE CASCADE
);

-- 4. COMPANY
CREATE TABLE COMPANY (
    Company_ID    INT AUTO_INCREMENT PRIMARY KEY,
    Company_Name  VARCHAR(100) NOT NULL UNIQUE,
    Company_Type  ENUM('Product','Service','Startup','Other') NOT NULL DEFAULT 'Other',
    Industry      VARCHAR(50),
    Location      VARCHAR(50)
);

-- 5. PLACEMENT  (one student can have many offers; only one can be Joined = 'Yes')
CREATE TABLE PLACEMENT (
    Placement_ID     INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID       INT           NOT NULL,
    Company_ID       INT           NOT NULL,
    Role             VARCHAR(60),
    Package          DECIMAL(5,2)  NOT NULL COMMENT 'in LPA',
    Placement_Year   SMALLINT      NOT NULL,
    Placement_Type   ENUM('On-campus','Off-campus') NOT NULL DEFAULT 'On-campus',
    Is_PPO           ENUM('Yes','No') NOT NULL DEFAULT 'No',
    Joined           ENUM('Yes','No') NOT NULL DEFAULT 'No',
    Interview_Rounds TINYINT,
    -- helper column: equals Student_ID only for the joined offer, NULL otherwise.
    -- UNIQUE on it => a student can have at most ONE joined placement.
    Joined_Student   INT GENERATED ALWAYS AS (CASE WHEN Joined = 'Yes' THEN Student_ID ELSE NULL END) STORED,
    UNIQUE KEY uq_one_joined_offer (Joined_Student),
    CONSTRAINT chk_package CHECK (Package > 0),
    CONSTRAINT chk_pl_rounds CHECK (Interview_Rounds IS NULL OR Interview_Rounds >= 0),
    FOREIGN KEY (Student_ID) REFERENCES STUDENT(Student_ID),
    FOREIGN KEY (Company_ID) REFERENCES COMPANY(Company_ID)
);

-- 6. PLACEMENT_SKILL  (Selected_Skills is multivalued)
CREATE TABLE PLACEMENT_SKILL (
    Placement_ID INT         NOT NULL,
    Skill        VARCHAR(50) NOT NULL,
    PRIMARY KEY (Placement_ID, Skill),
    FOREIGN KEY (Placement_ID) REFERENCES PLACEMENT(Placement_ID) ON DELETE CASCADE
);

-- 7. INTERNSHIP  (WEAK ENTITY: PK = Student_ID + Internship_No)
--    Internship_No 1 = summer after 2nd year (report in semester 5)
--    Internship_No 2: done in 8th semester, report submitted after the end of 8th semester
--    Internship_No 3+ = additional internships
--    Duration_Months is DERIVED, so it is not stored (see V_INTERNSHIP_DETAIL).
CREATE TABLE INTERNSHIP (
    Student_ID       INT         NOT NULL,
    Internship_No    TINYINT     NOT NULL,
    Company_ID       INT         NOT NULL,
    Internship_Type  ENUM('Mandatory','Additional') NOT NULL,
    Role             VARCHAR(60),
    Interview_Rounds TINYINT,
    Stipend          DECIMAL(10,2) DEFAULT 0,
    Start_Date       DATE        NOT NULL,
    End_Date         DATE        NOT NULL,
    Credits          TINYINT,
    Report_Semester  TINYINT,
    Report_Link      VARCHAR(255),
    Report_Grade     VARCHAR(3),
    Certificate_Link VARCHAR(255),
    PRIMARY KEY (Student_ID, Internship_No),
    FOREIGN KEY (Student_ID) REFERENCES STUDENT(Student_ID) ON DELETE CASCADE,
    FOREIGN KEY (Company_ID) REFERENCES COMPANY(Company_ID),
    CONSTRAINT chk_int_no    CHECK (Internship_No >= 1),
    CONSTRAINT chk_int_dates CHECK (End_Date >= Start_Date),
    CONSTRAINT chk_int_type  CHECK ((Internship_No <= 2 AND Internship_Type = 'Mandatory')
                                 OR (Internship_No >  2 AND Internship_Type = 'Additional')),
    CONSTRAINT chk_int_report CHECK ((Internship_No = 1 AND Report_Semester = 5 AND Credits = 4)
                                  OR (Internship_No = 2 AND Report_Semester = 8 AND Credits = 4)
                                  OR (Internship_No >  2 AND Report_Semester IS NULL AND Credits IS NULL))
);

-- =====================================================================
-- PART 2: SAMPLE DATA
-- =====================================================================

INSERT INTO STUDENT (Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs, Resume_Link) VALUES
('CS2101', 'Aman',  'Sharma', 'CSE', 2024, 8.40, 0, 'https://drive.example.com/resume/aman.pdf'),
('CS2102', 'Priya', 'Verma',  'CSE', 2024, 9.10, 0, 'https://drive.example.com/resume/priya.pdf'),
('EC2103', 'Rahul', 'Singh',  'ECE', 2024, 7.60, 1, 'https://drive.example.com/resume/rahul.pdf'),
('IT2204', 'Neha',  'Gupta',  'IT',  2025, 8.80, 0, 'https://drive.example.com/resume/neha.pdf'),
('ME2105', 'Karan', 'Mehta',  'ME',  2024, 7.20, 0, 'https://drive.example.com/resume/karan.pdf');

INSERT INTO STUDENT_PHONE VALUES
(1, '9810000001'), (1, '9810000011'),
(2, '9810000002'),
(3, '9810000003'),
(4, '9810000004'), (4, '9810000044'),
(5, '9810000005');

INSERT INTO STUDENT_SKILL VALUES
(1, 'Python'), (1, 'SQL'),
(2, 'Java'), (2, 'Spring Boot'), (2, 'AWS'),
(3, 'C++'), (3, 'Embedded C'),
(4, 'React'), (4, 'Node.js'), (4, 'SQL'),
(5, 'AutoCAD');

INSERT INTO COMPANY (Company_Name, Company_Type, Industry, Location) VALUES
('TCS',       'Service', 'IT Services', 'Mumbai'),
('Zoho',      'Product', 'Software',    'Chennai'),
('Razorpay',  'Product', 'FinTech',     'Bengaluru'),
('Tata Motors','Other',  'Automobile',  'Pune');

-- Aman (1) got two offers, joined TCS (PPO). Priya (2) joined Razorpay (PPO).
-- Rahul (3) joined TCS off-campus. Neha (4) joined Zoho (PPO). Karan (5) has no placement.
INSERT INTO PLACEMENT (Student_ID, Company_ID, Role, Package, Placement_Year, Placement_Type, Is_PPO, Joined, Interview_Rounds) VALUES
(1, 1, 'Developer',               7.00, 2024, 'On-campus',  'Yes', 'Yes', 3),
(1, 2, 'Software Engineer',       9.50, 2024, 'On-campus',  'No',  'No',  4),
(2, 3, 'Backend Engineer',       14.00, 2024, 'On-campus',  'Yes', 'Yes', 5),
(3, 1, 'System Engineer',         3.60, 2024, 'Off-campus', 'No',  'Yes', 2),
(4, 2, 'Member Technical Staff',  8.50, 2025, 'On-campus',  'Yes', 'Yes', 4);

INSERT INTO PLACEMENT_SKILL VALUES
(1, 'Python'), (1, 'SQL'),
(2, 'Java'),
(3, 'Java'), (3, 'Spring Boot'),
(4, 'C++'),
(5, 'React'), (5, 'Node.js');

INSERT INTO INTERNSHIP
(Student_ID, Internship_No, Company_ID, Internship_Type, Role, Interview_Rounds, Stipend, Start_Date, End_Date, Credits, Report_Semester, Report_Link, Report_Grade, Certificate_Link) VALUES
(1, 1, 1, 'Mandatory',  'Intern',            2,  8000, '2022-06-01', '2022-07-31', 4, 5, 'https://drive.example.com/report/1-1.pdf', 'A',  'https://drive.example.com/cert/1-1.pdf'),
(1, 2, 1, 'Mandatory',  'Developer Intern',  3, 15000, '2024-01-10', '2024-05-15', 4, 8, 'https://drive.example.com/report/1-2.pdf', 'A+', 'https://drive.example.com/cert/1-2.pdf'),
(2, 1, 2, 'Mandatory',  'Intern',            2, 10000, '2022-06-01', '2022-07-15', 4, 5, 'https://drive.example.com/report/2-1.pdf', 'A',  'https://drive.example.com/cert/2-1.pdf'),
(2, 2, 3, 'Mandatory',  'Backend Intern',    4, 30000, '2024-01-10', '2024-05-15', 4, 8, 'https://drive.example.com/report/2-2.pdf', 'A+', 'https://drive.example.com/cert/2-2.pdf'),
(2, 3, 2, 'Additional', 'Winter Intern',     2, 12000, '2023-12-01', '2024-01-15', NULL, NULL, NULL, NULL, 'https://drive.example.com/cert/2-3.pdf'),
(3, 1, 1, 'Mandatory',  'Intern',            1,  5000, '2022-06-10', '2022-07-20', 4, 5, 'https://drive.example.com/report/3-1.pdf', 'B+', 'https://drive.example.com/cert/3-1.pdf'),
(3, 2, 2, 'Mandatory',  'Embedded Intern',   2,  9000, '2024-01-10', '2024-05-15', 4, 8, 'https://drive.example.com/report/3-2.pdf', 'B',  'https://drive.example.com/cert/3-2.pdf'),
(4, 1, 2, 'Mandatory',  'Intern',            2, 12000, '2023-06-01', '2023-07-31', 4, 5, 'https://drive.example.com/report/4-1.pdf', 'A',  'https://drive.example.com/cert/4-1.pdf'),
(4, 2, 2, 'Mandatory',  'Frontend Intern',   3, 18000, '2025-01-10', '2025-05-15', 4, 8, 'https://drive.example.com/report/4-2.pdf', 'A+', 'https://drive.example.com/cert/4-2.pdf'),
(5, 1, 1, 'Mandatory',  'Intern',            1,  4000, '2022-06-01', '2022-07-15', 4, 5, 'https://drive.example.com/report/5-1.pdf', 'B',  'https://drive.example.com/cert/5-1.pdf'),
(5, 2, 4, 'Mandatory',  'Design Intern',     2,  6000, '2024-01-10', '2024-05-15', 4, 8, NULL, NULL, 'https://drive.example.com/cert/5-2.pdf');

-- =====================================================================
-- PART 3: VIEWS  (ready-made joins so queries stay short)
-- =====================================================================

CREATE VIEW V_PLACEMENT_DETAIL AS
SELECT p.Placement_ID, s.Student_ID, s.Roll_No,
       CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       s.Branch, s.Batch_Year, s.CGPA, s.Backlogs,
       c.Company_ID, c.Company_Name, c.Company_Type, c.Industry, c.Location,
       p.Role, p.Package, p.Placement_Year, p.Placement_Type,
       p.Is_PPO, p.Joined, p.Interview_Rounds
FROM PLACEMENT p
JOIN STUDENT s ON s.Student_ID = p.Student_ID
JOIN COMPANY c ON c.Company_ID = p.Company_ID;

-- Duration_Months is calculated here (derived attribute), never stored.
CREATE VIEW V_INTERNSHIP_DETAIL AS
SELECT i.Student_ID, s.Roll_No,
       CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       s.Branch, s.Batch_Year,
       i.Internship_No, i.Internship_Type,
       c.Company_ID, c.Company_Name, c.Company_Type,
       i.Role, i.Interview_Rounds, i.Stipend,
       i.Start_Date, i.End_Date,
       ROUND((DATEDIFF(i.End_Date, i.Start_Date) + 1) / 30, 1) AS Duration_Months,
       i.Credits, i.Report_Semester, i.Report_Link, i.Report_Grade, i.Certificate_Link
FROM INTERNSHIP i
JOIN STUDENT s ON s.Student_ID = i.Student_ID
JOIN COMPANY c ON c.Company_ID = i.Company_ID;

-- =====================================================================
-- PART 4: QUERIES
--  (change the values such as 'CSE', 2024, 'TCS', 'CS2101' to fetch other data)
-- =====================================================================

-- ---------------------------------------------------------------------
-- A. STUDENT QUERIES
-- ---------------------------------------------------------------------

-- A1. List all students
SELECT Student_ID, Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Student_Name,
       Branch, Batch_Year, CGPA, Backlogs
FROM STUDENT
ORDER BY Batch_Year, Branch, Student_Name;

-- A2. Students of one branch and batch
SELECT Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Student_Name, CGPA
FROM STUDENT
WHERE Branch = 'CSE' AND Batch_Year = 2024
ORDER BY CGPA DESC;

-- A3. Complete profile of one student (phones and extra skills combined)
SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       s.Branch, s.Batch_Year, s.CGPA, s.Backlogs, s.Resume_Link,
       (SELECT GROUP_CONCAT(ph.Phone_No SEPARATOR ', ')
          FROM STUDENT_PHONE ph WHERE ph.Student_ID = s.Student_ID) AS Phones,
       (SELECT GROUP_CONCAT(sk.Skill SEPARATOR ', ')
          FROM STUDENT_SKILL sk WHERE sk.Student_ID = s.Student_ID) AS Extra_Skills
FROM STUDENT s
WHERE s.Roll_No = 'CS2101';

-- A4. Students who have a particular extra skill
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.CGPA
FROM STUDENT s
JOIN STUDENT_SKILL sk ON sk.Student_ID = s.Student_ID
WHERE sk.Skill = 'SQL';

-- A5. Students with high CGPA and no backlogs
SELECT Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Student_Name, Branch, CGPA
FROM STUDENT
WHERE CGPA >= 8.0 AND Backlogs = 0
ORDER BY CGPA DESC;

-- A6. Students not placed (no joined offer)
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.Batch_Year
FROM STUDENT s
WHERE NOT EXISTS (SELECT 1 FROM PLACEMENT p
                  WHERE p.Student_ID = s.Student_ID AND p.Joined = 'Yes');

-- ---------------------------------------------------------------------
-- B. PLACEMENT QUERIES
-- ---------------------------------------------------------------------

-- B1. All placed students with company and package (joined offers only)
SELECT Roll_No, Student_Name, Branch, Batch_Year, Company_Name, Role, Package, Placement_Year
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
ORDER BY Package DESC;

-- B2. Placements of one company
SELECT Student_Name, Branch, Batch_Year, Role, Package, Placement_Year, Joined
FROM V_PLACEMENT_DETAIL
WHERE Company_Name = 'TCS'
ORDER BY Placement_Year;

-- B3. Branch-wise placement statistics
SELECT Branch,
       COUNT(*)               AS Students_Placed,
       ROUND(AVG(Package), 2) AS Avg_Package,
       MAX(Package)           AS Highest_Package,
       MIN(Package)           AS Lowest_Package
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
GROUP BY Branch
ORDER BY Avg_Package DESC;

-- B4. Year-wise placement statistics
SELECT Placement_Year,
       COUNT(*)               AS Students_Placed,
       ROUND(AVG(Package), 2) AS Avg_Package,
       MAX(Package)           AS Highest_Package
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
GROUP BY Placement_Year
ORDER BY Placement_Year;

-- B5. Company-wise hiring (how many students joined each company)
SELECT Company_Name, Company_Type,
       COUNT(*)               AS Students_Joined,
       ROUND(AVG(Package), 2) AS Avg_Package,
       MAX(Package)           AS Highest_Package
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
GROUP BY Company_ID, Company_Name, Company_Type
ORDER BY Students_Joined DESC, Avg_Package DESC;

-- B6. Top 5 highest packages
SELECT Student_Name, Branch, Company_Name, Package
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
ORDER BY Package DESC
LIMIT 5;

-- B7. Placement percentage by branch and batch
--     (percentage of students stored in the database who joined a company)
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

-- B8. Students who received more than one offer (with all offers listed)
SELECT Student_Name, Roll_No,
       COUNT(*) AS Total_Offers,
       GROUP_CONCAT(CONCAT(Company_Name, ' (', Package, ' LPA)') SEPARATOR ', ') AS Offers,
       MAX(CASE WHEN Joined = 'Yes' THEN Company_Name END) AS Joined_Company
FROM V_PLACEMENT_DETAIL
GROUP BY Student_ID, Student_Name, Roll_No
HAVING COUNT(*) > 1;

-- B9. Students who got a PPO (pre-placement offer)
SELECT Student_Name, Branch, Company_Name, Package, Placement_Year, Joined
FROM V_PLACEMENT_DETAIL
WHERE Is_PPO = 'Yes'
ORDER BY Placement_Year, Package DESC;

-- B10. On-campus vs off-campus comparison
SELECT Placement_Type,
       COUNT(*)               AS Students_Placed,
       ROUND(AVG(Package), 2) AS Avg_Package
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
GROUP BY Placement_Type;

-- B11. CGPA band vs average package
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

-- B12. Placed students who had backlogs
SELECT Student_Name, Branch, Backlogs, Company_Name, Package
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes' AND Backlogs > 0;

-- B13. Average interview rounds per company (placements)
SELECT Company_Name,
       ROUND(AVG(Interview_Rounds), 1) AS Avg_Interview_Rounds,
       COUNT(*)                        AS Offers_Made
FROM V_PLACEMENT_DETAIL
GROUP BY Company_ID, Company_Name
ORDER BY Avg_Interview_Rounds DESC;

-- B14. Packages above a given amount (e.g. 8 LPA and above)
SELECT Student_Name, Branch, Company_Name, Role, Package
FROM V_PLACEMENT_DETAIL
WHERE Package >= 8 AND Joined = 'Yes'
ORDER BY Package DESC;

-- B15. Placement type, company type and industry mix of joined offers
SELECT Company_Type, Industry, COUNT(*) AS Students_Joined, ROUND(AVG(Package), 2) AS Avg_Package
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
GROUP BY Company_Type, Industry
ORDER BY Students_Joined DESC;

-- ---------------------------------------------------------------------
-- C. INTERNSHIP QUERIES
-- ---------------------------------------------------------------------

-- C1. All internships of one student (Duration_Months is calculated)
SELECT Internship_No, Internship_Type, Company_Name, Role,
       Start_Date, End_Date, Duration_Months, Stipend,
       Credits, Report_Semester, Report_Grade
FROM V_INTERNSHIP_DETAIL
WHERE Roll_No = 'CS2102'
ORDER BY Internship_No;

-- C2. All internships done at one company
SELECT Student_Name, Branch, Internship_No, Role, Start_Date, End_Date, Stipend
FROM V_INTERNSHIP_DETAIL
WHERE Company_Name = 'Zoho'
ORDER BY Start_Date;

-- C3. Mandatory internship status of every student (must be 2)
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       COUNT(CASE WHEN i.Internship_Type = 'Mandatory'  THEN 1 END) AS Mandatory_Done,
       COUNT(CASE WHEN i.Internship_Type = 'Additional' THEN 1 END) AS Additional_Done,
       COUNT(i.Internship_No)                                       AS Total_Internships
FROM STUDENT s
LEFT JOIN INTERNSHIP i ON i.Student_ID = s.Student_ID
GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name;

-- C4. RULE CHECK: students who have NOT completed both mandatory internships
--     (this is how you check the "at least 2 internships" rule; should return no rows)
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       COUNT(CASE WHEN i.Internship_Type = 'Mandatory' THEN 1 END) AS Mandatory_Done
FROM STUDENT s
LEFT JOIN INTERNSHIP i ON i.Student_ID = s.Student_ID
GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name
HAVING COUNT(CASE WHEN i.Internship_Type = 'Mandatory' THEN 1 END) < 2;

-- C5. Students who did additional (extra) internships
SELECT Student_Name, Branch, Internship_No, Company_Name, Role, Duration_Months, Stipend
FROM V_INTERNSHIP_DETAIL
WHERE Internship_Type = 'Additional';

-- C6. Average stipend per company
SELECT Company_Name,
       COUNT(*)               AS Interns,
       ROUND(AVG(Stipend), 0) AS Avg_Stipend,
       MAX(Stipend)           AS Highest_Stipend
FROM V_INTERNSHIP_DETAIL
GROUP BY Company_ID, Company_Name
ORDER BY Avg_Stipend DESC;

-- C7. Report grade distribution for the mandatory internships, batch-wise
SELECT Batch_Year, Internship_No, Report_Grade, COUNT(*) AS Students
FROM V_INTERNSHIP_DETAIL
WHERE Internship_Type = 'Mandatory' AND Report_Grade IS NOT NULL
GROUP BY Batch_Year, Internship_No, Report_Grade
ORDER BY Batch_Year, Internship_No, Report_Grade;

-- C8. Mandatory internship reports not yet submitted
SELECT Student_Name, Branch, Internship_No, Report_Semester, Company_Name
FROM V_INTERNSHIP_DETAIL
WHERE Internship_Type = 'Mandatory' AND Report_Link IS NULL;

-- C9. Total internship credits earned by each student
SELECT Roll_No, Student_Name, COALESCE(SUM(Credits), 0) AS Total_Credits
FROM V_INTERNSHIP_DETAIL
GROUP BY Student_ID, Roll_No, Student_Name
ORDER BY Total_Credits DESC;

-- C10. Internship count per student (who did more than the mandatory 2)
SELECT Roll_No, Student_Name, COUNT(*) AS Total_Internships
FROM V_INTERNSHIP_DETAIL
GROUP BY Student_ID, Roll_No, Student_Name
HAVING COUNT(*) > 2;

-- C11. Average interview rounds for internships, per company
SELECT Company_Name, ROUND(AVG(Interview_Rounds), 1) AS Avg_Interview_Rounds
FROM V_INTERNSHIP_DETAIL
GROUP BY Company_ID, Company_Name
ORDER BY Avg_Interview_Rounds DESC;

-- C12. Internships in a given date range (e.g. summer 2023)
SELECT Student_Name, Internship_No, Company_Name, Start_Date, End_Date
FROM V_INTERNSHIP_DETAIL
WHERE Start_Date >= '2023-05-01' AND End_Date <= '2023-08-31';

-- ---------------------------------------------------------------------
-- D. COMBINED QUERIES (students + internships + placements + skills)
-- ---------------------------------------------------------------------

-- D1. Internship converted to job: student placed at a company where they interned
SELECT DISTINCT p.Student_Name, p.Branch, p.Company_Name, p.Package, p.Is_PPO
FROM V_PLACEMENT_DETAIL p
JOIN INTERNSHIP i
  ON i.Student_ID = p.Student_ID AND i.Company_ID = p.Company_ID
WHERE p.Joined = 'Yes';

-- D2. Most common extra skills among students
SELECT Skill, COUNT(*) AS Students_With_Skill
FROM STUDENT_SKILL
GROUP BY Skill
ORDER BY Students_With_Skill DESC, Skill;

-- D3. Skills companies selected students for (most in-demand first)
SELECT ps.Skill, COUNT(*) AS Times_Selected_For
FROM PLACEMENT_SKILL ps
GROUP BY ps.Skill
ORDER BY Times_Selected_For DESC, ps.Skill;

-- D4. Average package of joined students, by skill they were selected for
SELECT ps.Skill, COUNT(*) AS Students, ROUND(AVG(p.Package), 2) AS Avg_Package
FROM PLACEMENT_SKILL ps
JOIN PLACEMENT p ON p.Placement_ID = ps.Placement_ID
WHERE p.Joined = 'Yes'
GROUP BY ps.Skill
ORDER BY Avg_Package DESC;

-- D5. Skills for which a particular company selects students
SELECT DISTINCT c.Company_Name, ps.Skill
FROM PLACEMENT_SKILL ps
JOIN PLACEMENT p ON p.Placement_ID = ps.Placement_ID
JOIN COMPANY c   ON c.Company_ID  = p.Company_ID
WHERE c.Company_Name = 'Zoho';

-- D6. Companies that offered both internships and placements
SELECT c.Company_Name,
       (SELECT COUNT(*) FROM INTERNSHIP i WHERE i.Company_ID = c.Company_ID) AS Interns_Taken,
       (SELECT COUNT(*) FROM PLACEMENT  p WHERE p.Company_ID = c.Company_ID) AS Offers_Made
FROM COMPANY c
WHERE EXISTS (SELECT 1 FROM INTERNSHIP i WHERE i.Company_ID = c.Company_ID)
  AND EXISTS (SELECT 1 FROM PLACEMENT  p WHERE p.Company_ID = c.Company_ID);

-- D7. Everything about one company: who interned and who got placed
SELECT 'Internship' AS Record_Type, Student_Name, Branch, Role, NULL AS Package, Stipend
FROM V_INTERNSHIP_DETAIL
WHERE Company_Name = 'TCS'
UNION ALL
SELECT 'Placement', Student_Name, Branch, Role, Package, NULL
FROM V_PLACEMENT_DETAIL
WHERE Company_Name = 'TCS'
ORDER BY Record_Type, Student_Name;

-- D8. Full career report per student: skills, internships, final placement
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

-- D9. Do students with more extra skills get higher packages?
SELECT sc.Skill_Count, COUNT(*) AS Students, ROUND(AVG(p.Package), 2) AS Avg_Package
FROM (SELECT Student_ID, COUNT(*) AS Skill_Count
        FROM STUDENT_SKILL GROUP BY Student_ID) sc
JOIN PLACEMENT p ON p.Student_ID = sc.Student_ID AND p.Joined = 'Yes'
GROUP BY sc.Skill_Count
ORDER BY sc.Skill_Count;

-- D10. Batch-wise summary (dashboard): students, placed, avg and highest package
SELECT s.Batch_Year,
       COUNT(DISTINCT s.Student_ID)                                   AS Total_Students,
       COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' THEN s.Student_ID END) AS Placed_Students,
       ROUND(AVG(CASE WHEN p.Joined = 'Yes' THEN p.Package END), 2)   AS Avg_Package,
       MAX(CASE WHEN p.Joined = 'Yes' THEN p.Package END)             AS Highest_Package
FROM STUDENT s
LEFT JOIN PLACEMENT p ON p.Student_ID = s.Student_ID
GROUP BY s.Batch_Year
ORDER BY s.Batch_Year;

-- D11. Search a student by name (partial match) with joined company and package
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       s.Branch, s.CGPA, c.Company_Name AS Joined_Company, p.Package
FROM STUDENT s
LEFT JOIN PLACEMENT p ON p.Student_ID = s.Student_ID AND p.Joined = 'Yes'
LEFT JOIN COMPANY   c ON c.Company_ID = p.Company_ID
WHERE s.First_Name LIKE '%an%' OR s.Last_Name LIKE '%an%';

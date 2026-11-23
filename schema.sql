-- ============================================================================
-- CAMPUS PLACEMENT & INTERNSHIP MANAGEMENT SYSTEM
-- Canonical 7-Table Relational Schema (Single Source of Truth)
-- Approved Relational Design:
-- 1. STUDENT
-- 2. STUDENT_PHONE
-- 3. STUDENT_SKILL
-- 4. COMPANY
-- 5. PLACEMENT
-- 6. PLACEMENT_SKILL
-- 7. INTERNSHIP
-- ============================================================================

SET FOREIGN_KEY_CHECKS = 0;

-- Drop views if they exist
DROP VIEW IF EXISTS V_PLACEMENT_DETAIL;
DROP VIEW IF EXISTS V_INTERNSHIP_DETAIL;

-- Drop tables in reverse foreign-key dependency order
DROP TABLE IF EXISTS PLACEMENT_SKILL;
DROP TABLE IF EXISTS PLACEMENT;
DROP TABLE IF EXISTS INTERNSHIP;
DROP TABLE IF EXISTS COMPANY;
DROP TABLE IF EXISTS STUDENT_SKILL;
DROP TABLE IF EXISTS STUDENT_PHONE;
DROP TABLE IF EXISTS STUDENT;

-- ============================================================================
-- 1. STUDENT TABLE
-- ============================================================================
CREATE TABLE STUDENT (
    Student_ID       INT AUTO_INCREMENT PRIMARY KEY,
    Roll_No          VARCHAR(20)   NOT NULL UNIQUE,
    First_Name       VARCHAR(50)   NOT NULL,
    Last_Name        VARCHAR(50),
    Branch           VARCHAR(50)   NOT NULL,
    Batch_Year       INT           NOT NULL,
    Section          VARCHAR(5),
    CGPA             DECIMAL(3, 2) NOT NULL,
    Backlogs         INT           NOT NULL DEFAULT 0,
    Email            VARCHAR(100)  NOT NULL UNIQUE,
    Resume_Link      VARCHAR(255),
    Date_of_Birth    DATE,
    Gender           ENUM('Male', 'Female', 'Other'),
    Personal_Email   VARCHAR(100),
    CONSTRAINT chk_student_cgpa     CHECK (CGPA >= 0.00 AND CGPA <= 10.00),
    CONSTRAINT chk_student_backlogs CHECK (Backlogs >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_student_branch_batch ON STUDENT(Branch, Batch_Year);
CREATE INDEX idx_student_cgpa ON STUDENT(CGPA);
CREATE INDEX idx_student_roll ON STUDENT(Roll_No);

-- ============================================================================
-- 2. STUDENT_PHONE TABLE (1NF Decomposition: Multi-Valued Attribute)
-- ============================================================================
CREATE TABLE STUDENT_PHONE (
    Student_ID       INT         NOT NULL,
    Phone_No         VARCHAR(15) NOT NULL,
    PRIMARY KEY (Student_ID, Phone_No),
    CONSTRAINT fk_sphone_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 3. STUDENT_SKILL TABLE (1NF Decomposition: Multi-Valued Attribute)
-- ============================================================================
CREATE TABLE STUDENT_SKILL (
    Student_ID       INT         NOT NULL,
    Skill            VARCHAR(50) NOT NULL,
    PRIMARY KEY (Student_ID, Skill),
    CONSTRAINT fk_sskill_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 4. COMPANY TABLE
-- ============================================================================
CREATE TABLE COMPANY (
    Company_ID       INT AUTO_INCREMENT PRIMARY KEY,
    Company_Name     VARCHAR(100) NOT NULL UNIQUE,
    Company_Type     ENUM('Product', 'Service', 'Startup', 'Other') NOT NULL,
    Industry         VARCHAR(100) NOT NULL,
    Location         VARCHAR(100),
    Website          VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_company_name ON COMPANY(Company_Name);

-- ============================================================================
-- 5. PLACEMENT TABLE
-- ============================================================================
-- Rules:
-- 1. Offer_Status is restricted to ('Offered', 'Accepted', 'Declined').
-- 2. Joined records whether student actually joined ('Yes', 'No').
-- 3. CHECK (Joined = 'No' OR Offer_Status = 'Accepted') - student can only join accepted offers.
-- 4. Single-accepted-offer / single-joined-offer: student can join at most one offer.
--    Enforced via Joined_Student generated column + UNIQUE KEY uq_one_joined_offer.
-- ============================================================================
CREATE TABLE PLACEMENT (
    Placement_ID     INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID       INT           NOT NULL,
    Company_ID       INT           NOT NULL,
    Role             VARCHAR(100)  NOT NULL,
    Package          DECIMAL(5, 2) NOT NULL,
    Placement_Year   INT           NOT NULL,
    Placement_Type   ENUM('On-campus', 'Off-campus', 'Pooled') NOT NULL DEFAULT 'On-campus',
    Is_PPO           ENUM('Yes', 'No') NOT NULL DEFAULT 'No',
    Joined           ENUM('Yes', 'No') NOT NULL DEFAULT 'No',
    Offer_Status     ENUM('Offered', 'Accepted', 'Declined') NOT NULL DEFAULT 'Offered',
    Interview_Rounds INT           DEFAULT 1,
    Joined_Student   INT GENERATED ALWAYS AS (CASE WHEN Joined = 'Yes' THEN Student_ID ELSE NULL END) STORED,
    CONSTRAINT fk_placement_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE RESTRICT,
    CONSTRAINT fk_placement_company FOREIGN KEY (Company_ID)
        REFERENCES COMPANY(Company_ID) ON DELETE RESTRICT,
    CONSTRAINT chk_placement_package CHECK (Package > 0),
    CONSTRAINT chk_placement_joined_status CHECK (Joined = 'No' OR Offer_Status = 'Accepted'),
    CONSTRAINT uq_one_joined_offer UNIQUE KEY (Joined_Student)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_placement_student ON PLACEMENT(Student_ID);
CREATE INDEX idx_placement_company ON PLACEMENT(Company_ID);
CREATE INDEX idx_placement_year ON PLACEMENT(Placement_Year);
CREATE INDEX idx_placement_status ON PLACEMENT(Offer_Status);

-- ============================================================================
-- 6. PLACEMENT_SKILL TABLE (Evaluated Technical Competencies per Offer)
-- ============================================================================
CREATE TABLE PLACEMENT_SKILL (
    Placement_ID     INT         NOT NULL,
    Skill            VARCHAR(50) NOT NULL,
    PRIMARY KEY (Placement_ID, Skill),
    CONSTRAINT fk_pskill_placement FOREIGN KEY (Placement_ID)
        REFERENCES PLACEMENT(Placement_ID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 7. INTERNSHIP TABLE (Weak Entity: Identifying with Student_ID + Internship_No)
-- ============================================================================
-- Institutional Curriculum Rules:
-- 1. Internship 1 (Mandatory): Summer after 2nd year, evaluated in Semester 5 (4 credits).
-- 2. Internship 2 (Mandatory): Done during 8th semester, report submitted after end of 8th semester (4 credits).
-- 3. Internship 3+ (Additional): Voluntary industry training (Credits/Report_Semester optional).
-- Enforced via CHECK constraint chk_internship_curriculum.
-- ============================================================================
CREATE TABLE INTERNSHIP (
    Internship_ID    INT AUTO_INCREMENT UNIQUE KEY,
    Student_ID       INT           NOT NULL,
    Company_ID       INT           NOT NULL,
    Internship_No    TINYINT       NOT NULL,
    Internship_Type  ENUM('Mandatory', 'Additional') NOT NULL,
    Role             VARCHAR(100)  NOT NULL,
    Interview_Rounds INT           DEFAULT 1,
    Stipend          DECIMAL(10, 2) DEFAULT 0.00,
    Start_Date       DATE          NOT NULL,
    End_Date         DATE          NOT NULL,
    Credits          INT           DEFAULT NULL,
    Report_Semester  TINYINT       DEFAULT NULL,
    Report_Link      VARCHAR(255),
    Report_Grade     VARCHAR(5),
    Certificate_Link VARCHAR(255),
    PRIMARY KEY (Student_ID, Internship_No),
    CONSTRAINT chk_int_no CHECK (Internship_No >= 1),
    CONSTRAINT chk_internship_dates CHECK (End_Date >= Start_Date),
    CONSTRAINT chk_internship_curriculum CHECK (
        (Internship_No = 1 AND Internship_Type = 'Mandatory' AND Credits = 4 AND Report_Semester = 5) OR
        (Internship_No = 2 AND Internship_Type = 'Mandatory' AND Credits = 4 AND Report_Semester = 8) OR
        (Internship_No >= 3 AND Internship_Type = 'Additional')
    ),
    CONSTRAINT fk_internship_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE RESTRICT,
    CONSTRAINT fk_internship_company FOREIGN KEY (Company_ID)
        REFERENCES COMPANY(Company_ID) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_internship_student ON INTERNSHIP(Student_ID);
CREATE INDEX idx_internship_company ON INTERNSHIP(Company_ID);
CREATE INDEX idx_internship_type ON INTERNSHIP(Internship_Type);

-- ============================================================================
-- RELATIONAL VIEWS (Zero Stored Redundancy)
-- ============================================================================

-- V_PLACEMENT_DETAIL: Denormalized placement view joining Student and Company
CREATE VIEW V_PLACEMENT_DETAIL AS
SELECT p.Placement_ID, p.Student_ID, s.Roll_No,
       CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Student_Name,
       s.Branch, s.Batch_Year, s.CGPA,
       p.Company_ID, c.Company_Name, c.Company_Type,
       p.Role, p.Package, p.Placement_Year, p.Placement_Type,
       p.Is_PPO, p.Joined, p.Offer_Status, p.Interview_Rounds
FROM PLACEMENT p
JOIN STUDENT s ON p.Student_ID = s.Student_ID
JOIN COMPANY c ON p.Company_ID = c.Company_ID;

-- V_INTERNSHIP_DETAIL: Computes Duration_Months dynamically using DATEDIFF
CREATE VIEW V_INTERNSHIP_DETAIL AS
SELECT i.Internship_ID, i.Student_ID, s.Roll_No,
       CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Student_Name,
       s.Branch, s.Batch_Year,
       i.Company_ID, c.Company_Name,
       i.Internship_No, i.Internship_Type, i.Role,
       i.Start_Date, i.End_Date,
       ROUND(DATEDIFF(i.End_Date, i.Start_Date) / 30.44, 1) AS Duration_Months,
       i.Stipend,
       i.Credits, i.Report_Semester, i.Report_Link, i.Report_Grade, i.Certificate_Link
FROM INTERNSHIP i
JOIN STUDENT s ON i.Student_ID = s.Student_ID
JOIN COMPANY c ON i.Company_ID = c.Company_ID;

SET FOREIGN_KEY_CHECKS = 1;

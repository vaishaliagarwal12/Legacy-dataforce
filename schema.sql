-- ============================================================================
-- CAMPUS PLACEMENT & INTERNSHIP MANAGEMENT SYSTEM
-- Relational Database Schema Definition (schema.sql)
-- Target RDBMS: MySQL 8.0+ / InnoDB Engine
-- Approved 7-Table Relational Schema Architecture:
-- 1. STUDENT
-- 2. STUDENT_PHONE
-- 3. STUDENT_SKILL
-- 4. COMPANY
-- 5. PLACEMENT
-- 6. PLACEMENT_SKILL
-- 7. INTERNSHIP
-- ============================================================================

SET FOREIGN_KEY_CHECKS = 0;

-- Drop existing views if present
DROP VIEW IF EXISTS V_INTERNSHIP_DETAIL;
DROP VIEW IF EXISTS V_PLACEMENT_DETAIL;

-- Clean teardown of existing schema (in reverse dependency order)
DROP TABLE IF EXISTS PLACEMENT_SKILL;
DROP TABLE IF EXISTS PLACEMENT;
DROP TABLE IF EXISTS INTERNSHIP;
DROP TABLE IF EXISTS STUDENT_SKILL;
DROP TABLE IF EXISTS STUDENT_PHONE;
DROP TABLE IF EXISTS COMPANY;
DROP TABLE IF EXISTS STUDENT;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- 1. STUDENT MASTER TABLE
-- ============================================================================
-- Name is decomposed into First_Name and Last_Name for 1NF compliance.
-- Roll_No is an alternate unique candidate key.
CREATE TABLE STUDENT (
    Student_ID      INT AUTO_INCREMENT PRIMARY KEY,
    Roll_No         VARCHAR(20)  NOT NULL UNIQUE,
    First_Name      VARCHAR(50)  NOT NULL,
    Last_Name       VARCHAR(50),
    Branch          VARCHAR(30)  NOT NULL,
    Batch_Year      SMALLINT     NOT NULL,
    CGPA            DECIMAL(4,2) NOT NULL,
    Backlogs        TINYINT      NOT NULL DEFAULT 0,
    Email           VARCHAR(100) UNIQUE,
    Section         VARCHAR(5),
    Resume_Link     VARCHAR(255),
    CONSTRAINT chk_cgpa     CHECK (CGPA >= 0.00 AND CGPA <= 10.00),
    CONSTRAINT chk_backlogs CHECK (Backlogs >= 0),
    CONSTRAINT chk_batch    CHECK (Batch_Year BETWEEN 2000 AND 2100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- 2. STUDENT_PHONE TABLE (Multivalued Attribute Decomposition - 1NF)
-- ============================================================================
-- Decomposes multivalued contact numbers per student without comma-delimited strings.
CREATE TABLE STUDENT_PHONE (
    Student_ID      INT         NOT NULL,
    Phone_No        VARCHAR(20) NOT NULL,
    PRIMARY KEY (Student_ID, Phone_No),
    CONSTRAINT fk_phone_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- 3. STUDENT_SKILL TABLE (Multivalued Attribute Decomposition - 1NF)
-- ============================================================================
-- Decomposes technical and core skills possessed by a student.
CREATE TABLE STUDENT_SKILL (
    Student_ID      INT         NOT NULL,
    Skill           VARCHAR(50) NOT NULL,
    PRIMARY KEY (Student_ID, Skill),
    CONSTRAINT fk_skill_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- 4. COMPANY TABLE
-- ============================================================================
-- Participating corporate recruiters categorized by business tier / organization model.
CREATE TABLE COMPANY (
    Company_ID      INT AUTO_INCREMENT PRIMARY KEY,
    Company_Name    VARCHAR(100) NOT NULL UNIQUE,
    Company_Type    ENUM('Product', 'Service', 'Startup', 'Other') NOT NULL DEFAULT 'Other',
    Industry        VARCHAR(60),
    Location        VARCHAR(60),
    Website         VARCHAR(150)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- 5. PLACEMENT OFFERS TABLE
-- ============================================================================
-- Tracks campus and off-campus employment offers secured by students.
-- Enforces package validity (> 0 LPA) and institutional single accepted offer rule:
-- Generated column `Joined_Student` is populated ONLY when Joined = 'Yes' (or Offer_Status = 'Joined').
-- A UNIQUE index on `Joined_Student` physically enforces that a student can join at most ONE offer.
CREATE TABLE PLACEMENT (
    Placement_ID     INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID       INT           NOT NULL,
    Company_ID       INT           NOT NULL,
    Opportunity_ID   INT           NULL,
    Role             VARCHAR(80),
    Package          DECIMAL(6,2)  NOT NULL COMMENT 'CTC in LPA',
    Placement_Year   SMALLINT      NOT NULL,
    Placement_Type   ENUM('On-campus', 'Off-campus') NOT NULL DEFAULT 'On-campus',
    Is_PPO           ENUM('Yes', 'No') NOT NULL DEFAULT 'No',
    Joined           ENUM('Yes', 'No') NOT NULL DEFAULT 'No',
    Offer_Status     VARCHAR(20)   NOT NULL DEFAULT 'Offered',
    Interview_Rounds TINYINT       DEFAULT 1,
    Joined_Student   INT GENERATED ALWAYS AS (CASE WHEN Joined = 'Yes' OR Offer_Status = 'Joined' THEN Student_ID ELSE NULL END) STORED,
    UNIQUE KEY uq_one_joined_offer (Joined_Student),
    CONSTRAINT chk_package   CHECK (Package > 0.00),
    CONSTRAINT chk_pl_rounds CHECK (Interview_Rounds IS NULL OR Interview_Rounds >= 0),
    CONSTRAINT fk_placement_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE,
    CONSTRAINT fk_placement_company FOREIGN KEY (Company_ID)
        REFERENCES COMPANY(Company_ID) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- 6. PLACEMENT_SKILL TABLE (Multivalued Skills Evaluated for Placement)
-- ============================================================================
CREATE TABLE PLACEMENT_SKILL (
    Placement_ID    INT         NOT NULL,
    Skill           VARCHAR(50) NOT NULL,
    PRIMARY KEY (Placement_ID, Skill),
    CONSTRAINT fk_pskill_placement FOREIGN KEY (Placement_ID)
        REFERENCES PLACEMENT(Placement_ID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- 7. INTERNSHIP TABLE (Weak Entity Identifying with Student_ID + Internship_No)
-- ============================================================================
-- Internship_No 1 = Summer internship after 2nd year (evaluated in Semester 5, 4 credits).
-- Internship_No 2 = Summer internship after 3rd year (evaluated in Semester 7, 4 credits).
-- Internship_No 3+ = Additional voluntary internships (no academic degree credits).
-- Duration_Months is a DERIVED attribute computed in views and queries, never stored.
CREATE TABLE INTERNSHIP (
    Internship_ID    INT AUTO_INCREMENT UNIQUE KEY,
    Student_ID       INT           NOT NULL,
    Internship_No    TINYINT       NOT NULL,
    Company_ID       INT           NOT NULL,
    Opportunity_ID   INT           NULL,
    Requirement_ID   INT           NULL,
    Internship_Type  ENUM('Mandatory', 'Additional') NOT NULL,
    Role             VARCHAR(80),
    Interview_Rounds TINYINT       DEFAULT 1,
    Stipend          DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    Start_Date       DATE          NOT NULL,
    End_Date         DATE          NOT NULL,
    Credits          TINYINT       DEFAULT 4,
    Report_Semester  TINYINT,
    Report_Link      VARCHAR(255),
    Report_Grade     VARCHAR(5),
    Certificate_Link VARCHAR(255),
    PRIMARY KEY (Student_ID, Internship_No),
    CONSTRAINT chk_int_no      CHECK (Internship_No >= 1),
    CONSTRAINT chk_int_dates   CHECK (End_Date >= Start_Date),
    CONSTRAINT chk_int_stipend CHECK (Stipend >= 0.00),
    CONSTRAINT fk_internship_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE,
    CONSTRAINT fk_internship_company FOREIGN KEY (Company_ID)
        REFERENCES COMPANY(Company_ID) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- 8. INDEXES FOR HIGH-TRAFFIC SEARCH & FILTER PERFORMANCE
-- ============================================================================
CREATE INDEX idx_student_branch_batch ON STUDENT(Branch, Batch_Year);
CREATE INDEX idx_student_cgpa ON STUDENT(CGPA);
CREATE INDEX idx_student_roll ON STUDENT(Roll_No);
CREATE INDEX idx_company_name ON COMPANY(Company_Name);
CREATE INDEX idx_company_type ON COMPANY(Company_Type);
CREATE INDEX idx_placement_student ON PLACEMENT(Student_ID);
CREATE INDEX idx_placement_company ON PLACEMENT(Company_ID);
CREATE INDEX idx_placement_year ON PLACEMENT(Placement_Year);
CREATE INDEX idx_internship_student ON INTERNSHIP(Student_ID);
CREATE INDEX idx_internship_company ON INTERNSHIP(Company_ID);
CREATE INDEX idx_internship_type ON INTERNSHIP(Internship_Type);

-- ============================================================================
-- 9. RELATIONAL VIEWS (Pre-computed joins with derived attributes)
-- ============================================================================

-- V_PLACEMENT_DETAIL: Combines student profile, recruiting company, and offer package
CREATE VIEW V_PLACEMENT_DETAIL AS
SELECT p.Placement_ID, s.Student_ID, s.Roll_No,
       CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       s.Branch, s.Batch_Year, s.CGPA, s.Backlogs,
       c.Company_ID, c.Company_Name, c.Company_Type, c.Industry, c.Location,
       p.Role, p.Package, p.Placement_Year, p.Placement_Type,
       p.Is_PPO, p.Joined, p.Offer_Status, p.Interview_Rounds
FROM PLACEMENT p
JOIN STUDENT s ON s.Student_ID = p.Student_ID
JOIN COMPANY c ON c.Company_ID = p.Company_ID;

-- V_INTERNSHIP_DETAIL: Computes Duration_Months dynamically using DATEDIFF
CREATE VIEW V_INTERNSHIP_DETAIL AS
SELECT i.Internship_ID, i.Student_ID, s.Roll_No,
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

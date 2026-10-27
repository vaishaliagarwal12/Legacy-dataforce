-- ============================================================================
-- CAMPUS PLACEMENT & INTERNSHIP MANAGEMENT SYSTEM
-- Relational Database Schema Definition (schema.sql)
-- Target RDBMS: PostgreSQL 12+ / Standard Relational SQL
-- ============================================================================

-- Clean teardown of existing schema (in reverse dependency order)
DROP TABLE IF EXISTS PLACEMENT_SKILL CASCADE;
DROP TABLE IF EXISTS PLACEMENT CASCADE;
DROP TABLE IF EXISTS INTERNSHIP CASCADE;
DROP TABLE IF EXISTS INTERNSHIP_REQUIREMENT CASCADE;
DROP TABLE IF EXISTS SELECTION_PROCESS CASCADE;
DROP TABLE IF EXISTS ELIGIBILITY CASCADE;
DROP TABLE IF EXISTS OPPORTUNITY CASCADE;
DROP TABLE IF EXISTS RECRUITMENT_DRIVE CASCADE;
DROP TABLE IF EXISTS COMPANY CASCADE;
DROP TABLE IF EXISTS SEMESTER_RESULT CASCADE;
DROP TABLE IF EXISTS EDUCATION_DOCUMENT CASCADE;
DROP TABLE IF EXISTS RESUME CASCADE;
DROP TABLE IF EXISTS STUDENT_PROFILE CASCADE;
DROP TABLE IF EXISTS STUDENT_COURSE CASCADE;
DROP TABLE IF EXISTS STUDENT_SKILL CASCADE;
DROP TABLE IF EXISTS STUDENT_PHONE CASCADE;
DROP TABLE IF EXISTS STUDENT CASCADE;
DROP TABLE IF EXISTS COURSE CASCADE;
DROP TABLE IF EXISTS UNIVERSITY CASCADE;

-- ============================================================================
-- 1. UNIVERSITY & ACADEMIC CATALOG TABLES
-- ============================================================================

-- UNIVERSITY: Master table representing the academic institution
CREATE TABLE UNIVERSITY (
    University_ID   SERIAL PRIMARY KEY,
    University_Name VARCHAR(120) NOT NULL UNIQUE,
    Location        VARCHAR(100) NOT NULL,
    Established_Year INT CHECK (Established_Year BETWEEN 1800 AND 2100)
);

-- COURSE: Academic curriculum offerings mapped to the University
CREATE TABLE COURSE (
    Course_ID       SERIAL PRIMARY KEY,
    University_ID   INT NOT NULL,
    Course_Name     VARCHAR(100) NOT NULL,
    Department      VARCHAR(50)  NOT NULL,
    Semester        INT NOT NULL CHECK (Semester BETWEEN 1 AND 8),
    Credits         INT NOT NULL CHECK (Credits > 0),
    Course_Type     VARCHAR(30)  NOT NULL CHECK (Course_Type IN ('Core', 'Elective', 'Lab', 'Seminar')),
    CONSTRAINT fk_course_university FOREIGN KEY (University_ID)
        REFERENCES UNIVERSITY(University_ID) ON DELETE CASCADE,
    CONSTRAINT uq_course_dept_sem UNIQUE (University_ID, Course_Name, Semester)
);

-- ============================================================================
-- 2. STUDENT MASTER & ATTRIBUTE DECOMPOSITION TABLES
-- ============================================================================

-- STUDENT: Master student entity (Name is decomposed into First_Name and Last_Name for 1NF)
CREATE TABLE STUDENT (
    Student_ID      SERIAL PRIMARY KEY,
    Roll_No         VARCHAR(20)  NOT NULL UNIQUE,
    First_Name      VARCHAR(50)  NOT NULL,
    Last_Name       VARCHAR(50),
    Branch          VARCHAR(30)  NOT NULL,
    Batch_Year      INT          NOT NULL CHECK (Batch_Year BETWEEN 2000 AND 2100),
    Section         VARCHAR(5),
    CGPA            DECIMAL(4,2) NOT NULL CHECK (CGPA >= 0.00 AND CGPA <= 10.00),
    Backlogs        INT          NOT NULL DEFAULT 0 CHECK (Backlogs >= 0),
    Email           VARCHAR(100) NOT NULL UNIQUE,
    Resume_Link     VARCHAR(255)
);

-- STUDENT_PHONE: Multivalued attribute decomposition for Student contact numbers (1NF)
CREATE TABLE STUDENT_PHONE (
    Student_ID      INT         NOT NULL,
    Phone_No        VARCHAR(20) NOT NULL,
    PRIMARY KEY (Student_ID, Phone_No),
    CONSTRAINT fk_phone_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE
);

-- STUDENT_SKILL: Multivalued attribute decomposition for Student skillset (1NF)
CREATE TABLE STUDENT_SKILL (
    Student_ID      INT         NOT NULL,
    Skill           VARCHAR(50) NOT NULL,
    PRIMARY KEY (Student_ID, Skill),
    CONSTRAINT fk_skill_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE
);

-- STUDENT_COURSE: M:N enrollment relationship between Student and Course
CREATE TABLE STUDENT_COURSE (
    Student_ID      INT NOT NULL,
    Course_ID       INT NOT NULL,
    Enrollment_Year INT NOT NULL,
    Grade           VARCHAR(5),
    PRIMARY KEY (Student_ID, Course_ID),
    CONSTRAINT fk_sc_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE,
    CONSTRAINT fk_sc_course FOREIGN KEY (Course_ID)
        REFERENCES COURSE(Course_ID) ON DELETE CASCADE
);

-- STUDENT_PROFILE: Professional and extracurricular differentiators (Projects, Hackathons, Certifications)
CREATE TABLE STUDENT_PROFILE (
    Profile_ID        SERIAL PRIMARY KEY,
    Student_ID        INT          NOT NULL,
    Profile_Type      VARCHAR(40)  NOT NULL CHECK (Profile_Type IN ('Skill', 'Project', 'Hackathon', 'Certification', 'Competitive Coding', 'Other')),
    Title             VARCHAR(120) NOT NULL,
    Description       TEXT,
    Link              VARCHAR(255),
    Year              INT          NOT NULL CHECK (Year BETWEEN 2000 AND 2100),
    Proficiency_Level VARCHAR(30)  CHECK (Proficiency_Level IN ('Beginner', 'Intermediate', 'Advanced', 'Expert')),
    CONSTRAINT fk_profile_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE
);

-- RESUME: Resumes uploaded by students across academic cycles
CREATE TABLE RESUME (
    Resume_ID       SERIAL PRIMARY KEY,
    Student_ID      INT          NOT NULL,
    File_Name       VARCHAR(100) NOT NULL,
    File_Link       VARCHAR(255) NOT NULL,
    Upload_Date     DATE         NOT NULL DEFAULT CURRENT_DATE,
    Resume_Year     INT          NOT NULL CHECK (Resume_Year BETWEEN 2000 AND 2100),
    CONSTRAINT fk_resume_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE
);

-- EDUCATION_DOCUMENT: Supporting marksheet / verification documents associated with a Resume
CREATE TABLE EDUCATION_DOCUMENT (
    Doc_ID          SERIAL PRIMARY KEY,
    Resume_ID       INT          NOT NULL,
    Document_Type   VARCHAR(50)  NOT NULL CHECK (Document_Type IN ('10th Marksheet', '12th Marksheet', 'Diploma Certificate', 'Other')),
    Percentage_CGPA DECIMAL(5,2) NOT NULL CHECK (Percentage_CGPA > 0),
    Board           VARCHAR(80)  NOT NULL,
    Year_of_Passing INT          NOT NULL CHECK (Year_of_Passing BETWEEN 1990 AND 2100),
    File_Link       VARCHAR(255),
    CONSTRAINT fk_doc_resume FOREIGN KEY (Resume_ID)
        REFERENCES RESUME(Resume_ID) ON DELETE CASCADE
);

-- SEMESTER_RESULT: Official verified semester SGPA and credit tallies
CREATE TABLE SEMESTER_RESULT (
    Result_ID       SERIAL PRIMARY KEY,
    Student_ID      INT          NOT NULL,
    Semester        INT          NOT NULL CHECK (Semester BETWEEN 1 AND 8),
    SGPA            DECIMAL(4,2) NOT NULL CHECK (SGPA >= 0.00 AND SGPA <= 10.00),
    Year            INT          NOT NULL CHECK (Year BETWEEN 2000 AND 2100),
    Total_Credits   INT          NOT NULL CHECK (Total_Credits > 0),
    CONSTRAINT fk_result_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE,
    CONSTRAINT uq_student_semester UNIQUE (Student_ID, Semester)
);

-- ============================================================================
-- 3. COMPANY, RECRUITMENT DRIVES & OPPORTUNITIES
-- ============================================================================

-- COMPANY: Recruiting corporate organizations
CREATE TABLE COMPANY (
    Company_ID      SERIAL PRIMARY KEY,
    Company_Name    VARCHAR(100) NOT NULL UNIQUE,
    Company_Type    VARCHAR(30)  NOT NULL DEFAULT 'Other' CHECK (Company_Type IN ('Product', 'Service', 'Startup', 'PSU', 'MNC', 'Other')),
    Industry        VARCHAR(60),
    Location        VARCHAR(60),
    Website         VARCHAR(150)
);

-- RECRUITMENT_DRIVE: Campus drives conducted by companies per year/season
CREATE TABLE RECRUITMENT_DRIVE (
    Drive_ID        SERIAL PRIMARY KEY,
    Company_ID      INT          NOT NULL,
    Drive_Year      INT          NOT NULL CHECK (Drive_Year BETWEEN 2000 AND 2100),
    Drive_Type      VARCHAR(30)  NOT NULL CHECK (Drive_Type IN ('Placement', 'Internship', 'Both')),
    Season          VARCHAR(30)  NOT NULL CHECK (Season IN ('Summer', 'Winter', 'Autumn', 'Spring', 'Other')),
    Drive_Date      DATE,
    CONSTRAINT fk_drive_company FOREIGN KEY (Company_ID)
        REFERENCES COMPANY(Company_ID) ON DELETE RESTRICT
);

-- OPPORTUNITY: Specific job roles/internships opened during a recruitment drive
CREATE TABLE OPPORTUNITY (
    Opportunity_ID  SERIAL PRIMARY KEY,
    Drive_ID        INT          NOT NULL,
    Role            VARCHAR(80)  NOT NULL,
    Opportunity_Type VARCHAR(30) NOT NULL CHECK (Opportunity_Type IN ('Placement', 'Internship')),
    Package_Stipend DECIMAL(10,2) NOT NULL CHECK (Package_Stipend > 0),
    Duration_Months INT          CHECK (Duration_Months IS NULL OR Duration_Months > 0),
    CONSTRAINT fk_opportunity_drive FOREIGN KEY (Drive_ID)
        REFERENCES RECRUITMENT_DRIVE(Drive_ID) ON DELETE CASCADE
);

-- ELIGIBILITY: 1:1 criteria specification per opportunity
CREATE TABLE ELIGIBILITY (
    Eligibility_ID  SERIAL PRIMARY KEY,
    Opportunity_ID  INT          NOT NULL UNIQUE,
    Minimum_CGPA    DECIMAL(4,2) NOT NULL DEFAULT 6.00 CHECK (Minimum_CGPA BETWEEN 0.00 AND 10.00),
    Eligible_Branch VARCHAR(100) NOT NULL DEFAULT 'All Branches',
    Max_Backlogs    INT          NOT NULL DEFAULT 0 CHECK (Max_Backlogs >= 0),
    Other_Criteria  TEXT,
    CONSTRAINT fk_eligibility_opportunity FOREIGN KEY (Opportunity_ID)
        REFERENCES OPPORTUNITY(Opportunity_ID) ON DELETE CASCADE
);

-- SELECTION_PROCESS: Multi-round recruitment steps for an opportunity
CREATE TABLE SELECTION_PROCESS (
    Round_ID        SERIAL PRIMARY KEY,
    Opportunity_ID  INT          NOT NULL,
    Round_Number    INT          NOT NULL CHECK (Round_Number >= 1),
    Round_Type      VARCHAR(50)  NOT NULL CHECK (Round_Type IN ('Aptitude Test', 'Coding Round', 'Technical Interview', 'HR Interview', 'Group Discussion', 'Managerial Interview', 'Other')),
    Description     TEXT,
    CONSTRAINT fk_round_opportunity FOREIGN KEY (Opportunity_ID)
        REFERENCES OPPORTUNITY(Opportunity_ID) ON DELETE CASCADE,
    CONSTRAINT uq_opportunity_round UNIQUE (Opportunity_ID, Round_Number)
);

-- ============================================================================
-- 4. INTERNSHIP & ACADEMIC REQUIREMENTS
-- ============================================================================

-- INTERNSHIP_REQUIREMENT: Curriculum reference rules for mandatory summer internships
CREATE TABLE INTERNSHIP_REQUIREMENT (
    Requirement_ID             SERIAL PRIMARY KEY,
    Internship_No              INT          NOT NULL UNIQUE CHECK (Internship_No IN (1, 2)),
    Mandatory                  VARCHAR(5)   NOT NULL DEFAULT 'Yes' CHECK (Mandatory IN ('Yes', 'No')),
    Prescribed_Period          VARCHAR(100) NOT NULL,
    Required_Result_Semester   INT          NOT NULL CHECK (Required_Result_Semester BETWEEN 1 AND 8),
    Report_Submission_Semester INT          NOT NULL CHECK (Report_Submission_Semester BETWEEN 1 AND 8),
    Credits                    INT          NOT NULL DEFAULT 4 CHECK (Credits > 0),
    Description                TEXT
);

-- INTERNSHIP: Student internship experiences (Weak entity identifying with Student_ID + Internship_No)
CREATE TABLE INTERNSHIP (
    Internship_ID    SERIAL PRIMARY KEY,
    Student_ID       INT          NOT NULL,
    Company_ID       INT          NOT NULL,
    Opportunity_ID   INT,
    Requirement_ID   INT,
    Internship_No    INT          NOT NULL CHECK (Internship_No >= 1),
    Internship_Type  VARCHAR(30)  NOT NULL CHECK (Internship_Type IN ('Mandatory', 'Additional')),
    Role             VARCHAR(80),
    Interview_Rounds INT          DEFAULT 1 CHECK (Interview_Rounds >= 0),
    Stipend          DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (Stipend >= 0),
    Start_Date       DATE         NOT NULL,
    End_Date         DATE         NOT NULL,
    Credits          INT          CHECK (Credits IS NULL OR Credits >= 0),
    Report_Semester  INT          CHECK (Report_Semester IS NULL OR Report_Semester BETWEEN 1 AND 8),
    Report_Link      VARCHAR(255),
    Report_Grade     VARCHAR(5),
    Certificate_Link VARCHAR(255),
    CONSTRAINT fk_internship_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE,
    CONSTRAINT fk_internship_company FOREIGN KEY (Company_ID)
        REFERENCES COMPANY(Company_ID) ON DELETE RESTRICT,
    CONSTRAINT fk_internship_opportunity FOREIGN KEY (Opportunity_ID)
        REFERENCES OPPORTUNITY(Opportunity_ID) ON DELETE SET NULL,
    CONSTRAINT fk_internship_requirement FOREIGN KEY (Requirement_ID)
        REFERENCES INTERNSHIP_REQUIREMENT(Requirement_ID) ON DELETE SET NULL,
    CONSTRAINT uq_student_internship_no UNIQUE (Student_ID, Internship_No),
    CONSTRAINT chk_internship_dates CHECK (End_Date >= Start_Date),
    CONSTRAINT chk_internship_req_consistency CHECK (
        (Internship_Type = 'Mandatory' AND Requirement_ID IS NOT NULL) OR
        (Internship_Type = 'Additional' AND Requirement_ID IS NULL)
    )
);

-- ============================================================================
-- 5. PLACEMENTS & PLACEMENT SKILLS
-- ============================================================================

-- PLACEMENT: Final placement offers achieved by students
CREATE TABLE PLACEMENT (
    Placement_ID     SERIAL PRIMARY KEY,
    Student_ID       INT          NOT NULL,
    Company_ID       INT          NOT NULL,
    Opportunity_ID   INT,
    Role             VARCHAR(80),
    Package          DECIMAL(6,2) NOT NULL CHECK (Package > 0),
    Placement_Year   INT          NOT NULL CHECK (Placement_Year BETWEEN 2000 AND 2100),
    Placement_Type   VARCHAR(30)  NOT NULL DEFAULT 'On-campus' CHECK (Placement_Type IN ('On-campus', 'Off-campus')),
    Is_PPO           VARCHAR(5)   NOT NULL DEFAULT 'No' CHECK (Is_PPO IN ('Yes', 'No')),
    Joined           VARCHAR(5)   NOT NULL DEFAULT 'No' CHECK (Joined IN ('Yes', 'No')),
    Offer_Status     VARCHAR(20)  NOT NULL DEFAULT 'Offered' CHECK (Offer_Status IN ('Offered', 'Accepted', 'Joined', 'Declined')),
    Interview_Rounds INT          DEFAULT 1 CHECK (Interview_Rounds >= 0),
    CONSTRAINT fk_placement_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE,
    CONSTRAINT fk_placement_company FOREIGN KEY (Company_ID)
        REFERENCES COMPANY(Company_ID) ON DELETE RESTRICT,
    CONSTRAINT fk_placement_opportunity FOREIGN KEY (Opportunity_ID)
        REFERENCES OPPORTUNITY(Opportunity_ID) ON DELETE SET NULL
);

-- Partial Unique Index: A student can join at most ONE placement offer
CREATE UNIQUE INDEX uq_student_joined_placement
    ON PLACEMENT(Student_ID) WHERE Joined = 'Yes';

-- PLACEMENT_SKILL: Multivalued attribute decomposition for skills evaluated in placement offers
CREATE TABLE PLACEMENT_SKILL (
    Placement_ID    INT         NOT NULL,
    Skill           VARCHAR(50) NOT NULL,
    PRIMARY KEY (Placement_ID, Skill),
    CONSTRAINT fk_pskill_placement FOREIGN KEY (Placement_ID)
        REFERENCES PLACEMENT(Placement_ID) ON DELETE CASCADE
);

-- ============================================================================
-- 6. INDEXES ON FREQUENTLY SEARCHED / FILTERED COLUMNS
-- ============================================================================

-- Indexes for STUDENT searches
CREATE INDEX idx_student_branch_batch ON STUDENT(Branch, Batch_Year);
CREATE INDEX idx_student_cgpa ON STUDENT(CGPA);
CREATE INDEX idx_student_roll ON STUDENT(Roll_No);

-- Indexes for COMPANY & DRIVES
CREATE INDEX idx_company_name ON COMPANY(Company_Name);
CREATE INDEX idx_company_industry ON COMPANY(Industry);
CREATE INDEX idx_drive_year_season ON RECRUITMENT_DRIVE(Drive_Year, Season);
CREATE INDEX idx_opportunity_drive ON OPPORTUNITY(Drive_ID);
CREATE INDEX idx_opportunity_type ON OPPORTUNITY(Opportunity_Type, Package_Stipend);

-- Indexes for PLACEMENTS
CREATE INDEX idx_placement_student ON PLACEMENT(Student_ID);
CREATE INDEX idx_placement_company ON PLACEMENT(Company_ID);
CREATE INDEX idx_placement_year ON PLACEMENT(Placement_Year);
CREATE INDEX idx_placement_status ON PLACEMENT(Offer_Status, Joined);

-- Indexes for INTERNSHIPS
CREATE INDEX idx_internship_student ON INTERNSHIP(Student_ID);
CREATE INDEX idx_internship_company ON INTERNSHIP(Company_ID);
CREATE INDEX idx_internship_type ON INTERNSHIP(Internship_Type);

-- Indexes for RESULTS & PROFILES
CREATE INDEX idx_sem_result_student ON SEMESTER_RESULT(Student_ID, Semester);
CREATE INDEX idx_student_profile_type ON STUDENT_PROFILE(Student_ID, Profile_Type);

import argparse
import logging
import re
import sys
from db.connection import get_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("init_mysql")

TEARDOWN_SQL = """
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS PLACEMENT_SKILL;
DROP TABLE IF EXISTS PLACEMENT;
DROP TABLE IF EXISTS INTERNSHIP;
DROP TABLE IF EXISTS INTERNSHIP_REQUIREMENT;
DROP TABLE IF EXISTS SELECTION_PROCESS;
DROP TABLE IF EXISTS ELIGIBILITY_BRANCH;
DROP TABLE IF EXISTS ELIGIBILITY;
DROP TABLE IF EXISTS OPPORTUNITY;
DROP TABLE IF EXISTS RECRUITMENT_DRIVE;
DROP TABLE IF EXISTS COMPANY;
DROP TABLE IF EXISTS SEMESTER_RESULT;
DROP TABLE IF EXISTS EDUCATION_DOCUMENT;
DROP TABLE IF EXISTS RESUME;
DROP TABLE IF EXISTS STUDENT_PROFILE;
DROP TABLE IF EXISTS STUDENT_COURSE;
DROP TABLE IF EXISTS STUDENT_SKILL;
DROP TABLE IF EXISTS STUDENT_PHONE;
DROP TABLE IF EXISTS STUDENT;
DROP TABLE IF EXISTS COURSE;
DROP TABLE IF EXISTS UNIVERSITY;
SET FOREIGN_KEY_CHECKS = 1;
"""

MYSQL_SCHEMA = """
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS UNIVERSITY (
    University_ID   INT AUTO_INCREMENT PRIMARY KEY,
    University_Name VARCHAR(120) NOT NULL UNIQUE,
    Location        VARCHAR(100) NOT NULL,
    Established_Year INT CHECK (Established_Year BETWEEN 1800 AND 2100)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS COURSE (
    Course_ID       INT AUTO_INCREMENT PRIMARY KEY,
    University_ID   INT NOT NULL,
    Course_Name     VARCHAR(100) NOT NULL,
    Department      VARCHAR(50)  NOT NULL,
    Semester        INT NOT NULL CHECK (Semester BETWEEN 1 AND 8),
    Credits         INT NOT NULL CHECK (Credits > 0),
    Course_Type     VARCHAR(30)  NOT NULL CHECK (Course_Type IN ('Core', 'Elective', 'Lab', 'Seminar')),
    CONSTRAINT fk_course_university FOREIGN KEY (University_ID)
        REFERENCES UNIVERSITY(University_ID) ON DELETE CASCADE,
    CONSTRAINT uq_course_dept_sem UNIQUE (University_ID, Course_Name, Semester)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS STUDENT (
    Student_ID      INT AUTO_INCREMENT PRIMARY KEY,
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
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS STUDENT_PHONE (
    Student_ID      INT         NOT NULL,
    Phone_No        VARCHAR(20) NOT NULL,
    PRIMARY KEY (Student_ID, Phone_No),
    CONSTRAINT fk_phone_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS STUDENT_SKILL (
    Student_ID      INT         NOT NULL,
    Skill           VARCHAR(50) NOT NULL,
    PRIMARY KEY (Student_ID, Skill),
    CONSTRAINT fk_skill_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS STUDENT_COURSE (
    Student_ID      INT NOT NULL,
    Course_ID       INT NOT NULL,
    Enrollment_Year INT NOT NULL,
    Grade           VARCHAR(5),
    PRIMARY KEY (Student_ID, Course_ID),
    CONSTRAINT fk_sc_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE,
    CONSTRAINT fk_sc_course FOREIGN KEY (Course_ID)
        REFERENCES COURSE(Course_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS STUDENT_PROFILE (
    Profile_ID        INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID        INT          NOT NULL,
    Profile_Type      VARCHAR(40)  NOT NULL CHECK (Profile_Type IN ('Skill', 'Project', 'Hackathon', 'Certification', 'Competitive Coding', 'Other')),
    Title             VARCHAR(120) NOT NULL,
    Description       TEXT,
    Link              VARCHAR(255),
    Year              INT          NOT NULL CHECK (Year BETWEEN 2000 AND 2100),
    Proficiency_Level VARCHAR(30)  CHECK (Proficiency_Level IN ('Beginner', 'Intermediate', 'Advanced', 'Expert')),
    CONSTRAINT fk_profile_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

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

CREATE TABLE IF NOT EXISTS EDUCATION_DOCUMENT (
    Doc_ID          INT AUTO_INCREMENT PRIMARY KEY,
    Resume_ID       INT          NOT NULL,
    Document_Type   VARCHAR(50)  NOT NULL CHECK (Document_Type IN ('10th Marksheet', '12th Marksheet', 'Diploma Certificate', 'Other')),
    Percentage_CGPA DECIMAL(5,2) NOT NULL CHECK (Percentage_CGPA > 0),
    Board           VARCHAR(80)  NOT NULL,
    Year_of_Passing INT          NOT NULL CHECK (Year_of_Passing BETWEEN 1990 AND 2100),
    File_Link       VARCHAR(255),
    CONSTRAINT fk_doc_resume FOREIGN KEY (Resume_ID)
        REFERENCES RESUME(Resume_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS SEMESTER_RESULT (
    Result_ID       INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID      INT          NOT NULL,
    Semester        INT          NOT NULL CHECK (Semester BETWEEN 1 AND 8),
    SGPA            DECIMAL(4,2) NOT NULL CHECK (SGPA >= 0.00 AND SGPA <= 10.00),
    Year            INT          NOT NULL CHECK (Year BETWEEN 2000 AND 2100),
    Total_Credits   INT          NOT NULL CHECK (Total_Credits > 0),
    CONSTRAINT fk_result_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE,
    CONSTRAINT uq_student_semester UNIQUE (Student_ID, Semester)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS COMPANY (
    Company_ID      INT AUTO_INCREMENT PRIMARY KEY,
    Company_Name    VARCHAR(100) NOT NULL UNIQUE,
    Company_Type    VARCHAR(30)  NOT NULL DEFAULT 'Other' CHECK (Company_Type IN ('Product', 'Service', 'Startup', 'PSU', 'MNC', 'Other')),
    Industry        VARCHAR(60),
    Location        VARCHAR(60),
    Website         VARCHAR(150)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS RECRUITMENT_DRIVE (
    Drive_ID        INT AUTO_INCREMENT PRIMARY KEY,
    Company_ID      INT          NOT NULL,
    Drive_Year      INT          NOT NULL CHECK (Drive_Year BETWEEN 2000 AND 2100),
    Drive_Type      VARCHAR(30)  NOT NULL CHECK (Drive_Type IN ('Placement', 'Internship', 'Both')),
    Season          VARCHAR(30)  NOT NULL CHECK (Season IN ('Summer', 'Winter', 'Autumn', 'Spring', 'Other')),
    Drive_Date      DATE,
    CONSTRAINT fk_drive_company FOREIGN KEY (Company_ID)
        REFERENCES COMPANY(Company_ID) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS OPPORTUNITY (
    Opportunity_ID  INT AUTO_INCREMENT PRIMARY KEY,
    Drive_ID        INT          NOT NULL,
    Role            VARCHAR(80)  NOT NULL,
    Opportunity_Type VARCHAR(30) NOT NULL CHECK (Opportunity_Type IN ('Placement', 'Internship')),
    Package_Stipend DECIMAL(10,2) NOT NULL CHECK (Package_Stipend > 0),
    Duration_Months INT          CHECK (Duration_Months IS NULL OR Duration_Months > 0),
    CONSTRAINT fk_opportunity_drive FOREIGN KEY (Drive_ID)
        REFERENCES RECRUITMENT_DRIVE(Drive_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ELIGIBILITY (
    Eligibility_ID  INT AUTO_INCREMENT PRIMARY KEY,
    Opportunity_ID  INT          NOT NULL UNIQUE,
    Minimum_CGPA    DECIMAL(4,2) NOT NULL DEFAULT 6.00 CHECK (Minimum_CGPA BETWEEN 0.00 AND 10.00),
    Eligible_Branch VARCHAR(100) NOT NULL DEFAULT 'All Branches',
    Max_Backlogs    INT          NOT NULL DEFAULT 0 CHECK (Max_Backlogs >= 0),
    Other_Criteria  TEXT,
    CONSTRAINT fk_eligibility_opportunity FOREIGN KEY (Opportunity_ID)
        REFERENCES OPPORTUNITY(Opportunity_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ELIGIBILITY_BRANCH (
    Eligibility_ID  INT          NOT NULL,
    Branch          VARCHAR(50)  NOT NULL,
    PRIMARY KEY (Eligibility_ID, Branch),
    CONSTRAINT fk_ebranch_eligibility FOREIGN KEY (Eligibility_ID)
        REFERENCES ELIGIBILITY(Eligibility_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS SELECTION_PROCESS (
    Round_ID        INT AUTO_INCREMENT PRIMARY KEY,
    Opportunity_ID  INT          NOT NULL,
    Round_Number    INT          NOT NULL CHECK (Round_Number >= 1),
    Round_Type      VARCHAR(50)  NOT NULL CHECK (Round_Type IN ('Aptitude Test', 'Coding Round', 'Technical Interview', 'HR Interview', 'Group Discussion', 'Managerial Interview', 'Other')),
    Description     TEXT,
    CONSTRAINT fk_round_opportunity FOREIGN KEY (Opportunity_ID)
        REFERENCES OPPORTUNITY(Opportunity_ID) ON DELETE CASCADE,
    CONSTRAINT uq_opportunity_round UNIQUE (Opportunity_ID, Round_Number)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS INTERNSHIP_REQUIREMENT (
    Requirement_ID             INT AUTO_INCREMENT PRIMARY KEY,
    Internship_No              INT          NOT NULL UNIQUE CHECK (Internship_No IN (1, 2)),
    Mandatory                  VARCHAR(5)   NOT NULL DEFAULT 'Yes' CHECK (Mandatory IN ('Yes', 'No')),
    Prescribed_Period          VARCHAR(100) NOT NULL,
    Required_Result_Semester   INT          NOT NULL CHECK (Required_Result_Semester BETWEEN 1 AND 8),
    Report_Submission_Semester INT          NOT NULL CHECK (Report_Submission_Semester BETWEEN 1 AND 8),
    Credits                    INT          NOT NULL DEFAULT 4 CHECK (Credits > 0),
    Description                TEXT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS INTERNSHIP (
    Internship_ID    INT AUTO_INCREMENT PRIMARY KEY,
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
    CONSTRAINT chk_internship_dates CHECK (End_Date >= Start_Date)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS PLACEMENT (
    Placement_ID     INT AUTO_INCREMENT PRIMARY KEY,
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
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS PLACEMENT_SKILL (
    Placement_ID    INT         NOT NULL,
    Skill           VARCHAR(50) NOT NULL,
    PRIMARY KEY (Placement_ID, Skill),
    CONSTRAINT fk_pskill_placement FOREIGN KEY (Placement_ID)
        REFERENCES PLACEMENT(Placement_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

SET FOREIGN_KEY_CHECKS = 1;
"""

SECONDARY_INDEXES = [
    ("STUDENT", "idx_student_branch_batch", "(Branch, Batch_Year)"),
    ("STUDENT", "idx_student_cgpa", "(CGPA)"),
    ("STUDENT", "idx_student_roll", "(Roll_No)"),
    ("COMPANY", "idx_company_name", "(Company_Name)"),
    ("PLACEMENT", "idx_placement_student", "(Student_ID)"),
    ("INTERNSHIP", "idx_internship_student", "(Student_ID)"),
    ("STUDENT_PROFILE", "idx_student_profile_type", "(Student_ID, Profile_Type)"),
]


def split_sql_statements(sql_text: str):
    statements = []
    current = []
    in_single_quote = False
    in_double_quote = False
    in_comment = False
    i = 0
    n = len(sql_text)
    while i < n:
        c = sql_text[i]
        if in_comment:
            if c == "\n":
                in_comment = False
            i += 1
            continue

        if not in_single_quote and not in_double_quote:
            if c == "-" and i + 1 < n and sql_text[i + 1] == "-":
                in_comment = True
                i += 2
                continue
            if c == ";":
                stmt = "".join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []
                i += 1
                continue

        if c == "'" and not in_double_quote:
            if in_single_quote and i + 1 < n and sql_text[i + 1] == "'":
                current.append("''")
                i += 2
                continue
            in_single_quote = not in_single_quote
        elif c == '"' and not in_single_quote:
            if in_double_quote and i + 1 < n and sql_text[i + 1] == '"':
                current.append('""')
                i += 2
                continue
            in_double_quote = not in_double_quote

        current.append(c)
        i += 1

    stmt = "".join(current).strip()
    if stmt:
        statements.append(stmt)
    return statements


def execute_statements(conn, sql_text: str):
    statements = split_sql_statements(sql_text)
    with conn.cursor() as cur:
        for stmt in statements:
            cleaned = stmt.strip()
            if not cleaned or cleaned.upper() in ("BEGIN", "COMMIT"):
                continue
            cur.execute(cleaned)


def ensure_indexes(conn):
    with conn.cursor() as cur:
        for table_name, index_name, columns in SECONDARY_INDEXES:
            cur.execute("""
                SELECT COUNT(*) AS cnt 
                FROM information_schema.statistics 
                WHERE table_schema = DATABASE() 
                  AND table_name = %s 
                  AND index_name = %s
            """, (table_name.lower(), index_name))
            row = cur.fetchone()
            if row["cnt"] == 0:
                try:
                    cur.execute(f"CREATE INDEX {index_name} ON {table_name}{columns};")
                    logger.info("Created index %s on %s%s", index_name, table_name, columns)
                except Exception as err:
                    logger.warning("Could not create index %s: %s", index_name, err)
            else:
                logger.info("Index %s already exists on %s. Skipped.", index_name, table_name)


def init(reset: bool = False):
    with get_connection() as conn:
        if reset:
            logger.warning("RESET flag specified. Dropping all tables...")
            execute_statements(conn, TEARDOWN_SQL)
            conn.commit()
            logger.info("Tables dropped cleanly.")

        logger.info("Ensuring all tables exist (non-destructive)...")
        execute_statements(conn, MYSQL_SCHEMA)
        conn.commit()

        logger.info("Ensuring all secondary indexes exist...")
        ensure_indexes(conn)
        conn.commit()
        logger.info("Schema tables and indexes verified successfully.")

        if reset:
            logger.info("Loading seed.sql into empty database...")
            with open("seed.sql", "r", encoding="utf-8") as f:
                seed_content = f.read()

            with conn.cursor() as cur:
                cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            execute_statements(conn, seed_content)
            with conn.cursor() as cur:
                cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
            logger.info("Seed data loaded successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize or migrate MySQL placement_db")
    parser.add_argument("--reset", action="store_true", help="Perform destructive full reset and reload seed data")
    args = parser.parse_args()

    init(reset=args.reset)

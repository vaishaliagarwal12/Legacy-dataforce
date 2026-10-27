"""Safe, Non-Destructive Migration Script for Legacy Dataforce.

Creates any missing tables and indexes in placement_db WITHOUT dropping,
truncating, or altering existing tables or rows.
"""

import logging
from db.connection import get_connection, execute_query, execute_one

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("safe_migration")

# DDL for the 5 missing tables using IF NOT EXISTS
MISSING_TABLES_DDL = [
    # 1. SELECTION_PROCESS
    """
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
    """,
    # 2. INTERNSHIP_REQUIREMENT
    """
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
    """,
    # 3. INTERNSHIP
    """
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
    """,
    # 4. PLACEMENT
    """
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
    """,
    # 5. PLACEMENT_SKILL
    """
    CREATE TABLE IF NOT EXISTS PLACEMENT_SKILL (
        Placement_ID    INT         NOT NULL,
        Skill           VARCHAR(50) NOT NULL,
        PRIMARY KEY (Placement_ID, Skill),
        CONSTRAINT fk_pskill_placement FOREIGN KEY (Placement_ID)
            REFERENCES PLACEMENT(Placement_ID) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """,
]

SECONDARY_INDEXES = [
    ("STUDENT", "idx_student_branch_batch", "(Branch, Batch_Year)"),
    ("STUDENT", "idx_student_cgpa", "(CGPA)"),
    ("STUDENT", "idx_student_roll", "(Roll_No)"),
    ("COMPANY", "idx_company_name", "(Company_Name)"),
    ("PLACEMENT", "idx_placement_student", "(Student_ID)"),
    ("INTERNSHIP", "idx_internship_student", "(Student_ID)"),
    ("STUDENT_PROFILE", "idx_student_profile_type", "(Student_ID, Profile_Type)"),
]


def run_migration():
    """Applies the non-destructive schema additions."""
    logger.info("Connecting to MySQL placement_db...")
    with get_connection() as conn:
        with conn.cursor() as cur:
            # 1. Ensure foreign key checks enabled
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")

            # 2. Create missing tables
            for ddl in MISSING_TABLES_DDL:
                cur.execute(ddl.strip())
            conn.commit()
            logger.info("Missing tables created (or verified existing) successfully.")

            # 3. Create missing secondary indexes idempotently
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
                        conn.commit()
                        logger.info("Created index %s on %s%s", index_name, table_name, columns)
                    except Exception as err:
                        logger.warning("Could not create index %s: %s", index_name, err)
                else:
                    logger.info("Index %s already exists on %s. Skipped.", index_name, table_name)

    # 4. Verification
    all_tables = [list(t.values())[0] for t in execute_query("SHOW TABLES")]
    logger.info("Total tables in database now: %d", len(all_tables))
    logger.info("Tables list: %s", all_tables)

    # Verify PLACEMENT table exists
    placement_check = execute_one("""
        SELECT COUNT(*) AS cnt 
        FROM information_schema.tables 
        WHERE table_schema = DATABASE() AND table_name = 'placement'
    """)
    if placement_check["cnt"] > 0:
        logger.info("VERIFIED: PLACEMENT table exists and is ready!")
    else:
        logger.error("FAILED: PLACEMENT table was not detected.")


if __name__ == "__main__":
    run_migration()

# Topic-Wise SQL Revision Catalog: All Remaining 267 Backend Queries

> [!NOTE]
> **Complete Project Coverage**: This document meticulously catalogs all **267 remaining queries** from the Legacy Dataforce backend across the 9 official functional categories. Every query preserves its exact original SQL, source file, routine, relational tables, and identifies duplicate/template patterns so no query is skipped.

## Category Summary Overview

| Category | Total Backend Queries | Top 40 Master Guide | Remaining Revision Catalog |
|---|---|---|---|
| **Student management** | 40 | 1 | 39 |
| **Company management** | 21 | 2 | 19 |
| **Placement management** | 43 | 7 | 36 |
| **Internship management** | 21 | 5 | 16 |
| **Academic results** | 29 | 4 | 25 |
| **Dashboard and statistics** | 26 | 10 | 16 |
| **Compliance and eligibility** | 20 | 2 | 18 |
| **Reports and analytics** | 49 | 7 | 42 |
| **Other database operations** | 58 | 2 | 56 |
| **TOTAL** | **307** | **40** | **267** |

---

## Category: Student management (39 Queries)

> Category Focus: Systematic revision of backend routines, transaction hooks, duplicate validation patterns, and relational operations governing **student management**.

### STU-01: Create Student: Check Duplicate Roll Number
- **Source File / Routine:** `services/student_service.py` -> `create_student`
- **Purpose:** Enforces institutional uniqueness rule on Roll_No before inserting a new student.
- **Core DBMS Concepts:** Index-assisted existence check; prevents primary/unique constraint violation.
- **Pattern Note (Pre-Insert Uniqueness Check):** Reusable validation query run before INSERT transactions to prevent database collision and enforce candidate key constraints at the application layer.

```sql
SELECT Student_ID FROM STUDENT WHERE Roll_No = %s
```

### STU-02: Create Student: Check Duplicate Institutional Email
- **Source File / Routine:** `services/student_service.py` -> `create_student`
- **Purpose:** Validates that the provided email address is not already registered by another student.
- **Core DBMS Concepts:** Unique constraint pre-validation; prevents duplicate account creation.
- **Pattern Note (Pre-Insert Uniqueness Check):** Reusable validation query run before INSERT transactions to prevent database collision and enforce candidate key constraints at the application layer.

```sql
SELECT Student_ID FROM STUDENT WHERE Email = %s
```

### STU-03: Create Student: Insert Master Student Tuple
- **Source File / Routine:** `services/student_service.py` -> `create_student`
- **Purpose:** Inserts the core student entity attributes into the STUDENT table.
- **Core DBMS Concepts:** Atomic master record insertion; AUTO_INCREMENT primary key generation; CHECK constraint enforcement.
- **Pattern Note (Normalized Entity Insertion):** Parameterized single-row or bulk insert mapping sanitized form inputs to relational columns.

```sql
INSERT INTO STUDENT (
            Roll_No, First_Name, Last_Name, Branch, Batch_Year, Section,
            CGPA, Backlogs, Email, Resume_Link
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
```

### STU-04: Create Student: Insert Master Student Tuple
- **Source File / Routine:** `services/student_service.py` -> `create_student`
- **Purpose:** Inserts the core student entity attributes into the STUDENT table.
- **Core DBMS Concepts:** Atomic master record insertion; AUTO_INCREMENT primary key generation; CHECK constraint enforcement.
- **Pattern Note (Normalized Entity Insertion):** Parameterized single-row or bulk insert mapping sanitized form inputs to relational columns.

```sql
INSERT INTO STUDENT_PHONE (Student_ID, Phone_No) VALUES (%s, %s)
```

### STU-05: Create Student: Insert Master Student Tuple
- **Source File / Routine:** `services/student_service.py` -> `create_student`
- **Purpose:** Inserts the core student entity attributes into the STUDENT table.
- **Core DBMS Concepts:** Atomic master record insertion; AUTO_INCREMENT primary key generation; CHECK constraint enforcement.
- **Pattern Note (Normalized Entity Insertion):** Parameterized single-row or bulk insert mapping sanitized form inputs to relational columns.

```sql
INSERT INTO STUDENT_SKILL (Student_ID, Skill) VALUES (%s, %s)
```

### STU-06: Get Student: Query #6
- **Source File / Routine:** `services/student_service.py` -> `get_student`
- **Purpose:** Student domain database operation.
- **Core DBMS Concepts:** Relational query execution.

```sql
SELECT Student_ID, Roll_No, First_Name, Last_Name, Branch, Batch_Year,
               Section, CGPA, Backlogs, Email, Resume_Link
        FROM STUDENT
        WHERE Student_ID = %s
```

### STU-09: Get Student: Retrieve External Professional Profiles
- **Source File / Routine:** `services/student_service.py` -> `get_student`
- **Purpose:** Retrieves links to GitHub, LinkedIn, and competitive programming profiles.
- **Core DBMS Concepts:** 1:N child table retrieval; foreign key index scan; temporal ordering.

```sql
SELECT Profile_ID, Profile_Type, Title, Description, Link, Year, Proficiency_Level
        FROM STUDENT_PROFILE
        WHERE Student_ID = %s
        ORDER BY Year DESC, Profile_Type ASC
```

### STU-10: Get Student: Retrieve Technical Skills
- **Source File / Routine:** `services/student_service.py` -> `get_student`
- **Purpose:** Fetches all validated skills associated with the candidate for placement matching.
- **Core DBMS Concepts:** Child entity projection; clustered composite index scan; alphabetical sort.

```sql
SELECT Skill FROM STUDENT_SKILL WHERE Student_ID = %s ORDER BY Skill
```

### STU-12: Get Student: Retrieve Uploaded Resume Documents
- **Source File / Routine:** `services/student_service.py` -> `get_student`
- **Purpose:** Retrieves file metadata, URLs, and upload timestamps for uploaded student CVs.
- **Core DBMS Concepts:** Document metadata lookup; foreign key filtering.

```sql
SELECT Resume_ID, File_Name, File_Link, Resume_Year, Upload_Date
        FROM RESUME
        WHERE Student_ID = %s
        ORDER BY Resume_Year DESC, Upload_Date DESC
```

### STU-13: Get Student: Retrieve Educational Certificates
- **Source File / Routine:** `services/student_service.py` -> `get_student`
- **Purpose:** Fetches 10th, 12th, and Diploma verification certificates and mark percentages.
- **Core DBMS Concepts:** Academic audit verification; chronological ordering.

```sql
SELECT ed.Doc_ID, ed.Document_Type, ed.Board, ed.Percentage_CGPA, ed.Year_of_Passing, ed.File_Link,
               r.File_Name AS Attached_Resume
        FROM EDUCATION_DOCUMENT ed
        JOIN RESUME r ON ed.Resume_ID = r.Resume_ID
        WHERE r.Student_ID = %s
        ORDER BY ed.Year_of_Passing ASC
```

### STU-19: List Students: Total Count for Pagination
- **Source File / Routine:** `services/student_service.py` -> `list_students`
- **Purpose:** Computes the total number of matching student tuples under active search and multi-filter criteria.
- **Core DBMS Concepts:** Dynamic SQL query generation; parameterized WHERE predicates; aggregate COUNT(*) reduction.

```sql
SELECT COUNT(*) AS total FROM STUDENT s WHERE
```

### STU-21: Update Student: Verify Existing Record
- **Source File / Routine:** `services/student_service.py` -> `update_student`
- **Purpose:** Ensures the student record exists in the database prior to applying updates.
- **Core DBMS Concepts:** Primary key existence check.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT * FROM STUDENT WHERE Student_ID = %s
```

### STU-22: Update Student: Check Duplicate Roll Number Collision
- **Source File / Routine:** `services/student_service.py` -> `update_student`
- **Purpose:** Guarantees roll number uniqueness across all other student records.
- **Core DBMS Concepts:** Inequality filter; self-exclusion unique constraint validation.
- **Pattern Note (Pre-Insert Uniqueness Check):** Reusable validation query run before INSERT transactions to prevent database collision and enforce candidate key constraints at the application layer.

```sql
SELECT Student_ID FROM STUDENT WHERE Roll_No = %s AND Student_ID != %s
```

### STU-23: Update Student: Check Duplicate Email Collision
- **Source File / Routine:** `services/student_service.py` -> `update_student`
- **Purpose:** Guarantees institutional email uniqueness across all other student records.
- **Core DBMS Concepts:** Self-exclusion email uniqueness validation.
- **Pattern Note (Pre-Insert Uniqueness Check):** Reusable validation query run before INSERT transactions to prevent database collision and enforce candidate key constraints at the application layer.

```sql
SELECT Student_ID FROM STUDENT WHERE Email = %s AND Student_ID != %s
```

### STU-24: Update Student: Apply Master Attributes Mutation
- **Source File / Routine:** `services/student_service.py` -> `update_student`
- **Purpose:** Modifies student demographic, academic, and backlog attributes in-place.
- **Core DBMS Concepts:** In-place record mutation; clustered index write.

```sql
UPDATE STUDENT SET
```

### STU-25: Update Student: Purge Existing Phone Numbers
- **Source File / Routine:** `services/student_service.py` -> `update_student`
- **Purpose:** Removes prior contact phone numbers before inserting the revised phone roster.
- **Core DBMS Concepts:** Atomic child table purge prior to replacement.

```sql
DELETE FROM STUDENT_PHONE WHERE Student_ID = %s
```

### STU-26: Update Student: Re-Insert Updated Phone Numbers
- **Source File / Routine:** `services/student_service.py` -> `update_student`
- **Purpose:** Inserts the revised telephone numbers for the updated student.
- **Core DBMS Concepts:** Atomic child tuple insertion.

```sql
INSERT INTO STUDENT_PHONE (Student_ID, Phone_No) VALUES (%s, %s)
```

### STU-27: Update Student: Purge Existing Skills
- **Source File / Routine:** `services/student_service.py` -> `update_student`
- **Purpose:** Removes prior skill associations before inserting the updated skill roster.
- **Core DBMS Concepts:** Atomic child table purge prior to replacement.

```sql
DELETE FROM STUDENT_SKILL WHERE Student_ID = %s
```

### STU-28: Update Student: Re-Insert Updated Skills
- **Source File / Routine:** `services/student_service.py` -> `update_student`
- **Purpose:** Inserts the revised technical skill tokens for the updated student.
- **Core DBMS Concepts:** Atomic child tuple insertion.

```sql
INSERT INTO STUDENT_SKILL (Student_ID, Skill) VALUES (%s, %s)
```

### STU-29: Delete Student: Verify Existence Before Deletion
- **Source File / Routine:** `services/student_service.py` -> `delete_student`
- **Purpose:** Validates that the target student exists before performing safety checks.
- **Core DBMS Concepts:** Clustered index existence check.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Student_ID, Roll_No, First_Name, Last_Name FROM STUDENT WHERE Student_ID = %s
```

### STU-31: Delete Student: Permanently Remove Student Entity
- **Source File / Routine:** `services/student_service.py` -> `delete_student`
- **Purpose:** Deletes the student record from the database after verifying zero protected dependencies.
- **Core DBMS Concepts:** Foreign key ON DELETE CASCADE propagation; physical row deletion.
- **Pattern Note (Transactional Atomic Delete):** Standard parameterized DELETE statement executed within transaction blocks to maintain referential integrity.

```sql
DELETE FROM STUDENT WHERE Student_ID = %s
```

### STU-32: Get Student Selector Options: Dropdown Helper
- **Source File / Routine:** `services/student_service.py` -> `get_student_selector_options`
- **Purpose:** Fetches lightweight student attributes for UI selection dropdowns in placement and internship forms.
- **Core DBMS Concepts:** Lightweight projection; multi-attribute lexicographical sorting; database-driven selector.

```sql
SELECT Student_ID, Roll_No, First_Name, Last_Name, Branch, Batch_Year
        FROM STUDENT
        ORDER BY Roll_No ASC
```

### REG-12: Register Course: Verify Student Candidate
- **Source File / Routine:** `services/registration_service.py` -> `register_student_course`
- **Purpose:** Confirms student exists before enrollment.
- **Core DBMS Concepts:** Foreign key verification.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Student_ID, Roll_No FROM STUDENT WHERE Student_ID = %s
```

### PRF-22: Create Profile: Verify Student Candidate
- **Source File / Routine:** `services/profile_service.py` -> `create_profile`
- **Purpose:** Confirms student exists before adding a professional portfolio link.
- **Core DBMS Concepts:** Foreign key verification.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Student_ID FROM STUDENT WHERE Student_ID = %s
```

### PRF-23: Create Profile: Insert External Profile Link
- **Source File / Routine:** `services/profile_service.py` -> `create_profile`
- **Purpose:** Stores GitHub, LinkedIn, or portfolio link with proficiency level.
- **Core DBMS Concepts:** Child entity insertion; AUTO_INCREMENT primary key.

```sql
INSERT INTO STUDENT_PROFILE (Student_ID, Profile_Type, Title, Description, Link, Year, Proficiency_Level)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
```

### PRF-24: Get Profile: Equi-Join with Student Candidate
- **Source File / Routine:** `services/profile_service.py` -> `get_profile`
- **Purpose:** Retrieves professional profile link details with student roll number and name.
- **Core DBMS Concepts:** Relational equi-join.

```sql
SELECT sp.Profile_ID, sp.Student_ID, s.Roll_No, s.First_Name, s.Last_Name,
               sp.Profile_Type, sp.Title, sp.Description, sp.Link, sp.Year, sp.Proficiency_Level
        FROM STUDENT_PROFILE sp
        JOIN STUDENT s ON sp.Student_ID = s.Student_ID
        WHERE sp.Profile_ID = %s
```

### PRF-25: List Profiles: Directory of External Candidate Portfolios
- **Source File / Routine:** `services/profile_service.py` -> `list_profiles`
- **Purpose:** Browses all external professional profiles with candidate details.
- **Core DBMS Concepts:** Relational equi-join; temporal sorting.

```sql
SELECT sp.Profile_ID, sp.Student_ID, s.Roll_No, s.First_Name, s.Last_Name,
               sp.Profile_Type, sp.Title, sp.Description, sp.Link, sp.Year, sp.Proficiency_Level
        FROM STUDENT_PROFILE sp
        JOIN STUDENT s ON sp.Student_ID = s.Student_ID
        WHERE
```

### PRF-26: Update Profile: Verify Existing Profile
- **Source File / Routine:** `services/profile_service.py` -> `update_profile`
- **Purpose:** Confirms profile exists before update.
- **Core DBMS Concepts:** Primary key lookup.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT * FROM STUDENT_PROFILE WHERE Profile_ID = %s
```

### PRF-27: Update Profile: Mutate Portfolio Link
- **Source File / Routine:** `services/profile_service.py` -> `update_profile`
- **Purpose:** Modifies profile type, title, URL link, year, and proficiency.
- **Core DBMS Concepts:** In-place record mutation.

```sql
UPDATE STUDENT_PROFILE SET
```

### PRF-28: Delete Profile: Verify Target Existence
- **Source File / Routine:** `services/profile_service.py` -> `delete_profile`
- **Purpose:** Confirms profile exists before deletion.
- **Core DBMS Concepts:** Primary key lookup.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Profile_ID, Title FROM STUDENT_PROFILE WHERE Profile_ID = %s
```

### PRF-29: Delete Profile: Permanently Remove Portfolio
- **Source File / Routine:** `services/profile_service.py` -> `delete_profile`
- **Purpose:** Deletes external profile link from database.
- **Core DBMS Concepts:** Physical record deletion.
- **Pattern Note (Transactional Atomic Delete):** Standard parameterized DELETE statement executed within transaction blocks to maintain referential integrity.

```sql
DELETE FROM STUDENT_PROFILE WHERE Profile_ID = %s
```

### PRF-30: Add Phone: Verify Student Candidate
- **Source File / Routine:** `services/profile_service.py` -> `add_student_phone`
- **Purpose:** Confirms student exists before adding telephone number.
- **Core DBMS Concepts:** Foreign key verification.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Student_ID, Roll_No FROM STUDENT WHERE Student_ID = %s
```

### PRF-31: Add Phone: Prevent Duplicate Phone Number
- **Source File / Routine:** `services/profile_service.py` -> `add_student_phone`
- **Purpose:** Ensures the same phone number is not duplicated for the student.
- **Core DBMS Concepts:** Composite primary key uniqueness guard.
- **Pattern Note (Pre-Insert Uniqueness Check):** Reusable validation query run before INSERT transactions to prevent database collision and enforce candidate key constraints at the application layer.

```sql
SELECT * FROM STUDENT_PHONE WHERE Student_ID = %s AND Phone_No = %s
```

### PRF-32: Add Phone: Insert Multi-Valued Contact Phone Tuple
- **Source File / Routine:** `services/profile_service.py` -> `add_student_phone`
- **Purpose:** Inserts secondary phone number into child table STUDENT_PHONE.
- **Core DBMS Concepts:** 1NF multi-valued attribute insertion.
- **Pattern Note (Normalized Entity Insertion):** Parameterized single-row or bulk insert mapping sanitized form inputs to relational columns.

```sql
INSERT INTO STUDENT_PHONE (Student_ID, Phone_No) VALUES (%s, %s)
```

### PRF-33: List Phones: Verify Student Existence
- **Source File / Routine:** `services/profile_service.py` -> `list_student_phones`
- **Purpose:** Confirms student exists before listing phones.
- **Core DBMS Concepts:** Primary key lookup.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Student_ID FROM STUDENT WHERE Student_ID = %s
```

### PRF-34: List Phones: Retrieve Contact Telephone Roster
- **Source File / Routine:** `services/profile_service.py` -> `list_student_phones`
- **Purpose:** Fetches all contact telephone numbers registered for the student.
- **Core DBMS Concepts:** Child entity projection; alphabetical sort.

```sql
SELECT Phone_No FROM STUDENT_PHONE WHERE Student_ID = %s ORDER BY Phone_No
```

### PRF-35: Delete Phone: Verify Phone Existence
- **Source File / Routine:** `services/profile_service.py` -> `delete_student_phone`
- **Purpose:** Confirms phone number exists before deletion.
- **Core DBMS Concepts:** Composite key lookup.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT * FROM STUDENT_PHONE WHERE Student_ID = %s AND Phone_No = %s
```

### PRF-36: Delete Phone: Remove Contact Telephone Tuple
- **Source File / Routine:** `services/profile_service.py` -> `delete_student_phone`
- **Purpose:** Removes secondary phone number from STUDENT_PHONE table.
- **Core DBMS Concepts:** Physical record deletion on composite key.

```sql
DELETE FROM STUDENT_PHONE WHERE Student_ID = %s AND Phone_No = %s
```

### 10.16: Index Architecture & B+ Tree Metadata Inspection
- **Source File / Routine:** `schema.sql / init_mysql.py` -> `Index Health Verification`
- **Purpose:** Inspects B+ Tree indexes created on the STUDENT relation to verify index coverage, cardinality, and collation for optimized query execution.
- **Core DBMS Concepts:** Information schema inspection and secondary B+ Tree index verification.

```sql
SHOW INDEX FROM STUDENT;
```

---

## Category: Company management (19 Queries)

> Category Focus: Systematic revision of backend routines, transaction hooks, duplicate validation patterns, and relational operations governing **company management**.

### CMP-01: Create Company: Check Duplicate Company Name
- **Source File / Routine:** `services/company_service.py` -> `create_company`
- **Purpose:** Guarantees corporate recruiter uniqueness before insertion.
- **Core DBMS Concepts:** Unique constraint pre-validation; index-assisted existence check.
- **Pattern Note (Pre-Insert Uniqueness Check):** Reusable validation query run before INSERT transactions to prevent database collision and enforce candidate key constraints at the application layer.

```sql
SELECT Company_ID FROM COMPANY WHERE Company_Name = %s
```

### CMP-02: Create Company: Insert Partner Entity Tuple
- **Source File / Routine:** `services/company_service.py` -> `create_company`
- **Purpose:** Inserts a newly registered corporate recruiting partner into the COMPANY table.
- **Core DBMS Concepts:** Master entity insertion; AUTO_INCREMENT primary key; ENUM type constraint validation.
- **Pattern Note (Normalized Entity Insertion):** Parameterized single-row or bulk insert mapping sanitized form inputs to relational columns.

```sql
INSERT INTO COMPANY (Company_Name, Company_Type, Industry, Location, Website)
        VALUES (%s, %s, %s, %s, %s)
```

### CMP-03: Get Company: Retrieve Master Company Record
- **Source File / Routine:** `services/company_service.py` -> `get_company`
- **Purpose:** Retrieves master organization profile details by primary key.
- **Core DBMS Concepts:** Clustered primary key index lookup; O(1) point retrieval.

```sql
SELECT Company_ID, Company_Name, Company_Type, Industry, Location, Website FROM COMPANY WHERE Company_ID = %s
```

### CMP-04: Get Company: Retrieve Campus Recruitment Drives
- **Source File / Routine:** `services/company_service.py` -> `get_company`
- **Purpose:** Fetches all campus recruitment drives hosted by this corporate partner.
- **Core DBMS Concepts:** 1:N foreign key traversal; temporal ordering.

```sql
SELECT Drive_ID, Drive_Year, Drive_Type, Season, Drive_Date
        FROM RECRUITMENT_DRIVE
        WHERE Company_ID = %s
        ORDER BY Drive_Year DESC, Drive_Date DESC
```

### CMP-06: Get Company: Retrieve Opportunity Eligible Branches
- **Source File / Routine:** `services/company_service.py` -> `get_company`
- **Purpose:** Fetches the list of allowed engineering branches for a drive opportunity.
- **Core DBMS Concepts:** Child bridge table traversal; foreign key filtering.

```sql
SELECT Branch FROM ELIGIBILITY_BRANCH WHERE Eligibility_ID = %s ORDER BY Branch
```

### CMP-07: Get Company: Retrieve Selection Round Stages
- **Source File / Routine:** `services/company_service.py` -> `get_company`
- **Purpose:** Retrieves the sequential interview, coding, and HR rounds configured for the opportunity.
- **Core DBMS Concepts:** Sequential round ordering; foreign key scan.

```sql
SELECT Round_ID, Round_Number, Round_Type, Description FROM SELECTION_PROCESS WHERE Opportunity_ID = %s ORDER BY Round_Number ASC
```

### CMP-10: Update Company: Verify Existence
- **Source File / Routine:** `services/company_service.py` -> `update_company`
- **Purpose:** Confirms the target company exists before performing updates.
- **Core DBMS Concepts:** Primary key existence verification.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT * FROM COMPANY WHERE Company_ID = %s
```

### CMP-11: Update Company: Check Name Collision
- **Source File / Routine:** `services/company_service.py` -> `update_company`
- **Purpose:** Guarantees corporate name uniqueness across all other companies.
- **Core DBMS Concepts:** Self-exclusion unique constraint validation.

```sql
SELECT Company_ID FROM COMPANY WHERE Company_Name = %s AND Company_ID != %s
```

### CMP-12: Update Company: Apply Attribute Changes
- **Source File / Routine:** `services/company_service.py` -> `update_company`
- **Purpose:** Updates corporate category tier, industry sector, headquarters location, and website.
- **Core DBMS Concepts:** In-place record mutation; clustered index write.

```sql
UPDATE COMPANY SET
```

### CMP-13: Delete Company: Verify Target Record
- **Source File / Routine:** `services/company_service.py` -> `delete_company`
- **Purpose:** Verifies company existence prior to dependency analysis.
- **Core DBMS Concepts:** Clustered index scan.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Company_ID, Company_Name FROM COMPANY WHERE Company_ID = %s
```

### CMP-14: Delete Company: Check Drive Dependencies
- **Source File / Routine:** `services/company_service.py` -> `delete_company`
- **Purpose:** Audits dependent recruitment drives associated with the company.
- **Core DBMS Concepts:** Foreign key dependency check.

```sql
SELECT COUNT(*) AS total FROM RECRUITMENT_DRIVE WHERE Company_ID = %s
```

### CMP-16: Delete Company: Permanently Remove Entity
- **Source File / Routine:** `services/company_service.py` -> `delete_company`
- **Purpose:** Removes company entity from database after verifying zero dependent historical records.
- **Core DBMS Concepts:** Physical tuple removal; relational integrity enforcement.
- **Pattern Note (Transactional Atomic Delete):** Standard parameterized DELETE statement executed within transaction blocks to maintain referential integrity.

```sql
DELETE FROM COMPANY WHERE Company_ID = %s
```

### OPP-05: Get Opportunity: Full 3-Way Equi-Join Detail
- **Source File / Routine:** `services/opportunity_service.py` -> `get_opportunity`
- **Purpose:** Retrieves complete opportunity data with parent drive and company partner metadata.
- **Core DBMS Concepts:** Multi-table relational equi-join; complete opportunity projection.

```sql
SELECT o.Opportunity_ID, o.Drive_ID, rd.Company_ID, c.Company_Name, c.Company_Type,
               rd.Drive_Year, rd.Drive_Type, rd.Season,
               o.Role, o.Opportunity_Type, o.Package_Stipend, o.Duration_Months,
               e.Eligibility_ID, e.Minimum_CGPA, e.Max_Backlogs, e.Other_Criteria, e.Eligible_Branch
        FROM OPPORTUNITY o
        JOIN RECRUITMENT_DRIVE rd ON o.Drive_ID = rd.Drive_ID
        JOIN COMPANY c ON rd.Company_ID = c.Company_ID
        LEFT JOIN ELIGIBILITY e ON o.Opportunity_ID = e.Opportunity_ID
        WHERE o.Opportunity_ID = %s
```

### OPP-10: List Opportunities: Searchable Opportunity Directory
- **Source File / Routine:** `services/opportunity_service.py` -> `list_opportunities`
- **Purpose:** Browses all recruitment opportunities with company details and eligibility criteria.
- **Core DBMS Concepts:** Multi-table equi-join; dynamic parameterized WHERE filtering.

```sql
SELECT o.Opportunity_ID, o.Drive_ID, rd.Company_ID, c.Company_Name,
               rd.Drive_Year, o.Role, o.Opportunity_Type, o.Package_Stipend, o.Duration_Months,
               e.Eligibility_ID, e.Minimum_CGPA, e.Max_Backlogs, e.Eligible_Branch,
               COUNT(DISTINCT sp.Round_ID) AS Total_Rounds
        FROM OPPORTUNITY o
        JOIN RECRUITMENT_DRIVE rd ON o.Drive_ID = rd.Drive_ID
        JOIN COMPANY c ON rd.Company_ID = c.Company_ID
        LEFT JOIN ELIGIBILITY e ON o.Opportunity_ID = e.Opportunity_ID
        LEFT JOIN SELECTION_PROCESS sp ON o.Opportunity_ID = sp.Opportunity_ID
        WHERE
```

### DRV-18: Create Drive: Verify Corporate Recruiter
- **Source File / Routine:** `services/drive_service.py` -> `create_drive`
- **Purpose:** Confirms company partner exists before creating a recruitment drive.
- **Core DBMS Concepts:** Foreign key verification.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Company_ID FROM COMPANY WHERE Company_ID = %s
```

### DRV-19: Create Drive: Insert Recruitment Drive Record
- **Source File / Routine:** `services/drive_service.py` -> `create_drive`
- **Purpose:** Schedules a campus placement drive for an academic year, season, and date.
- **Core DBMS Concepts:** Master drive insertion; AUTO_INCREMENT primary key.

```sql
INSERT INTO RECRUITMENT_DRIVE (Company_ID, Drive_Year, Drive_Type, Season, Drive_Date)
        VALUES (%s, %s, %s, %s, %s)
```

### DRV-24: List Drives: Directory with Company Details
- **Source File / Routine:** `services/drive_service.py` -> `list_drives`
- **Purpose:** Browses all campus recruitment drives with company metadata and season.
- **Core DBMS Concepts:** Relational equi-join; chronological temporal ordering.

```sql
SELECT rd.Drive_ID, rd.Company_ID, c.Company_Name, c.Company_Type,
               rd.Drive_Year, rd.Drive_Type, rd.Season, rd.Drive_Date,
               COUNT(o.Opportunity_ID) AS Opportunity_Count
        FROM RECRUITMENT_DRIVE rd
        JOIN COMPANY c ON rd.Company_ID = c.Company_ID
        LEFT JOIN OPPORTUNITY o ON rd.Drive_ID = o.Drive_ID
        WHERE
```

### DRV-27: Delete Drive: Verify Drive Existence
- **Source File / Routine:** `services/drive_service.py` -> `delete_drive`
- **Purpose:** Confirms drive exists before deletion dependency audit.
- **Core DBMS Concepts:** Primary key lookup.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Drive_ID, Company_ID FROM RECRUITMENT_DRIVE WHERE Drive_ID = %s
```

### RND-34: List Rounds: Roster of Assessment Stages by Opportunity
- **Source File / Routine:** `services/round_service.py` -> `list_rounds`
- **Purpose:** Retrieves all sequential selection rounds configured for a job opportunity.
- **Core DBMS Concepts:** Relational equi-join; sequential integer ordering.

```sql
SELECT sp.Round_ID, sp.Opportunity_ID, o.Role, rd.Company_ID, c.Company_Name,
               sp.Round_Number, sp.Round_Type, sp.Description
        FROM SELECTION_PROCESS sp
        JOIN OPPORTUNITY o ON sp.Opportunity_ID = o.Opportunity_ID
        JOIN RECRUITMENT_DRIVE rd ON o.Drive_ID = rd.Drive_ID
        JOIN COMPANY c ON rd.Company_ID = c.Company_ID
        WHERE
```

---

## Category: Placement management (36 Queries)

> Category Focus: Systematic revision of backend routines, transaction hooks, duplicate validation patterns, and relational operations governing **placement management**.

### STU-20: List Students: Paginated Directory Projection
- **Source File / Routine:** `services/student_service.py` -> `list_students`
- **Purpose:** Fetches a paginated window of student records with calculated placement and internship summary statistics.
- **Core DBMS Concepts:** Correlated scalar subqueries in SELECT projection; dynamic sorting (ORDER BY); database pagination (LIMIT %s OFFSET %s).

```sql
SELECT 
            s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name,
            CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Full_Name,
            s.Branch, s.Batch_Year, s.Section, s.CGPA, s.Backlogs, s.Email, s.Resume_Link,
            GROUP_CONCAT(DISTINCT sp.Phone_No SEPARATOR ', ') AS Phone_Numbers,
            COUNT(DISTINCT p.Placement_ID) AS Placement_Offers,
            COUNT(DISTINCT CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN p.Placement_ID END) AS Accepted_Offers,
            MAX(CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN c.Company_Name END) AS Placed_Company,
            MAX(CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN p.Package END) AS Placed_Package,
            COUNT(DISTINCT i.Internship_ID) AS Internships
        FROM STUDENT s
        LEFT JOIN STUDENT_PHONE sp ON s.Student_ID = sp.Student_ID
        LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
        LEFT JOIN COMPANY c ON p.Company_ID = c.Company_ID
        LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
        WHERE
```

### CMP-09: List Companies: Directory with Aggregated Offer Counts
- **Source File / Routine:** `services/company_service.py` -> `list_companies`
- **Purpose:** Browses all corporate partners with dynamically aggregated placement offer counts.
- **Core DBMS Concepts:** LEFT OUTER JOIN; GROUP BY multi-attribute functional dependency preservation; COUNT(p.Placement_ID) aggregate projection.

```sql
SELECT c.Company_ID, c.Company_Name, c.Company_Type, c.Industry, c.Location, c.Website,
               COUNT(DISTINCT rd.Drive_ID) AS Total_Drives,
               COUNT(DISTINCT p.Placement_ID) AS Total_Placements,
               COUNT(DISTINCT i.Internship_ID) AS Total_Internships
        FROM COMPANY c
        LEFT JOIN RECRUITMENT_DRIVE rd ON c.Company_ID = rd.Company_ID
        LEFT JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
        LEFT JOIN INTERNSHIP i ON c.Company_ID = i.Company_ID
        WHERE
```

### PLC-01: Create Placement: Verify Student Candidate Existence
- **Source File / Routine:** `services/placement_service.py` -> `create_placement_offer`
- **Purpose:** Confirms candidate exists and retrieves Roll_No and Name.
- **Core DBMS Concepts:** Foreign key pre-validation.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Student_ID, Roll_No, First_Name, Last_Name FROM STUDENT WHERE Student_ID = %s
```

### PLC-02: Create Placement: Verify Corporate Recruiter
- **Source File / Routine:** `services/placement_service.py` -> `create_placement_offer`
- **Purpose:** Confirms recruiting organization exists before offer attachment.
- **Core DBMS Concepts:** Foreign key pre-validation.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Company_ID, Company_Name FROM COMPANY WHERE Company_ID = %s
```

### PLC-03: Create Placement: Verify Job Opportunity Attachment
- **Source File / Routine:** `services/placement_service.py` -> `create_placement_offer`
- **Purpose:** Validates the opportunity posting and retrieves default compensation package.
- **Core DBMS Concepts:** Job posting reference validation.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Opportunity_ID, Role, Opportunity_Type, Package_Stipend FROM OPPORTUNITY WHERE Opportunity_ID = %s
```

### PLC-04: Create Placement: Prevent Duplicate Offer per Opportunity
- **Source File / Routine:** `services/placement_service.py` -> `create_placement_offer`
- **Purpose:** Ensures a student cannot be issued multiple offers for the exact same job opportunity.
- **Core DBMS Concepts:** Composite domain uniqueness guard.
- **Pattern Note (Pre-Insert Uniqueness Check):** Reusable validation query run before INSERT transactions to prevent database collision and enforce candidate key constraints at the application layer.

```sql
SELECT Placement_ID, Role, Offer_Status FROM PLACEMENT WHERE Student_ID = %s AND Opportunity_ID = %s
```

### PLC-05: Create Placement Offer: Query #5
- **Source File / Routine:** `services/placement_service.py` -> `create_placement_offer`
- **Purpose:** Placement domain operational query.
- **Core DBMS Concepts:** Relational query execution.

```sql
SELECT p.Placement_ID, p.Role, p.Offer_Status, c.Company_Name
            FROM PLACEMENT p
            JOIN COMPANY c ON p.Company_ID = c.Company_ID
            WHERE p.Student_ID = %s AND p.Offer_Status IN ('Accepted', 'Joined')
```

### PLC-06: Create Placement: Insert Placement Offer Tuple
- **Source File / Routine:** `services/placement_service.py` -> `create_placement_offer`
- **Purpose:** Inserts the formal campus placement offer record into PLACEMENT table.
- **Core DBMS Concepts:** Master placement tuple insertion; AUTO_INCREMENT primary key; ENUM constraint validation.
- **Pattern Note (Normalized Entity Insertion):** Parameterized single-row or bulk insert mapping sanitized form inputs to relational columns.

```sql
INSERT INTO PLACEMENT (
            Student_ID, Company_ID, Opportunity_ID, Role, Package,
            Placement_Year, Placement_Type, Is_PPO, Joined, Offer_Status, Interview_Rounds
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
```

### PLC-07: Create Placement: Insert Placement Offer Tuple
- **Source File / Routine:** `services/placement_service.py` -> `create_placement_offer`
- **Purpose:** Inserts the formal campus placement offer record into PLACEMENT table.
- **Core DBMS Concepts:** Master placement tuple insertion; AUTO_INCREMENT primary key; ENUM constraint validation.
- **Pattern Note (Normalized Entity Insertion):** Parameterized single-row or bulk insert mapping sanitized form inputs to relational columns.

```sql
INSERT INTO PLACEMENT_SKILL (Placement_ID, Skill) VALUES (%s, %s)
```

### PLC-09: Get Placement Offer: Retrieve Evaluated Skills
- **Source File / Routine:** `services/placement_service.py` -> `get_placement_offer`
- **Purpose:** Fetches technical skills evaluated during the hiring interview process.
- **Core DBMS Concepts:** Child entity projection; alphabetical sorting.

```sql
SELECT Skill FROM PLACEMENT_SKILL WHERE Placement_ID = %s ORDER BY Skill
```

### PLC-10: Get Placement Offer: Retrieve Interview Selection Stages
- **Source File / Routine:** `services/placement_service.py` -> `get_placement_offer`
- **Purpose:** Fetches the sequential rounds conducted for the candidate's offer.
- **Core DBMS Concepts:** Sequential interview stages lookup.

```sql
SELECT Round_ID, Round_Number, Round_Type, Description
            FROM SELECTION_PROCESS
            WHERE Opportunity_ID = %s
            ORDER BY Round_Number ASC
```

### PLC-11: Get Placement Offer: Retrieve Eligible Engineering Branches
- **Source File / Routine:** `services/placement_service.py` -> `get_placement_offer`
- **Purpose:** Fetches the list of allowed engineering departments for the hiring opportunity.
- **Core DBMS Concepts:** Child bridge table scan.

```sql
SELECT Branch FROM ELIGIBILITY_BRANCH WHERE Eligibility_ID = %s ORDER BY Branch
```

### PLC-12: List Placements: Full-Text Candidate Search Predicate
- **Source File / Routine:** `services/placement_service.py` -> `list_placement_offers`
- **Purpose:** Disjunctively matches candidate roll number, first name, last name, full name, company name, or designated role.
- **Core DBMS Concepts:** Disjunctive pattern matching; composite name search.

```sql
(s.Roll_No LIKE %s OR s.First_Name LIKE %s OR s.Last_Name LIKE %s OR CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) LIKE %s OR c.Company_Name LIKE %s OR p.Role LIKE %s OR EXISTS (SELECT 1 FROM PLACEMENT_SKILL ps WHERE ps.Placement_ID = p.Placement_ID AND ps.Skill LIKE %s))
```

### PLC-13: List Placements: Count Matching Offers for Pagination
- **Source File / Routine:** `services/placement_service.py` -> `list_placement_offers`
- **Purpose:** Computes the exact total number of matching placement offers under active multi-filters.
- **Core DBMS Concepts:** Dynamic query assembly; parameterized WHERE clause; COUNT(DISTINCT) aggregate.

```sql
SELECT COUNT(DISTINCT p.Placement_ID) AS total
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE
```

### PLC-14: List Placements: Paginated Offer Directory with Skill Aggregation
- **Source File / Routine:** `services/placement_service.py` -> `list_placement_offers`
- **Purpose:** Retrieves a paginated cohort of placement offers with concatenated evaluated skills.
- **Core DBMS Concepts:** Three-table equi-join; correlated GROUP_CONCAT scalar subquery; database pagination (LIMIT %s OFFSET %s).

```sql
SELECT p.Placement_ID, p.Student_ID, s.Roll_No, s.First_Name, s.Last_Name,
               CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Student_Name,
               s.Branch, s.Batch_Year, s.CGPA, s.Backlogs, s.Email,
               p.Company_ID, c.Company_Name, c.Company_Type, c.Location, p.Opportunity_ID, p.Role, p.Package,
               p.Placement_Year, p.Placement_Type, p.Is_PPO, p.Joined, p.Offer_Status, p.Interview_Rounds,
               GROUP_CONCAT(DISTINCT ps.Skill SEPARATOR ', ') AS Evaluated_Skills
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        LEFT JOIN PLACEMENT_SKILL ps ON p.Placement_ID = ps.Placement_ID
        WHERE
```

### PLC-15: Placement Analytics: Statistical Compensation Reductions
- **Source File / Routine:** `services/placement_service.py` -> `get_placement_package_statistics`
- **Purpose:** Calculates total compensation count, average package, minimum, maximum, and standard deviation across offers.
- **Core DBMS Concepts:** Single-pass statistical aggregate reductions; continuous numeric analysis.

```sql
SELECT
            COUNT(p.Placement_ID) AS total_offers,
            ROUND(COALESCE(AVG(p.Package), 0), 2) AS avg_package,
            ROUND(COALESCE(MAX(p.Package), 0), 2) AS highest_package,
            ROUND(COALESCE(MIN(p.Package), 0), 2) AS lowest_package
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE
```

### PLC-16: Get Placement Analytics: Query #16
- **Source File / Routine:** `services/placement_service.py` -> `get_placement_analytics`
- **Purpose:** Placement domain operational query.
- **Core DBMS Concepts:** Relational query execution.

```sql
SELECT 
            COUNT(p.Placement_ID) AS total_offers,
            COUNT(DISTINCT p.Student_ID) AS unique_students_offered,
            COUNT(DISTINCT CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN p.Student_ID END) AS placed_students,
            COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' OR p.Offer_Status = 'Joined' THEN p.Student_ID END) AS joined_students,
            COUNT(CASE WHEN p.Is_PPO = 'Yes' THEN 1 END) AS ppo_offers,
            COUNT(CASE WHEN p.Placement_Type = 'On-campus' THEN 1 END) AS on_campus_offers,
            COUNT(CASE WHEN p.Placement_Type = 'Off-campus' THEN 1 END) AS off_campus_offers
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE
```

### PLC-17: Placement Analytics: Multi-Offer Candidate Count
- **Source File / Routine:** `services/placement_service.py` -> `get_placement_analytics`
- **Purpose:** Calculates the number of students who secured 2 or more distinct placement offers.
- **Core DBMS Concepts:** Derived table / subquery in FROM; post-aggregation HAVING filtering.

```sql
SELECT COUNT(*) AS multi_count FROM (
            SELECT p.Student_ID
            FROM PLACEMENT p
            JOIN STUDENT s ON p.Student_ID = s.Student_ID
            JOIN COMPANY c ON p.Company_ID = c.Company_ID
            WHERE
```

### PLC-19: Get Placement Analytics: Query #19
- **Source File / Routine:** `services/placement_service.py` -> `get_placement_analytics`
- **Purpose:** Placement domain operational query.
- **Core DBMS Concepts:** Relational query execution.

```sql
SELECT s.Branch,
               COUNT(p.Placement_ID) AS total_offers,
               COUNT(DISTINCT p.Student_ID) AS unique_offered_students,
               COUNT(DISTINCT CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN p.Student_ID END) AS placed_students,
               ROUND(AVG(p.Package), 2) AS avg_package,
               ROUND(MAX(p.Package), 2) AS highest_package
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE
```

### PLC-20: Get Placement Analytics: Query #20
- **Source File / Routine:** `services/placement_service.py` -> `get_placement_analytics`
- **Purpose:** Placement domain operational query.
- **Core DBMS Concepts:** Relational query execution.

```sql
SELECT 
            SUM(CASE WHEN p.Package <
```

### PLC-21: Get Placement Analytics: Query #21
- **Source File / Routine:** `services/placement_service.py` -> `get_placement_analytics`
- **Purpose:** Placement domain operational query.
- **Core DBMS Concepts:** Relational query execution.

```sql
SELECT p.Offer_Status, COUNT(*) AS count
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE
```

### PLC-25: Update Offer Status: Query #25
- **Source File / Routine:** `services/placement_service.py` -> `update_offer_status`
- **Purpose:** Placement domain operational query.
- **Core DBMS Concepts:** Relational query execution.

```sql
SELECT p.Placement_ID, p.Role, p.Offer_Status, c.Company_Name
            FROM PLACEMENT p
            JOIN COMPANY c ON p.Company_ID = c.Company_ID
            WHERE p.Student_ID = %s 
              AND p.Offer_Status IN ('Accepted', 'Joined')
              AND p.Placement_ID != %s
```

### PLC-26: Update Offer Status: Mutate Operational Status and Joining
- **Source File / Routine:** `services/placement_service.py` -> `update_offer_status`
- **Purpose:** Updates offer status to Accepted, Declined, or Joined and records the Joined flag.
- **Core DBMS Concepts:** Status transition mutation; ENUM constraint validation.

```sql
UPDATE PLACEMENT SET Offer_Status = %s, Joined = %s WHERE Placement_ID = %s
```

### PLC-27: Update Placement Offer: Query #27
- **Source File / Routine:** `services/placement_service.py` -> `update_placement_offer`
- **Purpose:** Placement domain operational query.
- **Core DBMS Concepts:** Relational query execution.

```sql
SELECT p.Placement_ID, p.Role, p.Offer_Status, c.Company_Name
            FROM PLACEMENT p
            JOIN COMPANY c ON p.Company_ID = c.Company_ID
            WHERE p.Student_ID = %s AND p.Offer_Status IN ('Accepted', 'Joined') AND p.Placement_ID != %s
```

### PLC-28: Update Placement: Apply Offer Attribute Modifications
- **Source File / Routine:** `services/placement_service.py` -> `update_placement_offer`
- **Purpose:** Modifies designated role, compensation package, placement type, PPO flag, and rounds.
- **Core DBMS Concepts:** In-place record mutation.

```sql
UPDATE PLACEMENT SET
```

### PLC-29: Update Placement: Purge Existing Evaluated Skills
- **Source File / Routine:** `services/placement_service.py` -> `update_placement_offer`
- **Purpose:** Removes prior evaluated skill associations before inserting the updated skill list.
- **Core DBMS Concepts:** Atomic child table purge.

```sql
DELETE FROM PLACEMENT_SKILL WHERE Placement_ID = %s
```

### PLC-30: Update Placement: Re-Insert Updated Evaluated Skills
- **Source File / Routine:** `services/placement_service.py` -> `update_placement_offer`
- **Purpose:** Inserts the revised evaluated skills for the updated placement offer.
- **Core DBMS Concepts:** Atomic child tuple insertion.

```sql
INSERT INTO PLACEMENT_SKILL (Placement_ID, Skill) VALUES (%s, %s)
```

### PLC-31: Delete Placement: Verify Offer Existence
- **Source File / Routine:** `services/placement_service.py` -> `delete_placement_offer`
- **Purpose:** Confirms placement offer exists before deletion.
- **Core DBMS Concepts:** Primary key lookup.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Placement_ID, Student_ID, Role FROM PLACEMENT WHERE Placement_ID = %s
```

### PLC-32: Delete Placement: Permanently Remove Placement Offer
- **Source File / Routine:** `services/placement_service.py` -> `delete_placement_offer`
- **Purpose:** Deletes placement offer record. Cascades deletion to PLACEMENT_SKILL.
- **Core DBMS Concepts:** Physical record deletion; foreign key cascade.
- **Pattern Note (Transactional Atomic Delete):** Standard parameterized DELETE statement executed within transaction blocks to maintain referential integrity.

```sql
DELETE FROM PLACEMENT WHERE Placement_ID = %s
```

### PLC-33: Multiple Offers: Roster of Multi-Offer Achievers
- **Source File / Routine:** `services/placement_service.py` -> `get_students_with_multiple_offers`
- **Purpose:** Retrieves student profiles who have earned multiple placement offers along with their offer count and maximum package.
- **Core DBMS Concepts:** Relational equi-join; GROUP BY multi-attribute grouping; HAVING post-aggregation cardinality filter; multi-attribute descending sort.

```sql
SELECT s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, s.CGPA,
               COUNT(p.Placement_ID) AS Total_Offers,
               MAX(p.Package) AS Highest_Package,
               MIN(p.Package) AS Lowest_Package,
               GROUP_CONCAT(CONCAT(c.Company_Name, ' (', p.Package, ' LPA - ', p.Offer_Status, ')') SEPARATOR '; ') AS Offers_Breakdown,
               MAX(CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN c.Company_Name ELSE NULL END) AS Accepted_Company,
               MAX(CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN p.Package ELSE NULL END) AS Accepted_Package
        FROM STUDENT s
        JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        GROUP BY s.Student_ID
        HAVING COUNT(p.Placement_ID) >= %s
        ORDER BY Total_Offers DESC, Highest_Package DESC
```

### PLC-34: Offer Distribution: Institutional Single vs Multi-Offer Breakdown
- **Source File / Routine:** `services/placement_service.py` -> `get_offer_distribution_summary`
- **Purpose:** Generates institutional summary: candidates with exactly 1 offer vs candidates with multiple offers.
- **Core DBMS Concepts:** Derived table in FROM; conditional aggregation; institutional summary metrics.

```sql
SELECT 
            SUM(CASE WHEN offer_count = 0 THEN 1 ELSE 0 END) AS zero_offers_count,
            SUM(CASE WHEN offer_count = 1 THEN 1 ELSE 0 END) AS single_offer_count,
            SUM(CASE WHEN offer_count >= 2 THEN 1 ELSE 0 END) AS multiple_offers_count,
            COUNT(*) AS total_students_evaluated
        FROM (
            SELECT s.Student_ID, COUNT(p.Placement_ID) AS offer_count
            FROM STUDENT s
            LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
            GROUP BY s.Student_ID
        ) AS student_offer_counts;
```

### OPP-08: Get Opportunity: Count Issued Placement Offers
- **Source File / Routine:** `services/opportunity_service.py` -> `get_opportunity`
- **Purpose:** Counts the total campus offers extended under this specific opportunity.
- **Core DBMS Concepts:** Aggregate COUNT(*) reduction.

```sql
SELECT 
            (SELECT COUNT(*) FROM PLACEMENT WHERE Opportunity_ID = %s) AS p_count,
            (SELECT COUNT(*) FROM INTERNSHIP WHERE Opportunity_ID = %s) AS i_count
```

### OPP-16: Delete Opportunity: Check Dependent Placement Offers
- **Source File / Routine:** `services/opportunity_service.py` -> `delete_opportunity`
- **Purpose:** Prevents deleting an opportunity if placement offers have already been issued.
- **Core DBMS Concepts:** Referential integrity guard; protected delete enforcement.

```sql
SELECT 
            (SELECT COUNT(*) FROM PLACEMENT WHERE Opportunity_ID = %s) AS p_bound,
            (SELECT COUNT(*) FROM INTERNSHIP WHERE Opportunity_ID = %s) AS i_bound
```

### DRV-28: Delete Drive: Query #28
- **Source File / Routine:** `services/drive_service.py` -> `delete_drive`
- **Purpose:** Recruitment drives, opportunity, or round operational query.
- **Core DBMS Concepts:** Relational query execution.

```sql
SELECT 
            (SELECT COUNT(*) FROM PLACEMENT p JOIN OPPORTUNITY o ON p.Opportunity_ID = o.Opportunity_ID WHERE o.Drive_ID = %s) AS p_bound,
            (SELECT COUNT(*) FROM INTERNSHIP i JOIN OPPORTUNITY o ON i.Opportunity_ID = o.Opportunity_ID WHERE o.Drive_ID = %s) AS i_bound
```

### 10.11: Exhaustive Foreign Key Orphan Detection (19 Referential Paths)
- **Source File / Routine:** `verify.sql` -> `Schema Verification Script (Statement 4)`
- **Purpose:** Performs LEFT OUTER anti-joins across all 19 defined foreign key relationships in the schema to mathematically prove zero referential integrity violations or orphaned child rows.
- **Core DBMS Concepts:** Relational anti-join (⋉), referential integrity constraint verification, and multi-query set union.

```sql
SELECT 'COURSE -> UNIVERSITY' AS fk_relation, COUNT(*) AS orphaned_count 
FROM COURSE c LEFT JOIN UNIVERSITY u ON c.University_ID = u.University_ID WHERE u.University_ID IS NULL
UNION ALL
SELECT 'STUDENT_PHONE -> STUDENT', COUNT(*) 
FROM STUDENT_PHONE sp LEFT JOIN STUDENT s ON sp.Student_ID = s.Student_ID WHERE s.Student_ID IS NULL
UNION ALL
SELECT 'STUDENT_SKILL -> STUDENT', COUNT(*) 
FROM STUDENT_SKILL sk LEFT JOIN STUDENT s ON sk.Student_ID = s.Student_ID WHERE s.Student_ID IS NULL
UNION ALL
SELECT 'STUDENT_PROFILE -> STUDENT', COUNT(*) 
FROM STUDENT_PROFILE p LEFT JOIN STUDENT s ON p.Student_ID = s.Student_ID WHERE s.Student_ID IS NULL
UNION ALL
SELECT 'RESUME -> STUDENT', COUNT(*) 
FROM RESUME r LEFT JOIN STUDENT s ON r.Student_ID = s.Student_ID WHERE s.Student_ID IS NULL
UNION ALL
SELECT 'EDUCATION_DOCUMENT -> RESUME', COUNT(*) 
FROM EDUCATION_DOCUMENT ed LEFT JOIN RESUME r ON ed.Resume_ID = r.Resume_ID WHERE r.Resume_ID IS NULL
UNION ALL
SELECT 'SEMESTER_RESULT -> STUDENT', COUNT(*) 
FROM SEMESTER_RESULT sr LEFT JOIN STUDENT s ON sr.Student_ID = s.Student_ID WHERE s.Student_ID IS NULL
UNION ALL
SELECT 'RECRUITMENT_DRIVE -> COMPANY', COUNT(*) 
FROM RECRUITMENT_DRIVE rd LEFT JOIN COMPANY c ON rd.Company_ID = c.Company_ID WHERE c.Company_ID IS NULL
UNION ALL
SELECT 'OPPORTUNITY -> RECRUITMENT_DRIVE', COUNT(*) 
FROM OPPORTUNITY o LEFT JOIN RECRUITMENT_DRIVE rd ON o.Drive_ID = rd.Drive_ID WHERE rd.Drive_ID IS NULL
UNION ALL
SELECT 'ELIGIBILITY -> OPPORTUNITY', COUNT(*) 
FROM ELIGIBILITY e LEFT JOIN OPPORTUNITY o ON e.Opportunity_ID = o.Opportunity_ID WHERE o.Opportunity_ID IS NULL
UNION ALL
SELECT 'SELECTION_PROCESS -> OPPORTUNITY', COUNT(*) 
FROM SELECTION_PROCESS sp LEFT JOIN OPPORTUNITY o ON sp.Opportunity_ID = o.Opportunity_ID WHERE o.Opportunity_ID IS NULL
UNION ALL
SELECT 'INTERNSHIP -> STUDENT', COUNT(*) 
FROM INTERNSHIP i LEFT JOIN STUDENT s ON i.Student_ID = s.Student_ID WHERE s.Student_ID IS NULL
UNION ALL
SELECT 'INTERNSHIP -> COMPANY', COUNT(*) 
FROM INTERNSHIP i LEFT JOIN COMPANY c ON i.Company_ID = c.Company_ID WHERE c.Company_ID IS NULL
UNION ALL
SELECT 'INTERNSHIP -> OPPORTUNITY (nullable)', COUNT(*) 
FROM INTERNSHIP i LEFT JOIN OPPORTUNITY o ON i.Opportunity_ID = o.Opportunity_ID WHERE i.Opportunity_ID IS NOT NULL AND o.Opportunity_ID IS NULL
UNION ALL
SELECT 'INTERNSHIP -> REQUIREMENT (nullable)', COUNT(*) 
FROM INTERNSHIP i LEFT JOIN INTERNSHIP_REQUIREMENT ir ON i.Requirement_ID = ir.Requirement_ID WHERE i.Requirement_ID IS NOT NULL AND ir.Requirement_ID IS NULL
UNION ALL
SELECT 'PLACEMENT -> STUDENT', COUNT(*) 
FROM PLACEMENT p LEFT JOIN STUDENT s ON p.Student_ID = s.Student_ID WHERE s.Student_ID IS NULL
UNION ALL
SELECT 'PLACEMENT -> COMPANY', COUNT(*) 
FROM PLACEMENT p LEFT JOIN COMPANY c ON p.Company_ID = c.Company_ID WHERE c.Company_ID IS NULL
UNION ALL
SELECT 'PLACEMENT -> OPPORTUNITY (nullable)', COUNT(*) 
FROM PLACEMENT p LEFT JOIN OPPORTUNITY o ON p.Opportunity_ID = o.Opportunity_ID WHERE p.Opportunity_ID IS NOT NULL AND o.Opportunity_ID IS NULL
UNION ALL
SELECT 'PLACEMENT_SKILL -> PLACEMENT', COUNT(*) 
FROM PLACEMENT_SKILL ps LEFT JOIN PLACEMENT p ON ps.Placement_ID = p.Placement_ID WHERE p.Placement_ID IS NULL;
```

### 10.13: Placement Offer Cardinality Distribution Analysis (CTE)
- **Source File / Routine:** `verify.sql` -> `Schema Verification Script (Statement 6)`
- **Purpose:** Classifies the entire student population into distinct offer tiers (0 offers, 1 offer, 2+ multiple offers) using a Common Table Expression to audit placement penetration.
- **Core DBMS Concepts:** Common Table Expression (WITH clause), outer joins, conditional aggregation, and multi-tier categorization.

```sql
WITH offer_counts AS (
    SELECT s.Student_ID, s.First_Name, s.Roll_No, COUNT(p.Placement_ID) AS total_offers,
           COUNT(CASE WHEN p.Joined = 'Yes' THEN 1 END) AS joined_offers
    FROM STUDENT s
    LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
    GROUP BY s.Student_ID, s.First_Name, s.Roll_No
)
SELECT 
    CASE 
        WHEN total_offers = 0 THEN '0 offers (Zero)'
        WHEN total_offers = 1 THEN '1 offer (Single)'
        ELSE '2+ offers (Multiple)'
    END AS category,
    COUNT(*) AS student_count
FROM offer_counts
GROUP BY category
ORDER BY category;
```

---

## Category: Internship management (16 Queries)

> Category Focus: Systematic revision of backend routines, transaction hooks, duplicate validation patterns, and relational operations governing **internship management**.

### STU-15: Get Student: Retrieve Semester Academic Results
- **Source File / Routine:** `services/student_service.py` -> `get_student`
- **Purpose:** Retrieves semester-by-semester SGPA performance records and credit allocations.
- **Core DBMS Concepts:** Chronological progression retrieval; single-table indexed scan.

```sql
SELECT i.Internship_ID, i.Internship_No, i.Internship_Type, i.Role,
               i.Stipend, i.Start_Date, i.End_Date, i.Credits,
               i.Report_Semester, i.Report_Grade, i.Report_Link, i.Certificate_Link,
               c.Company_ID, c.Company_Name, c.Company_Type,
               ir.Required_Result_Semester,
               sr.SGPA AS Prerequisite_Semester_SGPA
        FROM INTERNSHIP i
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        LEFT JOIN INTERNSHIP_REQUIREMENT ir ON i.Requirement_ID = ir.Requirement_ID
        LEFT JOIN SEMESTER_RESULT sr ON i.Student_ID = sr.Student_ID 
                                    AND ir.Required_Result_Semester = sr.Semester
        WHERE i.Student_ID = %s
        ORDER BY i.Internship_No ASC
```

### INT-04: Create Internship: Verify Student Candidate
- **Source File / Routine:** `services/internship_service.py` -> `create_internship`
- **Purpose:** Confirms student exists prior to internship registration.
- **Core DBMS Concepts:** Foreign key verification.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Student_ID, Roll_No FROM STUDENT WHERE Student_ID = %s
```

### INT-06: Create Internship: Prevent Duplicate Mandatory Sequence Number
- **Source File / Routine:** `services/internship_service.py` -> `create_internship`
- **Purpose:** Guarantees a student cannot register multiple attachments under the same Mandatory Internship number.
- **Core DBMS Concepts:** Degree policy uniqueness enforcement.
- **Pattern Note (Pre-Insert Uniqueness Check):** Reusable validation query run before INSERT transactions to prevent database collision and enforce candidate key constraints at the application layer.

```sql
SELECT Internship_ID, Internship_Type, Role FROM INTERNSHIP WHERE Student_ID = %s AND Internship_No = %s
```

### INT-07: Create Internship: Link Formal Requirement Meta
- **Source File / Routine:** `services/internship_service.py` -> `create_internship`
- **Purpose:** Validates the requirement link and extracts curriculum requirements.
- **Core DBMS Concepts:** Curriculum requirement traversal.

```sql
SELECT Requirement_ID, Internship_No, Mandatory, Required_Result_Semester FROM INTERNSHIP_REQUIREMENT WHERE Requirement_ID = %s
```

### INT-08: Create Internship: Insert Internship Attachment Tuple
- **Source File / Routine:** `services/internship_service.py` -> `create_internship`
- **Purpose:** Inserts the formal industry training record into the INTERNSHIP table.
- **Core DBMS Concepts:** Master internship insertion; AUTO_INCREMENT primary key; temporal date range validation.
- **Pattern Note (Normalized Entity Insertion):** Parameterized single-row or bulk insert mapping sanitized form inputs to relational columns.

```sql
INSERT INTO INTERNSHIP (
            Student_ID, Company_ID, Opportunity_ID, Requirement_ID, Internship_No,
            Internship_Type, Role, Interview_Rounds, Stipend, Start_Date, End_Date,
            Credits, Report_Semester, Report_Link, Report_Grade, Certificate_Link
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
```

### INT-09: Get Internship: Comprehensive 3-Way Equi-Join Detail
- **Source File / Routine:** `services/internship_service.py` -> `get_internship`
- **Purpose:** Retrieves complete internship data with student academic metrics, corporate host details, and prerequisite SGPA.
- **Core DBMS Concepts:** Multi-table equi-join; LEFT JOIN to prerequisite semester SGPA; temporal projection.

```sql
SELECT i.Internship_ID, i.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, s.Batch_Year, s.CGPA, s.Email,
               i.Company_ID, c.Company_Name, c.Company_Type, c.Location AS Company_Location, c.Website AS Company_Website,
               i.Opportunity_ID, o.Role AS Opportunity_Role, o.Opportunity_Type,
               i.Requirement_ID, ir.Prescribed_Period, ir.Required_Result_Semester, ir.Report_Submission_Semester,
               i.Internship_No, i.Internship_Type, i.Role, i.Interview_Rounds, i.Stipend,
               i.Start_Date, i.End_Date, i.Credits, i.Report_Semester, i.Report_Link,
               i.Report_Grade, i.Certificate_Link,
               sr.SGPA AS Prerequisite_Semester_SGPA,
               sr.Total_Credits AS Prerequisite_Credits
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        LEFT JOIN OPPORTUNITY o ON i.Opportunity_ID = o.Opportunity_ID
        LEFT JOIN INTERNSHIP_REQUIREMENT ir ON i.Requirement_ID = ir.Requirement_ID
        LEFT JOIN SEMESTER_RESULT sr ON i.Student_ID = sr.Student_ID 
                                    AND ir.Required_Result_Semester = sr.Semester
        WHERE i.Internship_ID = %s
```

### INT-10: List Internships: Total Count for Pagination
- **Source File / Routine:** `services/internship_service.py` -> `list_internships`
- **Purpose:** Computes matching internship attachments under active multi-filter criteria.
- **Core DBMS Concepts:** Dynamic query assembly; aggregate COUNT(*) reduction.

```sql
SELECT COUNT(*) AS total
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        WHERE
```

### INT-11: List Internships: Paginated Registry with Prerequisite SGPA
- **Source File / Routine:** `services/internship_service.py` -> `list_internships`
- **Purpose:** Retrieves a paginated cohort of internships with dynamically resolved prerequisite semester SGPAs.
- **Core DBMS Concepts:** Multi-table join; prerequisite semester SGPA resolution; database pagination (LIMIT %s OFFSET %s).

```sql
SELECT i.Internship_ID, i.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, s.Batch_Year, s.CGPA, s.Email,
               i.Company_ID, c.Company_Name, c.Company_Type,
               i.Opportunity_ID, o.Role AS Opportunity_Role,
               i.Requirement_ID, ir.Prescribed_Period, ir.Required_Result_Semester, ir.Report_Submission_Semester,
               i.Internship_No, i.Internship_Type, i.Role, i.Interview_Rounds, i.Stipend,
               i.Start_Date, i.End_Date, i.Credits, i.Report_Semester, i.Report_Link,
               i.Report_Grade, i.Certificate_Link,
               sr.SGPA AS Prerequisite_Semester_SGPA,
               sr.Total_Credits AS Prerequisite_Credits
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        LEFT JOIN OPPORTUNITY o ON i.Opportunity_ID = o.Opportunity_ID
        LEFT JOIN INTERNSHIP_REQUIREMENT ir ON i.Requirement_ID = ir.Requirement_ID
        LEFT JOIN SEMESTER_RESULT sr ON i.Student_ID = sr.Student_ID 
                                    AND ir.Required_Result_Semester = sr.Semester
        WHERE
```

### INT-12: Update Internship: Verify Requirement Sequence Number
- **Source File / Routine:** `services/internship_service.py` -> `update_internship`
- **Purpose:** Resolves Requirement_ID to the canonical Internship_No sequence.
- **Core DBMS Concepts:** Requirement reference lookup.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Internship_No FROM INTERNSHIP_REQUIREMENT WHERE Requirement_ID = %s
```

### INT-13: Update Internship: Mutate Training Record
- **Source File / Routine:** `services/internship_service.py` -> `update_internship`
- **Purpose:** Modifies internship dates, duration weeks/days, stipend, evaluation grade, report link, and status.
- **Core DBMS Concepts:** In-place record mutation; clustered index write.

```sql
UPDATE INTERNSHIP SET
```

### INT-14: Delete Internship: Verify Existence
- **Source File / Routine:** `services/internship_service.py` -> `delete_internship`
- **Purpose:** Confirms internship record exists before deletion.
- **Core DBMS Concepts:** Primary key lookup.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Internship_ID, Student_ID, Internship_No, Internship_Type FROM INTERNSHIP WHERE Internship_ID = %s
```

### INT-15: Delete Internship: Permanently Remove Record
- **Source File / Routine:** `services/internship_service.py` -> `delete_internship`
- **Purpose:** Deletes internship attachment from the database.
- **Core DBMS Concepts:** Physical record deletion.
- **Pattern Note (Transactional Atomic Delete):** Standard parameterized DELETE statement executed within transaction blocks to maintain referential integrity.

```sql
DELETE FROM INTERNSHIP WHERE Internship_ID = %s
```

### INT-18: Get Branch Internship Statistics: Query #18
- **Source File / Routine:** `services/internship_service.py` -> `get_branch_internship_statistics`
- **Purpose:** Internship domain operational query.
- **Core DBMS Concepts:** Relational query execution.

```sql
SELECT 
            s.Branch,
            COUNT(DISTINCT s.Student_ID) AS total_students,
            COUNT(DISTINCT CASE WHEN i.Internship_No = 1 AND i.Internship_Type = 'Mandatory' THEN s.Student_ID END) AS i1_completed,
            COUNT(DISTINCT CASE WHEN i.Internship_No = 2 AND i.Internship_Type = 'Mandatory' THEN s.Student_ID END) AS i2_completed,
            COUNT(DISTINCT CASE WHEN i.Internship_Type = 'Additional' THEN i.Internship_ID END) AS additional_count,
            ROUND(COALESCE(AVG(i.Stipend), 0), 2) AS avg_stipend,
            ROUND(COALESCE(MAX(i.Stipend), 0), 2) AS max_stipend
        FROM STUDENT s
        LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
        GROUP BY s.Branch
        ORDER BY s.Branch ASC
```

### INT-19: Internship Analytics: Candidates Completing Both Mandatory Internships by Branch
- **Source File / Routine:** `services/internship_service.py` -> `get_branch_internship_statistics`
- **Purpose:** Calculates the headcount of students who have completed BOTH Mandatory Internship 1 AND 2 per branch.
- **Core DBMS Concepts:** Conditional set cardinality; post-aggregation compliance audit.

```sql
SELECT s.Branch, COUNT(DISTINCT s.Student_ID) AS both_completed
        FROM STUDENT s
        JOIN INTERNSHIP i1 ON s.Student_ID = i1.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = 'Mandatory'
        JOIN INTERNSHIP i2 ON s.Student_ID = i2.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = 'Mandatory'
        GROUP BY s.Branch
```

### REQ-29: Internship Requirements: List Degree Curriculum Rules
- **Source File / Routine:** `services/internship_requirement_service.py` -> `list_requirements`
- **Purpose:** Retrieves the master catalog of institutional degree internship requirements.
- **Core DBMS Concepts:** Curriculum rule master projection; sequence ordering.

```sql
SELECT Requirement_ID, Internship_No, Mandatory, Prescribed_Period,
               Required_Result_Semester, Report_Submission_Semester, Credits, Description
        FROM INTERNSHIP_REQUIREMENT
        ORDER BY Internship_No ASC
```

### REQ-30: Internship Requirements: Fetch Requirement by Primary Key
- **Source File / Routine:** `services/internship_requirement_service.py` -> `get_requirement`
- **Purpose:** Retrieves a specific degree internship requirement rule by Requirement_ID.
- **Core DBMS Concepts:** Primary key point lookup.

```sql
SELECT Requirement_ID, Internship_No, Mandatory, Prescribed_Period,
               Required_Result_Semester, Report_Submission_Semester, Credits, Description
        FROM INTERNSHIP_REQUIREMENT
        WHERE Requirement_ID = %s
```

---

## Category: Academic results (25 Queries)

> Category Focus: Systematic revision of backend routines, transaction hooks, duplicate validation patterns, and relational operations governing **academic results**.

### STU-08: Get Student: Retrieve Registered Curriculum Courses
- **Source File / Routine:** `services/student_service.py` -> `get_student`
- **Purpose:** Fetches all academic courses the student has enrolled in along with grades and credits.
- **Core DBMS Concepts:** M:N relationship traversal through associative bridge entity STUDENT_COURSE; multi-column sorting.

```sql
SELECT c.Course_ID, c.Course_Name, c.Department, c.Semester, c.Credits, c.Course_Type,
               sc.Enrollment_Year, sc.Grade
        FROM STUDENT_COURSE sc
        JOIN COURSE c ON sc.Course_ID = c.Course_ID
        WHERE sc.Student_ID = %s
        ORDER BY sc.Enrollment_Year DESC, c.Semester ASC
```

### CRS-01: Create Course: Verify Parent University
- **Source File / Routine:** `services/course_service.py` -> `create_course`
- **Purpose:** Confirms university institution exists before creating a course.
- **Core DBMS Concepts:** Foreign key verification.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT University_ID FROM UNIVERSITY WHERE University_ID = %s
```

### CRS-02: Create Course: Prevent Duplicate Course per Semester
- **Source File / Routine:** `services/course_service.py` -> `create_course`
- **Purpose:** Guarantees course name uniqueness within a department and semester.
- **Core DBMS Concepts:** Composite uniqueness guard.
- **Pattern Note (Pre-Insert Uniqueness Check):** Reusable validation query run before INSERT transactions to prevent database collision and enforce candidate key constraints at the application layer.

```sql
SELECT Course_ID FROM COURSE WHERE University_ID = %s AND Course_Name = %s AND Semester = %s
```

### CRS-03: Create Course: Insert Course Master Tuple
- **Source File / Routine:** `services/course_service.py` -> `create_course`
- **Purpose:** Inserts a new academic course into the curriculum catalog.
- **Core DBMS Concepts:** Master catalog insertion; AUTO_INCREMENT primary key.
- **Pattern Note (Normalized Entity Insertion):** Parameterized single-row or bulk insert mapping sanitized form inputs to relational columns.

```sql
INSERT INTO COURSE (University_ID, Course_Name, Department, Semester, Credits, Course_Type)
        VALUES (%s, %s, %s, %s, %s, %s)
```

### CRS-04: Get Course: Equi-Join with University Institution
- **Source File / Routine:** `services/course_service.py` -> `get_course`
- **Purpose:** Retrieves course details along with parent university name.
- **Core DBMS Concepts:** Relational equi-join.

```sql
SELECT c.Course_ID, c.University_ID, u.University_Name, c.Course_Name,
               c.Department, c.Semester, c.Credits, c.Course_Type
        FROM COURSE c
        JOIN UNIVERSITY u ON c.University_ID = u.University_ID
        WHERE c.Course_ID = %s
```

### CRS-05: Get Course: Retrieve Enrolled Student Candidates
- **Source File / Routine:** `services/course_service.py` -> `get_course`
- **Purpose:** Fetches all students enrolled in the course with their assigned grades.
- **Core DBMS Concepts:** M:N relationship traversal through associative bridge.

```sql
SELECT s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch,
               sc.Enrollment_Year, sc.Grade
        FROM STUDENT_COURSE sc
        JOIN STUDENT s ON sc.Student_ID = s.Student_ID
        WHERE sc.Course_ID = %s
        ORDER BY sc.Enrollment_Year DESC, s.Roll_No ASC
```

### CRS-06: List Courses: Curricular Course Directory
- **Source File / Routine:** `services/course_service.py` -> `list_courses`
- **Purpose:** Browses all academic courses with credit weightings and departments.
- **Core DBMS Concepts:** Relational equi-join; multi-attribute curriculum sorting.

```sql
SELECT c.Course_ID, c.University_ID, u.University_Name, c.Course_Name,
               c.Department, c.Semester, c.Credits, c.Course_Type,
               COUNT(sc.Student_ID) AS Enrolled_Count
        FROM COURSE c
        JOIN UNIVERSITY u ON c.University_ID = u.University_ID
        LEFT JOIN STUDENT_COURSE sc ON c.Course_ID = sc.Course_ID
        WHERE
```

### CRS-08: Update Course: Mutate Course Attributes
- **Source File / Routine:** `services/course_service.py` -> `update_course`
- **Purpose:** Modifies course name, department, semester, credits, and type.
- **Core DBMS Concepts:** In-place record mutation.

```sql
UPDATE COURSE SET
```

### CRS-09: Delete Course: Verify Target Existence
- **Source File / Routine:** `services/course_service.py` -> `delete_course`
- **Purpose:** Confirms course exists before deletion.
- **Core DBMS Concepts:** Primary key lookup.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Course_ID, Course_Name FROM COURSE WHERE Course_ID = %s
```

### CRS-11: Delete Course: Permanently Remove Course
- **Source File / Routine:** `services/course_service.py` -> `delete_course`
- **Purpose:** Deletes course record from the catalog.
- **Core DBMS Concepts:** Physical record deletion.
- **Pattern Note (Transactional Atomic Delete):** Standard parameterized DELETE statement executed within transaction blocks to maintain referential integrity.

```sql
DELETE FROM COURSE WHERE Course_ID = %s
```

### REG-13: Register Course: Verify Course Catalog Entry
- **Source File / Routine:** `services/registration_service.py` -> `register_student_course`
- **Purpose:** Confirms course exists before enrollment.
- **Core DBMS Concepts:** Foreign key verification.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Course_ID, Course_Name FROM COURSE WHERE Course_ID = %s
```

### REG-14: Register Course: Prevent Duplicate Enrollment
- **Source File / Routine:** `services/registration_service.py` -> `register_student_course`
- **Purpose:** Ensures student cannot register multiple times for the same course.
- **Core DBMS Concepts:** Composite primary key uniqueness guard.
- **Pattern Note (Pre-Insert Uniqueness Check):** Reusable validation query run before INSERT transactions to prevent database collision and enforce candidate key constraints at the application layer.

```sql
SELECT * FROM STUDENT_COURSE WHERE Student_ID = %s AND Course_ID = %s
```

### REG-15: Register Course: Insert Course Enrollment Tuple
- **Source File / Routine:** `services/registration_service.py` -> `register_student_course`
- **Purpose:** Enrolls student in course, recording Enrollment_Year and Grade.
- **Core DBMS Concepts:** Associative bridge insertion; composite primary key (Student_ID, Course_ID).
- **Pattern Note (Normalized Entity Insertion):** Parameterized single-row or bulk insert mapping sanitized form inputs to relational columns.

```sql
INSERT INTO STUDENT_COURSE (Student_ID, Course_ID, Enrollment_Year, Grade)
        VALUES (%s, %s, %s, %s)
```

### REG-16: Get Registration: Equi-Join Enrollment Detail
- **Source File / Routine:** `services/registration_service.py` -> `get_registration`
- **Purpose:** Retrieves student enrollment record along with course details and credits.
- **Core DBMS Concepts:** Three-table relational equi-join.

```sql
SELECT sc.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch,
               sc.Course_ID, c.Course_Name, c.Department, c.Semester, c.Credits, c.Course_Type,
               sc.Enrollment_Year, sc.Grade
        FROM STUDENT_COURSE sc
        JOIN STUDENT s ON sc.Student_ID = s.Student_ID
        JOIN COURSE c ON sc.Course_ID = c.Course_ID
        WHERE sc.Student_ID = %s AND sc.Course_ID = %s
```

### REG-17: List Registrations: Roster of Student Course Enrollments
- **Source File / Routine:** `services/registration_service.py` -> `list_registrations`
- **Purpose:** Browses all course registrations with student names and letter grades.
- **Core DBMS Concepts:** Three-table equi-join; temporal cohort sorting.

```sql
SELECT sc.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch,
               sc.Course_ID, c.Course_Name, c.Department, c.Semester, c.Credits, c.Course_Type,
               sc.Enrollment_Year, sc.Grade
        FROM STUDENT_COURSE sc
        JOIN STUDENT s ON sc.Student_ID = s.Student_ID
        JOIN COURSE c ON sc.Course_ID = c.Course_ID
        WHERE
```

### REG-18: Update Registration: Verify Enrollment
- **Source File / Routine:** `services/registration_service.py` -> `update_registration`
- **Purpose:** Confirms enrollment exists before updating grade.
- **Core DBMS Concepts:** Composite key lookup.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT * FROM STUDENT_COURSE WHERE Student_ID = %s AND Course_ID = %s
```

### REG-19: Update Registration: Mutate Grade and Academic Year
- **Source File / Routine:** `services/registration_service.py` -> `update_registration`
- **Purpose:** Modifies student grade or enrollment year for a registered course.
- **Core DBMS Concepts:** In-place record mutation on composite key.

```sql
UPDATE STUDENT_COURSE SET
```

### REG-20: Unregister Course: Verify Enrollment Existence
- **Source File / Routine:** `services/registration_service.py` -> `unregister_student_course`
- **Purpose:** Confirms enrollment exists before deletion.
- **Core DBMS Concepts:** Composite key lookup.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT * FROM STUDENT_COURSE WHERE Student_ID = %s AND Course_ID = %s
```

### REG-21: Unregister Course: Remove Course Enrollment Tuple
- **Source File / Routine:** `services/registration_service.py` -> `unregister_student_course`
- **Purpose:** Unenrolls student from the course.
- **Core DBMS Concepts:** Physical record deletion on composite key.

```sql
DELETE FROM STUDENT_COURSE WHERE Student_ID = %s AND Course_ID = %s
```

### RES-37: Create Semester Result: Verify Student Candidate
- **Source File / Routine:** `services/semester_result_service.py` -> `create_semester_result`
- **Purpose:** Confirms student exists before recording semester performance.
- **Core DBMS Concepts:** Foreign key verification.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Student_ID, Roll_No FROM STUDENT WHERE Student_ID = %s
```

### RES-38: Create Semester Result: Prevent Duplicate Semester Performance
- **Source File / Routine:** `services/semester_result_service.py` -> `create_semester_result`
- **Purpose:** Guarantees student cannot have duplicate SGPA entries for the same semester.
- **Core DBMS Concepts:** Composite UNIQUE constraint validation.
- **Pattern Note (Pre-Insert Uniqueness Check):** Reusable validation query run before INSERT transactions to prevent database collision and enforce candidate key constraints at the application layer.

```sql
SELECT Result_ID FROM SEMESTER_RESULT WHERE Student_ID = %s AND Semester = %s
```

### RES-39: Create Semester Result: Insert SGPA Academic Performance Tuple
- **Source File / Routine:** `services/semester_result_service.py` -> `create_semester_result`
- **Purpose:** Records semester SGPA (0.00 to 10.00) and credits earned.
- **Core DBMS Concepts:** Clustered insertion; CHECK constraint enforcement on SGPA.
- **Pattern Note (Normalized Entity Insertion):** Parameterized single-row or bulk insert mapping sanitized form inputs to relational columns.

```sql
INSERT INTO SEMESTER_RESULT (Student_ID, Semester, SGPA, Year, Total_Credits)
        VALUES (%s, %s, %s, %s, %s)
```

### RES-42: Update Semester Result: Mutate SGPA and Credits
- **Source File / Routine:** `services/semester_result_service.py` -> `update_semester_result`
- **Purpose:** Modifies student SGPA or credits for a given semester result.
- **Core DBMS Concepts:** In-place record mutation.

```sql
UPDATE SEMESTER_RESULT SET
```

### RES-43: Delete Semester Result: Verify Result Existence
- **Source File / Routine:** `services/semester_result_service.py` -> `delete_semester_result`
- **Purpose:** Confirms semester result exists before deletion.
- **Core DBMS Concepts:** Primary key lookup.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Result_ID, Student_ID, Semester FROM SEMESTER_RESULT WHERE Result_ID = %s
```

### RES-44: Delete Semester Result: Permanently Remove Result Record
- **Source File / Routine:** `services/semester_result_service.py` -> `delete_semester_result`
- **Purpose:** Deletes semester result record from the database.
- **Core DBMS Concepts:** Physical record deletion.
- **Pattern Note (Transactional Atomic Delete):** Standard parameterized DELETE statement executed within transaction blocks to maintain referential integrity.

```sql
DELETE FROM SEMESTER_RESULT WHERE Result_ID = %s
```

---

## Category: Dashboard and statistics (16 Queries)

> Category Focus: Systematic revision of backend routines, transaction hooks, duplicate validation patterns, and relational operations governing **dashboard and statistics**.

### INT-22: Internship KPIs: Headline Attachment Volume & Average Compensation
- **Source File / Routine:** `services/internship_service.py` -> `get_internship_dashboard_analytics`
- **Purpose:** Calculates total internship volume, average stipend, max stipend, and total academic credits earned.
- **Core DBMS Concepts:** Single-pass aggregate reductions; financial and credit summary.

```sql
SELECT COUNT(*) AS total_internships, ROUND(COALESCE(AVG(Stipend), 0), 2) AS avg_stipend, ROUND(COALESCE(MAX(Stipend), 0), 2) AS max_stipend FROM INTERNSHIP
```

### INT-24: Internship KPIs: Institutional Student Denominator
- **Source File / Routine:** `services/internship_service.py` -> `get_internship_dashboard_analytics`
- **Purpose:** Retrieves total registered student headcount to compute overall compliance percentage.
- **Core DBMS Concepts:** Institutional denominator count.

```sql
SELECT COUNT(*) AS total_students FROM STUDENT
```

### INT-26: Internship KPIs: Total Pending or Active Internships
- **Source File / Routine:** `services/internship_service.py` -> `get_internship_dashboard_analytics`
- **Purpose:** Counts all internships with operational status 'Active' or 'Pending'.
- **Core DBMS Concepts:** Operational status counting.

```sql
SELECT COUNT(*) AS pending_count FROM INTERNSHIP
        WHERE End_Date <= CURDATE() AND (Report_Link IS NULL OR Report_Grade IS NULL OR Report_Grade = 'Pending')
```

### INT-27: Internship KPIs: Academic Evaluation Grade Distribution
- **Source File / Routine:** `services/internship_service.py` -> `get_internship_dashboard_analytics`
- **Purpose:** Aggregates internship evaluation grades (Excellent, Good, Satisfactory, Pending).
- **Core DBMS Concepts:** COALESCE null-handling; categorical grouping.

```sql
SELECT COALESCE(Report_Grade, 'Ungraded') AS grade, COUNT(*) AS count
        FROM INTERNSHIP
        GROUP BY COALESCE(Report_Grade, 'Ungraded')
        ORDER BY count DESC
```

### INT-28: Get Internship Dashboard Analytics: Query #28
- **Source File / Routine:** `services/internship_service.py` -> `get_internship_dashboard_analytics`
- **Purpose:** Internship domain operational query.
- **Core DBMS Concepts:** Relational query execution.

```sql
SELECT 
            CASE 
                WHEN Start_Date > CURDATE() THEN 'Upcoming'
                WHEN Start_Date <= CURDATE() AND End_Date >= CURDATE() THEN 'In Progress'
                WHEN End_Date <= CURDATE() AND (Report_Link IS NOT NULL OR Report_Grade IS NOT NULL) THEN 'Completed'
                ELSE 'Pending Report'
            END AS status_group,
            COUNT(*) AS count
        FROM INTERNSHIP
        GROUP BY status_group
```

### DSH-01: Dashboard Filters: Distinct Active Engineering Branches
- **Source File / Routine:** `services/dashboard_service.py` -> `get_dashboard_filter_options`
- **Purpose:** Retrieves canonical list of engineering branches actually populated in the database.
- **Core DBMS Concepts:** SELECT DISTINCT deduplication; index scan.

```sql
SELECT DISTINCT Branch FROM STUDENT WHERE Branch IS NOT NULL AND Branch != '' ORDER BY Branch ASC
```

### DSH-02: Dashboard Filters: Distinct Graduating Batch Years
- **Source File / Routine:** `services/dashboard_service.py` -> `get_dashboard_filter_options`
- **Purpose:** Retrieves all distinct graduation batch years for cohort filtering.
- **Core DBMS Concepts:** Temporal cohort extraction.

```sql
SELECT DISTINCT Batch_Year FROM STUDENT WHERE Batch_Year IS NOT NULL ORDER BY Batch_Year DESC
```

### DSH-03: Dashboard Filters: Distinct Placement Recruitment Years
- **Source File / Routine:** `services/dashboard_service.py` -> `get_dashboard_filter_options`
- **Purpose:** Retrieves all recruitment calendar years present in historical placement records.
- **Core DBMS Concepts:** Historical campaign year extraction.

```sql
SELECT DISTINCT Placement_Year FROM PLACEMENT WHERE Placement_Year IS NOT NULL ORDER BY Placement_Year DESC
```

### DSH-04: Dashboard KPI: Total Candidates & Placed Headcount
- **Source File / Routine:** `services/dashboard_service.py` -> `get_dashboard_stats`
- **Purpose:** Calculates total candidates and placed headcount under active dashboard filters.
- **Core DBMS Concepts:** LEFT JOIN; conditional aggregation; dynamic WHERE filtering.

```sql
SELECT 
            COUNT(*) AS total_students,
            COUNT(*) AS active_students,
            COUNT(CASE WHEN s.Backlogs = 0 AND s.CGPA >= 6.00 THEN 1 END) AS eligible_students,
            ROUND(COALESCE(AVG(s.CGPA), 0), 2) AS avg_cgpa
        FROM STUDENT s
        WHERE
```

### DSH-06: Dashboard KPI: Total Corporate Recruiting Partners
- **Source File / Routine:** `services/dashboard_service.py` -> `get_dashboard_stats`
- **Purpose:** Counts total active corporate employers in the database.
- **Core DBMS Concepts:** Table row count aggregate.

```sql
SELECT COUNT(*) AS total_companies FROM COMPANY
```

### DSH-07: Dashboard KPI: Tier-1 Product Company Count
- **Source File / Routine:** `services/dashboard_service.py` -> `get_dashboard_stats`
- **Purpose:** Calculates headcount of elite Product-based recruiting partners.
- **Core DBMS Concepts:** Conditional categorical counting.

```sql
SELECT SUM(CASE WHEN Company_Type = 'Product' THEN 1 ELSE 0 END) AS tier1_companies FROM COMPANY
```

### DSH-08: Dashboard KPI: Active Recruitment Drives Count
- **Source File / Routine:** `services/dashboard_service.py` -> `get_dashboard_stats`
- **Purpose:** Counts recruitment drives scheduled for the current academic season.
- **Core DBMS Concepts:** Temporal filtering; row counting.

```sql
SELECT COUNT(*) AS active_drives FROM RECRUITMENT_DRIVE rd WHERE
```

### DSH-09: Get Dashboard Stats: Query #9
- **Source File / Routine:** `services/dashboard_service.py` -> `get_dashboard_stats`
- **Purpose:** Executive dashboard visualization query.
- **Core DBMS Concepts:** Relational aggregation and analytics.

```sql
SELECT 
            COUNT(i.Internship_ID) AS total_internships,
            SUM(CASE WHEN i.Internship_Type = 'Mandatory' THEN 1 ELSE 0 END) AS mandatory_internships,
            SUM(CASE WHEN i.Internship_Type = 'Additional' THEN 1 ELSE 0 END) AS additional_internships,
            COUNT(DISTINCT i.Student_ID) AS distinct_students_interned
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        WHERE
```

### DSH-17: Dashboard Chart 7: Offer Status Breakdown Doughnut Chart
- **Source File / Routine:** `services/dashboard_service.py` -> `get_offer_status_chart_data`
- **Purpose:** Generates doughnut chart visualizing the proportion of Offered, Accepted, Declined, and Joined offers.
- **Core DBMS Concepts:** Categorical grouping; proportional distribution.

```sql
SELECT 
            p.Offer_Status,
            COUNT(*) AS count
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        WHERE
```

### DSH-18: Dashboard Chart 8: Mandatory vs Additional Internship Doughnut Chart
- **Source File / Routine:** `services/dashboard_service.py` -> `get_internship_breakdown_chart_data`
- **Purpose:** Visualizes attachment proportions across Mandatory I1, Mandatory I2, and Additional industry experiences.
- **Core DBMS Concepts:** Categorical grouping; degree compliance distribution.

```sql
SELECT 
            CASE 
                WHEN i.Internship_Type = 'Mandatory' AND i.Internship_No = 1 THEN 'Mandatory #1 (Sem 3)'
                WHEN i.Internship_Type = 'Mandatory' AND i.Internship_No = 2 THEN 'Mandatory #2 (Sem 5)'
                ELSE 'Additional Internships'
            END AS category,
            COUNT(*) AS count
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        WHERE
```

### DSH-19: Institutional Reporting: Multi-Filtered Master Cohort Synthesis
- **Source File / Routine:** `services/dashboard_service.py` -> `get_comprehensive_report_data`
- **Purpose:** Generates multi-dimensional institutional accreditation reports synthesized across student, placement, and internship entities.
- **Core DBMS Concepts:** Multi-way outer join; complex dynamic WHERE filtering; accreditation summary metrics.

```sql
SELECT 
            s.Student_ID,
            s.Roll_No,
            CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Full_Name,
            s.Email,
            s.Branch,
            s.Batch_Year,
            s.CGPA,
            COUNT(DISTINCT p.Placement_ID) AS Total_Offers,
            MAX(CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN c.Company_Name ELSE NULL END) AS Placed_Company,
            MAX(CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN p.Package ELSE NULL END) AS Placed_Package,
            MAX(CASE WHEN p.Offer_Status IN ('Accepted', 'Joined') THEN p.Offer_Status ELSE NULL END) AS Final_Status,
            COUNT(DISTINCT CASE WHEN i.Internship_Type = 'Mandatory' AND i.Internship_No = 1 THEN i.Internship_ID ELSE NULL END) AS Has_Mandatory_1,
            COUNT(DISTINCT CASE WHEN i.Internship_Type = 'Mandatory' AND i.Internship_No = 2 THEN i.Internship_ID ELSE NULL END) AS Has_Mandatory_2,
            COUNT(DISTINCT CASE WHEN i.Internship_Type = 'Additional' THEN i.Internship_ID ELSE NULL END) AS Additional_Internship_Count
        FROM STUDENT s
        LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
        LEFT JOIN COMPANY c ON p.Company_ID = c.Company_ID
        LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
        WHERE
```

---

## Category: Compliance and eligibility (18 Queries)

> Category Focus: Systematic revision of backend routines, transaction hooks, duplicate validation patterns, and relational operations governing **compliance and eligibility**.

### PLC-22: Eligibility Check: Retrieve Student Academic Metrics
- **Source File / Routine:** `services/placement_service.py` -> `check_candidate_eligibility_for_opportunity`
- **Purpose:** Fetches candidate CGPA, branch, and active backlogs to evaluate eligibility.
- **Core DBMS Concepts:** Primary key point lookup.

```sql
SELECT Student_ID, Roll_No, First_Name, Last_Name, Branch, CGPA, Backlogs FROM STUDENT WHERE Student_ID = %s
```

### PLC-23: Eligibility Check: Retrieve Opportunity Cutoff Criteria
- **Source File / Routine:** `services/placement_service.py` -> `check_candidate_eligibility_for_opportunity`
- **Purpose:** Fetches minimum CGPA, maximum allowed backlogs, and allowed branches for a job opportunity.
- **Core DBMS Concepts:** Relational equi-join; cutoff criteria retrieval.

```sql
SELECT o.Opportunity_ID, o.Role, o.Package_Stipend,
               e.Eligibility_ID, e.Minimum_CGPA, e.Max_Backlogs, e.Eligible_Branch, e.Other_Criteria
        FROM OPPORTUNITY o
        LEFT JOIN ELIGIBILITY e ON o.Opportunity_ID = e.Opportunity_ID
        WHERE o.Opportunity_ID = %s
```

### PLC-24: Eligibility Check: Retrieve Department Eligibility List
- **Source File / Routine:** `services/placement_service.py` -> `check_candidate_eligibility_for_opportunity`
- **Purpose:** Retrieves all allowed engineering branches for the opportunity.
- **Core DBMS Concepts:** Child table scan.

```sql
SELECT Branch FROM ELIGIBILITY_BRANCH WHERE Eligibility_ID = %s ORDER BY Branch
```

### INT-01: Internship Eligibility: Fetch Student Academic Snapshot
- **Source File / Routine:** `services/internship_service.py` -> `check_internship_eligibility`
- **Purpose:** Fetches student current CGPA, branch, batch year, and active backlogs.
- **Core DBMS Concepts:** Primary key lookup.

```sql
SELECT Student_ID, Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs FROM STUDENT WHERE Student_ID = %s
```

### INT-02: Internship Eligibility: Retrieve Requirement Rule Parameters
- **Source File / Routine:** `services/internship_service.py` -> `check_internship_eligibility`
- **Purpose:** Retrieves requirement rule definition, required result semester, and reporting semester.
- **Core DBMS Concepts:** Rule metadata retrieval.

```sql
SELECT Requirement_ID, Internship_No, Required_Result_Semester, Report_Submission_Semester, Credits, Prescribed_Period FROM INTERNSHIP_REQUIREMENT WHERE Internship_No = %s
```

### INT-03: Internship Eligibility: Retrieve Prerequisite Semester SGPA
- **Source File / Routine:** `services/internship_service.py` -> `check_internship_eligibility`
- **Purpose:** Fetches historical SGPA performance for the prerequisite semester to enforce the >= 6.00 threshold.
- **Core DBMS Concepts:** Prerequisite academic rule validation (Sem 3 for I1, Sem 5 for I2); academic constraint checking.

```sql
SELECT Result_ID, Semester, SGPA, Total_Credits FROM SEMESTER_RESULT WHERE Student_ID = %s AND Semester = %s
```

### INT-17: Degree Compliance: Roster of Candidates Missing Mandatory Attachments
- **Source File / Routine:** `services/internship_service.py` -> `get_students_missing_mandatory_internships`
- **Purpose:** Identifies candidates who have not yet completed Mandatory Internship 1 or Mandatory Internship 2.
- **Core DBMS Concepts:** Relational outer anti-join (R ▷ S); missing requirement detection.

```sql
SELECT 
            s.Student_ID,
            s.Roll_No,
            s.First_Name,
            s.Last_Name,
            s.Branch,
            s.Batch_Year,
            s.CGPA,
            s.Email,
            CASE WHEN i1.Internship_ID IS NOT NULL THEN 'Completed' ELSE 'MISSING' END AS Mandatory_I1_Status,
            CASE WHEN i2.Internship_ID IS NOT NULL THEN 'Completed' ELSE 'MISSING' END AS Mandatory_I2_Status,
            COALESCE(c1.Company_Name, 'None') AS I1_Company,
            COALESCE(c2.Company_Name, 'None') AS I2_Company
        FROM STUDENT s
        LEFT JOIN INTERNSHIP i1 ON s.Student_ID = i1.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = 'Mandatory'
        LEFT JOIN COMPANY c1 ON i1.Company_ID = c1.Company_ID
        LEFT JOIN INTERNSHIP i2 ON s.Student_ID = i2.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = 'Mandatory'
        LEFT JOIN COMPANY c2 ON i2.Company_ID = c2.Company_ID
        WHERE
```

### INT-20: Get Batch Compliance Reports: Query #20
- **Source File / Routine:** `services/internship_service.py` -> `get_batch_compliance_reports`
- **Purpose:** Internship domain operational query.
- **Core DBMS Concepts:** Relational query execution.

```sql
SELECT 
            s.Batch_Year,
            COUNT(DISTINCT s.Student_ID) AS total_students,
            COUNT(DISTINCT CASE WHEN i.Internship_No = 1 AND i.Internship_Type = 'Mandatory' THEN s.Student_ID END) AS i1_completed,
            COUNT(DISTINCT CASE WHEN i.Internship_No = 2 AND i.Internship_Type = 'Mandatory' THEN s.Student_ID END) AS i2_completed,
            COUNT(DISTINCT CASE WHEN i.Internship_Type = 'Additional' THEN i.Internship_ID END) AS additional_count,
            ROUND(COALESCE(AVG(i.Stipend), 0), 2) AS avg_stipend
        FROM STUDENT s
        LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
        GROUP BY s.Batch_Year
        ORDER BY s.Batch_Year ASC
```

### INT-21: Batch Compliance: Both Mandatory Completed per Batch
- **Source File / Routine:** `services/internship_service.py` -> `get_batch_compliance_reports`
- **Purpose:** Computes total candidates fully compliant with both degree internship requirements per graduating batch.
- **Core DBMS Concepts:** Degree certification audit; cohort aggregation.

```sql
SELECT s.Batch_Year, COUNT(DISTINCT s.Student_ID) AS both_completed
        FROM STUDENT s
        JOIN INTERNSHIP i1 ON s.Student_ID = i1.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = 'Mandatory'
        JOIN INTERNSHIP i2 ON s.Student_ID = i2.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = 'Mandatory'
        GROUP BY s.Batch_Year
```

### OPP-09: List Opportunities: Branch Eligibility Predicate
- **Source File / Routine:** `services/opportunity_service.py` -> `list_opportunities`
- **Purpose:** Filters opportunities available to a specific academic branch.
- **Core DBMS Concepts:** Disjunctive pattern matching.

```sql
(e.Eligible_Branch LIKE %s 
             OR EXISTS (SELECT 1 FROM ELIGIBILITY_BRANCH eb WHERE eb.Eligibility_ID = e.Eligibility_ID AND eb.Branch = %s))
```

### DRV-22: Get Drive: Retrieve Department Eligibility List
- **Source File / Routine:** `services/drive_service.py` -> `get_drive`
- **Purpose:** Fetches eligible engineering branches for drive opportunities.
- **Core DBMS Concepts:** Branch eligibility projection.

```sql
SELECT Branch FROM ELIGIBILITY_BRANCH WHERE Eligibility_ID = %s ORDER BY Branch
```

### CRS-10: Delete Course: Audit Active Student Enrollments
- **Source File / Routine:** `services/course_service.py` -> `delete_course`
- **Purpose:** Prevents deleting a course if active student enrollments exist.
- **Core DBMS Concepts:** Referential integrity guard; protected delete enforcement.

```sql
SELECT COUNT(*) AS total FROM STUDENT_COURSE WHERE Course_ID = %s
```

### 10.8: Verification Header: Global Schema Cardinality Audit
- **Source File / Routine:** `verify.sql` -> `Schema Verification Script (Statement 1)`
- **Purpose:** Outputs an informational header message signaling the start of full-database table row count verification.
- **Core DBMS Concepts:** Scalar literal expression projection.

```sql
SELECT 'Row Counts across all tables:' AS info;
```

### 10.9: Global Multi-Table Cardinality & Population Audit
- **Source File / Routine:** `verify.sql` -> `Schema Verification Script (Statement 2)`
- **Purpose:** Calculates the exact record count across all 18 core database relations via UNION ALL to confirm successful seeding, data persistence, and table accessibility.
- **Core DBMS Concepts:** Multi-relation set union (UNION ALL) and aggregate cardinality evaluation (COUNT).

```sql
SELECT 'UNIVERSITY' AS table_name, COUNT(*) AS row_count FROM UNIVERSITY
UNION ALL SELECT 'COURSE', COUNT(*) FROM COURSE
UNION ALL SELECT 'STUDENT', COUNT(*) FROM STUDENT
UNION ALL SELECT 'STUDENT_PHONE', COUNT(*) FROM STUDENT_PHONE
UNION ALL SELECT 'STUDENT_SKILL', COUNT(*) FROM STUDENT_SKILL
UNION ALL SELECT 'STUDENT_PROFILE', COUNT(*) FROM STUDENT_PROFILE
UNION ALL SELECT 'RESUME', COUNT(*) FROM RESUME
UNION ALL SELECT 'EDUCATION_DOCUMENT', COUNT(*) FROM EDUCATION_DOCUMENT
UNION ALL SELECT 'SEMESTER_RESULT', COUNT(*) FROM SEMESTER_RESULT
UNION ALL SELECT 'COMPANY', COUNT(*) FROM COMPANY
UNION ALL SELECT 'RECRUITMENT_DRIVE', COUNT(*) FROM RECRUITMENT_DRIVE
UNION ALL SELECT 'OPPORTUNITY', COUNT(*) FROM OPPORTUNITY
UNION ALL SELECT 'ELIGIBILITY', COUNT(*) FROM ELIGIBILITY
UNION ALL SELECT 'SELECTION_PROCESS', COUNT(*) FROM SELECTION_PROCESS
UNION ALL SELECT 'INTERNSHIP_REQUIREMENT', COUNT(*) FROM INTERNSHIP_REQUIREMENT
UNION ALL SELECT 'INTERNSHIP', COUNT(*) FROM INTERNSHIP
UNION ALL SELECT 'PLACEMENT', COUNT(*) FROM PLACEMENT
UNION ALL SELECT 'PLACEMENT_SKILL', COUNT(*) FROM PLACEMENT_SKILL;
```

### 10.10: Verification Header: Referential Integrity & Orphaned Row Audit
- **Source File / Routine:** `verify.sql` -> `Schema Verification Script (Statement 3)`
- **Purpose:** Emits an audit milestone notification denoting the execution of comprehensive foreign key orphan detection across all parent-child relationships.
- **Core DBMS Concepts:** Scalar literal expression projection and audit checkpoint logging.

```sql
SELECT 'FK Referential Integrity Verification (Orphaned row checks - must all be 0):' AS info;
```

### 10.12: Verification Header: Offer Distribution Analytics Audit
- **Source File / Routine:** `verify.sql` -> `Schema Verification Script (Statement 5)`
- **Purpose:** Emits section header designating verification of placement offer distribution across the entire enrolled student cohort.
- **Core DBMS Concepts:** Scalar literal expression projection.

```sql
SELECT 'Placement Offer Count Distribution per Student:' AS info;
```

### 10.14: View Integrity Validation: v_placed_students
- **Source File / Routine:** `schema.sql / verify.sql` -> `Database View Audit (v_placed_students)`
- **Purpose:** Validates the structural definition, execution plan, and relational projection of the v_placed_students view by executing a test query against the virtual relation.
- **Core DBMS Concepts:** Relational view evaluation, virtual table projection, and query rewriting.

```sql
SELECT Student_ID, Student_Name, Branch, Company_Name, Package, Placement_Year FROM v_placed_students LIMIT 5;
```

### 10.15: View Integrity Validation: v_active_internships
- **Source File / Routine:** `schema.sql / verify.sql` -> `Database View Audit (v_active_internships)`
- **Purpose:** Audits the execution and filtering logic of the v_active_internships view to ensure currently active and ongoing internships are accurately identified.
- **Core DBMS Concepts:** Temporal predicate evaluation within relational view views.

```sql
SELECT Internship_ID, Student_Name, Branch, Company_Name, Role, Start_Date, End_Date FROM v_active_internships LIMIT 5;
```

---

## Category: Reports and analytics (42 Queries)

> Category Focus: Systematic revision of backend routines, transaction hooks, duplicate validation patterns, and relational operations governing **reports and analytics**.

### 9.1: A1. List All Registered Students
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['students_all'] / execute_saved_query()`
- **Purpose:** Production saved report query 'A1. List All Registered Students' in category 'Students'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Relational projection (π) and lexicographical multi-attribute ordering (ORDER BY Batch_Year, Branch, Student_Name).

```sql
SELECT Student_ID, Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Student_Name,
       Branch, Batch_Year, CGPA, Backlogs
FROM STUDENT
ORDER BY Batch_Year, Branch, Student_Name;
```

### 9.2: A2. Students of Specific Branch and Batch
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['students_branch_batch'] / execute_saved_query()`
- **Purpose:** Production saved report query 'A2. Students of Specific Branch and Batch' in category 'Students'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Equality selection (σ) on composite index (Branch, Batch_Year) with descending sort on continuous numeric CGPA.

```sql
SELECT Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Student_Name, Branch, Batch_Year, CGPA
FROM STUDENT
WHERE Branch = %s AND Batch_Year = %s
ORDER BY CGPA DESC;
```

### 9.4: A4. Students Possessing a Particular Skill
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['students_by_skill'] / execute_saved_query()`
- **Purpose:** Production saved report query 'A4. Students Possessing a Particular Skill' in category 'Students'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Relational equi-join connecting master STUDENT with 1NF child entity STUDENT_SKILL using foreign key traversal.

```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.CGPA, sk.Skill
FROM STUDENT s
JOIN STUDENT_SKILL sk ON sk.Student_ID = s.Student_ID
WHERE sk.Skill = %s
ORDER BY s.CGPA DESC;
```

### 9.5: A5. Students with High CGPA and Zero Backlogs
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['students_high_cgpa_nobacklogs'] / execute_saved_query()`
- **Purpose:** Production saved report query 'A5. Students with High CGPA and Zero Backlogs' in category 'Students'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Multi-attribute selection on continuous domain (CGPA >= cutoff) and discrete domain (Backlogs = 0) utilizing secondary B+ tree index.

```sql
SELECT Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Student_Name, Branch, Batch_Year, CGPA, Backlogs
FROM STUDENT
WHERE CGPA >= %s AND Backlogs = 0
ORDER BY CGPA DESC;
```

### 9.7: ADD-2. Students with CGPA Above Institutional Average
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['students_above_avg_cgpa'] / execute_saved_query()`
- **Purpose:** Production saved report query 'ADD-2. Students with CGPA Above Institutional Average' in category 'Students'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Scalar non-correlated subquery dynamically calculating the global mean CGPA and projecting the individual variance delta at runtime.

```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.Batch_Year, s.CGPA,
       ROUND((SELECT AVG(CGPA) FROM STUDENT), 2) AS Benchmark_Avg_CGPA,
       ROUND(s.CGPA - (SELECT AVG(CGPA) FROM STUDENT), 2) AS Delta_From_Avg
FROM STUDENT s
WHERE s.CGPA > (SELECT AVG(CGPA) FROM STUDENT)
ORDER BY s.CGPA DESC;
```

### 9.8: D11. Search Student by Name (Disjunctive Wildcard)
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['students_name_search'] / execute_saved_query()`
- **Purpose:** Production saved report query 'D11. Search Student by Name (Disjunctive Wildcard)' in category 'Students'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Non-anchored pattern matching (LIKE %...%) disjunctively evaluated across composite names, outer joined to retrieve placement status.

```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       s.Branch, s.CGPA, COALESCE(c.Company_Name, 'Unplaced') AS Joined_Company, p.Package
FROM STUDENT s
LEFT JOIN PLACEMENT p ON p.Student_ID = s.Student_ID AND p.Joined = 'Yes'
LEFT JOIN COMPANY   c ON c.Company_ID = p.Company_ID
WHERE s.First_Name LIKE %s OR s.Last_Name LIKE %s
ORDER BY s.Student_ID;
```

### 9.9: B1. Placed Students with Company and Compensation
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['placements_all_joined'] / execute_saved_query()`
- **Purpose:** Production saved report query 'B1. Placed Students with Company and Compensation' in category 'Placements'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Relational view abstraction (V_PLACEMENT_DETAIL) encapsulating multi-table equi-join filtered by Joined = 'Yes' sorted by package descending.

```sql
SELECT Roll_No, Student_Name, Branch, Batch_Year, Company_Name, Role, Package, Placement_Year
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
ORDER BY Package DESC;
```

### 9.10: B2. Placements Recruited by Specific Company
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['placements_by_company'] / execute_saved_query()`
- **Purpose:** Production saved report query 'B2. Placements Recruited by Specific Company' in category 'Placements'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Parameterized relational equi-join with point-filter on indexed corporate entity evaluating organization-level hiring yield.

```sql
SELECT Student_Name, Branch, Batch_Year, Role, Package, Placement_Year, Joined
FROM V_PLACEMENT_DETAIL
WHERE Company_Name = %s
ORDER BY Placement_Year, Package DESC;
```

### 9.12: B4. Year-Wise Placement Statistics & Cohort Trends
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['placements_year_stats'] / execute_saved_query()`
- **Purpose:** Production saved report query 'B4. Year-Wise Placement Statistics & Cohort Trends' in category 'Placements'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Temporal aggregation grouping by academic cohort year measuring historical compensation escalation and placement volume.

```sql
SELECT Placement_Year,
       COUNT(*)               AS Students_Placed,
       ROUND(AVG(Package), 2) AS Avg_Package,
       MAX(Package)           AS Highest_Package
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
GROUP BY Placement_Year
ORDER BY Placement_Year;
```

### 9.13: B5. Company-Wise Hiring Volume & Salary Metrics
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['placements_company_hiring'] / execute_saved_query()`
- **Purpose:** Production saved report query 'B5. Company-Wise Hiring Volume & Salary Metrics' in category 'Placements'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Multi-column grouping (Company_ID, Company_Name, Company_Type) strictly preserving functional dependencies under ANSI SQL.

```sql
SELECT Company_Name, Company_Type,
       COUNT(*)               AS Students_Joined,
       ROUND(AVG(Package), 2) AS Avg_Package,
       MAX(Package)           AS Highest_Package
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
GROUP BY Company_ID, Company_Name, Company_Type
ORDER BY Students_Joined DESC, Avg_Package DESC;
```

### 9.15: B7. Placement Percentage by Branch and Batch
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['placements_branch_percent'] / execute_saved_query()`
- **Purpose:** Production saved report query 'B7. Placement Percentage by Branch and Batch' in category 'Placements'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Cohort grouping evaluating existential subquery membership (SUM(EXISTS...)) to compute institutional placement success rates.

```sql
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
```

### 9.17: B9. Students Receiving Pre-Placement Offers (PPO)
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['placements_ppo_offers'] / execute_saved_query()`
- **Purpose:** Production saved report query 'B9. Students Receiving Pre-Placement Offers (PPO)' in category 'Placements'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Selection on categorical ENUM attribute (Is_PPO = 'Yes') measuring direct conversion yield from internships to corporate placements.

```sql
SELECT Student_Name, Branch, Company_Name, Package, Placement_Year, Joined
FROM V_PLACEMENT_DETAIL
WHERE Is_PPO = 'Yes'
ORDER BY Placement_Year, Package DESC;
```

### 9.18: B11. CGPA Performance Bands vs Average Package
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['placements_cgpa_bands'] / execute_saved_query()`
- **Purpose:** Production saved report query 'B11. CGPA Performance Bands vs Average Package' in category 'Placements'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Conditional value discretization using CASE WHEN mapping continuous CGPA metrics into academic achievement tiers.

```sql
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
```

### 9.19: B14. Placement Packages Above Specified Threshold
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['placements_above_threshold'] / execute_saved_query()`
- **Purpose:** Production saved report query 'B14. Placement Packages Above Specified Threshold' in category 'Placements'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Decimal numerical inequality filtering parameterized safely, isolating elite compensation offers across hiring partners.

```sql
SELECT Student_Name, Branch, Company_Name, Role, Package, Placement_Year
FROM V_PLACEMENT_DETAIL
WHERE Package >= %s AND Joined = 'Yes'
ORDER BY Package DESC;
```

### 9.20: C1. All Internships of One Student (Calculated Duration)
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['internships_student_history'] / execute_saved_query()`
- **Purpose:** Production saved report query 'C1. All Internships of One Student (Calculated Duration)' in category 'Internships'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Dynamic calculation of derived attribute (Duration_Months via DATEDIFF) at query runtime, preventing physical storage redundancy.

```sql
SELECT Internship_No, Internship_Type, Company_Name, Role,
       Start_Date, End_Date, Duration_Months, Stipend,
       Credits, Report_Semester, Report_Grade
FROM V_INTERNSHIP_DETAIL
WHERE Roll_No = %s
ORDER BY Internship_No;
```

### 9.21: C2. Internships Hosted by Specific Organization
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['internships_by_company'] / execute_saved_query()`
- **Purpose:** Production saved report query 'C2. Internships Hosted by Specific Organization' in category 'Internships'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Weak entity to strong corporate entity relational join filtered by organization name, analyzing internship engagement.

```sql
SELECT Student_Name, Branch, Internship_No, Role, Start_Date, End_Date, Stipend
FROM V_INTERNSHIP_DETAIL
WHERE Company_Name = %s
ORDER BY Start_Date;
```

### 9.22: C3. Mandatory Internship Completion Audit
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['internships_mandatory_compliance'] / execute_saved_query()`
- **Purpose:** Production saved report query 'C3. Mandatory Internship Completion Audit' in category 'Internships'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Left outer join with conditional aggregation (COUNT(CASE WHEN...)) ensuring students with zero internships are preserved in audit.

```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       COUNT(CASE WHEN i.Internship_Type = 'Mandatory'  THEN 1 END) AS Mandatory_Done,
       COUNT(CASE WHEN i.Internship_Type = 'Additional' THEN 1 END) AS Additional_Done,
       COUNT(i.Internship_No)                                       AS Total_Internships
FROM STUDENT s
LEFT JOIN INTERNSHIP i ON i.Student_ID = s.Student_ID
GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name
ORDER BY Mandatory_Done ASC, Total_Internships ASC;
```

### 9.24: C6. Average Monthly Stipend Across Companies
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['internships_avg_stipend_company'] / execute_saved_query()`
- **Purpose:** Production saved report query 'C6. Average Monthly Stipend Across Companies' in category 'Internships'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Aggregate reduction evaluating compensation metrics (mean and maximum monthly stipend) across internship sponsor firms.

```sql
SELECT Company_Name,
       COUNT(*)               AS Interns,
       ROUND(AVG(Stipend), 0) AS Avg_Stipend,
       MAX(Stipend)           AS Highest_Stipend
FROM V_INTERNSHIP_DETAIL
GROUP BY Company_ID, Company_Name
ORDER BY Avg_Stipend DESC;
```

### 9.25: C12. Internships Active in Date Range
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['internships_date_range'] / execute_saved_query()`
- **Purpose:** Production saved report query 'C12. Internships Active in Date Range' in category 'Internships'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Temporal boundary filtering on calendar date types (Start_Date >= and End_Date <=) isolating seasonal internship batches.

```sql
SELECT Student_Name, Internship_No, Company_Name, Role, Start_Date, End_Date, Stipend
FROM V_INTERNSHIP_DETAIL
WHERE Start_Date >= %s AND End_Date <= %s
ORDER BY Start_Date;
```

### 9.26: D1. Internships Converted to Full-Time Placements (PPO Track)
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['combined_internship_to_job'] / execute_saved_query()`
- **Purpose:** Production saved report query 'D1. Internships Converted to Full-Time Placements (PPO Track)' in category 'Combined'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Composite multi-column inner equi-join matching on (Student_ID AND Company_ID) correlating internship history with final placement.

```sql
SELECT DISTINCT p.Student_Name, p.Branch, p.Company_Name, p.Package, p.Is_PPO
FROM V_PLACEMENT_DETAIL p
JOIN INTERNSHIP i
  ON i.Student_ID = p.Student_ID AND i.Company_ID = p.Company_ID
WHERE p.Joined = 'Yes'
ORDER BY p.Package DESC;
```

### 9.27: D2. Most Prevalent Technical Skills Among Students
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['combined_popular_skills'] / execute_saved_query()`
- **Purpose:** Production saved report query 'D2. Most Prevalent Technical Skills Among Students' in category 'Combined'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Frequency distribution across 1NF decomposed multi-valued skill entities ranking student technical capabilities.

```sql
SELECT Skill, COUNT(*) AS Students_With_Skill
FROM STUDENT_SKILL
GROUP BY Skill
ORDER BY Students_With_Skill DESC, Skill;
```

### 9.28: D3. In-Demand Skills Evaluated for Placement Offers
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['combined_indemand_skills'] / execute_saved_query()`
- **Purpose:** Production saved report query 'D3. In-Demand Skills Evaluated for Placement Offers' in category 'Combined'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Demand-side aggregation grouping through bridge relation PLACEMENT_SKILL to determine market skill requirements.

```sql
SELECT ps.Skill, COUNT(*) AS Times_Selected_For
FROM PLACEMENT_SKILL ps
GROUP BY ps.Skill
ORDER BY Times_Selected_For DESC, ps.Skill;
```

### 9.29: D4. Average Package by Technical Skill Evaluated
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['combined_skill_avg_package'] / execute_saved_query()`
- **Purpose:** Production saved report query 'D4. Average Package by Technical Skill Evaluated' in category 'Combined'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Many-to-many bridge relation traversal connecting technical competencies to realized salary outcomes with mean aggregation.

```sql
SELECT ps.Skill, COUNT(*) AS Students, ROUND(AVG(p.Package), 2) AS Avg_Package
FROM PLACEMENT_SKILL ps
JOIN PLACEMENT p ON p.Placement_ID = ps.Placement_ID
WHERE p.Joined = 'Yes'
GROUP BY ps.Skill
ORDER BY Avg_Package DESC;
```

### 9.30: D5. Technical Skills Targeted by Specific Company
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['combined_company_skills'] / execute_saved_query()`
- **Purpose:** Production saved report query 'D5. Technical Skills Targeted by Specific Company' in category 'Combined'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Three-table relational equi-join traversing bridge entity PLACEMENT_SKILL to PLACEMENT and COMPANY with selective filter.

```sql
SELECT DISTINCT c.Company_Name, ps.Skill
FROM PLACEMENT_SKILL ps
JOIN PLACEMENT p ON p.Placement_ID = ps.Placement_ID
JOIN COMPANY c   ON c.Company_ID  = p.Company_ID
WHERE c.Company_Name = %s
ORDER BY ps.Skill;
```

### 9.31: D6. Dual-Role Corporate Partners (Internships + Placements)
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['combined_dual_partners'] / execute_saved_query()`
- **Purpose:** Production saved report query 'D6. Dual-Role Corporate Partners (Internships + Placements)' in category 'Combined'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Dual correlated existential predicates (EXISTS ... AND EXISTS ...) proving relationship set intersection across distinct operational scopes.

```sql
SELECT c.Company_Name, c.Company_Type,
       (SELECT COUNT(*) FROM INTERNSHIP i WHERE i.Company_ID = c.Company_ID) AS Interns_Taken,
       (SELECT COUNT(*) FROM PLACEMENT  p WHERE p.Company_ID = c.Company_ID) AS Offers_Made
FROM COMPANY c
WHERE EXISTS (SELECT 1 FROM INTERNSHIP i WHERE i.Company_ID = c.Company_ID)
  AND EXISTS (SELECT 1 FROM PLACEMENT  p WHERE p.Company_ID = c.Company_ID);
```

### 9.32: D7. Polymorphic Corporate Activity Profile (UNION ALL)
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['combined_company_polymorphic'] / execute_saved_query()`
- **Purpose:** Production saved report query 'D7. Polymorphic Corporate Activity Profile (UNION ALL)' in category 'Combined'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Set Union (UNION ALL) combining distinct activity records into a unified polymorphic schema with synthetic discriminator column.

```sql
SELECT 'Internship' AS Record_Type, Student_Name, Branch, Role, NULL AS Package, Stipend
FROM V_INTERNSHIP_DETAIL
WHERE Company_Name = %s
UNION ALL
SELECT 'Placement' AS Record_Type, Student_Name, Branch, Role, Package, NULL AS Stipend
FROM V_PLACEMENT_DETAIL
WHERE Company_Name = %s
ORDER BY Record_Type, Student_Name;
```

### 9.33: D8. Comprehensive Student Career Synthesis
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['combined_full_career_report'] / execute_saved_query()`
- **Purpose:** Production saved report query 'D8. Comprehensive Student Career Synthesis' in category 'Combined'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Multiple correlated scalar subqueries synthesizing academic performance, technical skills, internship volume, and placement outcomes into a master tuple.

```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       s.Branch, s.Batch_Year, s.CGPA,
       (SELECT GROUP_CONCAT(sk.Skill SEPARATOR ', ')
          FROM STUDENT_SKILL sk WHERE sk.Student_ID = s.Student_ID)              AS Extra_Skills,
       (SELECT COUNT(*) FROM INTERNSHIP i WHERE i.Student_ID = s.Student_ID)     AS Internships_Done,
       (SELECT c.Company_Name FROM PLACEMENT p JOIN COMPANY c ON c.Company_ID = p.Company_ID
         WHERE p.Student_ID = s.Student_ID AND p.Joined = 'Yes' LIMIT 1)         AS Joined_Company,
       (SELECT p.Package FROM PLACEMENT p
         WHERE p.Student_ID = s.Student_ID AND p.Joined = 'Yes' LIMIT 1)         AS Package
FROM STUDENT s
ORDER BY s.Batch_Year, s.Branch, s.Roll_No;
```

### 9.34: ADD-3A. Skill Profile Comparison: Placed vs Non-Placed Cohorts
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['combined_skills_cohort_comparison'] / execute_saved_query()`
- **Purpose:** Production saved report query 'ADD-3A. Skill Profile Comparison: Placed vs Non-Placed Cohorts' in category 'Combined'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Multi-way outer join with conditional aggregation comparing total acquired skills, mean skill density, and unique skills acquired across cohorts.

```sql
SELECT
    CASE WHEN p.Joined = 'Yes' THEN 'Placed Students' ELSE 'Non-Placed Students' END AS Placement_Status,
    COUNT(DISTINCT s.Student_ID) AS Total_Students,
    COUNT(sk.Skill) AS Total_Skills_Reported,
    ROUND(COUNT(sk.Skill) / COUNT(DISTINCT s.Student_ID), 2) AS Avg_Skills_Per_Student,
    GROUP_CONCAT(DISTINCT sk.Skill ORDER BY sk.Skill SEPARATOR ', ') AS Unique_Skills_Acquired
FROM STUDENT s
LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID AND p.Joined = 'Yes'
LEFT JOIN STUDENT_SKILL sk ON s.Student_ID = sk.Student_ID
GROUP BY CASE WHEN p.Joined = 'Yes' THEN 'Placed Students' ELSE 'Non-Placed Students' END;
```

### 9.36: E2. Year-Wise Placement Statistics & YoY Growth Trends
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['report_year_placement_stats'] / execute_saved_query()`
- **Purpose:** Production saved report query 'E2. Year-Wise Placement Statistics & YoY Growth Trends' in category 'Executive Reports'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Temporal cohort aggregation combined with the LAG() analytic window function to compute year-over-year compensation escalation and growth rates across academic recruitment cycles.

```sql
WITH YearlyPlacements AS (
    SELECT
        p.Placement_Year,
        COUNT(p.Placement_ID) AS Total_Offers,
        COUNT(DISTINCT p.Student_ID) AS Total_Candidates_Offered,
        COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' OR p.Offer_Status = 'Joined' THEN p.Student_ID END) AS Placed_Count,
        ROUND(AVG(p.Package), 2) AS Avg_Offered_Package,
        ROUND(AVG(CASE WHEN p.Joined = 'Yes' OR p.Offer_Status = 'Joined' THEN p.Package END), 2) AS Avg_Accepted_Package,
        MAX(p.Package) AS Highest_Package,
        MIN(p.Package) AS Lowest_Package,
        ROUND(SUM(CASE WHEN p.Joined = 'Yes' OR p.Offer_Status = 'Joined' THEN p.Package ELSE 0 END), 2) AS Total_Accepted_Volume
    FROM PLACEMENT p
    JOIN STUDENT s ON p.Student_ID = s.Student_ID
    GROUP BY p.Placement_Year
),
YearlyWithGrowth AS (
    SELECT
        y.*,
        LAG(y.Avg_Accepted_Package) OVER (ORDER BY y.Placement_Year ASC) AS Prev_Year_Avg,
        LAG(y.Placed_Count) OVER (ORDER BY y.Placement_Year ASC) AS Prev_Year_Placed
    FROM YearlyPlacements y
)
SELECT
    Placement_Year,
    Total_Offers,
    Total_Candidates_Offered,
    Placed_Count,
    Avg_Accepted_Package AS Avg_Package,
    Highest_Package,
    Lowest_Package,
    Total_Accepted_Volume,
    ROUND(COALESCE(Avg_Accepted_Package - Prev_Year_Avg, 0), 2) AS YoY_Package_Change,
    ROUND(COALESCE(100.0 * (Avg_Accepted_Package - Prev_Year_Avg) / NULLIF(Prev_Year_Avg, 0), 0), 1) AS YoY_Growth_Percent,
    DENSE_RANK() OVER (ORDER BY Placed_Count DESC, Avg_Accepted_Package DESC) AS Volume_Rank
FROM YearlyWithGrowth
ORDER BY Placement_Year DESC;
```

### 9.37: E3. Average, Median, and Highest Package Reports
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['report_package_statistics'] / execute_saved_query()`
- **Purpose:** Production saved report query 'E3. Average, Median, and Highest Package Reports' in category 'Executive Reports'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Advanced statistical reduction computing Mean, exact Median via ROW_NUMBER() partitioning, Population Standard Deviation (STDDEV_POP), and discrete Rank distributions across departments and individual offers.

```sql
WITH RankedByBranch AS (
    SELECT
        s.Branch,
        p.Package,
        ROW_NUMBER() OVER (PARTITION BY s.Branch ORDER BY p.Package ASC) AS row_num,
        COUNT(*) OVER (PARTITION BY s.Branch) AS total_count
    FROM PLACEMENT p
    JOIN STUDENT s ON p.Student_ID = s.Student_ID
    WHERE (p.Joined = 'Yes' OR p.Offer_Status = 'Joined')
),
BranchMedians AS (
    SELECT
        Branch,
        ROUND(AVG(Package), 2) AS Median_Package
    FROM RankedByBranch
    WHERE row_num IN (FLOOR((total_count + 1) / 2), CEIL((total_count + 1) / 2))
    GROUP BY Branch
),
BranchStats AS (
    SELECT
        s.Branch,
        COUNT(p.Placement_ID) AS Placed_Count,
        ROUND(AVG(p.Package), 2) AS Mean_Package,
        MAX(p.Package) AS Highest_Package,
        MIN(p.Package) AS Lowest_Package,
        ROUND(STDDEV_POP(p.Package), 2) AS Std_Dev
    FROM PLACEMENT p
    JOIN STUDENT s ON p.Student_ID = s.Student_ID
    WHERE (p.Joined = 'Yes' OR p.Offer_Status = 'Joined')
    GROUP BY s.Branch
)
SELECT
    bs.Branch,
    bs.Placed_Count,
    bs.Mean_Package,
    COALESCE(bm.Median_Package, bs.Mean_Package) AS Median_Package,
    bs.Highest_Package,
    bs.Lowest_Package,
    COALESCE(bs.Std_Dev, 0.00) AS Std_Dev,
    DENSE_RANK() OVER (ORDER BY bs.Mean_Package DESC) AS Branch_Rank
FROM BranchStats bs
LEFT JOIN BranchMedians bm ON bs.Branch = bm.Branch
ORDER BY Branch_Rank ASC;
```

### 9.38: E4. Company-Wise Hiring Ratios & Yield Metrics
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['report_company_hiring_stats'] / execute_saved_query()`
- **Purpose:** Production saved report query 'E4. Company-Wise Hiring Ratios & Yield Metrics' in category 'Executive Reports'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Multi-table relational aggregation traversing corporate recruiters, computing offer acceptance yield percentages, and applying DENSE_RANK() to classify top hiring partners.

```sql
WITH CompanyHiring AS (
    SELECT
        c.Company_ID,
        c.Company_Name,
        c.Company_Type,
        c.Industry,
        c.Location,
        COUNT(p.Placement_ID) AS Total_Offers_Extended,
        COUNT(DISTINCT p.Student_ID) AS Distinct_Candidates_Offered,
        COUNT(CASE WHEN p.Joined = 'Yes' OR p.Offer_Status = 'Joined' THEN 1 END) AS Accepted_Offers,
        ROUND(AVG(p.Package), 2) AS Avg_Offered_Package,
        ROUND(AVG(CASE WHEN p.Joined = 'Yes' OR p.Offer_Status = 'Joined' THEN p.Package END), 2) AS Avg_Accepted_Package,
        MAX(p.Package) AS Highest_Package,
        MIN(p.Package) AS Lowest_Package,
        ROUND(SUM(CASE WHEN p.Joined = 'Yes' OR p.Offer_Status = 'Joined' THEN p.Package ELSE 0 END), 2) AS Total_Compensation_Committed
    FROM COMPANY c
    LEFT JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
    GROUP BY c.Company_ID, c.Company_Name, c.Company_Type, c.Industry, c.Location
)
SELECT
    Company_ID,
    Company_Name,
    Company_Type,
    Industry,
    Location,
    Total_Offers_Extended,
    Distinct_Candidates_Offered,
    Accepted_Offers,
    ROUND(COALESCE(100.0 * Accepted_Offers / NULLIF(Total_Offers_Extended, 0), 0), 1) AS Acceptance_Rate_Percent,
    COALESCE(Avg_Offered_Package, 0.00) AS Avg_Offered_Package,
    COALESCE(Avg_Accepted_Package, 0.00) AS Avg_Accepted_Package,
    COALESCE(Highest_Package, 0.00) AS Highest_Package,
    COALESCE(Lowest_Package, 0.00) AS Lowest_Package,
    Total_Compensation_Committed,
    DENSE_RANK() OVER (ORDER BY Accepted_Offers DESC, Avg_Accepted_Package DESC) AS Hiring_Rank
FROM CompanyHiring
WHERE Total_Offers_Extended > 0
ORDER BY Accepted_Offers DESC, Total_Offers_Extended DESC;
```

### 9.39: E5. Multiple Placement Offer Analysis & Package Spread
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['report_multiple_offers_analysis'] / execute_saved_query()`
- **Purpose:** Production saved report query 'E5. Multiple Placement Offer Analysis & Package Spread' in category 'Executive Reports'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Post-aggregation cardinality filtering (HAVING COUNT(*) > 1) computing the financial spread between highest and lowest offers, aggregating offer catalogs via GROUP_CONCAT, and sorting by DENSE_RANK().

```sql
WITH MultiOfferStudents AS (
    SELECT
        s.Student_ID,
        s.Roll_No,
        CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Student_Name,
        s.Branch,
        s.Batch_Year,
        s.CGPA,
        COUNT(p.Placement_ID) AS Total_Offers,
        MAX(p.Package) AS Highest_Offer,
        MIN(p.Package) AS Lowest_Offer,
        ROUND(MAX(p.Package) - MIN(p.Package), 2) AS Package_Spread,
        MAX(CASE WHEN p.Joined = 'Yes' OR p.Offer_Status = 'Joined' THEN c.Company_Name END) AS Joined_Company,
        MAX(CASE WHEN p.Joined = 'Yes' OR p.Offer_Status = 'Joined' THEN p.Package END) AS Joined_Package,
        GROUP_CONCAT(CONCAT(c.Company_Name, ' (', p.Package, ' LPA - ', p.Offer_Status, ')') ORDER BY p.Package DESC SEPARATOR ' | ') AS All_Offers
    FROM STUDENT s
    JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
    JOIN COMPANY c ON p.Company_ID = c.Company_ID
    GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, s.Batch_Year, s.CGPA
    HAVING COUNT(p.Placement_ID) > 1
)
SELECT
    m.*,
    DENSE_RANK() OVER (ORDER BY m.Total_Offers DESC, m.Highest_Offer DESC) AS Offer_Rank
FROM MultiOfferStudents m
ORDER BY m.Total_Offers DESC, m.Highest_Offer DESC;
```

### 9.40: E6. Degree Internship Policy Compliance & Audits
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['report_internship_compliance'] / execute_saved_query()`
- **Purpose:** Production saved report query 'E6. Degree Internship Policy Compliance & Audits' in category 'Executive Reports'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Multi-condition aggregation auditing degree fulfillment of Mandatory Internship 1 and Mandatory Internship 2, tracking additional industry attachments and average compensation.

```sql
WITH StudentInternshipSummary AS (
    SELECT
        s.Student_ID,
        s.Roll_No,
        CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Student_Name,
        s.Branch,
        s.Batch_Year,
        s.CGPA,
        COUNT(DISTINCT CASE WHEN i.Internship_No = 1 AND i.Internship_Type = 'Mandatory' THEN i.Internship_ID END) AS Has_I1,
        COUNT(DISTINCT CASE WHEN i.Internship_No = 2 AND i.Internship_Type = 'Mandatory' THEN i.Internship_ID END) AS Has_I2,
        COUNT(DISTINCT CASE WHEN i.Internship_Type = 'Additional' THEN i.Internship_ID END) AS Additional_Count,
        ROUND(AVG(i.Stipend), 2) AS Avg_Stipend
    FROM STUDENT s
    LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
    GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, s.Batch_Year, s.CGPA
)
SELECT
    Branch,
    COUNT(*) AS Total_Students,
    SUM(Has_I1) AS I1_Completed,
    SUM(Has_I2) AS I2_Completed,
    SUM(CASE WHEN Has_I1 > 0 AND Has_I2 > 0 THEN 1 ELSE 0 END) AS Fully_Compliant,
    SUM(CASE WHEN Has_I1 = 0 OR Has_I2 = 0 THEN 1 ELSE 0 END) AS Non_Compliant,
    SUM(Additional_Count) AS Total_Additional,
    ROUND(100.0 * SUM(CASE WHEN Has_I1 > 0 AND Has_I2 > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS Compliance_Rate,
    ROUND(COALESCE(AVG(Avg_Stipend), 0), 2) AS Avg_Stipend,
    DENSE_RANK() OVER (ORDER BY ROUND(100.0 * SUM(CASE WHEN Has_I1 > 0 AND Has_I2 > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) DESC) AS Compliance_Rank
FROM StudentInternshipSummary
GROUP BY Branch
ORDER BY Branch ASC;
```

### 9.41: E7. Unplaced Student Roster & Outreach Priority Ranking
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['report_unplaced_students'] / execute_saved_query()`
- **Purpose:** Production saved report query 'E7. Unplaced Student Roster & Outreach Priority Ranking' in category 'Executive Reports'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Outer anti-join identifying unplaced candidates, evaluating institutional eligibility via conditional expression, and utilizing ROW_NUMBER() window partitioning by branch to prioritize outreach by CGPA.

```sql
WITH UnplacedStudents AS (
    SELECT
        s.Student_ID,
        s.Roll_No,
        CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Student_Name,
        s.Branch,
        s.Batch_Year,
        s.CGPA,
        s.Backlogs,
        s.Email,
        CASE WHEN s.Backlogs = 0 AND s.CGPA >= 6.00 THEN 'Eligible' ELSE 'Ineligible' END AS Placement_Eligibility,
        (SELECT COUNT(*) FROM PLACEMENT p WHERE p.Student_ID = s.Student_ID) AS Total_Offers_Received,
        (SELECT GROUP_CONCAT(ph.Phone_No SEPARATOR ', ') FROM STUDENT_PHONE ph WHERE ph.Student_ID = s.Student_ID) AS Contact_Phones,
        ROW_NUMBER() OVER (PARTITION BY s.Branch ORDER BY s.CGPA DESC) AS Branch_Priority_Rank,
        DENSE_RANK() OVER (ORDER BY s.CGPA DESC) AS Overall_CGPA_Rank
    FROM STUDENT s
    LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID AND (p.Joined = 'Yes' OR p.Offer_Status = 'Joined')
    WHERE p.Placement_ID IS NULL
)
SELECT * FROM UnplacedStudents ORDER BY Branch, Branch_Priority_Rank;
```

### 9.42: E8. CGPA Tiers vs Placement Conversion & Compensation
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['report_cgpa_vs_placement'] / execute_saved_query()`
- **Purpose:** Production saved report query 'E8. CGPA Tiers vs Placement Conversion & Compensation' in category 'Executive Reports'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Categorical tiering via CASE WHEN evaluating academic performance bands, calculating group placement conversion rates, and correlating academic excellence with starting compensation packages.

```sql
WITH StudentBands AS (
    SELECT
        s.Student_ID,
        s.CGPA,
        CASE
            WHEN s.CGPA >= 9.0 THEN '1. 9.0 & Above (Elite)'
            WHEN s.CGPA >= 8.0 THEN '2. 8.0 - 8.99 (High Distinction)'
            WHEN s.CGPA >= 7.0 THEN '3. 7.0 - 7.99 (First Class)'
            WHEN s.CGPA >= 6.0 THEN '4. 6.0 - 6.99 (Eligible / Pass)'
            ELSE '5. Below 6.0 (Under Cutoff)'
        END AS CGPA_Band,
        CASE WHEN p.Joined = 'Yes' OR p.Offer_Status = 'Joined' THEN 1 ELSE 0 END AS Is_Placed,
        CASE WHEN p.Joined = 'Yes' OR p.Offer_Status = 'Joined' THEN p.Package END AS Placed_Package,
        p.Placement_ID
    FROM STUDENT s
    LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
)
SELECT
    CGPA_Band,
    COUNT(DISTINCT Student_ID) AS Total_Students,
    COUNT(DISTINCT CASE WHEN Is_Placed = 1 THEN Student_ID END) AS Placed_Students,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN Is_Placed = 1 THEN Student_ID END) / COUNT(DISTINCT Student_ID), 1) AS Placement_Rate,
    COUNT(Placement_ID) AS Total_Offers,
    ROUND(COALESCE(AVG(Placed_Package), 0), 2) AS Avg_Package,
    COALESCE(MAX(Placed_Package), 0.00) AS Highest_Package,
    COALESCE(MIN(Placed_Package), 0.00) AS Lowest_Package
FROM StudentBands
GROUP BY CGPA_Band
ORDER BY CGPA_Band ASC;
```

### 9.43: E9. Recruitment Drive Conversion & Hiring Yield
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['report_drive_performance'] / execute_saved_query()`
- **Purpose:** Production saved report query 'E9. Recruitment Drive Conversion & Hiring Yield' in category 'Executive Reports'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Four-table equi-join traversing RECRUITMENT_DRIVE, COMPANY, OPPORTUNITY, and PLACEMENT computing selection yield and classifying performance via DENSE_RANK().

```sql
WITH DriveStats AS (
    SELECT
        rd.Drive_ID,
        c.Company_Name,
        c.Company_Type,
        rd.Drive_Year,
        rd.Drive_Type,
        rd.Season,
        rd.Drive_Date,
        COUNT(DISTINCT o.Opportunity_ID) AS Total_Opportunities,
        COUNT(p.Placement_ID) AS Total_Offers_Extended,
        COUNT(CASE WHEN p.Joined = 'Yes' OR p.Offer_Status = 'Joined' THEN 1 END) AS Accepted_Hires,
        ROUND(AVG(p.Package), 2) AS Avg_Package_Offered,
        ROUND(AVG(CASE WHEN p.Joined = 'Yes' OR p.Offer_Status = 'Joined' THEN p.Package END), 2) AS Avg_Accepted_Package,
        MAX(p.Package) AS Highest_Package
    FROM RECRUITMENT_DRIVE rd
    JOIN COMPANY c ON rd.Company_ID = c.Company_ID
    LEFT JOIN OPPORTUNITY o ON rd.Drive_ID = o.Drive_ID
    LEFT JOIN PLACEMENT p ON o.Opportunity_ID = p.Opportunity_ID
    GROUP BY rd.Drive_ID, c.Company_Name, c.Company_Type, rd.Drive_Year, rd.Drive_Type, rd.Season, rd.Drive_Date
)
SELECT
    d.*,
    ROUND(COALESCE(100.0 * Accepted_Hires / NULLIF(Total_Offers_Extended, 0), 0), 1) AS Acceptance_Rate,
    DENSE_RANK() OVER (ORDER BY Total_Offers_Extended DESC, Accepted_Hires DESC) AS Drive_Rank
FROM DriveStats d
ORDER BY Drive_Year DESC, Total_Offers_Extended DESC;
```

### 9.44: E10. Semester Academic Progression & SGPA Trend Analysis
- **Source File / Routine:** `services/sql_report_service.py` -> `SAVED_QUERIES['report_semester_performance'] / execute_saved_query()`
- **Purpose:** Production saved report query 'E10. Semester Academic Progression & SGPA Trend Analysis' in category 'Executive Reports'. Designed for administrative decision support, institutional audits, and placement analytics.
- **Core DBMS Concepts:** Academic result evaluation computing Pass and Distinction rates, tracking student cohort trajectory via LAG() window functions across curriculum semesters, and ranking branches within each semester.

```sql
WITH SemStats AS (
    SELECT
        sr.Semester,
        s.Branch,
        COUNT(sr.Result_ID) AS Total_Students_Evaluated,
        ROUND(AVG(sr.SGPA), 2) AS Avg_SGPA,
        MAX(sr.SGPA) AS Highest_SGPA,
        MIN(sr.SGPA) AS Lowest_SGPA,
        COUNT(CASE WHEN sr.SGPA >= 6.0 THEN 1 END) AS Pass_Count,
        COUNT(CASE WHEN sr.SGPA >= 8.0 THEN 1 END) AS Distinction_Count,
        ROUND(100.0 * COUNT(CASE WHEN sr.SGPA >= 6.0 THEN 1 END) / COUNT(sr.Result_ID), 1) AS Pass_Rate,
        ROUND(100.0 * COUNT(CASE WHEN sr.SGPA >= 8.0 THEN 1 END) / COUNT(sr.Result_ID), 1) AS Distinction_Rate
    FROM SEMESTER_RESULT sr
    JOIN STUDENT s ON sr.Student_ID = s.Student_ID
    GROUP BY sr.Semester, s.Branch
)
SELECT
    Semester,
    Branch,
    Total_Students_Evaluated,
    Avg_SGPA,
    Highest_SGPA,
    Lowest_SGPA,
    Pass_Rate,
    Distinction_Rate,
    LAG(Avg_SGPA) OVER (PARTITION BY Branch ORDER BY Semester ASC) AS Prev_Sem_Avg,
    ROUND(COALESCE(Avg_SGPA - LAG(Avg_SGPA) OVER (PARTITION BY Branch ORDER BY Semester ASC), 0), 2) AS SGPA_Progression,
    DENSE_RANK() OVER (PARTITION BY Semester ORDER BY Avg_SGPA DESC) AS Sem_Branch_Rank
FROM SemStats
ORDER BY Semester ASC, Sem_Branch_Rank ASC;
```

### 10.3: Dynamic Branch Selector Options Extraction
- **Source File / Routine:** `services/sql_report_service.py` -> `get_report_dynamic_options()`
- **Purpose:** Retrieves the complete list of unique academic branches currently enrolled in the institution to dynamically populate report parameter dropdowns without hardcoded fallbacks.
- **Core DBMS Concepts:** Relational projection (π) with duplicate elimination (DISTINCT) and B-tree index ordering.

```sql
SELECT DISTINCT Branch FROM STUDENT WHERE Branch IS NOT NULL AND Branch != '' ORDER BY Branch;
```

### 10.4: Dynamic Batch Year Selector Options Extraction
- **Source File / Routine:** `services/sql_report_service.py` -> `get_report_dynamic_options()`
- **Purpose:** Queries all unique academic graduation batch years present in student records to provide database-driven cohort selection filters.
- **Core DBMS Concepts:** Relational projection with duplicate elimination and descending chronological index scan.

```sql
SELECT DISTINCT Batch_Year FROM STUDENT WHERE Batch_Year IS NOT NULL ORDER BY Batch_Year DESC;
```

### 10.5: Dynamic Corporate Partner Selector Options Extraction
- **Source File / Routine:** `services/sql_report_service.py` -> `get_report_dynamic_options()`
- **Purpose:** Extracts distinct registered corporate partner names to feed dynamic company selection dropdowns in placement and internship reports.
- **Core DBMS Concepts:** Unique attribute projection and collation-based alphabetical sorting.

```sql
SELECT DISTINCT Company_Name FROM COMPANY WHERE Company_Name IS NOT NULL AND Company_Name != '' ORDER BY Company_Name;
```

### 10.6: Dynamic Student Roll Number Selector Options Extraction
- **Source File / Routine:** `services/sql_report_service.py` -> `get_report_dynamic_options()`
- **Purpose:** Retrieves all distinct official institutional roll numbers to populate individual student lookup parameters in SQL report generators.
- **Core DBMS Concepts:** Index-only scan (covering index) on candidate key Roll_No with ordering.

```sql
SELECT DISTINCT Roll_No FROM STUDENT WHERE Roll_No IS NOT NULL AND Roll_No != '' ORDER BY Roll_No;
```

### 10.7: Dynamic Technical Skill Catalog Extraction
- **Source File / Routine:** `services/sql_report_service.py` -> `get_report_dynamic_options()`
- **Purpose:** Extracts all unique technical competencies registered across student talent profiles to populate filter selectors for talent search and skill demand analysis.
- **Core DBMS Concepts:** Multi-valued attribute normalization projection and set deduplication.

```sql
SELECT DISTINCT Skill FROM STUDENT_SKILL WHERE Skill IS NOT NULL AND Skill != '' ORDER BY Skill;
```

---

## Category: Other database operations (56 Queries)

> Category Focus: Systematic revision of backend routines, transaction hooks, duplicate validation patterns, and relational operations governing **other database operations**.

### DDL-01: Schema Definition: Table UNIVERSITY
- **Source File / Routine:** `init_mysql.py` -> `initialize_database`
- **Purpose:** Institution master entity storing accredited university metadata.
- **Core DBMS Concepts:** Primary key constraint on University_ID. Master entity for campus multi-tenancy. Uses MySQL InnoDB storage engine with UTF-8 character encoding.

```sql
CREATE TABLE IF NOT EXISTS UNIVERSITY (
    University_ID   INT AUTO_INCREMENT PRIMARY KEY,
    University_Name VARCHAR(120) NOT NULL UNIQUE,
    Location        VARCHAR(100) NOT NULL,
    Established_Year INT CHECK (Established_Year BETWEEN 1800 AND 2100)
) ENGINE=InnoDB;
```

### DDL-02: Schema Definition: Table COURSE
- **Source File / Routine:** `init_mysql.py` -> `initialize_database`
- **Purpose:** Curricular course catalog with semester level, department, and credit weightage.
- **Core DBMS Concepts:** Foreign key referencing UNIVERSITY(University_ID) with ON DELETE CASCADE. Enforces credit and semester domains. Uses MySQL InnoDB storage engine with UTF-8 character encoding.

```sql
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
```

### DDL-03: Schema Definition: Table STUDENT
- **Source File / Routine:** `init_mysql.py` -> `initialize_database`
- **Purpose:** Core student candidate entity with roll number, academic branch, CGPA, and backlog count.
- **Core DBMS Concepts:** Composite UNIQUE constraint on (Roll_No, Email). CHECK constraints on CGPA (0.00-10.00) and Backlogs (>= 0). Uses MySQL InnoDB storage engine with UTF-8 character encoding.

```sql
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
```

### DDL-04: Schema Definition: Table STUDENT_PHONE
- **Source File / Routine:** `init_mysql.py` -> `initialize_database`
- **Purpose:** Multi-valued attribute bridge for student contact numbers ensuring 1NF normalization.
- **Core DBMS Concepts:** Composite primary key (Student_ID, Phone_No). Foreign key referencing STUDENT(Student_ID) ON DELETE CASCADE. Uses MySQL InnoDB storage engine with UTF-8 character encoding.

```sql
CREATE TABLE IF NOT EXISTS STUDENT_PHONE (
    Student_ID      INT         NOT NULL,
    Phone_No        VARCHAR(20) NOT NULL,
    PRIMARY KEY (Student_ID, Phone_No),
    CONSTRAINT fk_phone_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT(Student_ID) ON DELETE CASCADE
) ENGINE=InnoDB;
```

### DDL-06: Schema Definition: Table STUDENT_COURSE
- **Source File / Routine:** `init_mysql.py` -> `initialize_database`
- **Purpose:** Course enrollment registry tracking student curriculum registrations and grades.
- **Core DBMS Concepts:** Composite primary key (Student_ID, Course_ID). Foreign keys to STUDENT and COURSE. Uses MySQL InnoDB storage engine with UTF-8 character encoding.

```sql
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
```

### DDL-07: Schema Definition: Table STUDENT_PROFILE
- **Source File / Routine:** `init_mysql.py` -> `initialize_database`
- **Purpose:** External student professional profiles (GitHub, LinkedIn, LeetCode, Portfolios).
- **Core DBMS Concepts:** Primary key Profile_ID. Foreign key to STUDENT(Student_ID) ON DELETE CASCADE. Uses MySQL InnoDB storage engine with UTF-8 character encoding.

```sql
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
```

### DDL-09: Schema Definition: Table EDUCATION_DOCUMENT
- **Source File / Routine:** `init_mysql.py` -> `initialize_database`
- **Purpose:** Prior secondary and higher-secondary educational certificates and verification records.
- **Core DBMS Concepts:** Primary key Doc_ID. Foreign key to STUDENT(Student_ID) ON DELETE CASCADE. Uses MySQL InnoDB storage engine with UTF-8 character encoding.

```sql
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
```

### DDL-10: Schema Definition: Table SEMESTER_RESULT
- **Source File / Routine:** `init_mysql.py` -> `initialize_database`
- **Purpose:** Historical semester-wise SGPA academic progression records and credit tallies.
- **Core DBMS Concepts:** Composite UNIQUE (Student_ID, Semester). Enforces SGPA check (0.00-10.00). Foreign key to STUDENT. Uses MySQL InnoDB storage engine with UTF-8 character encoding.

```sql
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
```

### DDL-11: Schema Definition: Table COMPANY
- **Source File / Routine:** `init_mysql.py` -> `initialize_database`
- **Purpose:** Corporate recruiting partner directory, corporate tier, and industry classification.
- **Core DBMS Concepts:** Primary key Company_ID. UNIQUE constraint on Company_Name. ENUM constraint on Company_Type (Product, Service, Core, Startup). Uses MySQL InnoDB storage engine with UTF-8 character encoding.

```sql
CREATE TABLE IF NOT EXISTS COMPANY (
    Company_ID      INT AUTO_INCREMENT PRIMARY KEY,
    Company_Name    VARCHAR(100) NOT NULL UNIQUE,
    Company_Type    VARCHAR(30)  NOT NULL DEFAULT 'Other' CHECK (Company_Type IN ('Product', 'Service', 'Startup', 'PSU', 'MNC', 'Other')),
    Industry        VARCHAR(60),
    Location        VARCHAR(60),
    Website         VARCHAR(150)
) ENGINE=InnoDB;
```

### DDL-12: Schema Definition: Table RECRUITMENT_DRIVE
- **Source File / Routine:** `init_mysql.py` -> `initialize_database`
- **Purpose:** Campus placement drive schedules, recruiting seasons, and academic years.
- **Core DBMS Concepts:** Primary key Drive_ID. Foreign key referencing COMPANY(Company_ID) ON DELETE CASCADE. Uses MySQL InnoDB storage engine with UTF-8 character encoding.

```sql
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
```

### DDL-13: Schema Definition: Table OPPORTUNITY
- **Source File / Routine:** `init_mysql.py` -> `initialize_database`
- **Purpose:** Job opportunities and internship postings offered during recruitment drives.
- **Core DBMS Concepts:** Primary key Opportunity_ID. Foreign key referencing RECRUITMENT_DRIVE(Drive_ID) ON DELETE CASCADE. Uses MySQL InnoDB storage engine with UTF-8 character encoding.

```sql
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
```

### DDL-14: Schema Definition: Table ELIGIBILITY
- **Source File / Routine:** `init_mysql.py` -> `initialize_database`
- **Purpose:** Academic cutoff criteria for recruitment drives (minimum CGPA, max backlogs).
- **Core DBMS Concepts:** Primary key Eligibility_ID. Foreign key referencing OPPORTUNITY(Opportunity_ID) ON DELETE CASCADE. Uses MySQL InnoDB storage engine with UTF-8 character encoding.

```sql
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
```

### DDL-15: Schema Definition: Table ELIGIBILITY_BRANCH
- **Source File / Routine:** `init_mysql.py` -> `initialize_database`
- **Purpose:** Multi-valued branch eligibility mapping allowed engineering departments for a drive.
- **Core DBMS Concepts:** Composite primary key (Eligibility_ID, Branch). Foreign key referencing ELIGIBILITY(Eligibility_ID). Uses MySQL InnoDB storage engine with UTF-8 character encoding.

```sql
CREATE TABLE IF NOT EXISTS ELIGIBILITY_BRANCH (
    Eligibility_ID  INT          NOT NULL,
    Branch          VARCHAR(50)  NOT NULL,
    PRIMARY KEY (Eligibility_ID, Branch),
    CONSTRAINT fk_ebranch_eligibility FOREIGN KEY (Eligibility_ID)
        REFERENCES ELIGIBILITY(Eligibility_ID) ON DELETE CASCADE
) ENGINE=InnoDB;
```

### DDL-16: Schema Definition: Table SELECTION_PROCESS
- **Source File / Routine:** `init_mysql.py` -> `initialize_database`
- **Purpose:** Sequential assessment and interview rounds within a recruitment opportunity.
- **Core DBMS Concepts:** Primary key Round_ID. Foreign key referencing OPPORTUNITY(Opportunity_ID) ON DELETE CASCADE. Sequential Round_Number ordering. Uses MySQL InnoDB storage engine with UTF-8 character encoding.

```sql
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
```

### DDL-17: Schema Definition: Table INTERNSHIP_REQUIREMENT
- **Source File / Routine:** `init_mysql.py` -> `initialize_database`
- **Purpose:** Institutional degree requirements defining mandatory training periods and prerequisite semesters.
- **Core DBMS Concepts:** Primary key Requirement_ID. Defines prerequisite semester and minimum SGPA criteria (Sem 3 for I1, Sem 5 for I2). Uses MySQL InnoDB storage engine with UTF-8 character encoding.

```sql
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
```

### DDL-18: Schema Definition: Table INTERNSHIP
- **Source File / Routine:** `init_mysql.py` -> `initialize_database`
- **Purpose:** Student industry internship attachment records, durations, stipends, and evaluations.
- **Core DBMS Concepts:** Primary key Internship_ID. Foreign keys to STUDENT, COMPANY, and INTERNSHIP_REQUIREMENT. Computes duration in weeks/days. Uses MySQL InnoDB storage engine with UTF-8 character encoding.

```sql
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
```

### DDL-19: Schema Definition: Table PLACEMENT
- **Source File / Routine:** `init_mysql.py` -> `initialize_database`
- **Purpose:** Official campus placement offers, compensation packages, offer statuses, and joining records.
- **Core DBMS Concepts:** Primary key Placement_ID. Foreign keys to STUDENT, COMPANY, and OPPORTUNITY. Single acceptance integrity rule. Uses MySQL InnoDB storage engine with UTF-8 character encoding.

```sql
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
```

### DDL-20: Schema Definition: Table PLACEMENT_SKILL
- **Source File / Routine:** `init_mysql.py` -> `initialize_database`
- **Purpose:** Technical competencies and domain skills evaluated during the hiring process.
- **Core DBMS Concepts:** Composite primary key (Placement_ID, Skill). Foreign key referencing PLACEMENT(Placement_ID) ON DELETE CASCADE. Uses MySQL InnoDB storage engine with UTF-8 character encoding.

```sql
CREATE TABLE IF NOT EXISTS PLACEMENT_SKILL (
    Placement_ID    INT         NOT NULL,
    Skill           VARCHAR(50) NOT NULL,
    PRIMARY KEY (Placement_ID, Skill),
    CONSTRAINT fk_pskill_placement FOREIGN KEY (Placement_ID)
        REFERENCES PLACEMENT(Placement_ID) ON DELETE CASCADE
) ENGINE=InnoDB;
```

### DDL-23: Performance Index: idx_student_cgpa
- **Source File / Routine:** `schema.sql` -> `schema_indexes`
- **Purpose:** Accelerates continuous range queries (e.g., CGPA >= 6.00 / 8.00) and top-performer ordering.
- **Core DBMS Concepts:** B+ Tree index structure; avoids full table scans (FTS); enables index range scans and index-only lookups.

```sql
CREATE INDEX idx_student_cgpa ON STUDENT(CGPA);
```

### DDL-24: Performance Index: idx_student_roll
- **Source File / Routine:** `schema.sql` -> `schema_indexes`
- **Purpose:** Provides O(log N) point lookup by academic roll number and prefix matching.
- **Core DBMS Concepts:** B+ Tree index structure; avoids full table scans (FTS); enables index range scans and index-only lookups.

```sql
CREATE INDEX idx_student_roll ON STUDENT(Roll_No);
```

### DDL-25: Performance Index: idx_company_name
- **Source File / Routine:** `schema.sql` -> `schema_indexes`
- **Purpose:** Optimizes corporate recruiter point filtering and exact name checks.
- **Core DBMS Concepts:** B+ Tree index structure; avoids full table scans (FTS); enables index range scans and index-only lookups.

```sql
CREATE INDEX idx_company_name ON COMPANY(Company_Name);
```

### DDL-26: Performance Index: idx_company_type
- **Source File / Routine:** `schema.sql` -> `schema_indexes`
- **Purpose:** Accelerates categorical tier filtering (Product, Service, Core, Startup).
- **Core DBMS Concepts:** B+ Tree index structure; avoids full table scans (FTS); enables index range scans and index-only lookups.

```sql
CREATE INDEX idx_company_type ON COMPANY(Company_Type);
```

### DDL-27: Performance Index: idx_placement_student
- **Source File / Routine:** `schema.sql` -> `schema_indexes`
- **Purpose:** Speeds up foreign key join traversal connecting students to placement offers.
- **Core DBMS Concepts:** B+ Tree index structure; avoids full table scans (FTS); enables index range scans and index-only lookups.

```sql
CREATE INDEX idx_placement_student ON PLACEMENT(Student_ID);
```

### DDL-28: Performance Index: idx_placement_company
- **Source File / Routine:** `schema.sql` -> `schema_indexes`
- **Purpose:** Optimizes foreign key joins between placements and corporate recruiters.
- **Core DBMS Concepts:** B+ Tree index structure; avoids full table scans (FTS); enables index range scans and index-only lookups.

```sql
CREATE INDEX idx_placement_company ON PLACEMENT(Company_ID);
```

### DDL-29: Performance Index: idx_placement_year
- **Source File / Routine:** `schema.sql` -> `schema_indexes`
- **Purpose:** Enhances temporal grouping and multi-cohort historical trend queries.
- **Core DBMS Concepts:** B+ Tree index structure; avoids full table scans (FTS); enables index range scans and index-only lookups.

```sql
CREATE INDEX idx_placement_year ON PLACEMENT(Placement_Year);
```

### DDL-30: Performance Index: idx_internship_student
- **Source File / Routine:** `schema.sql` -> `schema_indexes`
- **Purpose:** Accelerates foreign key joins evaluating student mandatory internship compliance.
- **Core DBMS Concepts:** B+ Tree index structure; avoids full table scans (FTS); enables index range scans and index-only lookups.

```sql
CREATE INDEX idx_internship_student ON INTERNSHIP(Student_ID);
```

### DDL-31: Performance Index: idx_internship_company
- **Source File / Routine:** `schema.sql` -> `schema_indexes`
- **Purpose:** Speeds up recruiter-level internship cohort tracking and hiring pipelines.
- **Core DBMS Concepts:** B+ Tree index structure; avoids full table scans (FTS); enables index range scans and index-only lookups.

```sql
CREATE INDEX idx_internship_company ON INTERNSHIP(Company_ID);
```

### DDL-32: Performance Index: idx_internship_type
- **Source File / Routine:** `schema.sql` -> `schema_indexes`
- **Purpose:** Enables rapid partitioning between Mandatory I1, Mandatory I2, and Additional attachments.
- **Core DBMS Concepts:** B+ Tree index structure; avoids full table scans (FTS); enables index range scans and index-only lookups.

```sql
CREATE INDEX idx_internship_type ON INTERNSHIP(Internship_Type);
```

### OPP-01: Create Opportunity: Verify Parent Drive
- **Source File / Routine:** `services/opportunity_service.py` -> `create_opportunity`
- **Purpose:** Confirms recruitment drive exists before attaching a job posting.
- **Core DBMS Concepts:** Foreign key verification.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Drive_ID FROM RECRUITMENT_DRIVE WHERE Drive_ID = %s
```

### OPP-02: Create Opportunity: Insert Job Opportunity Record
- **Source File / Routine:** `services/opportunity_service.py` -> `create_opportunity`
- **Purpose:** Inserts opportunity role, type (Full-time / Internship), package/stipend, and location.
- **Core DBMS Concepts:** Clustered insertion; AUTO_INCREMENT primary key.

```sql
INSERT INTO OPPORTUNITY (Drive_ID, Role, Opportunity_Type, Package_Stipend, Duration_Months)
            VALUES (%s, %s, %s, %s, %s)
```

### OPP-03: Create Opportunity: Insert Academic Cutoff Criteria
- **Source File / Routine:** `services/opportunity_service.py` -> `create_opportunity`
- **Purpose:** Records minimum CGPA cutoff and maximum allowable backlogs for the role.
- **Core DBMS Concepts:** 1:1 extension table insertion; eligibility criteria definition.

```sql
INSERT INTO ELIGIBILITY (Opportunity_ID, Minimum_CGPA, Eligible_Branch, Max_Backlogs, Other_Criteria)
            VALUES (%s, %s, %s, %s, %s)
```

### OPP-04: Create Opportunity: Insert Academic Cutoff Criteria
- **Source File / Routine:** `services/opportunity_service.py` -> `create_opportunity`
- **Purpose:** Records minimum CGPA cutoff and maximum allowable backlogs for the role.
- **Core DBMS Concepts:** 1:1 extension table insertion; eligibility criteria definition.

```sql
INSERT INTO ELIGIBILITY_BRANCH (Eligibility_ID, Branch) VALUES (%s, %s)
```

### OPP-06: Get Opportunity: Retrieve Eligible Department List
- **Source File / Routine:** `services/opportunity_service.py` -> `get_opportunity`
- **Purpose:** Fetches allowed engineering branches for the opportunity.
- **Core DBMS Concepts:** Child entity projection.

```sql
SELECT Branch FROM ELIGIBILITY_BRANCH WHERE Eligibility_ID = %s ORDER BY Branch
```

### OPP-07: Get Opportunity: Retrieve Sequential Hiring Rounds
- **Source File / Routine:** `services/opportunity_service.py` -> `get_opportunity`
- **Purpose:** Fetches the sequence of assessment rounds configured for the opportunity.
- **Core DBMS Concepts:** 1:N child table retrieval; sequence ordering.

```sql
SELECT Round_ID, Round_Number, Round_Type, Description
        FROM SELECTION_PROCESS
        WHERE Opportunity_ID = %s
        ORDER BY Round_Number ASC
```

### OPP-11: Update Opportunity: Mutate Role and Compensation
- **Source File / Routine:** `services/opportunity_service.py` -> `update_opportunity`
- **Purpose:** Modifies designated role, opportunity type, compensation, and duration.
- **Core DBMS Concepts:** In-place record mutation.

```sql
UPDATE OPPORTUNITY SET
```

### OPP-12: Update Opportunity: Purge Allowed Branches
- **Source File / Routine:** `services/opportunity_service.py` -> `update_opportunity`
- **Purpose:** Clears previous branch associations before re-inserting updated list.
- **Core DBMS Concepts:** Atomic child table purge.

```sql
DELETE FROM ELIGIBILITY_BRANCH WHERE Eligibility_ID = %s
```

### OPP-13: Update Opportunity: Re-Insert Allowed Branches
- **Source File / Routine:** `services/opportunity_service.py` -> `update_opportunity`
- **Purpose:** Inserts updated engineering branch eligibility associations.
- **Core DBMS Concepts:** Atomic child table insertion.

```sql
INSERT INTO ELIGIBILITY_BRANCH (Eligibility_ID, Branch) VALUES (%s, %s)
```

### OPP-14: Update Opportunity: Mutate Cutoff Criteria
- **Source File / Routine:** `services/opportunity_service.py` -> `update_opportunity`
- **Purpose:** Modifies minimum CGPA and maximum allowable backlogs.
- **Core DBMS Concepts:** 1:1 extension table update.

```sql
UPDATE ELIGIBILITY SET
```

### OPP-15: Delete Opportunity: Verify Existence
- **Source File / Routine:** `services/opportunity_service.py` -> `delete_opportunity`
- **Purpose:** Confirms opportunity exists prior to deletion check.
- **Core DBMS Concepts:** Primary key lookup.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Opportunity_ID, Role FROM OPPORTUNITY WHERE Opportunity_ID = %s
```

### OPP-17: Delete Opportunity: Permanently Remove Opportunity
- **Source File / Routine:** `services/opportunity_service.py` -> `delete_opportunity`
- **Purpose:** Deletes opportunity from the database. Cascades delete to ELIGIBILITY, ELIGIBILITY_BRANCH, and SELECTION_PROCESS.
- **Core DBMS Concepts:** Physical record deletion; foreign key cascade.
- **Pattern Note (Transactional Atomic Delete):** Standard parameterized DELETE statement executed within transaction blocks to maintain referential integrity.

```sql
DELETE FROM OPPORTUNITY WHERE Opportunity_ID = %s
```

### DRV-21: Get Drive: Retrieve Associated Job Opportunities
- **Source File / Routine:** `services/drive_service.py` -> `get_drive`
- **Purpose:** Fetches all job and internship opportunities hosted within this recruitment drive.
- **Core DBMS Concepts:** 1:N opportunity traversal.

```sql
SELECT o.Opportunity_ID, o.Role, o.Opportunity_Type, o.Package_Stipend, o.Duration_Months,
               e.Minimum_CGPA, e.Max_Backlogs, e.Other_Criteria, e.Eligible_Branch, e.Eligibility_ID
        FROM OPPORTUNITY o
        LEFT JOIN ELIGIBILITY e ON o.Opportunity_ID = e.Opportunity_ID
        WHERE o.Drive_ID = %s
        ORDER BY o.Opportunity_ID ASC
```

### DRV-23: Get Drive: Retrieve Drive Assessment Rounds
- **Source File / Routine:** `services/drive_service.py` -> `get_drive`
- **Purpose:** Fetches selection rounds configured for opportunities in the drive.
- **Core DBMS Concepts:** Sequential interview stages scan.

```sql
SELECT Round_ID, Round_Number, Round_Type, Description FROM SELECTION_PROCESS WHERE Opportunity_ID = %s ORDER BY Round_Number ASC
```

### DRV-25: Update Drive: Verify Target Record
- **Source File / Routine:** `services/drive_service.py` -> `update_drive`
- **Purpose:** Verifies drive exists before applying changes.
- **Core DBMS Concepts:** Primary key lookup.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT * FROM RECRUITMENT_DRIVE WHERE Drive_ID = %s
```

### DRV-26: Update Drive: Apply Schedule Changes
- **Source File / Routine:** `services/drive_service.py` -> `update_drive`
- **Purpose:** Modifies drive year, type, season, and scheduled date.
- **Core DBMS Concepts:** In-place record mutation.

```sql
UPDATE RECRUITMENT_DRIVE SET
```

### DRV-29: Delete Drive: Permanently Remove Drive Record
- **Source File / Routine:** `services/drive_service.py` -> `delete_drive`
- **Purpose:** Deletes recruitment drive record from the database.
- **Core DBMS Concepts:** Physical record deletion.
- **Pattern Note (Transactional Atomic Delete):** Standard parameterized DELETE statement executed within transaction blocks to maintain referential integrity.

```sql
DELETE FROM RECRUITMENT_DRIVE WHERE Drive_ID = %s
```

### RND-30: Create Round: Verify Parent Opportunity
- **Source File / Routine:** `services/round_service.py` -> `create_round`
- **Purpose:** Confirms job opportunity exists before adding an interview round.
- **Core DBMS Concepts:** Foreign key verification.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Opportunity_ID FROM OPPORTUNITY WHERE Opportunity_ID = %s
```

### RND-31: Create Round: Prevent Duplicate Round Number
- **Source File / Routine:** `services/round_service.py` -> `create_round`
- **Purpose:** Enforces unique round numbering sequence within an opportunity.
- **Core DBMS Concepts:** Composite sequence uniqueness guard.
- **Pattern Note (Pre-Insert Uniqueness Check):** Reusable validation query run before INSERT transactions to prevent database collision and enforce candidate key constraints at the application layer.

```sql
SELECT Round_ID FROM SELECTION_PROCESS WHERE Opportunity_ID = %s AND Round_Number = %s
```

### RND-32: Create Round: Insert Selection Round Stage
- **Source File / Routine:** `services/round_service.py` -> `create_round`
- **Purpose:** Inserts assessment stage (e.g. Coding Test, Technical Interview, HR Round).
- **Core DBMS Concepts:** Child entity insertion; AUTO_INCREMENT primary key.

```sql
INSERT INTO SELECTION_PROCESS (Opportunity_ID, Round_Number, Round_Type, Description)
        VALUES (%s, %s, %s, %s)
```

### RND-35: Update Round: Verify Target Stage
- **Source File / Routine:** `services/round_service.py` -> `update_round`
- **Purpose:** Verifies selection round exists before update.
- **Core DBMS Concepts:** Primary key lookup.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT * FROM SELECTION_PROCESS WHERE Round_ID = %s
```

### RND-36: Update Round: Check Sequence Collision
- **Source File / Routine:** `services/round_service.py` -> `update_round`
- **Purpose:** Guarantees round number sequence does not collide with existing rounds.
- **Core DBMS Concepts:** Self-exclusion sequence uniqueness validation.

```sql
SELECT Round_ID FROM SELECTION_PROCESS WHERE Opportunity_ID = %s AND Round_Number = %s AND Round_ID != %s
```

### RND-37: Update Round: Mutate Round Details
- **Source File / Routine:** `services/round_service.py` -> `update_round`
- **Purpose:** Modifies round number, round type, and stage description.
- **Core DBMS Concepts:** In-place record mutation.

```sql
UPDATE SELECTION_PROCESS SET
```

### RND-38: Delete Round: Verify Target Stage
- **Source File / Routine:** `services/round_service.py` -> `delete_round`
- **Purpose:** Confirms selection round exists before deletion.
- **Core DBMS Concepts:** Primary key lookup.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
SELECT Round_ID, Round_Number, Round_Type FROM SELECTION_PROCESS WHERE Round_ID = %s
```

### RND-39: Delete Round: Verify Target Stage
- **Source File / Routine:** `services/round_service.py` -> `delete_round`
- **Purpose:** Confirms selection round exists before deletion.
- **Core DBMS Concepts:** Primary key lookup.
- **Pattern Note (Foreign Key / Existence Probe):** Lightweight primary key lookup verifying entity presence before proceeding with an UPDATE or DELETE operation.

```sql
DELETE FROM SELECTION_PROCESS WHERE Round_ID = %s
```

### 10.1: Database Connection Liveness Probe & Version Check
- **Source File / Routine:** `db/connection.py` -> `ping_db()`
- **Purpose:** Executes a lightweight heartbeat query to verify MySQL server reachability, engine health, and active connection pool status.
- **Core DBMS Concepts:** DBMS server metadata inspection and connection health monitoring.

```sql
SELECT VERSION();
```

### 10.2: Dynamic Session Execution Timeout Governance
- **Source File / Routine:** `services/sql_report_service.py` -> `execute_custom_query()`
- **Purpose:** Configures the MySQL session-level statement timeout in milliseconds to prevent runaway reporting queries, denial-of-service, or excessive table lock contention.
- **Core DBMS Concepts:** Session variable manipulation and server-side execution resource throttling.

```sql
SET SESSION max_execution_time = %s;
```

### 10.17: ACID Transaction Isolation Level Verification
- **Source File / Routine:** `db/connection.py` -> `ACID Isolation Audit`
- **Purpose:** Verifies the server and session transaction isolation level to ensure REPEATABLE READ / READ COMMITTED guarantees for multi-table transactions (e.g. student creation with phones/skills, offer acceptance).
- **Core DBMS Concepts:** ACID transaction isolation level inspection and concurrency control guarantees.

```sql
SELECT @@transaction_isolation AS default_isolation_level;
```

---

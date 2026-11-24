# Topic-Wise SQL Revision Catalog: All Remaining Backend Queries

> [!NOTE]
> **Complete Project Coverage**: This document meticulously catalogs all backend SQL queries from the Legacy Dataforce services across the canonical **7-table relational schema**. Every query is documented with its source file, function name, purpose, core DBMS concepts, duplicate/template pattern classification, and exact SQL code.

## Category Summary Overview

| Category | Source File | Total Queries Found | Key Roles |
|---|---|:---:|---|
| **Students** | `services/student_service.py` | 26 | Candidate CRUD, multi-valued phones/skills, uniqueness checks, filtering |
| **Companies** | `services/company_service.py` | 12 | Corporate recruitment profiles, recruiter tiers, industry categories |
| **Placements** | `services/placement_service.py` | 25 | Job offers, single-joined offer enforcement, package statistics |
| **Internships** | `services/internship_service.py` | 25 | Curriculum milestones (Milestone 1 & 2), date audits, stipends |
| **Dashboard** | `services/dashboard_service.py` | 18 | 6 interactive charts, department KPIs, YoY trends |
| **Reports** | `services/sql_report_service.py` | 51 | Saved query catalog, ad-hoc console, window functions, CTEs |
| **TOTAL** | *Entire Service Layer* | **157** | *Complete coverage of active 7-table schema* |

---

## Duplicate & Template Pattern Analysis

To understand how software engineering principles are applied in database applications, many queries follow standardized, reusable design patterns:

| Pattern Name | Count | Architectural Purpose in Services |
|---|:---:|---|
| **Pre-Insert Uniqueness Check** | 10 | Standardized template applied across entity services. |
| **Primary Key Record Retrieval** | 10 | Standardized template applied across entity services. |
| **Entity Deletion by Primary Key** | 4 | Standardized template applied across entity services. |
| **Multivalued Child Attribute Insert/Delete** | 7 | Standardized template applied across entity services. |
| **Dropdown Distinct Filter Lookup** | 10 | Standardized template applied across entity services. |
| **Aggregate Metric Calculation** | 66 | Standardized template applied across entity services. |
| **Complex Analytical / Reporting Query** | 50 | Standardized template applied across entity services. |

---

## Category: Students (26 Queries)

### Q001: `create_student`
- **Source File & Function:** `services/student_service.py` -> `create_student`
- **Category:** `Students`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
INSERT INTO STUDENT (
            Roll_No, First_Name, Last_Name, Branch, Batch_Year, Section,
            CGPA, Backlogs, Email, Resume_Link
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
```

---

### Q002: `create_student`
- **Source File & Function:** `services/student_service.py` -> `create_student`
- **Category:** `Students`
- **Design Pattern:** `Pre-Insert Uniqueness Check`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Student_ID FROM STUDENT WHERE Roll_No = %s
```

---

### Q003: `create_student`
- **Source File & Function:** `services/student_service.py` -> `create_student`
- **Category:** `Students`
- **Design Pattern:** `Pre-Insert Uniqueness Check`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Student_ID FROM STUDENT WHERE Email = %s
```

---

### Q004: `get_student`
- **Source File & Function:** `services/student_service.py` -> `get_student`
- **Category:** `Students`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Retrieves full student details across canonical 7-table schema:
    1. Personal details & Phone Numbers (STUDENT, STUDENT_PHONE)
    2. Academic details (STUDENT)
    3. Technical skills (STUDENT_SKILL)
    4. Placement offers (PLACEMENT, COMPANY)
    5. Internship history (INTERNSHIP, COMPANY)
    """
    student_sql = """
        SELECT Student_ID, Roll_No, First_Name, Last_Name, Branch, Batch_Year,
               Section, CGPA, Backlogs, Email, Resume_Link, Date_of_Birth, Gender, Personal_Email
        FROM STUDENT
        WHERE Student_ID = %s
```

---

### Q005: `get_student`
- **Source File & Function:** `services/student_service.py` -> `get_student`
- **Category:** `Students`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT p.Placement_ID, p.Role, p.Package, p.Placement_Year, p.Placement_Type,
               p.Is_PPO, p.Joined, p.Offer_Status, p.Interview_Rounds,
               c.Company_ID, c.Company_Name, c.Company_Type, c.Location, c.Website
        FROM PLACEMENT p
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE p.Student_ID = %s
        ORDER BY p.Placement_Year DESC, p.Package DESC
```

---

### Q006: `get_student`
- **Source File & Function:** `services/student_service.py` -> `get_student`
- **Category:** `Students`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT i.Internship_ID, i.Internship_No, i.Internship_Type, i.Role,
               i.Stipend, i.Start_Date, i.End_Date, i.Credits,
               i.Report_Semester, i.Report_Grade, i.Report_Link, i.Certificate_Link,
               c.Company_ID, c.Company_Name, c.Company_Type
        FROM INTERNSHIP i
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        WHERE i.Student_ID = %s
        ORDER BY i.Internship_No ASC
```

---

### Q007: `list_students`
- **Source File & Function:** `services/student_service.py` -> `list_students`
- **Category:** `Students`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Lists, searches, and filters students with advanced criteria and pagination.
    Rule: 'Placed' means Joined = 'Yes'.
    """
    if per_page is not None:
        try:
            limit = int(per_page)
        except (ValueError, TypeError):
            pass

    where_clauses = ["1=1"]
    params: List[Any] = []

    if search and str(search).strip():
        search_pattern = f"%{str(search).strip()}%"
        where_clauses.append(
            "("
            "s.Roll_No LIKE %s OR "
            "s.First_Name LIKE %s OR "
            "s.Last_Name LIKE %s OR "
            "CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) LIKE %s OR "
            "s.Email LIKE %s OR "
            "EXISTS (SELECT 1 FROM STUDENT_SKILL ss WHERE ss.Student_ID = s.Student_ID AND ss.Skill LIKE %s)"
            ")"
        )
        params.extend([search_pattern] * 6)

    if branch and str(branch).strip() and str(branch).strip().lower() not in ("all", "none"):
        where_clauses.append("s.Branch = %s")
        params.append(str(branch).strip())

    if batch_year is not None:
        try:
            by = int(batch_year)
            where_clauses.append("s.Batch_Year = %s")
            params.append(by)
        except (ValueError, TypeError):
            pass

    if min_cgpa is not None:
        try:
            mc = float(min_cgpa)
            where_clauses.append("s.CGPA >= %s")
            params.append(mc)
        except (ValueError, TypeError):
            pass

    if max_cgpa is not None:
        try:
            xc = float(max_cgpa)
            where_clauses.append("s.CGPA <= %s")
            params.append(xc)
        except (ValueError, TypeError):
            pass

    if max_backlogs is not None:
        try:
            mb = int(max_backlogs)
            where_clauses.append("s.Backlogs <= %s")
            params.append(mb)
        except (ValueError, TypeError):
            pass

    # Placement Status Filter: 'Placed' strictly means Joined = 'Yes'
    if placement_status and str(placement_status).strip().lower() not in ("all", "none"):
        ps = str(placement_status).strip().lower()
        if ps in ("placed", "placed_only"):
            where_clauses.append(
                "EXISTS (SELECT 1 FROM PLACEMENT pl WHERE pl.Student_ID = s.Student_ID AND pl.Joined = 'Yes')"
            )
        elif ps in ("unplaced", "unplaced_only"):
            where_clauses.append(
                "NOT EXISTS (SELECT 1 FROM PLACEMENT pl WHERE pl.Student_ID = s.Student_ID AND pl.Joined = 'Yes')"
            )
        elif ps in ("multiple", "multiple_offers"):
            where_clauses.append(
                "(SELECT COUNT(*) FROM PLACEMENT pl WHERE pl.Student_ID = s.Student_ID) >= 2"
            )

    where_sql = " AND ".join(where_clauses)

    count_sql = f"SELECT COUNT(*) AS total FROM STUDENT s WHERE {where_sql}"
    count_res = execute_one(count_sql, tuple(params))
    total_count = int(count_res["total"] if count_res else 0)

    SORT_MAP = {
        "roll_no": "s.Roll_No",
        "name": "s.First_Name, s.Last_Name",
        "first_name": "s.First_Name",
        "last_name": "s.Last_Name",
        "branch": "s.Branch",
        "batch_year": "s.Batch_Year",
        "batch": "s.Batch_Year",
        "cgpa": "s.CGPA",
        "backlogs": "s.Backlogs",
        "student_id": "s.Student_ID",
        "placement_offers": "Placement_Offers",
        "internships": "Internships",
    }
    sort_key = str(sort_by or "roll_no").strip().lower()
    order_col = SORT_MAP.get(sort_key, "s.Roll_No")
    order_dir = "DESC" if str(sort_dir).strip().lower() == "desc" else "ASC"

    if page is not None and int(page) >= 1:
        offset = (int(page) - 1) * int(limit)

    query_sql = f
```

---

### Q008: `update_student`
- **Source File & Function:** `services/student_service.py` -> `update_student`
- **Category:** `Students`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Updates student record and synchronizes multivalued contact numbers and skills.
```

---

### Q009: `update_student`
- **Source File & Function:** `services/student_service.py` -> `update_student`
- **Category:** `Students`
- **Design Pattern:** `Pre-Insert Uniqueness Check`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Student_ID FROM STUDENT WHERE Roll_No = %s AND Student_ID != %s
```

---

### Q010: `update_student`
- **Source File & Function:** `services/student_service.py` -> `update_student`
- **Category:** `Students`
- **Design Pattern:** `Pre-Insert Uniqueness Check`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Student_ID FROM STUDENT WHERE Email = %s AND Student_ID != %s
```

---

### Q011: `update_student`
- **Source File & Function:** `services/student_service.py` -> `update_student`
- **Category:** `Students`
- **Design Pattern:** `Multivalued Child Attribute Insert/Delete`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
DELETE FROM STUDENT_PHONE WHERE Student_ID = %s
```

---

### Q012: `update_student`
- **Source File & Function:** `services/student_service.py` -> `update_student`
- **Category:** `Students`
- **Design Pattern:** `Multivalued Child Attribute Insert/Delete`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
DELETE FROM STUDENT_SKILL WHERE Student_ID = %s
```

---

### Q013: `delete_student`
- **Source File & Function:** `services/student_service.py` -> `delete_student`
- **Category:** `Students`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Safely deletes a student record ONLY if no placement or internship records exist.
    BLOCKS deletion if the student has placement offers or internship history to ensure
    career reporting integrity and prevent destruction of institutional audit trails.
```

---

### Q014: `delete_student`
- **Source File & Function:** `services/student_service.py` -> `delete_student`
- **Category:** `Students`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT
            (SELECT COUNT(*) FROM PLACEMENT WHERE Student_ID = %s) AS placement_count,
            (SELECT COUNT(*) FROM INTERNSHIP WHERE Student_ID = %s) AS internship_count
```

---

### Q015: `delete_student`
- **Source File & Function:** `services/student_service.py` -> `delete_student`
- **Category:** `Students`
- **Design Pattern:** `Primary Key Record Retrieval`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Student_ID, Roll_No, First_Name, Last_Name FROM STUDENT WHERE Student_ID = %s
```

---

### Q016: `delete_student`
- **Source File & Function:** `services/student_service.py` -> `delete_student`
- **Category:** `Students`
- **Design Pattern:** `Entity Deletion by Primary Key`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
DELETE FROM STUDENT WHERE Student_ID = %s
```

---

### Q017: `get_student_selector_options`
- **Source File & Function:** `services/student_service.py` -> `get_student_selector_options`
- **Category:** `Students`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Retrieves lightweight student identity tuples for dynamic UI dropdown selectors.
```

---

### Q018: `get_student_selector_options`
- **Source File & Function:** `services/student_service.py` -> `get_student_selector_options`
- **Category:** `Students`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Student_ID, Roll_No, First_Name, Last_Name, Branch, Batch_Year
        FROM STUDENT
        ORDER BY Roll_No ASC
```

---

### Q019: `list_student_phones`
- **Source File & Function:** `services/student_service.py` -> `list_student_phones`
- **Category:** `Students`
- **Design Pattern:** `Primary Key Record Retrieval`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Phone_No FROM STUDENT_PHONE WHERE Student_ID = %s ORDER BY Phone_No ASC
```

---

### Q020: `add_student_phone`
- **Source File & Function:** `services/student_service.py` -> `add_student_phone`
- **Category:** `Students`
- **Design Pattern:** `Primary Key Record Retrieval`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Phone_No FROM STUDENT_PHONE WHERE Student_ID = %s AND Phone_No = %s
```

---

### Q021: `add_student_phone`
- **Source File & Function:** `services/student_service.py` -> `add_student_phone`
- **Category:** `Students`
- **Design Pattern:** `Multivalued Child Attribute Insert/Delete`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
INSERT INTO STUDENT_PHONE (Student_ID, Phone_No) VALUES (%s, %s)
```

---

### Q022: `delete_student_phone`
- **Source File & Function:** `services/student_service.py` -> `delete_student_phone`
- **Category:** `Students`
- **Design Pattern:** `Multivalued Child Attribute Insert/Delete`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
DELETE FROM STUDENT_PHONE WHERE Student_ID = %s AND Phone_No = %s
```

---

### Q023: `list_student_skills`
- **Source File & Function:** `services/student_service.py` -> `list_student_skills`
- **Category:** `Students`
- **Design Pattern:** `Primary Key Record Retrieval`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Skill FROM STUDENT_SKILL WHERE Student_ID = %s ORDER BY Skill ASC
```

---

### Q024: `add_student_skill`
- **Source File & Function:** `services/student_service.py` -> `add_student_skill`
- **Category:** `Students`
- **Design Pattern:** `Primary Key Record Retrieval`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Skill FROM STUDENT_SKILL WHERE Student_ID = %s AND Skill = %s
```

---

### Q025: `add_student_skill`
- **Source File & Function:** `services/student_service.py` -> `add_student_skill`
- **Category:** `Students`
- **Design Pattern:** `Multivalued Child Attribute Insert/Delete`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
INSERT INTO STUDENT_SKILL (Student_ID, Skill) VALUES (%s, %s)
```

---

### Q026: `delete_student_skill`
- **Source File & Function:** `services/student_service.py` -> `delete_student_skill`
- **Category:** `Students`
- **Design Pattern:** `Multivalued Child Attribute Insert/Delete`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
DELETE FROM STUDENT_SKILL WHERE Student_ID = %s AND Skill = %s
```

---

## Category: Companies (12 Queries)

### Q027: `create_company`
- **Source File & Function:** `services/company_service.py` -> `create_company`
- **Category:** `Companies`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
INSERT INTO COMPANY (Company_Name, Company_Type, Industry, Location, Website)
        VALUES (%s, %s, %s, %s, %s)
```

---

### Q028: `create_company`
- **Source File & Function:** `services/company_service.py` -> `create_company`
- **Category:** `Companies`
- **Design Pattern:** `Pre-Insert Uniqueness Check`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Company_ID FROM COMPANY WHERE Company_Name = %s
```

---

### Q029: `get_company`
- **Source File & Function:** `services/company_service.py` -> `get_company`
- **Category:** `Companies`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Retrieves full company detail view with placement and internship counts."""
    company = execute_one(
        "SELECT Company_ID, Company_Name, Company_Type, Industry, Location, Website FROM COMPANY WHERE Company_ID = %s",
        (company_id,),
    )
    if not company:
        raise NotFoundError(f"Company with ID {company_id} not found.")

    company["Recruitment_Drives"] = []
    company["Total_Drives"] = 0

    # Check Placement / Internship stats
    history = execute_one(
```

---

### Q030: `get_company`
- **Source File & Function:** `services/company_service.py` -> `get_company`
- **Category:** `Companies`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Company_ID, Company_Name, Company_Type, Industry, Location, Website FROM COMPANY WHERE Company_ID = %s
```

---

### Q031: `list_companies`
- **Source File & Function:** `services/company_service.py` -> `list_companies`
- **Category:** `Companies`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Lists, searches, and filters recruiting companies."""
    where_clauses = ["1=1"]
    params: List[Any] = []

    if search:
        search_pattern = f"%{search.strip()}%"
        where_clauses.append("(c.Company_Name LIKE %s OR c.Industry LIKE %s OR c.Location LIKE %s)")
        params.extend([search_pattern, search_pattern, search_pattern])

    if company_type:
        where_clauses.append("c.Company_Type = %s")
        params.append(company_type.strip())

    if industry:
        where_clauses.append("c.Industry = %s")
        params.append(industry.strip())

    if location:
        where_clauses.append("c.Location = %s")
        params.append(location.strip())

    where_sql = " AND ".join(where_clauses)
    query_sql = f"""
        SELECT c.Company_ID, c.Company_Name, c.Company_Type, c.Industry, c.Location, c.Website,
               0 AS Total_Drives,
               COUNT(DISTINCT p.Placement_ID) AS Total_Placements,
               COUNT(DISTINCT i.Internship_ID) AS Total_Internships
        FROM COMPANY c
        LEFT JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
        LEFT JOIN INTERNSHIP i ON c.Company_ID = i.Company_ID
        WHERE {where_sql}
        GROUP BY c.Company_ID
        ORDER BY c.Company_Name ASC
```

---

### Q032: `update_company`
- **Source File & Function:** `services/company_service.py` -> `update_company`
- **Category:** `Companies`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Updates company attributes.
```

---

### Q033: `update_company`
- **Source File & Function:** `services/company_service.py` -> `update_company`
- **Category:** `Companies`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT * FROM COMPANY WHERE Company_ID = %s
```

---

### Q034: `update_company`
- **Source File & Function:** `services/company_service.py` -> `update_company`
- **Category:** `Companies`
- **Design Pattern:** `Pre-Insert Uniqueness Check`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Company_ID FROM COMPANY WHERE Company_Name = %s AND Company_ID != %s
```

---

### Q035: `delete_company`
- **Source File & Function:** `services/company_service.py` -> `delete_company`
- **Category:** `Companies`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Safely deletes a company, checking for dependent placements or internships.
```

---

### Q036: `delete_company`
- **Source File & Function:** `services/company_service.py` -> `delete_company`
- **Category:** `Companies`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT
            (SELECT COUNT(*) FROM PLACEMENT WHERE Company_ID = %s) AS p_cnt,
            (SELECT COUNT(*) FROM INTERNSHIP WHERE Company_ID = %s) AS i_cnt
```

---

### Q037: `delete_company`
- **Source File & Function:** `services/company_service.py` -> `delete_company`
- **Category:** `Companies`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Company_ID, Company_Name FROM COMPANY WHERE Company_ID = %s
```

---

### Q038: `delete_company`
- **Source File & Function:** `services/company_service.py` -> `delete_company`
- **Category:** `Companies`
- **Design Pattern:** `Entity Deletion by Primary Key`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
DELETE FROM COMPANY WHERE Company_ID = %s
```

---

## Category: Placements (25 Queries)

### Q039: `create_placement_offer`
- **Source File & Function:** `services/placement_service.py` -> `create_placement_offer`
- **Category:** `Placements`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Issues and records a placement offer, enforcing all business domain constraints.

    Business Rules Enforced:
    1. Joined can only be 'Yes' when Offer_Status = 'Accepted'.
    2. At most one Joined offer per student (uq_one_joined_offer).
    3. Evaluated skills are safely recorded in PLACEMENT_SKILL inside a transaction.
    """
    validate_placement_payload(data, is_update=False)

    student_id = int(data["Student_ID"])
    company_id = int(data["Company_ID"])
    role = str(data["Role"]).strip()
    package_lpa = round(float(data["Package"]), 2)
    placement_year = int(data["Placement_Year"])
    placement_type = str(data.get("Placement_Type", "On-campus") or "On-campus").strip()
    is_ppo = str(data.get("Is_PPO", "No") or "No").strip()
    offer_status = str(data.get("Offer_Status", "Offered") or "Offered").strip()
    joined = str(data.get("Joined", "No") or "No").strip()
    rounds = int(data.get("Interview_Rounds", 1) or 1)
    skills = [str(s).strip() for s in data.get("Skills", []) if str(s).strip()]

    # Integrity verification
    if joined == "Yes" and offer_status != "Accepted":
        raise ValidationError("Joined can only be 'Yes' if Offer_Status is 'Accepted'.")

    # 1. Verify Student Exists
    student = execute_one(
        "SELECT Student_ID, Roll_No, First_Name, Last_Name FROM STUDENT WHERE Student_ID = %s",
        (student_id,),
    )
    if not student:
        raise NotFoundError(f"Student with ID {student_id} does not exist.")

    # 2. Verify Company Exists
    company = execute_one(
        "SELECT Company_ID, Company_Name FROM COMPANY WHERE Company_ID = %s", (company_id,)
    )
    if not company:
        raise NotFoundError(f"Company with ID {company_id} does not exist.")

    # 3. Enforce at most ONE Joined offer per student (uq_one_joined_offer)
    if joined == "Yes":
        existing_joined = execute_one(
```

---

### Q040: `create_placement_offer`
- **Source File & Function:** `services/placement_service.py` -> `create_placement_offer`
- **Category:** `Placements`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
,
            (student_id,),
        )
        if existing_joined:
            raise ConflictError(
                f"Cannot join offer: Student {student['Roll_No']} already holds a joined offer "
                f"(Offer #{existing_joined['Placement_ID']} at {existing_joined['Company_Name']}). "
                "Institutional policy allows a student to join at most one offer."
            )

    insert_sql =
```

---

### Q041: `create_placement_offer`
- **Source File & Function:** `services/placement_service.py` -> `create_placement_offer`
- **Category:** `Placements`
- **Design Pattern:** `Primary Key Record Retrieval`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Student_ID, Roll_No, First_Name, Last_Name FROM STUDENT WHERE Student_ID = %s
```

---

### Q042: `create_placement_offer`
- **Source File & Function:** `services/placement_service.py` -> `create_placement_offer`
- **Category:** `Placements`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Company_ID, Company_Name FROM COMPANY WHERE Company_ID = %s
```

---

### Q043: `get_placement_offer`
- **Source File & Function:** `services/placement_service.py` -> `get_placement_offer`
- **Category:** `Placements`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Retrieves full placement offer record with joined student, company, and evaluated skills."""
    sql = """
        SELECT p.Placement_ID, p.Student_ID, s.Roll_No, s.First_Name, s.Last_Name,
               CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Student_Name,
               s.Branch, s.Batch_Year, s.Section, s.CGPA, s.Backlogs, s.Email, s.Resume_Link,
               p.Company_ID, c.Company_Name, c.Company_Type, c.Industry, c.Location, c.Website,
               p.Role, p.Package, p.Placement_Year, p.Placement_Type, p.Is_PPO,
               p.Joined, p.Offer_Status, p.Interview_Rounds
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE p.Placement_ID = %s
```

---

### Q044: `list_placement_offers`
- **Source File & Function:** `services/placement_service.py` -> `list_placement_offers`
- **Category:** `Placements`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Lists, searches, and filters placement offers with advanced criteria, safe sorting, and server-side pagination."""
    if per_page is not None:
        try:
            limit = int(per_page)
        except (ValueError, TypeError):
            pass

    where_clauses = ["1=1"]
    params: List[Any] = []

    if student_id is not None:
        where_clauses.append("p.Student_ID = %s")
        params.append(int(student_id))

    if company_id is not None:
        where_clauses.append("p.Company_ID = %s")
        params.append(int(company_id))

    if placement_year is not None:
        try:
            py = int(placement_year)
            where_clauses.append("p.Placement_Year = %s")
            params.append(py)
        except (ValueError, TypeError):
            pass

    if batch_year is not None:
        try:
            by = int(batch_year)
            where_clauses.append("s.Batch_Year = %s")
            params.append(by)
        except (ValueError, TypeError):
            pass

    if branch and str(branch).strip() and str(branch).strip().lower() not in ("all", "none"):
        where_clauses.append("s.Branch = %s")
        params.append(str(branch).strip())

    if (
        offer_status
        and str(offer_status).strip()
        and str(offer_status).strip().lower() not in ("all", "none")
    ):
        where_clauses.append("p.Offer_Status = %s")
        params.append(str(offer_status).strip())

    if (
        placement_type
        and str(placement_type).strip()
        and str(placement_type).strip().lower() not in ("all", "none")
    ):
        where_clauses.append("p.Placement_Type = %s")
        params.append(str(placement_type).strip())

    if is_ppo and str(is_ppo).strip() and str(is_ppo).strip().lower() not in ("all", "none"):
        where_clauses.append("p.Is_PPO = %s")
        params.append(str(is_ppo).strip())

    if joined and str(joined).strip() and str(joined).strip().lower() not in ("all", "none"):
        where_clauses.append("p.Joined = %s")
        params.append(str(joined).strip())

    if min_package is not None:
        try:
            min_p = float(min_package)
            where_clauses.append("p.Package >= %s")
            params.append(min_p)
        except (ValueError, TypeError):
            pass

    if max_package is not None:
        try:
            max_p = float(max_package)
            where_clauses.append("p.Package <= %s")
            params.append(max_p)
        except (ValueError, TypeError):
            pass

    if search and str(search).strip():
        search_pattern = f"%{str(search).strip()}%"
        where_clauses.append(
            "("
            "s.Roll_No LIKE %s OR "
            "s.First_Name LIKE %s OR "
            "s.Last_Name LIKE %s OR "
            "CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) LIKE %s OR "
            "c.Company_Name LIKE %s OR "
            "p.Role LIKE %s OR "
            "EXISTS (SELECT 1 FROM PLACEMENT_SKILL ps WHERE ps.Placement_ID = p.Placement_ID AND ps.Skill LIKE %s)"
            ")"
        )
        params.extend([search_pattern] * 7)

    where_sql = " AND ".join(where_clauses)

    count_sql = f
```

---

### Q045: `list_placement_offers`
- **Source File & Function:** `services/placement_service.py` -> `list_placement_offers`
- **Category:** `Placements`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
count_res = execute_one(count_sql, tuple(params))
    total_count = int(count_res["total"] if count_res else 0)

    SORT_MAP = {
        "package": "p.Package",
        "id": "p.Placement_ID",
        "placement_id": "p.Placement_ID",
        "roll_no": "s.Roll_No",
        "name": "s.First_Name, s.Last_Name",
        "student_name": "s.First_Name, s.Last_Name",
        "branch": "s.Branch",
        "company": "c.Company_Name",
        "company_name": "c.Company_Name",
        "role": "p.Role",
        "year": "p.Placement_Year",
        "placement_year": "p.Placement_Year",
        "batch_year": "s.Batch_Year",
        "status": "p.Offer_Status",
        "offer_status": "p.Offer_Status",
        "joined": "p.Joined",
        "is_ppo": "p.Is_PPO",
        "rounds": "p.Interview_Rounds",
    }
    sort_key = str(sort_by or "package").strip().lower()
    order_col = SORT_MAP.get(sort_key, "p.Package")
    order_dir = "ASC" if str(sort_dir).strip().lower() == "asc" else "DESC"

    if page is not None and int(page) >= 1:
        offset = (int(page) - 1) * int(limit)

    query_sql = f"""
        SELECT p.Placement_ID, p.Student_ID, s.Roll_No, s.First_Name, s.Last_Name,
               CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Student_Name,
               s.Branch, s.Batch_Year, s.CGPA, s.Backlogs, s.Email,
               p.Company_ID, c.Company_Name, c.Company_Type, c.Location, p.Role, p.Package,
               p.Placement_Year, p.Placement_Type, p.Is_PPO, p.Joined, p.Offer_Status, p.Interview_Rounds,
               GROUP_CONCAT(DISTINCT ps.Skill SEPARATOR ', ') AS Evaluated_Skills
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        LEFT JOIN PLACEMENT_SKILL ps ON p.Placement_ID = ps.Placement_ID
        WHERE {where_sql}
        GROUP BY p.Placement_ID
        ORDER BY {order_col} {order_dir}, p.Placement_ID DESC
        LIMIT %s OFFSET %s
```

---

### Q046: `get_placement_package_statistics`
- **Source File & Function:** `services/placement_service.py` -> `get_placement_package_statistics`
- **Category:** `Placements`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Calculates consolidated average, maximum, and minimum placement packages."""
    where_clauses = ["1=1"]
    params: List[Any] = []

    if placement_year is not None:
        try:
            where_clauses.append("p.Placement_Year = %s")
            params.append(int(placement_year))
        except (ValueError, TypeError):
            pass

    if batch_year is not None:
        try:
            where_clauses.append("s.Batch_Year = %s")
            params.append(int(batch_year))
        except (ValueError, TypeError):
            pass

    if branch and str(branch).strip() and str(branch).strip().lower() not in ("all", "none"):
        where_clauses.append("s.Branch = %s")
        params.append(str(branch).strip())

    if company_id is not None:
        try:
            where_clauses.append("p.Company_ID = %s")
            params.append(int(company_id))
        except (ValueError, TypeError):
            pass

    where_sql = " AND ".join(where_clauses)
    sql = f"""
        SELECT
            COUNT(p.Placement_ID) AS total_offers,
            ROUND(COALESCE(AVG(p.Package), 0), 2) AS avg_package,
            ROUND(COALESCE(MAX(p.Package), 0), 2) AS highest_package,
            ROUND(COALESCE(MIN(p.Package), 0), 2) AS lowest_package
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE {where_sql}
```

---

### Q047: `get_placement_analytics`
- **Source File & Function:** `services/placement_service.py` -> `get_placement_analytics`
- **Category:** `Placements`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Computes placement KPI metrics, company-wise statistics, branch-wise statistics,
    package distributions, and status distribution.
    Rule: 'Placed' means Joined = 'Yes'. 'Accepted Offers' tracks Offer_Status = 'Accepted'.
    """
    where_clauses = ["1=1"]
    params: List[Any] = []

    if placement_year is not None:
        try:
            where_clauses.append("p.Placement_Year = %s")
            params.append(int(placement_year))
        except (ValueError, TypeError):
            pass

    if batch_year is not None:
        try:
            where_clauses.append("s.Batch_Year = %s")
            params.append(int(batch_year))
        except (ValueError, TypeError):
            pass

    if branch and str(branch).strip() and str(branch).strip().lower() not in ("all", "none"):
        where_clauses.append("s.Branch = %s")
        params.append(str(branch).strip())

    if company_id is not None:
        try:
            where_clauses.append("p.Company_ID = %s")
            params.append(int(company_id))
        except (ValueError, TypeError):
            pass

    where_sql = " AND ".join(where_clauses)

    pkg_stats = get_placement_package_statistics(
        placement_year=placement_year,
        batch_year=batch_year,
        branch=branch,
        company_id=company_id,
    )

    kpi_sql = f"""
        SELECT
            COUNT(p.Placement_ID) AS total_offers,
            COUNT(DISTINCT p.Student_ID) AS unique_students_offered,
            COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' THEN p.Student_ID END) AS placed_students,
            COUNT(CASE WHEN p.Offer_Status = 'Accepted' THEN 1 END) AS accepted_offers,
            COUNT(CASE WHEN p.Joined = 'Yes' THEN 1 END) AS joined_offers,
            COUNT(CASE WHEN p.Is_PPO = 'Yes' THEN 1 END) AS ppo_offers,
            COUNT(CASE WHEN p.Placement_Type = 'On-campus' THEN 1 END) AS on_campus_offers,
            COUNT(CASE WHEN p.Placement_Type = 'Off-campus' THEN 1 END) AS off_campus_offers
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE {where_sql}
```

---

### Q048: `get_placement_analytics`
- **Source File & Function:** `services/placement_service.py` -> `get_placement_analytics`
- **Category:** `Placements`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT COUNT(*) AS multi_count FROM (
            SELECT p.Student_ID
            FROM PLACEMENT p
            JOIN STUDENT s ON p.Student_ID = s.Student_ID
            JOIN COMPANY c ON p.Company_ID = c.Company_ID
            WHERE {where_sql}
            GROUP BY p.Student_ID
            HAVING COUNT(p.Placement_ID) >= 2
        ) AS multi_sub
```

---

### Q049: `get_placement_analytics`
- **Source File & Function:** `services/placement_service.py` -> `get_placement_analytics`
- **Category:** `Placements`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT c.Company_ID, c.Company_Name, c.Company_Type, c.Industry,
               COUNT(p.Placement_ID) AS total_offers,
               COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' THEN p.Student_ID END) AS placed_count,
               COUNT(CASE WHEN p.Offer_Status = 'Accepted' THEN 1 END) AS accepted_count,
               ROUND(AVG(p.Package), 2) AS avg_package,
               ROUND(MAX(p.Package), 2) AS highest_package
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE {where_sql}
        GROUP BY c.Company_ID
        ORDER BY total_offers DESC, avg_package DESC
        LIMIT 10
```

---

### Q050: `get_placement_analytics`
- **Source File & Function:** `services/placement_service.py` -> `get_placement_analytics`
- **Category:** `Placements`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT s.Branch,
               COUNT(p.Placement_ID) AS total_offers,
               COUNT(DISTINCT p.Student_ID) AS unique_offered_students,
               COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' THEN p.Student_ID END) AS placed_students,
               COUNT(CASE WHEN p.Offer_Status = 'Accepted' THEN 1 END) AS accepted_offers,
               ROUND(AVG(p.Package), 2) AS avg_package,
               ROUND(MAX(p.Package), 2) AS highest_package
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE {where_sql}
        GROUP BY s.Branch
        ORDER BY placed_students DESC, avg_package DESC
```

---

### Q051: `get_placement_analytics`
- **Source File & Function:** `services/placement_service.py` -> `get_placement_analytics`
- **Category:** `Placements`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT
            SUM(CASE WHEN p.Package < {t1} THEN 1 ELSE 0 END) AS tier_below_6,
            SUM(CASE WHEN p.Package >= {t1} AND p.Package < {t2} THEN 1 ELSE 0 END) AS tier_6_to_10,
            SUM(CASE WHEN p.Package >= {t2} AND p.Package < {t3} THEN 1 ELSE 0 END) AS tier_10_to_15,
            SUM(CASE WHEN p.Package >= {t3} THEN 1 ELSE 0 END) AS tier_above_15
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE {where_sql}
```

---

### Q052: `get_placement_analytics`
- **Source File & Function:** `services/placement_service.py` -> `get_placement_analytics`
- **Category:** `Placements`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT p.Offer_Status, COUNT(*) AS count
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        WHERE {where_sql}
        GROUP BY p.Offer_Status
```

---

### Q053: `update_offer_status`
- **Source File & Function:** `services/placement_service.py` -> `update_offer_status`
- **Category:** `Placements`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Updates the status of an existing offer (Offered / Accepted / Declined).
    Enforces Rule: Joined can only be 'Yes' if Offer_Status is 'Accepted'.
    Enforces uq_one_joined_offer: at most one offer can have Joined = 'Yes'.
```

---

### Q054: `update_offer_status`
- **Source File & Function:** `services/placement_service.py` -> `update_offer_status`
- **Category:** `Placements`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT p.Placement_ID, p.Role, c.Company_Name
            FROM PLACEMENT p
            JOIN COMPANY c ON p.Company_ID = c.Company_ID
            WHERE p.Student_ID = %s
              AND p.Joined = 'Yes'
              AND p.Placement_ID != %s
```

---

### Q055: `update_placement_offer`
- **Source File & Function:** `services/placement_service.py` -> `update_placement_offer`
- **Category:** `Placements`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Updates placement offer fields and synchronization of evaluated skills.
```

---

### Q056: `update_placement_offer`
- **Source File & Function:** `services/placement_service.py` -> `update_placement_offer`
- **Category:** `Placements`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT p.Placement_ID, p.Role, c.Company_Name
            FROM PLACEMENT p
            JOIN COMPANY c ON p.Company_ID = c.Company_ID
            WHERE p.Student_ID = %s AND p.Joined = 'Yes' AND p.Placement_ID != %s
```

---

### Q057: `update_placement_offer`
- **Source File & Function:** `services/placement_service.py` -> `update_placement_offer`
- **Category:** `Placements`
- **Design Pattern:** `Multivalued Child Attribute Insert/Delete`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
DELETE FROM PLACEMENT_SKILL WHERE Placement_ID = %s
```

---

### Q058: `delete_placement_offer`
- **Source File & Function:** `services/placement_service.py` -> `delete_placement_offer`
- **Category:** `Placements`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Deletes a placement offer record.
```

---

### Q059: `delete_placement_offer`
- **Source File & Function:** `services/placement_service.py` -> `delete_placement_offer`
- **Category:** `Placements`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Placement_ID, Student_ID, Role FROM PLACEMENT WHERE Placement_ID = %s
```

---

### Q060: `delete_placement_offer`
- **Source File & Function:** `services/placement_service.py` -> `delete_placement_offer`
- **Category:** `Placements`
- **Design Pattern:** `Entity Deletion by Primary Key`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
DELETE FROM PLACEMENT WHERE Placement_ID = %s
```

---

### Q061: `get_students_with_multiple_offers`
- **Source File & Function:** `services/placement_service.py` -> `get_students_with_multiple_offers`
- **Category:** `Placements`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Identifies and aggregates students who received multiple placement offers."""
    sql = """
        SELECT s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, s.CGPA,
               COUNT(p.Placement_ID) AS Total_Offers,
               MAX(p.Package) AS Highest_Package,
               MIN(p.Package) AS Lowest_Package,
               GROUP_CONCAT(CONCAT(c.Company_Name, ' (', p.Package, ' LPA - ', p.Offer_Status, ', Joined: ', p.Joined, ')') SEPARATOR '; ') AS Offers_Breakdown,
               MAX(CASE WHEN p.Joined = 'Yes' THEN c.Company_Name ELSE NULL END) AS Placed_Company,
               MAX(CASE WHEN p.Joined = 'Yes' THEN p.Package ELSE NULL END) AS Placed_Package,
               MAX(CASE WHEN p.Offer_Status = 'Accepted' THEN c.Company_Name ELSE NULL END) AS Accepted_Company,
               MAX(CASE WHEN p.Offer_Status = 'Accepted' THEN p.Package ELSE NULL END) AS Accepted_Package
        FROM STUDENT s
        JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
        JOIN COMPANY c ON p.Company_ID = c.Company_ID
        GROUP BY s.Student_ID
        HAVING COUNT(p.Placement_ID) >= %s
        ORDER BY Total_Offers DESC, Highest_Package DESC
```

---

### Q062: `get_offer_distribution_summary`
- **Source File & Function:** `services/placement_service.py` -> `get_offer_distribution_summary`
- **Category:** `Placements`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Provides a breakdown of placement distribution: students with 0, 1, or multiple offers."""
    sql = """
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

---

### Q063: `check_candidate_eligibility_for_opportunity`
- **Source File & Function:** `services/placement_service.py` -> `check_candidate_eligibility_for_opportunity`
- **Category:** `Placements`
- **Design Pattern:** `Primary Key Record Retrieval`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Student_ID, Roll_No, First_Name, Last_Name, Branch, CGPA, Backlogs FROM STUDENT WHERE Student_ID = %s
```

---

## Category: Internships (25 Queries)

### Q064: `check_internship_eligibility`
- **Source File & Function:** `services/internship_service.py` -> `check_internship_eligibility`
- **Category:** `Internships`
- **Design Pattern:** `Primary Key Record Retrieval`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Student_ID, Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs FROM STUDENT WHERE Student_ID = %s
```

---

### Q065: `create_internship`
- **Source File & Function:** `services/internship_service.py` -> `create_internship`
- **Category:** `Internships`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Records an internship experience enforcing institutional curriculum rules."""
    validate_internship_payload(data, is_update=False)

    student_id = int(data["Student_ID"])
    company_id = int(data["Company_ID"])
    internship_no = int(data["Internship_No"])
    internship_type = str(data["Internship_Type"]).strip()
    role = str(data.get("Role", "") or "Intern").strip() or "Intern"
    rounds = int(data.get("Interview_Rounds", 1) or 1)
    stipend = round(float(data.get("Stipend", 0.0) or 0.0), 2)
    start_date = str(data["Start_Date"]).strip()
    end_date = str(data["End_Date"]).strip()

    if internship_no == 1:
        internship_type = "Mandatory"
        credits = 4
        report_sem = 5
    elif internship_no == 2:
        internship_type = "Mandatory"
        credits = 4
        report_sem = 8
    else:
        internship_type = "Additional"
        credits = int(data["Credits"]) if data.get("Credits") is not None and str(data["Credits"]).strip() != "" else None
        report_sem = int(data["Report_Semester"]) if data.get("Report_Semester") is not None and str(data["Report_Semester"]).strip() != "" else None

    report_link = str(data.get("Report_Link", "") or "").strip() or None
    report_grade = str(data.get("Report_Grade", "") or "").strip() or None
    cert_link = str(data.get("Certificate_Link", "") or "").strip() or None

    # Verify Student exists
    student = execute_one(
        "SELECT Student_ID, Roll_No FROM STUDENT WHERE Student_ID = %s", (student_id,)
    )
    if not student:
        raise NotFoundError(f"Student with ID {student_id} does not exist.")

    # Verify Company exists
    company = execute_one(
        "SELECT Company_ID, Company_Name FROM COMPANY WHERE Company_ID = %s", (company_id,)
    )
    if not company:
        raise NotFoundError(f"Company with ID {company_id} does not exist.")

    # Unique (Student_ID, Internship_No) primary key constraint
    existing_no = execute_one(
        "SELECT Internship_ID, Internship_Type, Role FROM INTERNSHIP WHERE Student_ID = %s AND Internship_No = %s",
        (student_id, internship_no),
    )
    if existing_no:
        raise ConflictError(
            f"Student {student['Roll_No']} already has an internship recorded with number {internship_no} "
            f"('{existing_no['Role']}' - Type: {existing_no['Internship_Type']})."
        )

    insert_sql =
```

---

### Q066: `create_internship`
- **Source File & Function:** `services/internship_service.py` -> `create_internship`
- **Category:** `Internships`
- **Design Pattern:** `Primary Key Record Retrieval`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Student_ID, Roll_No FROM STUDENT WHERE Student_ID = %s
```

---

### Q067: `create_internship`
- **Source File & Function:** `services/internship_service.py` -> `create_internship`
- **Category:** `Internships`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Company_ID, Company_Name FROM COMPANY WHERE Company_ID = %s
```

---

### Q068: `create_internship`
- **Source File & Function:** `services/internship_service.py` -> `create_internship`
- **Category:** `Internships`
- **Design Pattern:** `Primary Key Record Retrieval`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Internship_ID, Internship_Type, Role FROM INTERNSHIP WHERE Student_ID = %s AND Internship_No = %s
```

---

### Q069: `get_internship`
- **Source File & Function:** `services/internship_service.py` -> `get_internship`
- **Category:** `Internships`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Retrieves full internship details with joined student and company metadata."""
    sql = """
        SELECT i.Internship_ID, i.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, s.Batch_Year, s.CGPA, s.Email,
               i.Company_ID, c.Company_Name, c.Company_Type, c.Location AS Company_Location, c.Website AS Company_Website,
               i.Internship_No, i.Internship_Type, i.Role, i.Interview_Rounds, i.Stipend,
               i.Start_Date, i.End_Date, i.Credits, i.Report_Semester, i.Report_Link,
               i.Report_Grade, i.Certificate_Link
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        WHERE i.Internship_ID = %s
```

---

### Q070: `list_internships`
- **Source File & Function:** `services/internship_service.py` -> `list_internships`
- **Category:** `Internships`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Lists, filters, and searches student internships with canonical 7-table schema."""
    where_clauses = ["1=1"]
    params: List[Any] = []

    if search:
        search_term = f"%{search.strip()}%"
        where_clauses.append(
            "(s.First_Name LIKE %s OR s.Last_Name LIKE %s OR s.Roll_No LIKE %s OR c.Company_Name LIKE %s OR i.Role LIKE %s)"
        )
        params.extend([search_term, search_term, search_term, search_term, search_term])

    if student_id is not None:
        where_clauses.append("i.Student_ID = %s")
        params.append(int(student_id))

    if company_id is not None:
        where_clauses.append("i.Company_ID = %s")
        params.append(int(company_id))

    if branch and str(branch).strip().lower() not in ("all", "none", ""):
        where_clauses.append("s.Branch = %s")
        params.append(branch.strip())

    if batch_year is not None and str(batch_year).strip().lower() not in ("all", "none", ""):
        try:
            where_clauses.append("s.Batch_Year = %s")
            params.append(int(batch_year))
        except (ValueError, TypeError):
            pass

    if internship_type and str(internship_type).strip().lower() not in ("all", "none", ""):
        where_clauses.append("i.Internship_Type = %s")
        params.append(internship_type.strip())

    if internship_no is not None and str(internship_no).strip().lower() not in ("all", "none", ""):
        try:
            where_clauses.append("i.Internship_No = %s")
            params.append(int(internship_no))
        except (ValueError, TypeError):
            pass

    if report_grade and str(report_grade).strip().lower() not in ("all", "none", ""):
        where_clauses.append("i.Report_Grade = %s")
        params.append(report_grade.strip())

    if report_semester is not None and str(report_semester).strip().lower() not in (
        "all",
        "none",
        "",
    ):
        try:
            where_clauses.append("i.Report_Semester = %s")
            params.append(int(report_semester))
        except (ValueError, TypeError):
            pass

    if status and str(status).strip().lower() not in ("all", "none", ""):
        st = status.strip().lower()
        if st in ("completed", "complete"):
            where_clauses.append(
                "(i.End_Date <= CURDATE() AND (i.Report_Link IS NOT NULL OR i.Report_Grade IS NOT NULL))"
            )
        elif st in ("in_progress", "in progress", "ongoing"):
            where_clauses.append("(i.Start_Date <= CURDATE() AND i.End_Date >= CURDATE())")
        elif st in ("pending_report", "pending report", "pending"):
            where_clauses.append(
                "(i.End_Date <= CURDATE() AND (i.Report_Link IS NULL OR i.Report_Grade IS NULL OR i.Report_Grade = 'Pending'))"
            )
        elif st == "upcoming":
            where_clauses.append("(i.Start_Date > CURDATE())")

    where_sql = " AND ".join(where_clauses)

    SORT_MAP = {
        "student_id": "i.Student_ID",
        "roll_no": "s.Roll_No",
        "student_name": "s.First_Name",
        "company_name": "c.Company_Name",
        "internship_no": "i.Internship_No",
        "internship_type": "i.Internship_Type",
        "stipend": "i.Stipend",
        "start_date": "i.Start_Date",
        "end_date": "i.End_Date",
        "credits": "i.Credits",
        "report_grade": "i.Report_Grade",
        "report_semester": "i.Report_Semester",
        "branch": "s.Branch",
        "batch_year": "s.Batch_Year",
    }
    col_sql = SORT_MAP.get(sort_by.lower(), "i.Student_ID")
    dir_sql = "DESC" if sort_dir.lower() == "desc" else "ASC"
    order_sql = f"{col_sql} {dir_sql}, i.Internship_No ASC"

    count_sql = f"""
        SELECT COUNT(*) AS total
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        WHERE {where_sql}
```

---

### Q071: `list_internships`
- **Source File & Function:** `services/internship_service.py` -> `list_internships`
- **Category:** `Internships`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT i.Internship_ID, i.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, s.Batch_Year, s.CGPA, s.Email,
               i.Company_ID, c.Company_Name, c.Company_Type,
               i.Internship_No, i.Internship_Type, i.Role, i.Interview_Rounds, i.Stipend,
               i.Start_Date, i.End_Date, i.Credits, i.Report_Semester, i.Report_Link,
               i.Report_Grade, i.Certificate_Link
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        WHERE {where_sql}
        ORDER BY {order_sql}
        {limit_clause}
```

---

### Q072: `update_internship`
- **Source File & Function:** `services/internship_service.py` -> `update_internship`
- **Category:** `Internships`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Updates internship attributes with curriculum constraint validation.
```

---

### Q073: `delete_internship`
- **Source File & Function:** `services/internship_service.py` -> `delete_internship`
- **Category:** `Internships`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Deletes an internship record.
```

---

### Q074: `delete_internship`
- **Source File & Function:** `services/internship_service.py` -> `delete_internship`
- **Category:** `Internships`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Internship_ID, Student_ID, Internship_No, Internship_Type FROM INTERNSHIP WHERE Internship_ID = %s
```

---

### Q075: `delete_internship`
- **Source File & Function:** `services/internship_service.py` -> `delete_internship`
- **Category:** `Internships`
- **Design Pattern:** `Entity Deletion by Primary Key`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
DELETE FROM INTERNSHIP WHERE Internship_ID = %s
```

---

### Q076: `get_mandatory_internships_with_prerequisite_sgpa`
- **Source File & Function:** `services/internship_service.py` -> `get_mandatory_internships_with_prerequisite_sgpa`
- **Category:** `Internships`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Retrieves mandatory internships joined with Student and Company."""
    sql = """
        SELECT
            i.Internship_ID,
            i.Student_ID,
            s.Roll_No,
            CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Student_Name,
            s.Branch,
            s.Batch_Year,
            s.CGPA,
            c.Company_Name,
            i.Internship_No,
            i.Internship_Type,
            i.Role,
            i.Stipend,
            i.Start_Date,
            i.End_Date,
            i.Credits,
            i.Report_Semester,
            i.Report_Link,
            i.Certificate_Link,
            i.Report_Grade
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        JOIN COMPANY c ON i.Company_ID = c.Company_ID
        WHERE i.Internship_Type = 'Mandatory'
        ORDER BY i.Internship_No ASC, s.CGPA DESC;
```

---

### Q077: `get_students_missing_mandatory_internships`
- **Source File & Function:** `services/internship_service.py` -> `get_students_missing_mandatory_internships`
- **Category:** `Internships`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Identifies students who have NOT completed mandatory internships."""
    where_conds = ["(i1.Internship_ID IS NULL OR i2.Internship_ID IS NULL)"]
    params: List[Any] = []

    if branch and str(branch).strip().lower() not in ("all", "none", ""):
        where_conds.append("s.Branch = %s")
        params.append(branch.strip())

    if batch_year is not None and str(batch_year).strip().lower() not in ("all", "none", ""):
        try:
            where_conds.append("s.Batch_Year = %s")
            params.append(int(batch_year))
        except (ValueError, TypeError):
            pass

    clause = " AND ".join(where_conds)
    sql = f"""
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
        WHERE {clause}
        ORDER BY s.Batch_Year ASC, s.Roll_No ASC;
```

---

### Q078: `get_branch_internship_statistics`
- **Source File & Function:** `services/internship_service.py` -> `get_branch_internship_statistics`
- **Category:** `Internships`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Computes branch-wise internship completion statistics."""
    sql = """
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

---

### Q079: `get_branch_internship_statistics`
- **Source File & Function:** `services/internship_service.py` -> `get_branch_internship_statistics`
- **Category:** `Internships`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT s.Branch, COUNT(DISTINCT s.Student_ID) AS both_completed
        FROM STUDENT s
        JOIN INTERNSHIP i1 ON s.Student_ID = i1.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = 'Mandatory'
        JOIN INTERNSHIP i2 ON s.Student_ID = i2.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = 'Mandatory'
        GROUP BY s.Branch
```

---

### Q080: `get_batch_compliance_reports`
- **Source File & Function:** `services/internship_service.py` -> `get_batch_compliance_reports`
- **Category:** `Internships`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Computes batch-wise compliance reports."""
    sql = """
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

---

### Q081: `get_batch_compliance_reports`
- **Source File & Function:** `services/internship_service.py` -> `get_batch_compliance_reports`
- **Category:** `Internships`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT s.Batch_Year, COUNT(DISTINCT s.Student_ID) AS both_completed
        FROM STUDENT s
        JOIN INTERNSHIP i1 ON s.Student_ID = i1.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = 'Mandatory'
        JOIN INTERNSHIP i2 ON s.Student_ID = i2.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = 'Mandatory'
        GROUP BY s.Batch_Year
```

---

### Q082: `get_internship_dashboard_analytics`
- **Source File & Function:** `services/internship_service.py` -> `get_internship_dashboard_analytics`
- **Category:** `Internships`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Computes comprehensive executive analytics for the Internship Management Dashboard."""
    tot_res = (
        execute_one(
            "SELECT COUNT(*) AS total_internships, ROUND(COALESCE(AVG(Stipend), 0), 2) AS avg_stipend, ROUND(COALESCE(MAX(Stipend), 0), 2) AS max_stipend FROM INTERNSHIP"
        )
        or {}
    )
    total_internships = int(tot_res.get("total_internships") or 0)
    avg_stipend = float(tot_res.get("avg_stipend") or 0.0)
    max_stipend = float(tot_res.get("max_stipend") or 0.0)

    m_res = execute_one(
```

---

### Q083: `get_internship_dashboard_analytics`
- **Source File & Function:** `services/internship_service.py` -> `get_internship_dashboard_analytics`
- **Category:** `Internships`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
) or {}
    i1_count = int(m_res.get("i1_count") or 0)
    i2_count = int(m_res.get("i2_count") or 0)
    additional_count = int(m_res.get("additional_count") or 0)

    stud_count_res = execute_one("SELECT COUNT(*) AS total_students FROM STUDENT") or {}
    total_students = int(stud_count_res.get("total_students") or 0)

    both_sql =
```

---

### Q084: `get_internship_dashboard_analytics`
- **Source File & Function:** `services/internship_service.py` -> `get_internship_dashboard_analytics`
- **Category:** `Internships`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
comp_res = execute_one(both_sql) or {}
    fully_compliant = int(comp_res.get("fully_compliant") or 0)
    compliance_rate = (
        round((fully_compliant / total_students * 100), 1) if total_students > 0 else 0.0
    )

    pending_sql = """
        SELECT COUNT(*) AS pending_count FROM INTERNSHIP
        WHERE End_Date <= CURDATE() AND (Report_Link IS NULL OR Report_Grade IS NULL OR Report_Grade = 'Pending')
```

---

### Q085: `get_internship_dashboard_analytics`
- **Source File & Function:** `services/internship_service.py` -> `get_internship_dashboard_analytics`
- **Category:** `Internships`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT COALESCE(Report_Grade, 'Ungraded') AS grade, COUNT(*) AS count
        FROM INTERNSHIP
        GROUP BY COALESCE(Report_Grade, 'Ungraded')
        ORDER BY count DESC
```

---

### Q086: `get_internship_dashboard_analytics`
- **Source File & Function:** `services/internship_service.py` -> `get_internship_dashboard_analytics`
- **Category:** `Internships`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

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

---

### Q087: `get_internship_dashboard_analytics`
- **Source File & Function:** `services/internship_service.py` -> `get_internship_dashboard_analytics`
- **Category:** `Internships`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT COUNT(*) AS total_internships, ROUND(COALESCE(AVG(Stipend), 0), 2) AS avg_stipend, ROUND(COALESCE(MAX(Stipend), 0), 2) AS max_stipend FROM INTERNSHIP
```

---

### Q088: `get_internship_dashboard_analytics`
- **Source File & Function:** `services/internship_service.py` -> `get_internship_dashboard_analytics`
- **Category:** `Internships`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT COUNT(*) AS total_students FROM STUDENT
```

---

## Category: Dashboard (18 Queries)

### Q089: `get_dashboard_filter_options`
- **Source File & Function:** `services/dashboard_service.py` -> `get_dashboard_filter_options`
- **Category:** `Dashboard`
- **Design Pattern:** `Dropdown Distinct Filter Lookup`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT DISTINCT Branch FROM STUDENT WHERE Branch IS NOT NULL AND Branch !=
```

---

### Q090: `get_dashboard_filter_options`
- **Source File & Function:** `services/dashboard_service.py` -> `get_dashboard_filter_options`
- **Category:** `Dashboard`
- **Design Pattern:** `Dropdown Distinct Filter Lookup`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT DISTINCT Batch_Year FROM STUDENT WHERE Batch_Year IS NOT NULL ORDER BY Batch_Year DESC
```

---

### Q091: `get_dashboard_filter_options`
- **Source File & Function:** `services/dashboard_service.py` -> `get_dashboard_filter_options`
- **Category:** `Dashboard`
- **Design Pattern:** `Dropdown Distinct Filter Lookup`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT DISTINCT Placement_Year FROM PLACEMENT WHERE Placement_Year IS NOT NULL ORDER BY Placement_Year DESC
```

---

### Q092: `get_dashboard_stats`
- **Source File & Function:** `services/dashboard_service.py` -> `get_dashboard_stats`
- **Category:** `Dashboard`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Aggregates enterprise placement KPI metrics.
    Rule: 'Placed' means Joined = 'Yes'.
    """
    clean_filters = _extract_clean_filters(filters)
    branch = clean_filters.get("branch")
    batch_year = clean_filters.get("batch_year")
    placement_year = clean_filters.get("placement_year")

    # 1. Student Master Statistics
    s_conds, s_params = ["1=1"], []
    if branch:
        s_conds.append("s.Branch = %s")
        s_params.append(branch)
    if batch_year:
        s_conds.append("s.Batch_Year = %s")
        s_params.append(batch_year)
    elif placement_year:
        s_conds.append("s.Batch_Year = %s")
        s_params.append(placement_year)

    s_clause = " AND ".join(s_conds)
    student_stats = (
        execute_one(
            f"""
        SELECT
            COUNT(*) AS total_students,
            COUNT(*) AS active_students,
            COUNT(CASE WHEN s.Backlogs = 0 AND s.CGPA >= 6.00 THEN 1 END) AS eligible_students,
            ROUND(COALESCE(AVG(s.CGPA), 0), 2) AS avg_cgpa
        FROM STUDENT s
        WHERE {s_clause}
```

---

### Q093: `get_dashboard_stats`
- **Source File & Function:** `services/dashboard_service.py` -> `get_dashboard_stats`
- **Category:** `Dashboard`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT
            COUNT(p.Placement_ID) AS total_offers,
            COUNT(DISTINCT p.Student_ID) AS distinct_students_offered,
            COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' THEN p.Student_ID END) AS placed_students,
            SUM(CASE WHEN p.Offer_Status = 'Accepted' THEN 1 ELSE 0 END) AS accepted_offers,
            SUM(CASE WHEN p.Joined = 'Yes' THEN 1 ELSE 0 END) AS joined_offers,
            COUNT(DISTINCT p.Company_ID) AS companies_with_offers
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        WHERE {p_clause}
```

---

### Q094: `get_dashboard_stats`
- **Source File & Function:** `services/dashboard_service.py` -> `get_dashboard_stats`
- **Category:** `Dashboard`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT
            COUNT(i.Internship_ID) AS total_internships,
            SUM(CASE WHEN i.Internship_Type = 'Mandatory' THEN 1 ELSE 0 END) AS mandatory_internships,
            SUM(CASE WHEN i.Internship_Type = 'Additional' THEN 1 ELSE 0 END) AS additional_internships,
            COUNT(DISTINCT i.Student_ID) AS distinct_students_interned
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        WHERE {i_clause}
```

---

### Q095: `get_dashboard_stats`
- **Source File & Function:** `services/dashboard_service.py` -> `get_dashboard_stats`
- **Category:** `Dashboard`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT COUNT(*) AS missing_count
        FROM (
            SELECT s.Student_ID
            FROM STUDENT s
            LEFT JOIN INTERNSHIP i1 ON s.Student_ID = i1.Student_ID AND i1.Internship_No = 1 AND i1.Internship_Type = 'Mandatory'
            LEFT JOIN INTERNSHIP i2 ON s.Student_ID = i2.Student_ID AND i2.Internship_No = 2 AND i2.Internship_Type = 'Mandatory'
            WHERE {s_clause} AND (i1.Internship_ID IS NULL OR i2.Internship_ID IS NULL)
        ) AS missing_students
```

---

### Q096: `get_dashboard_stats`
- **Source File & Function:** `services/dashboard_service.py` -> `get_dashboard_stats`
- **Category:** `Dashboard`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT COUNT(*) AS total_companies FROM COMPANY
```

---

### Q097: `get_dashboard_stats`
- **Source File & Function:** `services/dashboard_service.py` -> `get_dashboard_stats`
- **Category:** `Dashboard`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT SUM(CASE WHEN Company_Type =
```

---

### Q098: `get_branchwise_analytics_chart_data`
- **Source File & Function:** `services/dashboard_service.py` -> `get_branchwise_analytics_chart_data`
- **Category:** `Dashboard`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Visualization 1: Branch-wise placement distribution. Placed students check Joined = 'Yes'."""
    clean_filters = _extract_clean_filters(filters)
    batch_year = clean_filters.get("batch_year")
    placement_year = clean_filters.get("placement_year")
    branch = clean_filters.get("branch")

    s_conds, s_params = ["1=1"], []
    if branch:
        s_conds.append("s.Branch = %s")
        s_params.append(branch)
    if batch_year:
        s_conds.append("s.Batch_Year = %s")
        s_params.append(batch_year)
    elif placement_year:
        s_conds.append("s.Batch_Year = %s")
        s_params.append(placement_year)

    p_extra_join = ""
    if placement_year:
        p_extra_join = f" AND p.Placement_Year = {int(placement_year)}"

    s_clause = " AND ".join(s_conds)
    rows = execute_query(
        f"""
        SELECT
            s.Branch,
            COUNT(DISTINCT s.Student_ID) AS student_count,
            COUNT(DISTINCT CASE WHEN s.Backlogs = 0 AND s.CGPA >= 6.00 THEN s.Student_ID END) AS eligible_students,
            COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' THEN s.Student_ID END) AS placed_students,
            COUNT(DISTINCT p.Placement_ID) AS offer_count,
            COUNT(DISTINCT i.Internship_ID) AS internship_count,
            ROUND(COALESCE(AVG(s.CGPA), 0), 2) AS avg_cgpa,
            ROUND(COALESCE(AVG(p.Package), 0), 2) AS avg_package
        FROM STUDENT s
        LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID {p_extra_join}
        LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
        WHERE {s_clause}
        GROUP BY s.Branch
        ORDER BY student_count DESC, s.Branch ASC
```

---

### Q099: `get_yearwise_placement_chart_data`
- **Source File & Function:** `services/dashboard_service.py` -> `get_yearwise_placement_chart_data`
- **Category:** `Dashboard`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Visualization 2: Year-wise placement trends."""
    clean_filters = _extract_clean_filters(filters)
    branch = clean_filters.get("branch")
    batch_year = clean_filters.get("batch_year")

    conds, params = ["1=1"], []
    if branch:
        conds.append("s.Branch = %s")
        params.append(branch)
    if batch_year:
        conds.append("s.Batch_Year = %s")
        params.append(batch_year)

    clause = " AND ".join(conds)
    rows = execute_query(
        f"""
        SELECT
            p.Placement_Year,
            COUNT(p.Placement_ID) AS offer_count,
            SUM(CASE WHEN p.Joined = 'Yes' THEN 1 ELSE 0 END) AS accepted_count,
            ROUND(COALESCE(AVG(p.Package), 0), 2) AS avg_package,
            ROUND(COALESCE(MAX(p.Package), 0), 2) AS max_package
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        WHERE {clause}
        GROUP BY p.Placement_Year
        ORDER BY p.Placement_Year ASC
```

---

### Q100: `get_package_distribution_chart_data`
- **Source File & Function:** `services/dashboard_service.py` -> `get_package_distribution_chart_data`
- **Category:** `Dashboard`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Visualization 3: CTC package distribution."""
    clean_filters = _extract_clean_filters(filters)
    branch = clean_filters.get("branch")
    batch_year = clean_filters.get("batch_year")
    placement_year = clean_filters.get("placement_year")

    conds, params = ["1=1"], []
    if branch:
        conds.append("s.Branch = %s")
        params.append(branch)
    if batch_year:
        conds.append("s.Batch_Year = %s")
        params.append(batch_year)
    if placement_year:
        conds.append("p.Placement_Year = %s")
        params.append(placement_year)

    clause = " AND ".join(conds)
    tiers = [
        {"key": "< 8 LPA", "label": "< 8 LPA (Core / Regular)", "min": 0, "max": 7.99},
        {"key": "8 - 12 LPA", "label": "8 - 12 LPA (Dream)", "min": 8.00, "max": 11.99},
        {"key": "12 - 16 LPA", "label": "12 - 16 LPA (Super Dream)", "min": 12.00, "max": 15.99},
        {"key": "16+ LPA", "label": "16+ LPA (Marquee / Elite)", "min": 16.00, "max": 999.00},
    ]

    tier_counts = {t["key"]: 0 for t in tiers}
    rows = execute_query(
        f"""
        SELECT p.Package
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        WHERE {clause}
```

---

### Q101: `get_placement_vs_internship_chart_data`
- **Source File & Function:** `services/dashboard_service.py` -> `get_placement_vs_internship_chart_data`
- **Category:** `Dashboard`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Visualization 4: Placement versus internship statistics."""
    clean_filters = _extract_clean_filters(filters)
    branch = clean_filters.get("branch")
    batch_year = clean_filters.get("batch_year")
    placement_year = clean_filters.get("placement_year")

    s_conds, s_params = ["1=1"], []
    if branch:
        s_conds.append("s.Branch = %s")
        s_params.append(branch)
    if batch_year:
        s_conds.append("s.Batch_Year = %s")
        s_params.append(batch_year)
    elif placement_year:
        s_conds.append("s.Batch_Year = %s")
        s_params.append(placement_year)

    p_extra_join = f" AND p.Placement_Year = {int(placement_year)}" if placement_year else ""

    s_clause = " AND ".join(s_conds)
    rows = execute_query(
        f"""
        SELECT
            s.Branch,
            COUNT(DISTINCT p.Placement_ID) AS placement_offers,
            COUNT(DISTINCT i.Internship_ID) AS total_internships,
            COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' THEN s.Student_ID END) AS placed_students,
            COUNT(DISTINCT i.Student_ID) AS interned_students
        FROM STUDENT s
        LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID {p_extra_join}
        LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
        WHERE {s_clause}
        GROUP BY s.Branch
        ORDER BY s.Branch ASC
```

---

### Q102: `get_internship_completion_chart_data`
- **Source File & Function:** `services/dashboard_service.py` -> `get_internship_completion_chart_data`
- **Category:** `Dashboard`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Visualization 5: Internship completion percentage."""
    clean_filters = _extract_clean_filters(filters)
    branch = clean_filters.get("branch")
    batch_year = clean_filters.get("batch_year")
    placement_year = clean_filters.get("placement_year")

    s_conds, s_params = ["1=1"], []
    if branch:
        s_conds.append("s.Branch = %s")
        s_params.append(branch)
    if batch_year:
        s_conds.append("s.Batch_Year = %s")
        s_params.append(batch_year)
    elif placement_year:
        s_conds.append("s.Batch_Year = %s")
        s_params.append(placement_year)

    s_clause = " AND ".join(s_conds)
    rows = execute_query(
        f"""
        SELECT
            status_category,
            COUNT(*) AS student_count
        FROM (
            SELECT
                s.Student_ID,
                CASE
                    WHEN COUNT(DISTINCT CASE WHEN i.Internship_Type = 'Mandatory' AND i.Internship_No = 1 THEN i.Internship_ID END) > 0
                     AND COUNT(DISTINCT CASE WHEN i.Internship_Type = 'Mandatory' AND i.Internship_No = 2 THEN i.Internship_ID END) > 0
                    THEN 'Fully Completed (Both)'
                    WHEN COUNT(DISTINCT CASE WHEN i.Internship_Type = 'Mandatory' AND i.Internship_No IN (1, 2) THEN i.Internship_ID END) > 0
                    THEN 'Partially Completed (1 of 2)'
                    ELSE 'Pending / Incomplete'
                END AS status_category
            FROM STUDENT s
            LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
            WHERE {s_clause}
            GROUP BY s.Student_ID
        ) AS student_compliance
        GROUP BY status_category
        ORDER BY FIELD(status_category, 'Fully Completed (Both)', 'Partially Completed (1 of 2)', 'Pending / Incomplete')
```

---

### Q103: `get_multiple_offers_chart_data`
- **Source File & Function:** `services/dashboard_service.py` -> `get_multiple_offers_chart_data`
- **Category:** `Dashboard`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Visualization 6: Multiple-offer student statistics."""
    clean_filters = _extract_clean_filters(filters)
    branch = clean_filters.get("branch")
    batch_year = clean_filters.get("batch_year")
    placement_year = clean_filters.get("placement_year")

    s_conds, s_params = ["1=1"], []
    if branch:
        s_conds.append("s.Branch = %s")
        s_params.append(branch)
    if batch_year:
        s_conds.append("s.Batch_Year = %s")
        s_params.append(batch_year)
    elif placement_year:
        s_conds.append("s.Batch_Year = %s")
        s_params.append(placement_year)

    p_extra_join = f" AND p.Placement_Year = {int(placement_year)}" if placement_year else ""

    s_clause = " AND ".join(s_conds)
    rows = execute_query(
        f"""
        SELECT
            offer_tier,
            COUNT(*) AS student_count
        FROM (
            SELECT
                s.Student_ID,
                CASE
                    WHEN COUNT(p.Placement_ID) = 0 THEN '0 Offers (Unplaced)'
                    WHEN COUNT(p.Placement_ID) = 1 THEN '1 Offer (Single)'
                    WHEN COUNT(p.Placement_ID) = 2 THEN '2 Offers (Dual)'
                    ELSE '3+ Offers (Multiple)'
                END AS offer_tier
            FROM STUDENT s
            LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID {p_extra_join}
            WHERE {s_clause}
            GROUP BY s.Student_ID
        ) AS student_offers
        GROUP BY offer_tier
        ORDER BY FIELD(offer_tier, '0 Offers (Unplaced)', '1 Offer (Single)', '2 Offers (Dual)', '3+ Offers (Multiple)')
```

---

### Q104: `get_offer_status_chart_data`
- **Source File & Function:** `services/dashboard_service.py` -> `get_offer_status_chart_data`
- **Category:** `Dashboard`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Fetches breakdown of placement statuses (Offered, Accepted, Declined)."""
    clean_filters = _extract_clean_filters(filters)
    branch = clean_filters.get("branch")
    batch_year = clean_filters.get("batch_year")
    placement_year = clean_filters.get("placement_year")

    conds, params = ["1=1"], []
    if branch:
        conds.append("s.Branch = %s")
        params.append(branch)
    if batch_year:
        conds.append("s.Batch_Year = %s")
        params.append(batch_year)
    if placement_year:
        conds.append("p.Placement_Year = %s")
        params.append(placement_year)

    clause = " AND ".join(conds)
    rows = execute_query(
        f"""
        SELECT
            p.Offer_Status,
            COUNT(*) AS count
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        WHERE {clause}
        GROUP BY p.Offer_Status
        ORDER BY FIELD(p.Offer_Status, 'Offered', 'Accepted', 'Declined')
```

---

### Q105: `get_internship_breakdown_chart_data`
- **Source File & Function:** `services/dashboard_service.py` -> `get_internship_breakdown_chart_data`
- **Category:** `Dashboard`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Fetches breakdown of internships: Mandatory #1, Mandatory #2, Additional."""
    clean_filters = _extract_clean_filters(filters)
    branch = clean_filters.get("branch")
    batch_year = clean_filters.get("batch_year")
    placement_year = clean_filters.get("placement_year")

    conds, params = ["1=1"], []
    if branch:
        conds.append("s.Branch = %s")
        params.append(branch)
    if batch_year:
        conds.append("s.Batch_Year = %s")
        params.append(batch_year)
    elif placement_year:
        conds.append("s.Batch_Year = %s")
        params.append(placement_year)

    clause = " AND ".join(conds)
    rows = execute_query(
        f"""
        SELECT
            CASE
                WHEN i.Internship_Type = 'Mandatory' AND i.Internship_No = 1 THEN 'Mandatory #1 (Sem 5)'
                WHEN i.Internship_Type = 'Mandatory' AND i.Internship_No = 2 THEN 'Mandatory #2 (8th Sem)'
                ELSE 'Additional Internships'
            END AS category,
            COUNT(*) AS count
        FROM INTERNSHIP i
        JOIN STUDENT s ON i.Student_ID = s.Student_ID
        WHERE {clause}
        GROUP BY category
        ORDER BY category ASC
```

---

### Q106: `get_comprehensive_report_data`
- **Source File & Function:** `services/dashboard_service.py` -> `get_comprehensive_report_data`
- **Category:** `Dashboard`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Fetches a detailed, multi-dimensional report on students with placement and internship status.
    Rule: 'Placed' means Joined = 'Yes'.
    """
    conditions = ["1=1"]
    params: List[Any] = []

    if filters.get("branch"):
        conditions.append("s.Branch = %s")
        params.append(filters["branch"])

    search_val = str(filters.get("search", "")).strip() if filters.get("search") else None
    if search_val:
        conditions.append(
            "(s.First_Name LIKE %s OR s.Last_Name LIKE %s OR CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) LIKE %s OR s.Roll_No LIKE %s OR s.Email LIKE %s OR s.Branch LIKE %s)"
        )
        like_term = f"%{search_val}%"
        params.extend([like_term] * 6)

    if filters.get("min_cgpa"):
        try:
            min_cgpa = float(filters["min_cgpa"])
            conditions.append("s.CGPA >= %s")
            params.append(min_cgpa)
        except (ValueError, TypeError):
            pass

    where_clause = " AND ".join(conditions)

    sql = f"""
        SELECT
            s.Student_ID,
            s.Roll_No,
            CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Full_Name,
            s.Email,
            s.Branch,
            s.Batch_Year,
            s.CGPA,
            COUNT(DISTINCT p.Placement_ID) AS Total_Offers,
            MAX(CASE WHEN p.Joined = 'Yes' THEN c.Company_Name ELSE NULL END) AS Placed_Company,
            MAX(CASE WHEN p.Joined = 'Yes' THEN p.Package ELSE NULL END) AS Placed_Package,
            MAX(CASE WHEN p.Joined = 'Yes' THEN p.Offer_Status ELSE NULL END) AS Final_Status,
            COUNT(DISTINCT CASE WHEN i.Internship_Type = 'Mandatory' AND i.Internship_No = 1 THEN i.Internship_ID ELSE NULL END) AS Has_Mandatory_1,
            COUNT(DISTINCT CASE WHEN i.Internship_Type = 'Mandatory' AND i.Internship_No = 2 THEN i.Internship_ID ELSE NULL END) AS Has_Mandatory_2,
            COUNT(DISTINCT CASE WHEN i.Internship_Type = 'Additional' THEN i.Internship_ID ELSE NULL END) AS Additional_Internship_Count
        FROM STUDENT s
        LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
        LEFT JOIN COMPANY c ON p.Company_ID = c.Company_ID
        LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
        WHERE {where_clause}
        GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Email, s.Branch, s.Batch_Year, s.CGPA
        ORDER BY s.Batch_Year ASC, s.Roll_No ASC
```

---

## Category: Reports (51 Queries)

### Q107: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Retrieves centralized (max_rows, timeout_ms) for custom and saved SQL execution."""
    max_rows = getattr(Config, "SQL_REPORT_MAX_ROWS", 500)
    timeout_ms = getattr(Config, "SQL_REPORT_TIMEOUT_MS", 3000)
    try:
        from flask import current_app, has_app_context

        if has_app_context() and current_app:
            max_rows = int(current_app.config.get("SQL_REPORT_MAX_ROWS", max_rows))
            timeout_ms = int(current_app.config.get("SQL_REPORT_TIMEOUT_MS", timeout_ms))
    except Exception:
        pass
    return max_rows, timeout_ms


# ==============================================================================
# CATALOG OF SAVED DBMS QUERIES
# Categorized into: Students, Placements, Internships, Combined
# ==============================================================================

SAVED_QUERIES: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # 1. STUDENTS
    # -------------------------------------------------------------------------
    {
        "id": "students_all",
        "title": "A1. List All Registered Students",
        "group": "Students",
        "dbms_concept": "Relational projection (π) and lexicographical multi-attribute ordering (ORDER BY Batch_Year, Branch, Student_Name).",
        "sql": """SELECT Student_ID, Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Student_Name,
       Branch, Batch_Year, CGPA, Backlogs
FROM STUDENT
ORDER BY Batch_Year, Branch, Student_Name;
```

---

### Q108: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Student_Name, Branch, Batch_Year, CGPA
FROM STUDENT
WHERE Branch = %s AND Batch_Year = %s
ORDER BY CGPA DESC;
```

---

### Q109: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       s.Branch, s.Batch_Year, s.CGPA, s.Backlogs, s.Resume_Link,
       (SELECT GROUP_CONCAT(ph.Phone_No SEPARATOR ', ')
          FROM STUDENT_PHONE ph WHERE ph.Student_ID = s.Student_ID) AS Phones,
       (SELECT GROUP_CONCAT(sk.Skill SEPARATOR ', ')
          FROM STUDENT_SKILL sk WHERE sk.Student_ID = s.Student_ID) AS Extra_Skills
FROM STUDENT s
WHERE s.Roll_No = %s;
```

---

### Q110: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.CGPA, sk.Skill
FROM STUDENT s
JOIN STUDENT_SKILL sk ON sk.Student_ID = s.Student_ID
WHERE sk.Skill = %s
ORDER BY s.CGPA DESC;
```

---

### Q111: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Roll_No, CONCAT_WS(' ', First_Name, Last_Name) AS Student_Name, Branch, Batch_Year, CGPA, Backlogs
FROM STUDENT
WHERE CGPA >= %s AND Backlogs = 0
ORDER BY CGPA DESC;
```

---

### Q112: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT s.Student_ID, s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       s.Branch, s.Batch_Year, s.CGPA
FROM STUDENT s
LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID AND p.Joined = 'Yes'
WHERE p.Placement_ID IS NULL
ORDER BY s.CGPA DESC;
```

---

### Q113: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name, s.Branch, s.Batch_Year, s.CGPA,
       ROUND((SELECT AVG(CGPA) FROM STUDENT), 2) AS Benchmark_Avg_CGPA,
       ROUND(s.CGPA - (SELECT AVG(CGPA) FROM STUDENT), 2) AS Delta_From_Avg
FROM STUDENT s
WHERE s.CGPA > (SELECT AVG(CGPA) FROM STUDENT)
ORDER BY s.CGPA DESC;
```

---

### Q114: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       s.Branch, s.CGPA, COALESCE(c.Company_Name, 'Unplaced') AS Joined_Company, p.Package
FROM STUDENT s
LEFT JOIN PLACEMENT p ON p.Student_ID = s.Student_ID AND p.Joined = 'Yes'
LEFT JOIN COMPANY   c ON c.Company_ID = p.Company_ID
WHERE s.First_Name LIKE %s OR s.Last_Name LIKE %s
ORDER BY s.Student_ID;
```

---

### Q115: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Roll_No, Student_Name, Branch, Batch_Year, Company_Name, Role, Package, Placement_Year
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
ORDER BY Package DESC;
```

---

### Q116: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Pre-Insert Uniqueness Check`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Student_Name, Branch, Batch_Year, Role, Package, Placement_Year, Joined
FROM V_PLACEMENT_DETAIL
WHERE Company_Name = %s
ORDER BY Placement_Year, Package DESC;
```

---

### Q117: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Branch,
       COUNT(*)               AS Students_Placed,
       ROUND(AVG(Package), 2) AS Avg_Package,
       MAX(Package)           AS Highest_Package,
       MIN(Package)           AS Lowest_Package
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
GROUP BY Branch
ORDER BY Avg_Package DESC;
```

---

### Q118: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

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

---

### Q119: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

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

---

### Q120: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Student_Name, Branch, Company_Name, Package, Placement_Year
FROM V_PLACEMENT_DETAIL
WHERE Joined = 'Yes'
ORDER BY Package DESC
LIMIT 5;
```

---

### Q121: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

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

---

### Q122: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Student_Name, Roll_No,
       COUNT(*) AS Total_Offers,
       GROUP_CONCAT(CONCAT(Company_Name, ' (', Package, ' LPA)') SEPARATOR ', ') AS Offers,
       MAX(CASE WHEN Joined = 'Yes' THEN Company_Name END) AS Joined_Company
FROM V_PLACEMENT_DETAIL
GROUP BY Student_ID, Student_Name, Roll_No
HAVING COUNT(*) > 1;
```

---

### Q123: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Student_Name, Branch, Company_Name, Package, Placement_Year, Joined
FROM V_PLACEMENT_DETAIL
WHERE Is_PPO = 'Yes'
ORDER BY Placement_Year, Package DESC;
```

---

### Q124: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

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

---

### Q125: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Student_Name, Branch, Company_Name, Role, Package, Placement_Year
FROM V_PLACEMENT_DETAIL
WHERE Package >= %s AND Joined = 'Yes'
ORDER BY Package DESC;
```

---

### Q126: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Pre-Insert Uniqueness Check`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Internship_No, Internship_Type, Company_Name, Role,
       Start_Date, End_Date, Duration_Months, Stipend,
       Credits, Report_Semester, Report_Grade
FROM V_INTERNSHIP_DETAIL
WHERE Roll_No = %s
ORDER BY Internship_No;
```

---

### Q127: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Pre-Insert Uniqueness Check`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Student_Name, Branch, Internship_No, Role, Start_Date, End_Date, Stipend
FROM V_INTERNSHIP_DETAIL
WHERE Company_Name = %s
ORDER BY Start_Date;
```

---

### Q128: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

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

---

### Q129: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT s.Roll_No, CONCAT_WS(' ', s.First_Name, s.Last_Name) AS Student_Name,
       COUNT(CASE WHEN i.Internship_Type = 'Mandatory' THEN 1 END) AS Mandatory_Done
FROM STUDENT s
LEFT JOIN INTERNSHIP i ON i.Student_ID = s.Student_ID
GROUP BY s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name
HAVING COUNT(CASE WHEN i.Internship_Type = 'Mandatory' THEN 1 END) < 2;
```

---

### Q130: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Company_Name,
       COUNT(*)               AS Interns,
       ROUND(AVG(Stipend), 0) AS Avg_Stipend,
       MAX(Stipend)           AS Highest_Stipend
FROM V_INTERNSHIP_DETAIL
GROUP BY Company_ID, Company_Name
ORDER BY Avg_Stipend DESC;
```

---

### Q131: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Student_Name, Internship_No, Company_Name, Role, Start_Date, End_Date, Stipend
FROM V_INTERNSHIP_DETAIL
WHERE Start_Date >= %s AND End_Date <= %s
ORDER BY Start_Date;
```

---

### Q132: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Dropdown Distinct Filter Lookup`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT DISTINCT p.Student_Name, p.Branch, p.Company_Name, p.Package, p.Is_PPO
FROM V_PLACEMENT_DETAIL p
JOIN INTERNSHIP i
  ON i.Student_ID = p.Student_ID AND i.Company_ID = p.Company_ID
WHERE p.Joined = 'Yes'
ORDER BY p.Package DESC;
```

---

### Q133: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT Skill, COUNT(*) AS Students_With_Skill
FROM STUDENT_SKILL
GROUP BY Skill
ORDER BY Students_With_Skill DESC, Skill;
```

---

### Q134: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT ps.Skill, COUNT(*) AS Times_Selected_For
FROM PLACEMENT_SKILL ps
GROUP BY ps.Skill
ORDER BY Times_Selected_For DESC, ps.Skill;
```

---

### Q135: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT ps.Skill, COUNT(*) AS Students, ROUND(AVG(p.Package), 2) AS Avg_Package
FROM PLACEMENT_SKILL ps
JOIN PLACEMENT p ON p.Placement_ID = ps.Placement_ID
WHERE p.Joined = 'Yes'
GROUP BY ps.Skill
ORDER BY Avg_Package DESC;
```

---

### Q136: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Dropdown Distinct Filter Lookup`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT DISTINCT c.Company_Name, ps.Skill
FROM PLACEMENT_SKILL ps
JOIN PLACEMENT p ON p.Placement_ID = ps.Placement_ID
JOIN COMPANY c   ON c.Company_ID  = p.Company_ID
WHERE c.Company_Name = %s
ORDER BY ps.Skill;
```

---

### Q137: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT c.Company_Name, c.Company_Type,
       (SELECT COUNT(*) FROM INTERNSHIP i WHERE i.Company_ID = c.Company_ID) AS Interns_Taken,
       (SELECT COUNT(*) FROM PLACEMENT  p WHERE p.Company_ID = c.Company_ID) AS Offers_Made
FROM COMPANY c
WHERE EXISTS (SELECT 1 FROM INTERNSHIP i WHERE i.Company_ID = c.Company_ID)
  AND EXISTS (SELECT 1 FROM PLACEMENT  p WHERE p.Company_ID = c.Company_ID);
```

---

### Q138: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Pre-Insert Uniqueness Check`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

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

---

### Q139: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

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

---

### Q140: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

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

---

### Q141: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
WITH BranchTotals AS (
    SELECT
        s.Branch,
        COUNT(DISTINCT s.Student_ID) AS Total_Students,
        COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' THEN s.Student_ID END) AS Placed_Students,
        COUNT(p.Placement_ID) AS Total_Offers,
        ROUND(AVG(CASE WHEN p.Joined = 'Yes' THEN p.Package END), 2) AS Avg_Package,
        MAX(CASE WHEN p.Joined = 'Yes' THEN p.Package END) AS Highest_Package,
        MIN(CASE WHEN p.Joined = 'Yes' THEN p.Package END) AS Lowest_Package
    FROM STUDENT s
    LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
    GROUP BY s.Branch
),
BranchMedians AS (
    SELECT
        Branch,
        ROUND(AVG(Package), 2) AS Median_Package
    FROM (
        SELECT
            s.Branch,
            p.Package,
            ROW_NUMBER() OVER (PARTITION BY s.Branch ORDER BY p.Package ASC) AS row_num,
            COUNT(*) OVER (PARTITION BY s.Branch) AS total_count
        FROM PLACEMENT p
        JOIN STUDENT s ON p.Student_ID = s.Student_ID
        WHERE p.Joined = 'Yes'
    ) ranked
    WHERE row_num IN (FLOOR((total_count + 1) / 2), CEIL((total_count + 1) / 2))
    GROUP BY Branch
)
SELECT
    b.Branch,
    b.Total_Students,
    b.Placed_Students,
    (b.Total_Students - b.Placed_Students) AS Unplaced_Students,
    ROUND(COALESCE(100.0 * b.Placed_Students / NULLIF(b.Total_Students, 0), 0), 1) AS Placement_Rate,
    b.Total_Offers,
    COALESCE(b.Avg_Package, 0.00) AS Avg_Package,
    COALESCE(m.Median_Package, 0.00) AS Median_Package,
    COALESCE(b.Highest_Package, 0.00) AS Highest_Package,
    COALESCE(b.Lowest_Package, 0.00) AS Lowest_Package,
    DENSE_RANK() OVER (ORDER BY ROUND(COALESCE(100.0 * b.Placed_Students / NULLIF(b.Total_Students, 0), 0), 1) DESC, b.Avg_Package DESC) AS Performance_Rank
FROM BranchTotals b
LEFT JOIN BranchMedians m ON b.Branch = m.Branch
ORDER BY b.Branch ASC;
```

---

### Q142: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
WITH YearlyPlacements AS (
    SELECT
        p.Placement_Year,
        COUNT(p.Placement_ID) AS Total_Offers,
        COUNT(DISTINCT p.Student_ID) AS Total_Candidates_Offered,
        COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' THEN p.Student_ID END) AS Placed_Count,
        ROUND(AVG(p.Package), 2) AS Avg_Offered_Package,
        ROUND(AVG(CASE WHEN p.Joined = 'Yes' THEN p.Package END), 2) AS Avg_Accepted_Package,
        MAX(p.Package) AS Highest_Package,
        MIN(p.Package) AS Lowest_Package,
        ROUND(SUM(CASE WHEN p.Joined = 'Yes' THEN p.Package ELSE 0 END), 2) AS Total_Accepted_Volume
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

---

### Q143: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
WITH RankedByBranch AS (
    SELECT
        s.Branch,
        p.Package,
        ROW_NUMBER() OVER (PARTITION BY s.Branch ORDER BY p.Package ASC) AS row_num,
        COUNT(*) OVER (PARTITION BY s.Branch) AS total_count
    FROM PLACEMENT p
    JOIN STUDENT s ON p.Student_ID = s.Student_ID
    WHERE p.Joined = 'Yes'
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
    WHERE p.Joined = 'Yes'
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

---

### Q144: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

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
        COUNT(CASE WHEN p.Joined = 'Yes' THEN 1 END) AS Accepted_Offers,
        ROUND(AVG(p.Package), 2) AS Avg_Offered_Package,
        ROUND(AVG(CASE WHEN p.Joined = 'Yes' THEN p.Package END), 2) AS Avg_Accepted_Package,
        MAX(p.Package) AS Highest_Package,
        MIN(p.Package) AS Lowest_Package,
        ROUND(SUM(CASE WHEN p.Joined = 'Yes' THEN p.Package ELSE 0 END), 2) AS Total_Compensation_Committed
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

---

### Q145: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

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
        MAX(CASE WHEN p.Joined = 'Yes' THEN c.Company_Name END) AS Joined_Company,
        MAX(CASE WHEN p.Joined = 'Yes' THEN p.Package END) AS Joined_Package,
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

---

### Q146: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

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

---

### Q147: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

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
    LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID AND p.Joined = 'Yes'
    WHERE p.Placement_ID IS NULL
)
SELECT * FROM UnplacedStudents ORDER BY Branch, Branch_Priority_Rank;
```

---

### Q148: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

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
        CASE WHEN p.Joined = 'Yes' THEN 1 ELSE 0 END AS Is_Placed,
        CASE WHEN p.Joined = 'Yes' THEN p.Package END AS Placed_Package,
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

---

### Q149: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
WITH CompanyHiringStats AS (
    SELECT
        c.Company_ID,
        c.Company_Name,
        c.Company_Type,
        c.Industry,
        p.Placement_Year,
        COUNT(p.Placement_ID) AS Total_Offers_Extended,
        COUNT(CASE WHEN p.Offer_Status = 'Accepted' THEN 1 END) AS Accepted_Offers,
        COUNT(CASE WHEN p.Joined = 'Yes' THEN 1 END) AS Joined_Hires,
        ROUND(AVG(p.Package), 2) AS Avg_Package_Offered,
        ROUND(AVG(CASE WHEN p.Joined = 'Yes' THEN p.Package END), 2) AS Avg_Joined_Package,
        MAX(p.Package) AS Highest_Package
    FROM COMPANY c
    JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
    GROUP BY c.Company_ID, c.Company_Name, c.Company_Type, c.Industry, p.Placement_Year
)
SELECT
    chs.*,
    ROUND(COALESCE(100.0 * Joined_Hires / NULLIF(Total_Offers_Extended, 0), 0), 1) AS Conversion_Rate,
    DENSE_RANK() OVER (PARTITION BY Placement_Year ORDER BY Total_Offers_Extended DESC, Joined_Hires DESC) AS Year_Company_Rank
FROM CompanyHiringStats chs
ORDER BY Placement_Year DESC, Total_Offers_Extended DESC;
```

---

### Q150: `get_sql_report_limits`
- **Source File & Function:** `services/sql_report_service.py` -> `get_sql_report_limits`
- **Category:** `Reports`
- **Design Pattern:** `Aggregate Metric Calculation`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
WITH CohortStats AS (
    SELECT
        s.Branch,
        s.Batch_Year,
        COUNT(DISTINCT s.Student_ID) AS Total_Students,
        ROUND(AVG(s.CGPA), 2) AS Avg_CGPA,
        COUNT(DISTINCT CASE WHEN p.Joined = 'Yes' THEN s.Student_ID END) AS Placed_Count,
        COUNT(DISTINCT CASE WHEN i.Internship_No = 1 AND i.Internship_Type = 'Mandatory' THEN s.Student_ID END) AS I1_Compliant,
        COUNT(DISTINCT CASE WHEN i.Internship_No = 2 AND i.Internship_Type = 'Mandatory' THEN s.Student_ID END) AS I2_Compliant,
        ROUND(COALESCE(AVG(p.Package), 0), 2) AS Avg_Placement_Package,
        MAX(p.Package) AS Max_Package
    FROM STUDENT s
    LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
    LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
    GROUP BY s.Branch, s.Batch_Year
)
SELECT
    Branch,
    Batch_Year,
    Total_Students,
    Avg_CGPA,
    Placed_Count,
    ROUND(100.0 * Placed_Count / NULLIF(Total_Students, 0), 1) AS Placement_Rate,
    I1_Compliant,
    I2_Compliant,
    Avg_Placement_Package,
    Max_Package,
    LAG(Avg_CGPA) OVER (PARTITION BY Branch ORDER BY Batch_Year ASC) AS Prev_Batch_CGPA,
    ROUND(COALESCE(Avg_CGPA - LAG(Avg_CGPA) OVER (PARTITION BY Branch ORDER BY Batch_Year ASC), 0), 2) AS CGPA_YoY_Delta,
    DENSE_RANK() OVER (PARTITION BY Batch_Year ORDER BY Placed_Count DESC, Avg_Placement_Package DESC) AS Batch_Branch_Rank
FROM CohortStats
ORDER BY Batch_Year DESC, Batch_Branch_Rank ASC;
```

---

### Q151: `get_report_dynamic_options`
- **Source File & Function:** `services/sql_report_service.py` -> `get_report_dynamic_options`
- **Category:** `Reports`
- **Design Pattern:** `Dropdown Distinct Filter Lookup`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT DISTINCT Branch FROM STUDENT WHERE Branch IS NOT NULL AND Branch !=
```

---

### Q152: `get_report_dynamic_options`
- **Source File & Function:** `services/sql_report_service.py` -> `get_report_dynamic_options`
- **Category:** `Reports`
- **Design Pattern:** `Dropdown Distinct Filter Lookup`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT DISTINCT Batch_Year FROM STUDENT WHERE Batch_Year IS NOT NULL ORDER BY Batch_Year DESC
```

---

### Q153: `get_report_dynamic_options`
- **Source File & Function:** `services/sql_report_service.py` -> `get_report_dynamic_options`
- **Category:** `Reports`
- **Design Pattern:** `Dropdown Distinct Filter Lookup`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT DISTINCT Company_Name FROM COMPANY WHERE Company_Name IS NOT NULL AND Company_Name !=
```

---

### Q154: `get_report_dynamic_options`
- **Source File & Function:** `services/sql_report_service.py` -> `get_report_dynamic_options`
- **Category:** `Reports`
- **Design Pattern:** `Dropdown Distinct Filter Lookup`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT DISTINCT Roll_No FROM STUDENT WHERE Roll_No IS NOT NULL AND Roll_No !=
```

---

### Q155: `get_report_dynamic_options`
- **Source File & Function:** `services/sql_report_service.py` -> `get_report_dynamic_options`
- **Category:** `Reports`
- **Design Pattern:** `Dropdown Distinct Filter Lookup`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
SELECT DISTINCT Skill FROM STUDENT_SKILL WHERE Skill IS NOT NULL AND Skill !=
```

---

### Q156: `validate_custom_sql`
- **Source File & Function:** `services/sql_report_service.py` -> `validate_custom_sql`
- **Category:** `Reports`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Validates user-submitted SQL against strict security rules on the server.

    Safety rules enforced:
    1. Query cannot be empty.
    2. Prohibits comment syntax (-- , /* */, #) to prevent statement hiding.
    3. Exactly ONE statement allowed (semicolons inside statement prohibited).
    4. Must start with SELECT.
    5. Rejects INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, and administrative keywords.
    6. Automatically caps / sets row limit to 500.

    Returns the sanitized SQL ready for execution.
    Raises ValidationError if any rule is violated.
```

---

### Q157: `execute_custom_query`
- **Source File & Function:** `services/sql_report_service.py` -> `execute_custom_query`
- **Category:** `Reports`
- **Design Pattern:** `Complex Analytical / Reporting Query`
- **Core DBMS Concepts:** Parameterized prepared statement (`%s`), transactional integrity, clean relational access.

```sql
Executes an ad-hoc SQL query submitted by the user under strict isolation:

    1. Validates SQL through `validate_custom_sql`.
    2. Authenticates as the dedicated MySQL user `placement_readonly` (SELECT privilege only).
    3. Enforces session statement timeout `max_execution_time` from centralized configuration.
    4. Fetches at most `SQL_REPORT_MAX_ROWS` rows.
    5. Measures execution time in milliseconds.
    6. Formats all database errors into human-readable messages without server crash.
```

---

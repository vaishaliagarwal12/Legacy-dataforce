# Comprehensive DBMS Normalization Report: Canonical 7-Table Relational Schema

> [!IMPORTANT]
> **DBMS Viva Examination Guide**: This report provides an exhaustive, mathematically rigorous, and viva-ready normalization analysis of **all 7 tables** in the active MySQL database (`placement_internship_db`). It examines First Normal Form (1NF), Second Normal Form (2NF), Third Normal Form (3NF), and Boyce-Codd Normal Form (BCNF), candidate keys, functional dependencies, partial dependencies, transitive dependencies, ER relationships, and the deliberate curriculum denormalization in `INTERNSHIP`.

---

## Executive Normalization Summary Table (Canonical 7 Tables)

| # | Table Name | Primary Key | Candidate Keys | 1NF | 2NF | 3NF | BCNF | Normalization Status & Key Mechanism |
|---|---|---|---|:---:|:---:|:---:|:---:|---|
| 1 | **`STUDENT`** | `Student_ID` | 3 Key(s) | YES | YES | YES | **YES** | Clean BCNF master entity; all candidate keys are single attributes (no partial dependencies). |
| 2 | **`STUDENT_PHONE`** | `(Student_ID, Phone_No)` | 1 Key(s) | YES | YES | YES | **YES** | 1NF multi-valued attribute decomposition; composite all-key table. |
| 3 | **`STUDENT_SKILL`** | `(Student_ID, Skill)` | 1 Key(s) | YES | YES | YES | **YES** | 1NF multi-valued attribute decomposition; composite all-key table. |
| 4 | **`COMPANY`** | `Company_ID` | 2 Key(s) | YES | YES | YES | **YES** | Clean BCNF dimension table; `Company_ID` and `Company_Name` are unique. |
| 5 | **`PLACEMENT`** | `Placement_ID` | 1 Key(s) | YES | YES | YES | **YES** | Clean BCNF fact table; Offer_Status and Joined are independent facts. |
| 6 | **`PLACEMENT_SKILL`** | `(Placement_ID, Skill)` | 1 Key(s) | YES | YES | YES | **YES** | 1NF multi-valued attribute decomposition; composite all-key table. |
| 7 | **`INTERNSHIP`** | `(Student_ID, Internship_No)` | 2 Key(s) | **YES** | **NO** | **NO** | **NO** | **1NF (Deliberate Denormalization)**; partial dependency `Internship_No -> {Type, Credits, Report_Semester}`. |

> [!WARNING]
> **Honest Viva Disclosure**: We do **NOT** claim all tables are BCNF. Exactly **6 tables are in BCNF**, and **1 table (`INTERNSHIP`) is in 1NF** due to deliberate, controlled curriculum denormalization.

---

## Relational Views Summary (Derived & Virtual Operations)

| View Name | Underlying Tables | Purpose & Architectural Rationale | Normalization Benefit |
|---|---|---|---|
| **`V_PLACEMENT_DETAIL`** | `PLACEMENT`, `STUDENT`, `COMPANY` | Pre-joined virtual projection of student, company, and placement terms. | Zero stored physical redundancy; computes student full name dynamically using `CONCAT` with `COALESCE`. |
| **`V_INTERNSHIP_DETAIL`** | `INTERNSHIP`, `STUDENT`, `COMPANY` | Dynamically calculates `Duration_Months` on the fly using `ROUND(DATEDIFF(End_Date, Start_Date) / 30.44, 1)`. | **Enforces 3NF**: Prevents storing derived duration on disk, eliminating update anomalies if dates change. |

---

## Detailed Table-by-Table Normalization Breakdown

### 1. Table: `STUDENT`
**Functional Role:** Master Entity (Demographics & Academic Standing)

#### Columns & Data Types
| Column Name | Data Type | Constraint / Key Role | Nullability |
|---|---|---|---|
| `Student_ID` | `INT` | PK, AUTO_INCREMENT | NOT NULL |
| `Roll_No` | `VARCHAR(20)` | Candidate Key (UNIQUE) | NOT NULL |
| `First_Name` | `VARCHAR(50)` | Non-prime | NOT NULL |
| `Last_Name` | `VARCHAR(50)` | Non-prime | NULL |
| `Branch` | `VARCHAR(50)` | Non-prime | NOT NULL |
| `Batch_Year` | `INT` | Non-prime | NOT NULL |
| `Section` | `VARCHAR(5)` | Non-prime | NULL |
| `CGPA` | `DECIMAL(3,2)` | Non-prime (CHECK 0.00-10.00) | NOT NULL |
| `Backlogs` | `INT` | Non-prime (CHECK >= 0) | NOT NULL DEFAULT 0 |
| `Email` | `VARCHAR(100)` | Candidate Key (UNIQUE) | NOT NULL |
| `Resume_Link` | `VARCHAR(255)` | Non-prime | NULL |
| `Date_of_Birth` | `DATE` | Non-prime | NULL |
| `Gender` | `ENUM('Male','Female','Other')` | Non-prime | NULL |
| `Personal_Email`| `VARCHAR(100)` | Non-prime | NULL |

#### Candidate Keys & Functional Dependencies
- **Primary Key:** `Student_ID`
- **Candidate Keys:**
  - $CK_1 = \{	ext{Student\_ID}\}$ (Surrogate Primary Key)
  - $CK_2 = \{	ext{Roll\_No}\}$ (Natural Academic Identifier, UNIQUE)
  - $CK_3 = \{	ext{Email}\}$ (Institutional Contact Identifier, UNIQUE)
- **Functional Dependencies:**
  - $FD_1: 	ext{Student\_ID}
ightarrow \{	ext{Roll\_No}, 	ext{First\_Name}, 	ext{Last\_Name}, 	ext{Branch}, 	ext{Batch\_Year}, 	ext{Section}, 	ext{CGPA}, 	ext{Backlogs}, 	ext{Email}, \dots\}$
  - $FD_2: 	ext{Roll\_No}
ightarrow \{	ext{Student\_ID}, 	ext{First\_Name}, 	ext{Last\_Name}, 	ext{Branch}, 	ext{Batch\_Year}, 	ext{Section}, 	ext{CGPA}, 	ext{Backlogs}, 	ext{Email}, \dots\}$
  - $FD_3: 	ext{Email}
ightarrow \{	ext{Student\_ID}, 	ext{Roll\_No}, 	ext{First\_Name}, 	ext{Last\_Name}, 	ext{Branch}, 	ext{Batch\_Year}, \dots\}$
- **Prime Attributes:** `Student_ID`, `Roll_No`, `Email`
- **Non-Prime Attributes:** `First_Name`, `Last_Name`, `Branch`, `Batch_Year`, `Section`, `CGPA`, `Backlogs`, `Resume_Link`, `Date_of_Birth`, `Gender`, `Personal_Email`

#### Normal Form Determinations
- **1NF (Atomic Attributes):** **YES.** Every attribute contains atomic scalar values. Repeating groups (phones, skills) were decomposed into separate tables.
- **2NF (No Partial Dependencies):** **YES.** Every candidate key consists of a single attribute ($|	ext{CK}| = 1$). A partial dependency requires a proper subset of a candidate key; since no candidate key is composite, partial dependencies are mathematically impossible.
- **3NF (No Transitive Dependencies):** **YES.** There are no non-trivial functional dependencies between non-prime attributes (e.g., `Branch` does not determine `Section`, `CGPA` does not determine `Backlogs`). Every determinant is a candidate key.
- **BCNF (Every Determinant is a Superkey):** **YES.** For every non-trivial functional dependency $X
ightarrow Y$, the determinant $X$ is a superkey.

#### What to Say in the Viva
> *"The STUDENT table is in **Boyce-Codd Normal Form (BCNF)**. It possesses three candidate keys: Student_ID, Roll_No, and Email. Because each candidate key is a single attribute, partial functional dependencies are mathematically impossible, satisfying 2NF. Furthermore, all non-key attributes such as CGPA, Branch, and Backlogs depend directly and solely on these candidate keys with zero transitive dependencies between non-prime columns, fulfilling both 3NF and BCNF."*

---

### 2. Table: `STUDENT_PHONE`
**Functional Role:** Multi-Valued Attribute Decomposition (1NF Normalization)

#### Columns & Data Types
| Column Name | Data Type | Constraint / Key Role | Nullability |
|---|---|---|---|
| `Student_ID` | `INT` | PK (Composite), FK -> STUDENT(Student_ID) ON DELETE CASCADE | NOT NULL |
| `Phone_No` | `VARCHAR(15)` | PK (Composite) | NOT NULL |

#### Candidate Keys & Functional Dependencies
- **Primary Key:** `(Student_ID, Phone_No)`
- **Candidate Keys:** $CK_1 = \{	ext{Student\_ID}, 	ext{Phone\_No}\}$
- **Functional Dependencies:** None non-trivial (All attributes are prime).
- **Prime Attributes:** `Student_ID`, `Phone_No`
- **Non-Prime Attributes:** None (Empty set).

#### Normal Form Determinations
- **1NF:** **YES.** Decomposes multi-valued phone lists into separate rows.
- **2NF:** **YES.** 2NF applies only to non-prime attributes. Since there are zero non-prime attributes, partial dependencies cannot exist.
- **3NF & BCNF:** **YES.** In an all-key binary junction table with no non-prime attributes, 3NF and BCNF are vacuously satisfied.

#### What to Say in the Viva
> *"STUDENT_PHONE represents a classical 1NF decomposition of a multi-valued attribute. Rather than storing comma-separated phone numbers inside the STUDENT table—which would violate First Normal Form—we store each number as an individual row. The primary key is composite `(Student_ID, Phone_No)`. Because every attribute is part of the primary key and there are no non-prime attributes, the table trivially satisfies BCNF."*

---

### 3. Table: `STUDENT_SKILL`
**Functional Role:** Multi-Valued Attribute Decomposition (1NF Normalization)

#### Columns & Data Types
| Column Name | Data Type | Constraint / Key Role | Nullability |
|---|---|---|---|
| `Student_ID` | `INT` | PK (Composite), FK -> STUDENT(Student_ID) ON DELETE CASCADE | NOT NULL |
| `Skill` | `VARCHAR(50)` | PK (Composite) | NOT NULL |

#### Candidate Keys & Functional Dependencies
- **Primary Key:** `(Student_ID, Skill)`
- **Candidate Keys:** $CK_1 = \{	ext{Student\_ID}, 	ext{Skill}\}$
- **Prime Attributes:** `Student_ID`, `Skill`
- **Non-Prime Attributes:** None.
- **Normal Forms:** **1NF, 2NF, 3NF, BCNF (YES).** Identical to `STUDENT_PHONE`, this is an all-key decomposed table in full BCNF.

---

### 4. Table: `COMPANY`
**Functional Role:** Master Dimension Entity (Corporate Recruiters)

#### Columns & Data Types
| Column Name | Data Type | Constraint / Key Role | Nullability |
|---|---|---|---|
| `Company_ID` | `INT` | PK, AUTO_INCREMENT | NOT NULL |
| `Company_Name`| `VARCHAR(100)` | Candidate Key (UNIQUE) | NOT NULL |
| `Company_Type`| `ENUM('Product','Service','Startup','Other')` | Non-prime | NOT NULL |
| `Industry` | `VARCHAR(100)` | Non-prime | NOT NULL |
| `Location` | `VARCHAR(100)` | Non-prime | NULL |
| `Website` | `VARCHAR(255)` | Non-prime | NULL |

#### Candidate Keys & Functional Dependencies
- **Primary Key:** `Company_ID`
- **Candidate Keys:**
  - $CK_1 = \{	ext{Company\_ID}\}$
  - $CK_2 = \{	ext{Company\_Name}\}$
- **Functional Dependencies:**
  - $FD_1: 	ext{Company\_ID}
ightarrow \{	ext{Company\_Name}, 	ext{Company\_Type}, 	ext{Industry}, 	ext{Location}, 	ext{Website}\}$
  - $FD_2: 	ext{Company\_Name}
ightarrow \{	ext{Company\_ID}, 	ext{Company\_Type}, 	ext{Industry}, 	ext{Location}, 	ext{Website}\}$
- **Normal Forms:** **1NF, 2NF, 3NF, BCNF (YES).** All candidate keys are single attributes, so partial dependencies cannot exist. Non-prime attributes depend directly and solely on candidate keys.

---

### 5. Table: `PLACEMENT`
**Functional Role:** Transaction / Fact Entity (Job Offers & Recruiter Selections)

#### Columns & Data Types
| Column Name | Data Type | Constraint / Key Role | Nullability |
|---|---|---|---|
| `Placement_ID` | `INT` | PK, AUTO_INCREMENT | NOT NULL |
| `Student_ID` | `INT` | FK -> STUDENT(Student_ID) | NOT NULL |
| `Company_ID` | `INT` | FK -> COMPANY(Company_ID) | NOT NULL |
| `Role` | `VARCHAR(100)` | Non-prime | NOT NULL |
| `Package` | `DECIMAL(5,2)` | Non-prime (CHECK Package > 0) | NOT NULL |
| `Placement_Year`| `INT` | Non-prime | NOT NULL |
| `Placement_Type`| `ENUM('On-campus','Off-campus','Pooled')` | Non-prime | NOT NULL DEFAULT 'On-campus' |
| `Is_PPO` | `ENUM('Yes','No')` | Non-prime | NOT NULL DEFAULT 'No' |
| `Joined` | `ENUM('Yes','No')` | Non-prime | NOT NULL DEFAULT 'No' |
| `Offer_Status` | `ENUM('Offered','Accepted','Declined')`| Non-prime | NOT NULL DEFAULT 'Offered' |
| `Interview_Rounds`| `INT` | Non-prime | NULL DEFAULT 1 |
| `Joined_Student`| `INT` | GENERATED ALWAYS AS (CASE WHEN Joined = 'Yes' THEN Student_ID ELSE NULL END) STORED | NULL |

#### Candidate Keys & Normalization Analysis
- **Primary Key:** `Placement_ID`
- **Candidate Key:** $CK_1 = \{	ext{Placement\_ID}\}$
- **Unique Constraint:** `uq_one_joined_offer UNIQUE (Joined_Student)`
- **Check Constraint:** `chk_placement_joined_status CHECK (Joined = 'No' OR Offer_Status = 'Accepted')`
- **Why PLACEMENT is in BCNF:**
  - `Offer_Status` (candidate decision) and `Joined` (actual joining event) are **independent facts**. `Offer_Status` does not functionally determine `Joined` (an offer can be Accepted with `Joined = 'No'` while onboarding is pending).
  - The CHECK constraint `chk_placement_joined_status` simply forbids impossible real-world states (`Joined = 'Yes'` when `Offer_Status = 'Offered'`), but does not create a functional dependency.
  - Since the primary key is a single attribute (`Placement_ID`), partial dependencies cannot exist.
  - There are no transitive dependencies between non-prime attributes.
  - Therefore, `PLACEMENT` strictly satisfies **BCNF**.

#### What to Say in the Viva
> *"PLACEMENT is in **BCNF**. Its primary key is `Placement_ID`. The attributes `Offer_Status` and `Joined` represent independent operational facts—an offer may be accepted without the student having joined yet. The CHECK constraint `Joined = 'No' OR Offer_Status = 'Accepted'` simply enforces a business rule by disallowing invalid combinations; it does not introduce a functional dependency. Furthermore, single-joined offer enforcement is achieved via a stored generated column `Joined_Student` with a UNIQUE constraint, completely eliminating data anomalies while keeping the table in BCNF."*

---

### 6. Table: `PLACEMENT_SKILL`
**Functional Role:** Evaluated Technical Competencies per Job Offer

#### Columns & Data Types
| Column Name | Data Type | Constraint / Key Role | Nullability |
|---|---|---|---|
| `Placement_ID` | `INT` | PK (Composite), FK -> PLACEMENT(Placement_ID) ON DELETE CASCADE | NOT NULL |
| `Skill` | `VARCHAR(50)` | PK (Composite) | NOT NULL |

#### Candidate Keys & Functional Dependencies
- **Primary Key:** `(Placement_ID, Skill)`
- **Candidate Keys:** $CK_1 = \{	ext{Placement\_ID}, 	ext{Skill}\}$
- **Normal Forms:** **1NF, 2NF, 3NF, BCNF (YES).** All-key decomposed table with zero non-prime attributes.

---

### 7. Table: `INTERNSHIP`
**Functional Role:** Weak Entity (Academic Milestones & Industry Training)

#### Columns & Data Types
| Column Name | Data Type | Constraint / Key Role | Nullability |
|---|---|---|---|
| `Internship_ID` | `INT` | Surrogate Unique Key, AUTO_INCREMENT | NOT NULL |
| `Student_ID` | `INT` | PK (Composite), FK -> STUDENT(Student_ID) | NOT NULL |
| `Internship_No` | `TINYINT` | PK (Composite) | NOT NULL |
| `Company_ID` | `INT` | FK -> COMPANY(Company_ID) | NOT NULL |
| `Internship_Type`| `ENUM('Mandatory','Additional')` | Non-prime | NOT NULL |
| `Role` | `VARCHAR(100)` | Non-prime | NOT NULL |
| `Interview_Rounds`| `INT` | Non-prime | NULL DEFAULT 1 |
| `Stipend` | `DECIMAL(10,2)`| Non-prime | NULL DEFAULT 0.00 |
| `Start_Date` | `DATE` | Non-prime | NOT NULL |
| `End_Date` | `DATE` | Non-prime (CHECK End_Date >= Start_Date) | NOT NULL |
| `Credits` | `INT` | Non-prime | NULL |
| `Report_Semester`| `TINYINT` | Non-prime | NULL |
| `Report_Link` | `VARCHAR(255)` | Non-prime | NULL |
| `Report_Grade` | `VARCHAR(5)` | Non-prime | NULL |
| `Certificate_Link`| `VARCHAR(255)`| Non-prime | NULL |

#### Keys & Functional Dependencies
-**Composite Primary Key:** `(Student_ID, Internship_No)`
-**Surrogate Alternate Key:** `Internship_ID` (UNIQUE)
-**Functional Dependencies:**
  - $FD_1: (	ext{Student\_ID}, 	ext{Internship\_No})
ightarrow \{	ext{Company\_ID}, 	ext{Role}, 	ext{Stipend}, 	ext{Start\_Date}, 	ext{End\_Date}, \dots\}$
  - $FD_2: 	ext{Internship\_No}
ightarrow \{	ext{Internship\_Type}, 	ext{Credits}, 	ext{Report\_Semester}\}$ *(Curriculum Rule)*

#### Normal Form Analysis: Why INTERNSHIP is in 1NF
1. **1NF:** **YES.** All attributes store atomic scalar values.
2. **2NF Failure (Partial Functional Dependency):**
   - The primary key is composite: $\{	ext{Student\_ID}, 	ext{Internship\_No}\}$.
   - By university curriculum regulations, `Internship_No = 1` dictates `Internship_Type = 'Mandatory'`, `Credits = 4`, and `Report_Semester = 5`.
   - `Internship_No = 2` dictates `Internship_Type = 'Mandatory'`, `Credits = 4`, and `Report_Semester = 8` (done during 8th semester, report submitted after end of 8th semester).
   - Therefore, the functional dependency $	ext{Internship\_No}
ightarrow \{	ext{Internship\_Type}, 	ext{Credits}, 	ext{Report\_Semester}\}$ exists.
   - Because the determinant $\{	ext{Internship\_No}\}$ is a **proper subset** of the composite candidate key $\{	ext{Student\_ID}, 	ext{Internship\_No}\}$, this is a **Partial Functional Dependency**.
   - Second Normal Form requires that every non-prime attribute be fully functionally dependent on the whole candidate key.
   - Because partial dependencies exist, **`INTERNSHIP` mathematically fails 2NF and is in 1NF**.

#### How It Could Be Fixed (Theoretical Decomposition)
To achieve 2NF/3NF/BCNF theoretically, we would decompose `INTERNSHIP` into two tables:
1. `INTERNSHIP_REQUIREMENT(Internship_No, Internship_Type, Credits, Report_Semester)` where `Internship_No` is the Primary Key.
2. `INTERNSHIP(Student_ID, Internship_No, Company_ID, Role, Stipend, Start_Date, End_Date, ...)` where `Internship_No` is a Foreign Key referencing `INTERNSHIP_REQUIREMENT`.

#### Why We Did NOT Decompose It (Deliberate Engineering Decision)
> *"We intentionally chose not to create an 8th table for three vital reasons:
> 1. **Commitment to the 7-Table Relational Schema:** Our approved project ER diagram specifies exactly 7 tables. Adding an 8th table would violate our approved architectural boundary.
> 2. **Elimination of Join Overhead:** Keeping the curriculum attributes in `INTERNSHIP` eliminates the need for an extra table join on every single internship query.
> 3. **Historical Evaluation Snapshot:** Keeping credits and grades directly on the student's internship tuple preserves an immutable record of what the student earned.
>
> Most importantly, this denormalization is **100% safe from anomalies** because MySQL enforces the rule at the storage engine level using the table CHECK constraint:
> ```sql
> CONSTRAINT chk_internship_curriculum CHECK (
>     (Internship_No = 1 AND Internship_Type = 'Mandatory' AND Credits = 4 AND Report_Semester = 5) OR
>     (Internship_No = 2 AND Internship_Type = 'Mandatory' AND Credits = 4 AND Report_Semester = 8) OR
>     (Internship_No >= 3 AND Internship_Type = 'Additional')
> )
> ```
> Therefore, no inconsistent data can ever enter the database."*

#### What to Say in the Viva
> *"The INTERNSHIP table is in **1NF**. Because our primary key is composite `(Student_ID, Internship_No)`, and `Internship_No` alone determines `Internship_Type`, `Credits`, and `Report_Semester`, a partial functional dependency exists, so 2NF fails. We intentionally kept this as a **deliberate denormalization** to avoid an extra join and preserve historical snapshot integrity, while remaining strictly within our approved 7-table schema. We protect the database against all update and insertion anomalies using MySQL's `chk_internship_curriculum` constraint."*

---

## 10 Normalization Viva Questions & High-Scoring Answers

### Q1: What is the primary objective of database normalization?
**Answer:** The primary objective of normalization is to eliminate data redundancy, prevent insertion, update, and deletion anomalies, and ensure that data dependencies make logical sense by storing each fact in exactly one place.

### Q2: What are the conditions for a table to be in First Normal Form (1NF)?
**Answer:** A table is in 1NF if every attribute contains only atomic (indivisible) scalar values, there are no repeating groups or arrays, every column has a unique name, and there exists a primary key to uniquely identify each row.

### Q3: What is a partial functional dependency and which normal form forbids it?
**Answer:** A partial functional dependency occurs when a non-prime attribute depends on only a proper subset of a composite candidate key, rather than the entire composite key. Second Normal Form (2NF) forbids partial dependencies.

### Q4: What is a transitive dependency and which normal form forbids it?
**Answer:** A transitive dependency occurs when a non-prime attribute depends on another non-prime attribute ($X
ightarrow Y$ and $Y
ightarrow Z$, where $X$ is a candidate key but $Y$ is not). Third Normal Form (3NF) forbids transitive dependencies.

### Q5: How does Boyce-Codd Normal Form (BCNF) differ from Third Normal Form (3NF)?
**Answer:** In 3NF, for any non-trivial dependency $X
ightarrow Y$, $X$ must be a superkey OR $Y$ must be a prime attribute. BCNF eliminates this second relaxation: in BCNF, for *every* non-trivial dependency $X
ightarrow Y$, the determinant $X$ must strictly be a superkey.

### Q6: Why are STUDENT_PHONE, STUDENT_SKILL, and PLACEMENT_SKILL in BCNF?
**Answer:** Because they are composite all-key tables resulting from 1NF multi-valued attribute decompositions. Every column is part of the primary key, meaning there are zero non-prime attributes. With no non-prime attributes, partial and transitive dependencies cannot exist, satisfying BCNF.

### Q7: Why is the PLACEMENT table in BCNF despite having both Offer_Status and Joined?
**Answer:** Because `Offer_Status` (whether the student accepted or declined) and `Joined` (whether the student physically joined) are independent operational facts. One does not determine the other. The CHECK constraint `chk_placement_joined_status` merely prevents impossible combinations, but does not create a functional dependency.

### Q8: Why does the INTERNSHIP table fail Second Normal Form (2NF)?
**Answer:** Because the primary key is composite `(Student_ID, Internship_No)`, and the institutional curriculum rule dictates that `Internship_No` alone determines `Internship_Type`, `Credits`, and `Report_Semester`. Since a non-prime attribute depends on a part of the candidate key, it is a partial dependency, violating 2NF.

### Q9: What is deliberate (or controlled) denormalization, and when is it justified?
**Answer:** Deliberate denormalization is the intentional decision to leave or introduce controlled redundancy in a physical schema to optimize query performance, avoid expensive joins, or preserve historical audit snapshots, provided the data is protected against anomalies using CHECK constraints or triggers.

### Q10: How do views like V_INTERNSHIP_DETAIL help preserve 3NF in our database?
**Answer:** Instead of storing derived values like `Duration_Months` on disk (which would create a transitive dependency on `Start_Date` and `End_Date` violating 3NF), `V_INTERNSHIP_DETAIL` calculates the duration dynamically using `ROUND(DATEDIFF(End_Date, Start_Date) / 30.44, 1)`. This guarantees 3NF compliance on disk while offering query convenience to developers.

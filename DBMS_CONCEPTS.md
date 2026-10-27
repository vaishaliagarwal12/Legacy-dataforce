# Database Management Systems (DBMS) Concepts Guide

An academic and technical reference guide detailing foundational and advanced DBMS principles implemented in the **Campus Placement & Internship Management System**.

---

## 📌 Table of Contents

- [1. Database Normalization (1NF to BCNF)](#1-database-normalization-1nf-to-bcnf)
  - [1.1 Purpose of Normalization](#11-purpose-of-normalization)
  - [1.2 Unnormalized Form (UNF) & Anomalies](#12-unnormalized-form-unf--anomalies)
  - [1.3 First Normal Form (1NF)](#13-first-normal-form-1nf)
  - [1.4 Second Normal Form (2NF)](#14-second-normal-form-2nf)
  - [1.5 Third Normal Form (3NF)](#15-third-normal-form-3nf)
  - [1.6 Boyce-Codd Normal Form (BCNF)](#16-boyce-codd-normal-form-bcnf)
- [2. Relational Keys](#2-relational-keys)
  - [2.1 Super Key vs. Candidate Key](#21-super-key-vs-candidate-key)
  - [2.2 Primary Key, Alternate Key & Foreign Key](#22-primary-key-alternate-key--foreign-key)
  - [2.3 Composite Keys & Surrogate vs. Natural Keys](#23-composite-keys--surrogate-vs-natural-keys)
- [3. SQL Joins & Multi-Table Query Optimization](#3-sql-joins--multi-table-query-optimization)
  - [3.1 INNER JOIN](#31-inner-join)
  - [3.2 LEFT OUTER JOIN](#32-left-outer-join)
  - [3.3 RIGHT OUTER JOIN & FULL OUTER JOIN Emulation](#33-right-outer-join--full-outer-join-emulation)
  - [3.4 CROSS JOIN & Self Joins](#34-cross-join--self-joins)
  - [3.5 Analytical CTEs & Window Functions](#35-analytical-ctes--window-functions)
- [4. Transactions & Concurrency Control (ACID)](#4-transactions--concurrency-control-acid)
  - [4.1 ACID Properties in Campus Placement](#41-acid-properties-in-campus-placement)
  - [4.2 Concurrency Anomalies & Isolation Levels](#42-concurrency-anomalies--isolation-levels)
  - [4.3 Two-Phase Locking & MVCC](#43-two-phase-locking--mvcc)
- [5. Database Indexing & Query Performance](#5-database-indexing--query-performance)
  - [5.1 B-Tree Index Internals](#51-b-tree-index-internals)
  - [5.2 Clustered vs. Secondary Indexes](#52-clustered-vs-secondary-indexes)
  - [5.3 Composite Indexes & The Leftmost Prefix Rule](#53-composite-indexes--the-leftmost-prefix-rule)
  - [5.4 Execution Plan Analysis (`EXPLAIN`)](#54-execution-plan-analysis-explain)

---

## 1. Database Normalization (1NF to BCNF)

### 1.1 Purpose of Normalization
Normalization is the systematic process of organizing relational database schemas to:
1. **Minimize Data Redundancy**: Eliminate duplicate data storage across rows and tables.
2. **Prevent Modification Anomalies**:
   - **Insertion Anomaly**: Inability to record certain facts without adding unrelated dummy records.
   - **Update Anomaly**: Modifying data in one place while leaving obsolete copies elsewhere, causing inconsistency.
   - **Deletion Anomaly**: Inadvertently losing vital historical data when deleting an unrelated attribute.
3. **Enforce Referential Integrity**: Ensure functional dependencies reflect valid domain relationships.

---

### 1.2 Unnormalized Form (UNF) & Anomalies

Suppose an institution maintained an unnormalized single flat table `STUDENT_PLACEMENT_RECORD`:

| Roll_No | Student_Name | Phone_Numbers | Skills | Company_Name | Company_Location | Drive_Date | Offer_Package |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| CS202001 | Aarav Sharma | 9876543201, 9876543210 | Python, Java | Google India | Bengaluru | 2024-01-15 | 32.50 LPA |
| CS202002 | Diya Patel | 9876543202 | C++, AWS | Google India | Bengaluru | 2024-01-15 | 28.00 LPA |

**Critical Anomalies in this Unnormalized Design**:
- **Insertion Anomaly**: If a new company registers for a recruitment drive, but has not yet placed any student, we cannot insert the company without generating dummy student records (`Roll_No = NULL` would violate entity integrity).
- **Update Anomaly**: If Google moves its campus recruitment office from Bengaluru to Hyderabad, we must update hundreds of rows. Missing a single row produces conflicting locations for the same corporate partner.
- **Deletion Anomaly**: If Diya Patel withdraws her registration, deleting her record deletes all institutional history of the 28.00 LPA offer and role specifications.

---

### 1.3 First Normal Form (1NF)

> **Definition**: A relation is in 1NF if and only if:
> 1. Every column contains only atomic (indivisible) values.
> 2. There are no repeating groups or multivalued arrays.
> 3. Each row is uniquely identifiable by a primary key.

#### How This Project Implements 1NF:
1. **Name Decomposition**: Composite names are decomposed into atomic attributes `First_Name` and `Last_Name` in `STUDENT`.
2. **Multivalued Phone Decomposition**: Rather than storing comma-separated strings (`"9876543201, 9876543210"`), contact numbers are decomposed into the dedicated relation:
   ```sql
   CREATE TABLE STUDENT_PHONE (
       Student_ID INT NOT NULL,
       Phone_No   VARCHAR(20) NOT NULL,
       PRIMARY KEY (Student_ID, Phone_No),
       FOREIGN KEY (Student_ID) REFERENCES STUDENT(Student_ID) ON DELETE CASCADE
   );
   ```
3. **Multivalued Skills Decomposition**: Technical competencies are decomposed into `STUDENT_SKILL` and `PLACEMENT_SKILL` with composite primary keys `(Student_ID, Skill)` and `(Placement_ID, Skill)`.

---

### 1.4 Second Normal Form (2NF)

> **Definition**: A relation is in 2NF if:
> 1. It is in First Normal Form (1NF).
> 2. No non-prime attribute is **partially functionally dependent** on any candidate key. Every non-prime attribute must depend on the **entire** candidate key.

#### Project Decomposition Proof:
Consider course enrollments. In an un-normalized intersection:
- **Composite Primary Key**: `(Student_ID, Course_ID)`
- **Functional Dependencies**:
  - `(Student_ID, Course_ID) -> Grade, Enrollment_Year` (Full dependency)
  - `Course_ID -> Course_Name, Department, Semester, Credits` (Partial dependency on a subset of the candidate key!)

If `Course_Name` and `Credits` were stored in the enrollment table, modifying course credits would require updating thousands of student enrollment records.

**2NF Resolution in Our Schema**:
- Decomposed into `COURSE(Course_ID, Course_Name, Department, Semester, Credits, Course_Type)`.
- The bridge table `STUDENT_COURSE(Student_ID, Course_ID, Enrollment_Year, Grade)` contains **only** attributes that depend on the full composite key `(Student_ID, Course_ID)`.

---

### 1.5 Third Normal Form (3NF)

> **Definition**: A relation is in 3NF if:
> 1. It is in Second Normal Form (2NF).
> 2. There are no **transitive functional dependencies** between non-prime attributes ($X \rightarrow Y$ and $Y \rightarrow Z$, where $Z$ is non-prime and $Y$ is not a candidate key).

#### Project Decomposition Proof:
Consider student placement offers:
- If `PLACEMENT` stored: `(Placement_ID, Student_ID, Company_ID, Company_Name, Company_Location, Package)`
- **Dependencies**:
  - `Placement_ID -> Company_ID` (Primary Key dependency)
  - `Company_ID -> Company_Name, Company_Location` (Non-prime transitive dependency!)
  - Therefore: `Placement_ID -> Company_Name` is a **transitive dependency**.

If Google relocated, every placement row referencing Google would need updating.

**3NF Resolution in Our Schema**:
- Decoupled into `COMPANY(Company_ID, Company_Name, Industry, Location, Website)` where `Company_ID` is the primary key.
- `PLACEMENT` references `Company_ID` as a foreign key. Non-prime attributes in `PLACEMENT` (`Package`, `Placement_Year`, `Offer_Status`) depend strictly and directly on `Placement_ID`.

---

### 1.6 Boyce-Codd Normal Form (BCNF)

> **Definition**: A relation is in BCNF (a stricter variant of 3NF) if and only if for every non-trivial functional dependency $X \rightarrow Y$, the determinant $X$ is a **superkey**.

#### Project Implementation in `COURSE`:
In `COURSE(Course_ID, University_ID, Course_Name, Department, Semester, Credits, Course_Type)`:
- Candidate Key 1: `Course_ID`
- Candidate Key 2: `(University_ID, Course_Name, Semester)`
- Functional Dependencies:
  - `Course_ID -> University_ID, Course_Name, Department, Semester, Credits, Course_Type` ($Course_ID$ is a candidate key / superkey).
  - `(University_ID, Course_Name, Semester) -> Course_ID, Department, Credits, Course_Type` ($University\_ID, Course\_Name, Semester$ is a candidate key / superkey).

Because every determinant in `COURSE` is a superkey, the table satisfies **BCNF**.

---

## 2. Relational Keys

### 2.1 Super Key vs. Candidate Key

- **Super Key**: Any set of attributes within a table that can uniquely identify each row. A table can have multiple super keys, some containing redundant attributes (e.g., `{Roll_No}`, `{Roll_No, First_Name}`, `{Roll_No, Email}`).
- **Candidate Key**: A **minimal super key** with no extraneous attributes. Removing any attribute from a candidate key destroys its uniqueness property.

#### Candidate Keys in `STUDENT`:
1. `Student_ID` (Surrogate Integer Key)
2. `Roll_No` (Natural Academic Key, e.g., `CS202001`)
3. `Email` (Institutional Communication Key, e.g., `aarav.sharma@fictional.edu`)

---

### 2.2 Primary Key, Alternate Key & Foreign Key

- **Primary Key (PK)**: The specific candidate key chosen by the database architect as the principal row identifier. It is indexed via a clustered index and cannot contain `NULL` values.
  - Example: `STUDENT.Student_ID`
- **Alternate Key (AK)**: Candidate keys that were not chosen as the primary key. In MySQL, alternate keys are enforced using `UNIQUE` constraints.
  - Example: `Roll_No VARCHAR(20) NOT NULL UNIQUE`
- **Foreign Key (FK)**: An attribute or collection of attributes in a referencing (child) table that matches the candidate key of a referenced (parent) table, enforcing referential integrity.
  - Example: `PLACEMENT.Student_ID REFERENCES STUDENT(Student_ID)`

---

### 2.3 Composite Keys & Surrogate vs. Natural Keys

#### Composite Key
A primary key consisting of two or more attributes:
- `STUDENT_PHONE`: `PRIMARY KEY (Student_ID, Phone_No)`
- `STUDENT_COURSE`: `PRIMARY KEY (Student_ID, Course_ID)`
- `PLACEMENT_SKILL`: `PRIMARY KEY (Placement_ID, Skill)`

#### Surrogate Key vs. Natural Key Trade-Offs

| Dimension | Surrogate Key (`Student_ID INT AUTO_INCREMENT`) | Natural Key (`Roll_No VARCHAR(20)`) |
| :--- | :--- | :--- |
| **Storage Efficiency** | Highly compact (4-byte integer in B-Tree index). | Larger (20-byte string). Foreign keys across 8 child tables waste space. |
| **Join Performance** | CPU hardware operates natively on 32-bit integers; fastest join execution. | String comparisons are slower and character-set dependent. |
| **Domain Stability** | Immutable. Never changes regardless of university policy. | Mutable. If an institution restructures student roll numbering (e.g., branch transfers), updating cascading natural FKs is expensive. |
| **Human Readability** | Low (internal numerical identifier). | High (students and faculty identify by Roll Number). |

**Our Architecture**: We implement **Surrogate Primary Keys** for internal joins and B-tree efficiency, while placing **Unique Constraints on Natural Keys** (`Roll_No`, `Email`, `Company_Name`) for user queries.

---

## 3. SQL Joins & Multi-Table Query Optimization

### 3.1 INNER JOIN
Retrieves records that have matching values in both tables.

```sql
-- Query: Retrieve all placement offers with student roll numbers, names, and recruiting companies
SELECT 
    s.Roll_No,
    CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Student_Name,
    s.Branch,
    c.Company_Name,
    p.Role,
    p.Package,
    p.Offer_Status
FROM PLACEMENT p
INNER JOIN STUDENT s ON p.Student_ID = s.Student_ID
INNER JOIN COMPANY c ON p.Company_ID = c.Company_ID
WHERE p.Offer_Status = 'Accepted'
ORDER BY p.Package DESC;
```

---

### 3.2 LEFT OUTER JOIN
Retrieves all records from the left table, and matching records from the right table. Unmatched right-table columns return `NULL`.

```sql
-- Query: Find all active students and their placement status (identifies unplaced students)
SELECT 
    s.Roll_No,
    s.First_Name,
    s.Branch,
    s.CGPA,
    c.Company_Name,
    p.Package,
    COALESCE(p.Offer_Status, 'Unplaced') AS Status
FROM STUDENT s
LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID AND p.Offer_Status IN ('Accepted', 'Joined')
LEFT JOIN COMPANY c ON p.Company_ID = c.Company_ID
ORDER BY s.Branch, s.Roll_No;
```

---

### 3.3 RIGHT OUTER JOIN & FULL OUTER JOIN Emulation

- **RIGHT OUTER JOIN**: Returns all records from the right table, and matching records from the left table.
- **FULL OUTER JOIN**: Returns all records when there is a match in either left or right table. Standard MySQL 8.0 does not have a native `FULL OUTER JOIN` keyword, but it is emulated using `UNION`:

```sql
-- Full Outer Join Emulation: All students and all companies, matched on placement offers
SELECT s.Roll_No, s.First_Name, c.Company_Name, p.Package
FROM STUDENT s
LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
LEFT JOIN COMPANY c ON p.Company_ID = c.Company_ID

UNION

SELECT s.Roll_No, s.First_Name, c.Company_Name, p.Package
FROM COMPANY c
LEFT JOIN PLACEMENT p ON c.Company_ID = p.Company_ID
LEFT JOIN STUDENT s ON p.Student_ID = s.Student_ID;
```

---

### 3.4 CROSS JOIN & Self Joins

- **CROSS JOIN**: Produces the Cartesian product ($M \times N$) of two tables. Useful for generating hypothetical candidate-company interview pairings.
- **Self Join**: Joins a table to itself.
  ```sql
  -- Find pairs of students in the same branch who achieved the exact same CGPA
  SELECT 
      s1.Roll_No AS Student_A,
      s2.Roll_No AS Student_B,
      s1.Branch,
      s1.CGPA
  FROM STUDENT s1
  JOIN STUDENT s2 ON s1.Branch = s2.Branch 
                 AND s1.CGPA = s2.CGPA 
                 AND s1.Student_ID < s2.Student_ID;
  ```

---

### 3.5 Analytical CTEs & Window Functions

Used in Phase 9 for accreditation reporting:

```sql
-- Window Function: Rank top placement packages per engineering branch using DENSE_RANK()
WITH BranchPlacementStats AS (
    SELECT 
        s.Roll_No,
        CONCAT(s.First_Name, ' ', COALESCE(s.Last_Name, '')) AS Student_Name,
        s.Branch,
        c.Company_Name,
        p.Package,
        DENSE_RANK() OVER (
            PARTITION BY s.Branch 
            ORDER BY p.Package DESC
        ) AS Branch_Package_Rank,
        AVG(p.Package) OVER (
            PARTITION BY s.Branch
        ) AS Branch_Avg_Package
    FROM PLACEMENT p
    JOIN STUDENT s ON p.Student_ID = s.Student_ID
    JOIN COMPANY c ON p.Company_ID = c.Company_ID
    WHERE p.Offer_Status IN ('Accepted', 'Joined')
)
SELECT * FROM BranchPlacementStats WHERE Branch_Package_Rank <= 3;
```

---

## 4. Transactions & Concurrency Control (ACID)

### 4.1 ACID Properties in Campus Placement

```
                                  A C I D
   +-------------------------------------------------------------------------+
   | A - ATOMICITY   | Offer + evaluated skills committed together or rolled |
   |                 | back completely if any failure occurs.                |
   +-------------------------------------------------------------------------+
   | C - CONSISTENCY | Invariants preserved: no negative packages, 0-10 CGPA,|
   |                 | single accepted offer rule strictly enforced.         |
   +-------------------------------------------------------------------------+
   | I - ISOLATION   | Concurrent offer acceptance by different students     |
   |                 | does not produce race conditions or phantom offers.   |
   +-------------------------------------------------------------------------+
   | D - DURABILITY  | Committed placement decisions survive sudden server   |
   |                 | crashes via InnoDB Write-Ahead Logging (WAL).         |
   +-------------------------------------------------------------------------+
```

#### Code Implementation in `db/connection.py`:
```python
@contextmanager
def get_cursor(commit: bool = False):
    with get_connection() as connection:
        cursor = connection.cursor()
        try:
            yield cursor
            if commit:
                connection.commit()  # Atomicity & Durability
        except Exception as exc:
            if commit:
                connection.rollback()  # Rollback preserves Consistency
            raise exc
        finally:
            cursor.close()
```

---

### 4.2 Concurrency Anomalies & Isolation Levels

1. **Dirty Read (Read Uncommitted)**: Transaction $T_2$ reads an offer accepted by $T_1$ before $T_1$ commits. If $T_1$ rolls back, $T_2$ acted on false data.
2. **Non-Repeatable Read (Read Committed)**: Transaction $T_1$ reads student CGPA as `8.50`. $T_2$ updates it to `8.75` and commits. $T_1$ re-reads and gets a different value.
3. **Phantom Read (Repeatable Read)**: Transaction $T_1$ queries students with `Package > 20 LPA` and gets 5 rows. $T_2$ inserts a new 25 LPA offer. $T_1$ re-runs the range query and sees 6 rows.

#### SQL Standard Isolation Levels Matrix:

| Isolation Level | Dirty Reads | Non-Repeatable Reads | Phantom Reads | Engine Mechanism |
| :--- | :---: | :---: | :---: | :--- |
| **Read Uncommitted** | Possible | Possible | Possible | No read locks. |
| **Read Committed** | Prevented | Possible | Possible | Read locks released immediately; uses MVCC statement snapshot. |
| **Repeatable Read (MySQL Default)** | Prevented | Prevented | Prevented* | InnoDB uses Next-Key Locking & Transaction Snapshot MVCC. |
| **Serializable** | Prevented | Prevented | Prevented | Strict 2-Phase Locking (2PL) on all reads and writes. |

*Note: In MySQL InnoDB, Repeatable Read prevents phantom reads for consistent non-locking reads via MVCC snapshots and for locking reads via Gap Locks / Next-Key Locks.*

---

### 4.3 Two-Phase Locking & MVCC

- **Multi-Version Concurrency Control (MVCC)**: InnoDB associates two hidden fields with every row: `DB_TRX_ID` (transaction ID that created/modified the row) and `DB_ROLL_PTR` (pointer to the undo log record). Readers do not block writers, and writers do not block readers.
- **Pessimistic Locking for the Single Accepted Offer Rule**:
  ```sql
  -- Concurrency-safe acceptance transaction
  START TRANSACTION;
  
  -- Lock student's placement rows against concurrent modification
  SELECT Placement_ID, Offer_Status 
  FROM PLACEMENT 
  WHERE Student_ID = 5 AND Offer_Status IN ('Accepted', 'Joined')
  FOR UPDATE;
  
  -- If none found, accept offer 12
  UPDATE PLACEMENT SET Offer_Status = 'Accepted' WHERE Placement_ID = 12;
  
  COMMIT;
  ```

---

## 5. Database Indexing & Query Performance

### 5.1 B-Tree Index Internals

MySQL InnoDB stores all indexes as **B+Trees** (Balanced Search Trees):
- **Logarithmic Time Complexity**: Searching, inserting, and deleting records operates in $O(\log N)$ disk I/O operations rather than $O(N)$ full table scans (`ALL`).
- **Leaf Node Linking**: All leaf nodes are doubly linked sequentially on disk. Range scans (e.g., `WHERE Package BETWEEN 10.00 AND 20.00`) locate the start key in $O(\log N)$ time and follow sibling pointers across data pages with zero random disk head seeks.

---

### 5.2 Clustered vs. Secondary Indexes

```
  CLUSTERED INDEX (Primary Key)              SECONDARY INDEX (idx_student_roll)
+------------------------------------+     +------------------------------------+
| Root -> Internal -> Leaf Data Page |     | Root -> Internal -> Leaf Index     |
| [PK=1] -> Complete Student Row     |     | ['CS202001'] -> Points to [PK=1]   |
| [PK=2] -> Complete Student Row     |     | ['CS202002'] -> Points to [PK=2]   |
+------------------------------------+     +------------------------------------+
```

1. **Clustered Index**:
   - The table data **is** the index. In InnoDB, the primary key dictates the physical arrangement of table rows on disk.
   - Primary key lookups require **1 index traversal** to retrieve all row attributes.
2. **Secondary Index**:
   - Leaf nodes do **not** store row data; they store the indexed column value and the corresponding primary key value.
   - A secondary lookup performs an index lookup, then a **Bookmark Lookup** into the clustered index to fetch additional row columns (unless the index is a *Covering Index*).

---

### 5.3 Composite Indexes & The Leftmost Prefix Rule

In `init_mysql.py`:
```sql
CREATE INDEX idx_student_branch_batch ON STUDENT(Branch, Batch_Year);
```

#### The Leftmost Prefix Rule:
A composite index on `(A, B)` can accelerate queries filtering on:
- `WHERE A = ?` (Matches leftmost prefix)
- `WHERE A = ? AND B = ?` (Matches full index)
- `WHERE A = ? ORDER BY B` (Accelerates sorting without filesort)

**Query That CANNOT Use the Index**:
- `WHERE Batch_Year = 2024` (Omits column `A`, the leftmost prefix; causes a full table scan `type: ALL`).

---

### 5.4 Execution Plan Analysis (`EXPLAIN`)

Running `EXPLAIN` against placement filtering queries:

```sql
EXPLAIN SELECT p.Placement_ID, p.Package, s.Roll_No 
FROM PLACEMENT p
JOIN STUDENT s ON p.Student_ID = s.Student_ID
WHERE p.Placement_Year = 2024 AND p.Offer_Status = 'Accepted';
```

#### Key `EXPLAIN` Output Columns:
- **`type`**: Access method. Best to worst: `system` > `const` > `eq_ref` > `ref` > `range` > `index` > `ALL` (Full Table Scan).
- **`possible_keys`**: Indexes evaluated by the query optimizer.
- **`key`**: The specific index selected (e.g., `idx_placement_status`).
- **`rows`**: Estimated number of rows scanned by the storage engine.
- **`Extra`**:
  - `Using index`: **Covering index** satisfied entirely in RAM without bookmark lookups.
  - `Using where`: Filter evaluated post-fetch.
  - `Using filesort`: Database had to perform an external sort; indicates a missing composite index.

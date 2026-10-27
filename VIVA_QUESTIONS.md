# Top 10 Viva Voce / Professor Questions & Answers
## Campus Placement & Internship Management System

This document prepares you for project defense and viva voce examinations by providing the **top 10 questions professors are most likely to ask**, accompanied by **concise, authoritative, and technically rigorous answers**.

---

### Question 1: "Why did you create separate tables for student phone numbers and skills instead of storing them as comma-separated values or JSON in the Student table?"

**Short Answer**:
> *"Storing multiple contact numbers or skills in a single column violates **First Normal Form (1NF)**, which strictly mandates atomic values. Storing comma-separated strings makes it impossible to enforce uniqueness (e.g., preventing duplicate phone numbers), prevents foreign key referential integrity, and destroys indexing efficiency—requiring expensive full-table text scans (`LIKE '%Python%'`) instead of $O(\log N)$ B-Tree index lookups.*
>
> *By decomposing these multivalued attributes into `STUDENT_PHONE(Student_ID, Phone_No)` and `STUDENT_SKILL(Student_ID, Skill)` with composite primary keys, each attribute remains atomic, fully indexable, and automatically cleaned up via `ON DELETE CASCADE`."*

---

### Question 2: "How does the system enforce the 'One Accepted Offer' rule while still allowing students to receive multiple offers?"

**Short Answer**:
> *"Our architecture cleanly decouples **offer receipt** from **offer acceptance**:*
> 1. *Students can receive and hold multiple distinct offers in `'Offered'` status across different companies and opportunities without violation.*
> 2. *However, institutional policy dictates that a student can have **at most one** offer in `'Accepted'` or `'Joined'` status.*
> 3. *During any status transition to `'Accepted'` or `'Joined'`, our service layer initiates a database check verifying that no other offer for that `Student_ID` is currently in `'Accepted'` or `'Joined'` status. If an existing accepted offer is found, the transaction is rejected with **HTTP 409 Conflict**.*
> 4. *The student must explicitly decline their active accepted offer before accepting another."*

---

### Question 3: "Why did you specify `ON DELETE RESTRICT` for Company, but `ON DELETE CASCADE` for Student child tables?"

**Short Answer**:
> *"Referential actions are designed around business domain semantics:*
> - *`ON DELETE CASCADE` is applied to dependent student attributes (`STUDENT_PHONE`, `STUDENT_SKILL`, `STUDENT_PROFILE`, `RESUME`) because these records are dependent child entities that have zero meaning once a student record is removed.*
> - *`ON DELETE RESTRICT` is applied to `COMPANY` because deleting a recruiting partner would corrupt critical institutional audit trails, alumni records, and accreditation placement statistics. If a company has registered drives, placement offers, or hired interns, MySQL error `1451` strictly prevents deletion."*

---

### Question 4: "What Normal Form is your database in, and can you formally prove it?"

**Short Answer**:
> *"The database satisfies **Boyce-Codd Normal Form (BCNF)** and **Third Normal Form (3NF)**:*
> - **1NF**: All column values are atomic; no repeating groups (decomposed phones and skills).
> - **2NF**: It is in 1NF and contains zero partial dependencies on composite keys. In `STUDENT_COURSE(Student_ID, Course_ID)`, course catalog attributes (`Course_Name`, `Credits`) are isolated into `COURSE`, leaving only attributes that depend on the full composite key (`Grade`).
> - **3NF**: It is in 2NF and contains zero transitive dependencies. In `PLACEMENT`, company attributes (`Company_Name`, `Location`) are not stored directly, eliminating `Placement_ID -> Company_ID -> Company_Name`.
> - **BCNF**: In every non-trivial functional dependency $X \rightarrow Y$, determinant $X$ is a superkey (e.g., candidate keys in `COURSE` and `STUDENT`)."*

---

### Question 5: "What is the difference between a Surrogate Key and a Natural Key, and why did you use both?"

**Short Answer**:
> *- A **Natural Key** is a business attribute that already exists in the real world (e.g., `Roll_No` like `CS202001`, or `Email`).*
> - *A **Surrogate Key** is a system-generated unique integer (e.g., `Student_ID INT AUTO_INCREMENT`).*
>
> *We intentionally use both: **Surrogate Keys** serve as primary keys because 4-byte integers maximize B-Tree node capacity and execute joins significantly faster than variable-length strings. Simultaneously, we enforce `UNIQUE` constraints on **Natural Keys** (`Roll_No`, `Email`, `Company_Name`) to maintain real-world institutional uniqueness and data integrity."*

---

### Question 6: "How do your transactions maintain ACID properties, especially during simultaneous offer updates?"

**Short Answer**:
> *- **Atomicity & Consistency**: Implemented via Python context managers `get_cursor(commit=True)`. Operations that write to multiple tables (e.g., creating a placement and inserting evaluated skills into `PLACEMENT_SKILL`) execute inside a single transaction. If inserting skills fails, the placement is automatically rolled back.*
> - **Isolation**: Managed by MySQL InnoDB's default **Repeatable Read** isolation level using Multi-Version Concurrency Control (MVCC) and Row-Level Next-Key Locks. This prevents dirty reads, non-repeatable reads, and phantom records.*
> - **Durability**: Committed data is written to disk using InnoDB's Write-Ahead Log (WAL / redo log), ensuring survival across sudden server restarts."*

---

### Question 7: "What is the Leftmost Prefix Rule in composite indexing, and where is it applied?"

**Short Answer**:
> *"When a composite B-Tree index is created on multiple columns `(A, B)`—such as `idx_student_branch_batch (Branch, Batch_Year)`—the MySQL query optimizer can only use the index if the query's `WHERE` clause filters on the **leftmost column (`A`)**.*
> - *A query on `WHERE Branch = 'CSE'` or `WHERE Branch = 'CSE' AND Batch_Year = 2024` leverages the index efficiently.*
> - *However, a query on `WHERE Batch_Year = 2024` alone cannot use the index and causes a full table scan (`type: ALL`), because the B-Tree is ordered primarily by `Branch` and only secondarily by `Batch_Year`."*

---

### Question 8: "Where did you use an INNER JOIN versus a LEFT OUTER JOIN in your project, and why?"

**Short Answer**:
> *- **INNER JOIN**: Used when records in both tables must exist. For example, when generating the active placement report (`PLACEMENT` joined with `STUDENT` and `COMPANY`), we only want offers where both the student and company exist.*
> - **LEFT OUTER JOIN**: Used when we must preserve records from the primary table even when no related child record exists. For example, when listing all students and their placement status, a `LEFT JOIN` on `PLACEMENT` returns all students, showing placed students with their package and unplaced students with `NULL`.*
> - *Similarly, off-campus placement offers have no associated drive (`Opportunity_ID IS NULL`), so `LEFT JOIN OPPORTUNITY` is required to display them without data omission."*

---

### Question 9: "What constitutes a Weak Entity in your schema, and how is it identified?"

**Short Answer**:
> *"A Weak Entity is an entity that cannot be uniquely identified by its own attributes alone and relies on an identifying relationship with a parent owner entity.*
>
> *In our schema, **`INTERNSHIP`** and **`SELECTION_PROCESS`** are weak entities:*
> 1. *`INTERNSHIP` is identified by the composite candidate key `(Student_ID, Internship_No)`. An 'Internship 1' has no independent meaning without the student who completed it.*
> 2. *`SELECTION_PROCESS` is identified by `(Opportunity_ID, Round_Number)`. 'Round 2' has no independent existence without the recruitment opportunity conducting it.*
>
> *Both enforce `ON DELETE CASCADE` from their identifying parents."*

---

### Question 10: "How does the system verify whether a student satisfies the prerequisite SGPA for a Mandatory Summer Internship?"

**Short Answer**:
> *"The system uses a dynamic relational query joining `INTERNSHIP`, `INTERNSHIP_REQUIREMENT`, and `SEMESTER_RESULT`:*
> 1. *`INTERNSHIP_REQUIREMENT` defines that Mandatory Summer Internship 1 requires completed results for Semester 4 (`Required_Result_Semester = 4`).*
> 2. *When recording or auditing an internship, the query joins `SEMESTER_RESULT` on `Student_ID` and `Semester = 4` to dynamically retrieve the student's verified SGPA.*
> 3. *If the SGPA is below the minimum threshold (e.g. `< 6.50`) or if Semester 4 results are missing, the system flags a compliance violation or blocks registration.*
> 4. *This replaces hard-coded checks with database-driven academic rule evaluation."*

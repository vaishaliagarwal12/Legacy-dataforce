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

### Question 3: "Why did you specify `ON DELETE RESTRICT` for Company and Student, but `ON DELETE CASCADE` for Phone and Skill tables?"

**Short Answer**:
> *"Referential actions are designed around business domain semantics:
> - `ON DELETE CASCADE` is applied to dependent multivalued attributes (`STUDENT_PHONE`, `STUDENT_SKILL`, `PLACEMENT_SKILL`) because contact numbers and evaluated skills are dependent child entities that have zero institutional meaning once the parent student or placement offer is removed.
> - `ON DELETE RESTRICT` is applied to `COMPANY` and `STUDENT` on `PLACEMENT` and `INTERNSHIP` because deleting an entity with historical career records would destroy critical institutional audit trails, alumni records, and accreditation statistics. If a company has hired graduates or interns, or if a student has registered offers, MySQL error `1451` strictly prevents accidental or malicious deletion."*

---

### Question 4: "What Normal Form is your database in, and can you formally prove it?"

**Short Answer**:
> *"The canonical 7-table schema is divided into BCNF tables and an intentionally denormalized 1NF table:
> - **BCNF Tables**: `STUDENT`, `STUDENT_PHONE`, `STUDENT_SKILL`, `COMPANY`, `PLACEMENT`, and `PLACEMENT_SKILL`. Every determinant in non-trivial functional dependencies is a candidate key. For example, in `STUDENT`, keys are `Student_ID`, `Roll_No`, and `Email`; in `COMPANY`, `Company_ID` and `Company_Name`; and `STUDENT_PHONE`, `STUDENT_SKILL`, and `PLACEMENT_SKILL` are all-key relations.
> - **1NF Table (`INTERNSHIP`)**: Primary key is composite `(Student_ID, Internship_No)`. Institutional rules mandate that `Internship_No = 1` carries 4 credits in Sem 5, while `Internship_No = 2` carries 4 credits in Sem 8 (done in 8th semester, report submitted after the end of 8th semester). The functional dependency `Internship_No -> {Internship_Type, Credits, Report_Semester}` is a **partial dependency** on a proper subset of the primary key, formally violating 2NF, 3NF, and BCNF.
> - **Engineering Justification**: This intentional 1NF denormalization allows curriculum rules to be enforced directly inside `INTERNSHIP` using the `chk_internship_curriculum` constraint, streamlining the architecture into exactly 7 canonical tables without an auxiliary requirements table."*

---

### Question 5: "What is the difference between a Surrogate Key and a Natural Key, and why did you use both?"

**Short Answer**:
> *- A **Natural Key** is a business attribute that already exists in the real world (e.g., `Roll_No` like `CS202001`, or `Email`).*
> - A **Surrogate Key** is a system-generated unique integer (e.g., `Student_ID INT AUTO_INCREMENT`).*
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
> *- **INNER JOIN**: Used when records in both tables must exist. For example, when generating the active placement detail view (`V_PLACEMENT_DETAIL`), we only want offers where both the student and company exist.*
> - **LEFT OUTER JOIN**: Used when we must preserve records from the primary table even when no related child record exists. For example, when listing all students and their placement status, a `LEFT JOIN` on `PLACEMENT` returns all students, showing placed students with their package and unplaced students with `NULL`.*
> - *Crucial Semantics: **'Placed' strictly means `Joined = 'Yes'`**. Students with `Offer_Status = 'Accepted'` but `Joined = 'No'` are tracked under accepted offers, while only joined students are counted as placed."*

---

### Question 9: "What constitutes a Weak Entity in your schema, and how is it identified?"

**Short Answer**:
> *"A Weak Entity is an entity that cannot be uniquely identified by its own attributes alone and relies on an identifying relationship with a parent owner entity.
>
> In our 7-table schema, **`INTERNSHIP`** is a weak entity:
> - Identified by the composite primary key `(Student_ID, Internship_No)`. 'Internship 1' or 'Internship 2' has no independent existence without the student who completed it.
> - Similarly, `STUDENT_PHONE` and `STUDENT_SKILL` are weak identifying relations identified by `(Student_ID, Phone_No)` and `(Student_ID, Skill)`."*

---

### Question 10: "How does the system enforce curriculum rules and the Single-Joined-Offer rule?"

**Short Answer**:
> *"The system enforces institutional rules directly at the schema layer:
> 1. **Single-Joined-Offer Rule (`uq_one_joined_offer`)**: Enforced via a generated virtual column `Joined_Student INT GENERATED ALWAYS AS (CASE WHEN Joined = 'Yes' THEN Student_ID ELSE NULL END) STORED` with a `UNIQUE KEY (Joined_Student)`. Multiple `NULL`s are permitted (allowing multiple unjoined offers), but a second `Joined = 'Yes'` produces duplicate `Student_ID`s, triggering a unique key violation.
> 2. **Joined Status Constraint (`chk_placement_joined_status`)**: `CHECK (Joined = 'No' OR Offer_Status = 'Accepted')` physically guarantees that an offer cannot be marked joined unless it has been officially accepted.
> 3. **Internship Curriculum Constraint (`chk_internship_curriculum`)**: Enforces:
>    - Internship 1: Mandatory, 4 credits, evaluated in Semester 5 (done in summer after 2nd year).
>    - Internship 2: Mandatory, 4 credits, evaluated in Semester 8 (Internship 2: done in 8th semester, report submitted after the end of 8th semester).
>    - Internship 3+: Additional voluntary internships."*

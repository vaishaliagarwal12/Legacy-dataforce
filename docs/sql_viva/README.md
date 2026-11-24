# Comprehensive SQL & Relational DBMS Viva Handbook
## Campus Placement & Internship Management System (Canonical 7-Table Schema)

Welcome to the definitive SQL and Database Management Systems (DBMS) viva examination guide. This handbook is engineered specifically for 2nd-year Computer Science & Engineering students defending their laboratory projects before academic examiners.

Every single query, schema definition, functional dependency, and execution plan in this repository has been strictly verified against MySQL 8.0 running the canonical 7-table schema.

---

## 1. Document Index & Study Sequence

The study material is organized into five specialized modules, available in both GitHub Flavored Markdown and publication-ready PDF formats:

| # | Document File | PDF Export | Description | Target Topic |
|---|---|---|---|---|
| **01** | [`01_practice_30_problems.md`](file:///d:/Legacy%20dataforce/docs/sql_viva/01_practice_30_problems.md) | [`01_practice_30_problems.pdf`](file:///d:/Legacy%20dataforce/docs/sql_viva/pdf/01_practice_30_problems.pdf) | 30 Core Practice Problems (10 Easy, 10 Medium, 10 Hard) with full SQL, explanations, and verified sample outputs. | Comprehensive DBMS syllabus coverage. |
| **02** | [`02_query_writing_55_problems.md`](file:///d:/Legacy%20dataforce/docs/sql_viva/02_query_writing_55_problems.md) | [`02_query_writing_55_problems.pdf`](file:///d:/Legacy%20dataforce/docs/sql_viva/pdf/02_query_writing_55_problems.pdf) | 55 "Write a Query on the Spot" Problems (18 Easy, 20 Medium, 17 Hard) categorized by query archetype. | Rapid live query construction under exam pressure. |
| **03** | [`03_top_40_master_guide.md`](file:///d:/Legacy%20dataforce/docs/sql_viva/03_top_40_master_guide.md) | [`03_top_40_master_guide.pdf`](file:///d:/Legacy%20dataforce/docs/sql_viva/pdf/03_top_40_master_guide.pdf) | Top 40 Production Queries directly from Python services, routes, and views with teacher traps and 1-sentence answers. | Production application defense and code cross-examination. |
| **04** | [`04_remaining_queries_catalog.md`](file:///d:/Legacy%20dataforce/docs/sql_viva/04_remaining_queries_catalog.md) | [`04_remaining_queries_catalog.pdf`](file:///d:/Legacy%20dataforce/docs/sql_viva/pdf/04_remaining_queries_catalog.pdf) | Exhaustive catalog of all 157 SQL queries across `services/*.py` grouped by domain, with query pattern analysis. | Complete codebase reference and architectural consistency. |
| **05** | [`05_normalization_report_7_tables.md`](file:///d:/Legacy%20dataforce/docs/sql_viva/05_normalization_report_7_tables.md) | [`05_normalization_report_7_tables.pdf`](file:///d:/Legacy%20dataforce/docs/sql_viva/pdf/05_normalization_report_7_tables.pdf) | Formal mathematical normalization proof for all 7 tables (6 in BCNF, 1 in 1NF) + 10 critical viva Q&As. | Normalization theory, Armstrong's Axioms, and curriculum trade-offs. |

---

## 2. Canonical 7-Table Schema Architecture

The database strictly enforces the following 7 relational tables and 2 analytical views. No other tables exist.

```
                           +----------------------+
                           |       STUDENT        |
                           +----------------------+
                           | PK: Student_ID       |
                           | AK: Roll_No, Email   |
                           +----------+-----------+
                                      |
         +----------------------------+----------------------------+
         | 1:N                        | 1:N                        | 1:N
+--------v---------+         +--------v---------+         +--------v---------+
|  STUDENT_PHONE   |         |  STUDENT_SKILL   |         |    INTERNSHIP    |
+------------------+         +------------------+         +------------------+
| PK: (Student_ID, |         | PK: (Student_ID, |         | PK: (Student_ID, |
|      Phone_No)   |         |      Skill)      |         |      Internship) |
+------------------+         +------------------+         | FK: Student_ID   |
                                                          | FK: Company_ID   |
                                                          +--------+---------+
                                                                   |
                           +----------------------+                | N:1
                           |       COMPANY        |                |
                           +----------------------+                |
                           | PK: Company_ID       |                |
                           | AK: Company_Name     |<---------------+
                           +----------+-----------+
                                      |
                                      | 1:N
                           +----------v-----------+
                           |      PLACEMENT       |
                           +----------------------+
                           | PK: Placement_ID     |
                           | FK: Student_ID       |
                           | FK: Company_ID       |
                           | UQ: Joined_Student   |
                           +----------+-----------+
                                      |
                                      | 1:N
                           +----------v-----------+
                           |   PLACEMENT_SKILL    |
                           +----------------------+
                           | PK: (Placement_ID,   |
                           |      Skill)          |
                           +----------------------+
```

### Institutional Business Rules Enforced in Schema
1. **Placement Definition**:
   - `Offer_Status` must be `'Offered'`, `'Accepted'`, or `'Declined'` (never `'Joined'`).
   - `Joined` is `'Yes'` or `'No'`.
   - A student is formally considered **placed** if and only if `Joined = 'Yes'`.
   - A student can only join an offer that was accepted: `CHECK (Joined = 'No' OR Offer_Status = 'Accepted')`.
   - A student can join at most one offer: enforced via virtual column `Joined_Student = (CASE WHEN Joined = 'Yes' THEN Student_ID ELSE NULL END)` and unique index `uq_one_joined_offer`.
2. **Curriculum Internship Rules**:
   - `Internship_No = 1`: Mandatory, evaluated in Semester 5, 4 academic credits.
   - `Internship_No = 2`: Mandatory, conducted during 8th semester, report submitted after the end of 8th semester, Report_Semester = 8, 4 academic credits.
   - `Internship_No >= 3`: Additional/Voluntary industry internships (Credits and Report_Semester may be NULL).
   - Enforced by `chk_internship_curriculum`.

---

## 3. Topic-to-Problem Syllabus Mapping

Use this quick matrix to locate problems covering specific DBMS syllabus concepts:

| DBMS Topic | Covered In Module 01 | Covered In Module 02 | Covered In Module 03 |
|---|---|---|---|
| **Simple Projections & Filters** | P01, P02 | Q01, Q02, Q03, Q04 | Q01, Q05, Q12 |
| **Aggregate Functions & GROUP BY** | P04, P05, P06 | Q06, Q07, Q08, Q09, Q10 | Q03, Q07, Q16 |
| **HAVING vs WHERE Filters** | P07, P08 | Q11, Q12, Q13 | Q09, Q17 |
| **Inner Joins (Multi-table)** | P03, P09, P10 | Q14, Q15, Q16, Q17, Q18 | Q02, Q04, Q11 |
| **Outer Joins (LEFT / RIGHT)** | P11, P12 | Q19, Q20, Q21, Q22, Q23 | Q14, Q20, Q27 |
| **FULL OUTER JOIN Simulation** | P13 | Q24 | Q33 |
| **Self Joins** | P14 | Q25, Q26 | Q34 |
| **Correlated Subqueries & EXISTS** | P15, P16 | Q27, Q28, Q29, Q30 | Q10, Q21, Q29 |
| **Window Functions (ROW_NUMBER)** | P17 | Q31, Q32 | Q24, Q31 |
| **Window Functions (DENSE_RANK)** | P18, P19 | Q33, Q34, Q35, Q36 | Q08, Q28 |
| **Window Functions (LEAD / LAG)** | P20 | Q37, Q38 | Q35 |
| **Set Operations (UNION / EXCEPT)** | P21, P22 | Q39, Q40, Q41 | Q23, Q36 |
| **Date & String Functions** | P23, P24 | Q42, Q43, Q44, Q45 | Q18, Q26 |
| **Relational Views** | P25, P26 | Q46, Q47, Q48 | Q15, Q25 |
| **Transactions & Concurrency (ACID)** | P27, P28 | Q49, Q50, Q51 | Q37, Q38 |
| **B-Tree Indexes & EXPLAIN Tuning** | P29, P30 | Q52, Q53, Q54, Q55 | Q39, Q40 |

---

## 4. Exam Strategy: How to Prepare

### Scenario A: The Night Before the Viva (3-Hour Plan)
1. **Hour 1 - Normalization & Architecture** (`05_normalization_report_7_tables.md`):
   - Memorize the candidate keys for all 7 tables.
   - Understand why `INTERNSHIP` is in 1NF (Internship_No alone determines Type, Credits, and Report_Semester, which is a partial dependency on the composite PK `(Student_ID, Internship_No)`).
   - Memorize the 10 Normalization Viva Q&As.
2. **Hour 2 - Top 40 Master Guide** (`03_top_40_master_guide.md`):
   - Review Queries 1 through 20. Read the "What the Teacher May Ask" and rehearse the "1-Sentence Viva Answer" out loud.
   - Review Query 13 (`uq_one_joined_offer` virtual column trick) and Query 18 (`chk_internship_curriculum`).
3. **Hour 3 - Hard Query Patterns** (`01_practice_30_problems.md`):
   - Review Problems 21 to 30 (DENSE_RANK partition, FULL OUTER JOIN via UNION, Correlated NOT EXISTS, and Transaction SAVEPOINT rollback).

### Scenario B: 30 Minutes Before Entering the Room
1. Re-read the **10 Core Rules of MySQL Execution Order**:
   $$\text{FROM} \longrightarrow \text{ON} \longrightarrow \text{JOIN} \longrightarrow \text{WHERE} \longrightarrow \text{GROUP BY} \longrightarrow \text{WITH CUBE/ROLLUP} \longrightarrow \text{HAVING} \longrightarrow \text{SELECT} \longrightarrow \text{DISTINCT} \longrightarrow \text{ORDER BY} \longrightarrow \text{LIMIT}$$
2. Re-read the difference between `COUNT(*)`, `COUNT(column)`, and `COUNT(DISTINCT column)`.
3. Re-read why `WHERE` cannot filter aggregate expressions (because `WHERE` filters individual rows before grouping, while `HAVING` filters aggregated groups).
4. Review the single-joined-offer mechanism:
   ```sql
   Joined_Student INT GENERATED ALWAYS AS (
       CASE WHEN Joined = 'Yes' THEN Student_ID ELSE NULL END
   ) STORED,
   CONSTRAINT uq_one_joined_offer UNIQUE KEY (Joined_Student)
   ```

---

## 5. Live Query Writing Cheatsheet

When the examiner says: *"Open MySQL workbench/terminal and write me a query to..."*

1. **Step 1: Identify Tables and Keys**
   - Students $\rightarrow$ `STUDENT s` (`s.Student_ID`)
   - Placements $\rightarrow$ `PLACEMENT p` (`p.Placement_ID`, `p.Student_ID`)
   - Internships $\rightarrow$ `INTERNSHIP i` (`i.Student_ID`)
   - Companies $\rightarrow$ `COMPANY c` (`c.Company_ID`)
2. **Step 2: Choose Join Type Carefully**
   - If they ask for "All students, whether placed or not" $\rightarrow$ `STUDENT s LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID`.
   - If they ask for "Only placed students" $\rightarrow$ `INNER JOIN` with `WHERE p.Joined = 'Yes'`.
3. **Step 3: Handle NULLs in Aggregations**
   - When grouping students with `LEFT JOIN PLACEMENT p`, use `COUNT(p.Placement_ID)` instead of `COUNT(*)`. `COUNT(*)` counts the row containing `NULL` as 1, while `COUNT(p.Placement_ID)` correctly counts 0.
4. **Step 4: Ranking Problems**
   - Always clarify whether ties should have gaps:
     - Continuous ranks without gaps (1, 2, 2, 3) $\rightarrow$ `DENSE_RANK() OVER (ORDER BY col DESC)`
     - Ranks with gaps (1, 2, 2, 4) $\rightarrow$ `RANK() OVER (ORDER BY col DESC)`
     - Unique sequence numbers (1, 2, 3, 4) $\rightarrow$ `ROW_NUMBER() OVER (ORDER BY col DESC)`

---

## 6. Accompanying Artifacts

- **Proposed Extra Seed Data**: [`seed_extra.sql`](file:///d:/Legacy%20dataforce/seed_extra.sql) contains curated additional records for testing queries that return 0 rows on current seed data (e.g. unplaced students with no internships, companies with no offers). This script is non-destructive and is not applied to the production database automatically.
- **Automated Verification Harnesses**: Located in `scratch/`:
  - `scratch/test_practice30_queries.py`: Tests all 30 practice problems.
  - `scratch/test_gen55_queries.py`: Tests all 55 query-writing problems.
  - `scratch/test_top40_queries.py`: Tests all 40 production service queries.
  - `scratch/test_special_topics.py`: Verifies transaction rollbacks and negative constraint tests.

All queries run with 0 errors across 100% of test suites.

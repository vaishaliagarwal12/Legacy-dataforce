# 5-Minute Live Demonstration Script
## Campus Placement & Internship Management System

**Presenter Role**: Lead Database Architect & Full-Stack Developer  
**Audience**: Evaluation Committee / Professor  
**Target Time**: Exactly 5 Minutes (0:00 – 5:00)  
**Required Windows Open**:
1. Browser Window on `http://localhost:5000` (Application Dashboard)
2. Terminal Window ready with `pytest` / command prompt

---

## ⏱ Timeline Breakdown

```
0:00 ─── 0:45  [Part 1] Project Architecture & Executive Dashboard
0:45 ─── 1:45  [Part 2] Student Master, 1NF Attribute Decomposition & Academics
1:45 ─── 2:45  [Part 3] Corporate Recruitment Pipeline & Selection Rounds
2:45 ─── 3:45  [Part 4] LIVE RULE ENFORCEMENT: The Single-Accepted-Offer Rule
3:45 ─── 4:30  [Part 5] Mandatory Internships & Prerequisite SGPA Verification
4:30 ─── 5:00  [Part 6] Automated Test Suite (113 Passing Tests) & Wrap-Up
```

---

### Part 1: Project Architecture & Executive Dashboard (0:00 – 0:45)

**Action**: Open browser at `http://localhost:5000/`.

**Spoken Script**:
> *"Good morning, Professor. Today I am presenting our **Campus Placement and Academic Internship Management System**, built on **MySQL 8.0 (InnoDB)** and **Flask**.*
>
> *Our design addresses two chronic real-world challenges in university administration: first, maintaining **strict relational integrity** across normalized academic records without data anomalies; and second, enforcing **complex institutional policies**—such as preventing students from hoarding multiple accepted job offers while simultaneously tracking students who hold multiple preliminary offers.*
>
> *Here on the Executive Dashboard, all metrics are computed dynamically using high-performance SQL aggregate queries. We see active student counts, placement rate, highest compensation package, and average LPA. Below, Chart.js visualizes real-time distribution across hiring years, engineering branches, offer acceptance lifecycles, and internship compliance."*

---

### Part 2: Student Master & 1NF Attribute Decomposition (0:45 – 1:45)

**Action**: Click **"Students"** in the top navigation bar (`/students`). Then click on **"Aarav Sharma" (CS202001)**.

**Spoken Script**:
> *"Let's examine our student relational model. In standard unnormalized databases, student contact numbers and skills are often stored as comma-separated text strings, violating First Normal Form.*
>
> *In our relational architecture, we strictly decomposed the schema into 1NF: composite names are split into `First_Name` and `Last_Name`, while multivalued contact numbers and technical skills reside in dedicated child relation tables: `STUDENT_PHONE` and `STUDENT_SKILL` with composite primary keys.*
>
> *Furthermore, as you can see on Aarav's profile, we track verified semester-by-semester SGPA records in `SEMESTER_RESULT`. Notice the system enforces composite uniqueness on `(Student_ID, Semester)`—preventing duplicate results for the same academic semester, while CHECK constraints guarantee SGPAs remain strictly within the 0.00 to 10.00 scale."*

---

### Part 3: Corporate Recruitment Pipeline & Selection Rounds (1:45 – 2:45)

**Action**: Click **"Companies"** (`/companies`), then click on **"Google India"**.

**Spoken Script**:
> *"Next, let's look at the recruitment pipeline. Our corporate model follows a clean hierarchical foreign key chain:*
> 1. *`COMPANY` represents the recruiting organization.*
> 2. *`RECRUITMENT_DRIVE` captures seasonal campus drives by batch year.*
> 3. *`OPPORTUNITY` defines open roles, packages, and role type—either 'Placement' or 'Internship'.*
> 4. *`ELIGIBILITY` establishes a 1:1 constraint on minimum CGPA and allowed engineering branches.*
> 5. *`SELECTION_PROCESS` models multi-round interview stages (Aptitude, Coding, Technical, HR).*
>
> *Notice our referential integrity design: we enforce `ON DELETE RESTRICT` on companies. If an administrator tries to delete Google India while active recruitment drives or placed students exist, MySQL immediately aborts the deletion to protect institutional career history. Conversely, dependent selection rounds and eligibility records use `ON DELETE CASCADE` under their parent opportunity."*

---

### Part 4: LIVE RULE DEMO: The Single-Accepted-Offer Rule (2:45 – 3:45)

**Action**: Click **"Placements"** (`/placements`). Click the **"Multiple Offer Analytics"** tab, then show the offers table.

**Spoken Script**:
> *"Now for the core business logic highlight: **The Single-Accepted-Offer Policy**.*
>
> *Institutions encourage students to participate in multiple campus drives. A high-achieving student may legitimately receive multiple offers in `'Offered'` status from different companies—as seen here, where Aarav Sharma holds 3 distinct offers.*
>
> *However, institutional policy dictates that a student may accept **at most ONE** offer. Let me demonstrate how our system enforces this both at the database transaction layer and through the UI.*
>
> *Aarav has currently accepted an offer at Google India. If an administrator or student attempts to change his TCS or Infosys offer to `'Accepted'` or `'Joined'`:*

**Action**: Click **"Update Status"** on Aarav's pending TCS offer. In the modal, select `'Accepted'`, and click **"Save Changes"**.

**Show On Screen**: A bright alert flashes:
`"Cannot accept offer: Student CS202001 already holds an accepted offer (Offer #1 at Google India - Status: 'Accepted'). Institutional placement policy allows at most ONE Accepted offer per student. Decline the existing accepted offer before accepting another."`

**Spoken Script**:
> *"The transaction was aborted and rolled back with HTTP 409 Conflict. The student cannot accept another offer until they explicitly decline their existing one. This guarantees complete institutional equity without phantom or hoarded offers."*

---

### Part 5: Academic Internships & Prerequisite Compliance (3:45 – 4:30)

**Action**: Click **"Internships"** (`/internships`). Click on the **"Mandatory Compliance"** tab.

**Spoken Script**:
> *"In academic compliance, our curriculum mandates summer internships between semesters. Our system enforces a strict business rule: a student cannot register a Mandatory Summer Internship without satisfying the prerequisite SGPA threshold in their prior semesters.*
>
> *Using dynamic SQL joins between `INTERNSHIP`, `INTERNSHIP_REQUIREMENT`, and `SEMESTER_RESULT`, our system automatically checks that a student registering for Summer Internship 1 completed Semester 4 with an SGPA of at least 6.50.*
>
> *The tab here instantly flags students who are missing their mandatory degree-fulfilling internships, allowing the placement cell to take proactive corrective action before final graduation audits."*

---

### Part 6: Automated Test Suite & Conclusion (4:30 – 5:00)

**Action**: Switch to the terminal window and run:
```bash
python -m pytest
```

**Spoken Script**:
> *"Finally, to verify every constraint, cascade, and endpoint under rigorous engineering standards, we developed an automated test suite.*
>
> *As you can see running live in terminal, our test suite runs across 9 modules—testing check constraints, foreign key cascades, uniqueness rules, the one-accepted-offer rule, analytical CTE queries, and all REST endpoints.*
>
> *All **113 automated tests pass with 0 failures in under 30 seconds**.*
>
> *In summary, this project demonstrates how clean relational theory (1NF to BCNF), robust ACID transactions, and intuitive full-stack engineering can transform campus career administration. Thank you, and I am now ready for your questions."*

---

## 🎯 Presenter Quick-Reference Card

| What to Show | Route / Command | Key Talking Point |
| :--- | :--- | :--- |
| **KPIs & Charts** | `GET /` | Dynamic SQL aggregations & Chart.js visualization |
| **1NF Decomposition** | `GET /students/1` | `STUDENT_PHONE` & `STUDENT_SKILL` child relations |
| **Hierarchical Drives**| `GET /companies/1` | Company -> Drive -> Opportunity -> Selection Rounds |
| **Single Accepted Offer**| `GET /placements` | Block second acceptance with HTTP 409 Conflict |
| **Prerequisite SGPA** | `GET /internships` | Dynamic join checking prerequisite semester SGPA |
| **Test Suite Validation**| `python -m pytest` | **113 passed in ~30s** with 0 errors |

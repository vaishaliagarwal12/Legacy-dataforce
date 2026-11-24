# Legacy DataForce: Professional Project Demonstration Guide
## Campus Placement & Academic Internship Management ERP
**Platform Architecture**: Flask 3.1 &bull; Python 3.13 &bull; MySQL 8.0 (InnoDB) &bull; Chart.js &bull; Bootstrap 5.3
**Presenter Role**: Lead Database Architect & Full-Stack Systems Engineer
**Target Audience**: Academic Evaluation Committee / Project Viva Board
**Target Duration**: 8 to 10 Minutes (or 5-Minute Fast Track)

---

## 🛠 Pre-Demo Setup & Presenter Checklist (1 Minute Before Presentation)

Before calling the professors to your screen, ensure:
1. **MySQL Server Running**: Local MySQL 8.0 is running on port `3306`.
2. **Virtual Environment Active**: Terminal is in `d:\Legacy dataforce` with `.\.venv\Scripts\activate`.
3. **Flask Server Running**: Run `python app.py` (Server running at `http://localhost:5000`).
4. **Browser Windows Ready**:
   - Window 1: `http://localhost:5000/` (Main Executive Dashboard)
   - Window 2: `http://localhost:5000/health` (System Health Diagnostic - Shows MySQL Connected)
5. **Terminal Window Ready**: A clean terminal tab open to run `pytest` live during conclusion.
6. **Demo Data Note**: If using the separate fictional demonstration dataset, ensure it was generated using `python generate_demo_dataset.py`.

---

## ⏱ Master Demonstration Timeline

```
0:00 ─── 0:45  [Module 1] Executive Dashboard & Dynamic Multi-Filtering
0:45 ─── 2:00  [Module 2] Student Management & 1NF Attribute Decomposition
2:00 ─── 3:15  [Module 3] Corporate Hierarchy & Recruitment Pipeline
3:15 ─── 4:45  [Module 4] LIVE RULE DEMO: Single-Accepted-Offer Policy
4:45 ─── 6:00  [Module 5] Academic Internships & Prerequisite Compliance
6:00 ─── 7:15  [Module 6] Reporting Centre, Advanced SQL, CSV & PDF Export
7:15 ─── 8:30  [Module 7] Core DBMS Concepts & Automated Test Suite Proof
```

---

## 📍 Module 1: Executive Dashboard (0:00 – 0:45)

### Actions to Perform:
1. Open browser to `http://localhost:5000/`.
2. Point out the **8 Core University Placement KPI Cards**:
   - Total Students, Eligible Students (CGPA $\ge$ 6.00 and 0 Backlogs), Total Companies, Accepted Offers, Total Placement Offers, Successfully Placed Students (Joined), Average CTC Package, and Highest Package.
3. In the **Cohort & Placement Filters** toolbar:
   - Select **Batch Year**: `2024`.
   - Select **Branch**: `Computer Science`.
   - Point out that KPI cards and all 6 charts update dynamically via AJAX without a full-page reload.
   - Click **Reset** to restore aggregate university metrics.
4. Scroll down to show the **6 Interactive Visualizations**:
   - *Chart 1*: Branch-wise placement distribution.
   - *Chart 2*: Year-wise placement trends.
   - *Chart 3*: CTC package distribution.
   - *Chart 4*: Placement offers vs total internships.
   - *Chart 5*: Internship completion and curriculum compliance.
   - *Chart 6*: Multiple-offer student statistics.

### Spoken Script:
> *"Good morning, esteemed evaluation committee. Today, I am demonstrating **Legacy DataForce**, an enterprise university career and academic internship management system engineered on **MySQL 8.0 InnoDB** and **Flask**.*
>
> *Our system solves two critical challenges faced by university career centers: first, maintaining **strict relational integrity** across normalized academic records without redundancy; and second, enforcing **complex institutional policies**—such as tracking multiple preliminary job offers while strictly enforcing the single accepted offer rule.*
>
> *Here on the Executive Dashboard, all metrics are computed dynamically from MySQL using optimized SQL aggregation queries. When I apply filters for Batch 2024 and Computer Science, notice how the KPI counters and all six Chart.js visualizations refresh instantly via AJAX with zero animations, ensuring crisp enterprise performance."*

---

## 📍 Module 2: Student Management & 1NF Decomposition (0:45 – 2:00)

### Actions to Perform:
1. In the sidebar, click **"Students"** (`/students`).
2. Demonstrate **Advanced Search**:
   - In the search bar, type `Aarav` or `CS202001`. The table instantly filters to match.
   - Filter by **Branch**: `CSE`, **Min CGPA**: `≥ 8.0`, **Placement Status**: `Placed`.
   - Click column headers (e.g. **CGPA**) to show server-side sorting (ascending / descending).
   - Click **Export CSV** in the top-right header to demonstrate instant export of filtered student records.
3. Click on **Aarav Sharma** (`/students/1`) to display the **Canonical Student Profile Dossier**:
   - Point out the 4 canonical tabs: Profile & Academics, Technical Skills, Internships, and Placement Offers.
   - Point out **Multivalued Phone Numbers** (`STUDENT_PHONE`) and **Technical Skills** (`STUDENT_SKILL`).
   - Highlight Academic Standing: CGPA (9.20), 0 Backlogs, and Placed destination.

### Spoken Script:
> *"Let's navigate to the Student Management module. In standard legacy databases, student phone numbers and technical skills are often stored as comma-separated text strings, directly violating First Normal Form (1NF).
>
> In our relational architecture, we strictly decomposed multivalued attributes into dedicated child relation tables: `STUDENT_PHONE` and `STUDENT_SKILL` with composite primary keys `(Student_ID, Phone_No)` and `(Student_ID, Skill)`.
>
> On Aarav's profile, notice his academic standing and career outcome. All tables in this master domain satisfy Boyce-Codd Normal Form (BCNF) with verified primary and candidate keys."*

---

## 📍 Module 3: Corporate Hierarchy & Hiring Records (2:00 – 3:15)

### Actions to Perform:
1. Click **"Companies"** (`/companies`) in the sidebar.
2. In the Search bar, filter by category: select **"Product"**.
3. Click on a company record (`/companies/1`).
4. Walk the committee through the **Canonical Corporate Relationship Design**:
   - `COMPANY`: Corporate entity metadata, industry sector, location, and category.
   - **Placement Offers Card** (Left): Shows all graduate offers issued by this company (`PLACEMENT`).
   - **Internship Engagements Card** (Right): Shows all student internships hosted by this company (`INTERNSHIP`).
5. Highlight **Referential Integrity Design**:
   - Point to the "Delete Company" button. Explain that `ON DELETE RESTRICT` protects the corporate partner from accidental deletion because active placed students or interns exist.

### Spoken Script:
> *"Next, let's examine our corporate hiring records. The canonical schema models clean relational connections directly between companies, student placements, and internships:
> 1. `COMPANY` represents the verified hiring partner.
> 2. `PLACEMENT` captures full-time employment offers, compensation packages, and joined outcomes.
> 3. `INTERNSHIP` records curricular practical training and degree internship fulfillment.
>
> Notice our referential integrity design: we enforce `ON DELETE RESTRICT` on companies. If an administrator attempts to delete a company while students hold offers or completed internships, MySQL immediately aborts the deletion (error 1451) to protect institutional career history. Conversely, evaluated skills in `PLACEMENT_SKILL` use `ON DELETE CASCADE` under their parent offer."*

---

## 📍 Module 4: LIVE RULE DEMO: The Single-Accepted-Offer Policy (3:15 – 4:45)

### Actions to Perform:
1. Click **"Placements"** (`/placements`) in the sidebar.
2. Click the **"Star Performers (Multiple Offers)"** tab (`/placements?view=multiple`).
   - Point out that high-achieving student **Aarav Sharma (CS202001)** holds **3 distinct offers**:
     * Offer #1: Google India — Status: `Accepted` (42.0 LPA)
     * Offer #2: TCS — Status: `Offered` (7.5 LPA)
     * Offer #3: Infosys — Status: `Offered` (9.5 LPA)
3. Return to the **"All Placement Offers"** tab.
4. **Trigger the Live Rule Violation**:
   - Locate Offer #2 (Aarav Sharma at TCS).
   - Click the **"Update Status"** button.
   - In the modal dropdown, select `'Accepted'`.
   - Click **"Save Changes"**.
5. **Show the Result on Screen**:
   - The application intercepts the request, aborts the database transaction, and flashes a bright alert:
     > `"Cannot accept offer: Student CS202001 already holds an accepted offer (Offer #1 at Google India - Status: 'Accepted'). Institutional placement policy allows at most ONE Accepted offer per student. Decline the existing accepted offer before accepting another."`
6. Explain the ACID transaction implementation:
   - The service issues `SELECT ... FOR UPDATE` to lock candidate records, checks if any other placement has `Offer_Status IN ('Accepted', 'Joined')`, rolls back the transaction, and returns HTTP 409 Conflict.

### Spoken Script:
> *"Now for the core business rule highlight: **The Single-Accepted-Offer Policy**.*
>
> *Institutions encourage students to participate in multiple recruitment drives. A student may legitimately receive multiple preliminary offers in `'Offered'` status from different companies—as seen here, where Aarav Sharma holds 3 distinct offers.*
>
> *However, institutional placement policy dictates that a student may accept **at most ONE** job offer to ensure equity for fellow classmates.*
>
> *Aarav has currently accepted an offer at Google India. Watch what happens when an administrator or student attempts to change his TCS offer to `'Accepted'`...*
>
> *(Click Save Changes $\rightarrow$ Alert flashes)*
>
> *The system aborts the operation. At the database layer, this is enforced inside an atomic ACID transaction using row-level locking (`SELECT ... FOR UPDATE`). The student cannot accept another offer until they explicitly decline their existing one. This completely prevents offer hoarding and phantom vacancies."*

---

## 📍 Module 5: Academic Internships & Prerequisite Compliance (4:45 – 6:00)

### Actions to Perform:
1. Click **"Internships"** (`/internships`) in the sidebar.
2. Point out the KPI Cards:
   - Mandatory I1 Completed, Mandatory I2 Completed, Additional Internships, Pending Reports, Degree Compliance Rate.
3. Click the **"Mandatory Compliance Audit"** tab (`#compliance-tab`):
   - Point out how the system partitions candidates:
     * Fully Compliant: Completed both Mandatory Internship 1 and 2.
     * Partially Compliant: Completed I1, pending I2.
     * Missing Mandatory: Flagged students requiring academic dean intervention.
4. Explain the **Academic Prerequisite Rule**:
   - Mandatory Summer Internship 1 (after Sem 4, evaluated in Semester 5, 4 credits).
   - Mandatory Internship 2 (done in 8th semester, report submitted after the end of 8th semester, 4 credits).
5. Click on an internship record (`/internships/1`) to show the dossier:
   - Start Date, End Date, Dynamic Duration (via `V_INTERNSHIP_DETAIL`), Stipend, Report Semester, Grade, and Certificate link.

### Spoken Script:
> *"In university academic governance, degree fulfillment requires mandatory internships. Our system enforces strict curriculum rules directly in MySQL:
> - Internship 1 is completed during the summer break after Semester 4, carrying 4 credits with report submitted in Semester 5.
> - Internship 2: done in 8th semester, report submitted after the end of 8th semester, carrying 4 credits (Report_Semester = 8).
> - Additional internships (No. 3 and above) are voluntary and optional.
>
> Enforced by the `chk_internship_curriculum` constraint and checked in the Python service layer, duration is computed on the fly through view `V_INTERNSHIP_DETAIL` using DATEDIFF, storing zero redundant weeks or months."*

---

## 📍 Module 6: Reports & SQL Analytics Reporting Centre (6:00 – 7:15)

### Actions to Perform:
1. Click **"Reports & Filters"** (`/reports`) in the sidebar.
2. Demonstrate dynamic reporting filters:
   - Select Batch Year `2024` and Branch `Computer Science`.
   - Scroll through the 10 real-time analytical reports:
     1. Branch-Wise Placement Statistics
     2. Year-Wise Placement Trends
     3. Package Distribution & Salary Quartiles
     4. Company-Wise Hiring Performance
     5. Multiple Placement Offer Analysis
     6. Academic Internship Compliance Audit
     7. Unplaced Students Identification
     8. CGPA vs Placement Outcome Correlation
     9. Recruitment Drive Conversion Analysis
     10. Semester Performance vs Placement Package
3. **Export Live Reports**:
   - Click **"Export CSV"**: Demonstrates immediate CSV download with active filter parameters.
   - Click **"Export PDF"**: Opens a professionally generated ReportLab landscape PDF report with headers, date stamps, and tabular styling.
   - Press **Ctrl+P** (Print Preview): Point out the clean print stylesheet (`@media print`) that automatically conceals sidebars, top navbars, and buttons.
4. Click **"SQL Reports"** (`/sql-reports`):
   - Show the SQL Analytics Console where CTEs, Window Functions (`DENSE_RANK()`, `ROW_NUMBER()`), and conditional aggregations are inspected directly.

### Spoken Script:
> *"In our reporting center, we provide 10 analytical reports computed from live relational data. These reports leverage advanced MySQL features including Common Table Expressions (CTEs), window functions like `DENSE_RANK()`, and conditional aggregation.*
>
> *Administrators can filter by batch or branch, export the results to CSV for external auditing, or generate a publication-quality landscape PDF complete with institutional branding.*
>
> *Furthermore, our clean print stylesheet guarantees that pressing Ctrl+P generates an audit-ready physical report without UI distractions."*

---

## 📍 Module 7: Core DBMS Concepts & Automated Test Suite Proof (7:15 – 8:30)

### Actions to Perform:
1. Switch to your terminal window.
2. Execute the full test suite live:
   ```bash
   pytest -q --disable-warnings
   ```
3. While tests run (approx. 75 seconds), present the **Core DBMS Concepts Alignment Table**:

| DBMS Concept | Implementation in Legacy DataForce |
| :--- | :--- |
| **Relational Model & Normalization** | Canonical 7 base tables (6 in BCNF, 1 in 1NF with curriculum denormalization); 1NF decomposition for phones & skills (`STUDENT_PHONE`, `STUDENT_SKILL`). |
| **Integrity Constraints** | Primary keys on all tables, composite keys on child tables, `CHECK` constraints on CGPA (0-10), placement joined status, and dates (`End_Date >= Start_Date`). |
| **Referential Integrity** | `ON DELETE RESTRICT` on students and companies to protect placement/internship history; `ON DELETE CASCADE` on `STUDENT_PHONE`, `STUDENT_SKILL`, `PLACEMENT_SKILL`. |
| **ACID Transactions** | Multi-table inserts and the Single-Joined-Offer rule wrapped in atomic transactions with rollback on conflict. |
| **Indexing & Performance** | Clustered primary B-Tree indexes + secondary composite indexes on `(Branch, Batch_Year)` and `(CGPA)`. |
| **Database Views** | `v_placement_detail` and `v_internship_detail` abstracting complex multi-table joins. |
| **Advanced SQL** | Window functions (`DENSE_RANK()`, `ROW_NUMBER()`), CTEs (`WITH ...`), and conditional aggregations (`COUNT(CASE WHEN...)`). |

4. When the test runner finishes:
   - Point to the final terminal output: **248 passed in ~80s (100% pass rate, 0 failures, 0 errors)**.

### Spoken Script:
> *"Finally, to verify every constraint, cascade, and transaction under rigorous engineering standards, we developed an automated test suite across 23 test modules.*
>
> *As you can see live in terminal, our test suite tests database check constraints, foreign key cascades, uniqueness rules, the single accepted offer policy, analytical CTE queries, transaction rollbacks, security sanitization, and all REST endpoints.*
>
> *All **248 automated tests pass with 0 failures**.*
>
> *In summary, Legacy DataForce demonstrates how clean relational theory (1NF to BCNF), robust ACID transactions, and intuitive full-stack engineering can transform university career administration. Thank you, and I am now ready for your questions."*

---

## 💡 Troubleshooting & Demo Safety Tips

- **If MySQL connection drops**: Navigate to `/health` to verify status. The application includes user-friendly 500 error pages with retry and diagnostic buttons.
- **If offline during presentation**: Both Bootstrap and Chart.js include local fallback assets in `static/vendor/`, ensuring 100% offline functionality.
- **If asked about real student data**: Reiterate that all names, emails, phone numbers, and organizations in the system are 100% fictional and synthetic, generated exclusively for academic demonstration.

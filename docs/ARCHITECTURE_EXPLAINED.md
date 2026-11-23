# Architecture Explained: Placement & Internship Management System

> **Target Audience:** 2nd-Year Computer Science & Engineering (CSE) Student  
> **Purpose:** Clear, step-by-step technical explanation for college lab viva, external examiners, and faculty project reviews.  
> **Codebase Baseline:** Verified against the active 7-table relational schema on branch `seven-table-schema`.

---

## PART 1: The Big Picture

### What This Project Does and Who Uses It
**Legacy Dataforce** is a web-based Placement and Internship Management System built for university training and placement departments, academic coordinators, and campus recruiters. It centralizes student academic performance records (CGPA, backlogs, technical skills), company recruitment partnerships, campus job offers (placement records, salary packages, joining status), and student internship milestones. The system tracks academic requirements (such as mandatory 5th-semester summer internship reports and 8th-semester final internships) and provides administrators with real-time analytics, downloadable CSV reports, and a secured interactive SQL query console.

### Request-Response Architecture Diagram

```text
+----------------------------------------------------------------------------------------------------+
|                                         CLIENT / FRONTEND                                          |
|                                                                                                    |
|    Web Browser (Chrome, Firefox, Edge)                                                             |
|    - HTML5 UI Pages (Rendered by Jinja2 templates extending base.html)                             |
|    - Bootstrap 5 & Custom CSS (Visual Styling & Responsive Grid)                                   |
|    - JavaScript Fetch API (AJAX calls for dynamic data without reloading)                         |
|    - Chart.js (Interactive visual charts on HTML5 <canvas> elements)                              |
+-------------------------------------------------+--------------------------------------------------+
                                                  |
                     1. HTTP Request              | 8. HTTP Response
                   (GET, POST with CSRF)          |  (HTML or JSON)
                                                  v
+----------------------------------------------------------------------------------------------------+
|                                    APPLICATION SERVER (Flask)                                      |
|                                                                                                    |
|  [ app.py ] - Flask Application Factory & Middleware Pipeline                                      |
|    ├── 1. Initializes app with config.py & .env settings                                           |
|    ├── 2. @app.before_request: CSRF token verification for POST/PUT/DELETE                         |
|    ├── 3. Global Error Handlers: Intercepts 400, 404, 500, DatabaseError, ServiceError            |
|    └── 4. @app.after_request: Injects OWASP HTTP security headers (nosniff, SAMEORIGIN)            |
+-------------------------------------------------+--------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|  [ routes/ ] - HTTP Routing & Controller Layer                                                     |
|    ├── routes/main.py: HTML Web Pages & SQL Console (GET /students, POST /students/new)            |
|    └── routes/students.py, companies.py, etc.: Pure REST API endpoints (/api/students)            |
+-------------------------------------------------+--------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|  [ services/ ] - Business Logic & Domain Validation Layer                                          |
|    ├── Input Sanitization & Range Checks (CGPA between 0.00 and 10.00, valid Enums)                |
|    ├── Business Rule Enforcement (1 Joined offer per student, Mandatory internship rules)          |
|    ├── Parameterized SQL Formulation (%s placeholders only - NO string formatting)                 |
|    └── Atomic Transactions (conn.commit() on success, conn.rollback() on exception)                |
+-------------------------------------------------+--------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|  [ db/connection.py ] - Data Access & Connection Pool Layer                                        |
|    ├── get_connection(): Read/Write PyMySQL connection for standard application services          |
|    ├── get_readonly_connection(): Isolated connection using restricted MySQL user                  |
|    └── get_cursor(commit=True): Context manager managing transactions & DictCursor                |
+-------------------------------------------------+--------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|                                      RELATIONAL DATABASE ENGINE                                    |
|                                                                                                    |
|  [ MySQL Server 8.0+ ]                                                                             |
|    ├── Canonical 7-Table Schema: STUDENT, STUDENT_PHONE, STUDENT_SKILL,                           |
|    │                             COMPANY, PLACEMENT, PLACEMENT_SKILL, INTERNSHIP                   |
|    ├── Relational Views: V_PLACEMENT_DETAIL, V_INTERNSHIP_DETAIL                                   |
|    ├── Integrity Constraints: Foreign Keys, Unique Keys (uq_one_joined_offer), CHECK Constraints   |
|    └── User Access Control: Root/Admin user (read-write) vs placement_readonly (SELECT only)       |
+----------------------------------------------------------------------------------------------------+
```

### Technology Stack Summary

| Technology | Role in Project | One-Line Explanation |
| :--- | :--- | :--- |
| **Python** | Backend Language | Powers the server runtime, handles data structures, and executes application logic. |
| **Flask** | Web Framework | Lightweight micro-framework that maps HTTP URLs to Python handler functions. |
| **Jinja2** | Template Engine | Merges backend Python dictionaries into HTML templates before sending them to the browser. |
| **PyMySQL** | Database Driver | Pure-Python database connector that sends parameterized SQL queries to MySQL. |
| **MySQL** | Relational Database (RDBMS) | Stores all persistent tables, enforces primary/foreign keys, and executes SQL queries. |
| **HTML** | Markup Language | Defines the structural layout and form inputs for all web pages. |
| **CSS** | Styling Language | Controls page colors, typography, spacing, and visual appearance. |
| **Bootstrap 5** | CSS Framework | Provides responsive grid layouts, navigation bars, modals, and alert badges. |
| **JavaScript (`fetch`)** | Client-Side Scripting | Sends background HTTP requests to Flask API endpoints without refreshing the page. |
| **Chart.js** | Data Visualization | Renders interactive HTML5 canvas charts for placement rates, packages, and trends. |
| **pytest** | Automated Testing | Test framework running 241 unit, integration, and security tests across the project. |

---

## PART 2: Backend Architecture (Layer by Layer)

### Layer 1: Application Factory & Middleware (`app.py`)

- **What It Does:**  
  `app.py` is the central initialization hub of the application. It implements the **Application Factory Pattern** through the `create_app()` function. It loads configuration classes, registers 6 modular route blueprints (`health_bp`, `main_bp`, `student_bp`, `company_bp`, `placement_bp`, `internship_bp`), intercepts incoming requests via `@app.before_request` to enforce CSRF security tokens, applies OWASP security headers on outgoing responses via `@app.after_request`, injects global template variables (such as `csrf_token` and `is_db_connected`), and defines centralized HTTP error handlers (`400`, `404`, `500`, `ServiceError`, `DatabaseError`).
- **What It Must NOT Do:**  
  `app.py` must **never** contain raw SQL queries, direct database table operations, or specific business rule calculations (e.g., verifying student placement eligibility or calculating average packages).
- **Two Example Files:**  
  1. `app.py` (The application factory and middleware configuration).  
  2. `tests/test_health.py` (Tests application factory startup and health endpoints).

---

### Layer 2: Configuration & Environment (`config.py` and `.env`)

- **What It Does:**  
  `config.py` defines the centralized `Config` class and its environment-specific subclasses (`DevelopmentConfig`, `TestingConfig`, `ProductionConfig`). It reads environment variables from the `.env` file using `python-dotenv`. It configures database connection parameters (host, port, user, password, database name), the read-only user credentials (`MYSQL_READONLY_USER`), application secret keys (`SECRET_KEY`), query limits (`SQL_REPORT_MAX_ROWS = 500`), and statement timeout thresholds (`SQL_REPORT_TIMEOUT_MS = 3000`).
- **Why Passwords Are Not in Code:**  
  Hardcoding database passwords in source code is a major security vulnerability. If code is pushed to a public repository (like GitHub), credentials are leaked immediately. Keeping configuration in `.env` ensures secrets stay local to the host server, while `.gitignore` prevents `.env` from ever being tracked in Git. The project provides `.env.example` as a safe template.
- **What It Must NOT Do:**  
  `config.py` must **never** run database queries, handle web requests, or render templates.
- **Two Example Files:**  
  1. `config.py` (Configuration class and parameter getters).  
  2. `.env.example` (Template defining required environment variables without real passwords).

---

### Layer 3: Routing & Controller Layer (`routes/`)

- **What a Route Is:**  
  A route is a Python function decorated with `@blueprint.route('/url-path', methods=['GET', 'POST'])`. Its job is to receive an HTTP request, extract query parameters (`request.args`) or submitted form data (`request.form` / `request.get_json()`), call the appropriate service function, and return an HTTP response (either rendered HTML or a JSON object).
- **HTML Pages vs. JSON APIs:**  
  - **HTML Pages:** Handled by `routes/main.py`. This file serves the user-facing web pages (`/`, `/students`, `/companies`, `/placements`, `/internships`, `/reports`, `/sql-reports`) using `render_template()`.
  - **JSON REST APIs:** Handled by `routes/students.py`, `routes/companies.py`, `routes/placements.py`, and `routes/internships.py`. These files handle programmatic API requests (`/api/students`, `/api/companies`, etc.) and return pure JSON via Flask's `jsonify()`.
- **Real Route Example End-to-End (`students_list` in `routes/main.py`):**
  ```python
  @main_bp.route("/students", methods=["GET"])
  def students_list():
      # 1. Read query parameters from URL (e.g., /students?search=John&branch=CSE&page=1)
      search = request.args.get("search", "").strip() or None
      raw_branch = request.args.get("branch", "").strip() or None
      branch = normalize_branch(raw_branch)
      page = parse_int(request.args.get("page", 1), "Page", 1)
      page_size = 15

      # 2. Call service layer to fetch filtered students and total count
      result = list_students(
          page=page,
          page_size=page_size,
          search=search,
          branch=branch
      )

      # 3. Render HTML template with the retrieved data
      return render_template(
          "students/index.html",
          active_page="students",
          students=result["students"],
          total=result["total"],
          page=page,
          total_pages=result["total_pages"],
          search=search or "",
          branch=branch or ""
      )
  ```
- **What It Must NOT Do:**  
  Routes must **never** construct raw SQL strings, use PyMySQL cursor objects directly, or execute database commits and rollbacks.
- **Two Example Files:**  
  1. `routes/main.py` (Web UI controller serving HTML pages and SQL report APIs).  
  2. `routes/students.py` (JSON REST API controller for student resources).

---

### Layer 4: Business Logic & Services Layer (`services/`)

- **What It Does:**  
  The `services/` layer is the heart of the backend. It contains all domain rules, data validation, database interaction, and transaction management. When a route calls a service, the service validates input fields, verifies uniqueness, starts a transaction, executes SQL queries using PyMySQL with parameterized `%s` placeholders, commits on success, and rolls back if an error occurs.
- **Real Service Function Step-by-Step (`create_student` in `services/student_service.py`):**
  1. **Validation:** Calls `validate_student_payload(data)` to verify mandatory fields (`Roll_No`, `First_Name`, `Branch`, `CGPA`, `Email`). Ensures CGPA is between 0.00 and 10.00 and Backlogs $\ge$ 0.
  2. **Uniqueness Check:** Executes `SELECT Student_ID FROM STUDENT WHERE Roll_No = %s` and `WHERE Email = %s`. Raises `ConflictError` if a duplicate is found.
  3. **Atomic Transaction:** Opens `with get_cursor(commit=True) as cursor:`.
  4. **Primary Insert:** Executes `INSERT INTO STUDENT (...) VALUES (%s, %s, ...)` and retrieves the auto-generated primary key using `cursor.lastrowid`.
  5. **Multivalued Inserts:** If phone numbers or skills are provided, executes `cursor.executemany()` to insert into `STUDENT_PHONE` and `STUDENT_SKILL`.
  6. **Commit / Rollback:** The context manager automatically issues `connection.commit()` when exiting cleanly. If an exception is raised, it automatically calls `connection.rollback()`.
  7. **Return Data:** Calls `get_student(student_id)` to return the newly created student record.
- **What It Must NOT Do:**  
  Services must **never** import Flask's `request` or `session`, parse HTTP request headers, or call `render_template()`. Services receive plain Python types (strings, ints, dicts) and return plain Python types.
- **Two Example Files:**  
  1. `services/student_service.py` (Student registration, phone/skill management, and queries).  
  2. `services/placement_service.py` (Placement offer tracking, salary validations, and single-joined-offer rule).

---

### Layer 5: Data Access & Database Connection (`db/connection.py`)

- **What It Does:**  
  `db/connection.py` manages low-level database communication using PyMySQL. It provides:
  - `get_connection()`: Context manager that opens a connection to MySQL using application credentials (`Config.get_db_config()`) and guarantees the connection is closed when done.
  - `get_readonly_connection()`: Context manager that connects using the restricted MySQL user `placement_readonly` (`Config.get_readonly_db_config()`).
  - `get_cursor(commit=False)`: Context manager that yields a `DictCursor` (returning rows as Python dictionaries). If `commit=True`, it commits on success and executes `connection.rollback()` if an error occurs.
- **Why a Read-Only MySQL User Exists:**  
  The system includes an interactive SQL Console where users can run custom queries. To achieve **Defense-in-Depth**, we do not rely solely on Python string checks. Even if a user crafts a query that bypasses Python-level filters, the MySQL database engine itself rejects any `INSERT`, `UPDATE`, `DELETE`, `DROP`, or `ALTER` command because the `placement_readonly` user has only `SELECT` privileges.
- **What It Must NOT Do:**  
  `db/connection.py` must **never** contain table-specific business rules or hardcoded business queries.
- **Two Example Files:**  
  1. `db/connection.py` (Connection context managers and cursor helpers).  
  2. `db/__init__.py` (Package exports for connection utilities).

---

### Layer 6: Relational Database Layer (`MySQL`)

The database stores all persistent state across **exactly 7 canonical tables** and **2 relational views**:

1. **`STUDENT`**: Stores core student identity and academic records.  
   - *Primary Key:* `Student_ID` (Auto Increment).  
   - *Unique Keys:* `Roll_No`, `Email`.  
   - *Constraints:* `chk_student_cgpa` (CGPA between 0.00 and 10.00), `chk_student_backlogs` (Backlogs $\ge$ 0).  
   - *Foreign Keys:* None.
2. **`STUDENT_PHONE`**: Stores multivalued phone numbers (1NF decomposition).  
   - *Primary Key:* `(Student_ID, Phone_No)`.  
   - *Foreign Key:* `Student_ID` references `STUDENT(Student_ID)` ON DELETE CASCADE.
3. **`STUDENT_SKILL`**: Stores multivalued student technical skills (1NF decomposition).  
   - *Primary Key:* `(Student_ID, Skill)`.  
   - *Foreign Key:* `Student_ID` references `STUDENT(Student_ID)` ON DELETE CASCADE.
4. **`COMPANY`**: Stores recruiting organization profiles.  
   - *Primary Key:* `Company_ID` (Auto Increment).  
   - *Unique Key:* `Company_Name`.  
   - *Foreign Keys:* None.
5. **`PLACEMENT`**: Stores job offers received by students.  
   - *Primary Key:* `Placement_ID` (Auto Increment).  
   - *Foreign Keys:* `Student_ID` references `STUDENT(Student_ID)`, `Company_ID` references `COMPANY(Company_ID)`.  
   - *Constraints:* `chk_placement_package` (Package > 0), `chk_placement_joined_status` (`Joined = 'No' OR Offer_Status = 'Accepted'`).  
   - *Unique Key:* `uq_one_joined_offer` on generated column `Joined_Student` (ensures a student can join at most one offer).
6. **`PLACEMENT_SKILL`**: Stores required skills evaluated for a placement offer.  
   - *Primary Key:* `(Placement_ID, Skill)`.  
   - *Foreign Key:* `Placement_ID` references `PLACEMENT(Placement_ID)` ON DELETE CASCADE.
7. **`INTERNSHIP`**: Weak entity tracking student internships and curriculum milestones.  
   - *Primary Key:* `(Student_ID, Internship_No)`.  
   - *Foreign Keys:* `Student_ID` references `STUDENT(Student_ID)`, `Company_ID` references `COMPANY(Company_ID)`.  
   - *Constraints:* `chk_int_no` (Internship_No $\ge$ 1), `chk_internship_dates` (`End_Date >= Start_Date`), and `chk_internship_curriculum` enforcing:  
     - Internship 1: Mandatory, 4 credits, evaluated in Semester 5 (`Report_Semester = 5`).  
     - Internship 2: Mandatory, done in 8th semester, report submitted after the end of 8th semester, 4 credits (`Report_Semester = 8`).  
     - Internship 3+: Additional, optional credits/semester.

**Relational Views:**
- `V_PLACEMENT_DETAIL`: Joins `PLACEMENT`, `STUDENT`, and `COMPANY` for unified reporting.
- `V_INTERNSHIP_DETAIL`: Joins `INTERNSHIP`, `STUDENT`, and `COMPANY`, calculating `Duration_Months` dynamically via `ROUND(DATEDIFF(End_Date, Start_Date) / 30.44, 1)`.

**Database Bootstrapping (`init_mysql.py` / `schema.sql` / `seed.sql`):**  
Running `python init_mysql.py` connects to MySQL, drops any obsolete tables, executes `schema.sql` to recreate all 7 tables and 2 views with their constraints, and then executes `seed.sql` to populate sample students, companies, placements, and internships.

---

### Layer 7: Security Architecture

1. **SQL Injection Prevention:**  
   Every query executed by application services uses PyMySQL parameterized placeholders (`%s`). User input is never concatenated or formatted into SQL strings. The MySQL driver transmits parameters separately from the SQL statement text.
2. **CSRF (Cross-Site Request Forgery) Protection:**  
   Implemented using the Synchronizer Token Pattern. In `app.py`, `@app.before_request` intercepts all state-modifying requests (`POST`, `PUT`, `PATCH`, `DELETE`). It verifies that `request.form['csrf_token']` or header `X-CSRFToken` matches the cryptographically signed token generated in the user's session.
3. **Read-Only SQL Console Sandbox:**  
   Multi-tiered security protects the custom SQL runner:
   - Server-side validation (`validate_custom_sql` in `services/sql_report_service.py`): Requires query to begin with `SELECT`, prohibits comment characters (`--`, `/*`, `#`), allows only one statement (no semicolons), and blocks keywords like `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`.
   - Execution as `placement_readonly`: Executes through `get_readonly_connection()` under a dedicated MySQL user who has only `SELECT` privileges.
   - Resource limits: Automatically enforces `LIMIT 500` and a 3,000 ms statement execution timeout.
4. **Input Validation:**  
   Rigorous boundary validation in `services/` (e.g., CGPA must be a valid float between 0.00 and 10.00; dates must have End Date $\ge$ Start Date).
5. **Safe Error Handling:**  
   Database exceptions (`pymysql.err.IntegrityError`, `DatabaseError`) are caught at the service and route boundaries. Technical stack traces are logged to the server console, while clean, human-readable messages (e.g., "A student with Roll Number CS202101 already exists") are shown to the user without crashing the application.

---

### Layer 8: Automated Test Suite (`tests/`)

- **What Tests Cover:**  
  The `tests/` directory contains 241 automated tests verifying every layer of the system:
  - Database schema integrity and CHECK constraints (`test_db_constraints.py`, `test_7_table_architecture.py`).
  - Service-layer business rules and transaction rollbacks (`test_services_unit.py`, `test_transactions_rollback.py`).
  - Web route integration and form submission (`test_routes_integration.py`, `test_phase2_controller_and_forms.py`).
  - CSRF protection, SQL injection resistance, and SQL console security (`test_security.py`, `test_sql_reports.py`).
  - Analytics and dynamic dashboard calculations (`test_dashboard_upgrade.py`).
- **How to Run pytest:**  
  Open a terminal in the project root and run:
  ```powershell
  pytest -v
  ```
  *(All 241 tests pass with zero failures).*

---

## PART 3: Project File Map

The following table catalogs every top-level folder and file in the workspace, identifying its purpose, architectural layer, and lifecycle status.

| Folder or File | What Is Inside | Which Layer It Belongs To | One Example Inside | Status |
| :--- | :--- | :--- | :--- | :--- |
| `app.py` | Flask factory, blueprints, CSRF check, security headers, error handlers | Application / Middleware | `create_app()` | **Active** |
| `config.py` | Configuration classes, database parameters, secret keys, limits | Configuration | `Config.get_db_config()` | **Active** |
| `init_mysql.py` | Python script to recreate tables from `schema.sql` and load `seed.sql` | Database Initialization | Script execution entry | **Active** |
| `schema.sql` | DDL script defining the 7 canonical tables, constraints, indexes, views | Database Schema | `CREATE TABLE STUDENT` | **Active** |
| `seed.sql` | DML script inserting sample students, companies, placements, internships | Database Seed Data | `INSERT INTO STUDENT` | **Active** |
| `verify.sql` | SQL verification script checking table count, foreign keys, constraints | Database Quality Assurance | Orphan check queries | **Active** |
| `routes/` | HTTP controllers for web UI and JSON REST endpoints | Routing / Controllers | `routes/main.py` | **Active** |
| `services/` | Business logic, domain validation, parameterized SQL, transactions | Service / Domain Logic | `services/student_service.py` | **Active** |
| `db/` | PyMySQL connection context managers and DictCursor transaction helpers | Data Access Layer | `db/connection.py` | **Active** |
| `templates/` | Jinja2 HTML templates extending `base.html` | Presentation / View | `templates/students/index.html` | **Active** |
| `static/` | Client assets: CSS (`style.css`), JavaScript (`main.js`), vendor libraries | Frontend Static Assets | `static/js/main.js` | **Active** |
| `tests/` | 24 automated test suites covering 241 test cases with pytest | Quality Assurance | `tests/test_sql_reports.py` | **Active** |
| `docs/` | System architecture guides, explanatory notes, UI screenshots | Documentation | `docs/ARCHITECTURE_EXPLAINED.md` | **Active** |
| `README.md` | Comprehensive project handbook, setup steps, ER model, API guide | Project Documentation | Setup instructions | **Active** |
| `DBMS_CONCEPTS.md` | Theoretical DBMS concepts (Normal Forms, ACID, Transactions, Indexing) | Academic Documentation | Normalization proofs | **Active** |
| `VIVA_QUESTIONS.md` | Curated lab viva questions and examiner answers | Academic Documentation | Viva preparation Q&A | **Active** |
| `RELATIONSHIP_DOCUMENT.md` | ER relationship definitions, cardinalities, participation constraints | Database Design | Relationship matrix | **Active** |
| `DEMO_SCRIPT.md` | Step-by-step viva presentation walkthrough and demo script | Academic Presentation | Live demo guide | **Active** |
| `requirements.txt` | Python package dependencies (`Flask`, `PyMySQL`, `pytest`, etc.) | Dependency Specification | `Flask==3.0.0` | **Active** |
| `.env` | Local environment secrets (MySQL host, user, password, secret key) | Environment Configuration | `MYSQL_PASSWORD=...` | **Active (Local)** |
| `.env.example` | Template for environment configuration without real passwords | Environment Template | Safe variable list | **Active** |
| `.gitignore` | Patterns excluding `.venv`, `__pycache__`, `.env`, test caches from git | Version Control | Rule definitions | **Active** |
| `pyproject.toml` | Linter (`ruff`) and build configuration | Tool Configuration | Linter settings | **Active** |
| `pytest.ini` | Pytest test discovery settings and CLI flags | Test Configuration | `testpaths = tests` | **Active** |
| `.github/workflows/` | GitHub Actions CI workflow running automated tests on commit | CI/CD Pipeline | `ci.yml` | **Active** |
| `archive/` | Historical migration scripts from previous schema iterations | Archived Code | `archive/migrate_internship_rule_v2.py` | **Archived** |
| `migrate_to_7_tables.py` | Standalone migration script that consolidated 20 tables into 7 | Migration Runner | 7-table migration runner | **Leftover (Completed)** |
| `placement_db_backup_20_tables.sql` | Full mysqldump backup taken before dropping obsolete 13 tables | Database Backup | SQL dump of 20 tables | **Leftover (Backup)** |
| `backup_scope_b.sql` | 0-byte empty file created during earlier testing | Leftover Artifact | Empty file | **Leftover (Unused)** |
| `placement_internship_db.sql` | Legacy full schema script from Phase 9 DBMS demo | Legacy Reference | Historical SQL reference | **Legacy (Reference)** |
| `demo_dataset.sql` | Legacy dataset SQL file from Phase 9 | Legacy Reference | Phase 9 demo data | **Legacy (Reference)** |
| `phase9_scope_a_demo.sql` | Legacy Phase 9 scope SQL demo file | Legacy Reference | Phase 9 demo queries | **Legacy (Reference)** |
| `generate_demo_dataset.py` | Script used to generate Phase 9 synthetic data | Legacy Utility | Dataset generator | **Legacy (Utility)** |
| `run_phase9_demo.py` | Script used to execute Phase 9 interactive demo | Legacy Runner | Demo execution script | **Legacy (Runner)** |
| `Legacy_Dataforce_Complete_SQL_Documentation.pdf` | Compiled PDF reference document containing project SQL documentation | Documentation Artifact | Compiled PDF | **Reference** |

---

## PART 4: How the Backend Connects to the Frontend

### Flow A: Opening a Page (Server-Side Rendering)
*Example: User opens the student directory (`GET /students`).*

```text
Browser                      Flask (app.py)               routes/main.py            services/student_service.py     MySQL Database
   |                               |                             |                               |                 |
   |-- 1. GET /students ---------->|                             |                               |                 |
   |                               |-- 2. Match route ---------->|                               |                 |
   |                               |                              |-- 3. list_students(page=1) ->|                 |
   |                               |                              |                               |-- 4. SELECT --->|
   |                               |                              |                               |<-- 5. Rows -----|
   |                               |                              |<-- 6. Returns Dict list ------|                 |
   |                               |<-- 7. render_template() ----|                               |                 |
   |                               |       (Jinja2 merges data)  |                               |                 |
   |<-- 8. Return HTML (200 OK) ---|                             |                               |                 |
```

1. **User Action:** The user clicks "Students" in the sidebar navigation or enters `http://127.0.0.1:5000/students`.
2. **HTTP Request:** The browser sends an HTTP `GET /students` request.
3. **Route Dispatch:** Flask matches the URL to `@main_bp.route("/students")` and calls `students_list()` in `routes/main.py`.
4. **Service Call:** `students_list()` parses query parameters (`page=1`, `branch='CSE'`) and calls `list_students()` in `services/student_service.py`.
5. **Database Execution:** `list_students()` borrows a PyMySQL connection from `get_connection()` and runs:
   ```sql
   SELECT Student_ID, Roll_No, First_Name, Last_Name, Branch, Batch_Year, CGPA, Backlogs, Email
   FROM STUDENT
   WHERE Branch = %s
   ORDER BY Roll_No ASC
   LIMIT %s OFFSET %s;
   ```
6. **Data Return:** MySQL returns matching rows. PyMySQL converts them into a list of Python dictionaries and returns them to `routes/main.py`.
7. **Jinja2 Rendering:** `routes/main.py` calls `render_template("students/index.html", students=students, ...)`. Jinja2 loads `templates/students/index.html`, which extends `templates/base.html`. It iterates over students using `{% for student in students %}`, inserting student data into `<tr>` table rows.
8. **HTTP Response:** Flask sends the completed HTML document (HTTP 200 OK) back to the browser, which renders the table.

---

### Flow B: Submitting a Form (POST with Redirect - PRG Pattern)
*Example: User registers a new student (`POST /students/new`).*

```text
Browser                      Flask (app.py)               routes/main.py            services/student_service.py     MySQL Database
   |                               |                             |                               |                 |
   |-- 1. POST /students/new ----->|                             |                               |                 |
   |      (Form Data + CSRF)       |-- 2. check_csrf_protection()|                               |                 |
   |                               |-- 3. Token valid ---------->|                               |                 |
   |                               |                             |-- 4. create_student(payload)->|                 |
   |                               |                             |                               |-- 5. INSERT --->|
   |                               |                             |                               |<-- 6. Success --|
   |                               |                             |<-- 7. Returns new student ----|                 |
   |                               |                             |-- 8. flash("Success")         |                 |
   |<-- 9. HTTP 302 Redirect ------|<-- redirect('/students/12')-|                               |                 |
   |       to /students/12         |                             |                               |                 |
   |-- 10. GET /students/12 ------>|                             |                               |                 |
   |<-- 11. Render Detail Page ----|                             |                               |                 |
```

1. **User Action:** The user fills in the student registration form on `/students/new` and clicks "Save Student".
2. **HTTP Request:** The browser submits a `POST /students/new` request with form fields and a hidden `<input type="hidden" name="csrf_token" value="...">`.
3. **CSRF Validation:** In `app.py`, `@app.before_request` intercepts the POST request. It calls `verify_csrf_token(token)`. If missing or invalid, it rejects the request with HTTP 400. Because the token matches, execution continues.
4. **Route Processing:** `student_create()` in `routes/main.py` extracts form fields and calls `create_student(payload)` in `services/student_service.py`.
5. **Atomic Service Transaction:**
   - Validates CGPA range and email format.
   - Checks if `Roll_No` already exists.
   - Begins a database transaction via `with get_cursor(commit=True) as cursor:`.
   - Executes `INSERT INTO STUDENT (...) VALUES (%s, ...)`.
   - Executes `INSERT INTO STUDENT_PHONE (...)` and `INSERT INTO STUDENT_SKILL (...)`.
   - Commits the transaction to MySQL.
6. **Flash Message & PRG Pattern:** `student_create()` adds a notification message via `flash("Student registered successfully!", "success")` and returns `redirect(f"/students/{student_id}")` (HTTP 302 Redirect).
7. **Post/Redirect/Get (PRG):** The browser receives the 302 redirect and issues a clean `GET /students/12`. This prevents duplicate form submissions if the user refreshes the page.
8. **Final Display:** Flask renders the student detail page showing a green success banner at the top.

---

### Flow C: JavaScript Without Reload (AJAX Fetch API)
*Example: User runs a custom query in the SQL Reports Console (`POST /api/sql-reports/run-custom`).*

```text
Browser (JS fetch)           routes/main.py               services/sql_report_service.py  db/connection.py           MySQL (Read-Only)
   |                               |                             |                               |                 |
   |-- 1. fetch('/api/.../run') -->|                             |                               |                 |
   |      JSON: {sql: "..."}       |-- 2. api_run_custom_query() |                               |                 |
   |                               |-- 3. validate_custom_sql()->|                               |                 |
   |                               |      (Checks SELECT only)   |-- 4. execute_custom_query() ->|                 |
   |                               |                             |      (Opens read-only conn)   |-- 5. Connect as  |
   |                               |                             |                               |      readonly ->|
   |                               |                             |                               |<-- 6. Connected |
   |                               |                             |-- 7. Execute with 500 limit ------------------->|
   |                               |                             |<-- 8. Return rows & execution time -------------|
   |                               |<-- 9. Dict with results ----|                               |                 |
   |<-- 10. Return JSON -----------|                             |                               |                 |
   |        {columns:[], rows:[]}  |                             |                               |                 |
   |-- 11. JS builds <table> DOM   |                             |                               |                 |
```

1. **User Action:** On `/sql-reports`, the user types `SELECT Roll_No, First_Name, CGPA FROM STUDENT WHERE CGPA >= 9.0;` into the query box and clicks "Execute Query".
2. **Client Event Interception:** The JavaScript event listener intercepts the form submission using `e.preventDefault()`.
3. **AJAX Request:** JavaScript calls `fetch("/api/sql-reports/run-custom", { ... })` with:
   - Method: `POST`
   - Headers: `{"Content-Type": "application/json", "X-CSRFToken": csrfToken}`
   - Body: `JSON.stringify({ sql: userSql })`
4. **Route Dispatch:** Flask routes the request to `api_run_custom_query()` in `routes/main.py`.
5. **Safety Validation:** Calls `validate_custom_sql(raw_sql)` in `services/sql_report_service.py`. It verifies that:
   - The query starts with `SELECT`.
   - It contains no comment markers (`--`, `/*`, `#`).
   - It contains only one statement (no semicolons).
   - Forbidden DDL/DML keywords (`DROP`, `DELETE`, `UPDATE`, `INSERT`) are absent.
6. **Isolated Execution:** Calls `execute_custom_query()`, which invokes `get_readonly_connection()`. PyMySQL connects using the MySQL user `placement_readonly`.
7. **Execution & Timing:** The query runs with an enforced `LIMIT 500` and a 3-second timeout. Python measures execution time using `time.perf_counter()`.
8. **JSON Serialization:** The route returns `jsonify({"status": "success", "columns": [...], "rows": [...], "row_count": 14, "execution_time_ms": 1.42})`.
9. **DOM Update:** The browser's `.then(response => response.json())` callback receives the JSON data and dynamically builds `<thead>` and `<tbody>` HTML table elements, inserting them into `#resultsContainer` with zero page flicker.

---

### Flow D: Interactive Charts (Chart.js Integration)
*Example: Dashboard loads 6 visual placement charts on `/`.*

1. **Page Load:** The user visits `/`. Flask renders `templates/dashboard.html`, which contains 6 HTML5 `<canvas>` elements:
   - `branchwisePlacementChart` (Branch-wise Placement & Offers)
   - `yearwisePlacementChart` (Year-wise Placement Trends)
   - `packageDistributionChart` (Salary Package Distribution)
   - `placementVsInternshipChart` (Placement vs Internship Correlation)
   - `internshipCompletionChart` (Internship Completion Status)
   - `multipleOffersChart` (Students with Multiple Offers)
2. **Asynchronous Fetch:** Once the DOM is ready, JavaScript in `templates/dashboard.html` executes `fetch('/api/analytics/dashboard')`.
3. **Analytics Aggregation:** The route calls functions in `services/dashboard_service.py`:
   - `get_branchwise_analytics_chart_data()`
   - `get_yearwise_placement_chart_data()`
   - `get_package_distribution_chart_data()`
   - `get_placement_vs_internship_chart_data()`
   - `get_internship_completion_chart_data()`
   - `get_multiple_offers_chart_data()`
4. **SQL Aggregations:** The service runs fast relational aggregations (`COUNT(*)`, `AVG(Package)`, `SUM(CASE WHEN ...)` grouped by `Branch`, `Placement_Year`, or `Salary_Band`).
5. **Chart.js Instantiation:** JavaScript receives the JSON response and initializes Chart.js instances:
   ```javascript
   new Chart(document.getElementById('branchwisePlacementChart'), {
       type: 'bar',
       data: {
           labels: data.branchwise.labels,
           datasets: [{
               label: 'Offers',
               data: data.branchwise.offers,
               backgroundColor: '#0d6efd'
           }]
       },
       options: { responsive: true, maintainAspectRatio: false }
   });
   ```
   Chart.js draws responsive vector charts directly onto the `<canvas>` tags.

---

### Flow E: HTML vs. JSON Responses Comparison

| Feature | HTML Response (`render_template`) | JSON Response (`jsonify`) |
| :--- | :--- | :--- |
| **Primary Use Case** | Full page navigation, initial page loading, form display. | Dynamic updates, AJAX fetch calls, Chart.js feeds, SQL console. |
| **Response Content** | Complete HTML markup including `<html>`, `<head>`, Bootstrap layout. | Raw data key-value payload: `{"status": "success", "data": [...]}`. |
| **Page Reload** | Browser triggers a standard page refresh and URL update. | No reload. The page stays intact while JavaScript updates DOM elements. |
| **Client Requirement**| Works in any browser, even if JavaScript is disabled. | Requires JavaScript to parse the JSON and update the user interface. |
| **Flask Method** | `return render_template("students/index.html", ...)` | `return jsonify({"success": True, "count": 10})` |
| **Example Route** | `GET /students` (Displays student directory) | `POST /api/sql-reports/run-custom` (Returns query result rows) |

---

### Flow F: What the User Sees on Errors

1. **Database Server Down / Connection Error:**  
   - *What Happens Behind the Scenes:* PyMySQL raises `pymysql.err.OperationalError` (Cannot connect to MySQL server). `db/connection.py` catches it and raises `DatabaseError`.
   - *What the User Sees:* The global error handler `@app.errorhandler(DatabaseError)` in `app.py` catches the exception. Instead of crashing, it renders `templates/errors/500.html` with a clear message:  
     *"Database Connection Unavailable: The application cannot connect to the MySQL database engine. Please verify the database server is running."*
2. **Validation Error (e.g., Invalid CGPA or Duplicate Roll Number):**  
   - *What Happens Behind the Scenes:* `services/student_service.py` detects CGPA > 10.0 or a duplicate roll number and raises `ValidationError` or `ConflictError`.
   - *What the User Sees:* The route catches the error and uses Flask's `flash()` function. The page re-renders with a red Bootstrap alert banner:  
     *"Registration Error: A student with Roll_No 'CS202101' already exists."*  
     The user's previously entered form values are preserved so they do not have to retype them.
3. **404 Not Found:**  
   - *What Happens Behind the Scenes:* User requests a non-existent URL (e.g., `/students/99999` or `/unknown-page`).
   - *What the User Sees:* `@app.errorhandler(404)` renders `templates/errors/404.html` showing a clean "404 - Page Not Found" screen with a button to return to the Dashboard.
4. **500 Internal Server Error:**  
   - *What Happens Behind the Scenes:* An unexpected exception occurs in code.
   - *What the User Sees:* `@app.errorhandler(500)` logs the complete technical traceback to server log files for debugging, but displays a safe, generic error screen to the user. Database passwords, internal directory paths, and SQL queries are **never** leaked to the browser.

---

## PART 5: Viva Scripts & Examiner Preparation

### Script 1: "Explain your backend architecture in 1 minute"
> *"Our project follows an industry-standard **Layered (N-Tier) Architecture** built on Python and Flask, with strict separation of concerns across four layers:*
>
> 1. *First is **app.py**, the application factory. It handles HTTP middleware, registers modular route blueprints, validates CSRF tokens, and injects OWASP security headers.*
> 2. *Second is the **routes layer**, which acts as the HTTP controller. It receives requests, extracts parameters, and delegates work to the services layer without containing any business rules or SQL.*
> 3. *Third is the **services layer**, which encapsulates all domain logic, input validation, and business constraints—such as ensuring a student joins at most one placement offer. All SQL queries are written here using parameterized `%s` placeholders inside atomic database transactions.*
> 4. *Fourth is the **data access layer (db/connection.py)**, which manages PyMySQL connections and provides a dedicated read-only connection for our SQL reports console.*
>
> *This backend connects to a MySQL database structured in **exactly 7 canonical tables and 2 views**, fully normalized to Boyce-Codd Normal Form with intentional curriculum denormalization in the Internship entity."*

---

### Script 2: "How do you connect backend and frontend in 1 minute?"
> *"We connect our Flask backend to the frontend using two distinct communication patterns:*
>
> 1. *The first pattern is **Server-Side Rendering (SSR)** for standard page navigation. When an administrator navigates to `/students`, Flask routes the request to `routes/main.py`, which fetches student records via `services/student_service.py`. Flask then passes those records to **Jinja2 templates**, which render complete HTML pages extending our master `base.html` template. For form submissions, we follow the **Post/Redirect/Get (PRG)** pattern with CSRF validation and flash messages to prevent duplicate submissions on page refresh.*
> 2. *The second pattern is **Asynchronous Client-Side Communication (AJAX)** using the JavaScript **Fetch API**. For interactive features—like our real-time analytics dashboard and the custom SQL console—the browser sends an asynchronous `POST` request with JSON data and an `X-CSRFToken` header. The backend executes the request and returns a lightweight JSON payload. JavaScript parses this JSON and dynamically updates the DOM or renders charts via **Chart.js** without reloading the page.*
>
> *This hybrid approach gives us fast initial page loads, bookmarkable URLs, and dynamic interactivity where needed."*

---

### 10 Likely Viva Questions and Examiner-Grade Answers

#### Q1: Why did you separate routes and services instead of writing SQL queries directly inside routes?
**Answer:**  
Separating routes and services adheres to the **Single Responsibility Principle**. Routes act solely as HTTP controllers—parsing web requests, HTTP headers, and URL parameters. Services contain the core business logic, domain validations, and SQL queries. This separation ensures business logic can be independently unit tested with pytest without needing an active HTTP web server, prevents code duplication, and makes the application maintainable.

#### Q2: How does your application prevent SQL Injection attacks?
**Answer:**  
We prevent SQL injection through **100% Parameterized Prepared Statements** using PyMySQL `%s` placeholders. We never use Python f-strings, string formatting (`%`), or concatenation (`+`) to build queries. When `%s` is used, the SQL query text and the user values are transmitted to MySQL as separate protocol packets. MySQL treats user values strictly as literal data, making it impossible for input containing quotes or `OR 1=1` to alter query structure.

#### Q3: What is CSRF and how did you prevent it?
**Answer:**  
Cross-Site Request Forgery (CSRF) is an attack where a malicious third-party website tricks an authenticated user's browser into performing unwanted actions on our server. We prevent this using the **Synchronizer Token Pattern**. On every session, Flask generates a unique, cryptographically random CSRF token stored in the server session. Every HTML form embeds this token in a hidden `<input name="csrf_token">` field, and AJAX requests include it in an `X-CSRFToken` header. In `app.py`, `@app.before_request` intercepts all state-changing HTTP methods (`POST`, `PUT`, `DELETE`) and verifies the token. If the token is missing or forged, the request is rejected immediately.

#### Q4: Why do you have a dedicated read-only MySQL user in addition to the root/admin user?
**Answer:**  
This implements the security principle of **Least Privilege** and **Defense-in-Depth**. In our SQL Reports page, administrators can write and execute ad-hoc SQL queries. While our service layer validates that queries start with `SELECT`, application-level regex checks can theoretically have edge-case bypasses. By executing custom queries through a separate connection authenticated as `placement_readonly`, the MySQL database engine itself guarantees that even if a `DROP TABLE` or `DELETE` statement reaches the database, MySQL rejects it with an access violation error.

#### Q5: What is the Post/Redirect/Get (PRG) pattern and why is it used?
**Answer:**  
PRG is a web development design pattern. When a user submits a form (`POST`), rather than returning HTML directly from the POST handler, the server responds with an HTTP 302 Redirect to a `GET` URL (e.g., `redirect('/students/12')`). This ensures that if the user refreshes the page or presses the browser back button, the browser issues a harmless `GET` request rather than resubmitting the `POST` request, preventing accidental duplicate database inserts.

#### Q6: How does Flask pass data into Jinja2 templates?
**Answer:**  
Flask passes data into Jinja2 templates via keyword arguments in the `render_template()` function—for example, `render_template('students/index.html', students=students_list, total=total_count)`. Jinja2 receives these variables as template context. Inside the template, double curly braces `{{ student.Roll_No }}` output variable values, while control tags `{% for student in students %}` and `{% if student.CGPA >= 9.0 %}` dynamically control HTML generation on the server before the page is transmitted.

#### Q7: How does Chart.js get data from MySQL?
**Answer:**  
Chart.js cannot connect directly to MySQL because it runs in the client browser. Instead, when the dashboard HTML page loads, a client-side JavaScript script calls `fetch('/api/analytics/dashboard')`. This Flask endpoint invokes `services/dashboard_service.py`, which executes SQL aggregation queries (`COUNT(*)`, `AVG(Package)` grouped by department or year). The service formats the data into label arrays and numeric data arrays, and Flask returns them as JSON. The JavaScript callback receives the JSON and passes it into `new Chart(ctx, { data: { labels: [...], datasets: [...] } })` to draw the chart on the canvas.

#### Q8: Why does the database have 7 tables now instead of 20?
**Answer:**  
The earlier 20-table schema contained redundant entity tables (like separate tables for `UNIVERSITY`, `COURSE`, `STUDENT_PROFILE`, `RESUME`, `SEMESTER_RESULT`, `OPPORTUNITY`, and `SELECTION_PROCESS`) that complicated queries with excessive joins and maintained overlapping attributes. By consolidating into the approved **canonical 7-table schema** (`STUDENT`, `STUDENT_PHONE`, `STUDENT_SKILL`, `COMPANY`, `PLACEMENT`, `PLACEMENT_SKILL`, `INTERNSHIP`), we aligned the implementation directly with our approved Entity-Relationship diagram, reduced foreign key overhead, improved query performance, and enforced all academic rules cleanly using table CHECK constraints and database views.

#### Q9: What Normal Form are your database tables in?
**Answer:**  
Six of our seven tables (`STUDENT`, `STUDENT_PHONE`, `STUDENT_SKILL`, `COMPANY`, `PLACEMENT`, `PLACEMENT_SKILL`) are in **Boyce-Codd Normal Form (BCNF)**. They have no composite or multivalued attributes (1NF), no partial dependencies on composite keys (2NF), and every non-trivial functional dependency $X \rightarrow Y$ has $X$ as a superkey (3NF and BCNF).  
Our seventh table, **`INTERNSHIP`**, is in **1NF (intentional curriculum denormalization)**. Because the curriculum mandates that Internship 1 requires 4 credits in Semester 5 and Internship 2 requires 4 credits in Semester 8, there exists a functional dependency `Internship_No -> {Internship_Type, Credits, Report_Semester}`. Because `Internship_No` is only part of the composite primary key `(Student_ID, Internship_No)`, this is a 2NF violation. We intentionally chose this denormalization to keep the design strictly within 7 tables while enforcing the curriculum milestone via a `CHECK` constraint (`chk_internship_curriculum`), avoiding the overhead of creating an 8th table.

#### Q10: How do database transactions protect data integrity in your application?
**Answer:**  
Database transactions ensure the **ACID properties** (Atomicity, Consistency, Isolation, Durability). For multi-table operations—such as creating a student along with their multivalued phone numbers and skills—we wrap the operations inside `with get_cursor(commit=True) as cursor:`. If inserting into `STUDENT` succeeds but inserting a phone number into `STUDENT_PHONE` fails, an exception is raised, and the context manager immediately executes `connection.rollback()`. This guarantees **Atomicity**: either the student and all their phone numbers and skills are saved together, or no partial records are left in the database.

---

## Technical Notes & Subtleties in the Codebase

1. **Active Schema vs. Historical Files:**  
   The active running application uses **strictly 7 tables and 2 views**. However, several historical files from earlier development phases remain in the repository for reference:
   - `phase9_scope_a_demo.sql`, `demo_dataset.sql`, `generate_demo_dataset.py`, and `run_phase9_demo.py` were part of the initial Phase 9 DBMS demonstration.
   - `placement_db_backup_20_tables.sql` is a safety backup taken before dropping obsolete tables.
   - `archive/migrate_internship_rule_v2.py` is an archived migration script.  
   *None of these legacy files are imported or executed by the running Flask application.*
2. **Placed Definition Consistency:**  
   Throughout the application, a student is strictly considered **"Placed"** if and only if they have a placement offer where `Joined = 'Yes'`. Offers with `Offer_Status = 'Accepted'` but `Joined = 'No'` represent accepted offers that have not yet resulted in joining. This is enforced at the database level by generated column `Joined_Student` and unique key `uq_one_joined_offer`.
3. **Internship 2 Curriculum Rule:**  
   In compliance with university curriculum regulations, Internship 2 is completed during the 8th semester, with the internship report submitted after the end of the 8th semester (`Report_Semester = 8`, 4 credits, Mandatory). This is enforced by MySQL check constraint `chk_internship_curriculum` and validated in `services/internship_service.py`.

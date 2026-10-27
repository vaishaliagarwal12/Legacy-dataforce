# Campus Placement & Internship Management System (Legacy Dataforce)

An enterprise-grade, relational database-driven **Campus Placement and Academic Internship Management System** designed for engineering institutions. Built with **Flask 3.1**, **MySQL 8.0 (InnoDB)**, and modern **Bootstrap 5 / Chart.js** responsive dashboards, the system enforces academic rules, recruitment pipelines, multi-offer tracking, and relational integrity constraints.

---

## 📌 Table of Contents

- [Key Highlights & Architecture](#-key-highlights--architecture)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Database Initialization & Seeding](#-database-initialization--seeding)
- [Running the Application](#-running-the-application)
- [Running Automated Tests](#-running-automated-tests)
- [Core Business Rules Enforced](#-core-business-rules-enforced)
- [REST API Reference](#-rest-api-reference)
- [Directory Structure](#-directory-structure)
- [Project Documentation Map](#-project-documentation-map)

---

## 🚀 Key Highlights & Architecture

1. **Strict Relational Design (BCNF / 3NF)**:
   - Atomic attributes decomposed for 1NF (e.g., student name decomposed into `First_Name` and `Last_Name`; multi-valued contact numbers and skills isolated into child relation tables `STUDENT_PHONE` and `STUDENT_SKILL`).
   - Weak entity relationships for `INTERNSHIP` and `SELECTION_PROCESS`.
   - Comprehensive composite primary and candidate keys across intersection tables.
2. **Institutional Rule Enforcement**:
   - **The Single-Accepted-Offer Rule**: A student may receive and hold multiple concurrent placement offers in `"Offered"` status, but institutional policy strictly limits each student to **at most ONE `"Accepted"` or `"Joined"` offer**.
   - **Mandatory vs. Additional Internships**: Enforces academic curriculum requirements where Mandatory Summer Internships require dynamic prerequisite SGPA verification from prior semesters.
   - **Referential Action Policies**: Strict `ON DELETE RESTRICT` protects recruiting partner audit records, while `ON DELETE CASCADE` purges dependent student attributes cleanly upon graduation or deregistration.
3. **Advanced Analytics & Accreditation Reports**:
   - Executive dashboard with Chart.js visualization.
   - High-performance SQL queries utilizing Common Table Expressions (CTEs), Window Functions (`ROW_NUMBER()`, `RANK()`, `AVG() OVER()`), and multi-table joins for NIRF/NAAC accreditation audits.

---

## 🛠 Tech Stack

- **Backend Framework**: Python 3.10+ / Flask 3.1.2
- **Relational Database**: MySQL 8.0+ (InnoDB Storage Engine)
- **Database Driver**: PyMySQL 1.2.3 with native parameter binding (`%s`)
- **Frontend / UI**: Jinja2 Templates, Bootstrap 5.3, Bootstrap Icons, Chart.js 4.4
- **Testing Framework**: pytest 8.3.3 & unittest (113 comprehensive tests)

---

## 📋 Prerequisites

Before setting up the project, ensure you have the following installed:

1. **Python 3.10, 3.11, 3.12, or 3.13** ([python.org](https://www.python.org/))
2. **MySQL Server 8.0+** ([mysql.com](https://dev.mysql.com/downloads/mysql/)) running locally on port `3306`
3. **Git** (optional, for version control)

---

## ⚙️ Installation & Setup

### 1. Clone or Open the Workspace

Open your terminal or PowerShell and navigate to the project root:

```bash
cd "d:/Legacy dataforce"
```

### 2. Configure Environment Variables (`.env`)

Verify or create the `.env` file in the project root directory. An example configuration is provided:

```ini
# Server Configuration
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev_legacy_dataforce_secret_key_2026
PORT=5000

# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=12345
MYSQL_DB=placement_db
MYSQL_CHARSET=utf8mb4
MYSQL_CONNECT_TIMEOUT=5
```

> **Note**: Update `MYSQL_PASSWORD` and `MYSQL_USER` to match your local MySQL server credentials.

### 3. Install Python Dependencies

Install the required packages from `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

Verify installed packages:
```bash
python -m pip list
```

---

## 🗄 Database Initialization & Seeding

The system includes an automated initialization script (`init_mysql.py`) that executes DDL schema generation and populates realistic institutional seed data (`seed.sql`).

### 1. Create the Database in MySQL (if not already existing)

Log in to your MySQL terminal or workbench:

```sql
CREATE DATABASE IF NOT EXISTS placement_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Run the Initialization Script

Execute the automated database builder:

```bash
python init_mysql.py
```

**What this does**:
- Drops old tables in safe reverse-dependency order.
- Generates 16 relational InnoDB tables with CHECK constraints, foreign keys, and indexes.
- Populates seed data: 1 university, 12 courses, 10 students, 30+ semester results, 8 companies, 10 recruitment drives, 12 opportunities, 20+ placement offers, and mandatory internship records.

---

## 🖥 Running the Application

Launch the Flask development server:

```bash
python app.py
```

The application will start on:
👉 **[http://localhost:5000](http://localhost:5000)**

### Key Accessible Web Views:
- **Executive Dashboard**: `http://localhost:5000/`
- **Student Career Profiles**: `http://localhost:5000/students`
- **Register New Student**: `http://localhost:5000/students/new`
- **Recruiting Partners**: `http://localhost:5000/companies`
- **Placement Offers & Outcomes**: `http://localhost:5000/placements`
- **Internships & Compliance**: `http://localhost:5000/internships`
- **Institutional Reports**: `http://localhost:5000/reports`
- **System Health Diagnostics**: `http://localhost:5000/health`

---

## 🧪 Running Automated Tests

The system features **113 automated unit, integration, and rule verification tests** across 8 test suites.

### Run All Tests:

```bash
python -m pytest
```

### Run Phase 10 Tests Specifically:

```bash
# 1. Database Rules: Constraints, Uniqueness, Cascades, and One-Accepted-Offer Rule
python -m pytest tests/test_phase10_db_rules.py -v

# 2. Key API and UI Routes
python -m pytest tests/test_phase10_key_routes.py -v
```

### Run by Specific Phase or Feature:

```bash
python -m pytest tests/test_health.py        # System health & ping
python -m pytest tests/test_phase4.py        # Students, courses, profiles
python -m pytest tests/test_phase5.py        # Companies, drives, opportunities
python -m pytest tests/test_phase6.py        # Placement offers & status updates
python -m pytest tests/test_phase7.py        # Academic internships & requirements
python -m pytest tests/test_phase8.py        # Frontend views & forms
python -m pytest tests/test_phase9.py        # SQL analytics, CTEs, window functions
```

**Expected Result**: `113 passed in ~30s` with **0 failures**.

---

## ⚖️ Core Business Rules Enforced

1. **The Single-Accepted-Offer Rule**:
   - A student can receive multiple offers (Offer_Status = `'Offered'`) without conflict.
   - When an offer is marked `'Accepted'` or `'Joined'`, the system blocks any other offer from being accepted (`HTTP 409 Conflict`).
   - The student must explicitly decline their accepted offer before accepting another.
2. **Opportunity Type Consistency**:
   - Placement offers can only be issued for opportunities of type `'Placement'` (cannot issue a placement offer for an `'Internship'` role).
3. **Internship Chronological & Prerequisite Rules**:
   - `chk_internship_dates`: `End_Date >= Start_Date`.
   - Mandatory internships require verification against curriculum `INTERNSHIP_REQUIREMENT` and prerequisite semester SGPA thresholds.
4. **Duplicate Offer Blocking**:
   - A student cannot be issued duplicate offers for the exact same recruitment opportunity.
5. **Referential Integrity & Cascades**:
   - `ON DELETE RESTRICT` on `COMPANY` prevents accidental deletion of corporate partners with active recruitment drives or placed students.
   - `ON DELETE CASCADE` cleanly purges child phone numbers, skills, and student profiles when a student entity is removed.

---

## 📡 REST API Reference

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/health` | `GET` | System health, DB connection state, MySQL version, query latency |
| `/api/students` | `GET` | List/search students (supports `branch`, `min_cgpa`, `search`, pagination) |
| `/api/students` | `POST` | Register a new student with multivalued phones |
| `/api/students/<id>` | `GET` | Get full student details (courses, profiles, skills, placement status) |
| `/api/students/<id>` | `PUT` | Update student profile fields |
| `/api/students/<id>` | `DELETE`| Delete student (blocks if placement/internship records exist) |
| `/api/students/<id>/phones` | `GET` | List student contact numbers |
| `/api/students/<id>/phones` | `POST` | Add contact number to student |
| `/api/courses` | `GET` | List academic catalog courses |
| `/api/companies` | `GET` | List recruiting organizations with filters |
| `/api/companies` | `POST` | Register new corporate recruiting partner |
| `/api/companies/<id>` | `GET` | Hierarchical company detail with drives & opportunities |
| `/api/drives` | `GET` | List campus recruitment drives |
| `/api/opportunities` | `GET` | List open job & internship opportunities |
| `/api/placements` | `GET` | List placement offers (filters by `package`, `status`, `year`) |
| `/api/placements` | `POST` | Issue placement offer (enforces duplicate & type rules) |
| `/api/placements/<id>/status` | `PATCH`| Update offer status (`Accepted`, `Declined`, `Joined`) |
| `/api/placements/analytics/multiple-offers` | `GET` | Analytical query for students holding 2+ offers |
| `/api/placements/analytics/distribution` | `GET` | Statistical breakdown of 0, 1, and multiple offer holders |
| `/api/internships` | `GET` | List student internships |
| `/api/internships/requirements` | `GET` | Curriculum mandatory internship guidelines |
| `/api/semester-results` | `GET` | Official verified semester result ledger |

---

## 📁 Directory Structure

```
Legacy dataforce/
├── app.py                     # Flask application factory and route registration
├── config.py                  # Environment-driven database and app settings
├── requirements.txt           # Python package dependencies
├── init_mysql.py              # Automated MySQL DDL execution & seed runner
├── schema.sql                 # Canonical Relational DDL Schema
├── seed.sql                   # Realistic institutional test datasets
├── .env                       # Local environment configuration
├── db/                        # Database connection pool & query execution engine
│   ├── __init__.py
│   └── connection.py          # Context managers, parameterized execution & error mapping
├── services/                  # Business logic services & domain rules
│   ├── student_service.py     # Student master, phones, profiles
│   ├── company_service.py     # Company master & hierarchical details
│   ├── drive_service.py       # Recruitment drives & schedule
│   ├── opportunity_service.py # Roles, eligibility criteria & packages
│   ├── placement_service.py   # Offers, single-acceptance rule, multi-offer queries
│   ├── internship_service.py  # Mandatory/additional internships & prerequisite SGPA joins
│   ├── semester_result_service.py # Verified academic results & SGPA audits
│   └── dashboard_service.py   # Analytics, CTEs, accreditation queries
├── routes/                    # REST API & Web UI controllers
│   ├── main.py                # Web view controllers (Dashboard, Students, Placements, etc.)
│   ├── students.py            # Student REST API
│   ├── companies.py           # Company REST API
│   ├── placements.py          # Placement offers REST API
│   ├── internships.py         # Internships REST API
│   └── health.py              # Health check endpoint
├── templates/                 # Responsive Jinja2 Bootstrap HTML templates
│   ├── base.html              # Master layout with navbar and flash messages
│   ├── dashboard.html         # Executive KPI dashboard with Chart.js
│   ├── students/              # Student directory and registration forms
│   ├── companies/             # Partner catalog and detail views
│   ├── placements/            # Placement offer tracking & status update modals
│   ├── internships/           # Internship records & compliance tabs
│   └── reports/               # Institutional NIRF/NAAC audit reports
├── static/                    # CSS stylesheets and client-side JavaScript
└── tests/                     # Automated test suites (113 tests)
    ├── test_health.py         # Health endpoint & DB ping
    ├── test_phase4.py         # Students, courses, profiles
    ├── test_phase5.py         # Companies, drives, opportunities
    ├── test_phase6.py         # Placement offers & one-accepted rule
    ├── test_phase7.py         # Academic internships & prerequisites
    ├── test_phase8.py         # Frontend web views
    ├── test_phase9.py         # Analytical SQL queries & CTEs
    ├── test_phase10_db_rules.py   # DB constraints, uniqueness, cascades & offer rule
    └── test_phase10_key_routes.py # Key API & Web UI routes
```

---

## 📚 Project Documentation Map

Comprehensive academic and technical companion documents prepared for presentation and evaluation:

1. **[RELATIONSHIP_DOCUMENT.md](file:///d:/Legacy%20dataforce/RELATIONSHIP_DOCUMENT.md)**: Full Entity-Relationship catalog, foreign keys, cardinality mappings (1:1, 1:N, M:N), cascading policies, and Mermaid ER diagram.
2. **[DBMS_CONCEPTS.md](file:///d:/Legacy%20dataforce/DBMS_CONCEPTS.md)**: Detailed DBMS theory guide covering Normalization (1NF to BCNF proofs), Keys, SQL Joins, ACID Transactions, and B-Tree Indexing strategies with concrete code examples from this project.
3. **[DEMO_SCRIPT.md](file:///d:/Legacy%20dataforce/DEMO_SCRIPT.md)**: Step-by-step 5-minute live presentation guide with click-by-click instructions, query demonstrations, and rule enforcement highlights.
4. **[VIVA_QUESTIONS.md](file:///d:/Legacy%20dataforce/VIVA_QUESTIONS.md)**: Top 10 viva voce questions most likely to be asked by professors with sharp, technically rigorous answers.

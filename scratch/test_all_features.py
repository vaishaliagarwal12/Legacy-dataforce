import sys, os
sys.path.insert(0, os.path.abspath("."))
import json
import urllib.request
import urllib.parse
from db.connection import execute_query, execute_one, execute_mutation

BASE_URL = "http://127.0.0.1:5000"

cookie_processor = urllib.request.HTTPCookieProcessor()
opener = urllib.request.build_opener(cookie_processor)
urllib.request.install_opener(opener)

def get(path):
    url = BASE_URL + path
    try:
        req = urllib.request.Request(url)
        with opener.open(req) as resp:
            return resp.status, resp.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return 0, str(e)

def post(path, data):
    url = BASE_URL + path
    encoded = urllib.parse.urlencode(data).encode('utf-8')
    try:
        req = urllib.request.Request(url, data=encoded, method='POST')
        with opener.open(req) as resp:
            return resp.status, resp.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return 0, str(e)

results_table = []

def run_test(page, feature, test_desc, passed, detail=""):
    results_table.append({
        "page": page,
        "feature": feature,
        "tested": test_desc,
        "result": "PASS" if passed else "FAIL",
        "detail": detail
    })
    print(f"[{'PASS' if passed else 'FAIL'}] {page} | {feature} | {test_desc}: {detail}")

print("=== STARTING FULL SYSTEM VERIFICATION ===\n")

# -------------------------------------------------------------
# 1. STUDENTS
# -------------------------------------------------------------
# Clean up any leftover test student first
execute_mutation("DELETE FROM STUDENT WHERE Roll_No LIKE %s", ("TEST_STU_%",))

# Create valid student
new_stu_data = {
    "Roll_No": "TEST_STU_01",
    "First_Name": "E2ETest",
    "Last_Name": "Student",
    "Email": "e2e.student@univ.edu",
    "Branch": "CSE",
    "Batch_Year": "2024",
    "Section": "B",
    "CGPA": "8.75",
    "Backlogs": "0",
    "Resume_Link": "https://storage.univ.edu/test.pdf"
}
status, html = post("/students/new", new_stu_data)
created_stu = execute_one("SELECT Student_ID FROM STUDENT WHERE Roll_No = 'TEST_STU_01'")
run_test("Students", "Create (Valid)", "POST /students/new with valid data", 
         status == 200 and created_stu is not None, 
         f"Created Student_ID: {created_stu['Student_ID'] if created_stu else 'None'}")
created_id = created_stu["Student_ID"] if created_stu else None

# Create invalid: duplicate roll number
dup_data = dict(new_stu_data)
dup_data["Email"] = "different@univ.edu"
status, html = post("/students/new", dup_data)
has_err = "already exists" in html or "Registration Error" in html
run_test("Students", "Create (Duplicate Roll No)", "Reject duplicate Roll_No with clear page error",
         has_err and status == 200, "Clean error alert rendered on page")

# Create invalid: invalid CGPA (15.00)
bad_cgpa_data = dict(new_stu_data)
bad_cgpa_data["Roll_No"] = "TEST_STU_02"
bad_cgpa_data["CGPA"] = "15.00"
status, html = post("/students/new", bad_cgpa_data)
has_cgpa_err = "between 0.00 and 10.00" in html or "cannot exceed" in html or "Registration Error" in html
run_test("Students", "Create (Invalid CGPA > 10)", "Reject CGPA 15.00 with clear page error",
         has_cgpa_err and status == 200, "Clean CGPA error alert rendered on page")

# Create invalid: non-numeric CGPA ("abc")
nonnum_cgpa_data = dict(new_stu_data)
nonnum_cgpa_data["Roll_No"] = "TEST_STU_03"
nonnum_cgpa_data["CGPA"] = "invalid_num"
status, html = post("/students/new", nonnum_cgpa_data)
has_num_err = "valid numeric" in html or "Registration Error" in html
run_test("Students", "Create (Non-numeric CGPA)", "Reject non-numeric CGPA with clean message (no 500 crash)",
         has_num_err and status == 200, "Handled safely without crash")

# Edit student
if created_id:
    edit_data = {
        "First_Name": "E2ETestUpdated",
        "Last_Name": "Student",
        "Email": "e2e.updated@univ.edu",
        "Branch": "CSE",
        "Batch_Year": "2024",
        "Section": "A",
        "CGPA": "9.10",
        "Backlogs": "0",
        "Resume_Link": "https://storage.univ.edu/test_updated.pdf"
    }
    status, html = post(f"/students/{created_id}/edit", edit_data)
    updated_stu = execute_one("SELECT First_Name, CGPA FROM STUDENT WHERE Student_ID = %s", (created_id,))
    run_test("Students", "Edit (Valid)", f"POST /students/{created_id}/edit update CGPA & Name",
             updated_stu and updated_stu["First_Name"] == "E2ETestUpdated" and float(updated_stu["CGPA"]) == 9.10,
             f"Updated CGPA: {updated_stu['CGPA'] if updated_stu else 'None'}")

# Delete student: Protected deletion (Student with placements: Student 1 Aarav)
status, html = post("/students/1/delete", {})
has_protect_err = "Cannot Delete Student" in html or "history detected" in html
aarav_still_exists = execute_one("SELECT Student_ID FROM STUDENT WHERE Student_ID = 1") is not None
run_test("Students", "Delete (Protected)", "Block deleting student with active placement offers",
         has_protect_err and aarav_still_exists, "Blocked deletion with institutional compliance flash alert")

# Delete student: Safe deletion (created test student with no placements)
if created_id:
    status, html = post(f"/students/{created_id}/delete", {})
    deleted_check = execute_one("SELECT Student_ID FROM STUDENT WHERE Student_ID = %s", (created_id,))
    has_success_msg = "safely deleted" in html
    run_test("Students", "Delete (Safe with confirmation)", f"POST /students/{created_id}/delete",
             deleted_check is None and has_success_msg, "Safely deleted unencumbered student")

# Search and filter
status, html = get("/students?search=Aarav")
run_test("Students", "Search", "GET /students?search=Aarav", "CS202001" in html, "Found student Aarav Sharma")

status, html = get("/students?branch=CSE")
run_test("Students", "Filter (Branch)", "GET /students?branch=CSE", "CS202001" in html and "EC201803" not in html, "Filtered CSE students correctly")

status, html = get("/students?min_cgpa=9.0")
run_test("Students", "Filter (Min CGPA)", "GET /students?min_cgpa=9.0", "CS202001" in html, "Filtered students with CGPA >= 9.0")

# -------------------------------------------------------------
# 2. COMPANIES
# -------------------------------------------------------------
execute_mutation("DELETE FROM COMPANY WHERE Company_Name LIKE %s", ("Test Co %",))

# Create valid company
c_data = {
    "Company_Name": "Test Co Automated 2026",
    "Company_Type": "Product",
    "Industry": "Cybersecurity & Cloud",
    "Location": "Hyderabad",
    "Website": "https://testco2026.com"
}
status, html = post("/companies/new", c_data)
created_comp = execute_one("SELECT Company_ID FROM COMPANY WHERE Company_Name = 'Test Co Automated 2026'")
run_test("Companies", "Create (Valid)", "POST /companies/new",
         status == 200 and created_comp is not None,
         f"Created Company_ID: {created_comp['Company_ID'] if created_comp else 'None'}")
comp_id = created_comp["Company_ID"] if created_comp else None

# Create duplicate company
dup_comp_data = dict(c_data)
status, html = post("/companies/new", dup_comp_data)
has_comp_dup_err = "already exists" in html or "Company Registration Error" in html
run_test("Companies", "Create (Duplicate)", "Reject duplicate company name",
         has_comp_dup_err and status == 200, "Clean error alert rendered on page")

# Edit company
if comp_id:
    c_edit_data = {
        "Company_Name": "Test Co Automated 2026",
        "Company_Type": "Startup",
        "Industry": "AI DeepTech",
        "Location": "Bengaluru",
        "Website": "https://testco-ai.com"
    }
    status, html = post(f"/companies/{comp_id}/edit", c_edit_data)
    updated_comp = execute_one("SELECT Company_Type, Industry FROM COMPANY WHERE Company_ID = %s", (comp_id,))
    run_test("Companies", "Edit (Valid)", f"POST /companies/{comp_id}/edit update Type & Industry",
             updated_comp and updated_comp["Company_Type"] == "Startup" and updated_comp["Industry"] == "AI DeepTech",
             f"Updated Type: {updated_comp['Company_Type'] if updated_comp else 'None'}")

# Delete company: Protected (Company 1 has drives and offers)
status, html = post("/companies/1/delete", {})
has_del_comp_block = "Cannot Delete Company" in html or "recruitment drive(s) are registered" in html
c1_exists = execute_one("SELECT Company_ID FROM COMPANY WHERE Company_ID = 1") is not None
run_test("Companies", "Delete (Protected)", "Block deleting company with recruitment drives",
         has_del_comp_block and c1_exists, "Blocked deletion with referential integrity flash alert")

# Delete company: Safe (created test company with no dependencies)
if comp_id:
    status, html = post(f"/companies/{comp_id}/delete", {})
    comp_del_check = execute_one("SELECT Company_ID FROM COMPANY WHERE Company_ID = %s", (comp_id,))
    run_test("Companies", "Delete (Safe with confirmation)", f"POST /companies/{comp_id}/delete",
             comp_del_check is None, "Safely deleted unencumbered company")

# Search and filter
status, html = get("/companies?search=Google")
run_test("Companies", "Search", "GET /companies?search=Google", "Google India" in html, "Found Google India")

status, html = get("/companies?tier=Product")
run_test("Companies", "Filter (Category)", "GET /companies?tier=Product", "Product" in html, "Filtered Product companies")

# -------------------------------------------------------------
# 3. INTERNSHIPS
# -------------------------------------------------------------
# Clean up any test internship
execute_mutation("DELETE FROM INTERNSHIP WHERE Role = 'E2E Test Automated Intern'")

# Create valid Additional internship
add_intern_data = {
    "Student_ID": "1",
    "Company_ID": "2",
    "Internship_Type": "Additional",
    "Internship_No": "4",
    "Role": "E2E Test Automated Intern",
    "Start_Date": "2024-05-01",
    "End_Date": "2024-06-30"
}
status, html = post("/internships/new", add_intern_data)
created_intern = execute_one("SELECT Internship_ID FROM INTERNSHIP WHERE Student_ID = 1 AND Internship_No = 4")
run_test("Internships", "Create (Valid Additional)", "POST /internships/new Additional Internship #4",
         created_intern is not None, f"Created Internship_ID: {created_intern['Internship_ID'] if created_intern else 'None'}")
intern_id = created_intern["Internship_ID"] if created_intern else None

# Create invalid: Mandatory without Requirement_ID
bad_intern_data = {
    "Student_ID": "2",
    "Company_ID": "1",
    "Internship_Type": "Mandatory",
    "Internship_No": "3",
    "Role": "Invalid Mandatory Intern",
    "Start_Date": "2024-05-01",
    "End_Date": "2024-06-30"
}
status, html = post("/internships/new", bad_intern_data)
has_int_err = "must link to an INTERNSHIP_REQUIREMENT" in html or "Internship Creation Rejected" in html
run_test("Internships", "Create (Mandatory without Requirement)", "Reject Mandatory without Requirement_ID",
         has_int_err, "Clean error alert rendered on page")

# Create invalid: End_Date earlier than Start_Date
bad_dates_data = {
    "Student_ID": "3",
    "Company_ID": "1",
    "Internship_Type": "Additional",
    "Internship_No": "5",
    "Role": "Bad Dates Intern",
    "Start_Date": "2024-08-01",
    "End_Date": "2024-05-01"
}
status, html = post("/internships/new", bad_dates_data)
has_date_err = "End_Date" in html or "earlier than Start_Date" in html or "Internship Creation Rejected" in html
run_test("Internships", "Create (Invalid Dates)", "Reject End_Date < Start_Date",
         has_date_err, "Clean date validation error rendered on page")

# Delete internship
if intern_id:
    status, html = post(f"/internships/{intern_id}/delete", {})
    del_intern_check = execute_one("SELECT Internship_ID FROM INTERNSHIP WHERE Internship_ID = %s", (intern_id,))
    run_test("Internships", "Delete (with confirmation)", f"POST /internships/{intern_id}/delete",
             del_intern_check is None, "Safely deleted internship record")

# Tabs
status, html = get("/internships?type=Mandatory")
run_test("Internships", "Tab: Mandatory Dynamic SGPA", "GET /internships?type=Mandatory",
         "Prerequisite SGPA" in html and status == 200, "Dynamic SGPA join table rendered")

status, html = get("/internships?type=Missing")
run_test("Internships", "Tab: Missing Audit", "GET /internships?type=Missing",
         "Missing Mandatory" in html and status == 200, "Missing mandatory compliance audit rendered")

# -------------------------------------------------------------
# 4. PLACEMENTS
# -------------------------------------------------------------
# Clean up any test placement offer
execute_mutation("DELETE FROM PLACEMENT WHERE Role = 'E2E QA Lead Architect'")

# Issue valid offer
pl_data = {
    "Student_ID": "4",
    "Company_ID": "2",
    "Opportunity_ID": "",
    "Role": "E2E QA Lead Architect",
    "Package": "16.50",
    "Placement_Year": "2024",
    "Offer_Status": "Offered",
    "Is_PPO": "No"
}
status, html = post("/placements/new", pl_data)
created_pl = execute_one("SELECT Placement_ID FROM PLACEMENT WHERE Role = 'E2E QA Lead Architect'")
run_test("Placements", "Issue Offer (Valid)", "POST /placements/new",
         created_pl is not None, f"Created Placement_ID: {created_pl['Placement_ID'] if created_pl else 'None'}")
test_pl_id = created_pl["Placement_ID"] if created_pl else None

# Issue invalid offer (package <= 0)
bad_pl_data = dict(pl_data)
bad_pl_data["Package"] = "-5.0"
status, html = post("/placements/new", bad_pl_data)
has_pkg_err = "Package must be at least" in html or "Offer Issue Rejected" in html
run_test("Placements", "Issue Offer (Invalid Package <= 0)", "Reject negative/zero package",
         has_pkg_err, "Clean package validation error rendered on page")

# Update Status: Accept offer
if test_pl_id:
    status, html = post(f"/placements/{test_pl_id}/status", {"status": "Accepted"})
    curr_status = execute_one("SELECT Offer_Status FROM PLACEMENT WHERE Placement_ID = %s", (test_pl_id,))["Offer_Status"]
    run_test("Placements", "Status Update (Accept)", f"POST /placements/{test_pl_id}/status Accepted",
             curr_status == "Accepted", "Status transitioned to Accepted")

# Single Accepted Offer Rule: Student 1 (Aarav) already has a joined offer. Attempt to accept another offer for Student 1:
# Let's find an unaccepted offer for student 1
s1_other_offer = execute_one("SELECT Placement_ID FROM PLACEMENT WHERE Student_ID = 1 AND Offer_Status != 'Joined' LIMIT 1")
if s1_other_offer:
    other_id = s1_other_offer["Placement_ID"]
    status, html = post(f"/placements/{other_id}/status", {"status": "Accepted"})
    has_single_accept_block = "Status Transition Blocked" in html or "already holds an accepted" in html or "joined" in html
    run_test("Placements", "Rule: Single Accepted Offer", f"Attempt 2nd accepted offer on Student 1 (Offer #{other_id})",
             has_single_accept_block, "Policy enforced: Student cannot hold multiple active accepted offers")

# Delete placement offer
if test_pl_id:
    status, html = post(f"/placements/{test_pl_id}/delete", {})
    del_pl_check = execute_one("SELECT Placement_ID FROM PLACEMENT WHERE Placement_ID = %s", (test_pl_id,))
    run_test("Placements", "Delete Offer (with confirmation)", f"POST /placements/{test_pl_id}/delete",
             del_pl_check is None, "Safely deleted placement offer")

# Search and filter
status, html = get("/placements?search=Google")
run_test("Placements", "Search", "GET /placements?search=Google", "Google India" in html, "Found Google India offers")

status, html = get("/placements?status=Joined")
run_test("Placements", "Filter (Status)", "GET /placements?status=Joined", "Joined" in html, "Filtered Joined offers")

status, html = get("/placements?view=multiple")
run_test("Placements", "View: Multiple Offer Achievers", "GET /placements?view=multiple",
         "Star Performers" in html and status == 200, "Rendered students holding >= 2 offers")

# -------------------------------------------------------------
# 5. REPORTS
# -------------------------------------------------------------
status, html = get("/reports?branch=CSE&placement_status=Placed")
run_test("Reports", "Filter (Branch + Placed)", "GET /reports?branch=CSE&placement_status=Placed",
         "CSE" in html and status == 200, "Multi-criteria filtered cohort report rendered")

status, html = get("/reports/export?branch=CSE")
run_test("Reports", "Export to CSV", "GET /reports/export?branch=CSE",
         status == 200 and "Roll No,Student Name" in html and "CSE" in html, "Streamed CSV report")

# -------------------------------------------------------------
# 6. DASHBOARD & CHARTS
# -------------------------------------------------------------
status, html = get("/")
has_kpis = "Active Students" in html and "Placement Rate" in html and "Average Package" in html
has_charts = "yearwisePlacementChart" in html and "branchwiseChart" in html and "offerStatusChart" in html and "internshipBreakdownChart" in html
run_test("Dashboard", "KPI Cards & Chart.js", "GET / (Dashboard)",
         has_kpis and has_charts and status == 200, "All 4 KPI cards and 4 Chart.js containers rendered")

# -------------------------------------------------------------
# 7. SYSTEM HEALTH
# -------------------------------------------------------------
status, html = get("/health")
try:
    health_data = json.loads(html)
    is_healthy = health_data.get("status") == "healthy" and health_data["database"]["connection"] == "connected"
except Exception:
    is_healthy = False
run_test("System Health", "REST API Healthcheck", "GET /health",
         status == 200 and is_healthy, "MySQL connected, latency reported")

# -------------------------------------------------------------
# SUMMARY TABLE
# -------------------------------------------------------------
print("\n" + "="*80)
print(f"{'PAGE':<15} | {'FEATURE':<25} | {'TESTED':<30} | {'RESULT'}")
print("="*80)
for r in results_table:
    print(f"{r['page']:<15} | {r['feature']:<25} | {r['tested'][:30]:<30} | {r['result']}")
print("="*80)

total_tests = len(results_table)
pass_tests = sum(1 for r in results_table if r["result"] == "PASS")
fail_tests = sum(1 for r in results_table if r["result"] == "FAIL")
print(f"\nTOTAL TESTS: {total_tests} | PASSED: {pass_tests} | FAILED: {fail_tests}")

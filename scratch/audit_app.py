import urllib.request
import urllib.parse
import json
import re

BASE_URL = "http://127.0.0.1:5000"

# Use cookie jar so redirects keep Flask session flash messages
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
    encoded_data = urllib.parse.urlencode(data).encode('utf-8')
    try:
        req = urllib.request.Request(url, data=encoded_data, method='POST')
        with opener.open(req) as resp:
            return resp.status, resp.read().decode('utf-8'), resp.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8'), e.geturl()
    except Exception as e:
        return 0, str(e), ""

audit_results = []

def record(category, test_name, passed, details=""):
    audit_results.append({
        "category": category,
        "test": test_name,
        "status": "PASS" if passed else "FAIL",
        "details": details
    })
    print(f"[{'PASS' if passed else 'FAIL'}] {category} -> {test_name}: {details}")

# 1. SIDEBAR LINKS
sidebar_links = [
    ("/", "Dashboard"),
    ("/students", "Students Directory"),
    ("/companies", "Companies"),
    ("/internships", "Internships"),
    ("/placements", "Placements"),
    ("/reports", "Reports & Filters"),
    ("/health", "System Health"),
]

for link, name in sidebar_links:
    status, body = get(link)
    record("Sidebar Link", f"GET {link} ({name})", status == 200, f"HTTP {status}")

# 2. STUDENTS PAGE AUDIT
# Filters
status, body = get("/students?search=Aarav")
record("Students Filter", "Search by query ?search=Aarav", "CS202001" in body, "Found Aarav in table")

# Test branch filter with dropdown value 'Computer Science'
status, body = get("/students?branch=Computer+Science")
record("Students Filter", "Filter by branch=Computer Science", "CS202001" in body, "Matches 'Computer Science' in DB or 0 rows?")

# Test branch filter with 'CSE'
status, body = get("/students?branch=CSE")
record("Students Filter", "Filter by branch=CSE", "CS202001" in body, "Matches CSE in DB")

# Test min_cgpa filter
status, body = get("/students?min_cgpa=9.0")
record("Students Filter", "Filter by min_cgpa=9.0", "CS202001" in body, "Contains students >= 9.0")

# Test is_active filter
status, body = get("/students?is_active=1")
record("Students Filter", "Filter by is_active=1", status == 200, "Dropdown has is_active")

# Create student form view
status, body = get("/students/new")
record("Students Create", "GET /students/new", status == 200, f"HTTP {status}")

# Duplicate Roll Number creation
dup_data = {
    "Roll_No": "CS202001",
    "First_Name": "Duplicate",
    "Last_Name": "Test",
    "Email": "dup.test@univ.edu",
    "Branch": "CSE",
    "Batch_Year": "2024",
    "Section": "A",
    "CGPA": "8.50",
    "Backlogs": "0"
}
status, body, redirected = post("/students/new", dup_data)
# Should render error message on page and NOT crash
has_err = "already exists" in body or "danger" in body or "already in use" in body
record("Students Create", "POST /students/new Duplicate Roll Number", has_err and status == 200, f"Status: {status}, Has clear error: {has_err}")

# Invalid CGPA (> 10)
bad_cgpa = {
    "Roll_No": "TEST_CGPA_BAD",
    "First_Name": "Bad",
    "Last_Name": "CGPA",
    "Email": "bad.cgpa@univ.edu",
    "Branch": "CSE",
    "Batch_Year": "2024",
    "Section": "A",
    "CGPA": "15.00",
    "Backlogs": "0"
}
status, body, redirected = post("/students/new", bad_cgpa)
has_cgpa_err = "between 0.00 and 10.00" in body or "CGPA" in body
record("Students Create", "POST /students/new Invalid CGPA (15.0)", has_cgpa_err, f"Status: {status}, Error shown: {has_cgpa_err}")

# Delete student with placements (Student 1: Aarav has placements)
status, body, redirected = post("/students/1/delete", {})
has_del_err = "Cannot delete student" in body or "history detected" in body or "Cannot Delete Student" in body
record("Students Delete", "POST /students/1/delete (Student has placements)", has_del_err, f"Status: {status}, Flash error shown: {has_del_err}")

# 3. COMPANIES PAGE AUDIT
# Tier filter
status, body = get("/companies?tier=Tier-1")
record("Companies Filter", "Filter by tier=Tier-1", "Google India" in body or "Nexus" in body, "Does Tier-1 filter work?")

# Filter by Product
status, body = get("/companies?tier=Product")
record("Companies Filter", "Filter by tier=Product", "Nexus" in body, "Matches Product")

# Duplicate Company Name
dup_comp = {
    "Company_Name": "Google India",
    "Company_Type": "Product",
    "Industry": "Tech"
}
status, body, redirected = post("/companies/new", dup_comp)
has_comp_err = "already exists" in body or "danger" in body
record("Companies Create", "POST /companies/new Duplicate Company", has_comp_err, f"Status: {status}, Error shown: {has_comp_err}")

# Delete company with drives / placements (Company 1)
status, body, redirected = post("/companies/1/delete", {})
# Check if it was caught as flash error or crashed with 409 JSON
is_json = body.strip().startswith("{")
has_del_comp_flash = "Cannot Delete Company" in body
record("Companies Delete", "POST /companies/1/delete (Has dependencies)", not is_json and has_del_comp_flash, f"Status: {status}, Is JSON API response instead of HTML page? {is_json}")

# 4. INTERNSHIPS PAGE AUDIT
# Tabs
for tab in ["All", "Mandatory", "Additional", "Missing"]:
    status, body = get(f"/internships?type={tab}")
    record("Internships Tab", f"GET /internships?type={tab}", status == 200, f"HTTP {status}")

# Check Role column in All tab
status, body = get("/internships?type=All")
has_empty_role = "<td></td>" in body
record("Internships Display", "All Internships table role column", not has_empty_role, "Check if Role column is blank")

# 5. PLACEMENTS PAGE AUDIT
status, body = get("/placements")
record("Placements View", "GET /placements", status == 200, f"HTTP {status}")
status, body = get("/placements?view=multiple")
record("Placements View", "GET /placements?view=multiple", status == 200, f"HTTP {status}")

# Check opportunity dropdown text in modal
status, body = get("/placements")
has_empty_opp = "Opp #1:  ( &bull;   LPA)" in body or "Opp #1:  (" in body
record("Placements Modal", "Opportunity dropdown label rendering", not has_empty_opp, "Check if opportunity labels are blank")

# 6. REPORTS PAGE AUDIT
status, body = get("/reports")
record("Reports View", "GET /reports", status == 200, f"HTTP {status}")
status, body = get("/reports/export")
record("Reports Export", "GET /reports/export (CSV download)", status == 200 and "Roll No,Student Name" in body, f"HTTP {status}")

# Report branch filter
status, body = get("/reports?branch=Computer+Science")
record("Reports Filter", "Filter reports by branch=Computer Science", "CS202001" in body, "Does 'Computer Science' match students?")

# Print summary
print('\n=== AUDIT SUMMARY ===')
pass_cnt = sum(1 for r in audit_results if r["status"] == "PASS")
fail_cnt = sum(1 for r in audit_results if r["status"] == "FAIL")
print(f'Total: {len(audit_results)}, Passed: {pass_cnt}, Failed: {fail_cnt}')

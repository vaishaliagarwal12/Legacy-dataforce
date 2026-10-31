import sys
sys.path.insert(0, ".")

from services.sql_report_service import (
    list_saved_queries,
    execute_saved_query,
    validate_custom_sql,
    execute_custom_query,
)
from services.exceptions import ValidationError

def test_all():
    print("=== Testing Saved Queries ===")
    queries = list_saved_queries()
    print(f"Total saved queries in catalog: {len(queries)}")
    
    for q in queries:
        try:
            res = execute_saved_query(q["id"])
            print(f"  [OK] {q['group']} | {q['title']} -> {res['row_count']} rows ({res['execution_time_ms']} ms)")
        except Exception as e:
            print(f"  [FAIL] {q['group']} | {q['title']} -> ERROR: {e}")
            raise e

    print("\n=== Testing Safety Rules for Custom SQL ===")
    
    # 1. DROP TABLE rejection
    try:
        validate_custom_sql("DROP TABLE STUDENT;")
        print("  [FAIL] DROP TABLE was NOT rejected!")
    except ValidationError as ve:
        print(f"  [PASS] DROP TABLE rejected: {ve.message}")

    # 2. Multiple statements rejection
    try:
        validate_custom_sql("SELECT * FROM STUDENT; DROP TABLE COMPANY;")
        print("  [FAIL] Multiple statements NOT rejected!")
    except ValidationError as ve:
        print(f"  [PASS] Multiple statements rejected: {ve.message}")

    # 3. Missing SELECT rejection
    try:
        validate_custom_sql("UPDATE STUDENT SET CGPA = 9.9 WHERE Student_ID = 1;")
        print("  [FAIL] Missing SELECT (UPDATE) NOT rejected!")
    except ValidationError as ve:
        print(f"  [PASS] Missing SELECT (UPDATE) rejected: {ve.message}")

    # 4. Comments hiding statements rejection
    try:
        validate_custom_sql("SELECT * FROM STUDENT -- hiding something")
        print("  [FAIL] Line comment '--' was NOT rejected!")
    except ValidationError as ve:
        print(f"  [PASS] Line comment rejected: {ve.message}")

    try:
        validate_custom_sql("SELECT * FROM STUDENT /* block comment */")
        print("  [FAIL] Block comment '/* */' was NOT rejected!")
    except ValidationError as ve:
        print(f"  [PASS] Block comment rejected: {ve.message}")

    try:
        validate_custom_sql("SELECT * FROM STUDENT # hash comment")
        print("  [FAIL] Hash comment '#' was NOT rejected!")
    except ValidationError as ve:
        print(f"  [PASS] Hash comment rejected: {ve.message}")

    # 5. Valid SELECT query execution
    res = execute_custom_query("SELECT Student_ID, Roll_No, First_Name, Last_Name, Branch, CGPA FROM STUDENT ORDER BY CGPA DESC")
    print(f"\n  [PASS] Valid custom SELECT returned {res['row_count']} rows in {res['execution_time_ms']} ms, status={res['status']}")
    assert res["status"] == "success"
    assert res["row_count"] > 0
    assert "Roll_No" in res["columns"]

    # 6. Syntax error handling (readable message, no crash)
    res_err = execute_custom_query("SELECT Non_Existent_Column_12345 FROM STUDENT")
    print(f"  [PASS] Non-existent column handled gracefully: status={res_err['status']}, error='{res_err['error']}'")
    assert res_err["status"] == "error"
    assert res_err["error"] is not None

    print("\nALL SQL REPORT SERVICE TESTS PASSED!")

if __name__ == "__main__":
    test_all()

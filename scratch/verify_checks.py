"""Database Verification Script for seed.sql checks.
Executes queries against MySQL placement_db and displays detailed tabular results.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db.connection import get_connection

def run_verifications():
    with get_connection() as conn:
        with conn.cursor() as cur:
            print("=" * 80)
            print("1. ROW COUNTS FOR EVERY TABLE IN PLACEMENT_DB")
            print("=" * 80)
            cur.execute("""
                SELECT TABLE_NAME AS tbl_name 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
                ORDER BY TABLE_NAME;
            """)
            tables = [row["tbl_name"] if isinstance(row, dict) else row[0] for row in cur.fetchall()]
            
            total_rows = 0
            print(f"{'Table Name':<30} | {'Row Count':>10}")
            print("-" * 45)
            for tbl in tables:
                cur.execute(f"SELECT COUNT(*) AS cnt FROM `{tbl}`;")
                cnt_res = cur.fetchone()
                cnt = cnt_res["cnt"] if isinstance(cnt_res, dict) else cnt_res[0]
                print(f"{tbl:<30} | {cnt:>10}")
                total_rows += cnt
            print("-" * 45)
            print(f"{'TOTAL ROWS ACROSS ALL TABLES':<30} | {total_rows:>10}")
            print()

            print("=" * 80)
            print("2. CHECK 1: STUDENTS WITH NO MANDATORY INTERNSHIP (Must return 0 rows)")
            print("=" * 80)
            check1_query = """
            SELECT s.Student_ID, s.Roll_No, s.First_Name, s.Last_Name, s.Branch, s.Batch_Year
            FROM STUDENT s
            WHERE NOT EXISTS (
                SELECT 1 
                FROM INTERNSHIP i 
                WHERE i.Student_ID = s.Student_ID 
                  AND i.Internship_Type = 'Mandatory'
            );
            """
            cur.execute(check1_query)
            rows1 = cur.fetchall()
            print(f"Query:\n{check1_query.strip()}\n")
            print(f"Rows Returned: {len(rows1)}")
            if rows1:
                for r in rows1:
                    print("  Found violation:", r)
            else:
                print(">>> PASSED: 0 rows returned. Every student has mandatory internship(s).")
            print()

            # Additional check: Does every student have BOTH Internship 1 AND Internship 2?
            print("-" * 80)
            print("2b. DETAILED MANDATORY INTERNSHIP AUDIT PER STUDENT (1 & 2, Sem 5 & 7, 4 credits)")
            print("-" * 80)
            check1b_query = """
            SELECT s.Student_ID, s.Roll_No,
                   SUM(CASE WHEN i.Internship_No = 1 AND i.Report_Semester = 5 AND i.Credits = 4 AND i.Internship_Type = 'Mandatory' THEN 1 ELSE 0 END) AS has_i1,
                   SUM(CASE WHEN i.Internship_No = 2 AND i.Report_Semester = 7 AND i.Credits = 4 AND i.Internship_Type = 'Mandatory' THEN 1 ELSE 0 END) AS has_i2,
                   SUM(CASE WHEN i.Internship_No >= 3 AND i.Internship_Type = 'Additional' AND i.Requirement_ID IS NULL THEN 1 ELSE 0 END) AS has_extra
            FROM STUDENT s
            LEFT JOIN INTERNSHIP i ON s.Student_ID = i.Student_ID
            GROUP BY s.Student_ID, s.Roll_No
            HAVING has_i1 != 1 OR has_i2 != 1;
            """
            cur.execute(check1b_query)
            rows1b = cur.fetchall()
            print(f"Students missing Internship 1 or 2 (Sem 5/7, 4 credits): {len(rows1b)}")
            if rows1b:
                for r in rows1b:
                    print("  Incomplete:", r)
            else:
                print(">>> PASSED: All 30 students have Internship 1 (Sem 5, 4 cr) AND Internship 2 (Sem 7, 4 cr).")
            print()

            print("=" * 80)
            print("3. CHECK 2: STUDENTS WITH MORE THAN ONE JOINED PLACEMENT (Must return 0 rows)")
            print("=" * 80)
            check2_query = """
            SELECT Student_ID, COUNT(*) AS joined_count
            FROM PLACEMENT
            WHERE Joined = 'Yes'
            GROUP BY Student_ID
            HAVING joined_count > 1;
            """
            cur.execute(check2_query)
            rows2 = cur.fetchall()
            print(f"Query:\n{check2_query.strip()}\n")
            print(f"Rows Returned: {len(rows2)}")
            if rows2:
                for r in rows2:
                    print("  Found violation:", r)
            else:
                print(">>> PASSED: 0 rows returned. No student has joined more than one offer.")
            print()

            print("=" * 80)
            print("4. CHECK 3: ANY FOREIGN KEY PROBLEMS / ORPHAN RECORDS")
            print("=" * 80)
            # Find all foreign keys defined in the schema
            cur.execute("""
                SELECT 
                    TABLE_NAME, 
                    COLUMN_NAME, 
                    REFERENCED_TABLE_NAME, 
                    REFERENCED_COLUMN_NAME,
                    CONSTRAINT_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                  AND REFERENCED_TABLE_NAME IS NOT NULL
                ORDER BY TABLE_NAME, COLUMN_NAME;
            """)
            fks = cur.fetchall()
            print(f"Total Foreign Key Constraints Checked: {len(fks)}")
            print(f"{'Child Table':<22} | {'Child Column':<18} | {'Parent Table':<22} | {'Orphans':>8}")
            print("-" * 80)

            total_orphans = 0
            for fk in fks:
                if isinstance(fk, dict):
                    c_tbl = fk["TABLE_NAME"]
                    c_col = fk["COLUMN_NAME"]
                    p_tbl = fk["REFERENCED_TABLE_NAME"]
                    p_col = fk["REFERENCED_COLUMN_NAME"]
                else:
                    c_tbl, c_col, p_tbl, p_col = fk[0], fk[1], fk[2], fk[3]

                orphan_query = f"""
                    SELECT COUNT(*) AS orphans
                    FROM `{c_tbl}` c
                    WHERE c.`{c_col}` IS NOT NULL
                      AND NOT EXISTS (
                          SELECT 1 FROM `{p_tbl}` p WHERE p.`{p_col}` = c.`{c_col}`
                      );
                """
                cur.execute(orphan_query)
                res = cur.fetchone()
                orphans = res["orphans"] if isinstance(res, dict) else res[0]
                print(f"{c_tbl:<22} | {c_col:<18} | {p_tbl:<22} | {orphans:>8}")
                total_orphans += orphans

            print("-" * 80)
            print(f"TOTAL ORPHAN RECORDS ACROSS ALL FOREIGN KEYS: {total_orphans}")
            if total_orphans == 0:
                print(">>> PASSED: 0 foreign key violations found. All relational links intact.")
            else:
                print(f">>> FAILED: Found {total_orphans} foreign key violations.")
            print()

            print("=" * 80)
            print("5. ADDITIONAL REQUIREMENTS VERIFICATION")
            print("=" * 80)
            # Batches and branches
            cur.execute("""
                SELECT Batch_Year, Branch, COUNT(*) AS student_count
                FROM STUDENT
                GROUP BY Batch_Year, Branch
                ORDER BY Batch_Year, Branch;
            """)
            print("Students distribution across Batches & Branches:")
            for r in cur.fetchall():
                print(f"  Batch {r['Batch_Year']} | Branch {r['Branch']:<4} | Count: {r['student_count']}")

            # Offers breakdown
            cur.execute("""
                SELECT 
                    offer_count, 
                    COUNT(*) AS num_students
                FROM (
                    SELECT s.Student_ID, COUNT(p.Placement_ID) AS offer_count
                    FROM STUDENT s
                    LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
                    GROUP BY s.Student_ID
                ) t
                GROUP BY offer_count
                ORDER BY offer_count;
            """)
            print("\nPlacement Offers Distribution:")
            for r in cur.fetchall():
                print(f"  Students with {r['offer_count']} offer(s): {r['num_students']}")

            # PPO check
            cur.execute("""
                SELECT p.Placement_ID, p.Student_ID, s.First_Name, s.Last_Name, c.Company_Name, p.Role, p.Package, p.Is_PPO
                FROM PLACEMENT p
                JOIN STUDENT s ON p.Student_ID = s.Student_ID
                JOIN COMPANY c ON p.Company_ID = c.Company_ID
                WHERE p.Is_PPO = 'Yes'
                ORDER BY p.Placement_ID;
            """)
            ppos = cur.fetchall()
            print(f"\nPPO Offers ({len(ppos)} total):")
            for p in ppos:
                # verify student interned at this company
                cur.execute("""
                    SELECT COUNT(*) AS intern_cnt 
                    FROM INTERNSHIP 
                    WHERE Student_ID = %s AND Company_ID = (
                        SELECT Company_ID FROM PLACEMENT WHERE Placement_ID = %s
                    )
                """, (p["Student_ID"], p["Placement_ID"]))
                icnt = cur.fetchone()["intern_cnt"]
                print(f"  Offer #{p['Placement_ID']}: {p['First_Name']} {p['Last_Name']} (ID: {p['Student_ID']}) at {p['Company_Name']} - {p['Package']} LPA | Interned there? {'YES (' + str(icnt) + ' internship(s))' if icnt > 0 else 'NO'}")

            # Salary package range
            cur.execute("""
                SELECT MIN(Package) AS min_pkg, MAX(Package) AS max_pkg, AVG(Package) AS avg_pkg
                FROM PLACEMENT;
            """)
            pkg = cur.fetchone()
            print(f"\nPackage Metrics: Min = {pkg['min_pkg']} LPA, Max = {pkg['max_pkg']} LPA, Avg = {round(pkg['avg_pkg'], 2)} LPA")

            # Companies breakdown
            cur.execute("""
                SELECT Company_Type, COUNT(*) AS cnt, GROUP_CONCAT(Company_Name SEPARATOR ', ') AS names
                FROM COMPANY
                GROUP BY Company_Type;
            """)
            print("\nCompany Types Breakdown:")
            for r in cur.fetchall():
                print(f"  {r['Company_Type']:<10} ({r['cnt']}): {r['names']}")

            print("=" * 80)

if __name__ == "__main__":
    run_verifications()

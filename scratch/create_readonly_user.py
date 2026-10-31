from db.connection import get_cursor
import pymysql
from config import Config

def main():
    with get_cursor(commit=True) as cursor:
        cursor.execute("CREATE USER IF NOT EXISTS 'placement_readonly'@'localhost' IDENTIFIED BY 'ReadOnly_Pass2026!';")
        cursor.execute("GRANT SELECT ON placement_db.* TO 'placement_readonly'@'localhost';")
        cursor.execute("CREATE USER IF NOT EXISTS 'placement_readonly'@'%' IDENTIFIED BY 'ReadOnly_Pass2026!';")
        cursor.execute("GRANT SELECT ON placement_db.* TO 'placement_readonly'@'%';")
        cursor.execute("FLUSH PRIVILEGES;")
        print("Read-only user created successfully.")

    # Now verify connection as placement_readonly
    conn = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user="placement_readonly",
        password="ReadOnly_Pass2026!",
        database=Config.MYSQL_DB,
    )
    cur = conn.cursor()
    cur.execute("SELECT 1 AS test;")
    row = cur.fetchone()
    print("Test SELECT as placement_readonly:", row)
    
    # Verify that write is forbidden for placement_readonly
    try:
        cur.execute("CREATE TABLE test_forbidden (id INT);")
        print("WARNING: Write should not have been allowed!")
    except Exception as e:
        print("Verified that write is blocked for placement_readonly as expected:", e)
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()

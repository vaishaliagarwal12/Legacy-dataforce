-- ============================================================================
-- VERIFY.SQL: Verification & Validation Script for Canonical 7-Table Schema
-- Database: placement_db
-- ============================================================================

SELECT '=====================================================' AS '';
SELECT 'CANONICAL 7-TABLE SCHEMA VERIFICATION' AS status;
SELECT '=====================================================' AS '';

-- 1. Row Counts Across All 7 Canonical Tables
SELECT '1. Canonical Table Row Counts:' AS verification_step;
SELECT 'STUDENT' AS table_name, COUNT(*) AS row_count FROM STUDENT
UNION ALL SELECT 'STUDENT_PHONE', COUNT(*) FROM STUDENT_PHONE
UNION ALL SELECT 'STUDENT_SKILL', COUNT(*) FROM STUDENT_SKILL
UNION ALL SELECT 'COMPANY', COUNT(*) FROM COMPANY
UNION ALL SELECT 'PLACEMENT', COUNT(*) FROM PLACEMENT
UNION ALL SELECT 'PLACEMENT_SKILL', COUNT(*) FROM PLACEMENT_SKILL
UNION ALL SELECT 'INTERNSHIP', COUNT(*) FROM INTERNSHIP;

-- 2. View Row Counts & Duration Calculation Verification
SELECT '2. Relational Views Verification:' AS verification_step;
SELECT 'V_PLACEMENT_DETAIL' AS view_name, COUNT(*) AS row_count FROM V_PLACEMENT_DETAIL
UNION ALL
SELECT 'V_INTERNSHIP_DETAIL', COUNT(*) FROM V_INTERNSHIP_DETAIL;

-- Sample check on dynamic Duration_Months in V_INTERNSHIP_DETAIL
SELECT Internship_ID, Student_Name, Company_Name, Internship_No, Internship_Type, 
       Start_Date, End_Date, Duration_Months
FROM V_INTERNSHIP_DETAIL
LIMIT 5;

-- 3. Foreign Key Referential Integrity (Orphaned row checks - must all be 0)
SELECT '3. FK Referential Integrity Verification (Orphaned count must be 0):' AS verification_step;

SELECT 'STUDENT_PHONE -> STUDENT' AS fk_relation, COUNT(*) AS orphaned_count 
FROM STUDENT_PHONE sp LEFT JOIN STUDENT s ON sp.Student_ID = s.Student_ID WHERE s.Student_ID IS NULL
UNION ALL
SELECT 'STUDENT_SKILL -> STUDENT', COUNT(*) 
FROM STUDENT_SKILL sk LEFT JOIN STUDENT s ON sk.Student_ID = s.Student_ID WHERE s.Student_ID IS NULL
UNION ALL
SELECT 'PLACEMENT -> STUDENT', COUNT(*) 
FROM PLACEMENT p LEFT JOIN STUDENT s ON p.Student_ID = s.Student_ID WHERE s.Student_ID IS NULL
UNION ALL
SELECT 'PLACEMENT -> COMPANY', COUNT(*) 
FROM PLACEMENT p LEFT JOIN COMPANY c ON p.Company_ID = c.Company_ID WHERE c.Company_ID IS NULL
UNION ALL
SELECT 'PLACEMENT_SKILL -> PLACEMENT', COUNT(*) 
FROM PLACEMENT_SKILL ps LEFT JOIN PLACEMENT p ON ps.Placement_ID = p.Placement_ID WHERE p.Placement_ID IS NULL
UNION ALL
SELECT 'INTERNSHIP -> STUDENT', COUNT(*) 
FROM INTERNSHIP i LEFT JOIN STUDENT s ON i.Student_ID = s.Student_ID WHERE s.Student_ID IS NULL
UNION ALL
SELECT 'INTERNSHIP -> COMPANY', COUNT(*) 
FROM INTERNSHIP i LEFT JOIN COMPANY c ON i.Company_ID = c.Company_ID WHERE c.Company_ID IS NULL;

-- 4. Business Rule Constraints Verification (Violations must all be 0)
SELECT '4. Integrity Constraints Verification (Violations must be 0):' AS verification_step;

-- Check 4.1: Placement Joined status rule: Joined = 'Yes' allowed ONLY IF Offer_Status = 'Accepted'
SELECT 'Placement Joined Status Violations (Joined="Yes" but Offer_Status != "Accepted")' AS rule_check,
       COUNT(*) AS violations
FROM PLACEMENT
WHERE NOT (Joined = 'No' OR Offer_Status = 'Accepted')
UNION ALL
-- Check 4.2: Single Joined Offer rule (uq_one_joined_offer): A student can join at most 1 offer
SELECT 'Multiple Joined Offers per Student (uq_one_joined_offer violations)',
       COUNT(*)
FROM (
    SELECT Student_ID
    FROM PLACEMENT
    WHERE Joined = 'Yes'
    GROUP BY Student_ID
    HAVING COUNT(*) > 1
) sub
UNION ALL
-- Check 4.3: Internship Curriculum Rule (chk_internship_curriculum)
-- I1: Mandatory, 4 cr, Sem 5
-- I2: Mandatory, 4 cr, Sem 8
-- I3+: Additional
SELECT 'Internship Curriculum Rule Violations',
       COUNT(*)
FROM INTERNSHIP
WHERE NOT (
    (Internship_No = 1 AND Internship_Type = 'Mandatory' AND Credits = 4 AND Report_Semester = 5)
    OR (Internship_No = 2 AND Internship_Type = 'Mandatory' AND Credits = 4 AND Report_Semester = 8)
    OR (Internship_No >= 3 AND Internship_Type = 'Additional')
)
UNION ALL
-- Check 4.4: Internship Chronological Dates Rule (chk_internship_dates)
SELECT 'Internship Date Violations (End_Date < Start_Date)',
       COUNT(*)
FROM INTERNSHIP
WHERE End_Date < Start_Date;

-- 5. Placement & Internship Business Metrics Summary
SELECT '5. Placement & Internship Key Metrics:' AS verification_step;

SELECT 
    (SELECT COUNT(*) FROM STUDENT) AS total_students,
    (SELECT COUNT(DISTINCT Student_ID) FROM PLACEMENT WHERE Joined = 'Yes') AS placed_students_joined,
    (SELECT COUNT(*) FROM PLACEMENT WHERE Offer_Status = 'Accepted') AS accepted_offers,
    (SELECT COUNT(*) FROM PLACEMENT WHERE Offer_Status = 'Offered') AS pending_offers,
    (SELECT COUNT(*) FROM PLACEMENT WHERE Offer_Status = 'Declined') AS declined_offers,
    (SELECT COUNT(*) FROM PLACEMENT) AS total_placement_offers;

SELECT 
    Internship_Type,
    Report_Semester,
    COUNT(*) AS count_internships,
    COUNT(DISTINCT Student_ID) AS unique_students
FROM INTERNSHIP
GROUP BY Internship_Type, Report_Semester
ORDER BY Report_Semester;

-- 6. Offer Distribution (Zero, Single, Multiple Offers)
SELECT '6. Offer Distribution Across Students:' AS verification_step;
WITH offer_counts AS (
    SELECT s.Student_ID, s.Roll_No, COUNT(p.Placement_ID) AS total_offers,
           COUNT(CASE WHEN p.Joined = 'Yes' THEN 1 END) AS joined_count
    FROM STUDENT s
    LEFT JOIN PLACEMENT p ON s.Student_ID = p.Student_ID
    GROUP BY s.Student_ID, s.Roll_No
)
SELECT 
    CASE 
        WHEN total_offers = 0 THEN '0 offers (Zero)'
        WHEN total_offers = 1 THEN '1 offer (Single)'
        ELSE '2+ offers (Multiple)'
    END AS offer_category,
    COUNT(*) AS student_count,
    SUM(joined_count) AS joined_in_category
FROM offer_counts
GROUP BY offer_category;

SELECT 'Verification Completed Successfully.' AS status;

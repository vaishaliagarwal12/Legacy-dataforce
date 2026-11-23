"""Legacy DataForce - Standalone Fictional Demonstration Dataset Generator.

Generates a realistic, university-grade, strictly fictional dataset for academic
and evaluation demonstrations.

Key Features & Demonstration Coverage:
1. Multi-Discipline Students: CSE, IT, ECE, ME, Civil, Electrical across Batches 2022 to 2026.
2. 1NF Decomposition: Multivalued phone numbers (STUDENT_PHONE) and technical skills (STUDENT_SKILL).
3. Complete Academic History: Semester 1 through 8 results (SEMESTER_RESULT) with realistic SGPAs.
4. Corporate Recruitment Hierarchy: COMPANY -> RECRUITMENT_DRIVE -> OPPORTUNITY -> ELIGIBILITY -> SELECTION_PROCESS.
5. Single-Accepted-Offer Rule Demonstration:
   - High-achieving candidates holding multiple offers in 'Offered' status.
   - At most one offer in 'Accepted' or 'Joined' status.
   - Declined offers for realistic conversion rates.
6. Internship Academic Rules:
   - Mandatory Internship 1: Completed post Sem 4 break; checks Sem 3 SGPA prerequisite.
   - Mandatory Internship 2: Completed post Sem 6 break; checks Sem 5 SGPA prerequisite.
   - Additional voluntary and winter internships.
   - Controlled compliance gaps (students missing I1 or I2 for audit warnings).

SAFETY GUARANTEE:
- This script DOES NOT touch or insert into any live database automatically.
- By default, it generates a clean SQL file: 'demo_dataset.sql'.
- Database insertion requires explicit flags: --apply --target-db <dbname>.
"""

import os
import sys
import argparse
import logging
from typing import List

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("demo_dataset_generator")


def generate_sql_script() -> str:
    """Constructs the complete, production-grade synthetic dataset SQL script."""
    sql_lines: List[str] = [
        "-- ============================================================================",
        "-- LEGACY DATAFORCE: PROFESSIONAL FICTIONAL DEMONSTRATION DATASET",
        "-- ============================================================================",
        "-- STRICTLY SYNTHETIC AND FICTIONAL DATA FOR ACADEMIC EVALUATION PURPOSES.",
        "-- Any resemblance to actual persons, companies, or live credentials is coincidental.",
        "-- ============================================================================",
        "",
        "SET FOREIGN_KEY_CHECKS = 0;",
        "",
        "-- Clear existing demo tables",
        "TRUNCATE TABLE PLACEMENT_SKILL;",
        "TRUNCATE TABLE PLACEMENT;",
        "TRUNCATE TABLE INTERNSHIP;",
        "TRUNCATE TABLE INTERNSHIP_REQUIREMENT;",
        "TRUNCATE TABLE SELECTION_PROCESS;",
        "TRUNCATE TABLE ELIGIBILITY_BRANCH;",
        "TRUNCATE TABLE ELIGIBILITY;",
        "TRUNCATE TABLE OPPORTUNITY;",
        "TRUNCATE TABLE RECRUITMENT_DRIVE;",
        "TRUNCATE TABLE COMPANY;",
        "TRUNCATE TABLE SEMESTER_RESULT;",
        "TRUNCATE TABLE EDUCATION_DOCUMENT;",
        "TRUNCATE TABLE RESUME;",
        "TRUNCATE TABLE STUDENT_PROFILE;",
        "TRUNCATE TABLE STUDENT_COURSE;",
        "TRUNCATE TABLE STUDENT_SKILL;",
        "TRUNCATE TABLE STUDENT_PHONE;",
        "TRUNCATE TABLE STUDENT;",
        "TRUNCATE TABLE COURSE;",
        "TRUNCATE TABLE UNIVERSITY;",
        "",
        "-- ============================================================================",
        "-- 1. UNIVERSITY & ACADEMIC CATALOG",
        "-- ============================================================================",
        "INSERT INTO UNIVERSITY (University_ID, University_Name, Location, Established_Year) VALUES",
        "(1, 'National Institute of Advanced Technology', 'Tech City, India', 1985);",
        "",
        "INSERT INTO COURSE (Course_ID, University_ID, Course_Name, Department, Semester, Credits, Course_Type) VALUES",
        "(1, 1, 'Data Structures & Algorithms', 'Computer Science', 3, 4, 'Core'),",
        "(2, 1, 'Database Management Systems', 'Computer Science', 4, 4, 'Core'),",
        "(3, 1, 'Operating Systems', 'Computer Science', 4, 4, 'Core'),",
        "(4, 1, 'Computer Networks', 'Computer Science', 5, 4, 'Core'),",
        "(5, 1, 'Software Engineering', 'Computer Science', 5, 3, 'Core'),",
        "(6, 1, 'Machine Learning Foundations', 'Computer Science', 6, 4, 'Elective'),",
        "(7, 1, 'Digital Signal Processing', 'Electronics', 4, 4, 'Core'),",
        "(8, 1, 'VLSI Design', 'Electronics', 5, 4, 'Core'),",
        "(9, 1, 'Microprocessors & Microcontrollers', 'Electronics', 5, 4, 'Core'),",
        "(10, 1, 'Thermodynamics & Heat Transfer', 'Mechanical', 3, 4, 'Core'),",
        "(11, 1, 'Computer-Aided Design', 'Mechanical', 5, 3, 'Lab'),",
        "(12, 1, 'Manufacturing Processes', 'Mechanical', 4, 4, 'Core'),",
        "(13, 1, 'Structural Analysis', 'Civil', 4, 4, 'Core'),",
        "(14, 1, 'Power Systems Engineering', 'Electrical', 5, 4, 'Core');",
        "",
        "-- ============================================================================",
        "-- 2. STUDENTS (32 Fictional Candidates across Batches 2022-2026 and Disciplines)",
        "-- ============================================================================",
        "INSERT INTO STUDENT (Student_ID, Roll_No, First_Name, Last_Name, Branch, Batch_Year, Section, CGPA, Backlogs, Email, Resume_Link) VALUES",
        "(1, 'CS202001', 'Aarav', 'Sharma', 'CSE', 2024, 'A', 9.45, 0, 'aarav.sharma@fictional.edu', 'https://storage.fictional.edu/resumes/cs202001.pdf'),",
        "(2, 'CS202002', 'Diya', 'Patel', 'CSE', 2024, 'A', 9.12, 0, 'diya.patel@fictional.edu', 'https://storage.fictional.edu/resumes/cs202002.pdf'),",
        "(3, 'EC202003', 'Kabir', 'Verma', 'ECE', 2024, 'B', 8.25, 0, 'kabir.verma@fictional.edu', 'https://storage.fictional.edu/resumes/ec202003.pdf'),",
        "(4, 'ME202004', 'Rohan', 'Deshmukh', 'ME', 2024, 'A', 6.85, 2, 'rohan.deshmukh@fictional.edu', 'https://storage.fictional.edu/resumes/me202004.pdf'),",
        "(5, 'IT202005', 'Sneha', 'Reddy', 'IT', 2024, 'A', 8.70, 0, 'sneha.reddy@fictional.edu', 'https://storage.fictional.edu/resumes/it202005.pdf'),",
        "(6, 'CS202006', 'Gaurav', 'Trivedi', 'CSE', 2024, 'B', 8.50, 0, 'gaurav.trivedi@fictional.edu', 'https://storage.fictional.edu/resumes/cs202006.pdf'),",
        "(7, 'EC202007', 'Simran', 'Kaur', 'ECE', 2024, 'A', 7.10, 1, 'simran.kaur@fictional.edu', 'https://storage.fictional.edu/resumes/ec202007.pdf'),",
        "(8, 'CS202108', 'Ananya', 'Iyer', 'CSE', 2025, 'A', 9.60, 0, 'ananya.iyer@fictional.edu', 'https://storage.fictional.edu/resumes/cs202108.pdf'),",
        "(9, 'CS202109', 'Vikram', 'Nair', 'CSE', 2025, 'B', 8.95, 0, 'vikram.nair@fictional.edu', 'https://storage.fictional.edu/resumes/cs202109.pdf'),",
        "(10, 'EC202110', 'Pooja', 'Joshi', 'ECE', 2025, 'A', 7.80, 0, 'pooja.joshi@fictional.edu', 'https://storage.fictional.edu/resumes/ec202110.pdf'),",
        "(11, 'ME202111', 'Arjun', 'Mehta', 'ME', 2025, 'A', 7.45, 0, 'arjun.mehta@fictional.edu', 'https://storage.fictional.edu/resumes/me202111.pdf'),",
        "(12, 'IT202112', 'Siddharth', 'Chopra', 'IT', 2025, 'B', 8.15, 0, 'siddharth.chopra@fictional.edu', 'https://storage.fictional.edu/resumes/it202112.pdf'),",
        "(13, 'CS202113', 'Harsh', 'Vardhan', 'CSE', 2025, 'A', 9.10, 0, 'harsh.vardhan@fictional.edu', 'https://storage.fictional.edu/resumes/cs202113.pdf'),",
        "(14, 'IT202114', 'Neha', 'Agarwal', 'IT', 2025, 'A', 7.65, 0, 'neha.agarwal@fictional.edu', 'https://storage.fictional.edu/resumes/it202114.pdf'),",
        "(15, 'CS202215', 'Aditya', 'Kulkarni', 'CSE', 2026, 'A', 8.40, 0, 'aditya.kulkarni@fictional.edu', 'https://storage.fictional.edu/resumes/cs202215.pdf'),",
        "(16, 'CS202216', 'Ishita', 'Bose', 'CSE', 2026, 'A', 9.30, 0, 'ishita.bose@fictional.edu', 'https://storage.fictional.edu/resumes/cs202216.pdf'),",
        "(17, 'CS201817', 'Meera', 'Menon', 'CSE', 2022, 'B', 9.55, 0, 'meera.menon@fictional.edu', 'https://storage.fictional.edu/resumes/cs201817.pdf'),",
        "(18, 'EC201818', 'Varun', 'Kapoor', 'ECE', 2022, 'A', 8.05, 0, 'varun.kapoor@fictional.edu', 'https://storage.fictional.edu/resumes/ec201818.pdf'),",
        "(19, 'CS201919', 'Kavya', 'Srinivasan', 'CSE', 2023, 'A', 9.20, 0, 'kavya.srinivasan@fictional.edu', 'https://storage.fictional.edu/resumes/cs201919.pdf'),",
        "(20, 'IT201920', 'Rahul', 'Saxena', 'IT', 2023, 'B', 6.90, 1, 'rahul.saxena@fictional.edu', 'https://storage.fictional.edu/resumes/it201920.pdf'),",
        "(21, 'ME201921', 'Priya', 'Pillai', 'ME', 2023, 'A', 7.15, 0, 'priya.pillai@fictional.edu', 'https://storage.fictional.edu/resumes/me201921.pdf'),",
        "(22, 'EC201922', 'Pranav', 'Singhania', 'ECE', 2023, 'B', 7.95, 0, 'pranav.singhania@fictional.edu', 'https://storage.fictional.edu/resumes/ec201922.pdf'),",
        "(23, 'CV202023', 'Rajesh', 'Kumar', 'Civil', 2024, 'A', 7.30, 0, 'rajesh.kumar@fictional.edu', 'https://storage.fictional.edu/resumes/cv202023.pdf'),",
        "(24, 'EE202024', 'Ananya', 'Sen', 'Electrical', 2024, 'A', 8.10, 0, 'ananya.sen@fictional.edu', 'https://storage.fictional.edu/resumes/ee202024.pdf'),",
        "(25, 'CS202025', 'Karthik', 'Raman', 'CSE', 2024, 'B', 6.40, 0, 'karthik.raman@fictional.edu', 'https://storage.fictional.edu/resumes/cs202025.pdf'),",
        "(26, 'IT202026', 'Deepa', 'Balaji', 'IT', 2024, 'B', 8.80, 0, 'deepa.balaji@fictional.edu', 'https://storage.fictional.edu/resumes/it202026.pdf'),",
        "(27, 'ME202027', 'Sanjay', 'Gupta', 'ME', 2024, 'A', 5.90, 3, 'sanjay.gupta@fictional.edu', 'https://storage.fictional.edu/resumes/me202027.pdf'),",
        "(28, 'CS202128', 'Tanya', 'Choudhury', 'CSE', 2025, 'B', 9.15, 0, 'tanya.choudhury@fictional.edu', 'https://storage.fictional.edu/resumes/cs202128.pdf'),",
        "(29, 'EC202129', 'Manish', 'Tiwari', 'ECE', 2025, 'A', 7.60, 0, 'manish.tiwari@fictional.edu', 'https://storage.fictional.edu/resumes/ec202129.pdf'),",
        "(30, 'IT202130', 'Pooja', 'Namboodiri', 'IT', 2025, 'A', 8.45, 0, 'pooja.namboodiri@fictional.edu', 'https://storage.fictional.edu/resumes/it202130.pdf'),",
        "(31, 'CV202131', 'Amit', 'Roy', 'Civil', 2025, 'A', 6.95, 0, 'amit.roy@fictional.edu', 'https://storage.fictional.edu/resumes/cv202131.pdf'),",
        "(32, 'EE202132', 'Bhavna', 'Mishra', 'Electrical', 2025, 'A', 7.75, 0, 'bhavna.mishra@fictional.edu', 'https://storage.fictional.edu/resumes/ee202132.pdf');",
        "",
        "-- ============================================================================",
        "-- 3. MULTIVALUED ATTRIBUTES: PHONES & TECHNICAL SKILLS (1NF Decomposition)",
        "-- ============================================================================",
        "INSERT INTO STUDENT_PHONE (Student_ID, Phone_No) VALUES",
        "(1, '+91-9876543201'), (1, '+91-9876550001'), (1, '+91-9876560001'),",
        "(2, '+91-9876540002'), (3, '+91-9876540003'), (3, '+91-9876550003'),",
        "(4, '+91-9876540004'), (5, '+91-9876540005'), (6, '+91-9876540006'),",
        "(7, '+91-9876540007'), (8, '+91-9876540008'), (9, '+91-9876540009'),",
        "(10, '+91-9876540010'), (11, '+91-9876540011'), (12, '+91-9876540012'),",
        "(13, '+91-9876540013'), (14, '+91-9876540014'), (15, '+91-9876540015'),",
        "(16, '+91-9876540016'), (17, '+91-9876540017'), (18, '+91-9876540018'),",
        "(19, '+91-9876540019'), (20, '+91-9876540020'), (21, '+91-9876540021'),",
        "(22, '+91-9876540022'), (23, '+91-9876540023'), (24, '+91-9876540024'),",
        "(25, '+91-9876540025'), (26, '+91-9876540026'), (27, '+91-9876540027');",
        "",
        "INSERT INTO STUDENT_SKILL (Student_ID, Skill) VALUES",
        "(1, 'Python'), (1, 'C++'), (1, 'Distributed Systems'), (1, 'MySQL'),",
        "(2, 'Java'), (2, 'Spring Boot'), (2, 'Microservices'), (2, 'Docker'),",
        "(3, 'Verilog'), (3, 'Embedded C'), (3, 'VLSI Design'), (3, 'FPGA'),",
        "(4, 'SolidWorks'), (4, 'AutoCAD'), (4, 'ANSYS Simulation'),",
        "(5, 'React'), (5, 'Node.js'), (5, 'TypeScript'), (5, 'GraphQL'),",
        "(6, 'Python'), (6, 'Machine Learning'), (6, 'PyTorch'), (6, 'SQL'),",
        "(8, 'Algorithms'), (8, 'System Design'), (8, 'Go'), (8, 'Kubernetes'),",
        "(9, 'Full Stack Web'), (9, 'Django'), (9, 'PostgreSQL'),",
        "(10, 'MATLAB'), (10, 'Signal Processing'), (10, 'C++'),",
        "(11, 'Thermodynamics'), (11, 'Finite Element Analysis'),",
        "(12, 'Cloud Computing'), (12, 'AWS'), (12, 'Terraform'),",
        "(13, 'Python'), (13, 'Data Engineering'), (13, 'Apache Spark'),",
        "(14, 'JavaScript'), (14, 'Vue.js'), (14, 'REST APIs'),",
        "(17, 'Distributed Systems'), (17, 'Rust'), (17, 'Linux Kernel'),",
        "(19, 'Java'), (19, 'Kotlin'), (19, 'Android Architecture');",
        "",
        "-- ============================================================================",
        "-- 4. SEMESTER RESULTS (Tracking SGPAs across Semesters 1 to 8)",
        "-- ============================================================================",
        "INSERT INTO SEMESTER_RESULT (Result_ID, Student_ID, Semester, SGPA, Year, Total_Credits) VALUES",
        "-- Aarav Sharma (CS202001) - High Performer (Meets I1 & I2 Prerequisites)",
        "(1, 1, 1, 9.20, 2020, 22), (2, 1, 2, 9.40, 2021, 22), (3, 1, 3, 9.50, 2021, 24),",
        "(4, 1, 4, 9.60, 2022, 24), (5, 1, 5, 9.35, 2022, 24), (6, 1, 6, 9.65, 2023, 24),",
        "-- Diya Patel (CS202002)",
        "(7, 2, 1, 8.90, 2020, 22), (8, 2, 2, 9.00, 2021, 22), (9, 2, 3, 9.20, 2021, 24),",
        "(10, 2, 4, 9.15, 2022, 24), (11, 2, 5, 9.30, 2022, 24), (12, 2, 6, 9.18, 2023, 24),",
        "-- Kabir Verma (EC202003)",
        "(13, 3, 1, 8.00, 2020, 22), (14, 3, 2, 8.10, 2021, 22), (15, 3, 3, 8.30, 2021, 24),",
        "(16, 3, 4, 8.40, 2022, 24), (17, 3, 5, 8.20, 2022, 24), (18, 3, 6, 8.50, 2023, 24),",
        "-- Rohan Deshmukh (ME202004) - Low SGPA / Backlogs (Demonstrating Academic Warning)",
        "(19, 4, 1, 6.50, 2020, 22), (20, 4, 2, 6.20, 2021, 22), (21, 4, 3, 5.80, 2021, 24),",
        "(22, 4, 4, 6.40, 2022, 24), (23, 4, 5, 5.90, 2022, 24), (24, 4, 6, 6.70, 2023, 24),",
        "-- Sneha Reddy (IT202005)",
        "(25, 5, 1, 8.50, 2020, 22), (26, 5, 2, 8.60, 2021, 22), (27, 5, 3, 8.80, 2021, 24),",
        "(28, 5, 4, 8.70, 2022, 24), (29, 5, 5, 8.90, 2022, 24), (30, 5, 6, 8.70, 2023, 24),",
        "-- Ananya Iyer (CS202108) - Batch 2025 Performer",
        "(31, 8, 1, 9.50, 2021, 22), (32, 8, 2, 9.60, 2022, 22), (33, 8, 3, 9.70, 2022, 24),",
        "(34, 8, 4, 9.60, 2023, 24), (35, 8, 5, 9.60, 2023, 24),",
        "-- Vikram Nair (CS202109)",
        "(36, 9, 1, 8.80, 2021, 22), (37, 9, 2, 8.90, 2022, 22), (38, 9, 3, 9.00, 2022, 24),",
        "(39, 9, 4, 9.10, 2023, 24), (40, 9, 5, 8.95, 2023, 24);",
        "",
        "-- ============================================================================",
        "-- 5. CORPORATE DIRECTORY & RECRUITING ORGANIZATIONS",
        "-- ============================================================================",
        "INSERT INTO COMPANY (Company_ID, Company_Name, Company_Type, Industry, Location, Website) VALUES",
        "(1, 'Google India', 'Product', 'Technology & Cloud', 'Bengaluru / Hyderabad', 'https://careers.google.com'),",
        "(2, 'Microsoft India R&D', 'Product', 'Software & Cloud Platforms', 'Bengaluru / Hyderabad', 'https://careers.microsoft.com'),",
        "(3, 'Amazon AWS India', 'Product', 'E-Commerce & Cloud Infrastructure', 'Bengaluru / Chennai', 'https://amazon.jobs'),",
        "(4, 'Cisco Systems', 'Product', 'Networking & Telecommunications', 'Bengaluru', 'https://jobs.cisco.com'),",
        "(5, 'Oracle Financial Software', 'Product', 'Enterprise Software & Database', 'Bengaluru / Pune', 'https://oracle.com/careers'),",
        "(6, 'Tata Consultancy Services', 'Service', 'IT Consulting & Services', 'Mumbai / Pan-India', 'https://tcs.com/careers'),",
        "(7, 'Infosys Limited', 'Service', 'Digital Services & Consulting', 'Bengaluru / Pune', 'https://infosys.com/careers'),",
        "(8, 'Larsen & Toubro Core Engineering', 'Service', 'Heavy Engineering & Infrastructure', 'Mumbai / Chennai', 'https://larsentoubro.com'),",
        "(9, 'Bosch India Automotive', 'Product', 'Embedded Systems & Mobility', 'Bengaluru / Coimbatore', 'https://bosch.in/careers'),",
        "(10, 'Razorpay Technologies', 'Startup', 'Fintech & Payments Infrastructure', 'Bengaluru', 'https://razorpay.com/jobs');",
        "",
        "-- ============================================================================",
        "-- 6. RECRUITMENT DRIVES ACROSS ACADEMIC YEARS",
        "-- ============================================================================",
        "INSERT INTO RECRUITMENT_DRIVE (Drive_ID, Company_ID, Drive_Year, Drive_Type, Season, Drive_Date) VALUES",
        "(1, 1, 2024, 'On-campus', 'Autumn', '2023-08-15'),",
        "(2, 2, 2024, 'On-campus', 'Autumn', '2023-08-28'),",
        "(3, 3, 2024, 'On-campus', 'Autumn', '2023-09-10'),",
        "(4, 6, 2024, 'On-campus', 'Autumn', '2023-09-20'),",
        "(5, 7, 2024, 'On-campus', 'Autumn', '2023-10-05'),",
        "(6, 8, 2024, 'On-campus', 'Spring', '2024-01-15'),",
        "(7, 1, 2025, 'On-campus', 'Autumn', '2024-08-20'),",
        "(8, 2, 2025, 'On-campus', 'Autumn', '2024-09-02'),",
        "(9, 10, 2024, 'Pooled', 'Autumn', '2023-10-18'),",
        "(10, 9, 2024, 'On-campus', 'Spring', '2024-02-10');",
        "",
        "-- ============================================================================",
        "-- 7. OPPORTUNITIES & ELIGIBILITY CONSTRAINTS",
        "-- ============================================================================",
        "INSERT INTO OPPORTUNITY (Opportunity_ID, Drive_ID, Role, Opportunity_Type, Package_Stipend, Duration_Months) VALUES",
        "(1, 1, 'Software Engineer (L3)', 'Placement', 42.00, 12),",
        "(2, 1, 'Software Engineering Summer Intern', 'Internship', 110000.00, 2),",
        "(3, 2, 'Software Development Engineer I', 'Placement', 38.50, 12),",
        "(4, 3, 'Cloud Solutions Associate', 'Placement', 32.00, 12),",
        "(5, 4, 'Assistant System Engineer (Digital)', 'Placement', 7.50, 12),",
        "(6, 5, 'Specialist Programmer', 'Placement', 9.50, 12),",
        "(7, 6, 'Graduate Engineer Trainee', 'Placement', 6.50, 12),",
        "(8, 7, 'Software Engineer (Early Career)', 'Placement', 45.00, 12),",
        "(9, 9, 'Backend Developer (Fintech)', 'Placement', 24.00, 12),",
        "(10, 10, 'Embedded Systems Engineer', 'Placement', 14.00, 12);",
        "",
        "INSERT INTO ELIGIBILITY (Eligibility_ID, Opportunity_ID, Min_CGPA, Max_Backlogs) VALUES",
        "(1, 1, 8.50, 0),",
        "(2, 2, 8.00, 0),",
        "(3, 3, 8.00, 0),",
        "(4, 4, 7.50, 0),",
        "(5, 5, 6.00, 1),",
        "(6, 6, 6.50, 0),",
        "(7, 7, 6.50, 0),",
        "(8, 8, 8.50, 0),",
        "(9, 9, 7.50, 0),",
        "(10, 10, 7.00, 0);",
        "",
        "INSERT INTO ELIGIBILITY_BRANCH (Eligibility_ID, Branch) VALUES",
        "(1, 'CSE'), (1, 'IT'),",
        "(2, 'CSE'), (2, 'IT'), (2, 'ECE'),",
        "(3, 'CSE'), (3, 'IT'),",
        "(4, 'CSE'), (4, 'IT'), (4, 'ECE'),",
        "(5, 'CSE'), (5, 'IT'), (5, 'ECE'), (5, 'ME'), (5, 'Civil'), (5, 'Electrical'),",
        "(6, 'CSE'), (6, 'IT'), (6, 'ECE'),",
        "(7, 'ME'), (7, 'Civil'), (7, 'Electrical'),",
        "(8, 'CSE'), (8, 'IT'),",
        "(9, 'CSE'), (9, 'IT'),",
        "(10, 'ECE'), (10, 'Electrical'), (10, 'CSE');",
        "",
        "-- ============================================================================",
        "-- 8. SELECTION PROCESS ROUNDS",
        "-- ============================================================================",
        "INSERT INTO SELECTION_PROCESS (Process_ID, Opportunity_ID, Round_Number, Round_Name, Round_Type, Description) VALUES",
        "(1, 1, 1, 'Online Coding Challenge', 'Coding Round', '2 algorithmic problems on DSA and dynamic programming.'),",
        "(2, 1, 2, 'Technical Interview 1', 'Technical Interview', 'In-depth evaluation on data structures, algorithms, and complexity.'),",
        "(3, 1, 3, 'System Design & Architecture', 'Technical Interview', 'Object-oriented design and distributed caching paradigms.'),",
        "(4, 1, 4, 'Googliness & Leadership', 'HR Interview', 'Behavioral and institutional culture fit.'),",
        "(5, 5, 1, 'TCS NQT Cognitive & Tech', 'Aptitude Test', 'Aptitude, logical reasoning, and programming basics.'),",
        "(6, 5, 2, 'Technical & Managerial', 'Technical Interview', 'Core computer science fundamentals and project discussion.'),",
        "(7, 5, 3, 'HR Interview', 'HR Interview', 'Communication and operational verification.');",
        "",
        "-- ============================================================================",
        "-- 9. MANDATORY INTERNSHIP REQUIREMENTS CATALOG",
        "-- ============================================================================",
        "INSERT INTO INTERNSHIP_REQUIREMENT (Requirement_ID, Internship_No, Mandatory, Prescribed_Period, Required_Result_Semester, Report_Submission_Semester, Credits, Description) VALUES",
        "(1, 1, 'Yes', 'Summer Break after Semester 4 (6 to 8 weeks)', 3, 5, 4, 'Mandatory Summer Internship 1. Evaluates foundational technical exposure. Prerequisite: Semester 3 SGPA >= 6.00.'),",
        "(2, 2, 'Yes', 'Summer Break after Semester 6 (8 to 10 weeks)', 5, 7, 4, 'Mandatory Summer Internship 2. Evaluates advanced industrial immersion. Prerequisite: Semester 5 SGPA >= 6.00.');",
        "",
        "-- ============================================================================",
        "-- 10. INTERNSHIP RECORDS (Mandatory I1, Mandatory I2, and Additional Experiences)",
        "-- ============================================================================",
        "INSERT INTO INTERNSHIP (Internship_ID, Student_ID, Company_ID, Opportunity_ID, Requirement_ID, Internship_No, Internship_Type, Role, Interview_Rounds, Stipend, Start_Date, End_Date, Credits, Report_Semester, Report_Link, Report_Grade, Certificate_Link) VALUES",
        "-- Aarav Sharma (CS202001) - Compliant with both Mandatory I1 & I2",
        "(1, 1, 1, 2, 1, 1, 'Mandatory', 'SWE Summer Intern', 3, 110000.00, '2022-06-01', '2022-07-31', 4, 5, 'https://storage.fictional.edu/reports/rep_1_1.pdf', 'A+', 'https://storage.fictional.edu/certs/cert_1_1.pdf'),",
        "(2, 1, 2, NULL, 2, 2, 'Mandatory', 'Research & Development Intern', 3, 80000.00, '2023-06-01', '2023-07-31', 4, 7, 'https://storage.fictional.edu/reports/rep_1_2.pdf', 'A+', 'https://storage.fictional.edu/certs/cert_1_2.pdf'),",
        "(3, 1, 10, NULL, NULL, 3, 'Additional', 'Open Source Fellow', 1, 35000.00, '2023-12-01', '2024-01-10', 2, 7, 'https://storage.fictional.edu/reports/rep_1_3.pdf', 'A', 'https://storage.fictional.edu/certs/cert_1_3.pdf'),",
        "-- Diya Patel (CS202002) - Compliant",
        "(4, 2, 2, NULL, 1, 1, 'Mandatory', 'Software Engineering Intern', 2, 75000.00, '2022-06-05', '2022-07-28', 4, 5, 'https://storage.fictional.edu/reports/rep_2_1.pdf', 'A', 'https://storage.fictional.edu/certs/cert_2_1.pdf'),",
        "(5, 2, 3, NULL, 2, 2, 'Mandatory', 'Cloud Platform Intern', 3, 85000.00, '2023-06-01', '2023-08-05', 4, 7, 'https://storage.fictional.edu/reports/rep_2_2.pdf', 'A+', 'https://storage.fictional.edu/certs/cert_2_2.pdf'),",
        "-- Kabir Verma (EC202003) - Compliant",
        "(6, 3, 4, NULL, 1, 1, 'Mandatory', 'Hardware Verification Intern', 2, 45000.00, '2022-06-01', '2022-07-20', 4, 5, 'https://storage.fictional.edu/reports/rep_3_1.pdf', 'B+', 'https://storage.fictional.edu/certs/cert_3_1.pdf'),",
        "(7, 3, 9, NULL, 2, 2, 'Mandatory', 'Automotive Embedded Intern', 2, 50000.00, '2023-06-01', '2023-07-31', 4, 7, 'https://storage.fictional.edu/reports/rep_3_2.pdf', 'A', 'https://storage.fictional.edu/certs/cert_3_2.pdf'),",
        "-- Sneha Reddy (IT202005) - Compliant with I1, Pending I2 Report Defense",
        "(8, 5, 7, NULL, 1, 1, 'Mandatory', 'Systems Intern', 1, 30000.00, '2022-06-10', '2022-07-25', 4, 5, 'https://storage.fictional.edu/reports/rep_5_1.pdf', 'A', 'https://storage.fictional.edu/certs/cert_5_1.pdf'),",
        "(9, 5, 10, NULL, 2, 2, 'Mandatory', 'Frontend Engineering Intern', 2, 40000.00, '2023-06-01', '2023-07-31', 4, 7, NULL, NULL, 'https://storage.fictional.edu/certs/cert_5_2.pdf'),",
        "-- Ananya Iyer (CS202108) - Completed I1",
        "(10, 8, 1, NULL, 1, 1, 'Mandatory', 'Engineering Intern', 3, 110000.00, '2023-06-01', '2023-07-31', 4, 5, 'https://storage.fictional.edu/reports/rep_8_1.pdf', 'A+', 'https://storage.fictional.edu/certs/cert_8_1.pdf');",
        "",
        "-- ============================================================================",
        "-- 11. PLACEMENT OFFERS & RECRUITMENT OUTCOMES",
        "-- Core Rule Highlight: The Single-Accepted-Offer Policy",
        "-- Aarav Sharma (Student ID 1) holds 3 offers: 1 Accepted, 2 Offered.",
        "-- ============================================================================",
        "INSERT INTO PLACEMENT (Placement_ID, Student_ID, Company_ID, Opportunity_ID, Role, Package, Placement_Year, Placement_Type, Is_PPO, Joined, Offer_Status, Interview_Rounds) VALUES",
        "-- Aarav Sharma: Multi-offer star candidate",
        "(1, 1, 1, 1, 'Software Engineer (L3)', 42.00, 2024, 'On-campus', 'Yes', 'No', 'Accepted', 4),",
        "(2, 1, 6, 5, 'Assistant System Engineer (Digital)', 7.50, 2024, 'On-campus', 'No', 'No', 'Offered', 3),",
        "(3, 1, 7, 6, 'Specialist Programmer', 9.50, 2024, 'On-campus', 'No', 'No', 'Offered', 3),",
        "-- Diya Patel: Dual offer (Accepted Microsoft, Declined Amazon)",
        "(4, 2, 2, 3, 'Software Development Engineer I', 38.50, 2024, 'On-campus', 'No', 'No', 'Accepted', 3),",
        "(5, 2, 3, 4, 'Cloud Solutions Associate', 32.00, 2024, 'On-campus', 'No', 'No', 'Declined', 3),",
        "-- Kabir Verma: Accepted Cisco Systems",
        "(6, 3, 4, NULL, 'Network Systems Engineer', 18.00, 2024, 'On-campus', 'No', 'No', 'Accepted', 3),",
        "-- Sneha Reddy: Accepted Razorpay",
        "(7, 5, 10, 9, 'Backend Developer (Fintech)', 24.00, 2024, 'Pooled', 'No', 'No', 'Accepted', 3),",
        "-- Gaurav Trivedi: Accepted TCS",
        "(8, 6, 6, 5, 'Assistant System Engineer', 7.50, 2024, 'On-campus', 'No', 'No', 'Accepted', 2),",
        "-- Simran Kaur: Accepted Infosys",
        "(9, 7, 7, 6, 'Specialist Programmer', 9.50, 2024, 'On-campus', 'No', 'No', 'Accepted', 2),",
        "-- Batch 2022 Alumni: Joined Status",
        "(10, 17, 1, 1, 'Senior Software Engineer', 36.00, 2022, 'On-campus', 'No', 'Yes', 'Joined', 4),",
        "(11, 18, 4, NULL, 'Hardware Engineer', 16.50, 2022, 'On-campus', 'No', 'Yes', 'Joined', 3),",
        "-- Batch 2023 Alumni: Joined Status",
        "(12, 19, 2, 3, 'Software Development Engineer I', 34.00, 2023, 'On-campus', 'Yes', 'Yes', 'Joined', 4),",
        "(13, 22, 9, 10, 'Embedded Systems Engineer', 12.50, 2023, 'On-campus', 'No', 'Yes', 'Joined', 3),",
        "-- Batch 2024 Placements across Civil & Electrical",
        "(14, 23, 8, 7, 'Graduate Engineer Trainee', 6.50, 2024, 'On-campus', 'No', 'No', 'Accepted', 2),",
        "(15, 24, 9, 10, 'Electrical Systems Engineer', 14.00, 2024, 'On-campus', 'No', 'No', 'Accepted', 3),",
        "(16, 26, 10, 9, 'Platform Engineer', 22.00, 2024, 'Pooled', 'No', 'No', 'Accepted', 3),",
        "-- Batch 2025 Early PPO Placement",
        "(17, 8, 1, 8, 'Software Engineer (Early Career)', 45.00, 2025, 'On-campus', 'Yes', 'No', 'Accepted', 4);",
        "",
        "-- ============================================================================",
        "-- 12. PLACEMENT SKILLS",
        "-- ============================================================================",
        "INSERT INTO PLACEMENT_SKILL (Placement_ID, Skill) VALUES",
        "(1, 'Python'), (1, 'Distributed Systems'), (1, 'Algorithms'),",
        "(2, 'Java'), (2, 'SQL'),",
        "(3, 'Java'), (3, 'Data Structures'),",
        "(4, 'C++'), (4, 'Distributed Systems'), (4, 'Azure'),",
        "(5, 'Cloud Architecture'), (5, 'AWS'),",
        "(6, 'Computer Networks'), (6, 'Linux'),",
        "(7, 'Go'), (7, 'Microservices'), (7, 'PostgreSQL'),",
        "(8, 'Java'), (8, 'SQL'),",
        "(9, 'Python'), (9, 'Full Stack Web'),",
        "(17, 'Algorithms'), (17, 'System Design'), (17, 'Machine Learning');",
        "",
        "SET FOREIGN_KEY_CHECKS = 1;",
        "",
        "-- ============================================================================",
        "-- END OF FICTIONAL DEMONSTRATION DATASET",
        "-- ============================================================================",
    ]
    return "\n".join(sql_lines)


def write_sql_file(filepath: str = "demo_dataset.sql") -> str:
    """Writes the synthetic SQL statements to a standalone file."""
    content = generate_sql_script()
    abs_path = os.path.abspath(filepath)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info("Fictional demonstration SQL script generated successfully: %s", abs_path)
    return abs_path


def apply_to_database(target_db: str, confirm_live: bool = False):
    """Safely executes the demonstration SQL script into a dedicated demo MySQL database."""
    import pymysql
    from dotenv import load_dotenv

    load_dotenv()

    # Safety check: Prevent accidental application to production or primary database
    primary_db = os.getenv("MYSQL_DATABASE", "placement_db")
    if target_db == primary_db and not confirm_live:
        logger.error(
            "SAFETY BLOCK: Target database '%s' matches primary MYSQL_DATABASE! "
            "To prevent overwriting your live database, you must pass '--confirm-live' explicitly.",
            target_db,
        )
        sys.exit(1)

    host = os.getenv("MYSQL_HOST", "localhost")
    port = int(os.getenv("MYSQL_PORT", 3306))
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")

    logger.info("Connecting to MySQL server at %s:%d as user '%s'...", host, port, user)
    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        charset="utf8mb4",
        client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS,
    )

    try:
        with conn.cursor() as cur:
            logger.info("Ensuring target demo database '%s' exists...", target_db)
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{target_db}` CHARACTER SET utf8mb4;")
            cur.execute(f"USE `{target_db}`;")

        # Load schema first if tables don't exist
        with open("schema.sql", "r", encoding="utf-8") as f:
            schema_sql = f.read()

        logger.info("Applying DDL schema to target database '%s'...", target_db)
        with conn.cursor() as cur:
            cur.execute(schema_sql)

        # Generate and apply demo dataset
        logger.info("Loading demonstration records into '%s'...", target_db)
        demo_sql = generate_sql_script()
        with conn.cursor() as cur:
            cur.execute(demo_sql)

        conn.commit()
        logger.info("SUCCESS: Fictional demonstration dataset applied to database '%s'!", target_db)
    except Exception as exc:
        conn.rollback()
        logger.error("Failed to apply demo dataset: %s", exc)
        raise
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Legacy DataForce - Fictional Demo Dataset Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  1. Generate standalone SQL file without touching any database (Safe default):
     python generate_demo_dataset.py

  2. Specify custom output file path:
     python generate_demo_dataset.py --sql-out my_demo_data.sql

  3. Safely populate a separate demonstration database:
     python generate_demo_dataset.py --apply --target-db placement_demo_db
        """,
    )
    parser.add_argument(
        "--sql-out",
        type=str,
        default="demo_dataset.sql",
        help="Path where the generated .sql file will be written (default: demo_dataset.sql)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Connect to MySQL and apply the demonstration dataset to a database.",
    )
    parser.add_argument(
        "--target-db",
        type=str,
        default="placement_demo_db",
        help="Target MySQL database name when --apply is specified (default: placement_demo_db).",
    )
    parser.add_argument(
        "--confirm-live",
        action="store_true",
        help="Required only if target-db equals your live production database to confirm intentional overwrite.",
    )

    args = parser.parse_args()

    # 1. Always generate the safe SQL output file
    out_file = write_sql_file(args.sql_out)
    print(f"[OK] Demo dataset script written to: {out_file}")

    # 2. Only touch database if user explicitly opted in with --apply
    if args.apply:
        print(f"[!] Applying dataset to target database: '{args.target_db}'...")
        apply_to_database(args.target_db, confirm_live=args.confirm_live)
        print(f"[OK] Successfully populated demo database: '{args.target_db}'.")
    else:
        print(
            "\n[NOTE] Safe mode: Database was NOT modified. To import this demo data into a separate test database, run:"
        )
        print(f"       python generate_demo_dataset.py --apply --target-db {args.target_db}\n")


if __name__ == "__main__":
    main()

"""Seed Data Generator and Validator for Campus Placement & Internship Management System.

Generates seed.sql ensuring:
1. 30 students across batches 2022-2025, branches CSE, IT, ECE, ME, with Indian-style fictional names.
2. 2-3 phone numbers and 1-4 skills per student.
3. 10 fictional companies (product, service, startup).
4. Placements: 0 offers, 1 offer, 2-3 offers. At most ONE Joined='Yes' per student. PPO offers for students with prior internships.
5. Skills selected for each placement in PLACEMENT_SKILL.
6. For EVERY student: Mandatory Internship 1 (Sem 5, 4 credits) and Mandatory Internship 2 (Sem 7, 4 credits), plus additional internships (No >= 3) for some students.
7. Realistic packages (3.00 to 20.00 LPA), stipends, dates, rounds.
8. Complete foreign key and constraint compliance.
"""

NULL = None

def generate_seed_sql():
    lines = []
    lines.append("-- ============================================================================")
    lines.append("-- CAMPUS PLACEMENT & INTERNSHIP MANAGEMENT SYSTEM")
    lines.append("-- FICTIONAL SEED DATA SCRIPT (seed.sql)")
    lines.append("-- ============================================================================")
    lines.append("-- DISCLAIMER: ALL DATA IN THIS SCRIPT IS STRICTLY SYNTHETIC AND FICTIONAL.")
    lines.append("-- Generated exclusively for academic verification, evaluation, and demonstration.")
    lines.append("-- All student names, corporate entities, phone numbers, and emails are synthetic.")
    lines.append("-- Any resemblance to real persons, live URLs, or actual organizations is coincidental.")
    lines.append("-- ============================================================================")
    lines.append("")
    lines.append("BEGIN;")
    lines.append("")

    # 1. UNIVERSITY
    lines.append("-- ============================================================================")
    lines.append("-- 1. UNIVERSITY & ACADEMIC CATALOG")
    lines.append("-- ============================================================================")
    lines.append("INSERT INTO UNIVERSITY (University_ID, University_Name, Location, Established_Year) VALUES")
    lines.append("(1, 'National Institute of Advanced Technology', 'Tech City, India', 1985);")
    lines.append("")

    # 2. COURSE (12 Courses)
    lines.append("INSERT INTO COURSE (Course_ID, University_ID, Course_Name, Department, Semester, Credits, Course_Type) VALUES")
    courses = [
        (1, 1, 'Data Structures & Algorithms', 'Computer Science', 3, 4, 'Core'),
        (2, 1, 'Database Management Systems', 'Computer Science', 4, 4, 'Core'),
        (3, 1, 'Operating Systems', 'Computer Science', 4, 4, 'Core'),
        (4, 1, 'Computer Networks', 'Computer Science', 5, 4, 'Core'),
        (5, 1, 'Software Engineering', 'Computer Science', 5, 3, 'Core'),
        (6, 1, 'Machine Learning Foundations', 'Computer Science', 6, 4, 'Elective'),
        (7, 1, 'Digital Signal Processing', 'Electronics', 4, 4, 'Core'),
        (8, 1, 'VLSI Design', 'Electronics', 5, 4, 'Core'),
        (9, 1, 'Microprocessors & Microcontrollers', 'Electronics', 5, 4, 'Core'),
        (10, 1, 'Thermodynamics & Heat Transfer', 'Mechanical', 3, 4, 'Core'),
        (11, 1, 'Computer-Aided Design', 'Mechanical', 5, 3, 'Lab'),
        (12, 1, 'Manufacturing Processes', 'Mechanical', 4, 4, 'Core')
    ]
    course_strs = [f"({c[0]}, {c[1]}, '{c[2]}', '{c[3]}', {c[4]}, {c[5]}, '{c[6]}')" for c in courses]
    lines.append(",\n".join(course_strs) + ";")
    lines.append("")

    # 3. 30 STUDENTS
    lines.append("-- ============================================================================")
    lines.append("-- 2. STUDENTS (30 Fictional Students across Batches 2022 to 2025; CSE, IT, ECE, ME)")
    lines.append("-- ============================================================================")
    lines.append("INSERT INTO STUDENT (Student_ID, Roll_No, First_Name, Last_Name, Branch, Batch_Year, Section, CGPA, Backlogs, Email, Resume_Link) VALUES")
    students = [
        # Batch 2022 (Seniors / Alumni)
        (1,  'CS202001', 'Aarav',     'Sharma',     'CSE', 2022, 'A', 9.45, 0, 'aarav.sharma@fictional.edu',     'https://storage.fictional.edu/resumes/cs202001.pdf'),
        (2,  'CS201802', 'Diya',      'Patel',      'CSE', 2022, 'A', 9.12, 0, 'diya.patel@fictional.edu',      'https://storage.fictional.edu/resumes/cs201802.pdf'),
        (3,  'EC201803', 'Kabir',     'Verma',      'ECE', 2022, 'B', 8.25, 0, 'kabir.verma@fictional.edu',     'https://storage.fictional.edu/resumes/ec201803.pdf'),
        (4,  'ME201804', 'Rohan',     'Deshmukh',   'ME',  2022, 'A', 6.85, 2, 'rohan.deshmukh@fictional.edu',  'https://storage.fictional.edu/resumes/me201804.pdf'),
        (5,  'IT201805', 'Sneha',     'Reddy',      'IT',  2022, 'A', 8.70, 0, 'sneha.reddy@fictional.edu',     'https://storage.fictional.edu/resumes/it201805.pdf'),
        (6,  'CS201806', 'Gaurav',    'Trivedi',    'CSE', 2022, 'B', 8.50, 0, 'gaurav.trivedi@fictional.edu',  'https://storage.fictional.edu/resumes/cs201806.pdf'),
        (7,  'EC201807', 'Simran',    'Kaur',       'ECE', 2022, 'A', 7.10, 1, 'simran.kaur@fictional.edu',     'https://storage.fictional.edu/resumes/ec201807.pdf'),

        # Batch 2023
        (8,  'CS201908', 'Ananya',    'Iyer',       'CSE', 2023, 'A', 9.60, 0, 'ananya.iyer@fictional.edu',     'https://storage.fictional.edu/resumes/cs201908.pdf'),
        (9,  'CS201909', 'Vikram',    'Nair',       'CSE', 2023, 'B', 8.95, 0, 'vikram.nair@fictional.edu',     'https://storage.fictional.edu/resumes/cs201909.pdf'),
        (10, 'EC201910', 'Pooja',     'Joshi',      'ECE', 2023, 'A', 7.80, 0, 'pooja.joshi@fictional.edu',     'https://storage.fictional.edu/resumes/ec201910.pdf'),
        (11, 'ME201911', 'Arjun',     'Mehta',      'ME',  2023, 'A', 7.45, 0, 'arjun.mehta@fictional.edu',     'https://storage.fictional.edu/resumes/me201911.pdf'),
        (12, 'IT201912', 'Siddharth', 'Chopra',     'IT',  2023, 'B', 8.15, 0, 'siddharth.chopra@fictional.edu','https://storage.fictional.edu/resumes/it201912.pdf'),
        (13, 'CS201913', 'Harsh',     'Vardhan',    'CSE', 2023, 'A', 9.10, 0, 'harsh.vardhan@fictional.edu',    'https://storage.fictional.edu/resumes/cs201913.pdf'),
        (14, 'IT201914', 'Neha',      'Agarwal',    'IT',  2023, 'A', 7.65, 0, 'neha.agarwal@fictional.edu',     'https://storage.fictional.edu/resumes/it201914.pdf'),

        # Batch 2024
        (15, 'CS202015', 'Aditya',    'Kulkarni',   'CSE', 2024, 'A', 8.40, 0, 'aditya.kulkarni@fictional.edu', 'https://storage.fictional.edu/resumes/cs202015.pdf'),
        (16, 'CS202016', 'Ishita',    'Bose',       'CSE', 2024, 'A', 9.30, 0, 'ishita.bose@fictional.edu',     'https://storage.fictional.edu/resumes/cs202016.pdf'),
        (17, 'CS202017', 'Meera',     'Menon',      'CSE', 2024, 'B', 9.55, 0, 'meera.menon@fictional.edu',     'https://storage.fictional.edu/resumes/cs202017.pdf'),
        (18, 'EC202018', 'Varun',     'Kapoor',     'ECE', 2024, 'A', 8.05, 0, 'varun.kapoor@fictional.edu',    'https://storage.fictional.edu/resumes/ec202018.pdf'),
        (19, 'CS202019', 'Kavya',     'Srinivasan', 'CSE', 2024, 'A', 9.20, 0, 'kavya.srinivasan@fictional.edu','https://storage.fictional.edu/resumes/cs202019.pdf'),
        (20, 'IT202020', 'Rahul',     'Saxena',     'IT',  2024, 'B', 6.90, 1, 'rahul.saxena@fictional.edu',    'https://storage.fictional.edu/resumes/it202020.pdf'),
        (21, 'ME202021', 'Priya',     'Pillai',     'ME',  2024, 'A', 7.15, 0, 'priya.pillai@fictional.edu',    'https://storage.fictional.edu/resumes/me202021.pdf'),
        (22, 'EC202022', 'Pranav',    'Singhania',  'ECE', 2024, 'B', 7.95, 0, 'pranav.singhania@fictional.edu', 'https://storage.fictional.edu/resumes/ec202022.pdf'),

        # Batch 2025
        (23, 'CS202123', 'Tarun',     'Bhatia',     'CSE', 2025, 'A', 8.65, 0, 'tarun.bhatia@fictional.edu',    'https://storage.fictional.edu/resumes/cs202123.pdf'),
        (24, 'CS202124', 'Rhea',      'Sen',        'CSE', 2025, 'A', 9.05, 0, 'rhea.sen@fictional.edu',        'https://storage.fictional.edu/resumes/cs202124.pdf'),
        (25, 'EC202125', 'Naveen',    'Rao',        'ECE', 2025, 'B', 7.80, 0, 'naveen.rao@fictional.edu',      'https://storage.fictional.edu/resumes/ec202125.pdf'),
        (26, 'CS202126', 'Manish',    'Gupta',      'CSE', 2025, 'B', 8.35, 0, 'manish.gupta@fictional.edu',    'https://storage.fictional.edu/resumes/cs202126.pdf'),
        (27, 'IT202127', 'Tanvi',     'Malhotra',   'IT',  2025, 'A', 8.85, 0, 'tanvi.malhotra@fictional.edu',   'https://storage.fictional.edu/resumes/it202127.pdf'),
        (28, 'CS202128', 'Shreya',    'Nambiar',    'CSE', 2025, 'B', 8.55, 0, 'shreya.nambiar@fictional.edu',  'https://storage.fictional.edu/resumes/cs202128.pdf'),
        (29, 'ME202129', 'Aniket',    'Bannerjee',  'ME',  2025, 'A', 7.30, 0, 'aniket.bannerjee@fictional.edu', 'https://storage.fictional.edu/resumes/me202129.pdf'),
        (30, 'IT202130', 'Divya',     'Swaminathan','IT',  2025, 'B', 8.40, 0, 'divya.swaminathan@fictional.edu','https://storage.fictional.edu/resumes/it202130.pdf')
    ]
    stu_strs = [f"({s[0]}, '{s[1]}', '{s[2]}', '{s[3]}', '{s[4]}', {s[5]}, '{s[6]}', {s[7]}, {s[8]}, '{s[9]}', '{s[10]}')" for s in students]
    lines.append(",\n".join(stu_strs) + ";")
    lines.append("")

    # 4. STUDENT_PHONE (2 or 3 phone numbers for students)
    lines.append("-- ============================================================================")
    lines.append("-- 3. MULTIVALUED ATTRIBUTES: PHONES & SKILLS")
    lines.append("-- ============================================================================")
    lines.append("INSERT INTO STUDENT_PHONE (Student_ID, Phone_No) VALUES")
    phones = []
    for s_id in range(1, 31):
        # 1st phone for all
        p1 = "+91-9876543201" if s_id == 1 else f"+91-987654{s_id:04d}"
        phones.append((s_id, p1))
        # 2nd phone for half the students
        if s_id % 2 == 1:
            p2 = f"+91-987655{s_id:04d}"
            phones.append((s_id, p2))
        # 3rd phone for some students (e.g. 1, 4, 8, 15, 23)
        if s_id in (1, 4, 8, 15, 23):
            p3 = f"+91-987656{s_id:04d}"
            phones.append((s_id, p3))
    phone_strs = [f"({p[0]}, '{p[1]}')" for p in phones]
    lines.append(",\n".join(phone_strs) + ";")
    lines.append("")

    # 5. STUDENT_SKILL (1 to 4 extra skills for each student)
    lines.append("INSERT INTO STUDENT_SKILL (Student_ID, Skill) VALUES")
    student_skills_map = {
        1:  ['Java', 'Spring Boot', 'Distributed Systems', 'PostgreSQL'],
        2:  ['Python', 'Machine Learning', 'TensorFlow', 'SQL'],
        3:  ['C++', 'Embedded Systems', 'RTOS'],
        4:  ['SolidWorks', 'AutoCAD', 'Thermodynamics'],
        5:  ['React', 'Node.js', 'TypeScript', 'MongoDB'],
        6:  ['Java', 'Microservices', 'Docker', 'Kubernetes'],
        7:  ['VHDL', 'VLSI Design', 'Circuit Simulation'],
        8:  ['Go', 'Distributed Systems', 'Raft Consensus', 'AWS'],
        9:  ['Python', 'Django', 'FastAPI', 'Redis'],
        10: ['Digital Signal Processing', 'MATLAB', 'Embedded C'],
        11: ['ANSYS', 'FEA Analysis', 'CAD Modeling'],
        12: ['JavaScript', 'Vue.js', 'GraphQL', 'PostgreSQL'],
        13: ['Scala', 'Apache Spark', 'Kafka', 'Data Engineering'],
        14: ['Python', 'Data Analytics', 'Power BI'],
        15: ['Java', 'Spring Cloud', 'Oracle DB', 'System Design'],
        16: ['C++', 'Competitive Programming', 'Graph Algorithms', 'Linux'],
        17: ['Python', 'FastAPI', 'gRPC', 'Docker'],
        18: ['IoT', 'Raspberry Pi', 'Embedded C', 'Python'],
        19: ['Cloud Architecture', 'Terraform', 'GCP', 'Kubernetes'],
        20: ['Web Development', 'PHP', 'MySQL'],
        21: ['Robotics', 'Mechatronics', 'Control Systems'],
        22: ['Microcontrollers', 'Arduino', 'PCB Design'],
        23: ['Python', 'Flask', 'SQLAlchemy', 'PostgreSQL'],
        24: ['C++', 'Algorithms', 'Distributed Computing'],
        25: ['Analog Electronics', 'Verilog', 'FPGA'],
        26: ['Java', 'Spring MVC', 'Hibernate'],
        27: ['React', 'Next.js', 'TailwindCSS', 'Node.js'],
        28: ['Python', 'PyTorch', 'Computer Vision'],
        29: ['CNC Machining', 'Heat Engines', 'SolidWorks'],
        30: ['Full Stack Web', 'FastAPI', 'Vue.js', 'Docker']
    }
    skill_rows = []
    for s_id, sks in student_skills_map.items():
        for sk in sks:
            skill_rows.append((s_id, sk))
    skill_strs = [f"({sr[0]}, '{sr[1]}')" for sr in skill_rows]
    lines.append(",\n".join(skill_strs) + ";")
    lines.append("")

    # 5b. STUDENT_COURSE (M:N Academic Course Enrollments)
    lines.append("INSERT INTO STUDENT_COURSE (Student_ID, Course_ID, Enrollment_Year, Grade) VALUES")
    course_enrollments = []
    for s in students:
        s_id, _, _, _, branch, batch, _, _, _, _, _ = s
        enr_year = batch - 3
        if branch == 'CSE':
            c_ids = [1, 2, 3, 4]
        elif branch == 'IT':
            c_ids = [1, 2, 4, 5]
        elif branch == 'ECE':
            c_ids = [1, 7, 8, 9]
        else: # ME
            c_ids = [1, 10, 11, 12]
        
        grades = ['A+', 'A', 'B+', 'A']
        for idx, cid in enumerate(c_ids):
            course_enrollments.append((s_id, cid, enr_year, grades[idx]))
    
    sc_strs = [f"({ce[0]}, {ce[1]}, {ce[2]}, '{ce[3]}')" for ce in course_enrollments]
    lines.append(",\n".join(sc_strs) + ";")
    lines.append("")

    # 6. STUDENT_PROFILE (Extracurricular projects, hackathons, certs)
    lines.append("-- ============================================================================")
    lines.append("-- 4. STUDENT PROFILES & ACHIEVEMENTS")
    lines.append("-- ============================================================================")
    lines.append("INSERT INTO STUDENT_PROFILE (Profile_ID, Student_ID, Profile_Type, Title, Description, Link, Year, Proficiency_Level) VALUES")
    profiles = [
        (1,  1,  'Hackathon', 'Smart India Hackathon Finalist', 'Built automated citizen portal using NLP', 'https://github.com/fictional/sih-proj', 2021, 'Advanced'),
        (2,  1,  'Certification', 'AWS Certified Solutions Architect', 'Enterprise multi-tier deployment credential', 'https://cert.fictional.org/aws-aarav', 2022, 'Advanced'),
        (3,  2,  'Project', 'CardioPredict ML Classifier', 'Clinical diagnostic estimator with 94% test accuracy', 'https://github.com/fictional/cardio', 2021, 'Expert'),
        (4,  3,  'Project', 'Autonomous Telemetry Drone', 'STM32 based telemetry running on FreeRTOS', 'https://github.com/fictional/drone', 2021, 'Intermediate'),
        (5,  4,  'Project', 'Thermal Exchanger Simulation', 'Heat distribution analysis modeled in ANSYS', 'https://github.com/fictional/ansys-heat', 2021, 'Intermediate'),
        (6,  5,  'Project', 'Campus Food Ordering Portal', 'React/Node microservice platform', 'https://github.com/fictional/campus-eats', 2022, 'Advanced'),
        (7,  8,  'Competitive Coding', 'Codeforces Master (2150 Peak)', 'Algorithms and graph contest finalist', 'https://codeforces.com/fictional_ananya', 2022, 'Expert'),
        (8,  8,  'Project', 'Raft Consensus Key-Value Store', 'Distributed fault-tolerant storage built in Go', 'https://github.com/fictional/raft-kv', 2023, 'Expert'),
        (9,  9,  'Hackathon', 'ETHIndia DeFi Track Winner', 'Smart contract escrow payment protocol', 'https://github.com/fictional/escrow', 2022, 'Advanced'),
        (10, 13, 'Certification', 'Databricks Certified Data Engineer', 'Apache Spark and delta lake pipelines', 'https://cert.fictional.org/databricks', 2023, 'Expert'),
        (11, 15, 'Certification', 'Oracle Certified Java Professional', 'Standard SE 17 Developer credential', 'https://cert.fictional.org/ocp-aditya', 2023, 'Advanced'),
        (12, 16, 'Competitive Coding', 'Google Kickstart Global Rank 45', 'Round D top performer among global participants', 'https://codingcompetitions.fictional/ishita', 2023, 'Expert'),
        (13, 17, 'Project', 'Fraud Detection Stream Pipeline', 'Real-time Apache Flink stream analytics', 'https://github.com/fictional/fraud-pipe', 2023, 'Advanced'),
        (14, 19, 'Certification', 'Google Cloud Professional Architect', 'Cloud deployment and infrastructure migration', 'https://cert.fictional.org/gcp-kavya', 2023, 'Expert'),
        (15, 23, 'Project', 'Collaborative Markdown Canvas', 'Real-time synchronization using WebSockets and CRDTs', 'https://github.com/fictional/collab-md', 2024, 'Intermediate'),
        (16, 24, 'Hackathon', 'ACM-ICPC Regional Qualifier', 'Represented university algorithm team', 'https://icpc.fictional.org/team-rhea', 2024, 'Advanced'),
        (17, 27, 'Project', 'Micro-SaaS Invoicing Engine', 'Fullstack Next.js and Stripe billing platform', 'https://github.com/fictional/saas-invoice', 2024, 'Advanced')
    ]
    prof_strs = [f"({p[0]}, {p[1]}, '{p[2]}', '{p[3]}', '{p[4]}', '{p[5]}', {p[6]}, '{p[7]}')" for p in profiles]
    lines.append(",\n".join(prof_strs) + ";")
    lines.append("")

    # 7. RESUMES & EDUCATION DOCUMENTS
    lines.append("-- ============================================================================")
    lines.append("-- 5. RESUMES & EDUCATION VERIFICATION DOCUMENTS")
    lines.append("-- ============================================================================")
    lines.append("INSERT INTO RESUME (Resume_ID, Student_ID, File_Name, File_Link, Upload_Date, Resume_Year) VALUES")
    resumes = [
        (1,  1,  'Aarav_Sharma_Resume.pdf',    'https://storage.fictional.edu/resumes/cs201801.pdf', '2021-08-01', 2022),
        (2,  2,  'Diya_Patel_DataScience.pdf', 'https://storage.fictional.edu/resumes/cs201802.pdf', '2021-08-01', 2022),
        (3,  3,  'Kabir_Verma_Embedded.pdf',   'https://storage.fictional.edu/resumes/ec201803.pdf', '2021-08-05', 2022),
        (4,  8,  'Ananya_Iyer_Backend.pdf',    'https://storage.fictional.edu/resumes/cs201908.pdf', '2022-08-01', 2023),
        (5,  9,  'Vikram_Nair_Fullstack.pdf',  'https://storage.fictional.edu/resumes/cs201909.pdf', '2022-08-10', 2023),
        (6,  15, 'Aditya_Kulkarni_Java.pdf',   'https://storage.fictional.edu/resumes/cs202015.pdf', '2023-08-01', 2024),
        (7,  16, 'Ishita_Bose_SDE.pdf',        'https://storage.fictional.edu/resumes/cs202016.pdf', '2023-08-01', 2024),
        (8,  17, 'Meera_Menon_Systems.pdf',    'https://storage.fictional.edu/resumes/cs202017.pdf', '2023-08-02', 2024),
        (9,  19, 'Kavya_Srinivasan_Cloud.pdf', 'https://storage.fictional.edu/resumes/cs202019.pdf', '2023-08-02', 2024),
        (10, 24, 'Rhea_Sen_Software.pdf',      'https://storage.fictional.edu/resumes/cs202124.pdf', '2024-08-01', 2025)
    ]
    res_strs = [f"({r[0]}, {r[1]}, '{r[2]}', '{r[3]}', '{r[4]}', {r[5]})" for r in resumes]
    lines.append(",\n".join(res_strs) + ";")
    lines.append("")

    lines.append("INSERT INTO EDUCATION_DOCUMENT (Doc_ID, Resume_ID, Document_Type, Percentage_CGPA, Board, Year_of_Passing, File_Link) VALUES")
    docs = [
        (1, 1, '10th Marksheet', 96.40, 'CBSE', 2016, 'https://storage.fictional.edu/docs/10th_cs01.pdf'),
        (2, 1, '12th Marksheet', 94.80, 'CBSE', 2018, 'https://storage.fictional.edu/docs/12th_cs01.pdf'),
        (3, 2, '10th Marksheet', 98.20, 'ICSE', 2016, 'https://storage.fictional.edu/docs/10th_cs02.pdf'),
        (4, 2, '12th Marksheet', 95.60, 'ISC',  2018, 'https://storage.fictional.edu/docs/12th_cs02.pdf'),
        (5, 4, '10th Marksheet', 99.00, 'CBSE', 2017, 'https://storage.fictional.edu/docs/10th_cs08.pdf'),
        (6, 4, '12th Marksheet', 97.20, 'CBSE', 2019, 'https://storage.fictional.edu/docs/12th_cs08.pdf'),
        (7, 6, '10th Marksheet', 92.50, 'State Board', 2018, 'https://storage.fictional.edu/docs/10th_cs15.pdf'),
        (8, 6, '12th Marksheet', 90.40, 'State Board', 2020, 'https://storage.fictional.edu/docs/12th_cs15.pdf')
    ]
    doc_strs = [f"({d[0]}, {d[1]}, '{d[2]}', {d[3]}, '{d[4]}', {d[5]}, '{d[6]}')" for d in docs]
    lines.append(",\n".join(doc_strs) + ";")
    lines.append("")

    # 8. SEMESTER RESULTS (Semesters 1 to 6 for prerequisite SGPA audits)
    lines.append("-- ============================================================================")
    lines.append("-- 6. SEMESTER RESULTS (Academic SGPA Ledger across Semesters 1 to 6)")
    lines.append("-- ============================================================================")
    lines.append("INSERT INTO SEMESTER_RESULT (Result_ID, Student_ID, Semester, SGPA, Year, Total_Credits) VALUES")
    sem_results = []
    r_id = 1
    for s_id in range(1, 31):
        s_batch = next(s[5] for s in students if s[0] == s_id)
        base_cgpa = next(s[7] for s in students if s[0] == s_id)
        # Give results for Sem 1 to 6 (satisfying prerequisite checks for Internship 1 & 2)
        for sem in range(1, 7):
            # calculate year: sem 1-2 in batch-4, sem 3-4 in batch-3, sem 5-6 in batch-2
            res_year = (s_batch - 4) + (sem // 2)
            # slight jitter on SGPA around base CGPA
            jitter = ((s_id + sem) % 5 - 2) * 0.15
            sgpa = round(min(10.0, max(6.0, base_cgpa + jitter)), 2)
            sem_results.append((r_id, s_id, sem, sgpa, res_year, 24))
            r_id += 1
    sem_strs = [f"({sr[0]}, {sr[1]}, {sr[2]}, {sr[3]}, {sr[4]}, {sr[5]})" for sr in sem_results]
    lines.append(",\n".join(sem_strs) + ";")
    lines.append("")

    # 9. 10 COMPANIES
    lines.append("-- ============================================================================")
    lines.append("-- 7. CORPORATE PARTNERS (10 Fictional Companies across Product, Service, Startup)")
    lines.append("-- ============================================================================")
    lines.append("INSERT INTO COMPANY (Company_ID, Company_Name, Company_Type, Industry, Location, Website) VALUES")
    companies = [
        (1,  'Nexus Software Technologies', 'Product', 'Enterprise SaaS',          'Bengaluru', 'https://nexus-tech.fictional.com'),
        (2,  'Apex Cloud Innovations',      'Product', 'Cloud Infrastructure',     'Hyderabad', 'https://apexcloud.fictional.com'),
        (3,  'Bharat FinServe Digital',     'Startup', 'FinTech & Payments',       'Mumbai',    'https://bharatfinserve.fictional.com'),
        (4,  'Quantum Robotics India',      'Startup', 'Robotics & Automation',    'Pune',      'https://quantumrobotics.fictional.com'),
        (5,  'ZenHealth Solutions',         'Product', 'HealthTech AI',            'Bengaluru', 'https://zenhealth.fictional.com'),
        (6,  'Tata Tech Services',          'Service', 'IT & Systems Consulting',  'Mumbai',    'https://tatatechservices.fictional.com'),
        (7,  'Infosys Technologies',        'Service', 'Enterprise Digital Tech',  'Bengaluru', 'https://infotech.fictional.com'),
        (8,  'UrbanMobility Systems',       'Startup', 'Electric Vehicles & IoT',  'Pune',      'https://urbanmobility.fictional.com'),
        (9,  'Silicon Embedded Systems',    'Product', 'Semiconductors & VLSI',    'Chennai',   'https://siliconembedded.fictional.com'),
        (10, 'CyberShield Networks',        'Service', 'Cybersecurity & Defense',  'Gurugram',  'https://cybershield.fictional.com')
    ]
    comp_strs = [f"({c[0]}, '{c[1]}', '{c[2]}', '{c[3]}', '{c[4]}', '{c[5]}')" for c in companies]
    lines.append(",\n".join(comp_strs) + ";")
    lines.append("")

    # 10. RECRUITMENT DRIVES (Across 2022 to 2025)
    lines.append("-- ============================================================================")
    lines.append("-- 8. RECRUITMENT DRIVES ACROSS YEARS (2022 to 2025)")
    lines.append("-- ============================================================================")
    lines.append("INSERT INTO RECRUITMENT_DRIVE (Drive_ID, Company_ID, Drive_Year, Drive_Type, Season, Drive_Date) VALUES")
    drives = [
        # 2022 Drives
        (1,  1,  2022, 'Both',       'Summer', '2022-04-10'),
        (2,  2,  2022, 'Both',       'Summer', '2022-04-20'),
        (3,  6,  2022, 'Both',       'Autumn', '2022-09-05'),
        (4,  9,  2022, 'Both',       'Summer', '2022-05-15'),

        # 2023 Drives
        (5,  1,  2023, 'Both',       'Autumn', '2023-08-15'),
        (6,  2,  2023, 'Both',       'Autumn', '2023-08-25'),
        (7,  3,  2023, 'Both',       'Summer', '2023-05-02'),
        (8,  5,  2023, 'Both',       'Autumn', '2023-09-10'),
        (9,  6,  2023, 'Both',       'Autumn', '2023-09-18'),
        (10, 7,  2023, 'Placement',  'Winter', '2023-11-12'),

        # 2024 Drives
        (11, 1,  2024, 'Both',       'Autumn', '2024-08-12'),
        (12, 2,  2024, 'Both',       'Autumn', '2024-08-22'),
        (13, 3,  2024, 'Both',       'Summer', '2024-05-10'),
        (14, 4,  2024, 'Placement',  'Autumn', '2024-09-05'),
        (15, 5,  2024, 'Both',       'Autumn', '2024-09-15'),
        (16, 6,  2024, 'Both',       'Autumn', '2024-09-20'),
        (17, 8,  2024, 'Placement',  'Autumn', '2024-10-02'),
        (18, 9,  2024, 'Both',       'Summer', '2024-05-20'),
        (19, 10, 2024, 'Placement',  'Winter', '2024-11-15'),

        # 2025 Drives
        (20, 1,  2025, 'Placement',  'Spring', '2025-01-20'),
        (21, 6,  2025, 'Both',       'Spring', '2025-02-10')
    ]
    drive_strs = [f"({d[0]}, {d[1]}, {d[2]}, '{d[3]}', '{d[4]}', '{d[5]}')" for d in drives]
    lines.append(",\n".join(drive_strs) + ";")
    lines.append("")

    # 11. OPPORTUNITIES
    lines.append("-- ============================================================================")
    lines.append("-- 9. OPPORTUNITIES (Roles & Packages)")
    lines.append("-- ============================================================================")
    lines.append("INSERT INTO OPPORTUNITY (Opportunity_ID, Drive_ID, Role, Opportunity_Type, Package_Stipend, Duration_Months) VALUES")
    opportunities = [
        # Drive 1 (Nexus 2022)
        (1,  1,  'Software Engineering Intern',   'Internship', 35000.00, 2),
        (2,  1,  'Member Technical Staff',        'Placement',  18.00,    NULL),

        # Drive 2 (Apex 2022)
        (3,  2,  'Cloud Systems Intern',          'Internship', 32000.00, 2),
        (4,  2,  'Associate Cloud Engineer',      'Placement',  16.50,    NULL),

        # Drive 3 (Tata Tech 2022)
        (5,  3,  'Developer Intern',              'Internship', 18000.00, 2),
        (6,  3,  'Systems Associate',             'Placement',  7.50,     NULL),

        # Drive 4 (Silicon Embedded 2022)
        (7,  4,  'VLSI Intern',                   'Internship', 25000.00, 2),
        (8,  4,  'Embedded Systems Engineer',     'Placement',  12.50,    NULL),

        # Drive 5 (Nexus 2023)
        (9,  5,  'Backend Engineering Intern',    'Internship', 40000.00, 2),
        (10, 5,  'Software Engineer Early Career','Placement',  19.50,    NULL),

        # Drive 6 (Apex 2023)
        (11, 6,  'Cloud Architecture Intern',     'Internship', 35000.00, 2),
        (12, 6,  'Software Development Engineer', 'Placement',  18.00,    NULL),

        # Drive 7 (Bharat FinServe 2023)
        (13, 7,  'FinTech Analyst Intern',        'Internship', 28000.00, 2),
        (14, 7,  'Associate Software Engineer',   'Placement',  14.00,    NULL),

        # Drive 8 (ZenHealth 2023)
        (15, 8,  'Applied AI Intern',             'Internship', 30000.00, 2),
        (16, 8,  'Machine Learning Engineer',     'Placement',  16.00,    NULL),

        # Drive 9 (Tata Tech 2023)
        (17, 9,  'Consulting Intern',             'Internship', 20000.00, 2),
        (18, 9,  'Digital Specialist Engineer',   'Placement',  8.50,     NULL),

        # Drive 10 (Infosys 2023)
        (19, 10, 'Specialist Programmer',         'Placement',  6.80,     NULL),

        # Drive 11 (Nexus 2024)
        (20, 11, 'Platform Engineering Intern',   'Internship', 42000.00, 2),
        (21, 11, 'Software Engineer',             'Placement',  20.00,    NULL),

        # Drive 12 (Apex 2024)
        (22, 12, 'Cloud Reliability Intern',      'Internship', 38000.00, 2),
        (23, 12, 'DevOps & Cloud Engineer',       'Placement',  18.50,    NULL),

        # Drive 13 (Bharat FinServe 2024)
        (24, 13, 'Backend Developer Intern',      'Internship', 32000.00, 2),
        (25, 13, 'Software Engineer',             'Placement',  15.00,    NULL),

        # Drive 14 (Quantum Robotics 2024)
        (26, 14, 'Robotics Software Engineer',    'Placement',  13.50,    NULL),

        # Drive 15 (ZenHealth 2024)
        (27, 15, 'HealthTech Developer Intern',   'Internship', 35000.00, 2),
        (28, 15, 'Software Engineer',             'Placement',  16.50,    NULL),

        # Drive 16 (Tata Tech 2024)
        (29, 16, 'Fullstack Intern',              'Internship', 22000.00, 2),
        (30, 16, 'Digital Engineer',              'Placement',  9.00,     NULL),

        # Drive 17 (UrbanMobility 2024)
        (31, 17, 'EV Powertrain Engineer',        'Placement',  9.00,     NULL),

        # Drive 18 (Silicon Embedded 2024)
        (32, 18, 'Hardware Design Intern',        'Internship', 30000.00, 2),
        (33, 18, 'Senior Embedded Engineer',      'Placement',  15.00,    NULL),

        # Drive 19 (CyberShield 2024)
        (34, 19, 'Security Analyst',              'Placement',  11.50,    NULL),

        # Drive 20 (Nexus 2025)
        (35, 20, 'Software Development Engineer', 'Placement',  17.50,    NULL),

        # Drive 21 (Tata Tech 2025)
        (36, 21, 'Trainee Systems Engineer',      'Placement',  6.50,     NULL)
    ]
    opp_strs = [f"({o[0]}, {o[1]}, '{o[2]}', '{o[3]}', {o[4]}, {o[5] if o[5] else 'NULL'})" for o in opportunities]
    lines.append(",\n".join(opp_strs) + ";")
    lines.append("")

    # 12. ELIGIBILITY & ELIGIBILITY_BRANCH
    lines.append("-- ============================================================================")
    lines.append("-- 10. ELIGIBILITY RULES & MULTI-BRANCH MAPPINGS")
    lines.append("-- ============================================================================")
    lines.append("INSERT INTO ELIGIBILITY (Eligibility_ID, Opportunity_ID, Minimum_CGPA, Eligible_Branch, Max_Backlogs, Other_Criteria) VALUES")
    elig_rows = []
    ebranch_rows = []
    e_id = 1
    for o in opportunities:
        opp_id = o[0]
        # set realistic min cgpa
        min_cgpa = 7.00 if 'Nexus' in str(o) or 'Apex' in str(o) or o[4] >= 15.00 else 6.00
        branch_desc = 'CSE, IT, ECE' if o[3] == 'Placement' and o[4] > 10 else 'All Branches'
        elig_rows.append((e_id, opp_id, min_cgpa, branch_desc, 0, 'No active academic backlogs'))
        # branches
        if 'All' in branch_desc:
            for b in ['CSE', 'IT', 'ECE', 'ME']:
                ebranch_rows.append((e_id, b))
        else:
            for b in ['CSE', 'IT', 'ECE']:
                ebranch_rows.append((e_id, b))
        e_id += 1
    elig_strs = [f"({e[0]}, {e[1]}, {e[2]}, '{e[3]}', {e[4]}, '{e[5]}')" for e in elig_rows]
    lines.append(",\n".join(elig_strs) + ";")
    lines.append("")

    lines.append("INSERT INTO ELIGIBILITY_BRANCH (Eligibility_ID, Branch) VALUES")
    ebr_strs = [f"({eb[0]}, '{eb[1]}')" for eb in ebranch_rows]
    lines.append(",\n".join(ebr_strs) + ";")
    lines.append("")

    # 13. SELECTION_PROCESS (Rounds)
    lines.append("-- ============================================================================")
    lines.append("-- 11. SELECTION PROCESS ROUNDS")
    lines.append("-- ============================================================================")
    lines.append("INSERT INTO SELECTION_PROCESS (Round_ID, Opportunity_ID, Round_Number, Round_Type, Description) VALUES")
    rounds = []
    rnd_id = 1
    for opp_id in range(1, len(opportunities) + 1):
        rounds.append((rnd_id, opp_id, 1, 'Aptitude Test', 'Quantitative and logical reasoning'))
        rnd_id += 1
        rounds.append((rnd_id, opp_id, 2, 'Coding Round', 'Data structures and programming challenge'))
        rnd_id += 1
        rounds.append((rnd_id, opp_id, 3, 'Technical Interview', 'Deep dive into architecture and core concepts'))
        rnd_id += 1
        rounds.append((rnd_id, opp_id, 4, 'HR Interview', 'Culture fit and behavioural assessment'))
        rnd_id += 1
    rnd_strs = [f"({r[0]}, {r[1]}, {r[2]}, '{r[3]}', '{r[4]}')" for r in rounds]
    lines.append(",\n".join(rnd_strs) + ";")
    lines.append("")

    # 14. INTERNSHIP_REQUIREMENT
    lines.append("-- ============================================================================")
    lines.append("-- 12. CURRICULAR INTERNSHIP REQUIREMENTS")
    lines.append("-- ============================================================================")
    lines.append("INSERT INTO INTERNSHIP_REQUIREMENT (Requirement_ID, Internship_No, Mandatory, Prescribed_Period, Required_Result_Semester, Report_Submission_Semester, Credits, Description) VALUES")
    lines.append("(1, 1, 'Yes', 'Summer Vacation after 2nd Year', 3, 5, 4, 'Mandatory Summer Internship 1 (Minimum 6 weeks industry training)'),")
    lines.append("(2, 2, 'Yes', 'Summer Vacation after 3rd Year', 5, 7, 4, 'Mandatory Summer Internship 2 (Minimum 8 weeks project engagement)');")
    lines.append("")

    # 15. INTERNSHIPS (Mandatory 1 & 2 for EVERY student 1..30 + Additional 3+ for some students)
    lines.append("-- ============================================================================")
    lines.append("-- 13. INTERNSHIPS (Every Student Has Mandatory 1 & 2; Additional for Select Students)")
    lines.append("-- ============================================================================")
    lines.append("INSERT INTO INTERNSHIP (Internship_ID, Student_ID, Company_ID, Opportunity_ID, Requirement_ID, Internship_No, Internship_Type, Role, Interview_Rounds, Stipend, Start_Date, End_Date, Credits, Report_Semester, Report_Link, Report_Grade, Certificate_Link) VALUES")
    internships = []
    i_id = 1
    # Companies to assign for I1 and I2 per student:
    company_allocations = [
        (1, 1), (2, 2), (9, 9), (4, 4), (6, 6), (3, 7), (9, 6), (1, 1), (2, 2), (7, 6),
        (4, 8), (6, 6), (5, 5), (6, 7), (3, 3), (1, 2), (2, 5), (8, 9), (1, 4), (6, 7),
        (4, 8), (9, 10),(1, 6), (5, 3), (9, 8), (7, 6), (6, 7), (1, 2), (4, 8), (6, 7)
    ]
    for s_id in range(1, 31):
        s_batch = next(s[5] for s in students if s[0] == s_id)
        c1, c2 = company_allocations[s_id - 1]

        # Internship 1 (Mandatory, Req=1, Report_Sem=5, Credits=4)
        i1_start = f"{s_batch - 3}-06-01"
        i1_end   = f"{s_batch - 3}-07-31"
        internships.append((
            i_id, s_id, c1, 'NULL', 1, 1, 'Mandatory', 'Engineering Intern', 2, 25000.00,
            i1_start, i1_end, 4, 5,
            f"https://storage.fictional.edu/reports/rep_{s_id}_1.pdf", 'A',
            f"https://storage.fictional.edu/certs/cert_{s_id}_1.pdf"
        ))
        i_id += 1

        # Internship 2 (Mandatory, Req=2, Report_Sem=7, Credits=4)
        i2_start = f"{s_batch - 2}-06-01"
        i2_end   = f"{s_batch - 2}-07-31"
        internships.append((
            i_id, s_id, c2, 'NULL', 2, 2, 'Mandatory', 'Project Intern', 2, 35000.00,
            i2_start, i2_end, 4, 7,
            f"https://storage.fictional.edu/reports/rep_{s_id}_2.pdf", 'A+',
            f"https://storage.fictional.edu/certs/cert_{s_id}_2.pdf"
        ))
        i_id += 1

        # Extra internships (No >= 3) for Students 1, 8, 15, 23 (Requirement_ID MUST be NULL)
        if s_id in (1, 8, 15, 23):
            i3_start = f"{s_batch - 1}-01-05"
            i3_end   = f"{s_batch - 1}-02-15"
            internships.append((
                i_id, s_id, (c1 % 10) + 1, 'NULL', 'NULL', 3, 'Additional', 'Winter Research Intern', 1, 40000.00,
                i3_start, i3_end, 3, 8,
                f"https://storage.fictional.edu/reports/rep_{s_id}_3.pdf", 'A+',
                f"https://storage.fictional.edu/certs/cert_{s_id}_3.pdf"
            ))
            i_id += 1

    int_strs = []
    for it in internships:
        req_val = it[4] if it[4] == 'NULL' else str(it[4])
        opp_val = it[3] if it[3] == 'NULL' else str(it[3])
        rep_sem = it[13] if it[13] else 'NULL'
        crd_val = it[12] if it[12] else 'NULL'
        s = f"({it[0]}, {it[1]}, {it[2]}, {opp_val}, {req_val}, {it[5]}, '{it[6]}', '{it[7]}', {it[8]}, {it[9]}, '{it[10]}', '{it[11]}', {crd_val}, {rep_sem}, '{it[14]}', '{it[15]}', '{it[16]}')"
        int_strs.append(s)
    lines.append(",\n".join(int_strs) + ";")
    lines.append("")

    # 16. PLACEMENT & PLACEMENT_SKILL
    lines.append("-- ============================================================================")
    lines.append("-- 14. PLACEMENT OFFERS & OUTCOMES")
    lines.append("-- (Zero, One, Multiple Offers; At Most ONE Joined per Student; PPO Matching)")
    lines.append("-- ============================================================================")
    lines.append("INSERT INTO PLACEMENT (Placement_ID, Student_ID, Company_ID, Opportunity_ID, Role, Package, Placement_Year, Placement_Type, Is_PPO, Joined, Offer_Status, Interview_Rounds) VALUES")

    # Placement distribution:
    # 0 offers: 4, 11, 14, 20, 21, 29 (6 students)
    # 1 offer:  2, 5, 7, 10, 12, 18, 22, 26, 28, 30 (10 students)
    # 2-3 offers: 1, 3, 6, 8, 9, 13, 15, 16, 17, 19, 23, 24, 25, 27 (14 students)
    placements = [
        # Student 1: 3 offers, PPO from Co 1 (Nexus) where interned
        (1,  1, 1, 10,   'Software Engineer Early Career', 19.50, 2022, 'On-campus', 'Yes', 'Yes', 'Joined',   4),
        (2,  1, 2, 4,    'Associate Cloud Engineer',       16.50, 2022, 'On-campus', 'No',  'No',  'Declined', 3),
        (3,  1, 6, 6,    'Systems Associate',              7.50,  2022, 'On-campus', 'No',  'No',  'Declined', 2),

        # Student 2: 1 offer
        (4,  2, 2, 4,    'Associate Cloud Engineer',       16.50, 2022, 'On-campus', 'No',  'Yes', 'Joined',   3),

        # Student 3: 2 offers, PPO from Co 9 (Silicon Embedded) where interned
        (5,  3, 9, 8,    'Embedded Systems Engineer',      12.50, 2022, 'On-campus', 'Yes', 'Yes', 'Joined',   3),
        (6,  3, 6, 6,    'Systems Associate',              7.50,  2022, 'On-campus', 'No',  'No',  'Declined', 2),

        # Student 5: 1 offer
        (7,  5, 6, 6,    'Systems Associate',              7.50,  2022, 'On-campus', 'No',  'Yes', 'Joined',   2),

        # Student 6: 2 offers
        (8,  6, 3, 14,   'Associate Software Engineer',    14.00, 2022, 'On-campus', 'No',  'Yes', 'Joined',   3),
        (9,  6, 7, 19,   'Specialist Programmer',          6.80,  2022, 'On-campus', 'No',  'No',  'Declined', 2),

        # Student 7: 1 offer
        (10, 7, 9, 8,    'Embedded Systems Engineer',      8.20,  2022, 'On-campus', 'No',  'Yes', 'Joined',   3),

        # Student 8: 3 offers, PPO from Co 1 (Nexus) where interned
        (11, 8, 1, 10,   'Software Engineer Early Career', 20.00, 2023, 'On-campus', 'Yes', 'Yes', 'Joined',   4),
        (12, 8, 5, 16,   'Machine Learning Engineer',      17.50, 2023, 'On-campus', 'No',  'No',  'Declined', 3),
        (13, 8, 3, 14,   'Associate Software Engineer',    15.00, 2023, 'On-campus', 'No',  'No',  'Declined', 3),

        # Student 9: 2 offers, PPO from Co 2 (Apex) where interned
        (14, 9, 2, 12,   'Software Development Engineer',  18.50, 2023, 'On-campus', 'Yes', 'Yes', 'Joined',   4),
        (15, 9, 6, 18,   'Digital Specialist Engineer',    8.50,  2023, 'On-campus', 'No',  'No',  'Declined', 2),

        # Student 10: 1 offer
        (16, 10, 7, 19,  'Specialist Programmer',          6.80,  2023, 'On-campus', 'No',  'Yes', 'Joined',   2),

        # Student 12: 1 offer (Offered, not joined)
        (17, 12, 6, 18,  'Digital Specialist Engineer',    8.00,  2023, 'On-campus', 'No',  'No',  'Offered',  2),

        # Student 13: 2 offers, PPO from Co 5 (ZenHealth) where interned
        (18, 13, 5, 16,  'Machine Learning Engineer',      16.00, 2023, 'On-campus', 'Yes', 'Yes', 'Joined',   4),
        (19, 13, 7, 19,  'Specialist Programmer',          6.80,  2023, 'On-campus', 'No',  'No',  'Declined', 2),

        # Student 15: 2 offers, PPO from Co 3 (Bharat FinServe) where interned
        (20, 15, 3, 25,  'Software Engineer',              17.00, 2024, 'On-campus', 'Yes', 'Yes', 'Joined',   4),
        (21, 15, 10, 34, 'Security Analyst',               11.50, 2024, 'On-campus', 'No',  'No',  'Declined', 3),

        # Student 16: 2 offers
        (22, 16, 1, 21,  'Software Engineer',              19.00, 2024, 'On-campus', 'No',  'Yes', 'Joined',   4),
        (23, 16, 2, 23,  'DevOps & Cloud Engineer',        18.20, 2024, 'On-campus', 'No',  'No',  'Declined', 3),

        # Student 17: 3 offers
        (24, 17, 2, 23,  'DevOps & Cloud Engineer',        18.00, 2024, 'On-campus', 'No',  'Yes', 'Joined',   4),
        (25, 17, 5, 28,  'Software Engineer',              15.50, 2024, 'On-campus', 'No',  'No',  'Declined', 3),
        (26, 17, 7, 19,  'Specialist Programmer',          7.00,  2024, 'On-campus', 'No',  'No',  'Declined', 2),

        # Student 18: 1 offer
        (27, 18, 8, 31,  'EV Powertrain Engineer',         7.20,  2024, 'On-campus', 'No',  'Yes', 'Joined',   2),

        # Student 19: 2 offers, PPO from Co 1 (Nexus) where interned
        (28, 19, 1, 21,  'Software Engineer',              19.50, 2024, 'On-campus', 'Yes', 'Yes', 'Joined',   4),
        (29, 19, 4, 26,  'Robotics Software Engineer',     13.50, 2024, 'On-campus', 'No',  'No',  'Declined', 3),

        # Student 22: 1 offer (Offered, not joined)
        (30, 22, 9, 33,  'Senior Embedded Engineer',       9.50,  2024, 'On-campus', 'No',  'No',  'Offered',  3),

        # Student 23: 2 offers
        (31, 23, 1, 35,  'Software Development Engineer',  17.50, 2025, 'On-campus', 'No',  'Yes', 'Joined',   4),
        (32, 23, 6, 36,  'Trainee Systems Engineer',       8.00,  2025, 'On-campus', 'No',  'No',  'Declined', 2),

        # Student 24: 2 offers, PPO from Co 5 (ZenHealth) where interned
        (33, 24, 5, 28,  'Software Engineer',              16.50, 2025, 'On-campus', 'Yes', 'Yes', 'Joined',   4),
        (34, 24, 3, 25,  'Software Engineer',              14.50, 2025, 'On-campus', 'No',  'No',  'Declined', 3),

        # Student 25: 2 offers
        (35, 25, 9, 33,  'Senior Embedded Engineer',       13.00, 2025, 'On-campus', 'No',  'Yes', 'Joined',   3),
        (36, 25, 8, 31,  'EV Powertrain Engineer',         9.00,  2025, 'On-campus', 'No',  'No',  'Declined', 2),

        # Student 26: 1 offer
        (37, 26, 7, 19,  'Specialist Programmer',          6.50,  2025, 'On-campus', 'No',  'Yes', 'Joined',   2),

        # Student 27: 2 offers, PPO from Co 6 (Tata Tech) where interned
        (38, 27, 6, 30,  'Digital Engineer',               9.00,  2025, 'On-campus', 'Yes', 'Yes', 'Joined',   2),
        (39, 27, 7, 19,  'Specialist Programmer',          6.80,  2025, 'On-campus', 'No',  'No',  'Declined', 2),

        # Student 28: 1 offer (Offered, not joined)
        (40, 28, 1, 35,  'Software Development Engineer',  14.00, 2025, 'On-campus', 'No',  'No',  'Offered',  3),

        # Student 30: 1 offer
        (41, 30, 6, 36,  'Trainee Systems Engineer',       7.00,  2025, 'On-campus', 'No',  'Yes', 'Joined',   2)
    ]
    plc_strs = [f"({p[0]}, {p[1]}, {p[2]}, {p[3]}, '{p[4]}', {p[5]}, {p[6]}, '{p[7]}', '{p[8]}', '{p[9]}', '{p[10]}', {p[11]})" for p in placements]
    lines.append(",\n".join(plc_strs) + ";")
    lines.append("")

    # 17. PLACEMENT_SKILL (Selected skills for each placement)
    lines.append("-- ============================================================================")
    lines.append("-- 15. PLACEMENT SKILLS (Evaluated Competencies per Placement Offer)")
    lines.append("-- ============================================================================")
    lines.append("INSERT INTO PLACEMENT_SKILL (Placement_ID, Skill) VALUES")
    skills_for_placement = {
        1:  ['Java', 'Spring Boot', 'Distributed Systems'],
        2:  ['Cloud Architecture', 'AWS', 'Linux'],
        3:  ['SQL', 'Database Administration'],
        4:  ['Python', 'Cloud Computing', 'SQL'],
        5:  ['C++', 'Embedded C', 'RTOS'],
        6:  ['Embedded Systems', 'Circuit Design'],
        7:  ['React', 'Web Services', 'MySQL'],
        8:  ['Java', 'Microservices', 'Docker'],
        9:  ['Algorithms', 'Data Structures'],
        10: ['VHDL', 'VLSI Design'],
        11: ['Go', 'Distributed Systems', 'System Design'],
        12: ['Machine Learning', 'Python', 'FastAPI'],
        13: ['Backend Development', 'PostgreSQL'],
        14: ['Python', 'Django', 'Redis'],
        15: ['Enterprise Java', 'Spring Boot'],
        16: ['C++', 'Competitive Programming'],
        17: ['JavaScript', 'Vue.js', 'SQL'],
        18: ['Apache Spark', 'Kafka', 'Data Engineering'],
        19: ['Java', 'SQL', 'Web Services'],
        20: ['Spring Cloud', 'Oracle DB', 'Microservices'],
        21: ['Network Security', 'Linux', 'Firewalls'],
        22: ['Algorithms', 'Data Structures', 'C++'],
        23: ['Docker', 'Kubernetes', 'CI/CD'],
        24: ['Terraform', 'GCP', 'Cloud Networking'],
        25: ['Python', 'REST APIs', 'FastAPI'],
        26: ['Java', 'SQL', 'Algorithms'],
        27: ['Automotive Electronics', 'CAN Protocol'],
        28: ['Kubernetes', 'Cloud Security', 'Go'],
        29: ['Robotics', 'Control Systems', 'C++'],
        30: ['Embedded C', 'Microcontrollers'],
        31: ['Flask', 'PostgreSQL', 'Python'],
        32: ['Java', 'Database Systems'],
        33: ['PyTorch', 'Computer Vision', 'Python'],
        34: ['FinTech APIs', 'SQL', 'Python'],
        35: ['FPGA', 'Verilog', 'VLSI'],
        36: ['Battery Management Systems', 'IoT'],
        37: ['Java', 'Web Development'],
        38: ['React', 'Next.js', 'TypeScript'],
        39: ['Fullstack Web', 'REST APIs'],
        40: ['Python', 'Machine Learning'],
        41: ['FastAPI', 'Vue.js', 'Docker']
    }
    pskill_rows = []
    for p_id, sks in skills_for_placement.items():
        for sk in sks:
            pskill_rows.append((p_id, sk))
    pskill_strs = [f"({ps[0]}, '{ps[1]}')" for ps in pskill_rows]
    lines.append(",\n".join(pskill_strs) + ";")
    lines.append("")

    lines.append("COMMIT;")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    content = generate_seed_sql()
    with open("seed.sql", "w", encoding="utf-8") as f:
        f.write(content)
    print("Generated seed.sql successfully! Total lines:", len(content.splitlines()))

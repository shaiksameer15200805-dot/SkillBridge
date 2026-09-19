-- Seed data for MySQL (SkillBridge)
-- Password for all demo accounts is: password123

USE aicp;

-- College
INSERT INTO colleges (id, name, location) VALUES
(1, 'National Institute of Technology', 'Warangal')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Users
-- Password hash for 'password123' (scrypt)
INSERT INTO users (id, name, email, password_hash, role) VALUES
(1, 'Priya Sharma', 'student@demo.com', 'scrypt:32768:8:1$qDk2n8WGU8Kk3XOZ$06b9f8699dc9cc96aea1e8be4ed712a08b8ac9726f04baaea229b53d7214b98e2254206c118fbf5d28942506793923e020483223a7b3fb1db7f03970485a6cd3', 'student'),
(2, 'Amit Rao', 'company@demo.com', 'scrypt:32768:8:1$s9Y86L1Fd6YU8OJQ$92620bb22a44386fde7b001ce301defac9dfc4d5ad7604a8ffe8bc38be7b258ad5adbe879d4c97a8a247d6d5bc5ec429c45a404a26dfd8f8dfa66e4fe1e77d64', 'company'),
(3, 'Dr. Meera Iyer', 'college@demo.com', 'scrypt:32768:8:1$bNWl16xPHHY2RsVN$4942649492b43f95bafa85279ee2b4e6e4b2d04dd764f7bb37e2828edec0dd87ed0442b254a1251aa6113bdfd3011b53b07c5f040cbc226f192b174ad06c2473', 'college'),
(4, 'Rahul Verma', 'rahul@demo.com', 'scrypt:32768:8:1$txoct8OWNPijeDY9$787e50749f826fdb1d4143a52d46addb9ce016e92271eb1a33e7eff0a5ed57f89200ae886205b53f3d0de2b03d7193621074347bd3c6e113a1d83036b06ca323', 'student')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Students
INSERT INTO students (id, user_id, college_id, department, year_of_study, career_goal) VALUES
(1, 1, 1, 'Computer Science', 3, 'Software engineering internship then full-time SDE'),
(2, 4, 1, 'Computer Science', 4, 'Data analyst role')
ON DUPLICATE KEY UPDATE department=VALUES(department);

-- Companies
INSERT INTO companies (id, user_id, company_name, industry) VALUES
(1, 2, 'Infotech Labs', 'IT Services')
ON DUPLICATE KEY UPDATE company_name=VALUES(company_name);

-- College Admins
INSERT INTO college_admins (id, user_id, college_id) VALUES
(1, 3, 1)
ON DUPLICATE KEY UPDATE user_id=VALUES(user_id);

-- Student Skills
INSERT INTO student_skills (id, student_id, skill_name) VALUES
(1, 1, 'Python'),
(2, 1, 'React'),
(3, 1, 'SQL'),
(4, 1, 'Git'),
(5, 1, 'JavaScript'),
(6, 2, 'Python'),
(7, 2, 'SQL'),
(8, 2, 'Data Analysis')
ON DUPLICATE KEY UPDATE skill_name=VALUES(skill_name);

-- Certifications
INSERT INTO certifications (id, student_id, title, issuer, year) VALUES
(1, 1, 'Python for Everybody', 'Coursera', 2025),
(2, 1, 'Responsive Web Design', 'freeCodeCamp', 2024),
(3, 2, 'Google Data Analytics', 'Coursera', 2025)
ON DUPLICATE KEY UPDATE title=VALUES(title);

-- Opportunities
INSERT INTO opportunities (id, company_id, title, type, description, location) VALUES
(1, 1, 'Frontend Intern', 'internship', 'Build UI for internal dashboards using React. Work with designers and backend APIs.', 'Hyderabad (hybrid)'),
(2, 1, 'Junior Software Engineer', 'job', 'Full-stack role on the collaboration platform. Flask APIs and React screens.', 'Bengaluru'),
(3, 1, 'Campus Skill-Gap Study', 'project', 'Analyze curriculum vs industry skill demands across universities in the state.', 'Remote')
ON DUPLICATE KEY UPDATE title=VALUES(title);

-- Opportunity Skills
INSERT INTO opportunity_skills (id, opportunity_id, skill_name) VALUES
(1, 1, 'React'),
(2, 1, 'JavaScript'),
(3, 1, 'CSS'),
(4, 2, 'Python'),
(5, 2, 'Flask'),
(6, 2, 'SQL'),
(7, 3, 'Data Analysis'),
(8, 3, 'Python'),
(9, 3, 'Communication')
ON DUPLICATE KEY UPDATE skill_name=VALUES(skill_name);

-- Applications
INSERT INTO applications (id, student_id, opportunity_id, status) VALUES
(1, 1, 1, 'applied')
ON DUPLICATE KEY UPDATE status=VALUES(status);

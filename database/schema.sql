-- MySQL schema for Academia–Industry Collaboration Portal
CREATE DATABASE IF NOT EXISTS aicp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE aicp;

CREATE TABLE IF NOT EXISTS colleges (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(200) NOT NULL,
  location VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(120) NOT NULL,
  email VARCHAR(160) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('student','company','college') NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS students (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL UNIQUE,
  college_id INT,
  department VARCHAR(120),
  year_of_study INT,
  career_goal VARCHAR(255),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (college_id) REFERENCES colleges(id)
);

CREATE TABLE IF NOT EXISTS companies (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL UNIQUE,
  company_name VARCHAR(200) NOT NULL,
  industry VARCHAR(120),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS college_admins (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL UNIQUE,
  college_id INT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (college_id) REFERENCES colleges(id)
);

CREATE TABLE IF NOT EXISTS student_skills (
  id INT PRIMARY KEY AUTO_INCREMENT,
  student_id INT NOT NULL,
  skill_name VARCHAR(80) NOT NULL,
  FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS certifications (
  id INT PRIMARY KEY AUTO_INCREMENT,
  student_id INT NOT NULL,
  title VARCHAR(200) NOT NULL,
  issuer VARCHAR(160),
  year INT,
  FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS opportunities (
  id INT PRIMARY KEY AUTO_INCREMENT,
  company_id INT NOT NULL,
  title VARCHAR(200) NOT NULL,
  type ENUM('internship','job','project') NOT NULL,
  description TEXT,
  location VARCHAR(160),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS opportunity_skills (
  id INT PRIMARY KEY AUTO_INCREMENT,
  opportunity_id INT NOT NULL,
  skill_name VARCHAR(80) NOT NULL,
  FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
);

CREATE TABLE IF NOT EXISTS applications (
  id INT PRIMARY KEY AUTO_INCREMENT,
  student_id INT NOT NULL,
  opportunity_id INT NOT NULL,
  status ENUM('applied','shortlisted','rejected','accepted') NOT NULL DEFAULT 'applied',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uniq_app (student_id, opportunity_id),
  FOREIGN KEY (student_id) REFERENCES students(id),
  FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
);

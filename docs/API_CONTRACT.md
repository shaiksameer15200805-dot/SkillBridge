# Lokesh Backend — Actual API Contract Reference

This document defines the actual API endpoints implemented in Lokesh's Flask backend (`temp-lokesh/backend/app.py`).

---

## 1. Authentication Endpoints

### 1.1 POST /api/auth/register
- **Purpose**: Register a new student user.
- **Authentication**: None (Public).
- **Request Body**:
  ```json
  {
    "name": "Priya Sharma",
    "email": "priya@example.com",
    "password": "password123",
    "role": "student",
    "department": "Computer Science",
    "year_of_study": 3,
    "career_goal": "Software Engineer"
  }
  ```
- **Validation**:
  - `name`, `email`, and `password` are required.
  - `role` must be `"student"` (self-registration is student-only).
  - Duplicate email returns HTTP 409 Conflict.
- **Response** (HTTP 201 Created):
  ```json
  {
    "token": "<jwt_hs256_token>",
    "user": {
      "id": 5,
      "name": "Priya Sharma",
      "email": "priya@example.com",
      "role": "student"
    }
  }
  ```

### 1.2 POST /api/auth/login
- **Purpose**: Authenticate user and obtain JWT token.
- **Authentication**: None (Public).
- **Request Body**:
  ```json
  {
    "email": "student@demo.com",
    "password": "password123"
  }
  ```
- **Validation**:
  - Checks `User` table for `email` (case-insensitive).
  - Verifies `password_hash` using `check_password_hash()`.
  - Invalid credentials return HTTP 401 Unauthorized: `{"error": "Invalid email or password"}`.
- **Response** (HTTP 200 OK):
  ```json
  {
    "token": "<jwt_hs256_token>",
    "user": {
      "id": 1,
      "name": "Priya Sharma",
      "email": "student@demo.com",
      "role": "student"
    }
  }
  ```

### 1.3 GET /api/auth/me
- **Purpose**: Retrieve currently authenticated user profile.
- **Authentication**: Required (`Authorization: Bearer <token>`).
- **Response** (HTTP 200 OK):
  ```json
  {
    "id": 1,
    "name": "Priya Sharma",
    "email": "student@demo.com",
    "role": "student"
  }
  ```

---

## 2. Student Endpoints

### 2.1 GET /api/student/profile
- **Purpose**: Retrieve student profile, academic information, skills, and certifications.
- **Authentication**: Required (`role: student`).
- **Response** (HTTP 200 OK):
  ```json
  {
    "id": 1,
    "name": "Priya Sharma",
    "email": "student@demo.com",
    "department": "Computer Science",
    "year_of_study": 3,
    "career_goal": "Software engineering internship then full-time SDE",
    "college": "National Institute of Technology",
    "skills": ["Python", "React", "SQL", "Git", "JavaScript"],
    "certifications": [
      {
        "id": 1,
        "title": "Python for Everybody",
        "issuer": "Coursera",
        "year": 2025
      }
    ]
  }
  ```

### 2.2 PUT /api/student/profile
- **Purpose**: Update student profile, skills list, and certifications list.
- **Authentication**: Required (`role: student`).
- **Request Body**:
  ```json
  {
    "name": "Priya Sharma",
    "department": "Computer Science & Engineering",
    "year_of_study": 3,
    "career_goal": "Full-stack developer",
    "skills": ["Python", "React", "SQL", "Git", "JavaScript", "Docker"],
    "certifications": [
      {
        "title": "Python for Everybody",
        "issuer": "Coursera",
        "year": 2025
      }
    ]
  }
  ```
- **Response** (HTTP 200 OK):
  Returns updated student profile object matching GET `/api/student/profile`.

### 2.3 GET /api/student/recommendations
- **Purpose**: Fetch opportunities ranked by explainable skill-match percentage against student's current skills.
- **Authentication**: Required (`role: student`).
- **Response** (HTTP 200 OK):
  ```json
  [
    {
      "id": 1,
      "title": "Frontend Intern",
      "type": "internship",
      "description": "Build UI for internal dashboards using React.",
      "location": "Hyderabad (hybrid)",
      "company_name": "Infotech Labs",
      "industry": "IT Services",
      "required_skills": ["React", "JavaScript", "CSS"],
      "created_at": "2026-09-18T15:14:00",
      "match": {
        "match_percent": 67,
        "matched_skills": ["React", "JavaScript"],
        "missing_skills": ["CSS"],
        "extra_skills": ["Python", "SQL", "Git"],
        "required_count": 3,
        "matched_count": 2,
        "explanation": "2 of 3 required skills match (React, JavaScript). Gap: CSS."
      },
      "recommended_learning": [
        {
          "skill": "CSS",
          "title": "Learn CSS",
          "provider": "Search",
          "url": "https://www.google.com/search?q=learn+CSS+course"
        }
      ]
    }
  ]
  ```

### 2.4 GET /api/student/skill-gap
- **Purpose**: Skill-gap analysis. If `?opportunity_id=<id>` is provided, analyzes gap against that opportunity; otherwise, analyzes gap across all posted opportunities.
- **Authentication**: Required (`role: student`).
- **Query Parameters**: `opportunity_id` (optional, integer).
- **Response** (HTTP 200 OK):
  ```json
  {
    "match": {
      "match_percent": 75,
      "matched_skills": ["Python", "React", "SQL", "Git"],
      "missing_skills": ["AWS", "Docker"],
      "extra_skills": ["JavaScript"],
      "required_count": 6,
      "matched_count": 4,
      "explanation": "4 of 6 required skills match..."
    },
    "recommended_learning": [
      {
        "skill": "AWS",
        "title": "AWS Cloud Practitioner Essentials",
        "provider": "AWS Skill Builder",
        "url": "https://skillbuilder.aws/"
      }
    ]
  }
  ```

### 2.5 GET /api/student/applications
- **Purpose**: List all submitted applications for the authenticated student.
- **Authentication**: Required (`role: student`).
- **Response** (HTTP 200 OK):
  ```json
  [
    {
      "id": 1,
      "title": "Frontend Intern",
      "type": "internship",
      "company_name": "Infotech Labs",
      "application_id": 1,
      "status": "applied",
      "applied_at": "2026-09-18T15:14:00",
      "match": { ... },
      "required_skills": ["React", "JavaScript", "CSS"]
    }
  ]
  ```

### 2.6 POST /api/student/applications
- **Purpose**: Apply to an opportunity. Prevents duplicate applications.
- **Authentication**: Required (`role: student`).
- **Request Body**:
  ```json
  {
    "opportunity_id": 1
  }
  ```
- **Validation**:
  - Checks if opportunity exists (HTTP 404 if not found).
  - Checks if already applied (HTTP 409 Conflict: `{"error": "Already applied", "application_id": 1, "status": "applied"}`).
- **Response** (HTTP 201 Created):
  ```json
  {
    "id": 2,
    "status": "applied"
  }
  ```

### 2.7 GET /api/opportunities/<int:opp_id>
- **Purpose**: Retrieve single opportunity details. If student is authenticated, includes personalized match and application status.
- **Authentication**: Required (`Authorization: Bearer <token>`).
- **Response** (HTTP 200 OK):
  ```json
  {
    "id": 1,
    "title": "Frontend Intern",
    "type": "internship",
    "description": "Build UI for internal dashboards using React.",
    "location": "Hyderabad (hybrid)",
    "company_name": "Infotech Labs",
    "industry": "IT Services",
    "required_skills": ["React", "JavaScript", "CSS"],
    "created_at": "2026-09-18T15:14:00",
    "match": { ... },
    "recommended_learning": [ ... ],
    "application_status": "applied"
  }
  ```

---

## 3. Company Endpoints

- `GET /api/company/dashboard`: Company statistics (`opportunity_count`, `application_count`, `status_counts`).
- `GET /api/company/opportunities`: List company's posted opportunities with applicant counts.
- `POST /api/company/opportunities`: Create new opportunity listing.
- `GET /api/company/opportunities/<int:opp_id>/applicants`: List applicants ranked by skill match score.
- `PATCH /api/company/applications/<int:app_id>`: Update applicant status (`applied`, `shortlisted`, `rejected`, `accepted`).

---

## 4. College Endpoints

- `GET /api/college/dashboard`: College dashboard summary.
- `GET /api/college/students`: Cohort student list with skills and matched opportunities.
- `GET /api/college/skill-gaps`: Aggregated skill gaps across students and opportunities.
- `GET /api/college/opportunities`: View all opportunities posted across companies.
- `GET /api/college/analytics`: Placement and application analytics.

---

## 5. System Endpoints

- `GET /api/health`: Health check (`{"ok": true}`).

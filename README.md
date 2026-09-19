# SkillBridge — Unified Academia–Industry Portal

SkillBridge is an end-to-end web portal bridging academia and industry. It enables students to discover internships and jobs based on transparent skill-match algorithms, companies to recruit candidates with verified capabilities, and colleges to monitor real-time placement analytics and curriculum skill gaps.

---

## Architecture & System Overview

- **Frontend**: React 19 + Vite with role-based routing (Student, Company, College), modular CSS design system, and unified API client.
- **Backend**: Flask + Flask-SQLAlchemy + Flask-CORS with itsdangerous token authentication, deterministic SQLite storage, and rule-based skill-matching engine.
- **Database**: SQLite (`backend/aicp.db`) for lightweight, reproducible development, with support for MySQL.

---

## Project Structure

```
SkillBridge/
├── backend/
│   ├── app.py              # Main Flask application, API routes, and DB models
│   ├── matching.py         # Skill-matching and learning-recommendation algorithms
│   ├── seed.py             # Database seed script with demo users and opportunities
│   ├── requirements.txt    # Python dependencies
│   ├── aicp.db             # Local SQLite database (ignored by Git)
│   ├── .env.example        # Backend environment template
│   └── .env                # Backend environment configuration (ignored by Git)
├── frontend/
│   ├── index.html          # HTML entry point
│   ├── package.json        # Frontend dependencies and scripts
│   ├── vite.config.js      # Vite dev server and /api proxy configuration
│   ├── .env.example        # Frontend environment template
│   ├── .env                # Frontend environment configuration (ignored by Git)
│   └── src/
│       ├── main.jsx        # React DOM bootstrap
│       ├── App.jsx         # App router & role guards (Student, Company, College)
│       ├── api.js          # Shared API client and session management
│       ├── styles.css      # Base styling and design tokens
│       └── pages/
│           ├── Login.jsx   # Unified authentication login
│           ├── Register.jsx# Multi-role registration
│           ├── student/    # Integrated Student Module
│           │   ├── StudentLayout.jsx       # Student shell navigation
│           │   ├── StudentDashboard.jsx    # Metrics, top skills, recommended opps
│           │   ├── StudentProfile.jsx      # Profile & certification management
│           │   ├── StudentSkills.jsx       # Student skill manager
│           │   ├── StudentOpportunities.jsx# Matched opportunities & filters
│           │   ├── OpportunityDetail.jsx   # Deep-dive with skill match breakdown
│           │   ├── StudentApplications.jsx # Multi-stage application tracker
│           │   ├── StudentSkillGap.jsx     # Gap analysis & recommended courses
│           │   ├── StudentCards.jsx        # Reusable UI card components
│           │   ├── studentApi.js           # Student API communication layer
│           │   ├── mockData.js             # Fallback demo data
│           │   └── student.css             # Student module styling
│           ├── company/    # Company Module (Dashboard, Post Opp, Applicants)
│           └── college/    # College Module (Analytics, Gap Summary, Cohort View)
├── database/               # Database migration and utility scripts
├── .gitignore              # Git ignore rules ensuring zero credential/DB leaks
└── README.md               # Complete setup and development guide
```

---

## Prerequisites

- **Python**: 3.10 or higher
- **Node.js**: 18.0 or higher
- **npm**: 9.0 or higher
- **Git**: 2.30 or higher

---

## Environment Configuration

### Backend (`backend/.env`)
Copy the template and set the environment variables:
```bash
cp backend/.env.example backend/.env
```
Default development configuration:
```ini
USE_SQLITE=1
SECRET_KEY=sih-hackathon-secret
PORT=5000
```

### Frontend (`frontend/.env`)
Copy the template and configure the backend URL:
```bash
cp frontend/.env.example frontend/.env
```
Default development configuration:
```ini
VITE_API_URL=http://127.0.0.1:5000
```

---

## Getting Started

### 1. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed the database with demo users, skills, and opportunities
python seed.py

# Start the backend server
python app.py
```
The backend starts at `http://127.0.0.1:5000`.

### 2. Frontend Setup

In a separate terminal window:
```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```
The frontend starts at `http://localhost:5173`.

### 3. Production Build

To test or verify the production bundle:
```bash
cd frontend
npm run build
```

---

## Development Demo Accounts

The database is pre-seeded with accounts for all three user roles:

| Role | Email | Password | Description |
| :--- | :--- | :--- | :--- |
| **Student** | `student@demo.com` | `student123` | Teja Varma — 3rd Year CSE, pre-populated skills & applications |
| **Student** | `aisha@demo.com` | `student123` | Aisha Khan — 4th Year CSE, ML focus |
| **Student** | `ravi@demo.com` | `student123` | Ravi Patel — 3rd Year IT, Frontend focus |
| **Company** | `company@demo.com` | `company123` | Priya Sharma — Acme Analytics, posted opportunities & applicants |
| **Company** | `nimbus@demo.com` | `company123` | Rahul Mehta — Nimbus Cloud |
| **College** | `college@demo.com` | `college123` | College Admin — NIT Demo placement & analytics dashboard |

> [!NOTE]
> All passwords above are strictly for development and testing environments. Never commit real production credentials.

---

## Key API Endpoints Reference

Base URL: `http://127.0.0.1:5000`

### Authentication
- `POST /api/auth/login` — Sign in and receive JWT token (`email`, `password`)
- `POST /api/auth/register` — Register a new student, company, or college account
- `GET /api/auth/me` — Retrieve the currently authenticated user's profile

### Student Module
- `GET /api/students/profile` & `PUT /api/students/profile` — View/update student profile
- `GET /api/students/skills` & `POST /api/students/skills` & `PUT /api/students/skills` — Manage skills
- `GET /api/student/certifications` & `POST` & `DELETE` — Manage certifications
- `GET /api/students/recommendations` — Fetch tailored opportunities with match scores
- `GET /api/opportunities/<id>` — Fetch full opportunity details
- `POST /api/applications` — Submit application (prevents duplicates with HTTP 400)
- `GET /api/students/applications` — Track all submitted student applications
- `GET /api/students/skill-gap` — Comprehensive skill gap analysis and recommended courses

### Company Module
- `GET /api/company/dashboard` — Overview of posted opportunities and applicants
- `POST /api/company/opportunities` — Create new internship or job listing
- `GET /api/company/opportunities/<id>/applicants` — Ranked applicants by skill match percentage
- `PUT /api/company/applications/<id>/status` — Update status (`applied`, `under_review`, `shortlisted`, `selected`, `rejected`)

### College Module
- `GET /api/college/dashboard` — Cohort placement statistics, top skill gaps, student list

---

## Troubleshooting & Common Gotchas

### Port Collisions (e.g. "Invalid email or password" error)
If port `5000` or `5173` is occupied by an older background process (such as a previous clone), requests might route to an incorrect process or stale database.
- **Identify listening processes on Windows**:
  ```powershell
  Get-NetTCPConnection -LocalPort 5000, 5173 -State Listen
  ```
- **Stop conflicting process**:
  ```powershell
  Stop-Process -Id <PID> -Force
  ```

### Database Location
The backend automatically resolves the absolute path to `backend/aicp.db` regardless of whether `python app.py` is run from the project root or the `backend` directory. If the database file is ever missing, simply re-run `python seed.py` from the `backend` folder.
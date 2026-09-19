# SkillBridge Integration Plan — Teja Student Frontend + Lokesh Backend & Database

This plan outlines the architecture, compatibility matrix, and step-by-step strategy for integrating **Lokesh's Flask backend and MySQL/SQLite database** with **Teja's Student Frontend** into the main **SkillBridge** repository.

---

## A. Current Frontend Structure (Teja's Frontend)

- **Framework**: React 19 + Vite 6
- **Routing**: React Router v7 (`main.jsx`, `App.jsx`)
- **State & Session**:
  - `localStorage.getItem("aicp_token")`
  - `localStorage.getItem("aicp_user")`
- **Core Files**:
  - `frontend/src/main.jsx`: Application bootstrap
  - `frontend/src/App.jsx`: Main routing & role guards (`Guard`, `HomeRedirect`)
  - `frontend/src/api.js`: Centralized fetch wrapper, token injection (`Authorization: Bearer <token>`), base URL configuration via `import.meta.env.VITE_API_URL || "http://127.0.0.1:5000"`.
  - `frontend/src/pages/student/`:
    - `StudentLayout.jsx`: Navigation bar, avatar, user greeting, logout button, view switcher.
    - `StudentDashboard.jsx`: Metric cards, welcome hero, top skills, recommended opportunities, application status counts, top gaps.
    - `StudentProfile.jsx`: Academic form (name, email, university, degree, branch, year, cgpa, bio, career goals) and certification list with add/delete handlers.
    - `StudentSkills.jsx`: Interactive skill chips with add/remove actions and smart suggestions.
    - `StudentOpportunities.jsx`: Split view list of matching roles with match %, chips, and inline detail pane.
    - `OpportunityDetail.jsx`: Standalone deep dive page for a specific role with apply action.
    - `StudentApplications.jsx`: Multi-stage recruitment tracker with search, status filters, and pipeline steps.
    - `StudentSkillGap.jsx`: Visual current vs missing skills and course cards.
    - `StudentCards.jsx`: Reusable UI primitives (`MetricCard`, `StudentCard`, `AlertBanner`, `LoadingCard`).
    - `studentApi.js`: Student API client mapping backend responses to UI models.
    - `mockData.js`: Fallback dataset for offline / initial state.

---

## B. Lokesh Backend Structure (`temp-lokesh/backend`)

- **Framework**: Python Flask 3.0.3, Flask-SQLAlchemy 3.1.1, Flask-CORS 4.0.1, PyJWT 2.9.0, PyMySQL 1.1.1, Werkzeug 3.0.4.
- **Entry Point**: `app.py` -> `create_app()`
- **Port**: `5000`
- **Database Engine**:
  - Primary: MySQL (via `MYSQL_URL` or `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`, `MYSQL_PORT`).
  - Fallback: SQLite (`data/aicp.db`) automatically used if MySQL environment variables are not set.
- **Authentication**: JWT HS256 (`PyJWT`), token expiration 24 hours, `Authorization: Bearer <token>`.
- **Matching Engine** (`matching.py`):
  - `skill_match(student_skills, required_skills)`: Pure set overlap algorithm calculating match %, matched skills, missing skills, extra skills, and explanation.
  - `learning_for(missing_skills)`: Course suggestions mapping missing skills to `LEARNING_CATALOG` items.

---

## C. Database Structure (`temp-lokesh/database/schema.sql`)

Relational schema supporting Academia–Industry interaction:
1. `colleges`: id, name, location
2. `users`: id, name, email (UNIQUE), password_hash, role (ENUM: student, company, college), created_at
3. `students`: id, user_id (FK users, UNIQUE), college_id (FK colleges), department, year_of_study, career_goal
4. `companies`: id, user_id (FK users, UNIQUE), company_name, industry
5. `college_admins`: id, user_id (FK users, UNIQUE), college_id (FK colleges)
6. `student_skills`: id, student_id (FK students), skill_name
7. `certifications`: id, student_id (FK students), title, issuer, year
8. `opportunities`: id, company_id (FK companies), title, type (ENUM: internship, job, project), description, location, created_at
9. `opportunity_skills`: id, opportunity_id (FK opportunities), skill_name
10. `applications`: id, student_id (FK students), opportunity_id (FK opportunities), status (ENUM: applied, shortlisted, rejected, accepted), created_at, UNIQUE(student_id, opportunity_id)

---

## D. Frontend / Backend Compatibility

| Frontend Expectation (`studentApi.js`) | Lokesh Backend Implementation (`temp-lokesh/backend/app.py`) | Compatibility Strategy |
| :--- | :--- | :--- |
| `POST /api/auth/login` | `POST /api/auth/login` | **100% Compatible**. Returns `{ token, user }`. |
| `POST /api/auth/register` | `POST /api/auth/register` | **100% Compatible**. Registers student user. |
| `GET /api/auth/me` | `GET /api/auth/me` | **100% Compatible**. Returns `{ id, name, email, role }`. |
| `GET /api/students/profile` (plural) | `GET /api/student/profile` (singular) | **Alias supported**: Backend will bind both `/api/student/profile` and `/api/students/profile`. |
| `PUT /api/students/profile` (plural) | `PUT /api/student/profile` (singular) | **Alias supported**: Backend binds both plural and singular. |
| `GET/POST/PUT /api/students/skills` | Nested in `Student.skills` | **Endpoint supported**: Provide `/api/students/skills` and `/api/student/skills` routes in `backend/app.py` querying `StudentSkill`. |
| `POST /api/student/certifications` & `DELETE /api/student/certifications/:id` | Nested in `PUT /api/student/profile` | **Endpoints supported**: Provide discrete certification POST and DELETE routes in `backend/app.py` mapping to `Certification`. |
| `GET /api/students/recommendations` | `GET /api/student/recommendations` | **Alias supported**: Backend binds both plural and singular. |
| `GET /api/students/skill-gap` | `GET /api/student/skill-gap` | **Alias supported**: Backend binds both plural and singular. |
| `POST /api/applications` / `/api/student/applications` | `POST /api/student/applications` | **Alias supported**: Backend binds both `/api/applications` and `/api/student/applications`. |
| `GET /api/students/applications` | `GET /api/student/applications` | **Alias supported**: Backend binds both plural and singular. |
| `GET /api/opportunities/:id` | `GET /api/opportunities/:id` | **100% Compatible**. Returns details with match & application status. |

---

## E. Authentication Compatibility

- **Mechanism**: Both Teja's frontend and Lokesh's backend use Bearer JWT authentication:
  - Header: `Authorization: Bearer <jwt_token>`
  - Frontend stores token in `localStorage` under key `aicp_token`.
  - Backend decodes JWT using secret key (`JWT_SECRET`).
- **User Object**: Both systems use `{ id, name, email, role }`.
- **Default Seed Accounts & Passwords**:
  - `student@demo.com` / `password123` (or `student123` alias support)
  - `company@demo.com` / `password123` (or `company123`)
  - `college@demo.com` / `password123` (or `college123`)

---

## F. API Endpoint Mapping

All student endpoints will support both the singular convention used by Lokesh and the plural convention called by Teja's frontend:
1. `GET, PUT /api/student/profile` ↔ `/api/students/profile`
2. `GET, POST, PUT /api/student/skills` ↔ `/api/students/skills`
3. `GET, POST /api/student/certifications` & `DELETE /api/student/certifications/<id>`
4. `GET /api/student/recommendations` ↔ `/api/students/recommendations`
5. `GET /api/student/skill-gap` ↔ `/api/students/skill-gap`
6. `POST /api/student/applications` ↔ `/api/applications`
7. `GET /api/student/applications` ↔ `/api/students/applications`
8. `GET /api/opportunities/<int:opp_id>`

---

## G. Environment Variables

### Backend (`backend/.env` & `backend/.env.example`)
```ini
# MySQL Configuration (leave empty to use SQLite automatically)
MYSQL_HOST=
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DB=aicp

# Authentication & Security
JWT_SECRET=sih-aicp-dev-secret
PORT=5000
```

### Frontend (`frontend/.env` & `frontend/.env.example`)
```ini
VITE_API_URL=http://127.0.0.1:5000
```

---

## H. Dependencies

### Backend (`backend/requirements.txt`)
- `flask==3.0.3`
- `flask-cors==4.0.1`
- `flask-sqlalchemy==3.1.1`
- `PyJWT==2.9.0`
- `PyMySQL==1.1.1`
- `Werkzeug==3.0.4`
- `cryptography==43.0.3`

### Frontend (`frontend/package.json`)
- Existing dependencies are retained without modifications:
  - `react: ^19.0.0`
  - `react-dom: ^19.0.0`
  - `react-router-dom: ^7.2.0`
  - `@vitejs/plugin-react: ^4.3.4`
  - `vite: ^6.2.0`

---

## I. File Conflicts & Resolution

1. **`schema.sql` location**:
   - `temp-lokesh/database/schema.sql` will be integrated into `database/schema.sql`.
2. **`matching.py`**:
   - Lokesh's `matching.py` provides pure set overlap without ML dependencies and clean learning catalog entries. It will be integrated into `backend/matching.py`.
3. **`temp-lokesh/frontend/`**:
   - Ignored completely as per instructions. Teja's `frontend/` is the master frontend.

---

## J. Files that Must NOT Be Overwritten

- `frontend/src/pages/student/*` (Teja's student UI components)
- `frontend/src/App.jsx` (master route configuration)
- `frontend/src/api.js` (master API abstraction)
- `frontend/package.json`

---

## K. Exact Integration Sequence

1. **Phase 1: Inspection & Plan Creation** (Completed):
   - Created `docs/API_CONTRACT.md` and `INTEGRATION_PLAN.md`.
2. **Phase 2: Database Artifacts**:
   - Copy `temp-lokesh/database/schema.sql` to `database/schema.sql`.
   - Provide `database/seed.sql` for MySQL seeding and update Python seeding in `backend/app.py`.
3. **Phase 3: Backend Integration**:
   - Integrate Lokesh's relational models (`colleges`, `users`, `students`, `companies`, `college_admins`, `student_skills`, `certifications`, `opportunities`, `opportunity_skills`, `applications`) into `backend/app.py`.
   - Implement route aliases for plural/singular endpoints to satisfy both contracts.
   - Include standalone skill and certification endpoints.
   - Ensure `database_uri()` supports MySQL when configured, and falls back to deterministic SQLite.
4. **Phase 4: Backend Independent Testing**:
   - Start backend server on port 5000.
   - Test login (`POST /api/auth/login`), profile, skills, recommendations, applications, and duplicate rejection.
5. **Phase 5: Frontend Connection**:
   - Run `npm run dev` on port 5173.
   - Test end-to-end student flow: Login -> Dashboard -> Profile -> Skills -> Opportunities -> Apply -> Applications -> Logout.
6. **Phase 6: Verification & Final Report**:
   - Verify production build (`npm run build`).
   - Check data persistence across logout/login.
   - Verify Git status and prepare final report.

---

## L. Potential Problems & Safeguards

1. **Port Collisions**: Ensure no orphaned Flask or Vite processes are running on port 5000 or 5173 before launching.
2. **Field Mismatch**: Student profile uses `university` on frontend, while DB uses `colleges.name`. Resolved via bidirectional alias in serialization.
3. **Duplicate Applications**: SQLite / MySQL unique constraint on `(student_id, opportunity_id)` ensures HTTP 400/409 duplicate rejection.
4. **Offline Resilience**: Teja's `mockData.js` is retained as a fallback layer in `studentApi.js` so network glitches never break the UI.

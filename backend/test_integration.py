import json
import os
import sys
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:5000"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def request(path, method="GET", data=None, headers=None):
    url = f"{BASE_URL}{path}"
    headers = headers or {}
    encoded_data = None
    if data is not None:
        encoded_data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            body = response.read().decode("utf-8")
            resp_headers = dict(response.headers)
            return response.status, (json.loads(body) if body else {}), resp_headers
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return e.code, parsed, dict(e.headers)

# 1. Startup & Health
def test_health():
    code, data, _ = request("/api/health")
    assert code == 200, f"Health check failed: {code}"
    assert data.get("ok") is True
    log("GET /api/health passed", "PASS")

# 2. Database URI Logic & Fallback
def test_database_uri_logic():
    import app as backend_app
    orig_env = dict(os.environ)
    try:
        # SQLite force
        os.environ["USE_SQLITE"] = "1"
        uri = backend_app.database_uri()
        assert uri.startswith("sqlite:///"), f"Expected sqlite URI, got {uri}"

        # MySQL URL
        os.environ["USE_SQLITE"] = "0"
        os.environ["MYSQL_URL"] = "mysql+pymysql://usr:pwd@dbhost:3306/aicp"
        uri = backend_app.database_uri()
        assert uri == "mysql+pymysql://usr:pwd@dbhost:3306/aicp"

        # MySQL env vars
        del os.environ["MYSQL_URL"]
        os.environ["MYSQL_HOST"] = "127.0.0.1"
        os.environ["MYSQL_USER"] = "root"
        os.environ["MYSQL_PASSWORD"] = "secret"
        os.environ["MYSQL_DB"] = "aicp"
        os.environ["MYSQL_PORT"] = "3306"
        uri = backend_app.database_uri()
        assert uri == "mysql+pymysql://root:secret@127.0.0.1:3306/aicp"

        # Default SQLite fallback
        del os.environ["MYSQL_HOST"]
        uri = backend_app.database_uri()
        assert uri.startswith("sqlite:///"), f"Expected sqlite URI, got {uri}"
    finally:
        os.environ.clear()
        os.environ.update(orig_env)
    log("Database URI resolution (MySQL + SQLite fallback) passed", "PASS")

# 3. Authentication & Demo Accounts
def test_auth_and_demo_accounts():
    # Student
    code, data, _ = request("/api/auth/login", method="POST", data={"email": "student@demo.com", "password": "password123"})
    assert code == 200, f"Student login failed: {code}"
    assert "token" in data and data["user"]["role"] == "student"
    student_token = data["token"]

    # Student fallback password
    c2, _, _ = request("/api/auth/login", method="POST", data={"email": "student@demo.com", "password": "student123"})
    assert c2 == 200, f"Student fallback login failed: {c2}"

    # Company
    c_comp, comp_data, _ = request("/api/auth/login", method="POST", data={"email": "company@demo.com", "password": "password123"})
    assert c_comp == 200 and comp_data["user"]["role"] == "company"
    company_token = comp_data["token"]

    # College
    c_coll, coll_data, _ = request("/api/auth/login", method="POST", data={"email": "college@demo.com", "password": "password123"})
    assert c_coll == 200 and coll_data["user"]["role"] == "college"
    college_token = coll_data["token"]

    # Invalid credentials
    c_inv, _, _ = request("/api/auth/login", method="POST", data={"email": "student@demo.com", "password": "wrongpassword"})
    assert c_inv == 401

    log("Demo accounts (student, company, college) & 401 rejection passed", "PASS")
    return student_token, company_token, college_token

# 4. Student APIs & Persistence
def test_student_apis(student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    
    # Singular & plural GET
    c1, d1, _ = request("/api/student/profile", headers=headers)
    c2, d2, _ = request("/api/students/profile", headers=headers)
    assert c1 == 200 and c2 == 200
    assert d1 == d2
    assert d1["email"] == "student@demo.com"
    log("GET /api/student/profile & /api/students/profile passed", "PASS")

    # Update profile
    c_up, d_up, _ = request("/api/students/profile", method="PUT", data={"career_goal": "Lead Architect"}, headers=headers)
    assert c_up == 200
    assert d_up["career_goal"] == "Lead Architect"
    log("PUT /api/students/profile passed", "PASS")

    # Skills GET
    c_sk, d_sk, _ = request("/api/students/skills", headers=headers)
    assert c_sk == 200 and "skills" in d_sk
    log("GET /api/students/skills passed", "PASS")

    # Skills Add
    c_add, d_add, _ = request("/api/students/skills", method="POST", data={"skill": "TypeScript"}, headers=headers)
    assert c_add == 200
    assert "TypeScript" in d_add["skills"]
    log("POST /api/students/skills passed", "PASS")

    # Recommendations
    c_r1, _, _ = request("/api/student/recommendations", headers=headers)
    c_r2, _, _ = request("/api/students/recommendations", headers=headers)
    c_r3, _, _ = request("/api/recommendations", headers=headers)
    assert c_r1 == 200 and c_r2 == 200 and c_r3 == 200
    log("Recommendations aliases passed", "PASS")

    # Skill Gap
    c_g1, gap, _ = request("/api/student/skill-gap", headers=headers)
    c_g2, _, _ = request("/api/students/skill-gap", headers=headers)
    c_g3, _, _ = request("/api/skill-gap", headers=headers)
    assert c_g1 == 200 and c_g2 == 200 and c_g3 == 200
    assert "top_skill_gaps" in gap
    log("Skill gap aliases passed", "PASS")

# 5. Opportunity APIs & Malformed Requests
def test_opportunities(student_token, company_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    comp_headers = {"Authorization": f"Bearer {company_token}"}

    # List & Get
    c1, opps, _ = request("/api/opportunities", headers=headers)
    assert c1 == 200 and len(opps) > 0
    opp_id = opps[0]["id"]
    c2, opp, _ = request(f"/api/opportunities/{opp_id}", headers=headers)
    assert c2 == 200 and opp["id"] == opp_id
    log("List & detail opportunities passed", "PASS")

    # Create Opportunity via Company
    c_create, new_opp, _ = request("/api/company/opportunities", method="POST", data={
        "title": "Backend Engineering Intern",
        "type": "internship",
        "description": "Python, Flask, and API development.",
        "location": "Hyderabad",
        "required_skills": ["Python", "Flask", "SQL"]
    }, headers=comp_headers)
    assert c_create == 201
    assert new_opp["title"] == "Backend Engineering Intern"
    log("Create opportunity (company) passed", "PASS")

    # Malformed Create Opportunity (missing title)
    c_bad, err_bad, _ = request("/api/company/opportunities", method="POST", data={
        "type": "internship",
        "required_skills": ["Python"]
    }, headers=comp_headers)
    assert c_bad == 400
    assert "error" in err_bad
    log("Malformed opportunity creation returns 400 JSON passed", "PASS")

    # Nonexistent Opportunity ID
    c_none, err_none, _ = request("/api/opportunities/99999", headers=headers)
    assert c_none == 404
    assert "error" in err_none
    log("Nonexistent opportunity returns 404 JSON passed", "PASS")

# 6. Application Logic & Rejection
def test_applications(student_token, company_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    comp_headers = {"Authorization": f"Bearer {company_token}"}

    c_apps, apps_list, _ = request("/api/students/applications", headers=headers)
    assert c_apps == 200

    # Test applying to opp #1 or duplicate check
    c_app, res_app, _ = request("/api/applications", method="POST", data={"opportunity_id": 1}, headers=headers)
    if c_app == 201:
        log("POST /api/applications passed", "PASS")
        # Duplicate check
        c_dup, res_dup, _ = request("/api/applications", method="POST", data={"opportunity_id": 1}, headers=headers)
        assert c_dup == 400
        assert "Already applied" in res_dup.get("error", "")
        log("Duplicate application rejected with 400 passed", "PASS")
    else:
        assert c_app == 400
        assert "Already applied" in res_app.get("error", "")
        log("Duplicate application rejected with 400 passed", "PASS")

    # Application Status Update (Company)
    c_up, d_up, _ = request("/api/company/applications/1", method="PATCH", data={"status": "shortlisted"}, headers=comp_headers)
    if c_up == 200:
        assert d_up["status"] == "shortlisted"
        log("PATCH /api/company/applications/<id> passed", "PASS")

    # Invalid status update
    c_inv, d_inv, _ = request("/api/company/applications/1", method="PATCH", data={"status": "invalid_status"}, headers=comp_headers)
    assert c_inv == 400
    assert "error" in d_inv
    log("Invalid status update returns 400 JSON passed", "PASS")

# 7. Matching Engine Edge Cases (8 cases)
def test_matching_edge_cases():
    from matching import skill_match

    # 1. Student with several skills
    m1 = skill_match(["Python", "React", "SQL"], ["React", "Python"])
    assert m1["match_percent"] == 100
    assert set(m1["matched_skills"]) == {"React", "Python"}
    assert m1["missing_skills"] == []

    # 2. Student with no skills
    m2 = skill_match([], ["React", "CSS"])
    assert m2["match_percent"] == 0
    assert m2["missing_skills"] == ["React", "CSS"]

    # 3. Opportunity with several required skills
    m3 = skill_match(["React"], ["React", "TypeScript", "Node.js"])
    assert m3["match_percent"] == 33
    assert m3["matched_skills"] == ["React"]
    assert m3["missing_skills"] == ["TypeScript", "Node.js"]

    # 4. Opportunity with no required skills
    m4 = skill_match(["React", "Python"], [])
    assert m4["match_percent"] == 0
    assert "no required skills" in m4["explanation"]

    # 5. Duplicate skills
    m5 = skill_match(["React", "React", "Python", "PYTHON"], ["React", "React"])
    assert m5["match_percent"] == 100
    assert m5["matched_skills"] == ["React"]

    # 6. Different capitalization
    m6 = skill_match(["javascript", "DOCKER"], ["JavaScript", "Docker"])
    assert m6["match_percent"] == 100
    assert len(m6["matched_skills"]) == 2

    # 7. No matching skills
    m7 = skill_match(["Java", "C++"], ["Python", "Flask"])
    assert m7["match_percent"] == 0
    assert m7["matched_skills"] == []
    assert len(m7["missing_skills"]) == 2

    # 8. Full match
    m8 = skill_match(["Python", "Flask", "SQL"], ["Python", "Flask", "SQL"])
    assert m8["match_percent"] == 100
    assert m8["missing_skills"] == []

    log("All 8 matching engine edge cases passed without crashing", "PASS")

# 8. CORS Preflight & Headers
def test_cors():
    req = urllib.request.Request(
        f"{BASE_URL}/api/auth/login",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization"
        },
        method="OPTIONS"
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        headers = dict(resp.headers)
        allow_origin = headers.get("Access-Control-Allow-Origin") or headers.get("access-control-allow-origin")
        assert allow_origin in ("*", "http://localhost:5173"), f"Unexpected CORS origin: {allow_origin}"
    log("CORS preflight & headers passed", "PASS")

# 9. Error Handling (400, 401, 403, 404)
def test_error_handling(student_token):
    # 404 for nonexistent API route
    c404, d404, _ = request("/api/nonexistent_route_test")
    assert c404 == 404
    assert "error" in d404
    log("404 returns JSON error passed", "PASS")

    # 401 for unauthenticated access
    c401, d401, _ = request("/api/student/profile")
    assert c401 == 401
    assert "error" in d401
    log("401 returns JSON error passed", "PASS")

    # 403 for unauthorized role access (student accessing company dashboard)
    c403, d403, _ = request("/api/company/dashboard", headers={"Authorization": f"Bearer {student_token}"})
    assert c403 == 401 or c403 == 403
    assert "error" in d403
    log("Role-protected rejection returns JSON error passed", "PASS")

if __name__ == "__main__":
    log("=== RUNNING BACKEND FINAL READINESS AUDIT ===")
    test_health()
    test_database_uri_logic()
    test_matching_edge_cases()
    student_token, company_token, college_token = test_auth_and_demo_accounts()
    test_student_apis(student_token)
    test_opportunities(student_token, company_token)
    test_applications(student_token, company_token)
    test_cors()
    test_error_handling(student_token)
    log("=== ALL READINESS AUDIT TESTS PASSED! ===", "SUCCESS")

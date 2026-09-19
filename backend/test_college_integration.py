import json
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
            return response.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return e.code, parsed

def test_college_flow():
    # 1. Login as college admin
    c, data = request("/api/auth/login", method="POST", data={"email": "college@demo.com", "password": "password123"})
    assert c == 200, f"Login failed: {c} {data}"
    assert data["user"]["role"] == "college"
    token = data["token"]
    headers = {"Authorization": f"Bearer {token}"}
    log("College login successful", "PASS")

    # 2. Test GET /api/college/students
    c_st, d_st = request("/api/college/students", headers=headers)
    assert c_st == 200, f"Failed /api/college/students: {c_st}"
    assert "students" in d_st, "Expected 'students' key in response"
    assert "total" in d_st, "Expected 'total' key in response"
    assert len(d_st["students"]) > 0, "No students returned"
    log(f"GET /api/college/students returned {d_st['total']} students", "PASS")

    # 3. Test GET /api/college/students with search filter
    c_search, d_search = request("/api/college/students?search=priya", headers=headers)
    assert c_search == 200
    assert any("priya" in s["name"].lower() for s in d_search["students"])
    log(f"GET /api/college/students?search=priya matched {len(d_search['students'])} student(s)", "PASS")

    # 4. Test GET /api/college/students with degree filter
    c_deg, d_deg = request("/api/college/students?degree=B.Tech", headers=headers)
    assert c_deg == 200
    assert len(d_deg["students"]) > 0
    log(f"GET /api/college/students?degree=B.Tech matched {len(d_deg['students'])} student(s)", "PASS")

    # 5. Test GET /api/college/skill-gaps
    c_gaps, d_gaps = request("/api/college/skill-gaps", headers=headers)
    assert c_gaps == 200
    assert "skill_gaps" in d_gaps
    assert isinstance(d_gaps["skill_gaps"], list)
    log(f"GET /api/college/skill-gaps returned {len(d_gaps['skill_gaps'])} skill gaps", "PASS")

    # 6. Test GET /api/college/analytics
    c_an, d_an = request("/api/college/analytics", headers=headers)
    assert c_an == 200
    assert "cards" in d_an
    assert "total_students" in d_an["cards"]
    assert "active_opportunities" in d_an["cards"]
    assert "internship_participation" in d_an["cards"]
    assert "students_placed" in d_an["cards"]
    assert "top_skills" in d_an
    assert "top_skill_gaps" in d_an
    assert "application_status" in d_an
    assert "internship_statistics" in d_an
    assert "placement_statistics" in d_an
    log("GET /api/college/analytics returned complete cards & metrics data", "PASS")

    # 7. Test unauthenticated access rejection
    c_unauth, d_unauth = request("/api/college/students")
    assert c_unauth == 401
    log("Unauthenticated college request rejected with 401", "PASS")

    # 8. Test role mismatch rejection (student token accessing college endpoints)
    c_st_login, d_st_login = request("/api/auth/login", method="POST", data={"email": "student@demo.com", "password": "password123"})
    st_token = d_st_login["token"]
    c_mismatch, _ = request("/api/college/analytics", headers={"Authorization": f"Bearer {st_token}"})
    assert c_mismatch == 401 or c_mismatch == 403
    log("Student token accessing college endpoint rejected with 401/403", "PASS")

    log("=== ALL KARTHIK COLLEGE INTEGRATION TESTS PASSED! ===", "SUCCESS")

if __name__ == "__main__":
    test_college_flow()

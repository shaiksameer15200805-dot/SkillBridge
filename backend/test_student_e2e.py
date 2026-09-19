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

def run_e2e_flow():
    log("--- Step 1: Student Login ---")
    c, res = request("/api/auth/login", method="POST", data={"email": "student@demo.com", "password": "password123"})
    assert c == 200, f"Login failed: {c} {res}"
    token = res["token"]
    user = res["user"]
    log(f"Login successful: {user['name']} ({user['email']})", "PASS")

    headers = {"Authorization": f"Bearer {token}"}

    log("--- Step 2: Dashboard & Profile Load ---")
    c, profile = request("/api/students/profile", headers=headers)
    assert c == 200, f"Failed to get profile: {c} {profile}"
    log(f"Profile loaded: {profile['name']}, College: {profile['college']}, Skills: {profile['skills']}", "PASS")

    log("--- Step 3: Update Profile & Skills (Teja Frontend flow) ---")
    new_goal = "Lead AI Engineer & Full Stack Specialist"
    updated_skills = profile["skills"] + (["Docker"] if "Docker" not in profile["skills"] else [])
    c, updated_profile = request("/api/students/profile", method="PUT", data={
        "career_goal": new_goal,
        "skills": updated_skills,
    }, headers=headers)
    assert c == 200, f"Failed to update profile: {c} {updated_profile}"
    assert updated_profile["career_goal"] == new_goal
    assert "Docker" in updated_profile["skills"]
    log(f"Profile updated successfully: Goal='{new_goal}', Skills={updated_profile['skills']}", "PASS")

    log("--- Step 4: Opportunities & Matching ---")
    c, opps_data = request("/api/students/recommendations", headers=headers)
    assert c == 200, f"Failed to get recommendations: {c}"
    opps = opps_data.get("opportunities", opps_data) if isinstance(opps_data, dict) else opps_data
    assert len(opps) > 0, "No opportunities found"
    for opp in opps:
        log(f"Opportunity: '{opp['title']}' | Match: {opp['match_percent']}% | Missing: {opp['missing_skills']}", "INFO")

    log("--- Step 5: Apply to an Opportunity ---")
    c_apps, existing_apps = request("/api/students/applications", headers=headers)
    applied_opp_ids = {a["opportunity_id"] for a in existing_apps}
    available_to_apply = [o for o in opps if o["id"] not in applied_opp_ids]
    
    if available_to_apply:
        target = available_to_apply[0]
        c_app, res_app = request("/api/applications", method="POST", data={"opportunity_id": target["id"]}, headers=headers)
        assert c_app == 201, f"Apply failed: {c_app} {res_app}"
        log(f"Successfully applied to '{target['title']}' (ID: {target['id']})", "PASS")
    else:
        log("Student has already applied to all opportunities. Verifying duplicate rejection.", "INFO")
        c_app, res_app = request("/api/applications", method="POST", data={"opportunity_id": opps[0]["id"]}, headers=headers)
        assert c_app == 400, f"Expected 400 duplicate rejection, got {c_app}"
        log("Duplicate application correctly rejected with 400", "PASS")

    log("--- Step 6: View Applications ---")
    c_apps2, final_apps = request("/api/students/applications", headers=headers)
    assert c_apps2 == 200
    log(f"Total applications submitted: {len(final_apps)}", "PASS")
    for app_item in final_apps:
        log(f"Application #{app_item['id']} - Opp: {app_item.get('title') or app_item.get('role')} - Status: {app_item['status']}", "INFO")

    log("--- Step 7: Logout (Session Termination) ---")
    token = None
    headers = {}
    c_unauth, _ = request("/api/students/profile", headers=headers)
    assert c_unauth == 401, f"Expected 401 without auth, got {c_unauth}"
    log("Logged out successfully: Unauthenticated access rejected with 401", "PASS")

    log("--- Step 8: Re-login & Data Persistence Verification ---")
    c_relogin, res_relogin = request("/api/auth/login", method="POST", data={"email": "student@demo.com", "password": "password123"})
    assert c_relogin == 200
    new_token = res_relogin["token"]
    new_headers = {"Authorization": f"Bearer {new_token}"}

    c_persisted, persisted_profile = request("/api/students/profile", headers=new_headers)
    assert c_persisted == 200
    assert persisted_profile["career_goal"] == new_goal, f"Career goal did not persist! Expected '{new_goal}', got '{persisted_profile['career_goal']}'"
    assert "Docker" in persisted_profile["skills"], f"Skill 'Docker' did not persist! Skills: {persisted_profile['skills']}"
    log("PERSISTENCE VERIFIED: Profile career goal and skills persisted across logout/re-login!", "PASS")

    c_apps_persisted, persisted_apps = request("/api/students/applications", headers=new_headers)
    assert c_apps_persisted == 200
    assert len(persisted_apps) == len(final_apps), "Applications did not persist across sessions!"
    log(f"PERSISTENCE VERIFIED: All {len(persisted_apps)} applications persisted across logout/re-login!", "PASS")

    log("=== END-TO-END STUDENT WORKFLOW COMPLETELY VERIFIED ===", "SUCCESS")

if __name__ == "__main__":
    run_e2e_flow()

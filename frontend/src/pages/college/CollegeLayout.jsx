import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { clearSession, getUser } from "../../api";
import "./college.css";

export default function CollegeLayout() {
  const user = getUser();
  const navigate = useNavigate();
  return (
    <div className="shell">
      <header className="topbar">
        <strong>SkillBridge · College Portal</strong>
        <nav style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <span style={{ color: "#c9d7ff", fontWeight: 500 }}>{user?.college_name || user?.name || "College Admin"}</span>
          <button
            className="btn small secondary"
            onClick={() => {
              clearSession();
              navigate("/login");
            }}
          >
            Logout
          </button>
        </nav>
      </header>
      <div style={{ padding: "16px 28px 0 28px" }}>
        <nav className="college-nav">
          <NavLink to="/college" end className={({ isActive }) => isActive ? "active" : ""}>Dashboard</NavLink>
          <NavLink to="/college/students" className={({ isActive }) => isActive ? "active" : ""}>Students</NavLink>
          <NavLink to="/college/skill-gaps" className={({ isActive }) => isActive ? "active" : ""}>Skill Gaps</NavLink>
          <NavLink to="/college/analytics" className={({ isActive }) => isActive ? "active" : ""}>Analytics</NavLink>
        </nav>
      </div>
      <main className="page" style={{ paddingTop: 0 }}>
        <Outlet />
      </main>
    </div>
  );
}

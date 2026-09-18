import { Link, Outlet, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { clearSession, getUser } from "../../api";
import StudentApplications from "./StudentApplications.jsx";
import StudentDashboard from "./StudentDashboard.jsx";
import StudentOpportunities from "./StudentOpportunities.jsx";
import StudentProfile from "./StudentProfile.jsx";
import StudentSkillGap from "./StudentSkillGap.jsx";
import StudentSkills from "./StudentSkills.jsx";
import "./student.css";

const VIEW_LINKS = [
  { to: "/student", label: "Dashboard", view: null },
  { to: "/student/profile", label: "Profile" },
  { to: "/student?view=skills", label: "Skills", view: "skills" },
  { to: "/student?view=opportunities", label: "Opportunities", view: "opportunities" },
  { to: "/student?view=skill-gap", label: "Skill gap", view: "skill-gap" },
  { to: "/student/applications", label: "Applications" },
];

function StudentView() {
  const location = useLocation();
  const [params] = useSearchParams();
  const view = params.get("view");
  const onHome = location.pathname === "/student" || location.pathname === "/student/";

  if (onHome) {
    if (view === "skills") return <StudentSkills />;
    if (view === "opportunities") return <StudentOpportunities />;
    if (view === "skill-gap") return <StudentSkillGap />;
    return <StudentDashboard />;
  }

  return <Outlet />;
}

export default function StudentLayout() {
  const user = getUser();
  const navigate = useNavigate();
  const location = useLocation();
  const [params] = useSearchParams();
  const view = params.get("view");
  const initials = (user?.name || "ST")
    .split(" ")
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  function isActive(link) {
    if (link.view === "opportunities" && (view === "opportunities" || location.pathname.startsWith("/student/opportunities"))) {
      return true;
    }
    if (link.view) return location.pathname.startsWith("/student") && view === link.view;
    if (link.to === "/student") {
      return (location.pathname === "/student" || location.pathname === "/student/") && !view;
    }
    return location.pathname === link.to;
  }

  return (
    <div className="sb-shell">
      <header className="sb-top">
        <div className="sb-top-row">
          <div className="sb-brand">
            <b>SkillBridge</b>
            <small>Student workspace</small>
          </div>
          <nav className="sb-nav">
            {VIEW_LINKS.map((link) => (
              <Link key={link.to} to={link.to} className={isActive(link) ? "active" : ""}>
                {link.label}
              </Link>
            ))}
          </nav>
          <div className="sb-user">
            <div className="sb-avatar">{initials}</div>
            <span>{user?.name || "Student"}</span>
            <button
              className="btn small secondary"
              onClick={() => {
                clearSession();
                navigate("/login");
              }}
            >
              Logout
            </button>
          </div>
        </div>
      </header>
      <main className="sb-main">
        <StudentView />
      </main>
    </div>
  );
}

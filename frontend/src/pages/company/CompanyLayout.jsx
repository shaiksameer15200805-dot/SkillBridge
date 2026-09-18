import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { clearSession, getUser } from "../../api";

export default function CompanyLayout() {
  const user = getUser();
  const navigate = useNavigate();
  return (
    <div className="shell">
      <header className="topbar">
        <strong>AICP · Company</strong>
        <nav>
          <NavLink to="/company" end>Dashboard</NavLink>
          <NavLink to="/company/post">Post opportunity</NavLink>
          <span style={{ color: "#c9d7ff" }}>{user?.company_name || user?.name}</span>
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
      <main className="page">
        <Outlet />
      </main>
    </div>
  );
}

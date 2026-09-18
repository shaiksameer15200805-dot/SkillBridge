import { Outlet, useNavigate } from "react-router-dom";
import { clearSession, getUser } from "../../api";

export default function CollegeLayout() {
  const user = getUser();
  const navigate = useNavigate();
  return (
    <div className="shell">
      <header className="topbar">
        <strong>AICP · College</strong>
        <nav>
          <span style={{ color: "#c9d7ff" }}>{user?.college_name || user?.name}</span>
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

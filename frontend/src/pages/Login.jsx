import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { api, getUser, setSession } from "../api";

export default function Login() {
  const navigate = useNavigate();
  const existing = getUser();
  if (existing) return <Navigate to="/" replace />;

  const [email, setEmail] = useState("student@demo.com");
  const [password, setPassword] = useState("student123");
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      const data = await api("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      setSession(data.token, data.user);
      navigate("/");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <div className="auth-brand">
          <p className="muted" style={{ color: "#c9d7ff" }}>Smart India Hackathon MVP</p>
          <h1>Academia–Industry Collaboration Portal</h1>
          <p>
            Students find internships by skill match. Companies shortlist by evidence.
            Colleges see skill gaps — without a black-box ML model.
          </p>
        </div>
        <form className="auth-form" onSubmit={submit}>
          <h2>Sign in</h2>
          <div className="demo-box">
            student@demo.com / student123<br />
            company@demo.com / company123<br />
            college@demo.com / college123
          </div>
          <label>Email</label>
          <input value={email} onChange={(e) => setEmail(e.target.value)} />
          <label>Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          {error && <p className="error">{error}</p>}
          <div className="row" style={{ marginTop: 16 }}>
            <button className="btn" type="submit">Login</button>
            <Link to="/register" className="btn secondary">Register</Link>
          </div>
        </form>
      </div>
    </div>
  );
}

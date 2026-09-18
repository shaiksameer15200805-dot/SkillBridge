import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, setSession } from "../api";

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    role: "student",
    college_name: "National Institute of Technology Demo",
    company_name: "",
    branch: "CSE",
    year: "3rd Year",
  });
  const [error, setError] = useState("");

  function set(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      const data = await api("/api/auth/register", {
        method: "POST",
        body: JSON.stringify(form),
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
          <h1>Create an account</h1>
          <p>Register as a student, company, or college admin for the demo.</p>
        </div>
        <form className="auth-form" onSubmit={submit}>
          <label>Role</label>
          <select value={form.role} onChange={(e) => set("role", e.target.value)}>
            <option value="student">Student</option>
            <option value="company">Company</option>
            <option value="college">College</option>
          </select>
          <label>Name</label>
          <input value={form.name} onChange={(e) => set("name", e.target.value)} required />
          <label>Email</label>
          <input value={form.email} onChange={(e) => set("email", e.target.value)} required />
          <label>Password</label>
          <input type="password" value={form.password} onChange={(e) => set("password", e.target.value)} required />
          {form.role === "student" && (
            <>
              <label>College</label>
              <input value={form.college_name} onChange={(e) => set("college_name", e.target.value)} />
              <label>Branch</label>
              <input value={form.branch} onChange={(e) => set("branch", e.target.value)} />
            </>
          )}
          {form.role === "company" && (
            <>
              <label>Company name</label>
              <input value={form.company_name} onChange={(e) => set("company_name", e.target.value)} />
            </>
          )}
          {form.role === "college" && (
            <>
              <label>College name</label>
              <input value={form.college_name} onChange={(e) => set("college_name", e.target.value)} />
            </>
          )}
          {error && <p className="error">{error}</p>}
          <div className="row" style={{ marginTop: 16 }}>
            <button className="btn" type="submit">Register</button>
            <Link className="btn secondary" to="/login">Back to login</Link>
          </div>
        </form>
      </div>
    </div>
  );
}

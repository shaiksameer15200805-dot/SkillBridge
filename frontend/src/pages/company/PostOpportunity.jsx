import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../api";

export default function PostOpportunity() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    title: "",
    type: "internship",
    description: "",
    location: "",
    stipend: "",
    deadline: "",
    required_skills: "Python, SQL",
  });
  const [error, setError] = useState("");

  function set(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function submit(e) {
    e.preventDefault();
    try {
      const created = await api("/api/company/opportunities", {
        method: "POST",
        body: JSON.stringify({
          ...form,
          required_skills: form.required_skills.split(",").map((s) => s.trim()).filter(Boolean),
        }),
      });
      navigate(`/company/opportunities/${created.id}`);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <h2>Post an opportunity</h2>
      <form className="card" onSubmit={submit}>
        <label>Title</label>
        <input value={form.title} onChange={(e) => set("title", e.target.value)} required />
        <label>Type</label>
        <select value={form.type} onChange={(e) => set("type", e.target.value)}>
          <option value="internship">Internship</option>
          <option value="project">Project</option>
          <option value="job">Job</option>
        </select>
        <label>Required skills (comma separated)</label>
        <input value={form.required_skills} onChange={(e) => set("required_skills", e.target.value)} />
        <label>Location</label>
        <input value={form.location} onChange={(e) => set("location", e.target.value)} />
        <label>Stipend / CTC</label>
        <input value={form.stipend} onChange={(e) => set("stipend", e.target.value)} />
        <label>Deadline</label>
        <input value={form.deadline} onChange={(e) => set("deadline", e.target.value)} placeholder="YYYY-MM-DD" />
        <label>Description</label>
        <textarea value={form.description} onChange={(e) => set("description", e.target.value)} />
        {error && <p className="error">{error}</p>}
        <button className="btn" style={{ marginTop: 12 }} type="submit">Publish</button>
      </form>
    </div>
  );
}

import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../../api";

export default function Applicants() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  async function load() {
    const d = await api(`/api/company/opportunities/${id}/applicants`);
    setData(d);
  }

  useEffect(() => {
    load().catch((e) => setError(e.message));
  }, [id]);

  async function setStatus(applicationId, status) {
    await api(`/api/company/applications/${applicationId}/status`, {
      method: "PUT",
      body: JSON.stringify({ status }),
    });
    load();
  }

  if (error) return <p className="error">{error}</p>;
  if (!data) return <p>Loading applicants…</p>;

  return (
    <div>
      <h2>{data.opportunity.title} — applicants</h2>
      <p className="muted">Sorted by skill match. Required: {(data.opportunity.required_skills || []).join(", ")}</p>
      {data.applicants.map((a) => (
        <div className="card" key={a.application_id} style={{ marginBottom: 12 }}>
          <div className="row" style={{ justifyContent: "space-between" }}>
            <div>
              <h3 style={{ margin: 0 }}>{a.student.name}</h3>
              <p className="muted">
                {a.student.branch} · {a.student.year} · {a.student.college_name}
              </p>
              <p>{a.student.career_goal}</p>
            </div>
            <div>
              <div className="percent">{a.match_percent}%</div>
              <div className="muted">{a.status}</div>
            </div>
          </div>
          <p>{a.explanation}</p>
          <p>
            {(a.matched_skills || []).map((s) => (
              <span className="badge match" key={s}>{s}</span>
            ))}
            {(a.missing_skills || []).map((s) => (
              <span className="badge gap" key={s}>{s}</span>
            ))}
          </p>
          <div className="row">
            <button className="btn small" onClick={() => setStatus(a.application_id, "shortlisted")}>Shortlist</button>
            <button className="btn small teal" onClick={() => setStatus(a.application_id, "selected")}>Select</button>
            <button className="btn small danger" onClick={() => setStatus(a.application_id, "rejected")}>Reject</button>
          </div>
        </div>
      ))}
      {data.applicants.length === 0 && <p className="muted">No applicants yet.</p>}
    </div>
  );
}

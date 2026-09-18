import { useEffect, useState } from "react";
import { api } from "../../api";

export default function CollegeDashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/api/college/dashboard")
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!data) return <p>Loading college analytics…</p>;

  const analytics = data.analytics || {};

  return (
    <div>
      <h2>Placement & skill-gap dashboard</h2>
      <div className="grid">
        <div className="card">
          <div className="muted">Students</div>
          <div className="percent">{data.student_count}</div>
        </div>
        <div className="card">
          <div className="muted">Avg skill match vs open roles</div>
          <div className="percent">{data.avg_match_percent}%</div>
        </div>
        <div className="card">
          <div className="muted">Open opportunities</div>
          <div className="percent">{analytics.opportunity_count}</div>
        </div>
      </div>

      <h3>Applications by status</h3>
      <div className="grid">
        {Object.entries(analytics.applications_by_status || {}).map(([k, v]) => (
          <div className="card" key={k}>
            <div className="muted">{k}</div>
            <strong>{v}</strong>
          </div>
        ))}
      </div>

      <h3>Top skill gaps</h3>
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Skill</th>
              <th>Student–opportunity gaps</th>
            </tr>
          </thead>
          <tbody>
            {(data.skill_gaps || []).map((g) => (
              <tr key={g.skill}>
                <td>{g.skill}</td>
                <td>{g.student_opportunity_gaps}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h3>Students</h3>
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Branch</th>
              <th>Skills</th>
              <th>Avg match</th>
              <th>Applications</th>
              <th>Selected</th>
            </tr>
          </thead>
          <tbody>
            {(data.students || []).map((s) => (
              <tr key={s.id}>
                <td>{s.name}</td>
                <td>{s.branch}</td>
                <td>{(s.skills || []).join(", ")}</td>
                <td>{s.avg_match_percent}%</td>
                <td>{s.application_count}</td>
                <td>{s.selected_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h3>Industry opportunities</h3>
      {(data.opportunities || []).map((opp) => (
        <div className="card" key={opp.id} style={{ marginBottom: 10 }}>
          <strong>{opp.title}</strong>
          <span className="badge">{opp.type}</span>
          <p className="muted">{opp.company_name} · {opp.location}</p>
          <p>
            {(opp.required_skills || []).map((sk) => (
              <span className="badge" key={sk}>{sk}</span>
            ))}
          </p>
        </div>
      ))}

      <h3>Recommended campus learning</h3>
      <div className="grid">
        {(data.recommended_learning || []).map((c) => (
          <div className="card" key={c.skill}>
            <strong>{c.title}</strong>
            <p className="muted">Closes gap in {c.skill}</p>
            <a href={c.link} target="_blank" rel="noreferrer">Open</a>
          </div>
        ))}
      </div>
    </div>
  );
}

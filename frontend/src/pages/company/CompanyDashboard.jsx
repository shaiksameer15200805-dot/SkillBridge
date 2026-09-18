import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../api";

export default function CompanyDashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/api/company/dashboard")
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!data) return <p>Loading dashboard…</p>;

  return (
    <div>
      <h2>Company dashboard</h2>
      <div className="grid">
        <div className="card">
          <div className="muted">Opportunities</div>
          <div className="percent">{data.total_opportunities}</div>
        </div>
        <div className="card">
          <div className="muted">Applicants</div>
          <div className="percent">{data.total_applicants}</div>
        </div>
      </div>
      {data.opportunities.map((opp) => (
        <div className="card" key={opp.id} style={{ marginTop: 12 }}>
          <span className="badge">{opp.type}</span>
          <h3>{opp.title}</h3>
          <p className="muted">{opp.applicant_count} applicants</p>
          <p>
            {(opp.required_skills || []).map((s) => (
              <span className="badge" key={s}>{s}</span>
            ))}
          </p>
          <Link className="btn small" to={`/company/opportunities/${opp.id}`}>
            View applicants
          </Link>
        </div>
      ))}
    </div>
  );
}

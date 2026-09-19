import { useEffect, useState } from "react";
import { collegeApi } from "../../lib/api";

const Card = ({ label, value }) => (
  <div className="college-card">
    <span>{label}</span>
    <strong>{value ?? 0}</strong>
  </div>
);

export default function CollegeDashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    collegeApi.analytics().then(setData).catch(e => setError(e.message));
  }, []);

  if (error) return <div className="college-page"><p className="error">{error}</p></div>;
  if (!data) return <div className="college-page"><p>Loading college analytics…</p></div>;

  const list = (items) => Object.entries(items || {});
  const cards = data.cards || {};

  return (
    <div className="college-page">
      <header className="college-header">
        <div><small>COLLEGE PORTAL</small><h1>College Dashboard</h1></div>
      </header>

      <div className="college-cards">
        <Card label="Total Students" value={cards.total_students ?? data.student_count} />
        <Card label="Active Opportunities" value={cards.active_opportunities ?? data.analytics?.opportunity_count} />
        <Card label="Internship Participation" value={cards.internship_participation ?? 0} />
        <Card label="Students Placed" value={cards.students_placed ?? 0} />
      </div>

      <div className="college-grid">
        <section className="college-panel">
          <h2>Top Skills</h2>
          {(data.top_skills || []).map(([name, count]) => (
            <div className="metric-row" key={name}><span>{name}</span><b>{count}</b></div>
          ))}
        </section>
        <section className="college-panel">
          <h2>Top Skill Gaps</h2>
          {(data.top_skill_gaps || []).map(([name, count]) => (
            <div className="metric-row" key={name}><span>{name}</span><b>{count}</b></div>
          ))}
        </section>
        <section className="college-panel">
          <h2>Applications</h2>
          {list(data.application_status).map(([name, count]) => (
            <div className="metric-row" key={name}><span>{name}</span><b>{count}</b></div>
          ))}
        </section>
        <section className="college-panel">
          <h2>Placement Statistics</h2>
          {list(data.placement_statistics).map(([name, count]) => (
            <div className="metric-row" key={name}><span>{name}</span><b>{count}</b></div>
          ))}
        </section>
      </div>
    </div>
  );
}

import { useEffect, useState } from "react";
import { collegeApi } from "../../lib/api";

function Bars({ title, data }) {
  const entries = Object.entries(data || {});
  const max = Math.max(...entries.map(([, v]) => Number(v)), 1);
  return (
    <section className="college-panel">
      <h2>{title}</h2>
      {entries.map(([label, value]) => (
        <div key={label} className="bar-item">
          <div className="bar-label"><span>{label}</span><b>{value}</b></div>
          <div className="bar-track"><i style={{ width: `${(Number(value) / max) * 100}%` }} /></div>
        </div>
      ))}
    </section>
  );
}

export default function CollegeAnalytics() {
  const [data, setData] = useState(null);
  useEffect(() => { collegeApi.analytics().then(setData).catch(console.error); }, []);
  if (!data) return <div className="college-page"><p>Loading analytics…</p></div>;

  return (
    <div className="college-page">
      <div className="college-header"><div><small>COLLEGE PORTAL</small><h1>Analytics</h1></div></div>
      <div className="college-grid">
        <Bars title="Application Status" data={data.application_status} />
        <Bars title="Internship Participation" data={data.internship_statistics} />
        <Bars title="Placement Statistics" data={data.placement_statistics} />
        <section className="college-panel">
          <h2>Skill Distribution</h2>
          {(data.top_skills || []).map(([skill, count]) => (
            <div className="bar-item" key={skill}>
              <div className="bar-label"><span>{skill}</span><b>{count}</b></div>
              <div className="bar-track"><i style={{width: `${Math.min(100, count * 10)}%`}} /></div>
            </div>
          ))}
        </section>
      </div>
    </div>
  );
}

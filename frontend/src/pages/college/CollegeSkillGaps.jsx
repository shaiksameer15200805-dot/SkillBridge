import { useEffect, useState } from "react";
import { collegeApi } from "../../lib/api";

export default function CollegeSkillGaps() {
  const [gaps, setGaps] = useState([]);
  useEffect(() => {
    collegeApi.skillGaps()
      .then(d => setGaps(d.skill_gaps || []))
      .catch(console.error);
  }, []);

  return (
    <div className="college-page">
      <div className="college-header"><div><small>COLLEGE PORTAL</small><h1>Skill Gaps</h1></div></div>
      <section className="college-panel">
        <h2>Top Skill Gaps</h2>
        {gaps.length ? gaps.map(g => (
          <div className="metric-row" key={g.skill}><span>{g.skill}</span><b>{g.students} students</b></div>
        )) : <p>No skill-gap data available yet.</p>}
      </section>
    </div>
  );
}

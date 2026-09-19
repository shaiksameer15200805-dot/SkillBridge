import { useEffect, useState } from "react";
import { collegeApi } from "../../lib/api";

export default function CollegeStudents() {
  const [students, setStudents] = useState([]);
  const [search, setSearch] = useState("");
  const [degree, setDegree] = useState("");

  useEffect(() => {
    collegeApi.students({ search, degree })
      .then(d => setStudents(d.students || []))
      .catch(console.error);
  }, [search, degree]);

  return (
    <div className="college-page">
      <div className="college-header">
        <div><small>COLLEGE PORTAL</small><h1>Students</h1></div>
      </div>

      <div className="college-filters">
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search student…" />
        <select value={degree} onChange={e => setDegree(e.target.value)}>
          <option value="">All degrees</option>
          <option>B.Tech</option><option>B.E.</option><option>B.Sc</option>
          <option>M.Tech</option><option>MCA</option>
        </select>
      </div>

      <div className="college-panel table-wrap">
        <table>
          <thead><tr>
            <th>Student</th><th>Degree</th><th>CGPA</th><th>Top Skills</th>
            <th>Internship</th><th>Placement</th>
          </tr></thead>
          <tbody>
            {(students || []).map(s => (
              <tr key={s.id}>
                <td>{s.name}</td>
                <td>{s.degree}</td>
                <td>{s.cgpa ?? "—"}</td>
                <td>{(s.top_skills || []).join(", ") || "—"}</td>
                <td>{s.internship_status}</td>
                <td>{s.placement_status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

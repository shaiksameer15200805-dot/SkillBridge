import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { AlertBanner, LoadingCard, StudentCard } from "./StudentCards.jsx";
import { getStudentSkillGap } from "./studentApi";

function SkillChips({ skills, tone }) {
  if (!skills.length) {
    return (
      <div className="sb-empty-inline">
        <p className="muted">None listed yet.</p>
      </div>
    );
  }
  return (
    <div className="sb-chip-row">
      {skills.map((skill) => (
        <span className={`sb-pill ${tone}`} key={skill}>
          {skill}
        </span>
      ))}
    </div>
  );
}

export default function StudentSkillGap() {
  const [data, setData] = useState({
    currentSkills: [],
    missingSkills: [],
    recommendedCourses: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    getStudentSkillGap()
      .then((payload) => {
        if (active) setData(payload);
      })
      .catch((err) => {
        if (active) setError(err.message || "Could not load skill gap");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  if (loading) {
    return (
      <div>
        <p className="sb-kicker">Skill gap</p>
        <LoadingCard message="Analyzing skill gaps & learning paths…" />
      </div>
    );
  }

  return (
    <div>
      <p className="sb-kicker">Skill gap</p>
      <div className="sb-hero">
        <div>
          <h2>Close the gaps</h2>
          <p className="muted">{data.explanation || "Current skills versus missing skills, with courses to cover each gap."}</p>
        </div>
      </div>

      {error && <AlertBanner type="error" message={error} onClose={() => setError("")} />}

      <div className="sb-gap-grid">
        <StudentCard
          title="Current skills"
          action={
            <Link className="muted" to="/student?view=skills">
              Manage
            </Link>
          }
        >
          <SkillChips skills={data.currentSkills} tone="ok" />
        </StudentCard>

        <StudentCard title="Missing skills">
          <SkillChips skills={data.missingSkills} tone="warn" />
        </StudentCard>
      </div>

      <StudentCard title="Recommended courses">
        {data.recommendedCourses.length === 0 ? (
          <div className="sb-empty-inline">
            <p className="ok">No course recommendations needed—you match the required skills!</p>
          </div>
        ) : (
          <ul className="sb-course-list">
            {data.recommendedCourses.map((course) => (
              <li key={course.skill || course.title} className="sb-item-row">
                <div>
                  <strong>{course.title}</strong>
                  <div className="muted">
                    For {course.skill}
                    {course.provider ? ` · ${course.provider}` : ""}
                    {course.hours ? ` · ${course.hours}h` : ""}
                  </div>
                </div>
                {course.link ? (
                  <a className="btn small secondary" href={course.link} target="_blank" rel="noreferrer">
                    Open ↗
                  </a>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </StudentCard>
    </div>
  );
}

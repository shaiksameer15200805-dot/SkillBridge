import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { AlertBanner, ItemRow, LoadingCard, MetricCard, StudentCard } from "./StudentCards.jsx";
import { getStudentDashboardData } from "./studentApi";

export default function StudentDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const payload = await getStudentDashboardData();
      setData(payload);
    } catch (err) {
      setError(err.message || "Could not load dashboard data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (loading) {
    return (
      <div>
        <p className="sb-kicker">Student dashboard</p>
        <LoadingCard message="Loading your personalized dashboard…" />
      </div>
    );
  }

  if (error && !data) {
    return (
      <div>
        <p className="sb-kicker">Student dashboard</p>
        <AlertBanner message={error} onRetry={load} />
      </div>
    );
  }

  const profile = data?.profile || {};
  const firstName = (profile.name || "Student").split(" ")[0];
  const completion = data?.completion ?? 0;
  const topMatch = data?.topMatch ?? 0;
  const recommended = data?.recommended || [];
  const topSkills = data?.skills || [];
  const appCounts = data?.appCounts || { total: 0, applied: 0, under_review: 0, shortlisted: 0, selected: 0, rejected: 0 };
  const skillGaps = data?.topGaps || [];

  return (
    <div>
      <p className="sb-kicker">Student dashboard</p>
      <div className="sb-hero">
        <div>
          <h1>Welcome back, {firstName}</h1>
          <p className="muted">
            {profile.branch || "General"} · {profile.year || "Student"} · {profile.university || "University"}
          </p>
        </div>
        <Link className="btn" to="/student?view=opportunities">
          Browse opportunities
        </Link>
      </div>

      <div className="grid sb-dash-metrics">
        <MetricCard
          label="Profile completion"
          value={`${completion}%`}
          percent={completion}
          hint="Complete profile, skills and a certification."
          to="/student/profile"
        />
        <MetricCard
          label="Top match percentage"
          value={`${topMatch}%`}
          percent={topMatch}
          hint={recommended[0] ? recommended[0].title : "No roles yet"}
          to="/student?view=opportunities"
        />
        <MetricCard
          label="Applications"
          value={appCounts.total}
          hint={`${appCounts.shortlisted} shortlisted · ${appCounts.under_review} in review`}
          to="/student/applications"
        />
      </div>

      <div className="sb-dash-grid">
        <StudentCard
          title="Top skills"
          action={
            <Link className="muted" to="/student?view=skills">
              Manage
            </Link>
          }
        >
          {topSkills.length === 0 && <p className="muted">Add skills to improve match scores.</p>}
          <div className="sb-top-skills">
            {topSkills.slice(0, 5).map((skill) => (
              <span className="sb-pill navy" key={skill.name}>
                {skill.name}
              </span>
            ))}
          </div>
        </StudentCard>

        <StudentCard
          title="Recommended"
          action={
            <Link className="muted" to="/student?view=opportunities">
              View all
            </Link>
          }
        >
          {recommended.length === 0 && <p className="muted">No recommendations available yet.</p>}
          {recommended.map((opp) => (
            <ItemRow
              key={opp.id}
              to="/student?view=opportunities"
              label={`${opp.title}`}
              value={`${opp.matchPercent}%`}
            />
          ))}
        </StudentCard>

        <StudentCard
          title="Skill gaps"
          action={
            <Link className="muted" to="/student?view=skill-gap">
              Analysis
            </Link>
          }
        >
          {skillGaps.length === 0 && <p className="ok">No major gaps on open roles.</p>}
          {skillGaps.map(([skill, count]) => (
            <ItemRow
              key={skill}
              to="/student?view=skill-gap"
              label={skill}
              value={`${count} ${count === 1 ? "role" : "roles"}`}
            />
          ))}
        </StudentCard>

        <StudentCard
          title="Applications"
          action={
            <Link className="muted" to="/student/applications">
              Tracker
            </Link>
          }
        >
          <ItemRow label="Applied" value={appCounts.applied} to="/student/applications" />
          <ItemRow label="Under Review" value={appCounts.under_review} to="/student/applications" />
          <ItemRow label="Shortlisted" value={appCounts.shortlisted} to="/student/applications" />
          <ItemRow label="Selected" value={appCounts.selected} to="/student/applications" />
        </StudentCard>
      </div>
    </div>
  );
}


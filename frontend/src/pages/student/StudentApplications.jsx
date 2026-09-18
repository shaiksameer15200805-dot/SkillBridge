import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { AlertBanner, LoadingCard, MetricCard } from "./StudentCards.jsx";
import { getStudentApplications } from "./studentApi";

const STATUS_CONFIG = {
  applied: { label: "Applied", pillClass: "navy", step: 1 },
  under_review: { label: "Under Review", pillClass: "review", step: 2 },
  shortlisted: { label: "Shortlisted", pillClass: "warn", step: 3 },
  selected: { label: "Selected", pillClass: "ok", step: 4 },
  rejected: { label: "Rejected", pillClass: "bad", step: -1 },
};

const PIPELINE_STEPS = [
  { key: "applied", label: "Applied" },
  { key: "under_review", label: "Under Review" },
  { key: "shortlisted", label: "Shortlisted" },
  { key: "selected", label: "Selected" },
];

function normalizeStatus(rawStatus) {
  const clean = (rawStatus || "").toLowerCase().trim().replace(/[\s-]+/g, "_");
  if (clean === "review" || clean === "in_review" || clean === "underreview") {
    return "under_review";
  }
  return STATUS_CONFIG[clean] ? clean : "applied";
}

function getStatusDetails(rawStatus) {
  const key = normalizeStatus(rawStatus);
  return STATUS_CONFIG[key] || { label: rawStatus || "Applied", pillClass: "navy", step: 1 };
}

function formatDate(dateString) {
  if (!dateString) return "—";
  try {
    const parts = dateString.split("-");
    if (parts.length === 3) {
      const year = parseInt(parts[0], 10);
      const month = parseInt(parts[1], 10) - 1;
      const day = parseInt(parts[2], 10);
      const d = new Date(year, month, day);
      if (!isNaN(d.getTime())) {
        return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
      }
    }
    const d = new Date(dateString);
    if (!isNaN(d.getTime())) {
      return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
    }
  } catch {
    /* fallback */
  }
  return dateString;
}

export default function StudentApplications() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await getStudentApplications();
      setApplications(data || []);
    } catch (err) {
      setError(err.message || "Failed to load applications.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const counts = useMemo(() => {
    const summary = {
      total: applications.length,
      applied: 0,
      under_review: 0,
      shortlisted: 0,
      selected: 0,
      rejected: 0,
    };
    applications.forEach((app) => {
      const key = normalizeStatus(app.status);
      if (summary[key] !== undefined) {
        summary[key] += 1;
      }
    });
    return summary;
  }, [applications]);

  const filteredApplications = useMemo(() => {
    const query = searchQuery.toLowerCase().trim();
    return applications.filter((app) => {
      const matchesFilter =
        statusFilter === "all" ? true : normalizeStatus(app.status) === statusFilter;
      const matchesQuery =
        !query ||
        (app.opportunityTitle && app.opportunityTitle.toLowerCase().includes(query)) ||
        (app.companyName && app.companyName.toLowerCase().includes(query));
      return matchesFilter && matchesQuery;
    });
  }, [applications, statusFilter, searchQuery]);

  return (
    <div>
      <p className="sb-kicker">Applications</p>
      <div className="sb-hero">
        <div>
          <h2>Application Tracker</h2>
          <p className="muted">
            Monitor real-time status updates, hiring pipelines, and feedback on your submissions.
          </p>
        </div>
        <Link className="btn" to="/student?view=opportunities">
          Browse Opportunities
        </Link>
      </div>

      <div className="grid sb-dash-metrics">
        <MetricCard
          label="Total Submitted"
          value={counts.total}
          hint="Applications placed"
        />
        <MetricCard
          label="Under Review"
          value={counts.under_review}
          hint="Evaluating profile"
        />
        <MetricCard
          label="Shortlisted"
          value={counts.shortlisted}
          hint="Moved to next stage"
        />
        <MetricCard
          label="Selected"
          value={counts.selected}
          hint={counts.rejected > 0 ? `${counts.rejected} rejected` : "Offers received"}
        />
      </div>

      <div className="card sb-app-toolbar">
        <input
          type="text"
          className="sb-app-search"
          placeholder="Search by role or company…"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          aria-label="Search applications"
        />
        <div className="sb-app-filters">
          {[
            { id: "all", label: "All" },
            { id: "applied", label: "Applied" },
            { id: "under_review", label: "Under Review" },
            { id: "shortlisted", label: "Shortlisted" },
            { id: "selected", label: "Selected" },
            { id: "rejected", label: "Rejected" },
          ].map((item) => (
            <button
              key={item.id}
              type="button"
              className={`btn small ${statusFilter === item.id ? "" : "secondary"}`}
              onClick={() => setStatusFilter(item.id)}
            >
              {item.label}
              {item.id !== "all" && counts[item.id] > 0 ? ` (${counts[item.id]})` : ""}
            </button>
          ))}
        </div>
      </div>

      {loading && <LoadingCard message="Loading your submitted applications…" />}

      {error && !loading && <AlertBanner message={error} onRetry={load} />}

      {!loading && !error && applications.length === 0 && (
        <div className="card sb-empty-card">
          <h3>No applications yet</h3>
          <p className="muted">
            You have not submitted any applications yet. Explore available internships and jobs to apply.
          </p>
          <Link to="/student?view=opportunities" className="btn" style={{ marginTop: 14 }}>
            Browse Opportunities
          </Link>
        </div>
      )}

      {!loading && !error && applications.length > 0 && filteredApplications.length === 0 && (
        <div className="card sb-empty-card">
          <h3>No matching applications</h3>
          <p className="muted">
            No applications match your selected filter or search term.
          </p>
          <button
            type="button"
            className="btn secondary small"
            style={{ marginTop: 14 }}
            onClick={() => {
              setStatusFilter("all");
              setSearchQuery("");
            }}
          >
            Clear Filters
          </button>
        </div>
      )}

      {!loading && !error && filteredApplications.length > 0 && (
        <div className="card">
          <div className="sb-table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Opportunity</th>
                  <th>Company</th>
                  <th>Match</th>
                  <th>Applied Date</th>
                  <th>Hiring Pipeline</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredApplications.map((app) => {
                  const statusDetails = getStatusDetails(app.status);
                  const isRejected = statusDetails.step === -1;

                  return (
                    <tr key={app.id}>
                      <td>
                        <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                          <Link
                            to={`/student/opportunities/${app.opportunityId}`}
                            style={{ fontWeight: 650, color: "var(--navy)" }}
                          >
                            {app.opportunityTitle || "Opportunity"}
                          </Link>
                          <div>
                            <span className="sb-pill navy" style={{ margin: 0, fontSize: 11, padding: "2px 8px" }}>
                              {app.type || "internship"}
                            </span>
                          </div>
                        </div>
                      </td>
                      <td>
                        <div>
                          <strong>{app.companyName || "Company"}</strong>
                          {app.location ? <div className="muted" style={{ fontSize: 12 }}>{app.location}</div> : null}
                        </div>
                      </td>
                      <td>
                        <span style={{ fontWeight: 700, color: "var(--navy)" }}>
                          {app.matchPercent !== undefined ? `${app.matchPercent}%` : "—"}
                        </span>
                      </td>
                      <td>
                        <span className="muted">{formatDate(app.appliedAt)}</span>
                      </td>
                      <td>
                        {isRejected ? (
                          <span className="sb-pill bad" style={{ margin: 0 }}>
                            Application Closed
                          </span>
                        ) : (
                          <div style={{ display: "inline-flex", gap: 4, flexWrap: "wrap" }}>
                            {PIPELINE_STEPS.map((step, idx) => {
                              const isCurrent = statusDetails.step === idx + 1;
                              const isPassed = statusDetails.step >= idx + 1;
                              const tone = isCurrent
                                ? statusDetails.pillClass
                                : isPassed
                                ? "ok"
                                : "muted";
                              return (
                                <span
                                  key={step.key}
                                  className={`sb-pill ${tone}`}
                                  style={{ margin: 0, fontSize: 11, padding: "2px 7px" }}
                                >
                                  {step.label}
                                </span>
                              );
                            })}
                          </div>
                        )}
                      </td>
                      <td>
                        <span className={`sb-pill ${statusDetails.pillClass}`} style={{ margin: 0 }}>
                          {statusDetails.label}
                        </span>
                      </td>
                      <td>
                        <Link
                          to={`/student/opportunities/${app.opportunityId}`}
                          className="btn small secondary"
                          style={{ whiteSpace: "nowrap" }}
                        >
                          View Details
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}


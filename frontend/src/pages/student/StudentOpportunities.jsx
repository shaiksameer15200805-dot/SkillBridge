import { useEffect, useState } from "react";
import { AlertBanner, LoadingCard } from "./StudentCards.jsx";
import { applyToOpportunity, getStudentOpportunities } from "./studentApi";

function getStatusPill(raw) {
  const s = (raw || "").toLowerCase().replace(/[\s-]+/g, "_");
  if (s === "applied") return { tone: "navy", label: "Applied" };
  if (s === "under_review" || s === "review") return { tone: "review", label: "Under Review" };
  if (s === "shortlisted") return { tone: "warn", label: "Shortlisted" };
  if (s === "selected") return { tone: "ok", label: "Selected" };
  if (s === "rejected") return { tone: "bad", label: "Rejected" };
  return { tone: "navy", label: raw || "Applied" };
}

function ChipList({ label, skills, tone }) {
  const safeSkills = Array.isArray(skills) ? skills : [];
  return (
    <div className="sb-opp-field">
      <span className="muted">{label}</span>
      <div className="sb-chip-row">
        {safeSkills.length === 0 ? (
          <span className="muted" style={{ fontSize: 13 }}>None</span>
        ) : (
          safeSkills.map((skill) => (
            <span className={`sb-pill ${tone}`} key={`${label}-${skill}`}>
              {skill}
            </span>
          ))
        )}
      </div>
    </div>
  );
}

function OpportunityCard({ opportunity, selected, onSelect, onApply, applying }) {
  const status = opportunity.applicationStatus;
  const statusInfo = status ? getStatusPill(status) : null;

  return (
    <article
      className={`card sb-opp-card ${selected ? "sb-opp-card-active" : ""}`}
      onClick={() => onSelect(opportunity.id)}
    >
      <div className="sb-opp-top">
        <div>
          <span className="sb-pill navy">{opportunity.type}</span>
          <h3>{opportunity.title}</h3>
          <p className="muted">{opportunity.company}</p>
        </div>
        <div className="sb-opp-match">
          <div className="percent">{opportunity.matchPercent}%</div>
          <span className="muted">match</span>
        </div>
      </div>
      <p>
        <strong>Location</strong> {opportunity.location || "—"}
      </p>
      <ChipList label="Required skills" skills={opportunity.requiredSkills} tone="navy" />
      <ChipList label="Matched skills" skills={opportunity.matchedSkills} tone="ok" />
      <ChipList label="Missing skills" skills={opportunity.missingSkills} tone="warn" />
      {status ? (
        <div style={{ marginTop: 10 }}>
          <span className={`sb-pill ${statusInfo.tone}`} style={{ margin: 0 }}>
            Status: {statusInfo.label}
          </span>
        </div>
      ) : (
        <button
          className="btn"
          type="button"
          disabled={applying}
          onClick={(e) => {
            e.stopPropagation();
            onApply(opportunity.id);
          }}
        >
          {applying ? "Applying…" : "Apply"}
        </button>
      )}
    </article>
  );
}

function OpportunityDetail({ opportunity, onApply, applying }) {
  if (!opportunity) {
    return (
      <section className="card sb-opp-detail">
        <p className="muted">Select an opportunity to see details.</p>
      </section>
    );
  }

  const status = opportunity.applicationStatus;

  return (
    <section className="card sb-opp-detail">
      <p className="sb-kicker">Opportunity detail</p>
      <span className="sb-pill navy">{opportunity.type}</span>
      <h2>{opportunity.title}</h2>
      <p className="muted">
        {opportunity.company} · {opportunity.location}
      </p>
      <div className="percent">{opportunity.matchPercent}%</div>
      <p>{opportunity.description}</p>
      {opportunity.stipend && (
        <p>
          <strong>Stipend / CTC</strong> {opportunity.stipend}
        </p>
      )}
      {opportunity.deadline && (
        <p>
          <strong>Deadline</strong> {opportunity.deadline}
        </p>
      )}
      {opportunity.explanation && <p className="sb-note">{opportunity.explanation}</p>}
      <ChipList label="Required skills" skills={opportunity.requiredSkills} tone="navy" />
      <ChipList label="Matched skills" skills={opportunity.matchedSkills} tone="ok" />
      <ChipList label="Missing skills" skills={opportunity.missingSkills} tone="warn" />
      {status ? (
        <div style={{ marginTop: 14 }}>
          <span className={`sb-pill ${getStatusPill(status).tone}`} style={{ margin: 0 }}>
            Application status: {getStatusPill(status).label}
          </span>
        </div>
      ) : (
        <button className="btn" type="button" disabled={applying} onClick={() => onApply(opportunity.id)} style={{ marginTop: 8 }}>
          {applying ? "Applying…" : "Apply"}
        </button>
      )}
    </section>
  );
}

export default function StudentOpportunities() {
  const [items, setItems] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [type, setType] = useState("all");
  const [loading, setLoading] = useState(true);
  const [applying, setApplying] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await getStudentOpportunities();
      setItems(data);
      setSelectedId((current) => current || data[0]?.id || null);
    } catch (err) {
      setError(err.message || "Could not load opportunities");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function onApply(id) {
    setApplying(true);
    setError("");
    try {
      const data = await applyToOpportunity(id);
      setItems(data);
      setMessage("Application submitted.");
    } catch (err) {
      setError(err.message || "Could not apply");
    } finally {
      setApplying(false);
    }
  }

  const visible = items.filter((opp) => (type === "all" ? true : opp.type === type));
  const selected = visible.find((opp) => opp.id === selectedId) || visible[0] || null;

  return (
    <div>
      <p className="sb-kicker">Opportunities</p>
      <div className="sb-hero">
        <div>
          <h2>Open roles</h2>
          <p className="muted">Match scores come from the API. This page only displays them.</p>
        </div>
        <select value={type} onChange={(e) => setType(e.target.value)} style={{ maxWidth: 160 }} aria-label="Filter opportunity types">
          <option value="all">All types</option>
          <option value="internship">Internships</option>
          <option value="project">Projects</option>
          <option value="job">Jobs</option>
        </select>
      </div>

      {error && <AlertBanner type="error" message={error} onClose={() => setError("")} />}
      {message && !error && <AlertBanner type="success" message={message} onClose={() => setMessage("")} />}
      {loading && <LoadingCard message="Loading opportunities & match scores…" />}

      {!loading && (
        <div className="sb-opp-layout">
          <div className="sb-opp-list">
            {visible.map((opp) => (
              <OpportunityCard
                key={opp.id}
                opportunity={opp}
                selected={selected?.id === opp.id}
                onSelect={setSelectedId}
                onApply={onApply}
                applying={applying}
              />
            ))}
            {visible.length === 0 && (
              <div className="sb-empty-inline">
                <p className="muted">No opportunities found for this filter.</p>
              </div>
            )}
          </div>
          <OpportunityDetail opportunity={selected} onApply={onApply} applying={applying} />
        </div>
      )}
    </div>
  );
}

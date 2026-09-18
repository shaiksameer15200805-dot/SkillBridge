import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../../api";
import { AlertBanner, LoadingCard } from "./StudentCards.jsx";

function getStatusPill(raw) {
  const s = (raw || "").toLowerCase().replace(/[\s-]+/g, "_");
  if (s === "applied") return { tone: "navy", label: "Applied" };
  if (s === "under_review" || s === "review") return { tone: "review", label: "Under Review" };
  if (s === "shortlisted") return { tone: "warn", label: "Shortlisted" };
  if (s === "selected") return { tone: "ok", label: "Selected" };
  if (s === "rejected") return { tone: "bad", label: "Rejected" };
  return { tone: "navy", label: raw || "Applied" };
}

export default function OpportunityDetail() {
  const { id } = useParams();
  const [opp, setOpp] = useState(null);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const [applying, setApplying] = useState(false);

  useEffect(() => {
    api(`/api/opportunities/${id}`)
      .then((data) => {
        setOpp(data);
        setStatus(data.application_status || "");
      })
      .catch((e) => setError(e.message));
  }, [id]);

  async function apply() {
    setApplying(true);
    setError("");
    try {
      const data = await api("/api/student/applications", {
        method: "POST",
        body: JSON.stringify({ opportunity_id: Number(id) }),
      });
      setStatus(data.status);
    } catch (e) {
      setError(e.message);
    } finally {
      setApplying(false);
    }
  }

  if (error && !opp) {
    return (
      <div>
        <Link to="/student?view=opportunities" className="btn small secondary" style={{ marginBottom: 14 }}>
          ← Back to Opportunities
        </Link>
        <AlertBanner message={error} />
      </div>
    );
  }

  if (!opp) {
    return (
      <div>
        <p className="sb-kicker">Opportunity detail</p>
        <LoadingCard message="Loading opportunity details…" />
      </div>
    );
  }

  const statusInfo = status ? getStatusPill(status) : null;

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Link to="/student?view=opportunities" className="btn small secondary">
          ← Back to Opportunities
        </Link>
      </div>

      <p className="sb-kicker">Opportunity detail</p>

      {error && <AlertBanner message={error} onClose={() => setError("")} />}

      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12, flexWrap: "wrap" }}>
          <div>
            <span className="sb-pill navy">{opp.type}</span>
            <h1 style={{ margin: "6px 0", fontSize: 24, fontWeight: 750 }}>{opp.title}</h1>
            <p className="muted" style={{ margin: 0 }}>
              {opp.company_name} · {opp.location || "Location not specified"} {opp.stipend ? `· ${opp.stipend}` : ""}
              {opp.deadline ? ` · Deadline: ${opp.deadline}` : ""}
            </p>
          </div>
          {opp.match_percent !== undefined && (
            <div style={{ textAlign: "right" }}>
              <div className="percent">{opp.match_percent}%</div>
              <span className="muted" style={{ fontSize: 13 }}>match</span>
            </div>
          )}
        </div>

        <div style={{ margin: "16px 0", lineHeight: 1.6 }}>
          <p>{opp.description}</p>
          {opp.explanation && <p className="sb-note">{opp.explanation}</p>}
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 10, margin: "14px 0" }}>
          {opp.matched_skills && opp.matched_skills.length > 0 && (
            <div>
              <span className="muted" style={{ display: "block", fontSize: 12, marginBottom: 4 }}>Matched Skills</span>
              <div className="sb-chip-row">
                {opp.matched_skills.map((s) => (
                  <span className="sb-pill ok" key={s}>{s}</span>
                ))}
              </div>
            </div>
          )}

          {opp.missing_skills && opp.missing_skills.length > 0 && (
            <div>
              <span className="muted" style={{ display: "block", fontSize: 12, marginBottom: 4 }}>Missing Skills</span>
              <div className="sb-chip-row">
                {opp.missing_skills.map((s) => (
                  <span className="sb-pill warn" key={s}>{s}</span>
                ))}
              </div>
            </div>
          )}
        </div>

        <div style={{ marginTop: 18, paddingTop: 14, borderTop: "1px solid var(--line)" }}>
          {status ? (
            <span className={`sb-pill ${statusInfo.tone}`} style={{ fontSize: 13, padding: "6px 14px", margin: 0 }}>
              Application Status: {statusInfo.label}
            </span>
          ) : (
            <button className="btn" type="button" disabled={applying} onClick={apply}>
              {applying ? "Submitting Application…" : "Apply Now"}
            </button>
          )}
        </div>
      </div>

      {opp.recommended_learning && opp.recommended_learning.length > 0 && (
        <div>
          <h2 style={{ fontSize: 20, marginBottom: 12 }}>Close the gaps with recommended courses</h2>
          <div className="grid">
            {opp.recommended_learning.map((c) => (
              <div className="card" key={c.skill || c.title} style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                <div>
                  <span className="sb-pill warn" style={{ fontSize: 11, marginBottom: 6 }}>For {c.skill}</span>
                  <h3 style={{ margin: "4px 0 6px", fontSize: 16 }}>{c.title}</h3>
                  <p className="muted" style={{ fontSize: 13, margin: "0 0 12px" }}>
                    {c.provider ? c.provider : "Online Resource"}{c.hours ? ` · ${c.hours} hours` : ""}
                  </p>
                </div>
                {c.link && (
                  <div>
                    <a className="btn small secondary" href={c.link} target="_blank" rel="noreferrer">
                      Open Course ↗
                    </a>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

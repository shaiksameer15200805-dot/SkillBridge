import { useEffect, useState } from "react";
import { AlertBanner, LoadingCard, StudentCard } from "./StudentCards.jsx";
import {
  addStudentCertification,
  getStudentProfile,
  removeStudentCertification,
  saveStudentProfile,
} from "./studentApi";

const EMPTY_PROFILE = {
  name: "",
  email: "",
  university: "",
  degree: "",
  branch: "",
  year: "",
  cgpa: "",
  careerGoal: "",
};

const EMPTY_CERT = { title: "", issuer: "", year: "2026" };

const FIELDS = [
  { key: "name", label: "Name", type: "text" },
  { key: "email", label: "Email", type: "email" },
  { key: "university", label: "University", type: "text" },
  { key: "degree", label: "Degree", type: "text" },
  { key: "branch", label: "Branch", type: "text" },
  { key: "year", label: "Year", type: "text" },
  { key: "cgpa", label: "CGPA", type: "text" },
];

export default function StudentProfile() {
  const [profile, setProfile] = useState(EMPTY_PROFILE);
  const [certifications, setCertifications] = useState([]);
  const [draft, setDraft] = useState(EMPTY_PROFILE);
  const [cert, setCert] = useState(EMPTY_CERT);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await getStudentProfile();
      setProfile(data.profile);
      setDraft(data.profile);
      setCertifications(data.certifications);
    } catch (err) {
      setError(err.message || "Could not load profile");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function setField(key, value) {
    setDraft((prev) => ({ ...prev, [key]: value }));
  }

  function cancelEdit() {
    setDraft(profile);
    setEditing(false);
    setMessage("");
  }

  async function save(e) {
    e.preventDefault();
    if (!draft.name.trim() || !draft.email.trim()) {
      setError("Name and email are required.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      const data = await saveStudentProfile(draft);
      setProfile(data.profile);
      setDraft(data.profile);
      setCertifications(data.certifications);
      setEditing(false);
      setMessage("Profile saved.");
    } catch (err) {
      setError(err.message || "Save failed");
    } finally {
      setSaving(false);
    }
  }

  async function addCert(e) {
    e.preventDefault();
    if (!cert.title.trim()) return;
    setError("");
    try {
      const data = await addStudentCertification(cert);
      setCertifications(data.certifications);
      setCert(EMPTY_CERT);
      setMessage("Certification added.");
    } catch (err) {
      setError(err.message || "Could not add certification");
    }
  }

  async function removeCert(id) {
    setError("");
    try {
      const data = await removeStudentCertification(id);
      setCertifications(data.certifications);
      setMessage("Certification removed.");
    } catch (err) {
      setError(err.message || "Could not remove certification");
    }
  }

  if (loading) {
    return (
      <div>
        <p className="sb-kicker">Profile</p>
        <LoadingCard message="Loading student profile…" />
      </div>
    );
  }

  return (
    <div>
      <p className="sb-kicker">Profile</p>
      <div className="sb-hero">
        <div>
          <h2>{profile.name || "Student profile"}</h2>
          <p className="muted">Academic details used for matching and college visibility.</p>
        </div>
        {!editing ? (
          <button className="btn" type="button" onClick={() => setEditing(true)}>
            Edit profile
          </button>
        ) : (
          <div className="row">
            <button className="btn secondary" type="button" onClick={cancelEdit}>
              Cancel
            </button>
            <button className="btn" type="submit" form="student-profile-form" disabled={saving}>
              {saving ? "Saving…" : "Save"}
            </button>
          </div>
        )}
      </div>

      {error && <AlertBanner type="error" message={error} onClose={() => setError("")} />}
      {message && !error && <AlertBanner type="success" message={message} onClose={() => setMessage("")} />}

      <div className="sb-split">
        <StudentCard title="Academic information">
          {editing ? (
            <form id="student-profile-form" onSubmit={save}>
              <div className="sb-profile-grid">
                {FIELDS.map((field) => (
                  <label key={field.key} className={field.key === "email" || field.key === "university" ? "sb-span-2" : ""}>
                    {field.label}
                    <input
                      type={field.type}
                      value={draft[field.key]}
                      onChange={(e) => setField(field.key, e.target.value)}
                    />
                  </label>
                ))}
              </div>
              <label>
                Career Goal
                <textarea value={draft.careerGoal} onChange={(e) => setField("careerGoal", e.target.value)} />
              </label>
            </form>
          ) : (
            <dl className="sb-profile-view">
              {FIELDS.map((field) => (
                <div key={field.key}>
                  <dt>{field.label}</dt>
                  <dd>{profile[field.key] || "—"}</dd>
                </div>
              ))}
              <div className="sb-span-2">
                <dt>Career Goal</dt>
                <dd>{profile.careerGoal || "—"}</dd>
              </div>
            </dl>
          )}
        </StudentCard>

        <StudentCard title="Certifications">
          {certifications.length === 0 && (
            <div className="sb-empty-inline">
              <p className="muted">No certifications added yet.</p>
            </div>
          )}
          {certifications.map((item) => (
            <div key={item.id} className="sb-item-row">
              <div>
                <strong>{item.title}</strong>
                <div className="muted">
                  {item.issuer} · {item.year}
                </div>
              </div>
              {editing && (
                <button className="btn small secondary" type="button" onClick={() => removeCert(item.id)}>
                  Remove
                </button>
              )}
            </div>
          ))}
          {editing && (
            <form className="sb-cert-form" onSubmit={addCert}>
              <input
                placeholder="Title"
                value={cert.title}
                onChange={(e) => setCert({ ...cert, title: e.target.value })}
              />
              <input
                placeholder="Issuer"
                value={cert.issuer}
                onChange={(e) => setCert({ ...cert, issuer: e.target.value })}
              />
              <input
                placeholder="Year"
                value={cert.year}
                onChange={(e) => setCert({ ...cert, year: e.target.value })}
              />
              <button className="btn small teal" type="submit">
                Add
              </button>
            </form>
          )}
        </StudentCard>
      </div>
    </div>
  );
}

import { useEffect, useState } from "react";
import { AlertBanner, LoadingCard, StudentCard } from "./StudentCards.jsx";
import { addStudentSkill, getStudentSkills, removeStudentSkill } from "./studentApi";

const SUGGESTIONS = ["Python", "SQL", "React", "Machine Learning"];

function SkillChip({ name, onRemove }) {
  return (
    <span className="sb-chip">
      {name}
      {onRemove ? (
        <button
          type="button"
          className="sb-chip-x"
          aria-label={`Remove ${name}`}
          onClick={() => onRemove(name)}
        >
          ×
        </button>
      ) : null}
    </span>
  );
}

export default function StudentSkills() {
  const [skills, setSkills] = useState([]);
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      setSkills(await getStudentSkills());
    } catch (err) {
      setError(err.message || "Could not load skills");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function addSkill(skillName) {
    const clean = (skillName || name).trim();
    if (!clean) return;
    setError("");
    try {
      const next = await addStudentSkill(clean);
      setSkills(next);
      setName("");
      setMessage(`${clean} added.`);
    } catch (err) {
      setError(err.message || "Could not add skill");
    }
  }

  async function onSubmit(e) {
    e.preventDefault();
    await addSkill(name);
  }

  async function onRemove(skillName) {
    setError("");
    try {
      setSkills(await removeStudentSkill(skillName));
      setMessage(`${skillName} removed.`);
    } catch (err) {
      setError(err.message || "Could not remove skill");
    }
  }

  const owned = new Set(skills.map((s) => s.name.toLowerCase()));
  const suggestions = SUGGESTIONS.filter((item) => !owned.has(item.toLowerCase()));

  return (
    <div>
      <p className="sb-kicker">Skills</p>
      <div className="sb-hero">
        <div>
          <h2>Your skills</h2>
          <p className="muted">These chips are matched against opportunity requirements.</p>
        </div>
      </div>

      {error && <AlertBanner type="error" message={error} onClose={() => setError("")} />}
      {message && !error && <AlertBanner type="success" message={message} onClose={() => setMessage("")} />}

      <StudentCard title={`Skills (${skills.length})`}>
        <form className="sb-skill-add" onSubmit={onSubmit}>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Add a skill, e.g. Python"
            aria-label="Skill name"
          />
          <button className="btn" type="submit" disabled={!name.trim()}>
            Add skill
          </button>
        </form>

        {loading ? (
          <LoadingCard message="Loading your skills…" />
        ) : skills.length === 0 ? (
          <div className="sb-empty-inline">
            <p className="muted">No skills yet. Add Python, SQL, React or Machine Learning to start matching.</p>
          </div>
        ) : (
          <div className="sb-chip-row">
            {skills.map((skill) => (
              <SkillChip key={skill.name} name={skill.name} onRemove={onRemove} />
            ))}
          </div>
        )}

        {suggestions.length > 0 && (
          <div className="sb-suggest">
            <p className="muted">Suggested</p>
            <div className="sb-chip-row">
              {suggestions.map((item) => (
                <button key={item} type="button" className="sb-chip sb-chip-ghost" onClick={() => addSkill(item)}>
                  + {item}
                </button>
              ))}
            </div>
          </div>
        )}
      </StudentCard>
    </div>
  );
}

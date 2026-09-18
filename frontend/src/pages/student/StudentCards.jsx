import { Link } from "react-router-dom";

export function StudentCard({ title, action, children, className = "" }) {
  return (
    <section className={`card sb-dash-card ${className}`.trim()}>
      {(title || action) && (
        <header className="sb-dash-card-head">
          {title ? <h3>{title}</h3> : <span />}
          {action}
        </header>
      )}
      {children}
    </section>
  );
}

export function MetricCard({ label, value, hint, percent, to }) {
  const content = (
    <>
      <p className="sb-kicker">{label}</p>
      <div className="percent">{value}</div>
      {hint ? <p className="muted">{hint}</p> : null}
      {typeof percent === "number" ? (
        <div className="sb-bar">
          <span style={{ width: `${Math.max(0, Math.min(100, percent))}%` }} />
        </div>
      ) : null}
    </>
  );

  if (to) {
    return (
      <StudentCard className="sb-dash-metric">
        <Link to={to} className="sb-dash-metric-link">
          {content}
        </Link>
      </StudentCard>
    );
  }

  return <StudentCard className="sb-dash-metric">{content}</StudentCard>;
}

export function ItemRow({ label, value, to }) {
  const inner = (
    <>
      <span>{label}</span>
      <strong>{value}</strong>
    </>
  );

  if (to) {
    return (
      <Link className="sb-item-row" to={to}>
        {inner}
      </Link>
    );
  }

  return <div className="sb-item-row">{inner}</div>;
}

export function LoadingCard({ message = "Loading..." }) {
  return (
    <div className="card sb-loading-state">
      <div className="sb-spinner" aria-hidden="true" />
      <p className="muted" style={{ margin: 0 }}>{message}</p>
    </div>
  );
}

export function EmptyState({ title = "No items found", message, action }) {
  return (
    <div className="card sb-empty-card">
      <h3>{title}</h3>
      {message && <p className="muted">{message}</p>}
      {action && <div style={{ marginTop: 14 }}>{action}</div>}
    </div>
  );
}

export function AlertBanner({ type = "error", message, onRetry, onClose }) {
  if (!message) return null;
  const isError = type === "error";

  return (
    <div className={isError ? "sb-alert-error" : "sb-alert-success"} role="alert">
      <span>{message}</span>
      {onRetry && (
        <button className="btn small secondary" type="button" onClick={onRetry}>
          Retry
        </button>
      )}
      {onClose && (
        <button
          type="button"
          className="sb-alert-close"
          aria-label="Close notification"
          onClick={onClose}
        >
          ×
        </button>
      )}
    </div>
  );
}


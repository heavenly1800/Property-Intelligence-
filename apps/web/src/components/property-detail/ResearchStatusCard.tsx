import type { ResearchResult } from "../../models/research";
import type { Property } from "../../types/property";

type ResearchStatusCardProps = {
  research: ResearchResult | null;
  property: Property;
  loading?: boolean;
  error?: string | null;
  compact?: boolean;
};

export default function ResearchStatusCard({
  research,
  property,
  loading = false,
  error = null,
  compact = false,
}: ResearchStatusCardProps) {
  const providers = research?.providers ?? [];
  const hasPersistedResearch = property.research_quality_score != null;
  const progress = loading ? 0 : research?.progress ?? (hasPersistedResearch ? 100 : 0);
  const completedCount = providers.filter((provider) => provider.status === "completed").length;
  const unavailableCount = providers.filter((provider) => provider.status === "failed" || provider.status === "skipped").length;
  const runState = error
    ? "Error"
    : loading
      ? "Researching"
      : providers.length > 0 && completedCount === providers.length
        ? "Success"
        : providers.length > 0 && completedCount > 0
          ? "Partial success"
          : providers.length > 0
            ? "No provider findings"
            : hasPersistedResearch
              ? "Saved findings"
              : "Not started";

  return (
    <section className="command-card research-status-card">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Due diligence</p>
          <h2>Research Progress</h2>
        </div>
        <strong>{runState} · {progress}%</strong>
      </div>
      <div className="progress-track" aria-label={`Research progress: ${progress}%`}>
        <span style={{ width: `${progress}%` }} />
      </div>
      {error && <p className="media-error" role="alert">{error}</p>}
      {loading ? (
        <p className="research-empty">Checking configured research providers…</p>
      ) : providers.length === 0 ? (
        <p className="research-empty">
          {hasPersistedResearch
            ? "Saved verified findings are shown below. Provider run details are available only for the current run."
            : "Run research to begin provider checks."}
        </p>
      ) : (
        <div className={compact ? "research-list compact" : "research-list"}>
          {providers.map((provider) => (
            <div className="research-row" key={provider.provider}>
              <span className={`status-dot ${provider.status}`} />
              <span>{provider.provider}</span>
              <small>{provider.status}{provider.message ? ` · ${provider.message}` : ""}</small>
            </div>
          ))}
          {unavailableCount > 0 && (
            <p className="research-empty">
              Unavailable or failed providers did not contribute findings.
            </p>
          )}
        </div>
      )}
      {(research?.quality_summary || hasPersistedResearch) && (
        <div className="research-list compact">
          <div className="research-row"><span>Quality score</span><small>{research?.quality_summary?.research_quality_score ?? property.research_quality_score}</small></div>
          <div className="research-row"><span>Risk</span><small>{research?.quality_summary?.research_risk_level ?? property.research_risk_level ?? "unavailable"}</small></div>
          <div className="research-row"><span>Next action</span><small>{research?.quality_summary?.recommended_research_action ?? property.recommended_research_action ?? "unavailable"}</small></div>
        </div>
      )}
    </section>
  );
}

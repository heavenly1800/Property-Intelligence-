import type { ResearchResult } from "../../models/research";

type ResearchStatusCardProps = {
  research: ResearchResult | null;
  compact?: boolean;
};

export default function ResearchStatusCard({
  research,
  compact = false,
}: ResearchStatusCardProps) {
  const providers = research?.providers ?? [];
  const progress = research?.progress ?? 0;

  return (
    <section className="command-card research-status-card">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Due diligence</p>
          <h2>Research Progress</h2>
        </div>
        <strong>{progress}%</strong>
      </div>
      <div className="progress-track" aria-label={`Research progress: ${progress}%`}>
        <span style={{ width: `${progress}%` }} />
      </div>
      {providers.length === 0 ? (
        <p className="research-empty">Run research to begin provider checks.</p>
      ) : (
        <div className={compact ? "research-list compact" : "research-list"}>
          {providers.map((provider) => (
            <div className="research-row" key={provider.provider}>
              <span className={`status-dot ${provider.status}`} />
              <span>{provider.provider}</span>
              <small>{provider.status}</small>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

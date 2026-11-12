import type { WorkflowState } from "../../services/workflowService";
import type { DecisionResult } from "../../models/decision";

interface DecisionPanelProps {
  decision: DecisionResult;
  workflow: WorkflowState;
  loading?: boolean;
  onAction?: () => void;
}

export default function DecisionPanel({
  decision,
  workflow,
  loading = false,
  onAction,
}: DecisionPanelProps) {
  const color =
    workflow.nextAction === "research"
      ? "#2563eb"
      : workflow.nextAction === "buyers"
      ? "#16a34a"
      : workflow.nextAction === "offer"
      ? "#7c3aed"
      : "#374151";

  return (
    <section className="command-card decision-panel">
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: 24,
        }}
      >
        <div>
          <p
            style={{
              color: "#6b7280",
              fontSize: 12,
              textTransform: "uppercase",
              letterSpacing: 1,
              marginBottom: 8,
            }}
          >
            Acquisition Brief
          </p>

          <h2 style={{ margin: 0 }}>
            {decision.decision ?? "REVIEW PROPERTY"}
          </h2>

          <p
            style={{
              marginTop: 8,
              color: "#6b7280",
            }}
          >
            {decision.strategy ?? "Strategy pending"}
          </p>
        </div>

        <div
          style={{
            background: color,
            color: "white",
            padding: "8px 16px",
            borderRadius: 999,
            fontWeight: 600,
          }}
        >
          {workflow.stage.replaceAll("_", " ").toUpperCase()} · {workflow.progress}%
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(2,1fr)",
          gap: 20,
          marginBottom: 24,
        }}
      >
        <Metric
          label="Legacy Decision Score"
          value={decision.score ?? "Not evaluated"}
        />

        <Metric
          label="Evidence Confidence"
          value={decision.confidence == null ? "Insufficient data" : `${decision.confidence}%`}
        />
      </div>

      <Section title="Next Action">
        <p>{workflow.description}</p>

        <p>
          Research: {workflow.researchStatus.replaceAll("_", " ")} · Buyer discovery: {workflow.buyerStatus.replaceAll("_", " ")} · Offer: {workflow.offerStatus.replaceAll("_", " ")}
        </p>

        {workflow.canExecuteAction && onAction && (
          <button
            onClick={onAction}
            disabled={loading}
            className="decision-button"
            style={{
              background: color,
              marginTop: 12,
            }}
          >
            {loading
              ? "Working..."
              : workflow.nextActionLabel}
          </button>
        )}
      </Section>

      <Section title="Persisted Progress">
        <ul>{workflow.completedTasks.map((task) => <li key={task}>{task}</li>)}</ul>
      </Section>

      <Section title="Why This Property?">
        <ul>
          {decision.reasons.map((reason) => (
            <li key={reason}>{reason}</li>
          ))}
        </ul>
      </Section>

      {decision.risks.length > 0 && (
        <Section title="Risks">
          <ul>
            {decision.risks.map((risk) => (
              <li key={risk}>{risk}</li>
            ))}
          </ul>
        </Section>
      )}
    </section>
  );
}

function Metric({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div>
      <p
        style={{
          color: "#6b7280",
          marginBottom: 4,
        }}
      >
        {label}
      </p>

      <h3
        style={{
          margin: 0,
          fontSize: 28,
        }}
      >
        {value}
      </h3>
    </div>
  );
}

function Section({
  title,
  children,
}: React.PropsWithChildren<{
  title: string;
}>) {
  return (
    <div style={{ marginTop: 24 }}>
      <h3>{title}</h3>

      {children}
    </div>
  );
}

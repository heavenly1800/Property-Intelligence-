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
      ? "bg-blue-600"
      : workflow.nextAction === "buyers"
      ? "bg-green-600"
      : workflow.nextAction === "offer"
      ? "bg-purple-600"
      : "bg-gray-700";

  return (
    <section className="command-card decision-panel">
      <div className="decision-heading">
        <div>
          <p className="eyebrow">Decision Engine</p>

          <h2>{decision.nextAction}</h2>
        </div>

        <span
          className={`decision-status ${color}`}
        >
          {workflow.stage.toUpperCase()}
        </span>
      </div>

      <p className="decision-description">{workflow.description}</p>

      <div className="decision-evidence">
        <span>Score {decision.score}</span>
        <span>Confidence {decision.confidence}%</span>
        {decision.reasons.slice(0, 2).map((reason) => <p key={reason}>{reason}</p>)}
        {decision.risks.slice(0, 1).map((risk) => <p className="decision-risk" key={risk}>{risk}</p>)}
      </div>

      {workflow.canExecuteAction && onAction && (
        <button
          onClick={onAction}
          disabled={loading}
          className={`decision-button ${color}`}
        >
          {loading ? "Working..." : workflow.nextActionLabel}
        </button>
      )}
    </section>
  );
}

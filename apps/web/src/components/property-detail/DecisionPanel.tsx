import React from "react";

export type DecisionAction =
  | "research"
  | "buyers"
  | "offer"
  | "complete";

interface DecisionPanelProps {
  action: DecisionAction;
  title: string;
  description: string;
  buttonLabel?: string;
  loading?: boolean;
  onAction?: () => void;
}

export default function DecisionPanel({
  action,
  title,
  description,
  buttonLabel,
  loading = false,
  onAction,
}: DecisionPanelProps) {
  const color =
    action === "research"
      ? "bg-blue-600"
      : action === "buyers"
      ? "bg-green-600"
      : action === "offer"
      ? "bg-purple-600"
      : "bg-gray-700";

  return (
    <section className="rounded-lg border bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-gray-500">
            Decision Engine
          </p>

          <h2 className="mt-1 text-2xl font-semibold">
            {title}
          </h2>
        </div>

        <span
          className={`rounded-full px-3 py-1 text-xs font-semibold text-white ${color}`}
        >
          {action.toUpperCase()}
        </span>
      </div>

      <p className="mb-6 text-gray-600">
        {description}
      </p>

      {buttonLabel && onAction && (
        <button
          onClick={onAction}
          disabled={loading}
          className={`${color} rounded-md px-5 py-2 font-medium text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50`}
        >
          {loading ? "Working..." : buttonLabel}
        </button>
      )}
    </section>
  );
}
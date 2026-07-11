import React from "react";

export interface NextAction {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  variant?: "primary" | "secondary";
  onClick: () => void;
}

interface NextActionsCardProps {
  title?: string;
  actions: NextAction[];
}

export default function NextActionsCard({
  title = "Next Actions",
  actions,
}: NextActionsCardProps) {
  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold">{title}</h2>

      <div className="space-y-3">
        {actions.map((action) => (
          <button
            key={action.id}
            onClick={action.onClick}
            className={`w-full rounded-lg border p-4 text-left transition hover:shadow ${
              action.variant === "primary"
                ? "bg-blue-600 text-white border-blue-600"
                : "bg-white hover:bg-gray-50"
            }`}
          >
            <div className="flex items-start gap-3">
              <div className="text-xl">{action.icon}</div>

              <div>
                <h3 className="font-medium">{action.title}</h3>

                <p
                  className={`text-sm ${
                    action.variant === "primary"
                      ? "text-blue-100"
                      : "text-gray-500"
                  }`}
                >
                  {action.description}
                </p>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
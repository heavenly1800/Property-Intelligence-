import type { DecisionResult } from "../models/decision";
import type { Property } from "../types/property";

export type WorkflowStage = "research" | "buyers" | "offer" | "complete";
export type WorkflowAction = "research" | "buyers" | "offer" | "complete";

export type WorkflowState = {
  stage: WorkflowStage;
  progress: number;
  nextAction: WorkflowAction;
  nextActionLabel: string;
  title: string;
  description: string;
  completedTasks: string[];
  canExecuteAction: boolean;
};

export type BackendWorkflow = Partial<WorkflowState> & {
  stage?: WorkflowStage;
  next_action?: WorkflowAction;
  completed_tasks?: string[];
};

type WorkflowInput = {
  property: Property;
  decision: DecisionResult | null;
  researchCompleted?: boolean;
  buyersFound?: boolean;
};

const workflowDefinitions: Record<WorkflowStage, Omit<WorkflowState, "description">> = {
  research: {
    stage: "research", progress: 25, nextAction: "research", nextActionLabel: "Run research",
    title: "Complete property research", completedTasks: ["Property intake"], canExecuteAction: true,
  },
  buyers: {
    stage: "buyers", progress: 50, nextAction: "buyers", nextActionLabel: "Find buyers",
    title: "Identify qualified buyers", completedTasks: ["Property intake", "Property research"], canExecuteAction: true,
  },
  offer: {
    stage: "offer", progress: 75, nextAction: "offer", nextActionLabel: "Generate offer",
    title: "Prepare offer recommendation", completedTasks: ["Property intake", "Property research", "Buyer discovery"], canExecuteAction: false,
  },
  complete: {
    stage: "complete", progress: 100, nextAction: "complete", nextActionLabel: "Workflow complete",
    title: "Deal workflow complete", completedTasks: ["Property intake", "Property research", "Buyer discovery", "Offer recommendation"], canExecuteAction: false,
  },
};

function getFallbackStage(input: WorkflowInput): WorkflowStage {
  if (input.property.offer_amount != null) return "complete";
  if (input.buyersFound || (input.property.buyer_count ?? 0) > 0) return "offer";
  const researchComplete = input.researchCompleted
    ?? input.property.research_completed
    ?? (input.property.latitude != null && input.property.longitude != null);
  return researchComplete ? "buyers" : "research";
}

/**
 * Normalizes workflow data for the UI. A persisted backend workflow payload
 * takes precedence; the fallback is deliberately isolated for replacement by
 * a future workflow endpoint.
 */
export function getWorkflowState(input: WorkflowInput): WorkflowState {
  const backend = input.property.workflow;
  const stage = backend?.stage ?? getFallbackStage(input);
  const definition = workflowDefinitions[stage];
  const action = backend?.next_action ?? backend?.nextAction ?? definition.nextAction;

  return {
    ...definition,
    ...backend,
    stage,
    nextAction: action,
    nextActionLabel: backend?.nextActionLabel ?? definition.nextActionLabel,
    completedTasks: backend?.completed_tasks ?? backend?.completedTasks ?? definition.completedTasks,
    description: input.decision?.reasons[0]
      ?? input.decision?.nextAction
      ?? input.property.next_action
      ?? "Complete the recommended acquisition step to advance this deal.",
  };
}

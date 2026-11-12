import { api } from "../lib/api";
import type { DecisionResult } from "../models/decision";

type DecisionResponse = {
  score: number | null;
  confidence: number | null;
  evaluation_status: "not_evaluated" | "evaluated";
  reasons: string[];
  risks: string[];
  next_action: string;
}

function toDecisionResult(response: DecisionResponse): DecisionResult {
  return {
    score: response.score,
    confidence: response.confidence,
    evaluationStatus: response.evaluation_status,
    reasons: response.reasons,
    risks: response.risks,
    nextAction: response.next_action,
  };
}

/** API adapter for the current rule evaluator and future AI evaluator. */
export async function getDecision(propertyId: string): Promise<DecisionResult> {
  return toDecisionResult(await api.get<DecisionResponse>(`/decision/${propertyId}`));
}

/**
 * Stable decision contract consumed by the UI. The producing evaluator may be
 * rule-based today and AI-backed later without changing consumers.
 */
export type DecisionResult = {
  score: number;
  confidence: number;
  reasons: string[];
  risks: string[];
  nextAction: string;
};

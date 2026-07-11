import { api } from "../lib/api";

export interface DecisionResult {
  score: number;
  confidence: number;
  reasons: string[];
  risks: string[];
  next_action: string;
}

export function getDecision(propertyId: string) {
  return api<DecisionResult>(
    `/decision/${propertyId}`
  );
}
/**
 * Stable decision contract consumed by the UI.
 *
 * The producing evaluator may evolve from
 * rule-based to AI-assisted without requiring
 * changes to the frontend.
 */
export type DecisionResult = {
  /**
   * Opportunity score from 0–100.
   */
  score: number;

  /**
   * Confidence in the recommendation.
   */
  confidence: number;

  /**
   * BUY
   * REVIEW
   * PASS
   */
  decision?: string;

  /**
   * Recommended acquisition strategy.
   */
  strategy?: string;

  /**
   * Recommended next action.
   */
  nextAction: string;

  /**
   * Future Offer Intelligence.
   */
  estimatedOffer?: number;

  /**
   * Future Offer Intelligence.
   */
  estimatedAssignment?: number;

  /**
   * Positive signals.
   */
  reasons: string[];

  /**
   * Potential risks.
   */
  risks: string[];
};

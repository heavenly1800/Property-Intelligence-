import { useEffect, useMemo, useState } from "react";

import type { Property } from "../../types/property";
import {
  getBuyers,
  type BuyerMatch,
  type BuyerMatchResult,
} from "../../services/buyerService";
import { getDecision } from "../../services/decisionService";
import type { DecisionResult } from "../../models/decision";
import { runResearch } from "../../services/researchService";
import type { ResearchResult } from "../../models/research";
import { ApiError } from "../../lib/api";
import { getOfferHistory } from "../../services/offerAnalysisService";
import { getSentOffers } from "../../services/crmService";
import type { OfferAnalysis } from "../../types/offerAnalysis";
import type { SentOffer } from "../../types/crm";
import {
  getWorkflowState,
  type BuyerDiscoveryStatus,
  type WorkflowAction,
  type WorkflowState,
} from "../../services/workflowService";

type UseWorkflowOptions = {
  property: Property | null;
  refreshProperty: () => Promise<void>;
};

export function useWorkflow({
  property,
  refreshProperty,
}: UseWorkflowOptions) {
  const [decision, setDecision] =
    useState<DecisionResult | null>(null);

  const [research, setResearch] =
    useState<ResearchResult | null>(null);

  const [buyers, setBuyers] =
    useState<BuyerMatch[]>([]);

  const [buyerResult, setBuyerResult] =
    useState<BuyerMatchResult | null>(null);

  const [buyerStatus, setBuyerStatus] =
    useState<BuyerDiscoveryStatus>("not_searched");

  const [buyerError, setBuyerError] =
    useState<string | null>(null);

  const [offerAnalyses, setOfferAnalyses] =
    useState<OfferAnalysis[] | null>(null);

  const [sentOffers, setSentOffers] =
    useState<SentOffer[] | null>(null);

  const [executingAction, setExecutingAction] =
    useState<WorkflowAction | null>(null);

  const [researchError, setResearchError] =
    useState<string | null>(null);

  useEffect(() => {
    if (!property) return;

    getDecision(property.property_id)
      .then(setDecision)
      .catch(console.error);
  }, [property]);

  async function refreshWorkflowActivity(propertyId = property?.property_id) {
    if (!propertyId) return;
    const [offers, sent] = await Promise.all([
      getOfferHistory(propertyId).catch(() => null),
      getSentOffers(propertyId).catch(() => null),
    ]);
    setOfferAnalyses(offers);
    setSentOffers(sent);
  }

  useEffect(() => {
    if (!property) return;
    setBuyerResult(null);
    setBuyers([]);
    setBuyerStatus("not_searched");
    setBuyerError(null);
    void refreshWorkflowActivity(property.property_id);
  }, [property?.property_id]);

  const workflow = useMemo<WorkflowState | null>(() => {
    if (!property) return null;

    return getWorkflowState({
      property,
      decision,
      buyerStatus,
      offerAnalyses,
      sentOffers,
    });
  }, [property, decision, buyerStatus, offerAnalyses, sentOffers]);

  async function executeAction(
    action: WorkflowAction
  ) {
    if (
      !property ||
      action === "offer" ||
      action === "none"
    ) {
      return;
    }

    setExecutingAction(action);

    try {
      if (action === "research") {
        setResearchError(null);
        const result = await runResearch(property.property_id);
        setResearch(result);

        await refreshProperty();
      }

      if (action === "buyers") {
        setBuyerError(null);
        setBuyerResult(null);
        setBuyers([]);
        const result = await getBuyers(
          property.property_id
        );

        setBuyerResult(result);
        setBuyers(result.buyers);
        setBuyerStatus(result.status);
      }
    } catch (error) {
      console.error(error);

      if (action === "research") {
        setResearchError(
          error instanceof ApiError
            ? error.message
            : "Research could not be completed. Try again."
        );
      }

      if (action === "buyers") {
        setBuyerStatus("failed");
        setBuyerError(
          error instanceof ApiError
            ? error.message
            : "Buyer discovery failed. Try again."
        );
      }
    } finally {
      setExecutingAction(null);
    }
  }

  return {
    workflow,
    decision,
    research,
    buyers,
    buyerResult,
    buyerStatus,
    buyerError,
    researchError,
    isResearching: executingAction === "research",
    isFindingBuyers: executingAction === "buyers",
    isExecuting: executingAction !== null,
    executeNextAction: () =>
      workflow &&
      executeAction(workflow.nextAction),
    runResearch: () =>
      executeAction("research"),
    findBuyers: () =>
      executeAction("buyers"),
    refreshWorkflowActivity,
  };
}

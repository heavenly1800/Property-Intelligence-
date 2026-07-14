import { useEffect, useMemo, useState } from "react";

import type { Property } from "../../types/property";
import {
  getBuyers,
  type BuyerMatch,
} from "../../services/buyerService";
import { getDecision } from "../../services/decisionService";
import type { DecisionResult } from "../../models/decision";
import { runResearch } from "../../services/researchService";
import type { ResearchResult } from "../../models/research";
import {
  getWorkflowState,
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

  const [isExecuting, setIsExecuting] =
    useState(false);

  useEffect(() => {
    if (!property) return;

    getDecision(property.property_id)
      .then(setDecision)
      .catch(console.error);
  }, [property]);

  const workflow = useMemo<WorkflowState | null>(() => {
    if (!property) return null;

    return getWorkflowState({
      property,
      decision,
      researchCompleted: research?.completed,
      buyersFound: buyers.length > 0,
    });
  }, [property, decision, research, buyers]);

  async function executeAction(
    action: WorkflowAction
  ) {
    if (
      !property ||
      action === "offer" ||
      action === "complete"
    ) {
      return;
    }

    setIsExecuting(true);

    try {
      if (action === "research") {
        setResearch(
          await runResearch(property.property_id)
        );

        await refreshProperty();
      }

      if (action === "buyers") {
        const result = await getBuyers(
          property.property_id
        );

        setBuyers(result.buyers);
      }
    } catch (error) {
      console.error(error);

      alert(
        `Unable to ${
          action === "research"
            ? "run research"
            : "find buyers"
        }.`
      );
    } finally {
      setIsExecuting(false);
    }
  }

  return {
    workflow,
    decision,
    research,
    buyers,
    isExecuting,
    executeNextAction: () =>
      workflow &&
      executeAction(workflow.nextAction),
    runResearch: () =>
      executeAction("research"),
    findBuyers: () =>
      executeAction("buyers"),
  };
}
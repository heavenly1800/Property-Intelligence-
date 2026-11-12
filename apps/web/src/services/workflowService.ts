import type { DecisionResult } from "../models/decision";
import type { SentOffer } from "../types/crm";
import type { OfferAnalysis } from "../types/offerAnalysis";
import type { Property } from "../types/property";

export type WorkflowStage = "research" | "buyers" | "offer" | "offer_sent";
export type WorkflowAction = "research" | "buyers" | "offer" | "none";
export type ResearchWorkflowStatus = "not_started" | "partial" | "complete";
export type BuyerDiscoveryStatus =
  | "not_searched"
  | "no_verified_buyers"
  | "verified_buyers_found"
  | "failed";
export type OfferWorkflowStatus = "unknown" | "not_created" | "blocked" | "prepared" | "sent";

export type WorkflowState = {
  stage: WorkflowStage;
  progress: number;
  nextAction: WorkflowAction;
  nextActionLabel: string;
  title: string;
  description: string;
  completedTasks: string[];
  canExecuteAction: boolean;
  researchStatus: ResearchWorkflowStatus;
  buyerStatus: BuyerDiscoveryStatus;
  offerStatus: OfferWorkflowStatus;
};

export type BackendWorkflow = {
  stage?: WorkflowStage;
  next_action?: WorkflowAction;
  completed_tasks?: string[];
};

type WorkflowInput = {
  property: Property;
  decision: DecisionResult | null;
  buyerStatus: BuyerDiscoveryStatus;
  offerAnalyses: OfferAnalysis[] | null;
  sentOffers: SentOffer[] | null;
};

function researchStatus(property: Property): ResearchWorkflowStatus {
  if (property.research_quality_score == null) return "not_started";
  return property.missing_research_items?.length ? "partial" : "complete";
}

function offerStatus(
  analyses: OfferAnalysis[] | null,
  sentOffers: SentOffer[] | null,
): OfferWorkflowStatus {
  if (sentOffers?.length) return "sent";
  if (analyses === null || sentOffers === null) return "unknown";
  if (analyses.some((offer) => offer.recommended_offer != null && ["calculated", "manual"].includes(offer.offer_status))) return "prepared";
  if (analyses.some((offer) => offer.offer_status === "blocked")) return "blocked";
  return "not_created";
}

export function getWorkflowState(input: WorkflowInput): WorkflowState {
  const research = researchStatus(input.property);
  const offer = offerStatus(input.offerAnalyses, input.sentOffers);
  const buyer = input.buyerStatus;
  const completedTasks = ["Property intake"];

  if (research === "complete") completedTasks.push("Property research complete");
  if (research === "partial") completedTasks.push("Partial property research saved");
  if (buyer === "verified_buyers_found") completedTasks.push("Verified buyers found");
  if (buyer === "no_verified_buyers") completedTasks.push("Buyer search completed: no verified buyers");
  if (offer === "prepared" || offer === "sent") completedTasks.push("Offer analysis prepared");
  if (offer === "sent") completedTasks.push("Offer recorded as sent");

  if (offer === "sent") {
    return state("offer_sent", 100, "none", "Offer recorded as sent", "Offer activity is persisted in sent-offer history.", false);
  }
  if (offer === "prepared") {
    return state("offer", 75, "offer", "Review offer", "A persisted offer analysis is ready for review or sent-offer recording.", true);
  }
  if (offer === "blocked") {
    return state("offer", 50, "offer", "Review blocked offer", "Offer analysis is persisted but blocked by missing or insufficient evidence.", true);
  }
  if (buyer === "verified_buyers_found") {
    return state("buyers", 50, "offer", "Prepare offer", "Verified buyers were found in this session; no persisted offer exists yet.", true);
  }
  if (buyer === "no_verified_buyers") {
    return state("buyers", 50, "buyers", "Search buyers again", "The latest search found no verified buyers. This search result is not persisted.", true);
  }
  if (buyer === "failed") {
    return state("buyers", research === "not_started" ? 25 : 50, "buyers", "Retry buyer search", "Buyer discovery failed; no completion was recorded.", true);
  }
  if (research !== "not_started") {
    return state("buyers", research === "complete" ? 50 : 25, "buyers", "Find verified buyers", "Research findings are persisted. Buyer search history is unavailable after refresh.", true);
  }
  return state("research", 25, "research", "Run research", input.decision?.nextAction ?? "No persisted research findings are available.", true);

  function state(
    stage: WorkflowStage,
    progress: number,
    nextAction: WorkflowAction,
    title: string,
    description: string,
    canExecuteAction: boolean,
  ): WorkflowState {
    return {
      stage,
      progress,
      nextAction,
      nextActionLabel: title,
      title,
      description,
      completedTasks,
      canExecuteAction,
      researchStatus: research,
      buyerStatus: buyer,
      offerStatus: offer,
    };
  }
}

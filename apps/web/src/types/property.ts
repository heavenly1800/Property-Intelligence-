import type { BackendWorkflow } from "../services/workflowService";

export type WorkflowStage =
  | "NEW_LEAD"
  | "RESEARCH"
  | "READY_TO_OFFER"
  | "OFFER_SENT"
  | "NEGOTIATING"
  | "UNDER_CONTRACT"
  | "MARKETING"
  | "SOLD"
  | "ARCHIVED";

export type Property = {
  property_id: string;

  address: string;

  city?: string;
  county?: string;
  state?: string;
  zip_code?: string;

  property_type?: string;

  // Opportunity Engine
  opportunity_score?: number;
  confidence?: number;
  strategy?: string;
  next_action?: string;

  // Research Engine
  apn?: string;
  acres?: number;
  square_feet?: number;
  zoning?: string;
  owner_name?: string;
  latitude?: number;
  longitude?: number;
  census_tract?: string;
  block_group?: string;

  research_completed?: boolean;
  buyer_count?: number;
  offer_amount?: number;
  workflow?: BackendWorkflow;
  workflow_stage?: WorkflowStage;
};
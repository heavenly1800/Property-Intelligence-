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
  flood_zone?: string;
  flood_zone_subtype?: string;
  special_flood_hazard_area?: boolean;
  flood_risk_level?: string;
  flood_source?: string;
  parcel_acres?: number;
  jurisdiction?: string;
  land_use?: string;
  parcel_source?: string;
  owner_mailing_address?: string;
  assessed_land_value?: number;
  assessed_improvement_value?: number;
  assessed_total_value?: number;
  tax_year?: number;
  tax_status?: string;
  last_transfer_date?: string;
  last_transfer_price?: number;
  assessor_source?: string;

  research_completed?: boolean;
  buyer_count?: number;
  offer_amount?: number;
  workflow?: BackendWorkflow;
  workflow_stage?: WorkflowStage;
};

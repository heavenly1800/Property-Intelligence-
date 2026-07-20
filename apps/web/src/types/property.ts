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
  electric_provider?: string;
  electric_service_evidence?: string;
  gas_provider?: string;
  gas_service_evidence?: string;
  water_provider?: string;
  water_service_evidence?: string;
  sewer_provider?: string;
  sewer_service_evidence?: string;
  broadband_summary?: string;
  broadband_evidence?: string;
  utilities_source?: string;
  research_quality_score?: number;
  parcel_certainty?: "high" | "medium" | "low";
  assessment_coverage?: "complete" | "partial" | "missing";
  utility_confidence?: "high" | "medium" | "low";
  research_risk_level?: "low" | "medium" | "high";
  missing_research_items?: string[];
  recommended_research_action?: string;
  listing_url?: string;
  listing_source?: string;
  asking_price?: number;
  unit_count?: number;
  property_subtype?: string;
  year_built?: number;
  bedrooms?: number;
  bathrooms?: number;
  current_monthly_rent?: number;
  current_monthly_rent_per_unit?: number;
  current_annual_rent?: number;
  occupancy_status?: string;
  property_condition?: string;
  rent_ready?: boolean;
  financial_data_source?: string;
  estimated_market_value?: number;
  after_repair_value?: number;
  expected_operating_expense_percentage?: number;
  estimated_monthly_rent?: number;
  estimated_monthly_rent_per_unit?: number;
  estimated_annual_rent?: number;
  estimated_operating_expenses_monthly?: number;
  estimated_operating_expenses_annual?: number;
  estimated_noi_annual?: number;
  estimated_cap_rate?: number;
  estimated_monthly_cash_flow?: number;
  gross_rent_multiplier?: number;
  financial_analysis_confidence?: string;
  rehab_needed?: boolean;
  rehab_scope_summary?: string;
  rehab_items?: string[];
  estimated_rehab_cost_low?: number;
  estimated_rehab_cost_high?: number;
  estimated_after_repair_value_low?: number;
  estimated_after_repair_value_high?: number;
  estimated_flip_profit_low?: number;
  estimated_flip_profit_high?: number;
  estimated_post_rehab_monthly_rent?: number;
  estimated_post_rehab_annual_rent?: number;
  financial_missing_items?: string[];
  recommended_financial_action?: string;
  listing_raw_text?: string;
  listing_summary?: string;
  listing_highlights?: string[];
  listing_risks?: string[];
  listing_missing_items?: string[];
  listing_last_analyzed_at?: string;
  listing_analysis_status?: string;

  research_completed?: boolean;
  buyer_count?: number;
  offer_amount?: number;
  workflow?: BackendWorkflow;
  workflow_stage?: WorkflowStage;
  crm_assigned_to?: string;
  next_follow_up?: string;
  has_overdue?: boolean;
  primary_seller_name?: string;
};

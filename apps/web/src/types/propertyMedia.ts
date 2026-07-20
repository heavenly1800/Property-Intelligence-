export type PropertyMedia = {
  media_id: string;
  property_id: string;
  storage_path: string;
  public_url?: string;
  original_filename: string;
  media_type: string;
  caption?: string;
  room_category?: string;
  source_type: string;
  source_url?: string;
  is_primary: boolean;
  sort_order: number;
  uploaded_at: string;
  analysis_status: string;
};

export type PropertyMediaUpdate = Pick<PropertyMedia, "caption" | "room_category" | "source_url" | "sort_order">;

export type ObservedPhotoIssue = {
  category: string; description: string; severity: string; visible_evidence: string;
  recommended_action: string; confidence: number; area?: string; supporting_media_ids?: string[];
};

export type InferredPhotoIssue = {
  category: string; description: string; basis: string; recommended_inspection: string; confidence: number;
};

export type InspectionItem = { category: string; description: string; reason: string; supporting_media_ids?: string[] };
export type RepairItem = {
  category: string; description: string; area: string; scope_units?: number;
  estimated_quantity_low?: number; estimated_quantity_high?: number; quantity_unit?: string; quantity_confidence: number;
  unit_cost_low: number; unit_cost_high: number; extended_cost_low: number; extended_cost_high: number;
  estimated_cost_low: number; estimated_cost_high: number; assumption_notes?: string; cost_confidence: number;
  regional_profile_id: string; regional_profile_name: string; minimum_job_cost_applied: boolean; supporting_media_ids?: string[];
};

export type PropertyMediaAnalysis = {
  analysis_id: string; media_id: string; room_or_area: string; visible_condition_summary: string;
  condition_rating: "excellent" | "good" | "fair" | "poor" | "severe" | "unknown";
  observed_issues: ObservedPhotoIssue[]; inferred_issues: InferredPhotoIssue[];
  unknown_inspection_items: InspectionItem[]; estimated_repair_items: RepairItem[];
  estimated_repair_cost_low: number; estimated_repair_cost_high: number;
  rent_ready_status: "ready" | "minor_work" | "substantial_work" | "unknown";
  safety_concerns: string[]; analysis_confidence: number; limitations: string[];
  model_name: string; analyzed_at: string; prompt_version: string; cost_assumption_version: string;
  visible_repair_subtotal_low: number; visible_repair_subtotal_high: number; contingency_low: number; contingency_high: number;
  regional_profile_id: string; regional_profile_name: string; profile_match_confidence: number; profile_match_reason: string;
  cost_assumption_effective_date: string; cost_limitations: string[];
  review_status: string; error_message?: string;
};

export type PropertyConditionSummary = {
  property_id: string; overall_visible_condition: string; overall_rent_ready_status: string;
  visible_repair_scope_summary?: string; estimated_visible_repair_cost_low: number;
  estimated_visible_repair_cost_high: number; major_observed_issues: ObservedPhotoIssue[];
  required_inspection_items: InspectionItem[]; analyzed_photo_count: number;
  analysis_confidence: number; last_analyzed_at: string; cost_assumption_version: string; review_status: string;
  visible_repair_items: RepairItem[]; visible_repair_subtotal_low: number; visible_repair_subtotal_high: number;
  contingency_low: number; contingency_high: number; regional_profile_id: string; regional_profile_name: string;
  profile_match_confidence: number; profile_match_reason: string; cost_assumption_effective_date: string; cost_limitations: string[];
};

export type AnalyzeAllResult = { results: { media_id: string; status: string; error?: string }[]; summary?: PropertyConditionSummary; completed: number; failed: number };

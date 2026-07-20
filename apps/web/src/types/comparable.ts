export type ComparableType = "sale" | "rental";
export type PropertyComparable = {
  comparable_id: string; subject_property_id: string; comparable_type: ComparableType;
  source_name: string; source_url: string; source_record_id?: string; address: string;
  latitude?: number; longitude?: number; distance_miles?: number; property_type: string; property_subtype?: string;
  unit_count?: number; bedrooms?: number; bathrooms?: number; square_feet?: number; lot_acres?: number; year_built?: number;
  condition?: string; sale_price?: number; sale_date?: string; monthly_rent?: number; listing_date?: string; status?: string;
  price_per_square_foot?: number; price_per_unit?: number; rent_per_unit?: number; rent_per_square_foot?: number;
  match_score?: number; score_components?: Record<string, number>; included: boolean; exclusion_reason?: string; notes?: string;
  created_at: string; updated_at: string;
};
export type ComparableInput = Omit<PropertyComparable, "comparable_id" | "subject_property_id" | "price_per_square_foot" | "price_per_unit" | "rent_per_unit" | "rent_per_square_foot" | "match_score" | "score_components" | "exclusion_reason" | "created_at" | "updated_at">;
export type ComparableAnalysis = {
  property_id: string; current_market_value_low?: number; current_market_value_high?: number; estimated_market_value?: number;
  after_repair_value_low?: number; after_repair_value_high?: number; estimated_after_repair_value?: number;
  estimated_monthly_market_rent_low?: number; estimated_monthly_market_rent_high?: number; estimated_monthly_market_rent?: number;
  estimated_annual_market_rent?: number; sale_comparable_count: number; rental_comparable_count: number;
  average_sale_distance?: number; average_rental_distance?: number; comparable_analysis_confidence: number;
  comparable_analysis_status: string; comparable_missing_items: string[]; comparable_limitations: string[];
  recommended_comparable_action: string; analyzed_at: string;
};

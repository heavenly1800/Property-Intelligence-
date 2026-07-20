export type StrategyName = "wholesale" | "wholetail" | "flip" | "rental_hold";
export type StrategyResult = {
  strategy_result_id?: string; strategy: StrategyName; viable: boolean; rank?: number; score: number; confidence: number;
  acquisition_price_used?: number; value_basis?: string; value_low?: number; value_high?: number;
  rehab_cost_low?: number; rehab_cost_high?: number; holding_costs?: number; closing_costs?: number; selling_costs?: number;
  projected_revenue_low?: number; projected_revenue_high?: number; projected_profit_low?: number; projected_profit_high?: number;
  projected_return_percentage_low?: number; projected_return_percentage_high?: number; monthly_cash_flow?: number; annual_cash_flow?: number; cap_rate?: number;
  major_risks: string[]; strengths: string[]; missing_inputs: string[]; formula_notes: string[];
};
export type StrategyAnalysis = {
  strategy_analysis_id: string; property_id: string; recommended_strategy?: StrategyName; recommendation_confidence: number;
  analysis_status: string; analyzed_at: string; assumptions_version: string; missing_inputs: string[]; limitations: string[];
  recommended_next_action: string; input_snapshot: Record<string, unknown>; results: StrategyResult[];
};

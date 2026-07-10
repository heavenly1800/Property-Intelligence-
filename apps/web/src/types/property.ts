export type Property = {
  property_id: string;
  address: string;
  city: string;
  county: string;
  state: string;
  zip_code: string;
  property_type: string;

  opportunity_score?: number;
  confidence?: number;
  strategy?: string;
  next_action?: string;
};
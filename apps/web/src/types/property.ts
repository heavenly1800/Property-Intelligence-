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
};
export type ResearchProviderStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "skipped";

export type ResearchProviderResult = {
  provider: string;
  status: ResearchProviderStatus;
  data: Record<string, unknown>;
  message: string | null;
  confidence: number;
};

export type ResearchResult = {
  providers: ResearchProviderResult[];
  completed_providers: string[];
  failed_providers: string[];
  progress: number;
  completed: boolean;
  confidence: number;
  quality_summary: {
    research_quality_score: number;
    parcel_certainty: string;
    assessment_coverage: string;
    utility_confidence: string;
    research_risk_level: string;
    missing_research_items: string[];
    recommended_research_action: string;
  } | null;
};

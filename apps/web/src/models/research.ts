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
};

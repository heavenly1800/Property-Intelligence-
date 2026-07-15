export type ShareIntakeStatus = "pending" | "processing" | "completed" | "needs_input" | "error";

export type ShareIntakeCreate = {
  source_url?: string;
  shared_text?: string;
  title?: string;
  notes?: string;
};

export type ShareIntake = ShareIntakeCreate & {
  share_id: string;
  source_domain?: string;
  status: ShareIntakeStatus;
  detected_address?: string;
  matched_property_id?: string;
  created_property_id?: string;
  created_at: string;
  processed_at?: string;
  error_message?: string;
};

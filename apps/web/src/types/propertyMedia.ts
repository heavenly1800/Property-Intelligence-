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

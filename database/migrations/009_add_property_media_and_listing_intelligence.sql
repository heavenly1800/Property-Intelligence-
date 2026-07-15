create table if not exists property_media (
    media_id uuid primary key, property_id text not null references properties(property_id) on delete cascade,
    storage_path text not null, public_url text, original_filename text not null, media_type text not null,
    caption text, room_category text, source_type text not null, source_url text, is_primary boolean not null default false,
    sort_order integer not null default 0, uploaded_at timestamptz not null default now(), analysis_status text not null default 'pending'
);
create table if not exists property_media_analysis (
    analysis_id uuid primary key default gen_random_uuid(), media_id uuid not null references property_media(media_id) on delete cascade,
    visible_condition_summary text, observed_issues jsonb, inferred_issues jsonb, unknown_inspection_items jsonb,
    estimated_repair_items jsonb, estimated_repair_cost_low numeric, estimated_repair_cost_high numeric,
    analysis_confidence numeric, model_name text, analyzed_at timestamptz, prompt_version text, raw_analysis jsonb, review_status text not null default 'pending_review'
);
alter table properties
    add column if not exists listing_raw_text text,
    add column if not exists listing_summary text,
    add column if not exists listing_highlights jsonb,
    add column if not exists listing_risks jsonb,
    add column if not exists listing_missing_items jsonb,
    add column if not exists listing_last_analyzed_at timestamptz,
    add column if not exists listing_analysis_status text;
create index if not exists property_media_property_sort_idx on property_media(property_id, sort_order);

alter table property_media_analysis
    add column if not exists room_or_area text,
    add column if not exists condition_rating text,
    add column if not exists rent_ready_status text,
    add column if not exists safety_concerns jsonb,
    add column if not exists limitations jsonb,
    add column if not exists cost_assumption_version text,
    add column if not exists error_message text;

create unique index if not exists property_media_analysis_media_id_idx
    on property_media_analysis(media_id);

create table if not exists property_condition_analysis (
    property_id text primary key references properties(property_id) on delete cascade,
    overall_visible_condition text not null,
    overall_rent_ready_status text not null,
    visible_repair_scope_summary text,
    estimated_visible_repair_cost_low numeric not null default 0,
    estimated_visible_repair_cost_high numeric not null default 0,
    major_observed_issues jsonb not null default '[]'::jsonb,
    required_inspection_items jsonb not null default '[]'::jsonb,
    analyzed_photo_count integer not null default 0,
    analysis_confidence numeric not null default 0,
    last_analyzed_at timestamptz not null default now(),
    cost_assumption_version text not null,
    review_status text not null default 'pending_review'
);

create index if not exists property_media_analysis_analyzed_at_idx
    on property_media_analysis(analyzed_at desc);

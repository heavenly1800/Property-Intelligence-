create table if not exists property_offer_analysis (
    offer_analysis_id uuid primary key default gen_random_uuid(),
    property_id text not null references properties(property_id) on delete cascade,
    selected_strategy text not null check (selected_strategy in ('wholesale','wholetail','flip','rental_hold','custom')),
    offer_status text not null, recommended_offer_low numeric, recommended_offer numeric,
    recommended_offer_high numeric, maximum_allowable_offer numeric, seller_asking_price numeric,
    estimated_discount_to_asking numeric, offer_confidence numeric not null check (offer_confidence between 0 and 1),
    value_basis text, rehab_basis text, rent_basis text, assumptions_version text not null,
    input_snapshot jsonb not null, blockers jsonb not null default '[]'::jsonb,
    warnings jsonb not null default '[]'::jsonb, missing_inputs jsonb not null default '[]'::jsonb,
    limitations jsonb not null default '[]'::jsonb, formula_notes jsonb not null default '[]'::jsonb,
    projected_metric_label text, projected_metric_low numeric, projected_metric_high numeric,
    manual_target_margin numeric, manual_notes text, created_at timestamptz not null default now()
);
create index if not exists property_offer_analysis_history_idx on property_offer_analysis(property_id, created_at desc);

create table if not exists share_intake (
    share_id uuid primary key default gen_random_uuid(),
    source_url text,
    source_domain text,
    shared_text text,
    title text,
    notes text,
    status text not null default 'pending',
    detected_address text,
    matched_property_id text references properties(property_id) on delete set null,
    created_property_id text references properties(property_id) on delete set null,
    created_at timestamptz not null default now(),
    processed_at timestamptz,
    error_message text,
    constraint share_intake_status_check
        check (status in ('pending', 'processing', 'completed', 'needs_input', 'error'))
);

create index if not exists share_intake_created_at_idx
    on share_intake(created_at desc);

create index if not exists share_intake_property_idx
    on share_intake(matched_property_id, created_property_id);

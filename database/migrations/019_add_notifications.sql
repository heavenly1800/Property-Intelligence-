create table if not exists property_notifications (
 notification_id uuid primary key default gen_random_uuid(),
 property_id text not null references properties(property_id) on delete cascade,
 notification_type text not null check (notification_type in ('overdue_follow_up','follow_up_due_today','follow_up_due_soon','deadline_overdue','deadline_due_today','deadline_due_soon','offer_expiring','seller_contact_needed','stale_lead','under_contract_deadline_risk','custom')),
 severity text not null check (severity in ('info','warning','high','critical')),
 title text not null, message text not null, related_entity_type text, related_entity_id text,
 scheduled_for timestamptz, triggered_at timestamptz not null default now(), read_at timestamptz,
 dismissed_at timestamptz, status text not null default 'unread' check (status in ('unread','read','dismissed','resolved')),
 dedupe_key text not null unique, metadata jsonb not null default '{}'::jsonb,
 created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create index if not exists idx_notifications_status on property_notifications(status, severity, scheduled_for);
create index if not exists idx_notifications_property on property_notifications(property_id, status, triggered_at desc);

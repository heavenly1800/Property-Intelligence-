alter table properties add column if not exists workflow_stage text not null default 'NEW_LEAD';
alter table properties add column if not exists crm_assigned_to text;
alter table properties drop constraint if exists properties_workflow_stage_check;
alter table properties add constraint properties_workflow_stage_check check (workflow_stage in ('NEW_LEAD','RESEARCH','READY_TO_OFFER','OFFER_SENT','NEGOTIATING','UNDER_CONTRACT','MARKETING','SOLD','ARCHIVED'));

create table if not exists property_contacts (
 contact_id uuid primary key default gen_random_uuid(), property_id text not null references properties(property_id) on delete cascade,
 first_name text, last_name text, company_name text, role text, phone text, email text, mailing_address text,
 preferred_contact_method text, best_contact_time text, is_primary boolean not null default false,
 contact_status text not null default 'active', notes text, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create unique index if not exists uq_property_primary_contact on property_contacts(property_id) where is_primary;
create index if not exists idx_property_contacts_property on property_contacts(property_id, updated_at desc);

create table if not exists property_follow_up_tasks (
 task_id uuid primary key default gen_random_uuid(), property_id text not null references properties(property_id) on delete cascade,
 contact_id uuid references property_contacts(contact_id) on delete set null, title text not null, description text, task_type text not null default 'follow_up',
 due_at timestamptz, priority text not null default 'normal', status text not null default 'open', completed_at timestamptz,
 assigned_to text, reminder_at timestamptz, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create index if not exists idx_follow_up_tasks_property_due on property_follow_up_tasks(property_id, status, due_at);

create table if not exists property_notes (
 note_id uuid primary key default gen_random_uuid(), property_id text not null references properties(property_id) on delete cascade,
 contact_id uuid references property_contacts(contact_id) on delete set null, note_type text not null default 'general', body text not null,
 is_pinned boolean not null default false, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create index if not exists idx_property_notes_property on property_notes(property_id, is_pinned desc, created_at desc);

create table if not exists property_workflow_history (
 history_id uuid primary key default gen_random_uuid(), property_id text not null references properties(property_id) on delete cascade,
 from_stage text, to_stage text not null, reason text, changed_by text, changed_at timestamptz not null default now()
);
create index if not exists idx_workflow_history_property on property_workflow_history(property_id, changed_at desc);

create table if not exists property_activity (
 activity_id uuid primary key default gen_random_uuid(), property_id text not null references properties(property_id) on delete cascade,
 activity_type text not null, entity_type text, entity_id text, title text not null, description text,
 metadata jsonb not null default '{}'::jsonb, occurred_at timestamptz not null default now()
);
create index if not exists idx_property_activity_property on property_activity(property_id, occurred_at desc);

create table if not exists property_deadlines (
 deadline_id uuid primary key default gen_random_uuid(), property_id text not null references properties(property_id) on delete cascade,
 deadline_type text not null check (deadline_type in ('next_seller_follow_up','offer_expiration','inspection','due_diligence','earnest_money','closing','buyer_marketing','assignment','custom')),
 title text not null, due_at timestamptz not null, status text not null default 'open', notes text,
 created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create index if not exists idx_property_deadlines_property_due on property_deadlines(property_id, status, due_at);

create table if not exists property_sent_offers (
 sent_offer_id uuid primary key default gen_random_uuid(), property_id text not null references properties(property_id) on delete cascade,
 offer_analysis_id uuid references property_offer_analysis(offer_analysis_id) on delete set null,
 contact_id uuid references property_contacts(contact_id) on delete set null, offer_amount numeric not null,
 sent_at timestamptz not null default now(), delivery_method text, expiration_at timestamptz, status text not null default 'sent',
 response_notes text, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create index if not exists idx_sent_offers_property on property_sent_offers(property_id, sent_at desc);

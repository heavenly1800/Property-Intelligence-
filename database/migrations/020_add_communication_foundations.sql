alter table property_contacts add column if not exists email_consent_status text not null default 'unknown';
alter table property_contacts add column if not exists email_consent_source text;
alter table property_contacts add column if not exists email_consent_at timestamptz;
alter table property_contacts add column if not exists sms_consent_status text not null default 'unknown';
alter table property_contacts add column if not exists sms_consent_source text;
alter table property_contacts add column if not exists sms_consent_at timestamptz;
alter table property_contacts add column if not exists sms_opted_out_at timestamptz;
alter table property_contacts add column if not exists email_opted_out_at timestamptz;
alter table property_contacts add column if not exists do_not_contact boolean not null default false;
alter table property_contacts add column if not exists timezone text;
alter table property_contacts drop constraint if exists property_contacts_email_consent_check;
alter table property_contacts add constraint property_contacts_email_consent_check check (email_consent_status in ('unknown','consented','transactional_only','opted_out','prohibited'));
alter table property_contacts drop constraint if exists property_contacts_sms_consent_check;
alter table property_contacts add constraint property_contacts_sms_consent_check check (sms_consent_status in ('unknown','consented','transactional_only','opted_out','prohibited'));

create table if not exists communication_templates (
 template_id uuid primary key default gen_random_uuid(), template_name text not null, channel text not null check(channel in ('email','sms')),
 category text not null check(category in ('first_contact','follow_up','offer_notice','offer_expiration','appointment_confirmation','document_request','status_update','custom')),
 subject_template text, body_template text not null, variables jsonb not null default '[]'::jsonb, active boolean not null default true,
 version integer not null default 1, created_at timestamptz not null default now(), updated_at timestamptz not null default now(), unique(template_name,version)
);
create table if not exists property_communications (
 message_id uuid primary key default gen_random_uuid(), property_id text not null references properties(property_id) on delete cascade,
 contact_id uuid not null references property_contacts(contact_id) on delete restrict, template_id uuid references communication_templates(template_id) on delete set null,
 channel text not null check(channel in ('email','sms')), direction text not null default 'outbound' check(direction in ('outbound','inbound')),
 status text not null default 'draft' check(status in ('draft','scheduled','blocked','queued','sent','delivered','failed','received','cancelled')),
 subject text, body text not null, rendered_variables jsonb not null default '{}'::jsonb, provider_name text, provider_message_id text,
 scheduled_for timestamptz, sent_at timestamptz, delivered_at timestamptz, failed_at timestamptz, read_at timestamptz, replied_at timestamptz,
 failure_reason text, consent_snapshot jsonb not null default '{}'::jsonb, related_offer_id uuid references property_sent_offers(sent_offer_id) on delete set null,
 related_task_id uuid references property_follow_up_tasks(task_id) on delete set null, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create index if not exists idx_communications_property on property_communications(property_id,created_at desc);
alter table property_notifications drop constraint if exists property_notifications_notification_type_check;
alter table property_notifications add constraint property_notifications_notification_type_check check(notification_type in ('overdue_follow_up','follow_up_due_today','follow_up_due_soon','deadline_overdue','deadline_due_today','deadline_due_soon','offer_expiring','seller_contact_needed','stale_lead','under_contract_deadline_risk','failed_message','seller_reply_received','scheduled_message_blocked','draft_awaiting_approval','custom'));

insert into communication_templates(template_name,channel,category,subject_template,body_template,variables)
select 'Initial seller email','email','first_contact','Regarding {{property_address}}','Hi {{seller_first_name}}, I am reaching out regarding {{property_address}}. Please call {{callback_number}}.','["seller_first_name","property_address","callback_number"]'::jsonb
where not exists(select 1 from communication_templates where template_name='Initial seller email' and version=1);
insert into communication_templates(template_name,channel,category,body_template,variables)
select 'Seller follow-up SMS','sms','follow_up','Hi {{seller_first_name}}, following up about {{property_address}}. Call {{callback_number}}.','["seller_first_name","property_address","callback_number"]'::jsonb
where not exists(select 1 from communication_templates where template_name='Seller follow-up SMS' and version=1);

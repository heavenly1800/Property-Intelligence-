create table if not exists scanner_execution_locks (
    lock_name text primary key,
    owner_id uuid not null,
    acquired_at timestamptz not null,
    expires_at timestamptz not null
);

create index if not exists idx_scanner_execution_locks_expires_at
    on scanner_execution_locks (expires_at);

alter table scanner_execution_locks enable row level security;

comment on table scanner_execution_locks is
    'Service-role-only leases used to prevent overlapping hosted scanner runs.';

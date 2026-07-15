alter table properties
    add column if not exists owner_name text,
    add column if not exists owner_mailing_address text,
    add column if not exists assessed_land_value numeric,
    add column if not exists assessed_improvement_value numeric,
    add column if not exists assessed_total_value numeric,
    add column if not exists tax_year integer,
    add column if not exists tax_status text,
    add column if not exists last_transfer_date date,
    add column if not exists last_transfer_price numeric,
    add column if not exists assessor_source text;

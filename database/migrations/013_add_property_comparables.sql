create table if not exists property_comparables (
    comparable_id uuid primary key default gen_random_uuid(),
    subject_property_id text not null references properties(property_id) on delete cascade,
    comparable_type text not null check (comparable_type in ('sale', 'rental')),
    source_name text not null, source_url text not null, source_record_id text,
    address text not null, latitude numeric, longitude numeric, distance_miles numeric check (distance_miles >= 0),
    property_type text not null, property_subtype text, unit_count integer check (unit_count > 0),
    bedrooms numeric, bathrooms numeric, square_feet numeric check (square_feet > 0), lot_acres numeric check (lot_acres >= 0),
    year_built integer, condition text, sale_price numeric check (sale_price > 0), sale_date date,
    monthly_rent numeric check (monthly_rent > 0), listing_date date, status text,
    price_per_square_foot numeric, price_per_unit numeric, rent_per_unit numeric, rent_per_square_foot numeric,
    match_score numeric check (match_score between 0 and 100), score_components jsonb not null default '{}'::jsonb,
    included boolean not null default true, exclusion_reason text, notes text,
    created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
    check ((comparable_type = 'sale' and sale_price is not null and sale_date is not null) or
           (comparable_type = 'rental' and monthly_rent is not null and listing_date is not null))
);
create index if not exists property_comparables_subject_idx on property_comparables(subject_property_id, comparable_type);
create unique index if not exists property_comparables_source_record_idx
    on property_comparables(subject_property_id, source_name, source_record_id) where source_record_id is not null;

create table if not exists property_comparable_analysis (
    property_id text primary key references properties(property_id) on delete cascade,
    current_market_value_low numeric, current_market_value_high numeric, estimated_market_value numeric,
    after_repair_value_low numeric, after_repair_value_high numeric, estimated_after_repair_value numeric,
    estimated_monthly_market_rent_low numeric, estimated_monthly_market_rent_high numeric, estimated_monthly_market_rent numeric,
    estimated_annual_market_rent numeric, sale_comparable_count integer not null default 0,
    rental_comparable_count integer not null default 0, average_sale_distance numeric, average_rental_distance numeric,
    comparable_analysis_confidence numeric not null default 0 check (comparable_analysis_confidence between 0 and 1),
    comparable_analysis_status text not null, comparable_missing_items jsonb not null default '[]'::jsonb,
    comparable_limitations jsonb not null default '[]'::jsonb, recommended_comparable_action text not null,
    analyzed_at timestamptz not null default now(), created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);

create or replace function set_property_comparable_updated_at() returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end;
$$;
drop trigger if exists property_comparables_updated_at on property_comparables;
create trigger property_comparables_updated_at before update on property_comparables for each row execute function set_property_comparable_updated_at();
drop trigger if exists property_comparable_analysis_updated_at on property_comparable_analysis;
create trigger property_comparable_analysis_updated_at before update on property_comparable_analysis for each row execute function set_property_comparable_updated_at();

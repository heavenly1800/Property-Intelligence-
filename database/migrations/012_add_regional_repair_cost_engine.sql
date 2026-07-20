create table if not exists repair_cost_profiles (
    profile_id uuid primary key default gen_random_uuid(), profile_name text not null,
    country text not null default 'US', state text, county text, city text, zip_code text,
    effective_date date not null, source_notes text not null, confidence numeric not null check (confidence between 0 and 1),
    is_default boolean not null default false, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create unique index if not exists repair_cost_profiles_name_effective_idx on repair_cost_profiles(profile_name, effective_date);
create unique index if not exists repair_cost_profiles_single_default_idx on repair_cost_profiles(is_default) where is_default;

create table if not exists repair_cost_items (
    item_id uuid primary key default gen_random_uuid(), profile_id uuid not null references repair_cost_profiles(profile_id) on delete cascade,
    category text not null, unit_type text not null check (unit_type in ('square foot','linear foot','per room','per item','per unit/apartment','lump sum','percentage contingency')),
    cost_low_per_unit numeric not null check (cost_low_per_unit >= 0), cost_high_per_unit numeric not null check (cost_high_per_unit >= cost_low_per_unit),
    minimum_job_cost_low numeric not null check (minimum_job_cost_low >= 0), minimum_job_cost_high numeric not null check (minimum_job_cost_high >= minimum_job_cost_low),
    labor_material_notes text not null, source_notes text not null, effective_date date not null,
    contingency_percentage numeric not null default 0 check (contingency_percentage between 0 and 100),
    created_at timestamptz not null default now(), updated_at timestamptz not null default now(), unique(profile_id, category)
);

create or replace function set_repair_cost_updated_at() returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end;
$$;
drop trigger if exists repair_cost_profiles_updated_at on repair_cost_profiles;
create trigger repair_cost_profiles_updated_at before update on repair_cost_profiles for each row execute function set_repair_cost_updated_at();
drop trigger if exists repair_cost_items_updated_at on repair_cost_items;
create trigger repair_cost_items_updated_at before update on repair_cost_items for each row execute function set_repair_cost_updated_at();

alter table property_media_analysis
    add column if not exists visible_repair_subtotal_low numeric not null default 0,
    add column if not exists visible_repair_subtotal_high numeric not null default 0,
    add column if not exists contingency_low numeric not null default 0,
    add column if not exists contingency_high numeric not null default 0,
    add column if not exists regional_profile_id uuid references repair_cost_profiles(profile_id),
    add column if not exists regional_profile_name text,
    add column if not exists profile_match_confidence numeric,
    add column if not exists profile_match_reason text,
    add column if not exists cost_assumption_effective_date date,
    add column if not exists cost_limitations jsonb not null default '[]'::jsonb;

alter table property_condition_analysis
    add column if not exists visible_repair_items jsonb not null default '[]'::jsonb,
    add column if not exists visible_repair_subtotal_low numeric not null default 0,
    add column if not exists visible_repair_subtotal_high numeric not null default 0,
    add column if not exists contingency_low numeric not null default 0,
    add column if not exists contingency_high numeric not null default 0,
    add column if not exists regional_profile_id uuid references repair_cost_profiles(profile_id),
    add column if not exists regional_profile_name text,
    add column if not exists profile_match_confidence numeric,
    add column if not exists profile_match_reason text,
    add column if not exists cost_assumption_effective_date date,
    add column if not exists cost_limitations jsonb not null default '[]'::jsonb;

insert into repair_cost_profiles(profile_id, profile_name, country, effective_date, source_notes, confidence, is_default)
values ('00000000-0000-0000-0000-000000000001', 'US National Underwriting Fallback', 'US', '2026-07-01',
        'Editable national underwriting assumptions; not contractor bids and not sourced from a live contractor database.', .45, true)
on conflict (profile_id) do update set profile_name=excluded.profile_name, source_notes=excluded.source_notes, confidence=excluded.confidence, is_default=excluded.is_default, updated_at=now();

insert into repair_cost_profiles(profile_id, profile_name, country, state, county, city, zip_code, effective_date, source_notes, confidence, is_default)
values ('00000000-0000-0000-0000-000000000029', 'San Bernardino County / Twentynine Palms Underwriting 2026', 'US', 'CA', 'San Bernardino', 'Twentynine Palms', '92277', '2026-07-01',
        'Editable Property Intelligence underwriting assumptions for preliminary visible-scope budgeting; not contractor bids and not sourced from a live contractor database.', .65, false)
on conflict (profile_id) do update set profile_name=excluded.profile_name, state=excluded.state, county=excluded.county, city=excluded.city, zip_code=excluded.zip_code, source_notes=excluded.source_notes, confidence=excluded.confidence, updated_at=now();

with seed(category, unit_type, low_rate, high_rate, min_low, min_high, contingency) as (values
 ('interior paint','square foot',2.00,4.50,750,1800,0), ('exterior paint','square foot',2.50,6.00,1200,3000,0),
 ('flooring','square foot',4.00,12.00,900,2500,0), ('drywall','square foot',3.00,8.00,500,1500,0),
 ('cabinets','linear foot',250,750,1500,5000,0), ('countertops','square foot',45,140,1000,3500,0),
 ('appliances','per item',500,1800,500,1800,0), ('bathroom fixtures','per item',350,1800,500,2200,0),
 ('windows','per item',650,1800,650,1800,0), ('exterior doors','per item',900,2600,900,2600,0),
 ('interior doors','per item',300,900,300,900,0), ('roofing surface','square foot',6,14,1800,5000,0),
 ('siding','square foot',7,18,1200,3500,0), ('landscaping','lump sum',500,3500,500,3500,0),
 ('debris removal','lump sum',400,2200,400,2200,0), ('cleaning','per unit/apartment',300,1200,300,1200,0),
 ('electrical visible repairs','per item',250,1200,350,1500,0), ('plumbing fixture repairs','per item',250,1200,350,1500,0),
 ('HVAC visible service/replacement allowance','per item',350,9500,500,9500,0), ('general contingency','percentage contingency',0,0,0,0,12)
)
insert into repair_cost_items(profile_id, category, unit_type, cost_low_per_unit, cost_high_per_unit, minimum_job_cost_low, minimum_job_cost_high, labor_material_notes, source_notes, effective_date, contingency_percentage)
select '00000000-0000-0000-0000-000000000001', category, unit_type, low_rate, high_rate, min_low, min_high,
       'Preliminary labor-and-material allowance; scope verification required.', 'Editable national underwriting fallback assumption; not a contractor bid.', '2026-07-01', contingency from seed
on conflict (profile_id, category) do update set unit_type=excluded.unit_type, cost_low_per_unit=excluded.cost_low_per_unit, cost_high_per_unit=excluded.cost_high_per_unit, minimum_job_cost_low=excluded.minimum_job_cost_low, minimum_job_cost_high=excluded.minimum_job_cost_high, contingency_percentage=excluded.contingency_percentage, updated_at=now();

with seed(category, unit_type, low_rate, high_rate, min_low, min_high, contingency) as (values
 ('interior paint','square foot',2.25,5.25,850,2100,0), ('exterior paint','square foot',3.00,7.25,1500,3600,0),
 ('flooring','square foot',4.50,14.00,1100,3000,0), ('drywall','square foot',3.50,9.50,600,1800,0),
 ('cabinets','linear foot',285,850,1800,6000,0), ('countertops','square foot',50,160,1200,4200,0),
 ('appliances','per item',550,2100,550,2100,0), ('bathroom fixtures','per item',400,2100,600,2700,0),
 ('windows','per item',750,2200,750,2200,0), ('exterior doors','per item',1050,3100,1050,3100,0),
 ('interior doors','per item',350,1050,350,1050,0), ('roofing surface','square foot',7,16,2200,6000,0),
 ('siding','square foot',8,21,1500,4200,0), ('landscaping','lump sum',600,4200,600,4200,0),
 ('debris removal','lump sum',500,2800,500,2800,0), ('cleaning','per unit/apartment',350,1450,350,1450,0),
 ('electrical visible repairs','per item',300,1450,450,1800,0), ('plumbing fixture repairs','per item',300,1450,450,1800,0),
 ('HVAC visible service/replacement allowance','per item',450,11000,650,11000,0), ('general contingency','percentage contingency',0,0,0,0,15)
)
insert into repair_cost_items(profile_id, category, unit_type, cost_low_per_unit, cost_high_per_unit, minimum_job_cost_low, minimum_job_cost_high, labor_material_notes, source_notes, effective_date, contingency_percentage)
select '00000000-0000-0000-0000-000000000029', category, unit_type, low_rate, high_rate, min_low, min_high,
       'Preliminary labor-and-material allowance reflecting remote High Desert mobilization uncertainty; scope verification required.', 'Editable San Bernardino/Twentynine Palms underwriting assumption; not a contractor bid.', '2026-07-01', contingency from seed
on conflict (profile_id, category) do update set unit_type=excluded.unit_type, cost_low_per_unit=excluded.cost_low_per_unit, cost_high_per_unit=excluded.cost_high_per_unit, minimum_job_cost_low=excluded.minimum_job_cost_low, minimum_job_cost_high=excluded.minimum_job_cost_high, contingency_percentage=excluded.contingency_percentage, updated_at=now();

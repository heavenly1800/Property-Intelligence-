create table properties (

    id uuid primary key default gen_random_uuid(),

    property_id text unique not null,

    address text,

    city text,

    county text,

    state text,

    zip_code text,

    apn text,

    property_type text,

    acres numeric,

    square_feet integer,

    zoning text,

    created_at timestamptz default now()

);

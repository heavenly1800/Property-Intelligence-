alter table properties
    add column if not exists parcel_acres numeric,
    add column if not exists jurisdiction text,
    add column if not exists land_use text,
    add column if not exists parcel_source text;

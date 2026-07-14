alter table properties
    add column if not exists latitude double precision,
    add column if not exists longitude double precision,
    add column if not exists census_tract text,
    add column if not exists block_group text;

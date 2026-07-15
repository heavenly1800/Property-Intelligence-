alter table properties
    add column if not exists flood_zone text,
    add column if not exists flood_zone_subtype text,
    add column if not exists special_flood_hazard_area boolean,
    add column if not exists flood_risk_level text,
    add column if not exists flood_source text;

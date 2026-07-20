alter table property_offer_analysis
    add column if not exists strengths jsonb not null default '[]'::jsonb,
    add column if not exists margin_to_mao numeric,
    add column if not exists allow_over_asking_offer boolean not null default false;

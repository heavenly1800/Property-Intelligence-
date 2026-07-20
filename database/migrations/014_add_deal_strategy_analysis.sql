create table if not exists property_strategy_analysis (
    strategy_analysis_id uuid primary key default gen_random_uuid(),
    property_id text not null references properties(property_id) on delete cascade,
    recommended_strategy text check (recommended_strategy in ('wholesale','wholetail','flip','rental_hold')),
    recommendation_confidence numeric not null check (recommendation_confidence between 0 and 1),
    analysis_status text not null, analyzed_at timestamptz not null default now(), assumptions_version text not null,
    missing_inputs jsonb not null default '[]'::jsonb, limitations jsonb not null default '[]'::jsonb,
    recommended_next_action text not null, input_snapshot jsonb not null,
    created_at timestamptz not null default now()
);
create index if not exists property_strategy_analysis_latest_idx on property_strategy_analysis(property_id, analyzed_at desc);

create table if not exists property_strategy_results (
    strategy_result_id uuid primary key default gen_random_uuid(),
    strategy_analysis_id uuid not null references property_strategy_analysis(strategy_analysis_id) on delete cascade,
    strategy text not null check (strategy in ('wholesale','wholetail','flip','rental_hold')),
    viable boolean not null, rank integer, score numeric not null check (score between 0 and 100),
    confidence numeric not null check (confidence between 0 and 1), acquisition_price_used numeric,
    value_basis text, value_low numeric, value_high numeric, rehab_cost_low numeric, rehab_cost_high numeric,
    holding_costs numeric, closing_costs numeric, selling_costs numeric,
    projected_revenue_low numeric, projected_revenue_high numeric, projected_profit_low numeric, projected_profit_high numeric,
    projected_return_percentage_low numeric, projected_return_percentage_high numeric,
    monthly_cash_flow numeric, annual_cash_flow numeric, cap_rate numeric,
    major_risks jsonb not null default '[]'::jsonb, strengths jsonb not null default '[]'::jsonb,
    missing_inputs jsonb not null default '[]'::jsonb, formula_notes jsonb not null default '[]'::jsonb,
    created_at timestamptz not null default now(), unique(strategy_analysis_id, strategy)
);
create index if not exists property_strategy_results_analysis_idx on property_strategy_results(strategy_analysis_id, rank);

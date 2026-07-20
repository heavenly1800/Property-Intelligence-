create table if not exists property_financing_scenarios (
    financing_scenario_id uuid primary key default gen_random_uuid(),
    property_id text not null references properties(property_id) on delete cascade,
    scenario_name text not null,
    financing_type text not null check (financing_type in ('cash','conventional','dscr','hard_money','private','seller_financing','custom')),
    purchase_price numeric, down_payment_amount numeric, down_payment_percentage numeric,
    loan_amount numeric, interest_rate numeric, amortization_years integer, loan_term_months integer,
    interest_only_months integer not null default 0, points_percentage numeric not null default 0,
    origination_fee numeric not null default 0, appraisal_fee numeric not null default 0,
    lender_fee numeric not null default 0, other_financing_costs numeric not null default 0,
    balloon_payment_month integer, prepayment_penalty numeric not null default 0,
    closing_costs_financed boolean not null default false, rehab_financed_amount numeric not null default 0,
    reserve_requirement numeric not null default 0, notes text, is_approved boolean not null default false,
    created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create index if not exists idx_financing_scenarios_property on property_financing_scenarios(property_id, updated_at desc);

create table if not exists property_financing_analysis (
    financing_analysis_id uuid primary key default gen_random_uuid(),
    financing_scenario_id uuid not null references property_financing_scenarios(financing_scenario_id) on delete restrict,
    property_id text not null references properties(property_id) on delete cascade,
    scenario_name text not null, financing_type text not null,
    monthly_principal_interest numeric, monthly_interest_only numeric, annual_debt_service numeric,
    total_cash_required numeric, financed_basis numeric, loan_to_cost numeric, loan_to_value numeric,
    debt_service_coverage_ratio numeric, leveraged_monthly_cash_flow numeric, leveraged_annual_cash_flow numeric,
    cash_on_cash_return numeric, break_even_occupancy numeric, balloon_balance numeric, total_interest_over_term numeric,
    analysis_confidence numeric not null, missing_inputs jsonb not null default '[]'::jsonb,
    warnings jsonb not null default '[]'::jsonb, limitations jsonb not null default '[]'::jsonb,
    formula_notes jsonb not null default '[]'::jsonb, stress_tests jsonb not null default '[]'::jsonb,
    input_snapshot jsonb not null default '{}'::jsonb, threshold_snapshot jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);
create index if not exists idx_financing_analysis_property on property_financing_analysis(property_id, created_at desc);

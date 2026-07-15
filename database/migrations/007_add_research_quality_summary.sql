alter table properties
    add column if not exists research_quality_score integer,
    add column if not exists parcel_certainty text,
    add column if not exists assessment_coverage text,
    add column if not exists utility_confidence text,
    add column if not exists research_risk_level text,
    add column if not exists missing_research_items jsonb,
    add column if not exists recommended_research_action text;

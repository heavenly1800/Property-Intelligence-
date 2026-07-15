alter table properties
    add column if not exists electric_provider text,
    add column if not exists electric_service_evidence text,
    add column if not exists gas_provider text,
    add column if not exists gas_service_evidence text,
    add column if not exists water_provider text,
    add column if not exists water_service_evidence text,
    add column if not exists sewer_provider text,
    add column if not exists sewer_service_evidence text,
    add column if not exists broadband_summary text,
    add column if not exists broadband_evidence text,
    add column if not exists utilities_source text;

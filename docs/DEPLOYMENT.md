# Staging deployment

For the provider-specific first deployment using Render, Vercel, and Supabase,
follow [STAGING_RUNBOOK.md](STAGING_RUNBOOK.md).

## Environment model

`APP_ENV` must be `development`, `test`, `staging`, or `production`. Development and test default to the two local Vite origins and enabled API docs. Staging requires explicit origins and has configurable docs. Production disables docs by default. Placeholder and wildcard credentialed-origin values are rejected in staging and production.

Backend-only secrets are `SUPABASE_SERVICE_ROLE_KEY` and `OPENAI_API_KEY`. They belong in the hosting secret store and must never use a `VITE_` prefix. `VITE_API_URL`, `VITE_SUPABASE_URL`, and `VITE_SUPABASE_ANON_KEY` are intentionally browser-public.

## Supabase and Auth

1. Create a separate staging Supabase project and enable email/password Auth.
2. Configure Site URL and allowed redirects for the exact staging frontend origin and `/update-password`.
3. Apply `database/migrations/001_create_properties.sql` through `022_add_scanner_execution_lock.sql` in order.
4. Create a test Auth user and bootstrap the migrated development organization.
5. Run SQL checks as authenticated viewer, analyst, manager, admin, suspended user, and service role. Confirm cross-organization `SELECT`, `INSERT`, `UPDATE`, and `DELETE` attempts fail and service-role maintenance succeeds.
6. Enable Supabase backups/PITR appropriate to the deployment tier before real data is accepted.

## Deploy

Copy `.env.staging.example` to an untracked `.env.staging`, replace every placeholder, and keep communications disabled. Validate with:

```powershell
docker compose --env-file .env.staging -f docker-compose.staging.yml config
docker compose --env-file .env.staging -f docker-compose.staging.yml build
docker compose --env-file .env.staging -f docker-compose.staging.yml up -d backend frontend
```

Terminate TLS at a trusted platform proxy. Keep `TRUST_PROXY_HEADERS=false` unless the platform restricts upstream traffic to known proxy addresses; when enabled, configure Uvicorn's `--forwarded-allow-ips` to those addresses rather than `*`. Set `TRUSTED_HOSTS` to the real API hostname and internal health-check hostname.

Verify `/health/live`, `/health/ready`, and `/health/version`. Readiness returns 503 without valid configuration or Supabase connectivity. Logs are structured JSON and can be correlated using `X-Request-ID`.

Run the scanner as a hosted cron one-shot every five minutes:

```bash
python -m app.jobs.notification_scan --batch-size 100
```

The socket lock prevents overlap on one host and migration 022 adds a Supabase lease for hosted cron containers. Rate limits and idempotency replay remain in-memory and single-instance; use shared Redis/database implementations before horizontally scaling the API.

## Rollback and operations

Deploy immutable image tags identified by `BUILD_ID`. To roll back, restore the prior backend/frontend image tags; do not reverse a migration until its compatibility and data impact are reviewed. Inspect error logs by request ID and never paste bearer tokens or seller message bodies into support systems. Rotate service-role, OpenAI, and platform secrets independently, restart affected workloads, and validate readiness. Test database restore procedures regularly.

## Security checklist

- [ ] No service-role key or OpenAI key exists in frontend source/build output.
- [ ] No `.env.local` or real staging environment file is committed.
- [ ] Docs and OpenAPI are disabled in production.
- [ ] CORS contains only explicit HTTPS frontend origins.
- [ ] RLS is enabled and cross-organization SQL checks pass.
- [ ] Supabase Auth email, redirect, password, and abuse settings are reviewed.
- [ ] Invitation expiry and final-owner safeguards are verified.
- [ ] Rate limits are tuned for staging traffic.
- [ ] Logs contain no tokens, secrets, message bodies, or seller-sensitive payloads.
- [ ] Backups and restore testing are enabled.
- [ ] Real communications remain disabled until provider, consent, TCPA, and compliance review are complete.

# Render + Vercel staging runbook

This runbook creates a staging frontend on Vercel, a Docker web service and cron job on Render, and uses the existing Supabase project. Provider limits and pricing change; review current terms before creating resources.

The example hostnames below are placeholders. Replace them with the URLs actually assigned by Render and Vercel.

## 1. Prepare GitHub and Supabase

1. Create and push a `staging` branch.
2. Apply database migrations `001` through `022` to the intended Supabase project and confirm backups are enabled. Migration 022 adds the service-role-only scanner lease table.
3. Review RLS using authenticated users in two organizations. Confirm cross-organization reads and writes fail.
4. In Supabase Auth, configure:
   - Site URL: `https://property-intelligence-staging.vercel.app`
   - Additional Redirect URL: `https://property-intelligence-staging.vercel.app`
   - Additional Redirect URL: `https://property-intelligence-staging.vercel.app/update-password`
   - Additional Redirect URL: `https://property-intelligence-staging.vercel.app/invitations/accept`
5. Replace the example Vercel hostname after Vercel assigns the real deployment URL. Supabase wildcard preview redirects should be enabled only after reviewing their security scope.

The application appends `/update-password` to password-recovery requests. Invitation links use `/invitations/accept?token=...`; Vercel rewrites both direct-navigation routes to the SPA.

## 2. Create Render services

1. Connect the GitHub repository to Render.
2. Create a Blueprint from the root `render.yaml`.
3. Confirm the Blueprint targets the `staging` branch and review the selected service plans.
4. During initial Blueprint creation, enter every `sync: false` value for both services:
   - `BUILD_ID`: Git commit or staging release identifier.
   - `FRONTEND_ORIGINS`: final Vercel origin only, with no trailing slash.
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `OPENAI_API_KEY`
5. Render creates `PORT`; do not add or override it. The web Docker command binds Uvicorn to `0.0.0.0:$PORT`.
6. Deploy `property-intelligence-api-staging` and verify:
   - `/health/live` is 200.
   - `/health/ready` is 200.
   - `/health/version` reports `staging` and the expected build.
   - `/docs` is 404 while `DOCS_ENABLED=false`.
7. Confirm the cron job `property-intelligence-notifications-staging` is scheduled for every ten minutes UTC and runs:

   ```bash
   python -m app.jobs.notification_scan --batch-size 100
   ```

The scanner is a one-shot job. A local socket lock prevents same-host overlap and migration 022 provides a Supabase lease for separate Render containers. Render should show a successful zero exit code. A stale lease expires after `SCANNER_LOCK_TTL_SECONDS`.

## 3. Create the Vercel frontend

1. Import the same GitHub repository into Vercel.
2. Set Root Directory to `apps/web`.
3. Confirm:
   - Framework: Vite
   - Node.js: 22
   - Install command: `npm ci`
   - Build command: `npm run build`
   - Output directory: `dist`
4. Add staging environment variables:
   - `VITE_API_URL=https://property-intelligence-api-staging.onrender.com`
   - `VITE_SUPABASE_URL=https://your-staging-project.supabase.co`
   - `VITE_SUPABASE_ANON_KEY=<staging anon key>`
5. Never add `SUPABASE_SERVICE_ROLE_KEY` or `OPENAI_API_KEY` to Vercel.
6. Deploy the frontend. `apps/web/vercel.json` provides SPA deep-link rewriting and immutable caching only for hashed assets.

## 4. Resolve the final URLs

1. Copy the final Vercel production-domain origin into Render `FRONTEND_ORIGINS` on both the web service and cron job.
2. Copy the final Render API URL into Vercel `VITE_API_URL`.
3. Redeploy the backend after CORS changes and the frontend after Vite variable changes.
4. Replace Supabase Site URL and redirect entries with the final Vercel URL.
5. Do not add Vercel preview origins to CORS unless preview authentication is deliberately supported and reviewed.

## 5. Automated endpoint verification

PowerShell:

```powershell
.\scripts\verify-staging.ps1 `
  -FrontendUrl https://property-intelligence-staging.vercel.app `
  -BackendUrl https://property-intelligence-api-staging.onrender.com `
  -DocsExpectation disabled
```

POSIX shell:

```bash
./scripts/verify-staging.sh \
  https://property-intelligence-staging.vercel.app \
  https://property-intelligence-api-staging.onrender.com \
  disabled
```

## 6. Authenticated smoke test

- [ ] Frontend loads over HTTPS.
- [ ] Email/password sign-in succeeds.
- [ ] Password-reset request reaches the configured staging redirect and password update succeeds.
- [ ] Invitation direct navigation loads and invitation acceptance succeeds after sign-in.
- [ ] Organization selection works.
- [ ] PROP-001 is visible only to the migrated development organization.
- [ ] Dashboard and property detail load.
- [ ] Media loads from Supabase Storage under the intended policies.
- [ ] AI analysis works when `AI_ANALYSIS_ENABLED=true`.
- [ ] Manual notification scan succeeds.
- [ ] Render cron execution finishes successfully.
- [ ] Communication draft saves.
- [ ] Communication Send remains blocked.
- [ ] Cross-organization API access returns 403.
- [ ] Unauthenticated protected API access returns 401.
- [ ] CORS accepts the staging Vercel origin and rejects an unrelated origin.
- [ ] Docs match `DOCS_ENABLED`.
- [ ] All health endpoints return expected metadata/status.
- [ ] Browser bundle contains neither service-role nor OpenAI secrets.

## Cost controls

- Use the smallest practical staging web and cron plans after checking current provider limits.
- Prefer the scheduled one-shot cron over an always-running worker.
- Keep communications disabled.
- Disable AI analysis when it is not under test.
- Keep AI reanalysis rate limits conservative and monitor OpenAI usage limits.
- Avoid enabling automatic preview deployments with paid resources until their lifecycle is understood.

## Rollback

1. Promote the previous healthy Vercel deployment or use Vercel's rollback control.
2. Roll back the Render web service to its previous successful deploy.
3. Suspend the Render cron job if scanner behavior is implicated.
4. Set `AI_ANALYSIS_ENABLED=false`.
5. Confirm `COMMUNICATIONS_ENABLED=false` and `ALLOW_CONSOLE_DELIVERY=false`.
6. Do not reverse database migrations automatically. Use a reviewed down migration or forward fix after evaluating stored data.
7. Preserve Supabase backups and verify restore readiness before any database remediation.

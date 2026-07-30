# Property Intelligence

Property Intelligence is an AI-powered acquisitions operating system for real estate investors, wholesalers, and land acquisition specialists.

The goal is to replace multiple disconnected tools with one intelligent platform that helps users discover opportunities, research properties, manage acquisitions, and make better investment decisions.

---

## Vision

Instead of switching between:

- PropStream
- Zillow
- County GIS
- Google Maps
- CRM software
- Spreadsheets
- AI chat tools
- Note-taking apps

Property Intelligence brings everything together into one workflow.

---

## Current Features

- React frontend
- FastAPI backend
- Supabase database
- Property management
- Opportunity scoring
- Search interface
- Dashboard
- Property detail pages
- Reusable UI component library

---

## Planned Features

### Property Intelligence

- Address search
- APN search
- Parcel search
- GIS integration
- Ownership research
- Market analysis
- Zoning analysis
- Flood zone analysis
- Utility availability
- Comparable sales
- Opportunity scoring

### Acquisition Workflow

- Seller tracking
- Follow-up management
- Notes
- Activity timeline
- Offer generation
- Buyer matching
- Assignment fee estimation

### AI

- Property analysis
- Seller motivation analysis
- Negotiation recommendations
- Offer recommendations
- Due diligence reports
- Acquisition Copilot

---

## Technology Stack

### Frontend

- React
- TypeScript
- Vite

### Backend

- FastAPI
- Python

### Database

- Supabase
- PostgreSQL

---

## Project Structure

```
Property-Intelligence/

apps/
    web/

services/
    api/
    decision-engine/

database/

docs/

design/
```

---

## Development

### Windows quick start

From the repository root, start both development services in separate PowerShell windows:

```powershell
.\start-dev.ps1
```

The script clears only listeners on ports 8000 and 5173, starts the backend and frontend, and verifies both HTTP endpoints. To stop those development services:

To also run the local in-app notification scanner every five minutes:

```powershell
powershell -ExecutionPolicy Bypass -File .\start-dev.ps1 -WithScanner
```

Run one notification scan without starting a recurring worker:

```powershell
cd services/api
.\.venv\Scripts\python.exe -m app.jobs.notification_scan
```

```powershell
.\stop-dev.ps1
```

If local execution policy blocks scripts, use `powershell -ExecutionPolicy Bypass -File .\start-dev.ps1` or the corresponding `stop-dev.ps1` command.

### Manual start

Frontend

```bash
cd apps/web
npm install
npm run dev
```

Backend

```bash
cd services/api

.\.venv\Scripts\Activate.ps1

python -m uvicorn app.main:app --reload
```

### Authentication and organizations

Apply the SQL migrations in `database/migrations` in numeric order, including
`021_add_auth_organizations_rls.sql`. Migration 021 creates the organization,
membership, invitation, profile, and audit tables; assigns existing development
records (including PROP-001) to a fixed development organization; and enables
organization-scoped row-level security.

Create a user in Supabase Authentication (or enable the desired email provider),
then configure the backend `services/api/.env` with `SUPABASE_URL`,
`SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_ROLE_KEY`. The service-role key is
backend-only and must never be copied into the web application.

Copy `apps/web/.env.example` to `apps/web/.env.local` and set the Supabase URL
and public anon key. On first sign-in, the organization setup screen assigns the
first user as owner of the migrated development organization. Later users should
join through an invitation. The selected organization is sent in
`X-Organization-ID` on API requests and is validated against the signed-in user's
active membership.

---

## Mission

Build the most intelligent acquisitions platform for real estate professionals by combining modern software engineering, automation, and artificial intelligence into one unified workspace.

---

Built by Heavenly Hughes.

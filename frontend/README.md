# ForgeGuard AI Operator Dashboard

Responsive dark-theme React/Next.js operator console for the existing ForgeGuard
FastAPI service. The dashboard brings together source telemetry, Phase 4
anomaly reports, Phase 5 visual evidence, Phase 6A maintenance references, and
Phase 6B AI assessments for operator review.

## Setup

Use Node.js 20.9 or newer. From this directory:

```bash
npm install
cp .env.example .env.local
```

Start the existing backend from the repository root in another terminal:

```bash
python3 -m uvicorn backend.app.main:app --reload
```

## Development and validation

```bash
npm run dev
```

Open <http://localhost:3000>. Available checks:

```bash
npm run lint
npm run typecheck
npm test
npm run build
```

## API configuration

Set `NEXT_PUBLIC_API_BASE_URL` in `.env.local`:

```dotenv
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

The browser calls the same-origin Next.js proxy at `/api/v1`; the proxy forwards
the same HTTP method, path, query, and JSON body to the configured existing
backend. This avoids requiring a new CORS configuration in the backend. An
optional server-only `FORGEGUARD_API_BASE_URL` can override the upstream URL.
The dashboard uses the existing routes and request/response shapes; it does not
add or assume any backend endpoint.

## Dashboard architecture

```text
app/
  api/v1/[...path]/route.ts  Same-origin proxy to existing FastAPI routes
  page.tsx                   Dashboard data loading and machine selection
  layout.tsx, globals.css    App shell and industrial dark theme
components/
  dashboard-header.tsx       API status and machine selector
  machine-overview.tsx       Health, severity, risk and diagnosis summary
  telemetry-panel.tsx        Source readings and selectable trend chart
  anomaly-panel.tsx           Sensor anomalies and correlated evidence
  visual-panel.tsx            Structured visual findings
  maintenance-panel.tsx       Retrieved manual sections and provenance
  assessment-panel.tsx        Reasoning, recommendations, operator decision
  evidence-flow.tsx           Evidence-to-operator pipeline diagram
lib/api.ts                    Central typed API client
types/api.ts                  Types matching the current API contracts
tests/                        Component tests for approval and DEMO labeling
```

## DEMO visual evidence

The visual evidence API currently returns Phase 5 synthetic demo evidence. The
dashboard visibly marks `mode: DEMO` as **DEMO EVIDENCE** and explains that it
is not real camera input or neural vision inference. It does not imply real
computer vision is running.

## Human approval and safety

When Phase 6B returns `human_approval_required: true`, the assessment shows
**HUMAN APPROVAL REQUIRED** with approve/reject controls. A choice posts only an
operator decision record to the existing `/api/v1/approval` endpoint. The
dashboard does not execute recommended actions or control machinery.

The present backend uses in-memory assessment/approval state and the project's
local synthetic telemetry dataset. This UI does not claim live telemetry,
persistent decisions, or AMD/ROCm execution.

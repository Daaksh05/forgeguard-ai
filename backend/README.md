# ForgeGuard Backend API

## Purpose

The FastAPI service exposes the existing ForgeGuard telemetry, anomaly detection,
visual evidence, maintenance retrieval, and Phase 6B reasoning pipeline to a
future frontend. It provides decision support only; it does not control
machinery.

## Architecture

```text
Frontend
  -> FastAPI /api/v1
  -> ForgeGuardService
  -> existing Phase 4 detector, Phase 5 DEMO evidence, Phase 6A retrieval
  -> existing Phase 6B Agent
  -> structured assessment requiring human approval
```

The backend invokes the Phase 6B `build_local_demo_evidence()` Python interface
and `Agent.from_evidence()` directly. This reuses the existing pipeline instead
of copying its algorithms or shelling out to a CLI. Sensor readings come from
`data/sensors/pump_001_telemetry.csv`; visual reports come from the existing
Phase 5 demo generator and remain explicitly marked `mode: "DEMO"`.

## API endpoints

All endpoints are under `/api/v1`. Interactive OpenAPI documentation is
available at `/docs` and `/redoc`.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | API health |
| `GET` | `/machines` | Machines found in the telemetry dataset |
| `GET` | `/machines/{machine_id}` | Dataset metadata and computed health/assessment, when available |
| `GET` | `/machines/{machine_id}/telemetry?limit=50&offset=0` | Paginated source telemetry |
| `GET` | `/machines/{machine_id}/anomalies` | Existing Phase 4 anomaly analysis |
| `GET` | `/machines/{machine_id}/visual-evidence` | Existing Phase 5 visual evidence |
| `GET` | `/machines/{machine_id}/maintenance` | Existing Phase 6A maintenance retrieval for the detected condition |
| `POST` | `/assessment` | Run the full evidence pipeline and Phase 6B reasoning |
| `GET` | `/assessment/{machine_id}` | Get the latest process-local assessment |
| `POST` | `/approval` | Record a human decision in process-local application state |

`POST /assessment` accepts `{"machine_id":"PUMP_001","notes":null}`. It returns
the Phase 6B `AgentOutput` field structure, including `machine_id`, `severity`,
`diagnosis`, `confidence`, `evidence`, `reasoning`, `recommended_actions`,
`human_approval_required`, and `metadata`.

`POST /approval` accepts:

```json
{
  "machine_id": "PUMP_001",
  "approved": true,
  "operator": "demo_operator",
  "comment": "Approved for maintenance inspection"
}
```

It records the decision only; it never sends commands to equipment.

## Project structure

```text
backend/
├── README.md
├── requirements.txt
├── app/
│   ├── main.py
│   ├── schemas.py
│   ├── dependencies.py
│   ├── routes/
│   └── services/forgeguard_service.py
└── tests/
```

## Install

From the repository root:

```bash
python3 -m pip install -r backend/requirements.txt
```

Dependencies are FastAPI, Pydantic, Uvicorn, and HTTPX (used by the API tests).

## Run

From the repository root:

```bash
python3 -m uvicorn backend.app.main:app --reload
```

## Tests

Run backend tests:

```bash
python3 -m unittest discover -s backend/tests -v
```

Run all existing AI module tests and backend tests:

```bash
python3 -m unittest discover -s ai/anomaly_detection/tests -v
python3 -m unittest discover -s ai/vision/tests -v
python3 -m unittest discover -s ai/agent/tests -v
python3 -m unittest discover -s backend/tests -v
```

The standalone Phase 6A test module currently requires the compatibility alias
that the Phase 6B integration helper installs in memory. Run those tests with
that existing helper loaded first:

```bash
python3 -c "from ai.agent.run_agent import _load_rag_pipeline; _load_rag_pipeline(); import unittest; result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover('ai/rag/tests')); raise SystemExit(not result.wasSuccessful())"
```

## Example requests

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/machines
curl 'http://localhost:8000/api/v1/machines/PUMP_001/telemetry?limit=10&offset=0'
curl -X POST http://localhost:8000/api/v1/assessment \
  -H 'Content-Type: application/json' \
  -d '{"machine_id":"PUMP_001"}'
curl -X POST http://localhost:8000/api/v1/approval \
  -H 'Content-Type: application/json' \
  -d '{"machine_id":"PUMP_001","approved":true,"operator":"demo_operator","comment":"Approved for maintenance inspection"}'
```

## Status and limitations

### Implemented

- REST API, OpenAPI docs, telemetry pagination, and unknown-machine handling.
- Direct reuse of Phase 4 anomaly analysis, Phase 5 visual demo evidence,
  Phase 6A maintenance retrieval, and Phase 6B structured reasoning.
- Process-local latest assessments and human approval decisions.
- API and integration tests.

### Demo

- The available asset is derived from the checked-in synthetic
  `PUMP_001` telemetry file.
- Visual evidence is synthetic Phase 5 evidence, always labeled `DEMO`; it is
  not real neural vision inference.
- Approval records only a human decision in application memory and does not
  control equipment.

### Planned

- Live telemetry ingestion, authentication/authorization, durable state,
  frontend integration, real visual inference, and deployment-specific AMD/ROCm
  execution. This backend does not claim AMD/ROCm execution.

Assessments and approvals are lost when the API process restarts. The service
uses the existing local lexical BM25 retrieval pipeline; it adds no vector
database or separate database.

The existing Phase 6A document loader has an unresolved `Tuple_Title_Id_Meta`
annotation. Phase 6B's local demo helper supplies the compatibility alias in
memory when importing the existing pipeline; this backend does not modify
Phase 6A or its loader.

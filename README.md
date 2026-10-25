<div align="center">

# 🛡️ ForgeGuard AI

### Evidence-Driven AI for Industrial Equipment Maintenance

**From sensor anomalies to evidence-backed recommendations—with humans in control.**

An end-to-end industrial AI application combining sensor anomaly detection, maintenance knowledge retrieval, AI-assisted reasoning, and human-in-the-loop decision support.

Built by **Linghuraj and Daakshayani** for the **AMD Developer Hackathon: ACT III — Intelligent Industry**.

<br/>

[![Python](https://img.shields.io/badge/Python-Backend-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-Operator%20Dashboard-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-Frontend-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![AI](https://img.shields.io/badge/AI-Reasoning%20%2B%20RAG-8A2BE2?style=for-the-badge)](#-ai-and-retrieval-pipeline)
[![AMD](https://img.shields.io/badge/AMD-Instinct%20%2B%20ROCm%20Roadmap-ED1C24?style=for-the-badge&logo=amd&logoColor=white)](https://www.amd.com/)

<br/>

**[Features](#-key-features) • [Architecture](#-system-architecture) • [Tech Stack](#-technology-stack) • [Getting Started](#-getting-started) • [API](#-api-overview) • [Testing](#-testing) • [Roadmap](#-roadmap)**

</div>

---

## 🖥️ Dashboard Preview

ForgeGuard AI provides an operator-oriented interface for monitoring industrial equipment, inspecting sensor telemetry, reviewing anomaly assessments, and following the evidence flow behind maintenance recommendations.

![ForgeGuard AI Operator Dashboard](docs/assets/forgeguard-dashboard.png)

*The dashboard screenshot illustrates the local application interface. Sensor readings shown in the demonstration use synthetic telemetry.*

---

## 💡 The Problem

Industrial equipment failures can result in unplanned downtime, expensive repairs, and operational disruption.

Traditional monitoring systems can identify abnormal sensor readings, but operators may still need to investigate several separate sources to understand what happened and decide what to do next.

AI systems introduce another challenge: **a recommendation is not enough if the operator cannot inspect the evidence behind it.**

Industrial maintenance requires more than a model-generated answer. It needs a workflow that connects equipment signals, technical knowledge, explanations, and human judgment.

### Our objective

Build an integrated AI application that helps operators:

- Identify abnormal industrial sensor patterns.
- Understand equipment conditions through structured assessments.
- Retrieve relevant maintenance documentation.
- Connect detected anomalies with maintenance knowledge.
- Review AI-generated explanations and recommended actions.
- Keep human approval within the maintenance decision workflow.

---

## 🚀 What Is ForgeGuard AI?

**ForgeGuard AI is an evidence-driven industrial maintenance assistant that combines telemetry analysis, retrieval-augmented generation, and AI-assisted reasoning in one application.**

The system brings together a Python-based processing pipeline, a FastAPI backend, and a Next.js operator dashboard.

Rather than treating AI reasoning as an isolated model call, ForgeGuard AI organizes the workflow around multiple evidence sources and a final human decision point.

### The core idea

**Detect → Retrieve → Reason → Recommend → Review**

The objective is to make equipment assessments easier to inspect and evaluate, while keeping people involved in maintenance decisions.

---

## ⚙️ Key Features

### 1. 🔍 Sensor Anomaly Detection

Analyzes industrial pump telemetry to identify abnormal operating conditions.

The implemented analysis pipeline includes:

- Sensor threshold checks.
- Rolling statistical analysis.
- Multi-sensor correlation.
- Severity assessment based on detected anomalies.
- Structured findings for downstream reasoning.

The current demonstration uses **synthetic pump telemetry**, rather than live readings from physical industrial equipment.

### 2. 📊 Equipment Health Dashboard

The Next.js operator interface presents equipment assessments in a unified view.

The dashboard includes:

- Machine identification and operating condition.
- Equipment health severity.
- Risk score.
- Sensor telemetry cards.
- Bearing temperature trend visualization.
- Anomaly and assessment information.
- Evidence pipeline status.
- Operator decision workflow.

The interface is designed to help users inspect the assessment rather than relying exclusively on a text response.

### 3. 📚 Retrieval-Augmented Generation (RAG)

ForgeGuard AI incorporates a maintenance knowledge retrieval pipeline to provide relevant technical documentation to the reasoning workflow.

The current retrieval implementation uses **BM25-based lexical retrieval** over maintenance documentation.

This enables the application to retrieve relevant maintenance information that can support troubleshooting and equipment assessment.

The retrieval component is intended to connect detected equipment conditions with supporting maintenance knowledge.

### 4. 🧠 AI-Assisted Reasoning

The reasoning agent brings together information from the available assessment pipeline, including:

- Sensor anomaly findings.
- Visual-evidence inputs.
- Retrieved maintenance knowledge.

It uses this evidence to produce a structured assessment, explanations, and recommended next steps.

The quality of any recommendation depends on the quality and completeness of the evidence supplied to the workflow.

### 5. 👁️ Visual-Evidence Integration

The application includes a visual-evidence component in the assessment workflow.

**Current limitation:** This component is a demonstration layer. It should not be interpreted as a production computer-vision model or as validated image-based defect detection.

Integrating and validating a real computer-vision model is a potential future improvement.

### 6. 🤝 Human-in-the-Loop Decision Support

ForgeGuard AI incorporates a human approval workflow.

The system is designed to support operator review of maintenance assessments and recommendations rather than treating an AI-generated recommendation as automatic authorization to perform physical maintenance.

Human oversight is an important part of the project's approach to responsible industrial AI.

### 7. ⚡ FastAPI Backend

The backend exposes versioned REST API endpoints for application functionality.

It connects the existing assessment pipeline to the frontend and provides endpoints for accessing equipment information, telemetry, anomaly findings, maintenance evidence, visual evidence, and approval workflows.

### 8. 💻 Next.js Operator Dashboard

The frontend provides an operator-facing application for interacting with the backend.

Its responsibilities include:

- Displaying equipment information.
- Presenting telemetry and assessment results.
- Visualizing sensor trends.
- Exposing the evidence flow.
- Connecting the operator interface to backend API routes.

### 9. ✅ Automated Testing

The project includes backend and frontend tests.

The development workflow has previously passed:

- **Python:** 48 tests in the full backend/project suite.
- **RAG:** 12 targeted tests.
- **Frontend:** 2 tests.
- **Frontend linting:** Passed.
- **Frontend production build:** Passed.

These results describe the tested development state and are not a guarantee of production readiness. Run the commands in the testing section to verify your current checkout.

---

## 🏗️ System Architecture

ForgeGuard AI is organized as an end-to-end application with a telemetry and assessment pipeline behind a web-based operator interface.

```text
                   ┌─────────────────────────────┐
                   │     Synthetic Telemetry     │
                   │      Industrial Pump        │
                   └──────────────┬──────────────┘
                                  │
                                  ▼
                   ┌─────────────────────────────┐
                   │   Sensor Anomaly Detection  │
                   │                             │
                   │  • Threshold checks         │
                   │  • Rolling statistics       │
                   │  • Sensor correlation       │
                   └──────────────┬──────────────┘
                                  │
                                  ▼
                   ┌─────────────────────────────┐
                   │    Evidence Collection      │
                   │                             │
                   │  • Sensor findings          │
                   │  • Visual evidence (demo)   │
                   │  • Maintenance knowledge    │
                   └──────────────┬──────────────┘
                                  │
                     ┌────────────┴────────────┐
                     │                         │
                     ▼                         ▼
          ┌────────────────────┐   ┌────────────────────┐
          │ Maintenance RAG    │   │ Visual-Evidence    │
          │ BM25 Retrieval     │   │ Demonstration      │
          └─────────┬──────────┘   └─────────┬──────────┘
                    │                        │
                    └────────────┬───────────┘
                                 │
                                 ▼
                   ┌─────────────────────────────┐
                   │   AI Reasoning Agent        │
                   │                             │
                   │ Evidence-based assessment   │
                   │ Explanations and actions    │
                   └──────────────┬──────────────┘
                                  │
                                  ▼
                   ┌─────────────────────────────┐
                   │      FastAPI Backend        │
                   │         /api/v1             │
                   └──────────────┬──────────────┘
                                  │
                                  ▼
                   ┌─────────────────────────────┐
                   │  Next.js Operator Dashboard │
                   │                             │
                   │  Health • Risk • Telemetry  │
                   │  Evidence • Recommendations │
                   └──────────────┬──────────────┘
                                  │
                                  ▼
                   ┌─────────────────────────────┐
                   │   Human Review / Approval   │
                   └─────────────────────────────┘
```

*Conceptual architecture: the diagram illustrates the logical workflow, not a claim that every component is an independently deployed service.*

### Evidence flow

**Telemetry → Anomaly Detection → Maintenance Retrieval → AI Reasoning → Recommendations → Human Review**

The visual-evidence demonstration is another input to the assessment workflow.

---

## 🧠 AI and Retrieval Pipeline

The project's AI workflow is designed to connect structured sensor analysis with relevant maintenance knowledge.

### Stage 1: Telemetry analysis

The sensor-analysis pipeline evaluates telemetry and identifies potentially abnormal readings using the implemented anomaly-detection logic.

### Stage 2: Knowledge retrieval

The RAG component retrieves relevant passages from the maintenance knowledge base using BM25 lexical retrieval.

### Stage 3: Evidence integration

Available anomaly findings, visual-evidence inputs, and retrieved maintenance information are supplied to the reasoning workflow.

### Stage 4: Assessment and recommendations

The reasoning agent produces an assessment intended to explain its findings and recommend potential next steps.

### Stage 5: Human review

The operator can review the resulting assessment through the application's approval workflow.

**Important distinction:** Evidence integration does not automatically guarantee that every recommendation is correct. Real-world deployment would require additional validation, representative industrial data, and appropriate operational safeguards.

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Backend language | Python | Core processing and assessment logic |
| REST API | FastAPI | Exposes backend functionality |
| ASGI server | Uvicorn | Runs the backend application |
| Frontend framework | Next.js | Operator dashboard |
| Frontend language | TypeScript | Frontend application logic and typing |
| Styling | CSS / project styling | Dashboard layout and presentation |
| Retrieval | BM25 lexical retrieval | Maintenance document search |
| AI reasoning | Reasoning-agent pipeline | Evidence-based assessment and recommendations |
| Testing | pytest and frontend test tooling | Automated validation |
| Target hardware exploration | AMD Instinct + ROCm | Planned GPU compatibility and execution validation |

The stack above describes the project's implementation and target platform. AMD Instinct hardware execution and ROCm compatibility remain subject to actual environment and workload validation.

---

## 📂 Project Structure

The following is a high-level guide to the repository. Exact filenames may vary by checkout.

```text
forgeguard-ai/
│
├── ai/
│   └── rag/
│       ├── document_loader.py
│       └── tests/
│
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
│
├── data/
│   └── maintenance_docs/
│       └── pump_bearing_maintenance.md
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── package.json
│   └── ...
│
├── docs/
│   └── assets/
│       └── forgeguard-dashboard.png
│
├── .venv/
├── README.md
└── ...
```

This is a simplified architectural overview, not an exhaustive listing of every file.

---

## 🚀 Getting Started

Follow these instructions to run ForgeGuard AI locally on macOS.

### Prerequisites

Install or prepare the following:

- Python 3.
- Node.js and npm.
- Git.
- A terminal.
- The project repository.

The Python virtual environment and frontend dependencies must be installed before starting the application for the first time.

### 1. Clone the repository

```bash
git clone https://github.com/Daaksh05/forgeguard-ai.git
cd forgeguard-ai
```

If you already have the repository on your computer, navigate to the existing project directory instead.

### 2. Set up the Python environment

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install backend dependencies:

```bash
pip install -r backend/requirements.txt
```

If the repository's dependency requirements change, reinstall or update the environment as needed.

### 3. Start the backend

From the repository root, with the virtual environment activated:

```bash
uvicorn backend.app.main:app --reload
```

The backend should be available at:

- **API:** http://127.0.0.1:8000
- **Interactive API documentation:** http://127.0.0.1:8000/docs

Keep this terminal running.

If startup fails, check the Python dependencies and the error output before proceeding.

### 4. Start the frontend

Open a second terminal:

```bash
cd ~/Downloads/forgeguard-ai/frontend
npm install
npm run dev -- --webpack
```

The Webpack flag is included because the development environment previously encountered missing native Turbopack bindings on macOS Apple Silicon.

If you cloned the repository to another location, replace the path above with your actual repository path.

Open:

**http://localhost:3000**

Keep the frontend terminal running while using the dashboard.

### 5. Verify the application

Check that:

1. The frontend opens.
2. The backend starts without errors.
3. The dashboard can reach the backend.
4. Equipment information and telemetry are displayed.
5. Assessment and evidence workflows respond as expected.

If the dashboard loads but API requests fail, check the backend terminal and the frontend's API configuration.

---

## 🔌 API Overview

The backend exposes versioned API routes under:

```text
/api/v1
```

The implemented application includes API functionality for the following areas:

| Area | Purpose |
|---|---|
| Health | Backend health checks |
| Machines | Equipment information |
| Telemetry | Sensor readings |
| Assessment | Equipment health assessment |
| Anomalies | Sensor anomaly findings |
| Maintenance | Maintenance knowledge and evidence |
| Visual evidence | Demonstration visual-evidence workflow |
| Approval | Human review and approval workflow |

For the authoritative route definitions and request schemas, start the backend and inspect the generated API documentation:

**http://127.0.0.1:8000/docs**

The available routes and schemas shown by the running application are the source of truth.

---

## 🧪 Testing

ForgeGuard AI includes automated tests for backend logic, retrieval functionality, and frontend components.

### Run the Python test suite

From the repository root:

```bash
source .venv/bin/activate
python3 -m pytest --import-mode=importlib -q
```

### Run the RAG tests

```bash
python3 -m pytest ai/rag/tests -q
```

### Run frontend tests

```bash
cd frontend
npm test
```

### Run frontend linting

```bash
npm run lint
```

### Build the frontend

```bash
npm run build
```

Run these checks after making changes to help identify regressions.

---

## 🧭 Roadmap

### Implemented application capabilities

- [x] Synthetic industrial pump telemetry workflow.
- [x] Sensor anomaly detection.
- [x] Multi-sensor assessment logic.
- [x] BM25-based maintenance knowledge retrieval.
- [x] AI-assisted reasoning workflow.
- [x] Visual-evidence demonstration component.
- [x] Human-in-the-loop approval workflow.
- [x] FastAPI backend.
- [x] Next.js operator dashboard.
- [x] Backend and frontend test suites.

### Next engineering milestones

- [ ] Complete end-to-end integration and hardening.
- [ ] Validate AMD Instinct hardware compatibility.
- [ ] Validate ROCm and the relevant GPU software stack.
- [ ] Benchmark representative workloads on verified hardware.
- [ ] Evaluate the reasoning pipeline using representative scenarios.
- [ ] Explore integration with a real computer-vision model.
- [ ] Investigate real sensor data and industrial integration requirements.
- [ ] Improve operational observability and assessment evaluation.
- [ ] Prepare a complete project demonstration and technical documentation.

Roadmap items are goals, not claims that the corresponding functionality has already been completed.

---

## 🔬 Current Limitations

ForgeGuard AI is a development and demonstration project. Several limitations should be understood when evaluating its capabilities.

**Synthetic telemetry:** The current demonstration uses synthetic pump readings. Results should not be interpreted as validated predictions for real industrial equipment.

**Visual evidence:** The visual-evidence layer is a demonstration component, not a validated production computer-vision system.

**Hardware validation:** AMD Instinct and ROCm execution have not been confirmed. Hardware compatibility and performance require actual testing in the target environment.

**Recommendation validation:** AI-generated maintenance recommendations require evaluation against reliable technical references and domain-expert judgment before use in real operations.

**Production deployment:** Real industrial deployment would require further reliability, security, operational, and safety validation.

We believe transparency about these limitations is an important part of building trustworthy industrial AI systems.

---

## 🎯 Project Goals

ForgeGuard AI explores how AI can support industrial maintenance by connecting:

- Sensor analytics.
- Retrieval-augmented generation.
- Evidence-informed reasoning.
- Operator-facing software.
- Human review and approval.

The broader goal is to move from isolated AI responses toward **integrated AI systems whose findings can be inspected, evaluated, and reviewed by people.**

---

## 👥 Built By

**Linghuraj and Daakshayani**

Developed for the **AMD Developer Hackathon: ACT III — Intelligent Industry**.

We are interested in building practical AI systems that combine machine learning, retrieval, reasoning, backend engineering, and user-facing applications.

---

## 🔗 Project Links

- **GitHub repository:** https://github.com/Daaksh05/forgeguard-ai
- **Local dashboard:** http://localhost:3000
- **Local API documentation:** http://127.0.0.1:8000/docs

The dashboard and API addresses above are local development URLs. They are not publicly hosted demo links.

---

## 🤝 Contributing

Contributions, technical feedback, and suggestions are welcome.

A useful contribution workflow is:

1. Fork the repository.
2. Create a feature branch.
3. Implement and test your changes.
4. Open a pull request describing the change and validation performed.

Please avoid committing API keys, credentials, local environment files, or other sensitive configuration.

---

## 📄 License

Check the repository for the project's license before reusing or redistributing the code. If no license file is present, the repository should not be assumed to have an open-source license.

---

<div align="center">

### ForgeGuard AI

**Evidence-driven AI. Explainable assessments. Human-centered decisions.**

Built by **Linghuraj and Daakshayani** 🤝

</div>
# ForgeGuard AI

> Multimodal AI-Powered Industrial Monitoring System for Predictive Maintenance

---

## 📌 Project Overview
**ForgeGuard AI** is an intelligent industrial monitoring and predictive maintenance system built to safeguard mission-critical industrial machinery. It aggregates and correlates multimodal data streams—including visual feeds, telemetry sensor signals, and technical maintenance manuals—orchestrating an AI agent to explain emerging issues, perform knowledge-backed root-cause analysis, and provide actionable maintenance recommendations to operators.

### Target Hackathon Track
- **Event:** AMD Developer Hackathon: ACT III
- **Track:** Intelligent Industry
- **Hardware & Acceleration Target (Planned):** AMD Infrastructure & ROCm-accelerated AI workloads.

---

## 🏗️ Planned Architecture

```
                                  +-----------------------+
                                  |    Industrial Fleet   |
                                  | (Cameras / Telemetry) |
                                  +-----------+-----------+
                                              |
                     +------------------------+------------------------+
                     |                                                 |
                     v                                                 v
           +--------------------+                            +--------------------+
           |   Visual Feeds     |                            |   Sensor Streams   |
           +---------+----------+                            +---------+----------+
                     |                                                 |
                     v                                                 v
       +----------------------------+                    +----------------------------+
       |   ai/vision/ (Planned)     |                    | ai/anomaly_detection/      |
       |  Visual Defect Detection   |                    | (Planned) Sensor Telemetry |
       +-------------+--------------+                    +-------------+--------------+
                     |                                                 |
                     +------------------------+------------------------+
                                              | Evidence Tokens
                                              v
                              +-------------------------------+
                              |       ai/agent/ (Planned)     | <====+  ai/rag/ (Planned)
                              | Multimodal Correlation Engine |      |  Maintenance Manuals &
                              +---------------+---------------+      |  Technical Docs Retrieval
                                              |                      +-----------------------+
                                              v
                              +-------------------------------+
                              |    backend/ (Planned API)     |
                              +---------------+---------------+
                                              |
                                              v
                              +-------------------------------+
                              |   frontend/ (Planned UI)      |
                              | Operator Monitoring Dashboard |
                              +-------------------------------+
```

---

## 🚦 Current Project Status

- [x] Initial repository scaffolding and clean architecture setup.
- [x] **AMD/ROCm Environment Setup & Verification Tooling:** Verification scripts and deployment guide for AMD Developer Cloud ([`docs/amd-setup.md`](file:///Users/daakshayani/Desktop/ForgeGuard%20AI/docs/amd-setup.md)).
- [x] **Data Foundation & Pipelines:** Industrial telemetry schema, 100-row time-series bearing dataset, failure scenarios, and maintenance SOPs ([`data/sensors/`](file:///Users/daakshayani/Desktop/ForgeGuard%20AI/data/sensors/), [`data/maintenance_docs/`](file:///Users/daakshayani/Desktop/ForgeGuard%20AI/data/maintenance_docs/)).

- [ ] **AI Modules:**
  - [ ] `ai/vision/`: Visual anomaly/defect detection *(Planned)*.
  - [ ] `ai/anomaly_detection/`: Sensor stream anomaly detection *(Planned)*.
  - [ ] `ai/rag/`: Retrieval-Augmented Generation for maintenance manuals *(Planned)*.
  - [ ] `ai/agent/`: Multimodal reasoning & operator recommendation agent *(Planned)*.
- [ ] **Backend Services:** API gateway and inference orchestration layer *(Planned)*.
- [ ] **Frontend Application:** Real-time industrial dashboard & incident explorer *(Planned)*.
- [ ] **AMD Hardware Execution:** Live execution of models on AMD Developer Cloud Instinct GPUs *(Planned)*.

---

## ⚡ AMD / ROCm Hardware Strategy & Status

ForgeGuard AI is built for the **AMD Developer Hackathon: ACT III (Intelligent Industry)**, targeting high-throughput acceleration on AMD hardware.

### Hardware Execution Status
- **Verified**:
  - AMD verification tooling created and functional ([`docs/verify_amd.py`](file:///Users/daakshayani/Desktop/ForgeGuard%20AI/docs/verify_amd.py)).
  - AMD Developer Cloud setup guide and ROCm 6.x deployment specifications completed ([`docs/amd-setup.md`](file:///Users/daakshayani/Desktop/ForgeGuard%20AI/docs/amd-setup.md)).
- **Not yet verified**:
  - Local workstation verification (Host is macOS/Apple Silicon; ROCm Linux kernel runtime is not natively supported on macOS).
- **Planned**:
  - Running visual defect detection on AMD Instinct GPU instances (ADC).
  - Accelerating embedding generation and vector search for technical maintenance RAG on ROCm.
  - Sensor anomaly inference batch evaluation on AMD compute units.

---

## 📂 Repository Structure

```
forgeguard-ai/
├── README.md                 # Project overview and architecture specification
├── .gitignore                # Git ignore rules for Python & JS/TS environments
├── frontend/                 # Operator dashboard & UI (Planned)
├── backend/                  # API server & orchestration bridge (Planned)
├── ai/                       # Multimodal AI modules
│   ├── vision/               # Visual defect detection (Planned)
│   ├── anomaly_detection/    # Sensor telemetry anomaly detection (Planned)
│   ├── rag/                  # Maintenance document retrieval/RAG (Planned)
│   └── agent/                # Multimodal correlation & recommendation agent (Planned)
├── data/                     # Raw & sample datasets
│   ├── sensors/              # Telemetry streams (temperature, vibration, pressure, etc.)
│   └── maintenance_docs/     # Standard operating procedures & maintenance manuals
└── docs/                     # Architecture diagrams, specifications, & hackathon deliverables
    ├── amd-setup.md          # AMD Developer Cloud & ROCm deployment guide
    ├── verify_amd.py         # Automated AMD/ROCm detection & verification script
    └── README.md             # Documentation index
```

---

## 🔒 Notes
*All AI models, backend logic, and frontend components are currently marked as **Planned** and will be implemented incrementally in subsequent phases.*


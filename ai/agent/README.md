# Agent Module - Multimodal Reasoning & Action Orchestrator

## Purpose
The central reasoning layer for ForgeGuard AI correlates sensor, visual, and maintenance evidence to produce a diagnosis, explanatory reasoning, recommended actions, severity, confidence, and approval guidance for operators.

## Phase 6B Implementation
This module normalizes the existing Phase 4, Phase 5, and Phase 6A evidence outputs into a single `AgentInput`, then synthesizes them with a deterministic reasoning engine.

## Included Components
- `schemas.py` - strongly typed normalized input/output contracts
- `evidence_adapter.py` - adapters from existing evidence objects to `AgentInput`
- `prompts.py` - prompt templates for the reasoning workflow
- `reasoning.py` - multimodal diagnosis and action synthesis engine
- `agent.py` - public orchestration interface
- `run_agent.py` - command-line execution entry point

## Supported Modes
Visual inference modes are preserved as:
- `REAL`
- `DEMO`
- `INFERENCE_SIMULATED`

Missing modalities are handled gracefully without inventing sensor values, visual findings, or maintenance guidance.

## Example
```python
from ai.agent.agent import Agent

result = Agent().from_evidence(
    machine_id="PUMP_001",
    sensor_report=sensor_report,
    visual_report=visual_report,
    maintenance_report=maintenance_report,
)

print(result.diagnosis)
print(result.recommended_actions)
```

## Local End-to-End Demo
Run the agent without evidence arguments to execute the existing PUMP_001 evidence pipeline:

```bash
python3 ai/agent/run_agent.py
```

The launcher runs Phase 4 telemetry analysis on `data/sensors/pump_001_telemetry.csv`, selects the corresponding explicitly labeled Phase 5 demo report, retrieves maintenance evidence with the Phase 6A BM25 pipeline, and passes all three reports through the Phase 6B adapter and reasoner. Supplying one or more `--sensor`, `--visual`, or `--maintenance` JSON paths keeps the CLI in file-input mode instead.

The current Phase 6A document loader has an unresolved runtime annotation (`Tuple_Title_Id_Meta`). The Phase 6B launcher supplies that missing type alias in memory when importing Phase 6A; it does not edit Phase 6A files or replace its loader, chunker, knowledge base, or retrieval logic.

## Status
Implemented for Phase 6B of the project with no external model dependency required for deterministic reasoning.

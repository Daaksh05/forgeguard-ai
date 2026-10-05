#!/usr/bin/env python3
"""Command-line entry point for the ForgeGuard multimodal reasoning agent."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai.anomaly_detection.config import DEFAULT_CONFIG
from ai.anomaly_detection.detector import AnomalyDetector, load_telemetry
from ai.agent.agent import Agent
from ai.vision.demo import (
    get_demo_evidence_incipient,
    get_demo_evidence_normal,
    get_demo_evidence_severe,
)


def _load_rag_pipeline():
    """Import the existing Phase 6A pipeline despite its unresolved type alias."""
    loader_module_name = "ai.rag.document_loader"
    if loader_module_name not in sys.modules:
        loader_path = PROJECT_ROOT / "ai" / "rag" / "document_loader.py"
        spec = importlib.util.spec_from_file_location(loader_module_name, loader_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Unable to load Phase 6A document loader: {loader_path}")

        loader_module = importlib.util.module_from_spec(spec)
        loader_module.__dict__["Tuple_Title_Id_Meta"] = Tuple[str, str, Dict[str, Any]]
        sys.modules[loader_module_name] = loader_module
        spec.loader.exec_module(loader_module)

    from ai.rag.run_rag import run_rag_pipeline

    return run_rag_pipeline


def _maintenance_query(sensor_report: Any, visual_report: Any) -> str:
    """Build a retrieval query only from actual sensor and visual report evidence."""
    sensor_payload = sensor_report.to_dict()
    final_state = sensor_payload["final_machine_state"]
    query_terms = []

    for anomaly in final_state.get("sensor_anomalies", []):
        query_terms.extend(
            (
                anomaly.get("sensor", ""),
                anomaly.get("evidence", ""),
                anomaly.get("possible_implication", ""),
            )
        )
    for correlated in final_state.get("correlated_evidence", []):
        query_terms.extend(
            (
                correlated.get("pattern_name", ""),
                correlated.get("description", ""),
                correlated.get("root_cause_hypothesis", ""),
            )
        )
    for finding in visual_report.to_dict().get("findings", []):
        query_terms.extend(
            (
                finding.get("defect_type", ""),
                finding.get("visual_evidence", ""),
                finding.get("possible_implication", ""),
            )
        )

    query = " ".join(term for term in query_terms if term)
    if not query.strip():
        raise ValueError("Cannot query maintenance knowledge without condition evidence")
    return query


def build_local_demo_evidence():
    """Run the existing Phase 4, Phase 5, and Phase 6A PUMP_001 evidence producers."""
    telemetry_path = PROJECT_ROOT / "data" / "sensors" / "pump_001_telemetry.csv"
    telemetry_rows = load_telemetry(telemetry_path)
    sensor_report = AnomalyDetector(DEFAULT_CONFIG).analyze_stream(telemetry_rows)

    final_severity = sensor_report.final_machine_state.get("severity", "NORMAL")
    visual_generators = {
        "NORMAL": get_demo_evidence_normal,
        "LOW": get_demo_evidence_normal,
        "MEDIUM": get_demo_evidence_incipient,
        "HIGH": get_demo_evidence_incipient,
        "CRITICAL": get_demo_evidence_severe,
    }
    if final_severity not in visual_generators:
        raise ValueError(f"Unsupported Phase 4 severity for visual demo selection: {final_severity}")
    visual_generator = visual_generators[final_severity]
    visual_report = visual_generator(
        machine_id=sensor_report.machine_id,
        timestamp=sensor_report.analysis_period.get("end"),
    )

    run_rag_pipeline = _load_rag_pipeline()
    maintenance_report, _, _ = run_rag_pipeline(
        query=_maintenance_query(sensor_report, visual_report),
        docs_dir=str(PROJECT_ROOT / "data" / "maintenance_docs"),
        top_k=3,
    )

    return sensor_report, visual_report, maintenance_report


def _load_json(path: Optional[str]) -> Any:
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(description="ForgeGuard AI multimodal reasoning agent")
    parser.add_argument("--sensor", "-s", default=None, help="Path to a sensor-evidence JSON report")
    parser.add_argument("--visual", "-v", default=None, help="Path to a visual-evidence JSON report")
    parser.add_argument("--maintenance", "-m", default=None, help="Path to a maintenance-evidence JSON report")
    parser.add_argument("--machine-id", default=None, help="Machine identifier")
    parser.add_argument("--output", "-o", default=None, help="Where to save the final JSON report")
    args = parser.parse_args()

    if not any((args.sensor, args.visual, args.maintenance)):
        sensor_report, visual_report, maintenance_report = build_local_demo_evidence()
        machine_id = None
    else:
        sensor_report = _load_json(args.sensor)
        visual_report = _load_json(args.visual)
        maintenance_report = _load_json(args.maintenance)
        machine_id = args.machine_id

    agent = Agent()
    result = agent.from_evidence(
        machine_id=machine_id,
        sensor_report=sensor_report,
        visual_report=visual_report,
        maintenance_report=maintenance_report,
    )

    payload = result.to_dict()
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

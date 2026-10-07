"""Orchestrate the existing ForgeGuard evidence and reasoning components."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from ai.agent.agent import Agent
from ai.agent.run_agent import build_local_demo_evidence

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TELEMETRY_PATH = PROJECT_ROOT / "data" / "sensors" / "pump_001_telemetry.csv"


class ForgeGuardService:
    """Read the project dataset, invoke existing AI modules, and retain demo state."""

    def __init__(self) -> None:
        self._telemetry: list[dict[str, Any]] | None = None
        self._evidence_reports: tuple[Any, Any, Any] | None = None
        self._assessments: dict[str, dict[str, Any]] = {}
        self._approvals: dict[str, dict[str, Any]] = {}

    def _load_telemetry(self) -> list[dict[str, Any]]:
        if self._telemetry is None:
            if not TELEMETRY_PATH.is_file():
                raise FileNotFoundError(f"Telemetry dataset not found: {TELEMETRY_PATH}")
            with TELEMETRY_PATH.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                records = []
                for row in reader:
                    records.append(
                        {
                            "machine_id": row["machine_id"],
                            "timestamp": row["timestamp"],
                            "operating_state": row.get("operating_state", "UNKNOWN"),
                            "values": {
                                key: float(value)
                                for key, value in row.items()
                                if key not in {"machine_id", "timestamp", "operating_state"}
                                and value not in (None, "")
                            },
                        }
                    )
            self._telemetry = records
        return self._telemetry

    def list_machines(self) -> list[dict[str, str]]:
        latest_by_machine: dict[str, str] = {}
        for row in self._load_telemetry():
            latest_by_machine[row["machine_id"]] = row["timestamp"]
        return [
            {"machine_id": machine_id, "last_seen": last_seen}
            for machine_id, last_seen in latest_by_machine.items()
        ]

    def _require_machine(self, machine_id: str) -> None:
        if not any(machine["machine_id"] == machine_id for machine in self.list_machines()):
            raise KeyError(machine_id)

    def get_telemetry(self, machine_id: str, limit: int, offset: int) -> dict[str, Any]:
        self._require_machine(machine_id)
        rows = [
            row for row in self._load_telemetry()
            if row["machine_id"] == machine_id
        ]
        return {
            "machine_id": machine_id,
            "total": len(rows),
            "limit": limit,
            "offset": offset,
            "items": rows[offset:offset + limit],
        }

    def _get_evidence_reports(self) -> tuple[Any, Any, Any]:
        if self._evidence_reports is None:
            self._evidence_reports = build_local_demo_evidence()
        sensor_report, _, _ = self._evidence_reports
        if sensor_report.machine_id not in {machine["machine_id"] for machine in self.list_machines()}:
            raise RuntimeError("The existing AI pipeline returned a machine absent from telemetry.")
        return self._evidence_reports

    def get_anomalies(self, machine_id: str) -> dict[str, Any]:
        self._require_machine(machine_id)
        sensor_report, _, _ = self._get_evidence_reports()
        if sensor_report.machine_id != machine_id:
            raise KeyError(machine_id)
        return sensor_report.to_dict()

    def get_visual_evidence(self, machine_id: str) -> dict[str, Any]:
        self._require_machine(machine_id)
        _, visual_report, _ = self._get_evidence_reports()
        if visual_report.machine_id != machine_id:
            raise KeyError(machine_id)
        return visual_report.to_dict()

    def get_maintenance_evidence(self, machine_id: str) -> dict[str, Any]:
        self._require_machine(machine_id)
        _, _, maintenance_report = self._get_evidence_reports()
        return maintenance_report.to_dict()

    def get_machine(self, machine_id: str) -> dict[str, Any]:
        self._require_machine(machine_id)
        anomaly_report = self.get_anomalies(machine_id)
        final_state = anomaly_report["final_machine_state"]
        matching = next(
            machine for machine in self.list_machines()
            if machine["machine_id"] == machine_id
        )
        return {
            **matching,
            "health_status": final_state["health_status"],
            "severity": final_state["severity"],
            "risk_score": final_state["risk_score"],
            "summary": final_state["summary"],
            "latest_assessment": self._assessments.get(machine_id),
        }

    def create_assessment(self, machine_id: str, notes: str | None = None) -> dict[str, Any]:
        self._require_machine(machine_id)
        sensor_report, visual_report, maintenance_report = self._get_evidence_reports()
        if sensor_report.machine_id != machine_id:
            raise KeyError(machine_id)
        result = Agent().from_evidence(
            machine_id=machine_id,
            sensor_report=sensor_report,
            visual_report=visual_report,
            maintenance_report=maintenance_report,
            notes=notes,
        ).to_dict()
        self._assessments[machine_id] = result
        return result

    def get_assessment(self, machine_id: str) -> dict[str, Any]:
        self._require_machine(machine_id)
        try:
            return self._assessments[machine_id]
        except KeyError:
            raise LookupError(machine_id) from None

    def record_approval(self, request: dict[str, Any]) -> dict[str, Any]:
        machine_id = request["machine_id"]
        self._require_machine(machine_id)
        self._approvals[machine_id] = dict(request)
        return {
            "machine_id": machine_id,
            "approved": request["approved"],
            "human_decision": request["approved"],
        }

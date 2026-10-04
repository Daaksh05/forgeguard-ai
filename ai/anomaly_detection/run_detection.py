#!/usr/bin/env python3
"""
ForgeGuard AI — Sensor Anomaly Detection CLI Runner
Executes the hybrid anomaly detection engine on sensor telemetry CSV files,
evaluates progressive degradation, and exports structured evidence.

Usage:
  python3 ai/anomaly_detection/run_detection.py --input data/sensors/pump_001_telemetry.csv
  python3 ai/anomaly_detection/run_detection.py --input data/sensors/pump_001_telemetry.csv --output results/pump_001_anomalies.json
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to sys.path so package imports resolve seamlessly
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai.anomaly_detection.config import DEFAULT_CONFIG
from ai.anomaly_detection.detector import AnomalyDetector, load_telemetry


def print_banner():
    print("=" * 78)
    print("  FORGEGUARD AI — SENSOR TELEMETRY ANOMALY DETECTION ENGINE")
    print("  Hybrid Physics Thresholds | Rolling Z-Scores | Multi-Sensor Correlation")
    print("=" * 78)


def main():
    parser = argparse.ArgumentParser(
        description="ForgeGuard AI Sensor Telemetry Anomaly Detection CLI"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to input sensor telemetry CSV file (e.g. data/sensors/pump_001_telemetry.csv)"
    )
    parser.add_argument(
        "--output", "-o",
        required=False,
        default=None,
        help="Path to output structured JSON file (e.g. results/pump_001_anomalies.json)"
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[-] Error: Input file does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)

    print_banner()
    print(f"[*] Ingesting telemetry: {input_path}")
    data = load_telemetry(input_path)
    print(f"[+] Loaded {len(data)} time-series rows for asset: {data[0].get('machine_id', 'UNKNOWN')}")

    detector = AnomalyDetector(DEFAULT_CONFIG)
    print("[*] Running hybrid anomaly detection & correlation engine...")
    report = detector.analyze_stream(data)

    print("\n" + "-" * 78)
    print("OPERATIONAL HEALTH PROGRESSION TIMELINE")
    print("-" * 78)
    for idx, stage in enumerate(report.overall_health_progression, 1):
        status = stage["stage"]
        icon = "[OK]" if status == "HEALTHY" else ("[WARN]" if status == "EARLY_DEGRADATION" else "[CRIT]")
        print(
            f"  Phase {idx}: {icon:<6} {status:<20} "
            f"Steps: {stage['start_index']:>2} - {stage['end_index']:>2} "
            f"({stage['start_timestamp']} -> {stage['end_timestamp']}) "
            f"[{stage['duration_steps']} steps]"
        )

    print("\n" + "-" * 78)
    print("FINAL MACHINE HEALTH ASSESSMENT")
    print("-" * 78)
    final_state = report.final_machine_state
    print(f"  Asset ID:          {final_state.get('machine_id')}")
    print(f"  Timestamp:         {final_state.get('timestamp')}")
    print(f"  Health Status:     {final_state.get('health_status')}")
    print(f"  Overall Severity:  {final_state.get('severity')}")
    print(f"  Risk Index:        {final_state.get('risk_score'):.1f} / 100.0")
    print(f"  Anomalous Sensors: {', '.join(final_state.get('anomalous_sensors', []))}")
    print(f"  Summary:           {final_state.get('summary')}")

    print("\n" + "-" * 78)
    print("CORRELATED MULTI-SENSOR EVIDENCE (FINAL STEP)")
    print("-" * 78)
    for corr in final_state.get("correlated_evidence", []):
        print(f"  * Pattern:        {corr.get('pattern_name')} [{corr.get('severity')}] (Score: {corr.get('correlation_score')})")
        print(f"    Sensors:        {', '.join(corr.get('involved_sensors', []))}")
        print(f"    Description:    {corr.get('description')}")
        print(f"    Hypothesis:     {corr.get('root_cause_hypothesis')}\n")

    print("-" * 78)
    print("KEY FINDINGS")
    print("-" * 78)
    for finding in report.key_findings:
        print(f"  - {finding}")

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"\n[+] Structured anomaly evidence written to: {out_path.resolve()}")

    print("=" * 78 + "\n")


if __name__ == "__main__":
    main()

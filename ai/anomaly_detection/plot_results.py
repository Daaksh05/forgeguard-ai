#!/usr/bin/env python3
"""
ForgeGuard AI — Sensor Anomaly Detection Visualizer
Generates a multi-panel telemetry and degradation progression plot showing:
1. Temperature (°C) with bearing vs ambient & thermal thresholds
2. Vibration Velocity RMS (mm/s) with ISO 10816 thresholds
3. High-Frequency Acoustic Emission (dB) with alert/critical limits
4. Motor Phase Current (A) with load limits
5. Machine Risk Score & Degradation State Timeline
"""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

from ai.anomaly_detection.config import DEFAULT_CONFIG, SENSOR_THRESHOLDS
from ai.anomaly_detection.detector import AnomalyDetector, load_telemetry


def plot_telemetry_analysis(
    input_csv: Path,
    output_png: Path,
    title: str = "ForgeGuard AI — Sensor Telemetry & Anomaly Detection Analysis (PUMP_001)"
):
    """
    Generate and save a multi-channel anomaly visualization.
    """
    data = load_telemetry(input_csv)
    detector = AnomalyDetector(DEFAULT_CONFIG)
    report = detector.analyze_stream(data)

    timestamps = [datetime.strptime(r["timestamp"], "%Y-%m-%dT%H:%M:%SZ") for r in data]
    temps = [r["temperature"] for r in data]
    amb_temps = [r["ambient_temp"] for r in data]
    vibs = [r["vibration"] for r in data]
    aes = [r["acoustic_emission"] for r in data]
    currs = [r["current"] for r in data]
    risks = [s["risk_score"] for s in report.timeline_evidence]

    # Setup figure with 5 subplots
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, axes = plt.subplots(5, 1, figsize=(14, 16), sharex=True)
    fig.suptitle(title, fontsize=15, fontweight="bold", y=0.99)

    # Shading degradation phases across all subplots
    phase_colors = {
        "HEALTHY": ("#e8f5e9", "#4caf50", "Normal Operation"),
        "EARLY_DEGRADATION": ("#fff8e1", "#ff9800", "Early Degradation"),
        "SEVERE_DEGRADATION": ("#ffebee", "#f44336", "Severe Degradation")
    }

    def shade_phases(ax):
        for stage in report.overall_health_progression:
            st = stage["stage"]
            s_idx = stage["start_index"]
            e_idx = stage["end_index"]
            bg_color, edge_color, label = phase_colors.get(st, ("#f5f5f5", "#9e9e9e", st))
            ax.axvspan(timestamps[s_idx], timestamps[e_idx], color=bg_color, alpha=0.5, zorder=0)

    # 1. Temperature Subplot
    ax0 = axes[0]
    shade_phases(ax0)
    ax0.plot(timestamps, temps, color="#d32f2f", linewidth=2.0, label="Bearing Temp (°C)")
    ax0.plot(timestamps, amb_temps, color="#1976d2", linestyle="--", linewidth=1.5, label="Ambient Temp (°C)")
    ax0.axhline(SENSOR_THRESHOLDS["temperature"].alert_max, color="#ff9800", linestyle=":", label="Alert (>75°C)")
    ax0.axhline(SENSOR_THRESHOLDS["temperature"].critical_max, color="#d32f2f", linestyle=":", label="Critical (>88°C)")
    ax0.fill_between(timestamps, SENSOR_THRESHOLDS["temperature"].normal_min, SENSOR_THRESHOLDS["temperature"].normal_max,
                     color="#c8e6c9", alpha=0.3, label="Normal Band (55-68°C)")
    ax0.set_ylabel("Temperature (°C)", fontweight="bold")
    ax0.legend(loc="upper left", framealpha=0.9, ncol=3, fontsize=9)
    ax0.set_title("1. Bearing Housing Temperature vs Ambient Temperature (Thermal Decoupling)", fontsize=11, fontweight="bold", loc="left")

    # 2. Vibration Subplot
    ax1 = axes[1]
    shade_phases(ax1)
    ax1.plot(timestamps, vibs, color="#e65100", linewidth=2.0, label="Overall Vibration Velocity (mm/s RMS)")
    ax1.axhline(SENSOR_THRESHOLDS["vibration"].alert_max, color="#ff9800", linestyle=":", label="ISO Warning (>4.5 mm/s)")
    ax1.axhline(SENSOR_THRESHOLDS["vibration"].critical_max, color="#d32f2f", linestyle=":", label="ISO Critical (>7.1 mm/s)")
    ax1.fill_between(timestamps, SENSOR_THRESHOLDS["vibration"].normal_min, SENSOR_THRESHOLDS["vibration"].normal_max,
                     color="#c8e6c9", alpha=0.3, label="ISO Good Band (1.2-2.8 mm/s)")
    ax1.set_ylabel("Vibration (mm/s)", fontweight="bold")
    ax1.legend(loc="upper left", framealpha=0.9, ncol=3, fontsize=9)
    ax1.set_title("2. Tri-Axial Vibration Velocity RMS (ISO 10816-3 Class II)", fontsize=11, fontweight="bold", loc="left")

    # 3. Acoustic Emission Subplot
    ax2 = axes[2]
    shade_phases(ax2)
    ax2.plot(timestamps, aes, color="#7b1fa2", linewidth=2.0, label="Acoustic Emission (dB)")
    ax2.axhline(SENSOR_THRESHOLDS["acoustic_emission"].alert_max, color="#ff9800", linestyle=":", label="Alert (>55 dB)")
    ax2.axhline(SENSOR_THRESHOLDS["acoustic_emission"].critical_max, color="#d32f2f", linestyle=":", label="Critical (>70 dB)")
    ax2.fill_between(timestamps, SENSOR_THRESHOLDS["acoustic_emission"].normal_min, SENSOR_THRESHOLDS["acoustic_emission"].normal_max,
                     color="#c8e6c9", alpha=0.3, label="Normal Band (32-45 dB)")
    ax2.set_ylabel("Acoustic (dB)", fontweight="bold")
    ax2.legend(loc="upper left", framealpha=0.9, ncol=3, fontsize=9)
    ax2.set_title("3. High-Frequency Acoustic Stress Waves (Incipient Friction Indicator)", fontsize=11, fontweight="bold", loc="left")

    # 4. Motor Current Subplot
    ax3 = axes[3]
    shade_phases(ax3)
    ax3.plot(timestamps, currs, color="#0288d1", linewidth=2.0, label="Motor Phase Current (A RMS)")
    ax3.axhline(SENSOR_THRESHOLDS["current"].alert_max, color="#ff9800", linestyle=":", label="Alert (>31.5 A)")
    ax3.axhline(SENSOR_THRESHOLDS["current"].critical_max, color="#d32f2f", linestyle=":", label="Critical (>34.0 A)")
    ax3.fill_between(timestamps, SENSOR_THRESHOLDS["current"].normal_min, SENSOR_THRESHOLDS["current"].normal_max,
                     color="#c8e6c9", alpha=0.3, label="Normal Band (26-29 A)")
    ax3.set_ylabel("Current (A)", fontweight="bold")
    ax3.legend(loc="upper left", framealpha=0.9, ncol=3, fontsize=9)
    ax3.set_title("4. Motor Current Draw (Mechanical Resistance Drag)", fontsize=11, fontweight="bold", loc="left")

    # 5. Machine Risk Score Subplot
    ax4 = axes[4]
    shade_phases(ax4)
    ax4.plot(timestamps, risks, color="#212121", linewidth=2.2, label="Machine Risk Index (0-100)")
    ax4.axhline(20.0, color="#4caf50", linestyle="--", alpha=0.7, label="Normal Baseline (<20)")
    ax4.axhline(45.0, color="#ff9800", linestyle="--", alpha=0.7, label="Early Degradation (45)")
    ax4.axhline(70.0, color="#d32f2f", linestyle="--", alpha=0.7, label="Critical Alarm (70)")
    ax4.set_ylabel("Risk Score", fontweight="bold")
    ax4.set_ylim(0, 105)
    ax4.legend(loc="upper left", framealpha=0.9, ncol=4, fontsize=9)
    ax4.set_title("5. Synthesized Machine Health & Degradation Risk Score", fontsize=11, fontweight="bold", loc="left")

    # Format x-axis timestamps
    ax4.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax4.set_xlabel("Time (UTC - 2026-10-04)", fontweight="bold", labelpad=10)

    plt.tight_layout(rect=[0, 0, 1, 0.98])
    output_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_png, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"[+] Visualization successfully saved to: {output_png.resolve()}")


def main():
    parser = argparse.ArgumentParser(
        description="ForgeGuard AI Telemetry Anomaly Visualization Generator"
    )
    parser.add_argument(
        "--input", "-i",
        default="data/sensors/pump_001_telemetry.csv",
        help="Path to sensor telemetry CSV"
    )
    parser.add_argument(
        "--output", "-o",
        default="results/pump_001_anomaly_plot.png",
        help="Path to output visualization PNG"
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"[-] Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Generating telemetry visualization from {input_path}...")
    plot_telemetry_analysis(input_path, output_path)


if __name__ == "__main__":
    main()

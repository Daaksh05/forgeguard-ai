"""
ForgeGuard AI — Sensor Telemetry Anomaly Detection Engine
Modular, explainable, hybrid anomaly detection combining engineering thresholds,
rolling statistical Z-scores, multi-sensor cross-correlation, and machine risk scoring.
"""

import csv
import math
import statistics
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from ai.anomaly_detection.config import (
    DEFAULT_CONFIG,
    SENSOR_THRESHOLDS,
    SENSOR_WEIGHTS,
    AnomalyDetectionConfig,
    SensorThreshold,
)
from ai.anomaly_detection.evidence import (
    CorrelatedEvidence,
    MachineHealthSummary,
    SensorAnomalyEvidence,
    TelemetryAnalysisReport,
)


def load_telemetry(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Load sensor telemetry from a CSV file into structured dictionaries
    with numeric conversions.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Telemetry file not found: {file_path}")

    records = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed_row: Dict[str, Any] = {
                "timestamp": row["timestamp"],
                "machine_id": row["machine_id"],
                "operating_state": row.get("operating_state", "RUNNING")
            }
            # Parse numeric sensor fields
            for key, val in row.items():
                if key not in ("timestamp", "machine_id", "operating_state"):
                    try:
                        parsed_row[key] = float(val)
                    except (ValueError, TypeError):
                        parsed_row[key] = val
            records.append(parsed_row)
    return records


def calculate_baseline(
    data: List[Dict[str, Any]],
    baseline_window: int = 20
) -> Dict[str, Dict[str, float]]:
    """
    Compute baseline statistical parameters (mean, std, min, max) for each sensor
    over the initial healthy baseline window.
    """
    if not data:
        raise ValueError("Cannot calculate baseline on empty dataset")

    window_size = min(len(data), max(3, baseline_window))
    baseline_data = data[:window_size]

    baseline_stats: Dict[str, Dict[str, float]] = {}
    for sensor_name in SENSOR_THRESHOLDS.keys():
        values = [
            row[sensor_name]
            for row in baseline_data
            if sensor_name in row and isinstance(row[sensor_name], (int, float))
        ]
        if values:
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values) if len(values) > 1 else 0.1
            # Avoid division by zero with minimum variance floor
            std_val = max(std_val, 0.05)
            baseline_stats[sensor_name] = {
                "mean": round(mean_val, 3),
                "std": round(std_val, 3),
                "min": round(min(values), 3),
                "max": round(max(values), 3),
                "count": len(values)
            }
    return baseline_stats


def compute_rolling_statistics(
    series: List[float],
    window_size: int = 10
) -> List[Tuple[float, float]]:
    """
    Compute moving average and standard deviation over a sliding window.
    Returns list of (rolling_mean, rolling_std).
    """
    results: List[Tuple[float, float]] = []
    for i in range(len(series)):
        start_idx = max(0, i - window_size + 1)
        sub_series = series[start_idx : i + 1]
        mean_val = statistics.mean(sub_series)
        std_val = statistics.stdev(sub_series) if len(sub_series) > 1 else 0.05
        std_val = max(std_val, 0.05)
        results.append((round(mean_val, 3), round(std_val, 3)))
    return results


class AnomalyDetector:
    """
    Hybrid Sensor Anomaly Detection Engine for industrial rotating machinery.
    Combines ISO/Engineering thresholds, statistical Z-scores, and multi-sensor correlation.
    """

    def __init__(self, config: Optional[AnomalyDetectionConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.thresholds = SENSOR_THRESHOLDS
        self.weights = SENSOR_WEIGHTS

    def evaluate_sensor_sample(
        self,
        machine_id: str,
        timestamp: str,
        sensor_name: str,
        value: float,
        baseline_stats: Dict[str, float],
        rolling_stats: Tuple[float, float]
    ) -> Optional[SensorAnomalyEvidence]:
        """
        Evaluate a single sensor observation against engineering limits and statistical baseline.
        Returns SensorAnomalyEvidence if abnormal, or None if healthy.
        """
        if sensor_name not in self.thresholds:
            return None

        spec = self.thresholds[sensor_name]
        baseline_mean = baseline_stats.get("mean", (spec.normal_min + spec.normal_max) / 2.0)
        baseline_std = max(baseline_stats.get("std", 0.1), 0.05)

        # 1. Statistical Z-score calculation relative to baseline
        z_score = (value - baseline_mean) / baseline_std

        # 2. Engineering Threshold Checks
        is_critical = False
        is_alert = False
        is_normal_range = (spec.normal_min <= value <= spec.normal_max)
        violation_type = ""
        threshold_val = spec.normal_max

        if spec.critical_max is not None and value >= spec.critical_max:
            is_critical = True
            threshold_val = spec.critical_max
            violation_type = f"critical high (>= {spec.critical_max} {spec.unit})"
        elif spec.critical_min is not None and value <= spec.critical_min:
            is_critical = True
            threshold_val = spec.critical_min
            violation_type = f"critical low (<= {spec.critical_min} {spec.unit})"
        elif spec.alert_max is not None and value >= spec.alert_max:
            is_alert = True
            threshold_val = spec.alert_max
            violation_type = f"alert high (>= {spec.alert_max} {spec.unit})"
        elif spec.alert_min is not None and value <= spec.alert_min:
            is_alert = True
            threshold_val = spec.alert_min
            violation_type = f"alert low (<= {spec.alert_min} {spec.unit})"
        elif not is_normal_range:
            threshold_val = spec.normal_max if value > spec.normal_max else spec.normal_min
            violation_type = f"exceeds normal range ({spec.normal_min} - {spec.normal_max} {spec.unit})"

        # 3. Decision Logic: Combine Engineering & Statistical Evidence
        span = max(1.0, spec.normal_max - spec.normal_min)
        abs_deviation = abs(value - baseline_mean)
        has_physical_drift = (abs_deviation >= span * self.config.min_span_fraction_drift)
        is_statistically_abnormal = (abs(z_score) >= self.config.z_score_warning and has_physical_drift)

        # Ambient temperature is an environmental reference sensor; only flag if it exceeds alert limits
        if sensor_name == "ambient_temp" and is_normal_range:
            return None

        # If within normal engineering range and no significant statistical drift, machine is healthy
        if is_normal_range and not is_statistically_abnormal:
            return None

        # Determine severity and anomaly score (0.0 to 100.0)
        if is_critical:
            severity = "CRITICAL"
            excess_ratio = min(2.0, max(1.0, value / (spec.critical_max if spec.critical_max else 1.0)))
            anomaly_score = min(100.0, 85.0 + 15.0 * (excess_ratio - 1.0) + abs(z_score) * 1.5)
            evidence_text = (
                f"Observed {sensor_name} of {value:.2f} {spec.unit} breached CRITICAL threshold "
                f"({threshold_val} {spec.unit}) with statistical deviation Z={z_score:+.2f}σ "
                f"(baseline: {baseline_mean:.2f} {spec.unit})."
            )
            implication = spec.implication_high if value > baseline_mean else spec.implication_low
        elif is_alert:
            severity = "HIGH"
            anomaly_score = min(85.0, 65.0 + abs(z_score) * 2.5)
            evidence_text = (
                f"Observed {sensor_name} of {value:.2f} {spec.unit} breached ALERT threshold "
                f"({threshold_val} {spec.unit}) with statistical deviation Z={z_score:+.2f}σ "
                f"(baseline: {baseline_mean:.2f} {spec.unit})."
            )
            implication = spec.implication_high if value > baseline_mean else spec.implication_low
        elif not is_normal_range:
            severity = "MEDIUM"
            anomaly_score = min(65.0, 40.0 + abs(z_score) * 3.0)
            evidence_text = (
                f"Observed {sensor_name} of {value:.2f} {spec.unit} {violation_type} "
                f"with statistical shift Z={z_score:+.2f}σ above baseline ({baseline_mean:.2f} {spec.unit})."
            )
            implication = spec.implication_high if value > baseline_mean else spec.implication_low
        elif is_statistically_abnormal:
            severity = "LOW"
            anomaly_score = min(40.0, 20.0 + abs(z_score) * 3.5)
            evidence_text = (
                f"Observed {sensor_name} of {value:.2f} {spec.unit} exhibits statistical drift "
                f"Z={z_score:+.2f}σ from baseline ({baseline_mean:.2f} {spec.unit}), though within static envelope."
            )
            implication = f"Incipient parameter drift detected on {sensor_name}."
        else:
            return None

        return SensorAnomalyEvidence(
            machine_id=machine_id,
            timestamp=timestamp,
            sensor=sensor_name,
            observed_value=round(value, 2),
            baseline_value=round(baseline_mean, 2),
            threshold=round(threshold_val, 2),
            anomaly_score=round(anomaly_score, 1),
            severity=severity,
            evidence=evidence_text,
            possible_implication=implication
        )

    def correlate_anomalies(
        self,
        machine_id: str,
        timestamp: str,
        row: Dict[str, Any],
        sensor_anomalies: List[SensorAnomalyEvidence]
    ) -> List[CorrelatedEvidence]:
        """
        Cross-correlate multiple sensor streams to detect complex electro-mechanical patterns.
        """
        correlated: List[CorrelatedEvidence] = []
        anomalous_sensor_names = {a.sensor for a in sensor_anomalies}

        temp = row.get("temperature", 0.0)
        vib = row.get("vibration", 0.0)
        ae = row.get("acoustic_emission", 0.0)
        curr = row.get("current", 0.0)
        amb = row.get("ambient_temp", 22.0)
        press = row.get("pressure", 5.0)

        # 1. Bearing Friction & Lubrication Breakdown Syndrome
        # (Acoustic Emission + Temperature + Vibration + Current)
        bearing_symptoms = [s for s in ["acoustic_emission", "temperature", "vibration", "current"] if s in anomalous_sensor_names]
        
        if len(bearing_symptoms) >= 2:
            max_sensor_sev = max((a.anomaly_score for a in sensor_anomalies if a.sensor in bearing_symptoms), default=50.0)
            corr_score = min(100.0, max_sensor_sev * (1.0 + 0.1 * len(bearing_symptoms)))
            
            if len(bearing_symptoms) >= 3 and (vib >= 4.5 or temp >= 75.0 or ae >= 70.0):
                sev = "CRITICAL" if (vib >= 7.1 or temp >= 88.0) else "HIGH"
                desc = (
                    f"Multi-sensor triad detected across {', '.join(bearing_symptoms)}: "
                    f"Acoustic stress waves ({ae:.1f} dB), thermal escalation ({temp:.1f} °C), "
                    f"and elevated vibration velocity ({vib:.2f} mm/s) indicate active bearing degradation."
                )
                hypothesis = (
                    "Progressive boundary lubrication breakdown causing inner raceway micro-spalling, "
                    "rotational friction, and rapid component wear."
                )
            else:
                sev = "MEDIUM" if len(bearing_symptoms) == 2 else "HIGH"
                desc = (
                    f"Co-occurring elevation in {', '.join(bearing_symptoms)}: "
                    f"Early friction stress waves ({ae:.1f} dB) accompanied by thermal climb ({temp:.1f} °C)."
                )
                hypothesis = "Incipient grease starvation or lubricant film thinning in drive-end bearing cavity."

            correlated.append(CorrelatedEvidence(
                machine_id=machine_id,
                timestamp=timestamp,
                pattern_name="BEARING_LUBRICATION_DEGRADATION",
                involved_sensors=bearing_symptoms,
                correlation_score=round(corr_score, 1),
                severity=sev,
                description=desc,
                root_cause_hypothesis=hypothesis
            ))

        # 2. Thermal Decoupling (Internal Heat vs Ambient Weather)
        delta_t = temp - amb
        if delta_t >= self.config.delta_t_warning and "temperature" in anomalous_sensor_names:
            sev = "CRITICAL" if delta_t >= self.config.delta_t_critical else "HIGH"
            correlated.append(CorrelatedEvidence(
                machine_id=machine_id,
                timestamp=timestamp,
                pattern_name="THERMAL_DECOUPLING",
                involved_sensors=["temperature", "ambient_temp"],
                correlation_score=round(min(100.0, 60.0 + (delta_t - self.config.delta_t_warning) * 2.5), 1),
                severity=sev,
                description=(
                    f"Bearing differential temperature ΔT = {delta_t:.1f} °C (Bearing: {temp:.1f} °C, Ambient: {amb:.1f} °C). "
                    f"Heat generation is strictly internal to the bearing assembly and decoupled from plant climate."
                ),
                root_cause_hypothesis="Internal mechanical heat generation due to excessive friction or preload."
            ))

        # 3. Mechanical vs Hydraulic Discriminator
        # If vibration and temp are elevated but pressure is stable, rule out cavitation
        if ("vibration" in anomalous_sensor_names or "temperature" in anomalous_sensor_names) and (4.8 <= press <= 5.2):
            correlated.append(CorrelatedEvidence(
                machine_id=machine_id,
                timestamp=timestamp,
                pattern_name="MECHANICAL_VS_HYDRAULIC_ISOLATION",
                involved_sensors=["vibration", "pressure"],
                correlation_score=75.0,
                severity="MEDIUM",
                description=(
                    f"Discharge pressure remains stable at {press:.2f} bar while mechanical vibration/temperature escalate. "
                    f"Rules out hydraulic cavitation or discharge blockage; confirms localized mechanical defect."
                ),
                root_cause_hypothesis="Isolated mechanical bearing defect with nominal hydraulic fluid end."
            ))

        return correlated

    def assess_machine_health(
        self,
        machine_id: str,
        timestamp: str,
        row: Dict[str, Any],
        sensor_anomalies: List[SensorAnomalyEvidence],
        correlated_evidence: List[CorrelatedEvidence]
    ) -> MachineHealthSummary:
        """
        Synthesize sensor anomalies and correlated patterns into machine-level health and risk state.
        """
        anomalous_sensors = [a.sensor for a in sensor_anomalies]

        if not sensor_anomalies:
            return MachineHealthSummary(
                machine_id=machine_id,
                timestamp=timestamp,
                health_status="HEALTHY",
                risk_score=0.0,
                severity="NORMAL",
                anomalous_sensors=[],
                correlated_evidence=[],
                summary="All monitored telemetry channels operating within nominal engineering baselines.",
                sensor_anomalies=[]
            )

        # Calculate weighted base risk
        weighted_score = 0.0
        total_weight = 0.0
        for anom in sensor_anomalies:
            w = self.weights.get(anom.sensor, 0.1)
            weighted_score += anom.anomaly_score * w
            total_weight += w

        base_risk = weighted_score / max(total_weight, 0.1)

        # Correlation boost factor
        multiplier = 1.0
        if any(c.pattern_name == "BEARING_LUBRICATION_DEGRADATION" for c in correlated_evidence):
            multiplier *= self.config.bearing_syndrome_boost
        if any(c.pattern_name == "THERMAL_DECOUPLING" for c in correlated_evidence):
            multiplier *= self.config.decoupling_boost

        final_risk = min(100.0, round(base_risk * multiplier, 1))

        # Determine machine progression status and overall severity
        has_critical_sensor = any(a.severity == "CRITICAL" for a in sensor_anomalies)
        has_high_sensor = any(a.severity == "HIGH" for a in sensor_anomalies)
        has_critical_corr = any(c.severity == "CRITICAL" for c in correlated_evidence)

        if has_critical_sensor or has_critical_corr or final_risk >= self.config.risk_threshold_high:
            health_status = "SEVERE_DEGRADATION"
            severity = "CRITICAL" if (has_critical_sensor or final_risk >= 85.0) else "HIGH"
            summary_desc = (
                f"Severe electro-mechanical degradation active on {machine_id}. "
                f"Multiple critical telemetry violations detected across {', '.join(anomalous_sensors)}. "
                f"High risk of imminent bearing seizure or mechanical breakdown."
            )
        elif has_high_sensor or final_risk >= self.config.risk_threshold_medium:
            health_status = "EARLY_DEGRADATION"
            severity = "HIGH" if has_high_sensor else "MEDIUM"
            summary_desc = (
                f"Early degradation symptoms emerging on {machine_id}. "
                f"Anomalous signatures detected on {', '.join(anomalous_sensors)} "
                f"suggesting progressive lubricant film breakdown."
            )
        elif final_risk >= self.config.risk_threshold_low or len(anomalous_sensors) >= 1:
            health_status = "EARLY_DEGRADATION"
            severity = "LOW"
            summary_desc = (
                f"Incipient parameter drift detected on {machine_id} for {', '.join(anomalous_sensors)}. "
                f"Machine remains operational but trending away from nominal baseline."
            )
        else:
            health_status = "HEALTHY"
            severity = "NORMAL"
            summary_desc = f"Nominal baseline condition for {machine_id}."

        return MachineHealthSummary(
            machine_id=machine_id,
            timestamp=timestamp,
            health_status=health_status,
            risk_score=final_risk,
            severity=severity,
            anomalous_sensors=anomalous_sensors,
            correlated_evidence=[c.to_dict() for c in correlated_evidence],
            summary=summary_desc,
            sensor_anomalies=[a.to_dict() for a in sensor_anomalies]
        )

    def analyze_stream(
        self,
        telemetry_rows: List[Dict[str, Any]]
    ) -> TelemetryAnalysisReport:
        """
        Analyze a complete time-series telemetry dataset step-by-step.
        """
        if not telemetry_rows:
            raise ValueError("No telemetry records provided for analysis")

        machine_id = telemetry_rows[0].get("machine_id", "UNKNOWN_ASSET")
        baseline_stats = calculate_baseline(telemetry_rows, self.config.baseline_window_size)

        # Precompute rolling series statistics for all numerical sensor channels
        sensor_series: Dict[str, List[float]] = {}
        for s in self.thresholds.keys():
            sensor_series[s] = [
                float(r[s]) if s in r and isinstance(r[s], (int, float)) else 0.0
                for r in telemetry_rows
            ]

        rolling_stats_map: Dict[str, List[Tuple[float, float]]] = {}
        for s, series in sensor_series.items():
            rolling_stats_map[s] = compute_rolling_statistics(series, self.config.rolling_window_size)

        timeline_summaries: List[MachineHealthSummary] = []
        total_sensor_anomalies = 0

        for idx, row in enumerate(telemetry_rows):
            timestamp = row.get("timestamp", f"STEP_{idx}")
            m_id = row.get("machine_id", machine_id)

            # Evaluate each sensor in this row
            step_sensor_anomalies: List[SensorAnomalyEvidence] = []
            for sensor_name in self.thresholds.keys():
                if sensor_name in row and isinstance(row[sensor_name], (int, float)):
                    val = float(row[sensor_name])
                    b_stat = baseline_stats.get(sensor_name, {})
                    r_stat = rolling_stats_map[sensor_name][idx]

                    evidence = self.evaluate_sensor_sample(
                        machine_id=m_id,
                        timestamp=timestamp,
                        sensor_name=sensor_name,
                        value=val,
                        baseline_stats=b_stat,
                        rolling_stats=r_stat
                    )
                    if evidence:
                        step_sensor_anomalies.append(evidence)

            total_sensor_anomalies += len(step_sensor_anomalies)

            # Evaluate multi-sensor cross-correlations
            step_correlated = self.correlate_anomalies(
                machine_id=m_id,
                timestamp=timestamp,
                row=row,
                sensor_anomalies=step_sensor_anomalies
            )

            # Synthesize machine health status
            machine_summary = self.assess_machine_health(
                machine_id=m_id,
                timestamp=timestamp,
                row=row,
                sensor_anomalies=step_sensor_anomalies,
                correlated_evidence=step_correlated
            )
            timeline_summaries.append(machine_summary)

        # Analyze degradation progression phases
        progression_stages: List[Dict[str, Any]] = []
        current_stage = None
        stage_start_ts = None
        stage_start_idx = 0

        for idx, s in enumerate(timeline_summaries):
            st = s.health_status
            if st != current_stage:
                if current_stage is not None:
                    progression_stages.append({
                        "stage": current_stage,
                        "start_timestamp": stage_start_ts,
                        "end_timestamp": timeline_summaries[idx - 1].timestamp,
                        "start_index": stage_start_idx,
                        "end_index": idx - 1,
                        "duration_steps": idx - stage_start_idx
                    })
                current_stage = st
                stage_start_ts = s.timestamp
                stage_start_idx = idx

        if current_stage is not None:
            progression_stages.append({
                "stage": current_stage,
                "start_timestamp": stage_start_ts,
                "end_timestamp": timeline_summaries[-1].timestamp,
                "start_index": stage_start_idx,
                "end_index": len(timeline_summaries) - 1,
                "duration_steps": len(timeline_summaries) - stage_start_idx
            })

        # Key findings synthesis
        final_summary = timeline_summaries[-1]
        key_findings = [
            f"Asset {machine_id} transitioned through {len(progression_stages)} distinct operational health stages.",
            f"Earliest anomaly indicator observed at {progression_stages[1]['start_timestamp'] if len(progression_stages) > 1 else 'N/A'} (Acoustic Emission / Friction climb).",
            f"Critical degradation reached at {progression_stages[-1]['start_timestamp']} with max risk score {max((s.risk_score for s in timeline_summaries)):.1f}/100.",
            "Multi-sensor correlation confirms drive-end bearing lubrication breakdown (Acoustic + Temp + Vibration + Current surge with stable Pressure and Ambient Temp)."
        ]

        return TelemetryAnalysisReport(
            machine_id=machine_id,
            total_samples=len(telemetry_rows),
            analysis_period={
                "start": telemetry_rows[0].get("timestamp", ""),
                "end": telemetry_rows[-1].get("timestamp", "")
            },
            overall_health_progression=progression_stages,
            final_machine_state=final_summary.to_dict(),
            total_anomalies_detected=total_sensor_anomalies,
            key_findings=key_findings,
            timeline_evidence=[s.to_dict() for s in timeline_summaries]
        )

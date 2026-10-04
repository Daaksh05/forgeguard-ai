"""
ForgeGuard AI — Unit Tests for Sensor Telemetry Anomaly Detection
Tests covering:
- Normal telemetry
- Temperature anomaly
- Vibration anomaly
- Correlated anomalies
- Severity classification
- Machine risk scoring
- Full dataset progression
"""

import unittest
from pathlib import Path

from ai.anomaly_detection.config import (
    DEFAULT_CONFIG,
    SENSOR_THRESHOLDS,
    AnomalyDetectionConfig,
)
from ai.anomaly_detection.detector import (
    AnomalyDetector,
    calculate_baseline,
    compute_rolling_statistics,
    load_telemetry,
)
from ai.anomaly_detection.evidence import (
    CorrelatedEvidence,
    MachineHealthSummary,
    SensorAnomalyEvidence,
)


class TestSensorAnomalyDetector(unittest.TestCase):

    def setUp(self):
        self.detector = AnomalyDetector(DEFAULT_CONFIG)
        self.baseline_stats = {
            "temperature": {"mean": 60.5, "std": 1.0, "min": 59.0, "max": 62.0},
            "vibration": {"mean": 1.8, "std": 0.2, "min": 1.5, "max": 2.1},
            "pressure": {"mean": 5.02, "std": 0.05, "min": 4.95, "max": 5.10},
            "rpm": {"mean": 1770.0, "std": 2.0, "min": 1766.0, "max": 1774.0},
            "current": {"mean": 27.4, "std": 0.3, "min": 27.0, "max": 27.8},
            "ambient_temp": {"mean": 21.5, "std": 0.5, "min": 20.8, "max": 22.2},
            "acoustic_emission": {"mean": 38.0, "std": 1.2, "min": 36.0, "max": 40.0},
        }
        self.rolling_stats = (60.5, 1.0)

    def test_normal_telemetry(self):
        """Verify normal telemetry values produce no anomaly evidence and a HEALTHY machine state."""
        sample_row = {
            "timestamp": "2026-10-04T08:00:00Z",
            "machine_id": "PUMP_001",
            "temperature": 60.5,
            "vibration": 1.8,
            "pressure": 5.02,
            "rpm": 1770.0,
            "current": 27.4,
            "ambient_temp": 21.5,
            "acoustic_emission": 38.0,
            "operating_state": "RUNNING"
        }

        # Check each sensor individually
        for sensor_name, val in sample_row.items():
            if sensor_name in self.baseline_stats:
                ev = self.detector.evaluate_sensor_sample(
                    machine_id="PUMP_001",
                    timestamp=sample_row["timestamp"],
                    sensor_name=sensor_name,
                    value=val,
                    baseline_stats=self.baseline_stats[sensor_name],
                    rolling_stats=(val, 0.1)
                )
                self.assertIsNone(ev, f"Normal sensor {sensor_name} should not trigger an anomaly")

        # Check machine-level assessment
        summary = self.detector.assess_machine_health(
            machine_id="PUMP_001",
            timestamp=sample_row["timestamp"],
            row=sample_row,
            sensor_anomalies=[],
            correlated_evidence=[]
        )
        self.assertEqual(summary.health_status, "HEALTHY")
        self.assertEqual(summary.severity, "NORMAL")
        self.assertEqual(summary.risk_score, 0.0)
        self.assertEqual(len(summary.anomalous_sensors), 0)

    def test_temperature_anomaly_detection(self):
        """Verify alert and critical temperature spikes are detected with proper severity and evidence."""
        # 1. Alert threshold breach (>75.0°C)
        alert_ev = self.detector.evaluate_sensor_sample(
            machine_id="PUMP_001",
            timestamp="2026-10-04T12:00:00Z",
            sensor_name="temperature",
            value=76.5,
            baseline_stats=self.baseline_stats["temperature"],
            rolling_stats=(75.0, 1.2)
        )
        self.assertIsNotNone(alert_ev)
        self.assertEqual(alert_ev.sensor, "temperature")
        self.assertEqual(alert_ev.severity, "HIGH")
        self.assertGreaterEqual(alert_ev.anomaly_score, 65.0)
        self.assertIn("ALERT threshold", alert_ev.evidence)

        # 2. Critical threshold breach (>88.0°C)
        crit_ev = self.detector.evaluate_sensor_sample(
            machine_id="PUMP_001",
            timestamp="2026-10-04T15:00:00Z",
            sensor_name="temperature",
            value=92.0,
            baseline_stats=self.baseline_stats["temperature"],
            rolling_stats=(90.0, 1.5)
        )
        self.assertIsNotNone(crit_ev)
        self.assertEqual(crit_ev.severity, "CRITICAL")
        self.assertGreaterEqual(crit_ev.anomaly_score, 85.0)
        self.assertIn("CRITICAL threshold", crit_ev.evidence)

    def test_vibration_anomaly_detection(self):
        """Verify vibration velocity anomalies trigger per ISO 10816 limits."""
        # Alert (ISO Zone C > 4.5 mm/s)
        vib_alert = self.detector.evaluate_sensor_sample(
            machine_id="PUMP_001",
            timestamp="2026-10-04T13:00:00Z",
            sensor_name="vibration",
            value=4.9,
            baseline_stats=self.baseline_stats["vibration"],
            rolling_stats=(4.5, 0.3)
        )
        self.assertIsNotNone(vib_alert)
        self.assertEqual(vib_alert.severity, "HIGH")

        # Critical (ISO Zone D > 7.1 mm/s)
        vib_crit = self.detector.evaluate_sensor_sample(
            machine_id="PUMP_001",
            timestamp="2026-10-04T15:30:00Z",
            sensor_name="vibration",
            value=8.4,
            baseline_stats=self.baseline_stats["vibration"],
            rolling_stats=(8.0, 0.4)
        )
        self.assertIsNotNone(vib_crit)
        self.assertEqual(vib_crit.severity, "CRITICAL")
        self.assertIn("CRITICAL threshold", vib_crit.evidence)

    def test_correlated_anomalies(self):
        """Verify multi-sensor cross-correlation identifies bearing degradation triad and thermal decoupling."""
        row = {
            "timestamp": "2026-10-04T14:30:00Z",
            "machine_id": "PUMP_001",
            "temperature": 82.0,
            "vibration": 5.8,
            "acoustic_emission": 74.0,
            "current": 33.2,
            "ambient_temp": 22.5,
            "pressure": 5.01
        }

        # Simulated individual sensor anomalies
        anomalies = [
            SensorAnomalyEvidence("PUMP_001", row["timestamp"], "temperature", 82.0, 60.5, 75.0, 75.0, "HIGH", "Temp high", "Friction"),
            SensorAnomalyEvidence("PUMP_001", row["timestamp"], "vibration", 5.8, 1.8, 4.5, 70.0, "HIGH", "Vib high", "Spalling"),
            SensorAnomalyEvidence("PUMP_001", row["timestamp"], "acoustic_emission", 74.0, 38.0, 70.0, 90.0, "CRITICAL", "AE high", "Micro-cracks"),
            SensorAnomalyEvidence("PUMP_001", row["timestamp"], "current", 33.2, 27.4, 31.5, 72.0, "HIGH", "Current high", "Motor drag")
        ]

        corr = self.detector.correlate_anomalies(
            machine_id="PUMP_001",
            timestamp=row["timestamp"],
            row=row,
            sensor_anomalies=anomalies
        )

        pattern_names = [c.pattern_name for c in corr]
        self.assertIn("BEARING_LUBRICATION_DEGRADATION", pattern_names)
        self.assertIn("THERMAL_DECOUPLING", pattern_names)
        self.assertIn("MECHANICAL_VS_HYDRAULIC_ISOLATION", pattern_names)

        bearing_pattern = next(c for c in corr if c.pattern_name == "BEARING_LUBRICATION_DEGRADATION")
        self.assertGreaterEqual(bearing_pattern.correlation_score, 80.0)

    def test_severity_classification(self):
        """Verify severity levels span NORMAL, LOW, MEDIUM, HIGH, CRITICAL correctly."""
        # LOW: Statistical drift only
        low_ev = self.detector.evaluate_sensor_sample(
            machine_id="PUMP_001",
            timestamp="2026-10-04T10:00:00Z",
            sensor_name="acoustic_emission",
            value=43.5,  # Within 32-45 normal band, but Z = (43.5-38.0)/1.2 = 4.58σ
            baseline_stats=self.baseline_stats["acoustic_emission"],
            rolling_stats=(42.0, 1.0)
        )
        self.assertIsNotNone(low_ev)
        self.assertIn(low_ev.severity, ["LOW", "MEDIUM"])

        # MEDIUM: Out of normal range (e.g. 70.0°C for temp)
        med_ev = self.detector.evaluate_sensor_sample(
            machine_id="PUMP_001",
            timestamp="2026-10-04T11:00:00Z",
            sensor_name="temperature",
            value=70.0,
            baseline_stats=self.baseline_stats["temperature"],
            rolling_stats=(69.0, 0.8)
        )
        self.assertIsNotNone(med_ev)
        self.assertEqual(med_ev.severity, "MEDIUM")

        # HIGH: Alert threshold breach
        high_ev = self.detector.evaluate_sensor_sample(
            machine_id="PUMP_001",
            timestamp="2026-10-04T12:00:00Z",
            sensor_name="temperature",
            value=76.0,
            baseline_stats=self.baseline_stats["temperature"],
            rolling_stats=(75.5, 0.8)
        )
        self.assertIsNotNone(high_ev)
        self.assertEqual(high_ev.severity, "HIGH")

        # CRITICAL: Critical threshold breach
        crit_ev = self.detector.evaluate_sensor_sample(
            machine_id="PUMP_001",
            timestamp="2026-10-04T16:00:00Z",
            sensor_name="temperature",
            value=94.0,
            baseline_stats=self.baseline_stats["temperature"],
            rolling_stats=(93.0, 0.8)
        )
        self.assertIsNotNone(crit_ev)
        self.assertEqual(crit_ev.severity, "CRITICAL")

    def test_machine_risk_scoring(self):
        """Verify machine risk score scales dynamically with weighted anomalies and correlation factors."""
        row = {
            "timestamp": "2026-10-04T15:45:00Z",
            "machine_id": "PUMP_001",
            "temperature": 94.0,
            "vibration": 8.5,
            "ambient_temp": 23.0
        }
        anomalies = [
            SensorAnomalyEvidence("PUMP_001", row["timestamp"], "vibration", 8.5, 1.8, 7.1, 95.0, "CRITICAL", "Vib crit", "Spalling"),
            SensorAnomalyEvidence("PUMP_001", row["timestamp"], "temperature", 94.0, 60.5, 88.0, 92.0, "CRITICAL", "Temp crit", "Burnout")
        ]
        corr = self.detector.correlate_anomalies("PUMP_001", row["timestamp"], row, anomalies)

        summary = self.detector.assess_machine_health(
            machine_id="PUMP_001",
            timestamp=row["timestamp"],
            row=row,
            sensor_anomalies=anomalies,
            correlated_evidence=corr
        )

        self.assertEqual(summary.health_status, "SEVERE_DEGRADATION")
        self.assertEqual(summary.severity, "CRITICAL")
        self.assertGreaterEqual(summary.risk_score, 80.0)

    def test_full_dataset_stream_progression(self):
        """Verify detector against synthetic CSV identifies the 3-stage progression correctly."""
        csv_path = Path("data/sensors/pump_001_telemetry.csv")
        self.assertTrue(csv_path.exists(), "Telemetry CSV must exist")

        data = load_telemetry(csv_path)
        self.assertEqual(len(data), 100)

        report = detector_report = self.detector.analyze_stream(data)

        # 1. Verify progression phases
        stages = [s["stage"] for s in report.overall_health_progression]
        self.assertIn("HEALTHY", stages)
        self.assertIn("EARLY_DEGRADATION", stages)
        self.assertIn("SEVERE_DEGRADATION", stages)

        # 2. Verify baseline period (first 30 rows) is primarily healthy (NOT every row flagged anomalous)
        early_health = [s["health_status"] for s in report.timeline_evidence[:30]]
        healthy_count = early_health.count("HEALTHY")
        self.assertGreaterEqual(healthy_count, 28, "Baseline rows must be predominantly HEALTHY")

        # 3. Verify final row is in SEVERE_DEGRADATION with CRITICAL severity
        final_state = report.final_machine_state
        self.assertEqual(final_state["health_status"], "SEVERE_DEGRADATION")
        self.assertEqual(final_state["severity"], "CRITICAL")
        self.assertGreaterEqual(final_state["risk_score"], 80.0)
        self.assertIn("vibration", final_state["anomalous_sensors"])
        self.assertIn("temperature", final_state["anomalous_sensors"])


if __name__ == "__main__":
    unittest.main()

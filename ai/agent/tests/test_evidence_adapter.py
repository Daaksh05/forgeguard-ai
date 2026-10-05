import unittest

from ai.agent.evidence_adapter import adapt_evidence


class TestEvidenceAdapter(unittest.TestCase):
    def test_adapter_keeps_visual_mode_and_handles_missing_modalities(self):
        sensor_report = {
            "machine_id": "PUMP_001",
            "status": "DEGRADED",
            "summary": "Bearing temperature elevated",
            "sensor_anomalies": [{
                "sensor": "temperature",
                "severity": "HIGH",
                "evidence": "Temperature exceeded alert threshold",
                "possible_implication": "Bearing friction is increasing",
                "timestamp": "2026-10-04T12:00:00Z",
            }],
        }
        visual_report = {
            "machine_id": "PUMP_001",
            "mode": "DEMO",
            "summary": "Darkening around seal",
            "findings": [{
                "defect_type": "DEFECT_OIL_LEAK",
                "severity": "MEDIUM",
                "visual_evidence": "Dark fluid with droplet trail",
                "possible_implication": "Lubrication loss",
                "confidence": 0.92,
                "mode": "DEMO",
            }],
        }
        maintenance_report = {
            "query": "bearing lubrication",
            "retrieval_method": "BM25",
            "results": [{
                "source_document": "SOP-MNT-PUMP-042",
                "section": "Re-lubrication Protocol",
                "retrieved_content": "Use polyurea grease NLGI Grade 2.",
                "relevance_score": 0.87,
                "source_path": "data/maintenance_docs/pump_bearing_maintenance.md",
            }],
        }

        agent_input = adapt_evidence(
            machine_id="PUMP_001",
            sensor_report=sensor_report,
            visual_report=visual_report,
            maintenance_report=maintenance_report,
        )

        self.assertEqual(agent_input.machine.machine_id, "PUMP_001")
        self.assertEqual(agent_input.visual_evidence.mode, "DEMO")
        self.assertEqual(agent_input.maintenance_evidence.results[0].source_name, "SOP-MNT-PUMP-042")
        self.assertIn("Temperature exceeded alert threshold", agent_input.sensor_evidence.evidence_items[0].observation)

    def test_missing_modalities_are_graceful(self):
        agent_input = adapt_evidence(
            machine_id="PUMP_002",
            sensor_report={"machine_id": "PUMP_002", "status": "HEALTHY", "summary": "Nominal conditions"},
            visual_report=None,
            maintenance_report={
                "query": "safety",
                "results": [{"source_document": "SOP-001", "section": "Safety", "retrieved_content": "Use LOTO"}],
            },
        )
        self.assertIsNotNone(agent_input.sensor_evidence)
        self.assertIsNone(agent_input.visual_evidence)
        self.assertIsNotNone(agent_input.maintenance_evidence)

    def test_sensor_report_reads_nested_final_state_without_fabricating_values(self):
        sensor_report = {
            "machine_id": "PUMP_001",
            "analysis_period": {"start": "2026-10-04T09:00:00Z", "end": "2026-10-04T15:30:00Z"},
            "final_machine_state": {
                "timestamp": "2026-10-04T15:30:00Z",
                "health_status": "SEVERE_DEGRADATION",
                "severity": "CRITICAL",
                "summary": "Severe bearing degradation.",
                "anomalous_sensors": ["temperature"],
                "sensor_anomalies": [{
                    "machine_id": "PUMP_001",
                    "timestamp": "2026-10-04T15:30:00Z",
                    "sensor": "temperature",
                    "observed_value": 96.51,
                    "anomaly_score": 100.0,
                    "severity": "CRITICAL",
                    "evidence": "Temperature exceeded the emergency threshold.",
                    "possible_implication": "Bearing seizure risk.",
                }],
                "correlated_evidence": [{
                    "pattern_name": "BEARING_LUBRICATION_DEGRADATION",
                    "severity": "CRITICAL",
                    "correlation_score": 100.0,
                    "description": "Thermal and vibration escalation.",
                    "root_cause_hypothesis": "Lubrication breakdown.",
                }],
            },
        }

        agent_input = adapt_evidence(sensor_report=sensor_report)
        sensor_input = agent_input.sensor_evidence
        self.assertEqual(sensor_input.status, "SEVERE_DEGRADATION")
        self.assertEqual(sensor_input.timestamp, "2026-10-04T15:30:00Z")
        self.assertEqual(sensor_input.observed_values, {"temperature": 96.51})
        self.assertEqual(len(sensor_input.evidence_items), 2)
        self.assertEqual(sensor_input.evidence_items[0].confidence, 1.0)


if __name__ == "__main__":
    unittest.main()

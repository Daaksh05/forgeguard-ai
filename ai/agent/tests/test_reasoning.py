import unittest

from ai.agent.evidence_adapter import adapt_evidence
from ai.agent.reasoning import ReasoningEngine


class TestReasoning(unittest.TestCase):
    def test_reasoning_produces_diagnosis_and_actions(self):
        sensor_report = {
            "machine_id": "PUMP_001",
            "status": "DEGRADED",
            "summary": "Temperature and vibration are elevated",
            "sensor_anomalies": [{
                "sensor": "temperature",
                "severity": "HIGH",
                "evidence": "Temperature exceeded alert threshold",
                "possible_implication": "Bearing friction increased",
            }],
        }
        visual_report = {
            "machine_id": "PUMP_001",
            "mode": "DEMO",
            "summary": "Thermal discoloration observed near seal area",
            "findings": [{
                "defect_type": "DEFECT_THERMAL_DISCOLOR",
                "severity": "CRITICAL",
                "visual_evidence": "Severe darkening and blistering",
                "possible_implication": "Thermal damage to housing",
                "confidence": 0.96,
                "mode": "DEMO",
            }],
        }
        maintenance_report = {
            "query": "bearing maintenance",
            "results": [{
                "source_document": "SOP-MNT-PUMP-042",
                "section": "Re-lubrication Protocol",
                "retrieved_content": "Check grease condition and inspect seal integrity before restart.",
                "relevance_score": 0.95,
            }],
        }

        agent_input = adapt_evidence(
            machine_id="PUMP_001",
            sensor_report=sensor_report,
            visual_report=visual_report,
            maintenance_report=maintenance_report,
        )
        output = ReasoningEngine().reason(agent_input)

        self.assertGreaterEqual(output.confidence, 0.5)
        self.assertIn("diagnosis", output.diagnosis.lower())
        self.assertTrue(output.human_approval_required)
        self.assertTrue(len(output.recommended_actions) >= 2)


if __name__ == "__main__":
    unittest.main()

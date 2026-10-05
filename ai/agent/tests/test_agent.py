import unittest

from ai.agent.agent import Agent
from ai.agent.evidence_adapter import adapt_evidence
from ai.agent.run_agent import build_local_demo_evidence


class TestAgent(unittest.TestCase):
    def test_agent_from_evidence(self):
        output = Agent().from_evidence(
            machine_id="PUMP_003",
            sensor_report={
                "machine_id": "PUMP_003",
                "summary": "Mild bearing drift",
                "sensor_anomalies": [{
                    "sensor": "vibration",
                    "severity": "MEDIUM",
                    "evidence": "Vibration above alert threshold",
                    "possible_implication": "Early bearing wear",
                }],
            },
            visual_report={
                "machine_id": "PUMP_003",
                "mode": "REAL",
                "summary": "No major visual defects",
                "findings": [],
            },
            maintenance_report={
                "query": "inspection",
                "results": [{
                    "source_document": "SOP-01",
                    "section": "Inspection",
                    "retrieved_content": "Inspect bearing housing and lubrication fit.",
                    "relevance_score": 0.8,
                }],
            },
        )

        self.assertEqual(output.machine_id, "PUMP_003")
        self.assertTrue(output.human_approval_required)
        self.assertIn("machine", output.reasoning.lower())

    def test_local_demo_consumes_all_existing_phase_evidence(self):
        sensor_report, visual_report, maintenance_report = build_local_demo_evidence()

        self.assertEqual(sensor_report.machine_id, "PUMP_001")
        self.assertTrue(sensor_report.final_machine_state["sensor_anomalies"])
        self.assertEqual(visual_report.mode, "DEMO")
        self.assertTrue(visual_report.findings)
        self.assertTrue(maintenance_report.results)
        self.assertTrue(
            any(
                result.source_document == "SOP-MNT-PUMP-042"
                for result in maintenance_report.results
            )
        )

        agent_input = adapt_evidence(
            sensor_report=sensor_report,
            visual_report=visual_report,
            maintenance_report=maintenance_report,
        )
        output = Agent().analyze(agent_input)

        self.assertEqual(output.machine_id, "PUMP_001")
        self.assertEqual(output.severity, "CRITICAL")
        self.assertEqual(output.metadata["visual_mode"], "DEMO")
        self.assertEqual(
            output.metadata["sources"],
            {"sensor": True, "visual": True, "maintenance": True},
        )
        self.assertGreater(output.metadata["source_details"]["sensor"]["finding_count"], 0)
        self.assertGreater(output.metadata["source_details"]["visual"]["finding_count"], 0)
        self.assertIn(
            "SOP-MNT-PUMP-042",
            output.metadata["source_details"]["maintenance"]["document_ids"],
        )
        evidence = "\n".join(output.evidence)
        self.assertIn("[sensor:", evidence)
        self.assertIn("[visual:", evidence)
        self.assertIn("[maintenance:SOP-MNT-PUMP-042]", evidence)
        self.assertIn("EMERGENCY STOP", "\n".join(output.recommended_actions))
        self.assertTrue(output.human_approval_required)


if __name__ == "__main__":
    unittest.main()

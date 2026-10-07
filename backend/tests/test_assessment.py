import unittest

from fastapi.testclient import TestClient

from backend.app.main import app


class TestEvidenceAndAssessmentEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_anomalies_endpoint_uses_existing_detector(self):
        response = self.client.get("/api/v1/machines/PUMP_001/anomalies")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["machine_id"], "PUMP_001")
        self.assertGreater(payload["total_anomalies_detected"], 0)
        self.assertEqual(payload["final_machine_state"]["severity"], "CRITICAL")

    def test_visual_evidence_is_demo_labeled(self):
        response = self.client.get("/api/v1/machines/PUMP_001/visual-evidence")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["mode"], "DEMO")
        self.assertTrue(payload["findings"])
        self.assertTrue(all(item["mode"] == "DEMO" for item in payload["findings"]))

    def test_maintenance_endpoint_returns_retrieved_evidence(self):
        response = self.client.get("/api/v1/machines/PUMP_001/maintenance")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreater(payload["results_count"], 0)
        self.assertTrue(
            any(result["source_document"] == "SOP-MNT-PUMP-042" for result in payload["results"])
        )

    def test_assessment_invokes_real_pipeline_and_is_retrievable(self):
        response = self.client.post(
            "/api/v1/assessment",
            json={"machine_id": "PUMP_001"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        for field in (
            "machine_id",
            "severity",
            "diagnosis",
            "evidence",
            "reasoning",
            "recommended_actions",
            "human_approval_required",
        ):
            self.assertIn(field, payload)
        self.assertEqual(payload["machine_id"], "PUMP_001")
        self.assertTrue(payload["diagnosis"])
        self.assertTrue(payload["evidence"])
        self.assertTrue(payload["reasoning"])
        self.assertTrue(payload["recommended_actions"])
        self.assertTrue(payload["human_approval_required"])
        self.assertEqual(payload["metadata"]["visual_mode"], "DEMO")

        latest = self.client.get("/api/v1/assessment/PUMP_001")
        self.assertEqual(latest.status_code, 200)
        self.assertEqual(latest.json(), payload)

    def test_latest_assessment_returns_404_before_generation_for_new_service(self):
        from backend.app.services.forgeguard_service import ForgeGuardService

        from backend.app.dependencies import get_forgeguard_service

        service = ForgeGuardService()
        app.dependency_overrides[get_forgeguard_service] = lambda: service
        try:
            response = self.client.get("/api/v1/assessment/PUMP_001")
        finally:
            app.dependency_overrides.clear()
        self.assertEqual(response.status_code, 404)

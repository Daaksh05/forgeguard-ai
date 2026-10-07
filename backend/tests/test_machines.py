import unittest

from fastapi.testclient import TestClient

from backend.app.main import app


class TestMachineEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_machines_are_derived_from_project_data(self):
        response = self.client.get("/api/v1/machines")
        self.assertEqual(response.status_code, 200)
        self.assertIn("PUMP_001", [machine["machine_id"] for machine in response.json()])

    def test_unknown_machine_returns_404(self):
        response = self.client.get("/api/v1/machines/NOT_A_MACHINE")
        self.assertEqual(response.status_code, 404)

    def test_telemetry_uses_dataset_rows(self):
        response = self.client.get("/api/v1/machines/PUMP_001/telemetry?limit=2")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["machine_id"], "PUMP_001")
        self.assertEqual(payload["total"], 100)
        self.assertEqual(len(payload["items"]), 2)
        self.assertEqual(payload["items"][0]["values"]["temperature"], 60.58)

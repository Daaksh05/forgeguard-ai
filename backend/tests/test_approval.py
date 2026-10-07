import unittest

from fastapi.testclient import TestClient

from backend.app.main import app


class TestApprovalEndpoint(unittest.TestCase):
    def test_approval_records_human_decision_only(self):
        response = TestClient(app).post(
            "/api/v1/approval",
            json={
                "machine_id": "PUMP_001",
                "approved": True,
                "operator": "demo_operator",
                "comment": "Approved for maintenance inspection",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "machine_id": "PUMP_001",
                "approved": True,
                "human_decision": True,
            },
        )

    def test_invalid_approval_returns_400(self):
        response = TestClient(app).post(
            "/api/v1/approval",
            json={"machine_id": "", "approved": "yes", "operator": " "},
        )
        self.assertEqual(response.status_code, 400)

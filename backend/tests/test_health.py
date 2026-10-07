import unittest

from fastapi.testclient import TestClient

from backend.app.main import app


class TestHealthEndpoint(unittest.TestCase):
    def test_health(self):
        response = TestClient(app).get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "ok", "service": "forgeguard-api"},
        )

# tests/test_client.py

import unittest
from infinianalytics.register import InfiniAnalytics

class TestInfiniAnalytics(unittest.TestCase):

    def setUp(self):
        # Token y automation_id de prueba (puedes mockear las llamadas a la API)
        self.client = InfiniAnalytics(
            token="randomtoken1",
            automation_id="44444444-4444-4444-4444-444444444444"
        )

    def test_start(self):
        result = self.client.start(description="Test start")
        self.assertIsNotNone(result, "Debería devolver un resultado válido")

    def test_event(self):
        result = self.client.event(description="Test event")
        self.assertIsNotNone(result, "Debería devolver un resultado válido")

    def test_end(self):
        result = self.client.end(description="Test end")
        self.assertIsNotNone(result, "Debería devolver un resultado válido")

    def test_error(self):
        result = self.client.error("desc", "error_id", "detalle del error")
        self.assertIsNotNone(result, "Debería devolver un resultado válido")

if __name__ == "__main__":
    unittest.main()

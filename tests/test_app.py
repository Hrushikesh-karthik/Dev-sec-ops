import os
import tempfile
import unittest

os.environ["DB_PATH"] = os.path.join(tempfile.gettempdir(), "devsecops-workshop-test.db")

from app import app, initialize_database  # noqa: E402


class WorkshopAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_database()

    def setUp(self):
        self.client = app.test_client()

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Build it. Test it. Secure it.", response.data)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_login_page_loads(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()

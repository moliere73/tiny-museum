import os
import tempfile
import unittest
from unittest.mock import patch

import app as museum


class TinyMuseumTest(unittest.TestCase):
    def setUp(self):
        handle, self.db_path = tempfile.mkstemp()
        os.close(handle)
        museum.DATABASE = self.db_path
        museum.app.config.update(TESTING=True, SECRET_KEY="test")
        museum.init_db()
        self.client = museum.app.test_client()

    def tearDown(self):
        os.unlink(self.db_path)

    def test_add_object_and_save_experiment(self):
        response = self.client.post(
            "/objects/new",
            data={"name": "Blue mug", "emoji": "☕", "memory": "A graduation gift", "location": "Kitchen"},
        )
        self.assertEqual(response.status_code, 302)
        object_id = int(response.location.rsplit("/", 1)[-1])
        response = self.client.get(response.location)
        self.assertIn(b"Blue mug", response.data)
        self.assertIn(b"A graduation gift", response.data)

        response = self.client.post(
            "/experiments",
            data={"object_id": object_id, "prompt": "Use it once today.", "observation": "It made tea feel special."},
            follow_redirects=True,
        )
        self.assertIn(b"It made tea feel special.", response.data)

    def test_surprise_requires_an_object(self):
        response = self.client.get("/surprise", follow_redirects=True)
        self.assertIn(b"Add an object first.", response.data)


if __name__ == "__main__":
    unittest.main()


import io
import json
import unittest
from unittest.mock import patch
from urllib.error import URLError

import healthcheck


class HealthcheckTests(unittest.TestCase):
    def test_default_url(self):
        self.assertEqual(healthcheck.validate_base_url("http://127.0.0.1:11434"), healthcheck.DEFAULT_URL)

    def test_reject_external_host(self):
        for url in ("https://example.com:11434", "http://192.168.1.1:11434",
                    "http://127.0.0.1:11434/other", "http://localhost:11434?x=1"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                healthcheck.validate_base_url(url)

    @patch("healthcheck.get_json")
    def test_models(self, mock_get):
        mock_get.side_effect = [{"version": "0.1.0"},
                                {"models": [{"name": "gemma3:latest"}, {"name": "llama3.2:latest"}]}]
        result = healthcheck.check(healthcheck.DEFAULT_URL)
        self.assertTrue(result["healthy"])
        self.assertEqual(result["model_count"], 2)
        self.assertEqual(result["models"], ["gemma3:latest", "llama3.2:latest"])

    @patch("healthcheck.get_json", side_effect=URLError("connection refused"))
    def test_offline(self, mock_get):
        with patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(healthcheck.main([]), 1)


if __name__ == "__main__":
    unittest.main()

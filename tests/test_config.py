import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

from homelab_manager.config import Config


class TestConfig(unittest.TestCase):
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"services": [{"name": "test", "enabled": true, "compose_file": "test.yml"}]}',
    )
    def setUp(self, mock_file):
        self.config = Config("dummy_path.json")

    def test_get_services(self):
        services = self.config.get_services()
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0]["name"], "test")

    def test_is_service_enabled(self):
        self.assertTrue(self.config.is_service_enabled("test"))
        self.assertFalse(self.config.is_service_enabled("nonexistent"))

    def test_get_enabled_services(self):
        enabled = self.config.get_enabled_services()
        self.assertEqual(len(enabled), 1)
        self.assertEqual(enabled[0]["name"], "test")

    def test_get_core_services(self):
        self.config.config["services"].append(
            {"name": "core", "enabled": True, "core": True, "compose_file": "core.yml"}
        )
        core = self.config.get_core_services()
        self.assertEqual(len(core), 1)
        self.assertEqual(core[0]["name"], "core")

    @patch("json.dump")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_config(self, mock_file, mock_json_dump):
        self.config.save_config()
        mock_file.assert_called_once_with(Path("dummy_path.json"), "w")
        mock_json_dump.assert_called_once()


if __name__ == "__main__":
    unittest.main()

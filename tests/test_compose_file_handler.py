import unittest
from unittest.mock import MagicMock, patch

from homelab_manager.compose_file_handler import ComposeFileHandler


class TestComposeFileHandler(unittest.TestCase):
    def setUp(self):
        self.mock_config = MagicMock()
        self.compose_handler = ComposeFileHandler(self.mock_config)

    @patch("requests.get")
    def test_get_compose_file_http(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200, content=b"compose_content")
        self.mock_config.get_services.return_value = [
            {
                "name": "test_service",
                "compose_file": "http://example.com/docker-compose.yml",
            }
        ]

        result = self.compose_handler.get_compose_file("test_service")
        self.assertIsNotNone(result)
        self.assertTrue(result.endswith(".yml"))

    @patch("pathlib.Path.exists")
    def test_get_compose_file_local(self, mock_exists):
        mock_exists.return_value = True
        self.mock_config.get_services.return_value = [
            {"name": "test_service", "compose_file": "local/docker-compose.yml"}
        ]

        result = self.compose_handler.get_compose_file("test_service")
        self.assertIsNotNone(result)
        self.assertTrue(result.endswith("local/docker-compose.yml"))

    @patch("subprocess.run")
    def test_run_docker_compose(self, mock_run):
        mock_run.return_value = MagicMock(stdout="Compose output")
        self.compose_handler.get_compose_file = MagicMock(
            return_value="path/to/docker-compose.yml"
        )

        result = self.compose_handler.run_docker_compose(
            "test_service", ["up", "-d"])
        self.assertTrue(result)
        mock_run.assert_called_once()

    # Add more tests for error cases and other scenarios...


if __name__ == "__main__":
    unittest.main()

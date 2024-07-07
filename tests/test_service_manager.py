import unittest
from unittest.mock import MagicMock, patch

from homelab_manager.service_manager import ServiceManager


class TestServiceManager(unittest.TestCase):
    def setUp(self):
        self.mock_config = MagicMock()
        self.mock_docker_utils = MagicMock()
        self.mock_compose_handler = MagicMock()

        self.service_manager = ServiceManager(self.mock_config)
        self.service_manager.docker_utils = self.mock_docker_utils
        self.service_manager.compose_handler = self.mock_compose_handler

    def test_start_service(self):
        self.mock_config.is_service_enabled.return_value = True
        self.mock_docker_utils.container_is_running.return_value = False
        self.mock_docker_utils.container_exists.return_value = False
        self.mock_compose_handler.run_docker_compose.return_value = True

        result = self.service_manager.start_service("test_service")
        self.assertTrue(result)
        self.mock_compose_handler.run_docker_compose.assert_called_once_with(
            "test_service", ["up", "-d"]
        )

    def test_stop_service(self):
        self.mock_docker_utils.container_exists.return_value = True
        self.mock_compose_handler.run_docker_compose.return_value = True

        result = self.service_manager.stop_service("test_service")
        self.assertTrue(result)
        self.mock_compose_handler.run_docker_compose.assert_called_once_with(
            "test_service", ["down"]
        )

    def test_service_status(self):
        self.mock_docker_utils.container_is_running.return_value = True
        self.mock_docker_utils.container_is_healthy.return_value = True

        status = self.service_manager.service_status("test_service")
        self.assertEqual(status, "Running (Healthy)")

    # Add more tests for other methods...


if __name__ == "__main__":
    unittest.main()

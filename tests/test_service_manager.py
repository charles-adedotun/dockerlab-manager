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

    def test_start_service_success(self):
        self.mock_config.is_service_enabled.return_value = True
        self.mock_compose_handler.get_compose_file.return_value = "path/to/compose.yml"
        self.mock_compose_handler.run_docker_compose.return_value = True

        result = self.service_manager.start_service("test_service")
        self.assertTrue(result)
        self.mock_compose_handler.run_docker_compose.assert_called_once_with(
            "test_service", ["up", "-d"]
        )

    def test_start_service_not_enabled(self):
        self.mock_config.is_service_enabled.return_value = False
        result = self.service_manager.start_service("test_service")
        self.assertFalse(result)

    def test_start_service_no_compose_file(self):
        self.mock_config.is_service_enabled.return_value = True
        self.mock_compose_handler.get_compose_file.return_value = None
        result = self.service_manager.start_service("test_service")
        self.assertFalse(result)

    def test_stop_service_success(self):
        self.mock_compose_handler.get_compose_file.return_value = "path/to/compose.yml"
        self.mock_compose_handler.run_docker_compose.return_value = True

        result = self.service_manager.stop_service("test_service")
        self.assertTrue(result)
        self.mock_compose_handler.run_docker_compose.assert_called_once_with(
            "test_service", ["down"]
        )

    def test_stop_service_no_compose_file(self):
        self.mock_compose_handler.get_compose_file.return_value = None
        result = self.service_manager.stop_service("test_service")
        self.assertFalse(result)

    def test_start_all_services(self):
        self.mock_config.get_enabled_services.return_value = [
            {"name": "service1"},
            {"name": "service2"},
        ]
        self.service_manager.start_service = MagicMock()

        self.service_manager.start_all_services()
        self.assertEqual(self.service_manager.start_service.call_count, 2)

    def test_stop_all_services(self):
        self.mock_config.get_enabled_services.return_value = [
            {"name": "service1"},
            {"name": "service2"},
        ]
        self.service_manager.stop_service = MagicMock()

        self.service_manager.stop_all_services()
        self.assertEqual(self.service_manager.stop_service.call_count, 2)

    def test_service_status_running_healthy(self):
        self.mock_compose_handler.get_compose_file.return_value = "path/to/compose.yml"
        self.mock_docker_utils.container_is_running.return_value = True
        self.mock_docker_utils.container_is_healthy.return_value = True

        status = self.service_manager.service_status("test_service")
        self.assertEqual(status, "Running (Healthy)")

    def test_service_status_running_unhealthy(self):
        self.mock_compose_handler.get_compose_file.return_value = "path/to/compose.yml"
        self.mock_docker_utils.container_is_running.return_value = True
        self.mock_docker_utils.container_is_healthy.return_value = False

        status = self.service_manager.service_status("test_service")
        self.assertEqual(status, "Running (Unhealthy)")

    def test_service_status_stopped(self):
        self.mock_compose_handler.get_compose_file.return_value = "path/to/compose.yml"
        self.mock_docker_utils.container_is_running.return_value = False
        self.mock_docker_utils.container_exists.return_value = True

        status = self.service_manager.service_status("test_service")
        self.assertEqual(status, "Stopped")

    def test_service_status_not_running(self):
        self.mock_compose_handler.get_compose_file.return_value = "path/to/compose.yml"
        self.mock_docker_utils.container_is_running.return_value = False
        self.mock_docker_utils.container_exists.return_value = False

        status = self.service_manager.service_status("test_service")
        self.assertEqual(status, "Not running")

    def test_all_services_status(self):
        self.mock_config.get_services.return_value = [
            {"name": "service1"},
            {"name": "service2"},
        ]
        self.service_manager.service_status = MagicMock(
            side_effect=["Running (Healthy)", "Stopped"]
        )

        statuses = self.service_manager.all_services_status()
        self.assertEqual(
            statuses, {"service1": "Running (Healthy)", "service2": "Stopped"}
        )

    def test_check_all_services_healthy(self):
        self.mock_config.get_enabled_services.return_value = [
            {"name": "service1"},
            {"name": "service2"},
        ]
        self.service_manager.service_status = MagicMock(
            side_effect=["Running (Healthy)", "Running (Unhealthy)"]
        )

        result = self.service_manager.check_all_services_healthy()
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()

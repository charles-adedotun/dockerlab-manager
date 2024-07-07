import subprocess
import unittest
from unittest.mock import MagicMock, patch

from homelab_manager.service_manager import ServiceManager


class TestServiceManager(unittest.TestCase):
    def setUp(self):
        self.mock_config = MagicMock()
        self.mock_config.is_service_enabled.return_value = True
        self.mock_config.get_services.return_value = [
            {
                "name": "test_service",
                "enabled": True,
                "compose_file": "./test_service/docker-compose.yml",
            }
        ]
        self.mock_config.get_enabled_services.return_value = (
            self.mock_config.get_services.return_value
        )
        self.manager = ServiceManager(self.mock_config)

    @patch("homelab_manager.service_manager.Path.exists")
    def test_get_compose_file(self, mock_exists):
        mock_exists.return_value = True
        result = self.manager.get_compose_file("test_service")
        self.assertIsNotNone(result)
        mock_exists.return_value = False
        result = self.manager.get_compose_file("nonexistent")
        self.assertIsNone(result)

    @patch("homelab_manager.service_manager.subprocess.run")
    def test_run_docker_compose_success(self, mock_run):
        with patch.object(self.manager, "get_compose_file", return_value="dummy_path"):
            mock_run.return_value.returncode = 0
            result = self.manager.run_docker_compose(
                "test_service", ["up", "-d"])
            self.assertTrue(result)
            mock_run.assert_called_once()

    @patch("homelab_manager.service_manager.subprocess.run")
    def test_run_docker_compose_failure(self, mock_run):
        with patch.object(self.manager, "get_compose_file", return_value="dummy_path"):
            mock_run.side_effect = subprocess.CalledProcessError(1, "cmd")
            result = self.manager.run_docker_compose(
                "test_service", ["up", "-d"])
            self.assertFalse(result)

    @patch("homelab_manager.service_manager.subprocess.run")
    def test_start_service(self, mock_run):
        with patch.object(self.manager, "get_compose_file", return_value="dummy_path"):
            mock_run.return_value.returncode = 0
            self.assertTrue(self.manager.start_service("test_service"))
            mock_run.assert_called_once()

    @patch("homelab_manager.service_manager.subprocess.run")
    def test_stop_service(self, mock_run):
        with patch.object(self.manager, "get_compose_file", return_value="dummy_path"):
            mock_run.return_value.returncode = 0
            self.assertTrue(self.manager.stop_service("test_service"))
            mock_run.assert_called_once()

    @patch.object(ServiceManager, "start_service")
    def test_start_all_services(self, mock_start):
        mock_start.return_value = True
        self.manager.start_all_services()
        mock_start.assert_called_once_with("test_service")

    @patch.object(ServiceManager, "stop_service")
    def test_stop_all_services(self, mock_stop):
        mock_stop.return_value = True
        self.manager.stop_all_services()
        mock_stop.assert_called_once_with("test_service")

    @patch("homelab_manager.service_manager.subprocess.run")
    def test_service_status_running(self, mock_run):
        with patch.object(self.manager, "get_compose_file", return_value="dummy_path"):
            mock_run.return_value.stdout = "test_service"
            status = self.manager.service_status("test_service")
            self.assertEqual(status, "Running")

    @patch("homelab_manager.service_manager.subprocess.run")
    def test_service_status_stopped(self, mock_run):
        with patch.object(self.manager, "get_compose_file", return_value="dummy_path"):
            mock_run.return_value.stdout = ""
            status = self.manager.service_status("test_service")
            self.assertEqual(status, "Stopped")

    @patch("homelab_manager.service_manager.subprocess.run")
    def test_service_status_error(self, mock_run):
        with patch.object(self.manager, "get_compose_file", return_value="dummy_path"):
            mock_run.side_effect = subprocess.CalledProcessError(1, "cmd")
            status = self.manager.service_status("test_service")
            self.assertEqual(status, "Error")

    @patch.object(ServiceManager, "service_status")
    def test_all_services_status(self, mock_status):
        mock_status.return_value = "Running"
        statuses = self.manager.all_services_status()
        self.assertEqual(statuses, {"test_service": "Running"})
        mock_status.assert_called_once_with("test_service")


if __name__ == "__main__":
    unittest.main()

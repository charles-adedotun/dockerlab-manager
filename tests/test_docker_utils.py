import subprocess
import unittest
from unittest.mock import MagicMock, patch

from homelab_manager.docker_utils import DockerUtils


class TestDockerUtils(unittest.TestCase):
    def setUp(self):
        self.docker_utils = DockerUtils()

    @patch("shutil.which")
    def test_get_docker_compose_cmd(self, mock_which):
        mock_which.side_effect = [None, "/usr/bin/docker"]
        cmd = self.docker_utils._get_docker_compose_cmd()
        self.assertEqual(cmd, ["docker", "compose"])

        mock_which.side_effect = ["/usr/bin/docker-compose", None]
        cmd = self.docker_utils._get_docker_compose_cmd()
        self.assertEqual(cmd, ["docker-compose"])

        mock_which.side_effect = [None, None]
        with self.assertRaises(RuntimeError):
            self.docker_utils._get_docker_compose_cmd()

    @patch("subprocess.run")
    def test_container_exists(self, mock_run):
        mock_run.return_value = MagicMock(stdout="container_name")
        self.assertTrue(self.docker_utils.container_exists("container_name"))

        mock_run.return_value = MagicMock(stdout="")
        self.assertFalse(
            self.docker_utils.container_exists("nonexistent_container"))

        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd")
        self.assertFalse(self.docker_utils.container_exists("error_container"))

    @patch("subprocess.run")
    def test_container_is_running(self, mock_run):
        mock_run.return_value = MagicMock(stdout="container_name")
        self.assertTrue(
            self.docker_utils.container_is_running("container_name"))

        mock_run.return_value = MagicMock(stdout="")
        self.assertFalse(
            self.docker_utils.container_is_running("stopped_container"))

        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd")
        self.assertFalse(
            self.docker_utils.container_is_running("error_container"))

    @patch("subprocess.run")
    def test_container_is_healthy(self, mock_run):
        mock_run.return_value = MagicMock(stdout="healthy")
        self.assertTrue(
            self.docker_utils.container_is_healthy("healthy_container"))

        mock_run.return_value = MagicMock(stdout="unhealthy")
        self.assertFalse(
            self.docker_utils.container_is_healthy("unhealthy_container"))

        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd")
        self.assertFalse(
            self.docker_utils.container_is_healthy("error_container"))

    @patch("subprocess.run")
    def test_remove_container(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(
            self.docker_utils.remove_container("container_to_remove"))

        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd")
        self.assertFalse(self.docker_utils.remove_container("error_container"))


if __name__ == "__main__":
    unittest.main()

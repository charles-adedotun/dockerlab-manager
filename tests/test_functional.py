import json
import os
import tempfile
import time
import unittest

from click.testing import CliRunner

from homelab_manager.cli import cli


class TestFunctional(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create temporary docker-compose files
        cls.temp_dir = tempfile.mkdtemp()

        # Redis service
        redis_compose = os.path.join(cls.temp_dir, "redis-compose.yml")
        with open(redis_compose, "w") as f:
            f.write(
                """
version: '3'
services:
  redis:
    image: redis:alpine
    ports:
      - "6379"
"""
            )

        # Nginx service
        nginx_compose = os.path.join(cls.temp_dir, "nginx-compose.yml")
        with open(nginx_compose, "w") as f:
            f.write(
                """
version: '3'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80"
"""
            )

        # Create config file
        cls.config_path = os.path.join(cls.temp_dir, "config.json")
        config = {
            "services": [
                {"name": "redis", "enabled": True, "compose_file": redis_compose},
                {"name": "nginx", "enabled": True, "compose_file": nginx_compose},
            ]
        }
        with open(cls.config_path, "w") as f:
            json.dump(config, f)

        # Set environment variable for the config file
        os.environ["HOMELAB_CONFIG"] = cls.config_path

    @classmethod
    def tearDownClass(cls):
        # Clean up temporary files
        os.remove(cls.config_path)
        for file in os.listdir(cls.temp_dir):
            os.remove(os.path.join(cls.temp_dir, file))
        os.rmdir(cls.temp_dir)

    def setUp(self):
        self.runner = CliRunner()

    def test_start_stop_single_service(self):
        # Start Redis
        result = self.runner.invoke(cli, ["start", "redis"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Service redis started successfully", result.output)

        # Check status
        result = self.runner.invoke(cli, ["status"])
        self.assertIn("redis: Running", result.output)
        self.assertIn("nginx: Stopped", result.output)

        # Stop Redis
        result = self.runner.invoke(cli, ["stop", "redis"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Service redis stopped successfully", result.output)

        # Check status again
        result = self.runner.invoke(cli, ["status"])
        self.assertIn("redis: Stopped", result.output)
        self.assertIn("nginx: Stopped", result.output)

    def test_start_stop_all_services(self):
        # Start all services
        result = self.runner.invoke(cli, ["start-all"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("All enabled services have been started", result.output)

        # Wait for services to start
        time.sleep(5)

        # Check status

        result = self.runner.invoke(cli, ["status"])
        self.assertIn("redis: Running", result.output)
        self.assertIn("nginx: Running", result.output)

        # Stop all services
        result = self.runner.invoke(cli, ["stop-all"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("All services have been stopped", result.output)

        # Check status again
        result = self.runner.invoke(cli, ["status"])
        self.assertIn("redis: Stopped", result.output)
        self.assertIn("nginx: Stopped", result.output)

    def test_service_not_found(self):
        result = self.runner.invoke(cli, ["start", "nonexistent"])
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Service nonexistent is not enabled", result.output)

    def test_invalid_command(self):
        result = self.runner.invoke(cli, ["invalid-command"])
        self.assertEqual(result.exit_code, 2)
        self.assertIn("No such command 'invalid-command'", result.output)


if __name__ == "__main__":
    unittest.main()

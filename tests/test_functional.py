import os
import subprocess
import time
import unittest

from click.testing import CliRunner

from homelab_manager.cli import cli
from homelab_manager.config import Config


class TestFunctional(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_path = os.path.abspath("test_config.json")
        os.environ["HOMELAB_CONFIG"] = cls.config_path

        cls.config = Config(cls.config_path)

        cls.services = {
            s["name"]: s for s in cls.config.get_services() if s["enabled"]}
        cls.core_services = [
            s["name"]
            for s in cls.config.get_services()
            if s.get("core", False) and s["enabled"]
        ]
        cls.non_core_services = [
            s["name"]
            for s in cls.config.get_services()
            if not s.get("core", False) and s["enabled"]
        ]

        cls.initially_running = cls.get_running_services()

        # Check if Docker is running
        try:
            subprocess.run(["docker", "info"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            raise unittest.SkipTest(
                "Docker is not running. Skipping functional tests.")

    @classmethod
    def tearDownClass(cls):
        cls.stop_test_services()

    def setUp(self):
        self.runner = CliRunner()

    @classmethod
    def get_running_services(cls):
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True
        )
        return (set(result.stdout.strip().split("\n"))
                if result.stdout.strip() else set())

    @classmethod
    def stop_test_services(cls):
        current_running = cls.get_running_services()
        services_to_stop = current_running - cls.initially_running
        for service in services_to_stop:
            subprocess.run(["docker", "stop", service], check=True)
            subprocess.run(["docker", "rm", service], check=True)

    def test_start_stop_core_services(self):
        for service in self.core_services:
            result = self.runner.invoke(cli, ["start", service])
            print(f"Start output for {service}: {result.output}")
            self.assertEqual(
                result.exit_code,
                0,
                f"Start command failed for {service} with output: {result.output}",
            )
            self.assertIn(
                f"Service {service} started successfully",
                result.output)

        time.sleep(5)  # Give services time to start up

        result = self.runner.invoke(cli, ["status"])
        print(f"Status output: {result.output}")
        for service in self.core_services:
            self.assertIn(
                f"{service}: Running",
                result.output,
                f"Service {service} is not running. Full status output: {result.output}",
            )

        for service in self.core_services:
            result = self.runner.invoke(cli, ["stop", service])
            print(f"Stop output for {service}: {result.output}")
            self.assertEqual(
                result.exit_code,
                0,
                f"Stop command failed for {service} with output: {result.output}",
            )
            self.assertIn(
                f"Service {service} stopped successfully",
                result.output)

        result = self.runner.invoke(cli, ["status"])
        print(f"Final status output: {result.output}")
        for service in self.core_services:
            self.assertIn(
                f"{service}: Stopped",
                result.output,
                f"Service {service} is not stopped. Full status output: {result.output}",
            )

    def test_start_stop_all_services(self):
        result = self.runner.invoke(cli, ["start-all"])
        print(f"Start-all output: {result.output}")
        self.assertEqual(
            result.exit_code,
            0,
            f"Start-all command failed with output: {result.output}",
        )
        self.assertIn("All enabled services have been started", result.output)

        time.sleep(5)  # Give services time to start up

        result = self.runner.invoke(cli, ["status"])
        print(f"Status after start-all: {result.output}")
        for service in self.services:
            self.assertIn(
                f"{service}: Running",
                result.output,
                f"Service {service} is not running. Full status output: {result.output}",
            )

        result = self.runner.invoke(cli, ["stop-all"])
        print(f"Stop-all output: {result.output}")
        self.assertEqual(
            result.exit_code,
            0,
            f"Stop-all command failed with output: {result.output}")
        self.assertIn("All services have been stopped", result.output)

        result = self.runner.invoke(cli, ["status"])
        print(f"Final status output: {result.output}")
        for service in self.services:
            self.assertIn(
                f"{service}: Stopped",
                result.output,
                f"Service {service} is not stopped. Full status output: {result.output}",
            )

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

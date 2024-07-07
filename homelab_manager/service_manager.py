import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import requests


class ServiceManager:
    def __init__(self, config):
        self.config = config
        self.base_dir = Path(
            os.path.dirname(
                os.path.abspath(
                    self.config.config_path)))
        self.docker_compose_cmd = self._get_docker_compose_cmd()
        self.temp_files = {}

    def _get_docker_compose_cmd(self):
        if shutil.which("docker-compose"):
            return ["docker-compose"]
        elif shutil.which("docker"):
            return ["docker", "compose"]
        else:
            raise RuntimeError(
                "Neither docker-compose nor docker compose found. Please install Docker Compose."
            )

    def get_compose_file(self, service_name):
        service = next((s for s in self.config.get_services()
                        if s["name"] == service_name), None)
        if not service:
            return None

        compose_file = service["compose_file"]
        if compose_file.startswith("http"):
            if service_name not in self.temp_files:
                response = requests.get(compose_file)
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".yml"
                    ) as tmp_file:
                        tmp_file.write(response.content)
                        self.temp_files[service_name] = tmp_file.name
                else:
                    print(
                        f"Failed to download docker-compose file for {service_name}")
                    return None
            return self.temp_files[service_name]
        else:
            full_path = self.base_dir / compose_file
            if full_path.exists():
                return str(full_path)
            else:
                print(f"Compose file not found: {full_path}")
                return None

    def run_docker_compose(self, service_name, command):
        compose_file = self.get_compose_file(service_name)
        if not compose_file:
            print(f"docker-compose file not found for service {service_name}")
            return False

        try:
            result = subprocess.run(
                self.docker_compose_cmd + ["-f", compose_file] + command,
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"Command output: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Docker compose command failed for {service_name}: {e}")
            print(f"Error output: {e.stdout}")
            print(f"Error: {e.stderr}")
            return False

    def start_service(self, service_name):
        if not self.config.is_service_enabled(service_name):
            print(f"Service {service_name} is not enabled.")
            return False
        return self.run_docker_compose(service_name, ["up", "-d"])

    def stop_service(self, service_name):
        return self.run_docker_compose(service_name, ["down"])

    def start_all_services(self):
        for service in self.config.get_enabled_services():
            self.start_service(service["name"])

    def stop_all_services(self):
        for service in reversed(self.config.get_enabled_services()):
            self.stop_service(service["name"])

    def service_status(self, service_name):
        compose_file = self.get_compose_file(service_name)
        if not compose_file:
            return "Not configured"

        try:
            result = subprocess.run(
                self.docker_compose_cmd
                + [
                    "-f",
                    compose_file,
                    "ps",
                    "--services",
                    "--filter",
                    "status=running",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return "Running" if service_name in result.stdout else "Stopped"
        except subprocess.CalledProcessError as e:
            print(f"Error checking status for {service_name}: {e}")
            print(f"Error output: {e.stdout}")
            print(f"Error: {e.stderr}")
            return "Error"

    def all_services_status(self):
        return {
            service["name"]: self.service_status(service["name"])
            for service in self.config.get_services()
        }

    def __del__(self):
        for tmp_file in self.temp_files.values():
            if os.path.exists(tmp_file):
                os.unlink(tmp_file)

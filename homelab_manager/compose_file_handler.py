import os
import subprocess
import tempfile
from pathlib import Path

import requests


class ComposeFileHandler:
    def __init__(self, config):
        self.config = config
        self.base_dir = Path(
            os.path.dirname(
                os.path.abspath(
                    self.config.config_path)))
        self.temp_files = {}

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
                ["docker-compose", "-f", compose_file] + command + ["--remove-orphans"],
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

    def __del__(self):
        for tmp_file in self.temp_files.values():
            if os.path.exists(tmp_file):
                os.unlink(tmp_file)

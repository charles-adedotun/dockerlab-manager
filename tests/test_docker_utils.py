import shutil
import subprocess


class DockerUtils:
    def __init__(self):
        self.docker_compose_cmd = self._get_docker_compose_cmd()

    def _get_docker_compose_cmd(self):
        if shutil.which("docker-compose"):
            return ["docker-compose"]
        elif shutil.which("docker"):
            return ["docker", "compose"]
        else:
            raise RuntimeError(
                "Neither docker-compose nor docker compose found. Please install Docker Compose."
            )

    def container_exists(self, service_name):
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "-a",
                    "--filter",
                    f"name=^/{service_name}$",
                    "--format",
                    "{{.Names}}",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False

    def container_is_running(self, service_name):
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    f"name=^/{service_name}$",
                    "--format",
                    "{{.Names}}",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False

    def container_is_healthy(self, service_name):
        try:
            result = subprocess.run(
                [
                    "docker",
                    "inspect",
                    "--format",
                    "{{.State.Health.Status}}",
                    service_name,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip() == "healthy"
        except subprocess.CalledProcessError:
            return False

    def remove_container(self, service_name):
        try:
            subprocess.run(["docker", "rm", "-f", service_name],
                           check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False

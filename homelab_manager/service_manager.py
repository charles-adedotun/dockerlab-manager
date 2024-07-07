from .compose_file_handler import ComposeFileHandler
from .docker_utils import DockerUtils


class ServiceManager:
    def __init__(self, config):
        self.config = config
        self.docker_utils = DockerUtils()
        self.compose_handler = ComposeFileHandler(config)

    def start_service(self, service_name):
        if not self.config.is_service_enabled(service_name):
            print(f"Service {service_name} is not enabled.")
            return False

        compose_file = self.compose_handler.get_compose_file(service_name)
        if not compose_file:
            print(f"Compose file for {service_name} not found.")
            return False

        success = self.compose_handler.run_docker_compose(
            service_name, ["up", "-d"])
        if success:
            print(f"Service {service_name} started successfully.")
        return success

    def stop_service(self, service_name):
        compose_file = self.compose_handler.get_compose_file(service_name)
        if not compose_file:
            print(f"Compose file for {service_name} not found.")
            return False

        success = self.compose_handler.run_docker_compose(
            service_name, ["down"])
        if success:
            print(f"Service {service_name} stopped successfully.")
        return success

    def start_all_services(self):
        for service in self.config.get_enabled_services():
            self.start_service(service["name"])

    def stop_all_services(self):
        for service in reversed(self.config.get_enabled_services()):
            self.stop_service(service["name"])

    def service_status(self, service_name):
        compose_file = self.compose_handler.get_compose_file(service_name)
        if not compose_file:
            return "Not configured"

        if self.docker_utils.container_is_running(service_name):
            if self.docker_utils.container_is_healthy(service_name):
                return "Running (Healthy)"
            else:
                return "Running (Unhealthy)"
        elif self.docker_utils.container_exists(service_name):
            return "Stopped"
        else:
            return "Not running"

    def all_services_status(self):
        return {
            service["name"]: self.service_status(service["name"])
            for service in self.config.get_services()
        }

    def check_all_services_healthy(self):
        all_healthy = True
        for service in self.config.get_enabled_services():
            status = self.service_status(service["name"])
            if status != "Running (Healthy)":
                print(
                    f"Service {service['name']} is not healthy. Status: {status}")
                all_healthy = False
        return all_healthy

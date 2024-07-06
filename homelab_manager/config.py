import json
from pathlib import Path


class Config:
    def __init__(self, config_path="config.json"):
        self.config_path = Path(config_path)
        self.load_config()

    def load_config(self):
        with open(self.config_path, "r") as f:
            self.config = json.load(f)

    def save_config(self):
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def get_services(self):
        return self.config["services"]

    def is_service_enabled(self, service_name):
        return any(s["name"] == service_name and s["enabled"]
                   for s in self.get_services())

    def get_enabled_services(self):
        return [s for s in self.get_services() if s["enabled"]]

    def get_core_services(self):
        return [
            s for s in self.get_services() if s.get(
                "core", False) and s["enabled"]]

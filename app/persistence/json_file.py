import json
from typing import Dict, Any
from app.models.route import FakeRoute
from app.interfaces.route_interface import RouteInterface
import os

class JSONFilePersistence(RouteInterface):
    def remove_route(self, name):
        if name in self.routes:
            del self.routes[name]
            self._save_routes()
    def __init__(self, file_path: str = "routes.json"):
        self.file_path = file_path
        self.routes: Dict[str, FakeRoute] = {}
        self._load_routes()

    def _load_routes(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                data = json.load(f)
                for name, route_data in data.items():
                    self.routes[name] = FakeRoute(**route_data)

    def _save_routes(self):
        with open(self.file_path, "w") as f:
            json.dump({name: route.dict() for name, route in self.routes.items()}, f, indent=2)

    def add_route(self, name, return_value, status_code=200, headers=None, delay=0.0):
        route = FakeRoute(name=name, return_value=return_value, status_code=status_code, headers=headers, delay=delay)
        self.routes[name] = route
        self._save_routes()

    def get_route(self, name):
        return self.routes.get(name)

    def list_routes(self):
        return {name: route.dict() for name, route in self.routes.items()}

    def clear_routes(self):
        self.routes.clear()
        self._save_routes()

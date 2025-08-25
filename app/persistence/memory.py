from typing import Dict
from app.models.route import FakeRoute
from app.interfaces.route_interface import RouteInterface

class MemoryPersistence(RouteInterface):
    def remove_route(self, name):
        if name in self.routes:
            del self.routes[name]
    def __init__(self):
        self.routes: Dict[str, FakeRoute] = {}

    def add_route(self, name, return_value, status_code=200, headers=None, delay=0.0):
        route = FakeRoute(name=name, return_value=return_value, status_code=status_code, headers=headers, delay=delay)
        self.routes[name] = route

    def get_route(self, name):
        return self.routes.get(name)

    def list_routes(self):
        return {name: route.dict() for name, route in self.routes.items()}

    def clear_routes(self):
        self.routes.clear()

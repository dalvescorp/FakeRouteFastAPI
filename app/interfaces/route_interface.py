from abc import ABC, abstractmethod
from typing import Any, Dict

class RouteInterface(ABC):
    @abstractmethod
    def remove_route(self, name: str):
        pass
    @abstractmethod
    def add_route(self, name: str, return_value: Dict[str, Any], status_code: int = 200, headers: Dict[str, str] = None, delay: float = 0.0):
        pass

    @abstractmethod
    def get_route(self, name: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def list_routes(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def clear_routes(self):
        pass

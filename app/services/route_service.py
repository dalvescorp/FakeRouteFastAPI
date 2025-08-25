from app.persistence.memory import MemoryPersistence
from app.models.route import FakeRoute

class RouteService:
    def remove_route(self, name):
        self.persistence.remove_route(name)
    def __init__(self):
        self.persistence = MemoryPersistence()

    def create_route(self, data):
        # Extrai os campos do JSON recebido
        name = data.get("name")
        # require 'return' field
        if data.get("return") is None:
            raise ValueError("Campo 'return' é obrigatório ao criar rota")
        return_value = data.get("return")
        status_code = data.get("status_code", 200)
        headers = data.get("headers")
        delay = data.get("delay", 0.0)
        self.persistence.add_route(name, return_value, status_code, headers, delay)
        return {"message": "Rota criada", "route": {
            "name": name,
            "return": return_value,
            "status_code": status_code,
            "headers": headers,
            "delay": delay
        }}

    def list_routes(self):
        return self.persistence.list_routes()

    def clear_routes(self):
        self.persistence.clear_routes()

route_service = RouteService()

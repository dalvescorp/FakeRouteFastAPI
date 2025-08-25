import asyncio
from fastapi import Request
from fastapi.responses import JSONResponse

def add_dynamic_route(app, name, route):
    # require 'return' key
    if route.get("return") is None:
        raise ValueError("Entrada inválida: campo 'return' obrigatorio para rota dinâmica")
    return_value = route.get("return")
    status_code = route.get("status_code", 200)
    headers = route.get("headers")
    delay = route.get("delay", 0.0)

    def make_endpoint(return_value, status_code, headers, delay):
        async def endpoint():
            if delay:
                await asyncio.sleep(delay)
            response_headers = headers or {}
            return JSONResponse(content=return_value, status_code=status_code, headers=response_headers)
        return endpoint

    app.add_api_route(name, make_endpoint(return_value, status_code, headers, delay), methods=["GET"])

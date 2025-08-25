import base64
from fastapi import FastAPI, Request
from starlette.responses import Response
import asyncio

from app.core.config import config
from app.api.routes import router

import os
import aiofiles
import json

app = FastAPI(title=config.API_TITLE)
app.include_router(router)

USERNAME = config.SWAGGER_USERNAME
PASSWORD = config.SWAGGER_PASSWORD


@app.middleware("http")
async def docs_basic_auth_middleware(request: Request, call_next):
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Basic "):
            return Response("Unauthorized", status_code=401, headers={"WWW-Authenticate": "Basic"})
        encoded = auth.split(" ")[1]
        try:
            decoded = base64.b64decode(encoded).decode()
            user, pwd = decoded.split(":", 1)
        except Exception:
            return Response("Unauthorized", status_code=401, headers={"WWW-Authenticate": "Basic"})
        if user != USERNAME or pwd != PASSWORD:
            return Response("Unauthorized", status_code=401, headers={"WWW-Authenticate": "Basic"})
    return await call_next(request)


async def load_and_register_fakes():
    FAKES_FILE = config.FAKES_FILE

    # 🔐 Garante que o diretório exista
    os.makedirs(os.path.dirname(FAKES_FILE), exist_ok=True)

    # 📄 Cria o arquivo vazio se não existir
    if not os.path.exists(FAKES_FILE):
        async with aiofiles.open(FAKES_FILE, "w") as f:
            await f.write("[]")

    # 📖 Lê conteúdo do JSON
    async with aiofiles.open(FAKES_FILE, "r") as f:
        content = await f.read()
        fakes = json.loads(content or "[]")

    # 🚀 Registra as rotas dinamicamente
    for fake in fakes:
        if "methods" not in fake:
            raise ValueError(f"Campo obrigatório 'methods' ausente na rota: {fake.get('name', '<sem nome>')}")

        if fake.get("return") is None:
            raise ValueError(f"Rota inválida: campo 'return' ausente na rota: {fake.get('name', '<sem nome>')}")

        def make_fake_endpoint(return_value, status_code, headers, delay):
            async def endpoint():
                if delay:
                    await asyncio.sleep(delay)
                response_headers = headers or {}
                return __import__("fastapi").responses.JSONResponse(content=return_value, status_code=status_code, headers=response_headers)
            return endpoint

        return_value = fake["return"]
        app.add_api_route(
            fake["name"],
            make_fake_endpoint(
                return_value,
                fake.get("status_code", 200),
                fake.get("headers"),
                fake.get("delay", 0.0)
            ),
            methods=fake["methods"],
            response_model=dict,
            tags=["Fake"]
        )


@app.on_event("startup")
async def on_startup():
    await load_and_register_fakes()


@app.get("/health")
async def health():
    return {"status": "ok"}

import base64
import asyncio
import json
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.responses import Response
import aiofiles

from app.core.config import config
from app.api.routes import router

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


def make_fake_endpoint(return_value, status_code, headers, delay):
    async def endpoint():
        if delay:
            await asyncio.sleep(delay)
        response_headers = headers or {}
        return JSONResponse(content=return_value, status_code=status_code, headers=response_headers)
    return endpoint


async def load_and_register_fakes():
    FAKES_FILE = config.FAKES_FILE

    os.makedirs(os.path.dirname(FAKES_FILE), exist_ok=True)

    if not os.path.exists(FAKES_FILE):
        async with aiofiles.open(FAKES_FILE, "w") as f:
            await f.write("[]")

    async with aiofiles.open(FAKES_FILE, "r") as f:
        content = await f.read()
        fakes = json.loads(content or "[]")

    for fake in fakes:
        name = fake.get("name")
        methods = fake.get("methods", ["GET"])
        return_value = fake.get("return", {})
        status_code = fake.get("status_code", 200)
        headers = fake.get("headers", {})
        delay = fake.get("delay", 0.0)

        if not name or not return_value:
            print(f"[⚠️] Ignorando rota inválida: {fake}")
            continue

        app.add_api_route(
            name,
            endpoint=make_fake_endpoint(return_value, status_code, headers, delay),
            methods=methods,
            response_model=dict,
            tags=["Fake"]
        )

@app.on_event("startup")
async def on_startup():
    await load_and_register_fakes()


@app.get("/health")
async def health():
    return {"status": "ok"}

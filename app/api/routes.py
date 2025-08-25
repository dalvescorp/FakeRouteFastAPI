import json
import os
import aiofiles
import asyncio
from fastapi import APIRouter, Request, Body, status, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List
from app.services.route_service import route_service
from app.core.config import config # Importando o config

# FAKES_FILE = os.path.join(os.path.dirname(__file__), "../fakes.json") # Linha removida/comentada
router = APIRouter()

def normalize_path(path: str) -> str:
	return path if path.startswith("/") else f"/{path}"

class FakeRouteCreate(BaseModel):
	name: str
	# use `return` as the external field name, map to `return_value` internally
	return_value: Dict[str, Any] = Field(..., alias="return")
	status_code: int = 200
	headers: Optional[Dict[str, str]] = None
	delay: float = 0.0
	methods: List[str]

	class Config:
		json_schema_extra = {
			"example": {
				"name": "/meu-exemplo",
				"return": {
					"status": "ok",
					"dados": [1, 2, 3],
					"mensagem": "Esta é uma resposta fake personalizada!"
				},
				"status_code": 201,
				"headers": {
					"X-Custom-Header": "valor"
				},
				"delay": 1.0,
				"methods": ["GET"]
			}
		}

def register_fake_route(app, fake):
	# require new key \'return\'
	if fake.get("return") is None:
		raise ValueError("Rota inválida: campo \'return\' obrigatório")
	return_value = fake.get("return")
	status_code = fake.get("status_code", 200)
	headers = fake.get("headers")
	delay = fake.get("delay", 0.0)

	def make_fake_endpoint(return_value, status_code, headers, delay):
		async def endpoint():
			if delay:
				await asyncio.sleep(delay)
			response_headers = headers or {}
			return JSONResponse(content=return_value, status_code=status_code, headers=response_headers)
		return endpoint

	app.add_api_route(
		fake["name"],
		make_fake_endpoint(return_value, status_code, headers, delay),
		methods=fake["methods"],
		response_model=dict,
		tags=["Fake"]
	)

@router.post("/populate-fakes", tags=["Admin"])
async def populate_fakes(fakes: List[FakeRouteCreate] = Body(...)):
	# write using alias so file contains the external field name \'return\'
	fakes = [fake.dict(by_alias=True) for fake in fakes]
	existing_fakes = []
	if os.path.exists(config.FAKES_FILE): # Usando config.FAKES_FILE
		async with aiofiles.open(config.FAKES_FILE, "r") as f: # Usando config.FAKES_FILE
			content = await f.read()
			try:
				existing_fakes = json.loads(content)
			except Exception:
				existing_fakes = []
	all_fakes = existing_fakes + fakes
	async with aiofiles.open(config.FAKES_FILE, "w") as f: # Usando config.FAKES_FILE
		await f.write(json.dumps(all_fakes, indent=2))
	# Registro dinâmico
	from app.main import app
	for fake in fakes:
		register_fake_route(app, fake)

	# Força a atualização do esquema OpenAPI para o Swagger UI
	app.openapi_schema = None
	app.setup()

	return {"message": "Rotas fakes adicionadas e registradas", "count": len(fakes)}

@router.delete("/fake/{path}", tags=["Admin"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_fake_route(path: str = Path(..., description="Path da rota a ser removida")):
	norm_path = normalize_path(path)
	
	# Remova a rota do FastAPI
	from app.main import app # Importe app
	for i, route in enumerate(app.routes):
		if hasattr(route, "path") and route.path == norm_path:
			del app.routes[i]
			break

	# Remova a rota da persistência (seu fakes.json)
	route_service.remove_route(norm_path) # Isso ainda é importante para manter o fakes.json atualizado

	if os.path.exists(config.FAKES_FILE): # Usando config.FAKES_FILE
		async with aiofiles.open(config.FAKES_FILE, "r") as f: # Usando config.FAKES_FILE
			content = await f.read()
			fakes = json.loads(content)
		new_fakes = [fake for fake in fakes if fake.get("name") != norm_path]
		async with aiofiles.open(config.FAKES_FILE, "w") as f: # Usando config.FAKES_FILE
			await f.write(json.dumps(new_fakes, indent=2))

	# Força a atualização do esquema OpenAPI para o Swagger UI
	app.openapi_schema = None
	app.setup()

@router.get("/fakes", tags=["Admin"])
async def list_fakes():
    if os.path.exists(config.FAKES_FILE): # Usando config.FAKES_FILE
        async with aiofiles.open(config.FAKES_FILE, "r") as f: # Usando config.FAKES_FILE
            content = await f.read()
            try:
                return json.loads(content)
            except:
                return []
    return []

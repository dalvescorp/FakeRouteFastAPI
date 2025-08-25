# Projeto FakeRouteFastAPI

## Sumário
- [Descrição Geral](#descrição-geral)
- [Arquitetura](#arquitetura)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Principais Arquivos](#principais-arquivos)
- [Dependências](#dependências)
 # Projeto FakeRouteFastAPI — documentação

Este documento descreve o estado atual do projeto e como usar as rotas fake dinâmicas (campo `return`).

Sumário
- Descrição Geral
- Formato de `app/fakes.json`
- Como rodar
- Testes e validação
- Endpoints administrativos
- Arquitetura e arquivos
- Docker / Deploy

---

Descrição rápida
 - O projeto registra rotas dinâmicas a partir de `app/fakes.json` na inicialização.
 - As respostas configuradas nas rotas devem usar a chave `return` (ex.: `"return": { ... }`).
 - Os endpoints gerados não possuem parâmetros na assinatura, evitando que o Swagger peça campos desnecessários.

Formato do `app/fakes.json`
 - Arquivo: um array JSON com objetos descrevendo cada rota.
 - Campos por rota:
   - `name`: caminho (ex: `/meu-exemplo`)
   - `return`: JSON que será retornado pela rota
   - `status_code`: código HTTP da resposta (padrão 200)
   - `headers`: objeto de headers adicionais
   - `delay`: atraso em segundos antes de responder
   - `methods`: lista de métodos HTTP (ex.: `["GET"]` ou `["GET","POST"]`)

Exemplo de entrada (adicione ao array em `app/fakes.json`):

```json
{
  "name": "/meu-exemplo",
  "return": {
    "status": "ok",
    "dados": [1, 2, 3],
    "mensagem": "Esta é uma resposta fake personalizada!"
  },
  "status_code": 201,
  "headers": { "X-Custom-Header": "valor" },
  "delay": 1.0,
  "methods": ["GET"]
}
```

Como rodar (PowerShell)

```powershell
uvicorn app.main:app --reload --reload-dir app --reload-include "fakes.json"
```

Se sua versão do `uvicorn` não suportar `--reload-include`, use:

```powershell
uvicorn app.main:app --reload --reload-dir app
```

Testando uma rota

```powershell
# GET simples
Invoke-RestMethod -Uri "http://localhost:8000/meu-exemplo" -Method GET

# curl
curl http://localhost:8000/meu-exemplo
```

Comportamento no Swagger
- Rotas configuradas apenas com `GET` não mostrarão body no Swagger.
- Se você incluir `POST` em `methods`, o Swagger exibirá o campo de request body para esse método (comportamento normal do OpenAPI).

Endpoints administrativos
- `POST /populate-fakes`: recebe uma lista de rotas e persiste em `app/fakes.json`. Use o campo `return` nos objetos.
- `DELETE /fake/{path}`: remove rota da memória e do arquivo `fakes.json`.

Arquitetura e arquivos principais
- `app/main.py`: inicialização e registro dinâmico de rotas.
- `app/api/routes.py`: endpoints administrativos e modelos de request.
- `app/models/*`: modelos Pydantic (agora usando alias `return`).
- `app/persistence/*`: implementações de persistência (memória/arquivo).
- `app/services/route_service.py`: lógica de criação/remoção/listagem.
- `app/utils/dynamic.py`: helpers para adicionar rotas dinamicamente.

Docker / Deploy (resumo)
- Em produção prefira Gunicorn + Uvicorn workers (não use `--reload`).
- Para dev dentro de container, monte `app/fakes.json` como volume para que alterações no host reflitam no container.

Validação e notas
- Sempre use a chave `return` nas novas entradas de `app/fakes.json`.
- Se precisar que `POST` priorize o body enviado (echo), posso adaptar os endpoints para esse comportamento.

Fim.

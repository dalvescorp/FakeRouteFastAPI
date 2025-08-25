import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

class Config:
    SWAGGER_USERNAME = os.getenv("SWAGGER_USERNAME", "admin")
    SWAGGER_PASSWORD = os.getenv("SWAGGER_PASSWORD", "senha123")
    API_TITLE = os.getenv("API_TITLE", "FakeRouteFastAPI")
    FAKES_FILE = os.getenv("FAKES_FILE", "/tmp/fakes.json")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    # Adicione outras variáveis conforme necessário

config = Config()

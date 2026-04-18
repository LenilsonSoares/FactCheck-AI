import uvicorn
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router


BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")


def _parse_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ALLOW_ORIGINS", "")
    if not raw:
        return [
            "http://localhost:19006",
            "http://127.0.0.1:19006",
            "http://localhost:8081",
            "http://127.0.0.1:8081",
            "http://localhost:8082",
            "http://127.0.0.1:8082",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]

# 1. Inicialização Sênior (Metadados ajudam na documentação automática)
app = FastAPI(
    title="FactCheck-AI API",
    description="Sistema de verificação de fatos com Google API e Machine Learning",
    version="1.1.0"
)

# 2. Configuração de CORS (Essencial para o Flutter/Web se conectar sem erros)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_origins(),
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):\d+$",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# 5. Entrypoint para execução direta
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
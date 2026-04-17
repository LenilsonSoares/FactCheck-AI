import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router

# 1. Inicialização Sênior (Metadados ajudam na documentação automática)
app = FastAPI(
    title="FactCheck-AI API",
    description="Sistema de verificação de fatos com Google API e Machine Learning",
    version="1.0.0"
)

# 2. Configuração de CORS (Essencial para o Flutter/Web se conectar sem erros)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# 5. Entrypoint para execução direta
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
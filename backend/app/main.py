import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.services.fact_check_manager import FactCheckManager
from app.services.ml_engine import ModelLoader
from app.domain.models import VerificationResult

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

# 3. Injeção de Dependência (Instancia o Gerente uma única vez)
manager = FactCheckManager()

# 4. Schema de Entrada (Contrato de API)
class ClaimRequest(BaseModel):
    text: str

# --- ENDPOINTS ---

@app.get("/health")
def health_check():
    """Verifica se o sistema e o modelo de IA estão operacionais."""
    try:
        loader = ModelLoader.get_instance()
        return {
            "status": "online",
            "model_loaded": True,
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "model_loaded": False,
            "error": str(e)
        }

@app.post("/verify", response_model=VerificationResult)
async def verify_claim(request: ClaimRequest):
    """
    Recebe uma afirmação e processa a verificação.
    Fluxo: Google Fact Check API -> Machine Learning Model (Fallback).
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="O texto da afirmação não pode estar vazio.")
    
    try:
        # O Manager encapsula toda a complexidade (Google vs IA)
        result = manager.check_statement(request.text)
        return result
    except Exception as e:
        # Logging de erro sênior
        print(f"⚠️ Erro no processamento: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a verificação.")

# 5. Entrypoint para execução direta
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from app.services.fact_check_manager import FactCheckManager
from app.domain.models import VerificationResult
from app.services.ml_engine import ModelLoader

load_dotenv()

app = FastAPI()
manager = FactCheckManager()


class ClaimRequest(BaseModel):
    text: str


@app.post("/verify")
async def verify_claim(request: ClaimRequest) -> VerificationResult:
    """Endpoint que verifica uma afirmação — primeiro consulta Google, senão usa ML."""
    result = manager.check_statement(request.text)
    return result


@app.get("/health")
def health():
    try:
        loader = ModelLoader.get_instance()
        return {"status": "ok", "model_loaded": True}
    except Exception as e:
        return {"status": "degraded", "model_loaded": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

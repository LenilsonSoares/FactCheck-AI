from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_verify_claim_use_case
from app.api.schemas import ClaimRequest
from app.application.use_cases import VerifyClaimUseCase
from app.domain.models import VerificationResult
from app.services.ml_engine import ModelLoader


router = APIRouter()


@router.get("/")
def root() -> dict:
    return {
        "name": "FactCheck-AI API",
        "status": "online",
        "endpoints": ["/health", "/verify"],
    }


@router.get("/health")
def health_check() -> dict:
    try:
        ModelLoader.get_instance()
        return {"status": "online", "model_loaded": True, "version": "1.1.0"}
    except Exception as exc:
        return {"status": "degraded", "model_loaded": False, "error": str(exc)}


@router.post("/verify", response_model=VerificationResult)
async def verify_claim(
    request: ClaimRequest,
    use_case: VerifyClaimUseCase = Depends(get_verify_claim_use_case),
) -> VerificationResult:
    statement = request.text.strip()
    if not statement:
        raise HTTPException(status_code=400, detail="O texto da afirmação não pode estar vazio.")

    try:
        return use_case.execute(statement)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar verificação: {exc}")

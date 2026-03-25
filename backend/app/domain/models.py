from pydantic import BaseModel
from typing import Optional


class VerificationResult(BaseModel):
    source: str  # "Google API" ou "AI Model"
    rating: Optional[str]
    text: Optional[str]
    confidence: float

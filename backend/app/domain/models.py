from pydantic import BaseModel
from typing import Optional


class VerificationResult(BaseModel):
    source: str
    rating: Optional[str]
    text: Optional[str]
    confidence: float

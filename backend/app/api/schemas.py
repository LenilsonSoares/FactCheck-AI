from pydantic import BaseModel, Field


class ClaimRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Afirmação para verificação")


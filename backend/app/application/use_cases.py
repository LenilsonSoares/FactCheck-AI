import logging
from dataclasses import dataclass
from typing import Optional

from app.domain.models import VerificationResult
from app.application.ports import ClaimClassifier, DatasetRepository, FactCheckProvider


logger = logging.getLogger(__name__)


@dataclass
class VerifyClaimUseCase:
    fact_check_provider: FactCheckProvider
    classifier: ClaimClassifier
    dataset_repository: DatasetRepository

    def execute(self, statement: str) -> VerificationResult:
        google_claim: Optional[dict]
        try:
            google_claim = self.fact_check_provider.search(statement)
        except Exception as exc:
            logger.warning("Falha ao consultar API de fact-check: %s", exc)
            google_claim = None

        if google_claim:
            source, rating, text, source_url = self._extract_google_payload(google_claim)
            self._safe_store(
                text=text,
                source=source,
                rating=rating,
                confidence=1.0,
                source_url=source_url,
            )
            return VerificationResult(source="Google Fact Check", rating=rating, text=text, confidence=1.0)

        try:
            prediction = self.classifier.predict(statement)
            rating = prediction.get("rating")
            confidence = float(prediction.get("confidence", 0.0))
        except Exception as exc:
            logger.warning("Falha na inferencia do modelo local: %s", exc)
            rating = "Inconclusive"
            confidence = 0.5

        self._safe_store(
            text=statement,
            source="Internal AI Model",
            rating=rating,
            confidence=confidence,
            source_url="",
        )

        return VerificationResult(
            source="Internal AI Model",
            rating=rating,
            text=statement,
            confidence=confidence,
        )

    def _extract_google_payload(self, google_claim: dict) -> tuple[str, Optional[str], str, str]:
        try:
            review = (google_claim.get("claimReview") or [])[0]
        except Exception:
            review = {}

        source = review.get("publisher", {}).get("name") or "Google Fact Check"
        rating = review.get("textualRating")
        source_url = review.get("url") or ""
        text = google_claim.get("text") or google_claim.get("claim") or ""
        if not text:
            text = str(google_claim)

        return source, rating, text, source_url

    def _safe_store(self, *, text: str, source: str, rating: Optional[str], confidence: float, source_url: str) -> None:
        try:
            self.dataset_repository.append(
                text=text,
                source=source,
                rating=rating,
                confidence=confidence,
                source_url=source_url,
            )
        except Exception as exc:
            logger.warning("Falha ao persistir consulta no dataset local: %s", exc)

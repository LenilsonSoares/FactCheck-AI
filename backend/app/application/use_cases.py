import logging
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.domain.models import VerificationResult
from app.application.ports import ClaimClassifier, DatasetRepository, FactCheckProvider


logger = logging.getLogger(__name__)
RULE_BASED_SOURCE = "Rule-based Context"


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

        direct_fact = self._resolve_presidency_fact(statement)
        if not direct_fact:
            direct_fact = self._resolve_brazil_vote_obligation_fact(statement)
        if direct_fact:
            rating, confidence = direct_fact
            self._safe_store(
                text=statement,
                source=RULE_BASED_SOURCE,
                rating=rating,
                confidence=confidence,
                source_url="",
            )
            return VerificationResult(
                source=RULE_BASED_SOURCE,
                rating=rating,
                text=statement,
                confidence=confidence,
            )

        try:
            prediction = self.classifier.predict(statement)
            rating = prediction.get("rating")
            confidence = float(prediction.get("confidence", 0.0))
        except Exception as exc:
            logger.warning("Falha na inferencia do modelo local: %s", exc)
            rating = "Inconclusivo"
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

    def _resolve_presidency_fact(self, statement: str) -> Optional[tuple[str, float]]:
        text = self._normalize_text(statement)
        if not text:
            return None

        # Regra pequena para perguntas factuais comuns de presidencia.
        if "president" not in text:
            return None

        person = None
        if "lula" in text:
            person = "lula"
        elif "bolsonaro" in text:
            person = "bolsonaro"

        if not person:
            return None

        current_year = datetime.now().year
        year_match = re.search(r"\b(19\d{2}|20\d{2})\b", text)
        target_year = int(year_match.group(1)) if year_match else current_year

        mandates = {
            "lula": [(2003, 2010), (2023, 2026)],
            "bolsonaro": [(2019, 2022)],
        }
        is_president = any(start <= target_year <= end for start, end in mandates[person])
        is_left_office_claim = bool(
            re.search(r"\b(deixou|parou|saiu)\s+de\s+ser\s+president", text)
        )

        is_true = not is_president if is_left_office_claim else is_president
        if self._has_negation(text):
            is_true = not is_true

        rating = "Verdadeiro" if is_true else "Falso"
        confidence = 0.98
        return rating, confidence

    def _resolve_brazil_vote_obligation_fact(self, statement: str) -> Optional[tuple[str, float]]:
        text = self._normalize_text(statement)
        if not text:
            return None

        if "voto" not in text or "obrigat" not in text or "brasil" not in text:
            return None

        optional_vote_group = bool(
            re.search(
                r"\b(analfabet|16|17|dezesseis|dezessete|maior(?:es)? de 70|"
                r"mais de 70|maior(?:es)? de setenta|mais de setenta|setenta anos)\w*\b",
                text,
            )
        )

        is_true = not optional_vote_group
        if self._has_negation(text):
            is_true = not is_true
        rating = "Verdadeiro" if is_true else "Falso"
        confidence = 0.98
        return rating, confidence

    def _normalize_text(self, statement: str) -> str:
        text = (statement or "").strip().lower()
        text = unicodedata.normalize("NFKD", text)
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        text = re.sub(r"\s+", " ", text)
        return text

    def _has_negation(self, text: str) -> bool:
        return bool(re.search(r"\b(nao|nunca|jamais)\b", text))

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

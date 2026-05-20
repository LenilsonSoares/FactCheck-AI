import requests
import os
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")


class GoogleFactCheckClient:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.min_relevance_score = self._get_min_relevance_score()
        self.base_urls = [
            "https://factchecktools.googleapis.com/v1alpha1",
            "https://factchecktools.googleapis.com/v1",
        ]

    def _get_min_relevance_score(self) -> float:
        raw_value = os.getenv("GOOGLE_MIN_RELEVANCE_SCORE", "0.45")
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            return 0.45
        return max(0.0, min(1.0, value))

    def _normalize_text(self, text: str) -> str:
        text = unicodedata.normalize("NFKD", text or "")
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _tokenize(self, text: str) -> set[str]:
        stopwords = {
            "a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "ou", "em",
            "no", "na", "nos", "nas", "um", "uma", "uns", "umas", "que", "se", "por",
            "para", "com", "sem", "ao", "aos", "a", "ha", "foi", "ser", "esta", "estao",
            "isso", "esse", "essa", "este", "sobre", "como", "quando", "onde", "porque",
            "qual", "quais", "tem", "ter", "teve", "vai", "ja",
        }
        tokens = {tok for tok in self._normalize_text(text).split(" ") if tok and tok not in stopwords}
        return tokens

    def _important_tokens(self, text: str) -> set[str]:
        generic_terms = {
            "eleicao", "eleicoes", "eleitoral", "voto", "votos", "votacao", "urna",
            "urnas", "presidente", "governo", "brasil", "brasileiro", "brasileira",
            "brasileiros", "brasileiras", "noticia", "video", "foto", "mensagem",
            "postagem", "afirma", "afirmam", "dizem", "disse",
        }
        return {token for token in self._tokenize(text) if len(token) >= 4 and token not in generic_terms}

    def _score_match(self, query: str, candidate_text: str) -> float:
        q_norm = self._normalize_text(query)
        c_norm = self._normalize_text(candidate_text)

        if not q_norm or not c_norm:
            return 0.0

        seq = SequenceMatcher(None, q_norm, c_norm).ratio()
        q_tokens = self._tokenize(query)
        c_tokens = self._tokenize(candidate_text)
        if not q_tokens or not c_tokens:
            token_overlap = 0.0
        else:
            token_overlap = len(q_tokens & c_tokens) / len(q_tokens | c_tokens)

        query_coverage = len(q_tokens & c_tokens) / len(q_tokens) if q_tokens else 0.0
        score = (0.45 * seq) + (0.30 * token_overlap) + (0.25 * query_coverage)

        query_important = self._important_tokens(query)
        candidate_important = self._important_tokens(candidate_text)
        if query_important:
            shared_important = query_important & candidate_important
            if not candidate_important:
                return min(score, 0.25)
            if not shared_important:
                return min(score, 0.30)
            important_coverage = len(shared_important) / len(query_important)
            score = (0.85 * score) + (0.15 * important_coverage)

        return score

    def _review_text(self, review: dict) -> str:
        publisher = review.get("publisher", {}) or {}
        candidate_parts = [
            review.get("title") or "",
            review.get("textualRating") or "",
            publisher.get("name") or "",
        ]
        return " ".join(part for part in candidate_parts if part).strip()

    def _claim_score(self, query: str, claim: dict) -> tuple[float, Optional[dict]]:
        claim_text = " ".join(
            part
            for part in [
                claim.get("text") or "",
                claim.get("claim") or "",
                claim.get("claimant") or "",
            ]
            if part
        ).strip()
        reviews = claim.get("claimReview") or []
        if not reviews:
            return self._score_match(query, claim_text), None

        best_score = 0.0
        best_review = None
        for review in reviews:
            review_text = self._review_text(review)
            combined_text = " ".join(part for part in [claim_text, review_text] if part).strip()
            score = max(
                self._score_match(query, claim_text),
                self._score_match(query, review_text),
                self._score_match(query, combined_text),
            )
            if score > best_score:
                best_score = score
                best_review = review

        return best_score, best_review

    def _with_best_review_first(self, claim: dict, best_review: Optional[dict]) -> dict:
        if not best_review:
            return claim

        reviews = claim.get("claimReview") or []
        reordered_reviews = [best_review] + [review for review in reviews if review is not best_review]
        claim = dict(claim)
        claim["claimReview"] = reordered_reviews
        return claim

    def _pick_best_claim(self, query: str, claims: list[dict]) -> Optional[dict]:
        best_claim = None
        best_review = None
        best_score = 0.0

        for claim in claims:
            score, review = self._claim_score(query, claim)
            if score > best_score:
                best_score = score
                best_claim = claim
                best_review = review

        if best_claim and best_score >= self.min_relevance_score:
            return self._with_best_review_first(best_claim, best_review)
        return None

    def search(self, query: str) -> Optional[dict]:
        if not self.api_key:
            raise RuntimeError("GOOGLE_API_KEY não configurada")

        params = {"query": query, "key": self.api_key, "languageCode": "pt"}
        last_error = None
        for base_url in self.base_urls:
            url = f"{base_url}/claims:search"
            try:
                resp = requests.get(url, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                claims = data.get("claims") or []
                if claims:
                    best_claim = self._pick_best_claim(query, claims)
                    if best_claim:
                        return best_claim
            except requests.HTTPError as exc:
                # 404 can happen when a given API version/path is unavailable; try next candidate.
                if exc.response is not None and exc.response.status_code == 404:
                    last_error = exc
                    continue
                raise

        if last_error:
            raise last_error

        return None

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
        self.min_relevance_score = 0.45
        self.base_urls = [
            "https://factchecktools.googleapis.com/v1alpha1",
            "https://factchecktools.googleapis.com/v1",
        ]

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
        }
        tokens = {tok for tok in self._normalize_text(text).split(" ") if tok and tok not in stopwords}
        return tokens

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

        # Weighted score: semantic proximity (sequence) + keyword overlap.
        return (0.65 * seq) + (0.35 * token_overlap)

    def _pick_best_claim(self, query: str, claims: list[dict]) -> Optional[dict]:
        best_claim = None
        best_score = 0.0

        for claim in claims:
            review = (claim.get("claimReview") or [{}])[0]
            candidate_parts = [
                claim.get("text") or "",
                claim.get("claim") or "",
                review.get("title") or "",
            ]
            candidate_text = " ".join(part for part in candidate_parts if part).strip()
            score = self._score_match(query, candidate_text)
            if score > best_score:
                best_score = score
                best_claim = claim

        if best_claim and best_score >= self.min_relevance_score:
            return best_claim
        return None

    def search(self, query: str) -> Optional[dict]:
        if not self.api_key:
            raise RuntimeError("GOOGLE_API_KEY não configurada")

        params = {"query": query, "key": self.api_key}
        last_error = None
        for base_url in self.base_urls:
            url = f"{base_url}/claims:search"
            try:
                resp = requests.get(url, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                claims = data.get("claims") or []
                if claims:
                    return self._pick_best_claim(query, claims)
                return None
            except requests.HTTPError as exc:
                # 404 can happen when a given API version/path is unavailable; try next candidate.
                if exc.response is not None and exc.response.status_code == 404:
                    last_error = exc
                    continue
                raise

        if last_error:
            raise last_error

        return None

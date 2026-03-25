from typing import Optional
import os
import csv
from ..domain.models import VerificationResult
from .google_api import GoogleFactCheckClient
from .ml_engine import ModelLoader


class FactCheckManager:
    def __init__(self):
        self.google_client = GoogleFactCheckClient()

    def check_statement(self, statement: str) -> VerificationResult:
        # 1. Tenta o Google
        try:
            google_data = self.google_client.search(statement)
        except Exception:
            google_data = None

        if google_data:
            # extrair rating e texto de forma segura
            try:
                review = google_data.get("claimReview", [])[0]
                rating = review.get("textualRating")
                publisher = review.get("publisher", {}).get("name")
                text = google_data.get("text") or google_data.get("claim")
            except Exception:
                rating = None
                publisher = "Google Fact Check"
                text = str(google_data)

            return VerificationResult(
                source="Google Fact Check",
                rating=rating,
                text=text,
                confidence=1.0,
            )

        # 2. Se não achou, chama o modelo interno
        try:
            loader = ModelLoader.get_instance()
            pred = loader.predict(statement)
            rating = pred.get("rating")
            confidence = pred.get("confidence", 0.0)

            # salvar consulta no dataset local para auditoria/treino futuro
            try:
                self._append_to_dataset(statement, "Internal AI Model", rating, statement, confidence)
            except Exception:
                pass

            return VerificationResult(
                source="Internal AI Model",
                rating=rating,
                text=statement,
                confidence=confidence,
            )
        except Exception:
            # fallback mock
            return self._call_ai_model(statement)

    def _call_ai_model(self, statement: str) -> VerificationResult:
        return VerificationResult(
            source="Internal AI Model",
            rating="Inconclusive",
            text=statement,
            confidence=0.5,
        )

    def _append_to_dataset(self, statement: str, source: str, rating: Optional[str], text: str, confidence: float):
        # Append a minimal row to data/processed/dataset_eleicoes.csv for auditing
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        out_dir = os.path.join(root, "data", "processed")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "dataset_eleicoes.csv")

        headers = ["texto", "fonte", "source_url", "veredito", "data", "image_url", "tags", "confidence"]
        write_header = not os.path.exists(out_path)

        with open(out_path, "a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            if write_header:
                writer.writeheader()
            writer.writerow({
                "texto": statement,
                "fonte": source,
                "source_url": "",
                "veredito": rating,
                "data": "",
                "image_url": "",
                "tags": "[]",
                "confidence": confidence,
            })

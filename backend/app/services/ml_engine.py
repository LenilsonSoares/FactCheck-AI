import joblib
import os
import threading
from typing import Dict, Optional


class ModelLoader:
    """Singleton loader that supports either a full sklearn Pipeline (saved
    as `modelo.pkl` / `model.pkl`) or a separate `modelo.pkl`/`model.pkl`
    and `vectorizer.pkl` pairing. Exposes `predict(text)` returning a dict
    with `label`(0/1), `rating` (string) and `confidence` (float 0..1).
    """

    _instance: Optional["ModelLoader"] = None
    _lock = threading.Lock()

    def __init__(self, model_path: Optional[str] = None):
        services_dir = os.path.dirname(__file__)
        app_dir = os.path.abspath(os.path.join(services_dir, ".."))
        ml_dir = os.path.join(app_dir, "ml_models")

        # Defaults balance caution and usability.
        # Values can still be tuned via env for demos/experiments.
        self.min_confidence = float(os.getenv("MODEL_MIN_CONFIDENCE", "0.80"))
        self.min_margin = float(os.getenv("MODEL_MIN_MARGIN", "0.20"))

        # candidate files (in order of preference)
        candidates = []
        if model_path:
            candidates.append(model_path)
        candidates += [
            os.path.join(ml_dir, "modelo.pkl"),
            os.path.join(ml_dir, "model.pkl"),
            os.path.join(services_dir, "model.pkl"),
        ]

        found_pipeline = None
        for p in candidates:
            if p and os.path.exists(p) and os.path.getsize(p) > 0:
                # attempt to load as pipeline
                try:
                    pipeline = joblib.load(p)
                    # succesful load
                    self.pipeline = pipeline
                    self.model = None
                    self.vectorizer = None
                    self._model_path = p
                    return
                except Exception:
                    # not a pipeline or corrupted — continue to try others
                    found_pipeline = p

        # If we reach here, try separate model + vectorizer
        model_file = os.path.join(ml_dir, "modelo.pkl")
        vectorizer_file = os.path.join(ml_dir, "vectorizer.pkl")
        if os.path.exists(model_file) and os.path.exists(vectorizer_file):
            try:
                self.model = joblib.load(model_file)
                self.vectorizer = joblib.load(vectorizer_file)
                self.pipeline = None
                self._model_path = model_file
                return
            except Exception as e:
                raise RuntimeError(f"Falha ao carregar model+vectorizer: {e}")

        # nothing worked
        raise FileNotFoundError(f"Nenhum modelo válido encontrado. Tentados: {candidates + [model_file, vectorizer_file]}")

    @classmethod
    def get_instance(cls) -> "ModelLoader":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def predict(self, text: str) -> Dict:
        try:
            probs = None
            margin = 0.0
            if getattr(self, "pipeline", None) is not None:
                # pipeline supports single-call predict/predict_proba
                pred = int(self.pipeline.predict([text])[0])
                confidence = 0.0
                if hasattr(self.pipeline, "predict_proba"):
                    try:
                        probs = self.pipeline.predict_proba([text])[0]
                        confidence = float(max(probs))
                        if len(probs) >= 2:
                            margin = float(abs(probs[1] - probs[0]))
                    except Exception:
                        confidence = 0.0
            else:
                # separate vectorizer + model
                vec = self.vectorizer.transform([text])
                pred = int(self.model.predict(vec)[0])
                confidence = 0.0
                if hasattr(self.model, "predict_proba"):
                    try:
                        probs = self.model.predict_proba(vec)[0]
                        confidence = float(max(probs))
                        if len(probs) >= 2:
                            margin = float(abs(probs[1] - probs[0]))
                    except Exception:
                        confidence = 0.0

            # Conservative rule: if either confidence or separation is weak,
            # return Inconclusive instead of forcing true/false.
            is_uncertain = confidence < self.min_confidence or margin < self.min_margin
            rating = "Verdadeiro" if pred == 1 else "Falso"
            if is_uncertain:
                rating = "Inconclusive"

            return {
                "label": pred,
                "rating": rating,
                "confidence": confidence,
                "is_uncertain": is_uncertain,
                "margin": margin,
            }
        except Exception as e:
            # on error, raise to caller to fallback
            raise RuntimeError(f"Erro na predição do modelo: {e}")


__all__ = ["ModelLoader"]
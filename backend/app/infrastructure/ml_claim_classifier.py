from app.services.ml_engine import ModelLoader


class MLClaimClassifier:
    def __init__(self) -> None:
        self._loader = ModelLoader.get_instance()

    def predict(self, text: str) -> dict:
        return self._loader.predict(text)

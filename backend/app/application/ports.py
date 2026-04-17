from typing import Optional, Protocol


class FactCheckProvider(Protocol):
    def search(self, query: str) -> Optional[dict]:
        ...


class ClaimClassifier(Protocol):
    def predict(self, text: str) -> dict:
        ...


class DatasetRepository(Protocol):
    def append(self, *, text: str, source: str, rating: Optional[str], confidence: float, source_url: str = "") -> None:
        ...

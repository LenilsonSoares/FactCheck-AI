from fastapi.testclient import TestClient

from app.main import app
from app.api import routes
from app.api.dependencies import get_verify_claim_use_case
from app.domain.models import VerificationResult


class StubUseCase:
    def execute(self, statement: str) -> VerificationResult:
        return VerificationResult(
            source="Internal AI Model",
            rating="Falso",
            text=statement,
            confidence=0.87,
        )


client = TestClient(app)


def setup_function() -> None:
    app.dependency_overrides[get_verify_claim_use_case] = lambda: StubUseCase()


def teardown_function() -> None:
    app.dependency_overrides.clear()


def test_health_online(monkeypatch):
    monkeypatch.setattr(routes.ModelLoader, "get_instance", staticmethod(lambda: object()))

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "online"
    assert payload["model_loaded"] is True


def test_verify_success_uses_dependency_override():
    response = client.post("/verify", json={"text": "Boato eleitoral qualquer"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "Internal AI Model"
    assert payload["rating"] == "Falso"
    assert payload["text"] == "Boato eleitoral qualquer"
    assert 0 <= payload["confidence"] <= 1


def test_verify_rejects_empty_text():
    response = client.post("/verify", json={"text": "    "})

    assert response.status_code == 400
    assert "não pode estar vazio" in response.json()["detail"].lower()

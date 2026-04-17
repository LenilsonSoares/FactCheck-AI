from app.application.use_cases import VerifyClaimUseCase


class FakeProvider:
    def __init__(self, result=None, raises=False):
        self.result = result
        self.raises = raises

    def search(self, query: str):
        if self.raises:
            raise RuntimeError("provider error")
        return self.result


class FakeClassifier:
    def __init__(self, result=None, raises=False):
        self.result = result or {"rating": "Falso", "confidence": 0.66}
        self.raises = raises

    def predict(self, text: str):
        if self.raises:
            raise RuntimeError("classifier error")
        return self.result


class InMemoryDataset:
    def __init__(self):
        self.rows = []

    def append(self, **kwargs):
        self.rows.append(kwargs)


def test_use_case_prefers_google_result():
    google_claim = {
        "text": "Afirmação validada",
        "claimReview": [
            {
                "publisher": {"name": "Agência X"},
                "textualRating": "True",
                "url": "https://example.org/check",
            }
        ],
    }
    repo = InMemoryDataset()
    use_case = VerifyClaimUseCase(
        fact_check_provider=FakeProvider(result=google_claim),
        classifier=FakeClassifier(result={"rating": "Falso", "confidence": 0.3}),
        dataset_repository=repo,
    )

    result = use_case.execute("texto")

    assert result.source == "Google Fact Check"
    assert result.rating == "True"
    assert result.text == "Afirmação validada"
    assert result.confidence == 1.0
    assert len(repo.rows) == 1
    assert repo.rows[0]["source"] == "Agência X"


def test_use_case_fallback_to_classifier_when_provider_fails():
    repo = InMemoryDataset()
    use_case = VerifyClaimUseCase(
        fact_check_provider=FakeProvider(raises=True),
        classifier=FakeClassifier(result={"rating": "Verdadeiro", "confidence": 0.91}),
        dataset_repository=repo,
    )

    result = use_case.execute("texto sem claim externa")

    assert result.source == "Internal AI Model"
    assert result.rating == "Verdadeiro"
    assert result.text == "texto sem claim externa"
    assert result.confidence == 0.91
    assert len(repo.rows) == 1
    assert repo.rows[0]["source"] == "Internal AI Model"


def test_use_case_returns_inconclusive_on_classifier_error():
    repo = InMemoryDataset()
    use_case = VerifyClaimUseCase(
        fact_check_provider=FakeProvider(result=None),
        classifier=FakeClassifier(raises=True),
        dataset_repository=repo,
    )

    result = use_case.execute("texto")

    assert result.source == "Internal AI Model"
    assert result.rating == "Inconclusive"
    assert result.confidence == 0.5
    assert len(repo.rows) == 1

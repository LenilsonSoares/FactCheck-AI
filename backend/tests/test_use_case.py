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

    assert result.source == "Classificador local"
    assert result.rating == "Verdadeiro"
    assert result.text == "texto sem claim externa"
    assert result.confidence == 0.91
    assert len(repo.rows) == 1
    assert repo.rows[0]["source"] == "Classificador local"


def test_use_case_returns_inconclusive_for_vague_arrest_question():
    repo = InMemoryDataset()
    google_claim = {
        "text": "Outra checagem parecida, mas nao equivalente",
        "claimReview": [{"publisher": {"name": "Agencia X"}, "textualRating": "Falso"}],
    }
    use_case = VerifyClaimUseCase(
        fact_check_provider=FakeProvider(result=google_claim),
        classifier=FakeClassifier(result={"rating": "Falso", "confidence": 0.99}),
        dataset_repository=repo,
    )

    result = use_case.execute("Lula foi preso?")

    assert result.source == "Regras contextuais"
    assert result.rating == "Inconclusivo"
    assert result.confidence == 0.55
    assert len(repo.rows) == 1


def test_use_case_returns_inconclusive_for_future_candidacy_question():
    repo = InMemoryDataset()
    use_case = VerifyClaimUseCase(
        fact_check_provider=FakeProvider(result=None),
        classifier=FakeClassifier(result={"rating": "Verdadeiro", "confidence": 0.99}),
        dataset_repository=repo,
    )

    result = use_case.execute("Bolsonaro vai candidatar a presidente?")

    assert result.source == "Regras contextuais"
    assert result.rating == "Inconclusivo"
    assert result.confidence == 0.55
    assert len(repo.rows) == 1


def test_use_case_returns_inconclusive_for_unknown_presidency_name():
    repo = InMemoryDataset()
    use_case = VerifyClaimUseCase(
        fact_check_provider=FakeProvider(result=None),
        classifier=FakeClassifier(result={"rating": "Inconclusivo", "confidence": 0.99}),
        dataset_repository=repo,
    )

    result = use_case.execute("Favio e presidente?")

    assert result.source == "Regras contextuais"
    assert result.rating == "Inconclusivo"
    assert result.confidence == 0.55
    assert len(repo.rows) == 1


def test_use_case_returns_inconclusive_for_broad_urna_safety_question():
    repo = InMemoryDataset()
    use_case = VerifyClaimUseCase(
        fact_check_provider=FakeProvider(result=None),
        classifier=FakeClassifier(result={"rating": "Falso", "confidence": 0.99}),
        dataset_repository=repo,
    )

    result = use_case.execute("A urna e segura?")

    assert result.source == "Regras contextuais"
    assert result.rating == "Inconclusivo"
    assert result.confidence == 0.55
    assert len(repo.rows) == 1


def test_use_case_returns_inconclusive_on_classifier_error():
    repo = InMemoryDataset()
    use_case = VerifyClaimUseCase(
        fact_check_provider=FakeProvider(result=None),
        classifier=FakeClassifier(raises=True),
        dataset_repository=repo,
    )

    result = use_case.execute("texto")

    assert result.source == "Classificador local"
    assert result.rating == "Inconclusivo"
    assert result.confidence == 0.5
    assert len(repo.rows) == 1


def test_use_case_resolves_lula_president_2025_without_classifier_call():
    repo = InMemoryDataset()
    use_case = VerifyClaimUseCase(
        fact_check_provider=FakeProvider(result=None),
        classifier=FakeClassifier(result={"rating": "Falso", "confidence": 0.2}),
        dataset_repository=repo,
    )

    result = use_case.execute("Lula e presidente em 2025?")

    assert result.source == "Regras contextuais"
    assert result.rating == "Verdadeiro"
    assert result.confidence == 0.98
    assert len(repo.rows) == 1
    assert repo.rows[0]["source"] == "Regras contextuais"


def test_use_case_prefers_context_rule_for_direct_presidency_question():
    repo = InMemoryDataset()
    google_claim = {
        "text": "Lula e presidente?",
        "claimReview": [
            {
                "publisher": {"name": "Agencia X"},
                "textualRating": "Falso",
                "url": "https://example.org/check",
            }
        ],
    }
    use_case = VerifyClaimUseCase(
        fact_check_provider=FakeProvider(result=google_claim),
        classifier=FakeClassifier(result={"rating": "Falso", "confidence": 0.99}),
        dataset_repository=repo,
    )

    result = use_case.execute("Lula e presidente?")

    assert result.source == "Regras contextuais"
    assert result.rating == "Verdadeiro"
    assert result.confidence == 0.98
    assert len(repo.rows) == 1
    assert repo.rows[0]["source"] == "Regras contextuais"


def test_use_case_resolves_bolsonaro_president_2025_as_false():
    repo = InMemoryDataset()
    use_case = VerifyClaimUseCase(
        fact_check_provider=FakeProvider(result=None),
        classifier=FakeClassifier(result={"rating": "Verdadeiro", "confidence": 0.9}),
        dataset_repository=repo,
    )

    result = use_case.execute("Bolsonaro e presidente em 2025?")

    assert result.source == "Regras contextuais"
    assert result.rating == "Falso"
    assert result.confidence == 0.98
    assert len(repo.rows) == 1
    assert repo.rows[0]["source"] == "Regras contextuais"


def test_use_case_resolves_lula_not_president_as_false():
    repo = InMemoryDataset()
    use_case = VerifyClaimUseCase(
        fact_check_provider=FakeProvider(result=None),
        classifier=FakeClassifier(result={"rating": "Verdadeiro", "confidence": 0.9}),
        dataset_repository=repo,
    )

    result = use_case.execute("Lula nao e presidente?")

    assert result.source == "Regras contextuais"
    assert result.rating == "Falso"
    assert result.confidence == 0.98
    assert len(repo.rows) == 1
    assert repo.rows[0]["source"] == "Regras contextuais"


def test_use_case_resolves_bolsonaro_not_president_as_true():
    repo = InMemoryDataset()
    use_case = VerifyClaimUseCase(
        fact_check_provider=FakeProvider(result=None),
        classifier=FakeClassifier(result={"rating": "Falso", "confidence": 0.2}),
        dataset_repository=repo,
    )

    result = use_case.execute("Bolsonaro nao e presidente?")

    assert result.source == "Regras contextuais"
    assert result.rating == "Verdadeiro"
    assert result.confidence == 0.98
    assert len(repo.rows) == 1
    assert repo.rows[0]["source"] == "Regras contextuais"


def test_use_case_resolves_vote_not_mandatory_claim_as_false():
    repo = InMemoryDataset()
    use_case = VerifyClaimUseCase(
        fact_check_provider=FakeProvider(result=None),
        classifier=FakeClassifier(result={"rating": "Verdadeiro", "confidence": 0.9}),
        dataset_repository=repo,
    )

    result = use_case.execute("Voto no Brasil nao e obrigatorio?")

    assert result.source == "Regras contextuais"
    assert result.rating == "Falso"
    assert result.confidence == 0.98
    assert len(repo.rows) == 1
    assert repo.rows[0]["source"] == "Regras contextuais"


def test_use_case_resolves_vote_mandatory_claim_as_true():
    repo = InMemoryDataset()
    use_case = VerifyClaimUseCase(
        fact_check_provider=FakeProvider(result=None),
        classifier=FakeClassifier(result={"rating": "Falso", "confidence": 0.2}),
        dataset_repository=repo,
    )

    result = use_case.execute("Voto no Brasil e obrigatorio?")

    assert result.source == "Regras contextuais"
    assert result.rating == "Verdadeiro"
    assert result.confidence == 0.98
    assert len(repo.rows) == 1
    assert repo.rows[0]["source"] == "Regras contextuais"


def test_use_case_resolves_vote_mandatory_for_illiterate_people_as_false():
    repo = InMemoryDataset()
    use_case = VerifyClaimUseCase(
        fact_check_provider=FakeProvider(result=None),
        classifier=FakeClassifier(result={"rating": "Verdadeiro", "confidence": 0.9}),
        dataset_repository=repo,
    )

    result = use_case.execute("O voto no Brasil e obrigatorio para analfabetos?")

    assert result.source == "Regras contextuais"
    assert result.rating == "Falso"
    assert result.confidence == 0.98
    assert len(repo.rows) == 1
    assert repo.rows[0]["source"] == "Regras contextuais"


def test_use_case_resolves_vote_mandatory_for_over_70_as_false():
    repo = InMemoryDataset()
    use_case = VerifyClaimUseCase(
        fact_check_provider=FakeProvider(result=None),
        classifier=FakeClassifier(result={"rating": "Verdadeiro", "confidence": 0.9}),
        dataset_repository=repo,
    )

    result = use_case.execute("O voto no Brasil e obrigatorio para maiores de 70 anos?")

    assert result.source == "Regras contextuais"
    assert result.rating == "Falso"
    assert result.confidence == 0.98
    assert len(repo.rows) == 1
    assert repo.rows[0]["source"] == "Regras contextuais"


def test_use_case_resolves_left_presidency_claim_as_false_when_current_president():
    repo = InMemoryDataset()
    use_case = VerifyClaimUseCase(
        fact_check_provider=FakeProvider(result=None),
        classifier=FakeClassifier(result={"rating": "Verdadeiro", "confidence": 0.9}),
        dataset_repository=repo,
    )

    result = use_case.execute("Lula deixou de ser presidente em 2025?")

    assert result.source == "Regras contextuais"
    assert result.rating == "Falso"
    assert result.confidence == 0.98
    assert len(repo.rows) == 1
    assert repo.rows[0]["source"] == "Regras contextuais"

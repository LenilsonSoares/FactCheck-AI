from pathlib import Path
from ..domain.models import VerificationResult
from app.application.use_cases import VerifyClaimUseCase
from app.infrastructure.csv_dataset_repository import CsvDatasetRepository
from app.infrastructure.google_fact_check_provider import GoogleFactCheckProvider
from app.infrastructure.ml_claim_classifier import MLClaimClassifier


class FactCheckManager:
    def __init__(self):
        base_dir = Path(__file__).resolve().parents[3]
        self.use_case = VerifyClaimUseCase(
            fact_check_provider=GoogleFactCheckProvider(),
            classifier=MLClaimClassifier(),
            dataset_repository=CsvDatasetRepository(base_dir=base_dir),
        )

    def check_statement(self, statement: str) -> VerificationResult:
        return self.use_case.execute(statement)

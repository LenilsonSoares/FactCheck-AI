from pathlib import Path

from app.application.use_cases import VerifyClaimUseCase
from app.infrastructure.csv_dataset_repository import CsvDatasetRepository
from app.infrastructure.google_fact_check_provider import GoogleFactCheckProvider
from app.infrastructure.ml_claim_classifier import MLClaimClassifier


BASE_DIR = Path(__file__).resolve().parents[3]


def get_verify_claim_use_case() -> VerifyClaimUseCase:
    return VerifyClaimUseCase(
        fact_check_provider=GoogleFactCheckProvider(),
        classifier=MLClaimClassifier(),
        dataset_repository=CsvDatasetRepository(base_dir=BASE_DIR),
    )

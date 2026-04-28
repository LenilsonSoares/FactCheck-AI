import csv

from app.infrastructure.csv_dataset_repository import CsvDatasetRepository


def test_csv_dataset_repository_writes_runtime_consultas(tmp_path):
    repo = CsvDatasetRepository(base_dir=tmp_path)

    repo.append(
        text="O voto no Brasil e obrigatorio?",
        source="Rule-based Context",
        rating="Verdadeiro",
        confidence=0.98,
        source_url="",
    )

    output = tmp_path / "data" / "runtime" / "consultas.csv"
    assert output.exists()

    with output.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["texto"] == "O voto no Brasil e obrigatorio?"
    assert rows[0]["fonte"] == "Rule-based Context"
    assert rows[0]["veredito"] == "Verdadeiro"

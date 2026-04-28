import csv
from pathlib import Path
from typing import Optional


class CsvDatasetRepository:
    def __init__(self, base_dir: Path) -> None:
        self._dataset_path = base_dir / "data" / "runtime" / "consultas.csv"

    def append(
        self,
        *,
        text: str,
        source: str,
        rating: Optional[str],
        confidence: float,
        source_url: str = "",
    ) -> None:
        self._dataset_path.parent.mkdir(parents=True, exist_ok=True)
        headers = ["texto", "fonte", "source_url", "veredito", "data", "image_url", "tags", "confidence"]
        write_header = not self._dataset_path.exists()

        with self._dataset_path.open("a", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            if write_header:
                writer.writeheader()
            writer.writerow(
                {
                    "texto": text,
                    "fonte": source,
                    "source_url": source_url,
                    "veredito": rating,
                    "data": "",
                    "image_url": "",
                    "tags": "[]",
                    "confidence": confidence,
                }
            )

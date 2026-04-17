import os
import sys
from pathlib import Path


KEYWORDS = [
    "eleicao",
    "bolsonaro",
    "lula",
    "pt",
    "campanha",
    "urna",
    "voto",
    "fraude",
]


def build_dataset() -> None:
    try:
        from factcheckexplorer.factcheckexplorer import FactCheckLib
    except Exception as exc:
        print(f"Falha ao importar factcheckexplorer: {exc}")
        print("Instale as dependencias com: pip install -r backend/requirements.txt")
        sys.exit(1)

    base_dir = Path(__file__).resolve().parents[1]
    output_dir = base_dir / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)

    for keyword in KEYWORDS:
        print(f"Coletando verificacoes para palavra-chave: {keyword}")
        collector = FactCheckLib(query=keyword, language="pt", num_results=500)
        collector.process()

    print("Coleta finalizada. Revise os arquivos em data/raw e normalize para data/processed.")


if __name__ == "__main__":
    build_dataset()

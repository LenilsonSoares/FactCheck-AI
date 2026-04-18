import sys
import shutil
import json
from pathlib import Path

import pandas as pd

KEYWORDS = ["eleicao", "bolsonaro", "lula", "pt", "campanha", "urna", "voto", "fraude"]


def _normalize_verdict(value):
    s = str(value or "").upper().strip()

    wrong_values = [
        "ENGANOSO", "INSUSTENTAVEL", "INSUSTENTÁVEL", "DISTORCIDO",
        "NAO_E_BEM_ASSIM", "NÃO_É_BEM_ASSIM", "INCONCLUSIVO",
        "FORA DE CONTEXTO", "ERRADO", "FAKE", "FALSO", "SEM CONTEXTO",
    ]
    correct_values = ["COMPROVADO", "CONTEXTUALIZANDO", "VERDADEIRO", "VERDADE"]

    if any(x in s for x in wrong_values):
        return "FALSO"
    if any(x in s for x in correct_values):
        return "VERDADEIRO"
    return s

def build_dataset() -> None:
    try:
        from factcheckexplorer.factcheckexplorer import FactCheckLib
    except Exception as exc:
        print(f"Falha ao importar factcheckexplorer: {exc}")
        sys.exit(1)

    base_dir = Path(__file__).resolve().parents[1]
    raw_dir = base_dir / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    failures = []
    all_items = []
    failures = []

    for keyword in KEYWORDS:
        print(f"Coletando verificações para: {keyword}")
        try:
            collector = FactCheckLib(query=keyword, language="pt", num_results=100)
            raw = collector.fetch_data()
            clean = collector.clean_json(raw)
            data = collector.extract_info(clean)
            if data:
                all_items.extend(data)
            else:
                failures.append((keyword, "retorno vazio"))
        except Exception as exc:
            failures.append((keyword, str(exc)))
            print(f"[WARN] Falha ao coletar '{keyword}': {exc}")
            continue

    if failures:
        print("\nResumo de falhas de coleta:")
        for keyword, reason in failures:
            print(f"- {keyword}: {reason}")

    if not all_items:
        print("[WARN] Nenhum dado coletado. Mantendo dataset existente sem alteracao.")
        return

    # Remove duplicados por claim+source+url.
    dedup = {}
    for item in all_items:
        claim = str(item.get("Claim", "")).strip()
        source = str(item.get("Source Name", "")).strip()
        url = str(item.get("Source URL", "")).strip()
        key = (claim.lower(), source.lower(), url.lower())
        if key not in dedup:
            dedup[key] = item

    records = list(dedup.values())
    print(f"Total coletado (com deduplicacao): {len(records)}")

    df = pd.DataFrame(records)
    if "Verdict" in df.columns:
        df["Verdict"] = df["Verdict"].apply(_normalize_verdict)

    base_dir = Path(__file__).resolve().parents[1]
    output_json = base_dir / "output.json"
    output_pipe = base_dir / "output_pipe.csv"

    with output_json.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    df.to_csv(output_pipe, sep="|", index=False, encoding="utf-8")

    # Move e renomeia o arquivo gerado para o local que o seu normalizador espera
    generated_file = output_pipe
    if generated_file.exists():
        destination = raw_dir / "eleições.csv"
        shutil.move(str(generated_file), str(destination))
        print(f"[OK] Dataset inicial movido para: {destination}")
    else:
        print("[WARN] O coletor não gerou o arquivo output_pipe.csv. Verifique a conexão com a API.")

if __name__ == "__main__":
    build_dataset()

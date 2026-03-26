import os
import json
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

TERMS = ["eleição", "bolsonaro", "lula", "pt", "campanha", "urna", "voto", "fraude"]


def collect_with_factcheckexplorer(terms):
    try:
        from factcheckexplorer import FactCheckLib
    except Exception as e:
        return None, str(e)

    rows = []
    for t in terms:
        print(f"buscando via factcheckexplorer: {t}")
        try:
            lib = FactCheckLib(t)
            raw = lib.fetch_data()
            if not raw:
                print(f"⚠ nenhuma resposta para termo {t}")
                continue
            data = FactCheckLib.clean_json(raw)
            items = lib.extract_info(data)
            for item in items:
                rows.append({
                    "texto": item.get("Claim") or '',
                    "veredito": item.get("Verdict"),
                    "fonte": item.get("Source Name"),
                    "data": item.get("Review Publication Date"),
                    "image_url": item.get("Image URL"),
                    "tags": item.get("Tags"),
                    "termo": t,
                })
        except Exception as e:
            print(f"⚠ erro factcheckexplorer para {t}: {e}")

    return rows, None


def collect_with_google_api(terms, api_key):
    rows = []
    if not api_key:
        print("⚠ GOOGLE_API_KEY não configurada — pulando consulta direta ao Google.")
        return rows

    for t in terms:
        print(f"buscando via Google Fact Check API: {t}")
        q = t
        url = f"https://factchecktools.googleapis.com/v1/claims:search?query={requests.utils.quote(q)}&key={api_key}"
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            data = r.json()
            for claim in data.get("claims", []):
                reviews = claim.get("claimReview", [])
                rating = reviews[0].get("textualRating") if reviews else None
                publisher = reviews[0].get("publisher", {}).get("name") if reviews else None
                text = claim.get("text") or claim.get("claim", '')
                date = claim.get("claimDate") or (reviews[0].get("reviewDate") if reviews else None)

                rows.append({
                    "texto": text,
                    "veredito": rating,
                    "fonte": publisher,
                    "data": date,
                    "termo": t,
                })
        except Exception as e:
            print(f"⚠ erro Google API para {t}: {e}")

    return rows


def ensure_data_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(project_root, "data")
    ensure_data_dir(data_dir)
    out_path = os.path.join(data_dir, "dataset_eleicoes.csv")

    # Primeiro, tente usar factcheckexplorer (recomendado)
    rows, err = collect_with_factcheckexplorer(TERMS)
    if rows is None:
        print(f"factcheckexplorer indisponível: {err}")
        print("Tentando buscar diretamente via Google Fact Check API...")
        rows = collect_with_google_api(TERMS, API_KEY)
    else:
        # se retornou lista vazia, podemos complementar com Google API
        if len(rows) == 0:
            print("Nenhum resultado com factcheckexplorer — tentando Google API...")
            rows = collect_with_google_api(TERMS, API_KEY)

    if not rows:
        print("Nenhum dado coletado. Verifique a conexão e a configuração da API.")
        return

    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Dataset salvo em: {out_path} ({len(df)} registros)")


if __name__ == "__main__":
    main()

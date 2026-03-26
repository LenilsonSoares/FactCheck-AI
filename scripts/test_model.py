import os
import joblib
import pandas as pd


def load_model():
    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app", "ml_models", "modelo.pkl"))
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Modelo não encontrado: {model_path}")
    print(f"Carregando modelo: {model_path}")
    return joblib.load(model_path)


def pretty_label(v: int) -> str:
    return "VERDADEIRO" if int(v) == 1 else "FALSO"


def main():
    model = load_model()

    examples = [
        "Lula ladrão seu lugar é na prisão em plena propaganda eleitoral na Marquês de Sapucaí",
        "NASA confirma descoberta de água em Marte",
        "Vacina X causa autismo conforme estudo desconhecido",
    ]

    print("\n--- Previsões em exemplos customizados ---")
    for t in examples:
        pred = model.predict([t])[0]
        proba = None
        try:
            proba = model.predict_proba([t])[0]
        except Exception:
            pass
        print(f"Texto: {t[:120]!s}")
        print(f" Predito: {pretty_label(pred)} ({int(pred)})")
        if proba is not None:
            print(f" Probabilidades: {proba}")
        print()

    # testar nas primeiras linhas do dataset
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "dataset_eleicoes.csv"))
    if os.path.exists(dataset_path):
        df = pd.read_csv(dataset_path)
        print("\n--- Previsões nas primeiras 5 linhas do dataset ---")
        text_col = None
        for c in ["texto", "Claim", "Claim", "claim"]:
            if c in df.columns:
                text_col = c
                break
        if text_col is None:
            # fallback para primeira coluna textual
            for c in df.columns:
                if df[c].dtype == object:
                    text_col = c
                    break

        for i, row in df.head(5).iterrows():
            txt = row[text_col] if text_col else str(row[0])
            pred = model.predict([txt])[0]
            print(f"#{i+1}: {txt[:100]!s} -> {pretty_label(pred)}")
    else:
        print(f"Dataset não encontrado em: {dataset_path}")


if __name__ == "__main__":
    main()

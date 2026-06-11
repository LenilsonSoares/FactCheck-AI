import json
import sys
from pathlib import Path

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report


BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED = BASE_DIR / "data" / "processed" / "dataset_eleicoes.csv"
RAW = BASE_DIR / "data" / "dataset_eleicoes.csv"
DATASET_PATH = PROCESSED if PROCESSED.exists() else RAW
MODEL_OUTPUT_DIR = BASE_DIR / "backend" / "app" / "ml_models"
METRICS_OUTPUT = BASE_DIR / "data" / "processed" / "metrics.json"


def _project_path(path: Path) -> str:
    try:
        return path.relative_to(BASE_DIR).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_labels(val):
    """Padroniza diferentes vereditos para formato binário (0 ou 1)."""
    if pd.isna(val):
        return None
    s = str(val).lower().strip()
    if any(term in s for term in ["true", "verdade", "fato", "correto", "confirmado", "sim", "1"]):
        return 1
    if any(term in s for term in ["false", "falso", "fake", "enganoso", "distorcido", "errado", "fraude", "0"]):
        return 0
    return None


def get_engine():
    return Pipeline([
        ("vectorizer", TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),
        ("classifier", LogisticRegression(max_iter=1000, class_weight='balanced'))
    ])


def train():
    print(f"Iniciando processamento do dataset: {DATASET_PATH}")

    if not DATASET_PATH.exists():
        print(f"ERRO: Arquivo não localizado em {DATASET_PATH}")
        sys.exit(1)

    df = pd.read_csv(DATASET_PATH, engine="python", on_bad_lines="skip")

    text_candidates = ["texto", "text", "claim", "afirmacao", "body", "content"]
    label_candidates = ["veredito", "verdict", "label", "rating"]

    cols_lower = {c.lower(): c for c in df.columns}
    text_col = next((cols_lower[tc] for tc in text_candidates if tc in cols_lower), None)
    label_col = next((cols_lower[lc] for lc in label_candidates if lc in cols_lower), None)

    if text_col is None:
        text_col = next((c for c in df.columns if df[c].dtype == object), df.columns[0])
    if label_col is None:
        label_col = next((c for c in df.columns if c != text_col), df.columns[1] if len(df.columns) > 1 else df.columns[0])

    print(f"Usando colunas: Input='{text_col}' | Target='{label_col}'")

    X = df[text_col].fillna("")
    y = df[label_col].apply(normalize_labels)
    valid_mask = y.notna()
    X = X[valid_mask]
    y = y[valid_mask].astype(int)

    if y.nunique() < 2:
        print("ERRO: dataset filtrado possui apenas uma classe valida. Revise o dataset/normalizacao.")
        sys.exit(1)

    class_distribution = y.value_counts().sort_index().to_dict()
    print(f"Distribuição de classes no dataset: {class_distribution}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    def upsample_training(X_tr, y_tr, random_state=42):
        df_tr = pd.DataFrame({"text": X_tr, "label": y_tr})
        counts = df_tr["label"].value_counts()
        if counts.min() == counts.max():
            return X_tr, y_tr
        max_count = counts.max()
        parts = []
        for lbl, cnt in counts.items():
            df_lbl = df_tr[df_tr["label"] == lbl]
            if cnt < max_count:
                sampled = df_lbl.sample(max_count - cnt, replace=True, random_state=random_state)
                df_lbl = pd.concat([df_lbl, sampled], ignore_index=True)
            parts.append(df_lbl)
        df_res = pd.concat(parts, ignore_index=True).sample(frac=1, random_state=random_state).reset_index(drop=True)
        return df_res["text"], df_res["label"]

    print("Balanceando treino (upsampling) se necessário...")
    train_distribution_before = y_train.value_counts().sort_index().to_dict()
    X_train_bal, y_train_bal = upsample_training(X_train, y_train)
    train_distribution_after = y_train_bal.value_counts().sort_index().to_dict()
    print(f"Distribuição treino antes: {train_distribution_before}")
    print(f"Distribuição treino depois: {train_distribution_after}")

    model = get_engine()
    print("Treinando modelo...")
    model.fit(X_train_bal, y_train_bal)

    preds = model.predict(X_test)
    accuracy = accuracy_score(y_test, preds)
    report = classification_report(y_test, preds, zero_division=0, output_dict=True)
    print("\nMétricas de Validação:")
    print(f"Acurácia: {accuracy:.4f}")
    print("\nRelatório de Classificação:")
    print(classification_report(y_test, preds, zero_division=0))

    MODEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    save_path = MODEL_OUTPUT_DIR / "modelo.pkl"
    joblib.dump(model, save_path)
    print(f"\nModelo exportado com sucesso: {save_path}")

    METRICS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    metrics = {
        "dataset_path": _project_path(DATASET_PATH),
        "rows_used": int(len(y)),
        "class_distribution": {str(k): int(v) for k, v in class_distribution.items()},
        "train_distribution_before_upsampling": {
            str(k): int(v) for k, v in train_distribution_before.items()
        },
        "train_distribution_after_upsampling": {
            str(k): int(v) for k, v in train_distribution_after.items()
        },
        "accuracy": float(accuracy),
        "classification_report": report,
    }
    METRICS_OUTPUT.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Métricas salvas em: {METRICS_OUTPUT}")


if __name__ == "__main__":
    try:
        train()
    except Exception as e:
        print(f"Erro no treinamento: {e}")
        sys.exit(1)

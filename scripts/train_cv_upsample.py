import sys
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import precision_recall_fscore_support, accuracy_score


# --- CONFIGURAÇÕES ---
BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED = BASE_DIR / "data" / "processed" / "dataset_eleicoes.csv"
RAW = BASE_DIR / "data" / "dataset_eleicoes.csv"
DATASET_PATH = PROCESSED if PROCESSED.exists() else RAW
MODEL_OUTPUT_DIR = BASE_DIR / "backend" / "app" / "ml_models"
MODEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SAVE_PATH = MODEL_OUTPUT_DIR / "modelo.pkl"


def normalize_labels(val):
    if pd.isna(val):
        return 0
    s = str(val).lower().strip()
    if any(term in s for term in ["true", "verdade", "fato", "correto", "confirmado", "sim", "1"]):
        return 1
    return 0


def get_engine():
    return Pipeline([
        ("vectorizer", TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),
        ("classifier", LogisticRegression(max_iter=1000, class_weight='balanced'))
    ])


def upsample_training(X_tr, y_tr, random_state=42):
    df_tr = pd.DataFrame({"text": X_tr, "label": y_tr})
    counts = df_tr["label"].value_counts()
    if counts.min() == counts.max():
        return X_tr.values, y_tr.values
    max_count = counts.max()
    parts = []
    for lbl, cnt in counts.items():
        df_lbl = df_tr[df_tr["label"] == lbl]
        if cnt < max_count:
            sampled = df_lbl.sample(max_count - cnt, replace=True, random_state=random_state)
            df_lbl = pd.concat([df_lbl, sampled], ignore_index=True)
        parts.append(df_lbl)
    df_res = pd.concat(parts, ignore_index=True).sample(frac=1, random_state=random_state).reset_index(drop=True)
    return df_res["text"].values, df_res["label"].values


def run_cv(n_splits=5):
    print(f"Carregando dataset: {DATASET_PATH}")
    if not DATASET_PATH.exists():
        print(f"Erro: Arquivo não encontrado: {DATASET_PATH}")
        sys.exit(1)

    df = pd.read_csv(DATASET_PATH)
    # detectar colunas
    text_candidates = ["texto", "text", "claim", "afirmacao", "body", "content"]
    label_candidates = ["veredito", "verdict", "label", "rating"]
    cols_lower = {c.lower(): c for c in df.columns}
    text_col = next((cols_lower[tc] for tc in text_candidates if tc in cols_lower), None)
    label_col = next((cols_lower[lc] for lc in label_candidates if lc in cols_lower), None)
    if text_col is None:
        text_col = next((c for c in df.columns if df[c].dtype == object), df.columns[0])
    if label_col is None:
        label_col = next((c for c in df.columns if c != text_col), df.columns[1] if len(df.columns) > 1 else df.columns[0])

    X = df[text_col].fillna("").values
    y = df[label_col].apply(normalize_labels).values

    print(f"Distribuição total: {pd.Series(y).value_counts().to_dict()}")

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    accs = []
    prfs = []

    fold = 1
    for train_idx, val_idx in skf.split(X, y):
        X_tr, X_val = X[train_idx], X[val_idx]
        y_tr, y_val = y[train_idx], y[val_idx]

        X_tr_bal, y_tr_bal = upsample_training(X_tr, y_tr, random_state=42 + fold)

        model = get_engine()
        model.fit(X_tr_bal, y_tr_bal)

        preds = model.predict(X_val)
        acc = accuracy_score(y_val, preds)
        prec, rec, f1, _ = precision_recall_fscore_support(y_val, preds, average='binary', zero_division=0)

        accs.append(acc)
        prfs.append((prec, rec, f1))

        print(f"Fold {fold}: acc={acc:.4f} prec={prec:.4f} rec={rec:.4f} f1={f1:.4f} (val size={len(y_val)})")
        fold += 1

    acc_mean = np.mean(accs)
    prec_mean = np.mean([p for p, r, f in prfs])
    rec_mean = np.mean([r for p, r, f in prfs])
    f1_mean = np.mean([f for p, r, f in prfs])

    print("\n📊 Resultados CV (média):")
    print(f"Accuracy: {acc_mean:.4f} | Precision: {prec_mean:.4f} | Recall: {rec_mean:.4f} | F1: {f1_mean:.4f}")

    # Treinar modelo final usando todo o dataset com upsampling
    X_full_bal, y_full_bal = upsample_training(X, y, random_state=999)
    final_model = get_engine()
    print("\nTreinando modelo final com dataset balanceado...")
    final_model.fit(X_full_bal, y_full_bal)
    joblib.dump(final_model, SAVE_PATH)
    print(f"Modelo final salvo em: {SAVE_PATH}")


if __name__ == "__main__":
    try:
        run_cv(n_splits=5)
    except Exception as e:
        print(f"Erro durante CV/treino: {e}")
        sys.exit(1)

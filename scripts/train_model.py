import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import joblib


def infer_label_column(df: pd.DataFrame):
    candidates = ["label", "veredito", "rating", "truth", "y"]
    for c in candidates:
        if c in df.columns:
            return c
    for c in df.columns:
        if df[c].dtype == object:
            nunique = df[c].nunique()
            if 2 <= nunique <= 10:
                return c
    return None


def normalize_label(val: str) -> int:
    if pd.isna(val):
        return 0
    s = str(val).lower()
    if any(tok in s for tok in ["true", "verdade", "real", "correto", "yes", "1"]):
        return 1
    if any(tok in s for tok in ["false", "falso", "mentira", "no", "0"]):
        return 0
    try:
        v = float(s)
        return 1 if v > 0.5 else 0
    except Exception:
        return 0


def load_dataset(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset não encontrado em: {path}")
    df = pd.read_csv(path)
    return df


def prepare_xy(df: pd.DataFrame):
    label_col = infer_label_column(df)
    if label_col is None:
        raise ValueError("Não foi possível inferir a coluna de labels.")

    text_col = None
    for c in ["texto", "text", "claim", "afirmacao", "Claim"]:
        if c in df.columns:
            text_col = c
            break
    if text_col is None:
        for c in df.columns:
            if df[c].dtype == object:
                text_col = c
                break
    if text_col is None:
        raise ValueError("Não foi possível identificar coluna de texto no dataset.")

    X = df[text_col].fillna("")
    y = df[label_col].apply(normalize_label)
    return X, y


def train_and_save(dataset_path: str, out_dir: str):
    df = load_dataset(dataset_path)
    X, y = prepare_xy(df)

    # decide stratify
    value_counts = y.value_counts()
    use_stratify = True
    if len(value_counts) <= 1 or value_counts.min() < 2:
        use_stratify = False
        print("Aviso: distribuição de classes irregular — 'stratify' desabilitado para train_test_split.")

    stratify_arg = y if use_stratify else None
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=stratify_arg)

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=20000, ngram_range=(1,2))),
        ("clf", LogisticRegression(max_iter=1000))
    ])

    print("Treinando modelo...")
    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_test)

    acc = accuracy_score(y_test, preds)
    prec = precision_score(y_test, preds, zero_division=0)
    rec = recall_score(y_test, preds, zero_division=0)
    f1 = f1_score(y_test, preds, zero_division=0)

    print("Métricas de validação:")
    print(f"Accuracy: {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall: {rec:.4f}")
    print(f"F1-score: {f1:.4f}")
    print("\nClassification report:\n")
    print(classification_report(y_test, preds, zero_division=0))

    os.makedirs(out_dir, exist_ok=True)
    model_path = os.path.join(out_dir, "modelo.pkl")
    joblib.dump(pipeline, model_path)
    print(f"Modelo salvo em: {model_path}")


if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    candidates = [
        os.path.join(root, "data", "processed", "dataset_eleicoes.csv"),
        os.path.join(root, "data", "processed", "dataset_limpo.csv"),
        os.path.join(root, "data", "raw", "eleições.csv"),
        os.path.join(root, "data", "raw", "dataset_raw.csv"),
    ]

    dataset = None
    for p in candidates:
        if os.path.exists(p):
            dataset = p
            break

    if dataset is None:
        print("Nenhum dataset encontrado. Coloque o CSV em data/processed/dataset_eleicoes.csv ou data/raw/eleições.csv")
        sys.exit(1)

    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app", "ml_models"))
    train_and_save(dataset, out_dir)
import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import joblib


def infer_label_column(df: pd.DataFrame):
    candidates = ["label", "veredito", "rating", "truth", "y"]
    for c in candidates:
        if c in df.columns:
            return c
    # try to guess a textual column with small set of unique values
    for c in df.columns:
        if df[c].dtype == object:
            nunique = df[c].nunique()
            if 2 <= nunique <= 10:
                return c
    return None


def normalize_label(val: str) -> int:
    if pd.isna(val):
        return 0
    s = str(val).lower()
    if any(tok in s for tok in ["true", "verdade", "real", "correto", "yes", "1"]):
        return 1
    if any(tok in s for tok in ["false", "falso", "mentira", "no", "0"]):
        return 0
    # fallback: try numeric
    try:
        v = float(s)
        return 1 if v > 0.5 else 0
    except Exception:
        return 0


def load_dataset(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset não encontrado em: {path}")
    df = pd.read_csv(path)
    return df


def prepare_xy(df: pd.DataFrame):
    label_col = infer_label_column(df)
    if label_col is None:
        raise ValueError("Não foi possível inferir a coluna de labels. Certifique-se de ter 'veredito' ou 'label' no CSV.")

    # attempt to find text column
    text_col = None
    for c in ["texto", "text", "claim", "afirmacao"]:
        if c in df.columns:
            text_col = c
            break
    if text_col is None:
        # fallback to first object column
        for c in df.columns:
            if df[c].dtype == object:
                text_col = c
                break

    if text_col is None:
        raise ValueError("Não foi possível identificar coluna de texto no dataset.")

    X = df[text_col].fillna("")
    y = df[label_col].apply(normalize_label)
    return X, y


def train_and_save(dataset_path: str, out_dir: str):
    df = load_dataset(dataset_path)
    X, y = prepare_xy(df)

    # decidir se usamos stratify: somente quando todas as classes tiverem pelo menos 2 amostras
    value_counts = y.value_counts()
    use_stratify = True
    if len(value_counts) <= 1:
        use_stratify = False
    elif value_counts.min() < 2:
        use_stratify = False

    if not use_stratify:
        print("Aviso: distribuição de classes irregular — 'stratify' desabilitado para train_test_split.")

    stratify_arg = y if use_stratify else None
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=stratify_arg)

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=20000, ngram_range=(1,2))),
        ("clf", LogisticRegression(max_iter=1000))
    ])

    print("Treinando modelo... isso pode levar alguns segundos dependendo do dataset")
    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_test)

    acc = accuracy_score(y_test, preds)
    prec = precision_score(y_test, preds, zero_division=0)
    rec = recall_score(y_test, preds, zero_division=0)
    f1 = f1_score(y_test, preds, zero_division=0)

    print("Métricas de validação:")
    print(f"Accuracy: {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall: {rec:.4f}")
    print(f"F1-score: {f1:.4f}")
    print("\nClassification report:\n")
    print(classification_report(y_test, preds, zero_division=0))

    os.makedirs(out_dir, exist_ok=True)
    model_path = os.path.join(out_dir, "model.pkl")
    joblib.dump(pipeline, model_path)
    print(f"Modelo salvo em: {model_path}")


if __name__ == "__main__":
    # procura dataset em data/processed ou data/
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    candidates = [
        os.path.join(root, "data", "processed", "dataset_eleicoes.csv"),
        os.path.join(root, "data", "dataset_eleicoes.csv"),
        os.path.join(root, "data", "dataset.csv"),
        os.path.join(root, "data", "raw", "dataset_raw.csv"),
    ]

    dataset = None
    for p in candidates:
        if os.path.exists(p):
            dataset = p
            break

    if dataset is None:
        print("Nenhum dataset encontrado. Coloque o CSV em data/processed/dataset_eleicoes.csv ou em data/dataset_eleicoes.csv")
        sys.exit(1)

    out = os.path.join(os.path.dirname(__file__))
    train_and_save(dataset, out)

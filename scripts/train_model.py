import os
import sys
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report

def normalize_label(val):
    """Mapeia os vereditos variados da API para 0 (Falso) ou 1 (Verdadeiro)."""
    if pd.isna(val): return 0
    s = str(val).lower().strip()
    # Tokens que indicam veracidade (Classe 1)
    pos = ["true", "verdade", "fato", "correto", "verificado", "sim", "1"]
    if any(t in s for t in pos): return 1
    return 0 # Padrão: Falso/Inconclusivo (Classe 0)

def train_fact_checker():
    # 1. Configuração de Caminhos (Caminhos relativos sêniores)
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dataset_path = os.path.join(root, "data", "dataset_eleicoes.csv")
    model_dir = os.path.join(root, "backend", "app", "ml_models")
    
    if not os.path.exists(dataset_path):
        print(f"❌ Erro: Dataset não encontrado em {dataset_path}")
        return

    # 2. Carga e Preparação (Data Engineering)
    print(f"📊 Carregando dataset: {dataset_path}")
    df = pd.read_csv(dataset_path)
    
    # Identificar colunas (Resiliência)
    text_col = 'texto' if 'texto' in df.columns else df.columns[0]
    label_col = 'veredito' if 'veredito' in df.columns else df.columns[1]

    X = df[text_col].fillna("")
    y = df[label_col].apply(normalize_label)

    print(f"📈 Distribuição de classes: {y.value_counts().to_dict()}")

    # 3. Divisão de Treino/Teste (Stratify garante proporção de classes)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if y.nunique() > 1 else None
    )

    # 4. Pipeline de ML (O Coração da IA)
    # Sênior usa class_weight='balanced' para lidar com o excesso de 'Falsos'
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),
        ("clf", LogisticRegression(max_iter=1000, class_weight='balanced')) 
    ])

    print("🧠 Treinando modelo (Logistic Regression com Pesos Balanceados)...")
    pipeline.fit(X_train, y_train)

    # 5. Avaliação (Métricas Reais)
    preds = pipeline.predict(X_test)
    print("\n✅ Métricas de Validação:")
    print(f"Acurácia: {accuracy_score(y_test, preds):.4f}")
    print("\nRelatório de Classificação:")
    print(classification_report(y_test, preds, zero_division=0))

    # 6. Exportação (Salvando os artefatos)
    os.makedirs(model_dir, exist_ok=True)
    model_file = os.path.join(model_dir, "modelo.pkl")
    
    # Salvamos o pipeline COMPLETO (Vetorizador + Modelo) em um único arquivo
    joblib.dump(pipeline, model_file)
    print(f"\n🏆 Modelo exportado com sucesso para: {model_file}")

if __name__ == "__main__":
    train_fact_checker()
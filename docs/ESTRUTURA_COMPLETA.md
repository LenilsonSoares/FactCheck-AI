# Estrutura Completa

```text
FactCheck-AI/
├── backend/
│   ├── app/
│   │   ├── api/                 # Rotas, schemas e dependencias FastAPI
│   │   ├── application/         # Caso de uso principal e portas
│   │   ├── domain/              # Modelos de resposta
│   │   ├── infrastructure/      # Adaptadores Google, ML e CSV
│   │   ├── ml_models/           # modelo.pkl treinado
│   │   ├── services/            # Cliente Google e loader do modelo
│   │   └── main.py              # App FastAPI
│   ├── tests/                   # Testes de API e caso de uso
│   └── requirements.txt
├── data/
│   ├── raw/                     # Coleta bruta do factcheckexplorer
│   ├── processed/               # Dataset limpo usado no treino
│   └── runtime/                 # Consultas feitas durante o uso do app
├── docs/                        # Documentacao e roteiro da apresentacao
├── frontend/                    # App React Native/Expo
├── notebooks/                   # Analises exploratorias
├── scripts/                     # Coleta, normalizacao e treino
├── iniciar_tudo.ps1             # Inicializacao completa
├── parar_tudo.ps1               # Encerramento das portas locais
├── pytest.ini                   # Testes rodando a partir da raiz
└── README.md
```

## Responsabilidade por Camada

- `frontend/`: recebe a afirmacao do usuario, chama `/verify` e exibe resultado, confianca, fonte e historico local.
- `backend/app/api/`: expoe `/health` e `/verify`.
- `backend/app/application/`: implementa o fluxo API externa primeiro, ML depois.
- `backend/app/services/google_api.py`: consulta Google Fact Check Tools API.
- `backend/app/services/ml_engine.py`: carrega e executa o modelo `joblib`.
- `backend/app/infrastructure/csv_dataset_repository.py`: salva consultas de runtime em CSV local.
- `scripts/bootstrap_dataset.py`: coleta dataset inicial com `factcheckexplorer`.
- `scripts/normalize_dataset.py`: limpa, normaliza, deduplica e fortalece o dataset.
- `scripts/train_model.py`: treina `TF-IDF + Logistic Regression`.

## Fluxo Tecnico

1. Usuario envia uma afirmacao.
2. Frontend envia `POST /verify`.
3. Backend consulta Google Fact Check Tools API.
4. Havendo verificacao, retorna resultado oficial e salva consulta.
5. Sem verificacao externa, aplica regras contextuais curtas quando cabivel.
6. Quando nao ha regra contextual, chama o modelo local.
7. Modelo retorna `Verdadeiro`, `Falso` ou `Inconclusivo`.
8. Resultado e salvo em `data/runtime/consultas.csv`.

## Entregaveis Cobertos

- Codigo fonte: backend, frontend e scripts.
- Dataset utilizado: `data/raw/` e `data/processed/dataset_eleicoes.csv`.
- Modelo treinado: `backend/app/ml_models/modelo.pkl`.
- Documentacao: `README.md` e `docs/`.
- Apresentacao: `docs/ROTEIRO_APRESENTACAO.md` e `docs/Factum-Apresentacao.pptx`.
- Demonstracao: `./iniciar_tudo.ps1` inicia backend e frontend.

# Estrutura Completa do App (FactCheck-AI)

## Visao geral

```text
FactCheck-AI/
├── backend/
│   ├── .env
│   ├── .env.example
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── dependencies.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── application/
│   │   │   ├── ports.py
│   │   │   └── use_cases.py
│   │   ├── domain/
│   │   │   └── models.py
│   │   ├── infrastructure/
│   │   │   ├── csv_dataset_repository.py
│   │   │   ├── google_fact_check_provider.py
│   │   │   └── ml_claim_classifier.py
│   │   ├── services/
│   │   │   ├── google_api.py
│   │   │   └── ml_engine.py
│   │   └── ml_models/
│   └── tests/
│       ├── test_api.py
│       └── test_use_case.py
├── data/
│   ├── raw/
│   │   └── eleicoes.csv
│   └── processed/
│       └── dataset_eleicoes.csv
├── frontend/
│   ├── .env
│   ├── .env.example
│   ├── App.js
│   ├── index.js
│   ├── app.json
│   ├── package.json
│   └── assets/
├── scripts/
│   ├── bootstrap_dataset.py
│   ├── normalize_dataset.py
│   ├── train_model.py
│   └── ensure_model.py
├── doc/
│   ├── COMO_INICIAR.md
│   └── ESTRUTURA_COMPLETA.md
├── iniciar_tudo.ps1
└── README.md
```

## Responsabilidade por camada

### Backend (Clean Architecture)
- `api/`: entrada HTTP (FastAPI), validacao de request e resposta.
- `application/`: regras de caso de uso (fluxo API externa -> fallback ML -> persistencia).
- `domain/`: contratos e modelos de dominio.
- `infrastructure/`: adaptadores concretos (CSV, Google Fact Check, classificador ML).
- `services/`: implementacao tecnica de clientes e motor de inferencia.
- `ml_models/`: artefato treinado (`modelo.pkl`).

### Dados
- `data/raw/`: dataset bruto coletado (entrada).
- `data/processed/`: dataset limpo/normalizado usado no treino.

### Frontend
- `App.js`: tela principal e integracao com backend.
- `index.js`: ponto de entrada Expo/React Native.
- `.env`: URL da API para o ambiente atual.

### Scripts operacionais
- `bootstrap_dataset.py`: coleta dataset inicial com `factcheckexplorer`.
- `normalize_dataset.py`: limpeza de encoding, normalizacao e mapeamento de labels.
- `train_model.py`: treino do modelo e exportacao de `modelo.pkl`.
- `ensure_model.py`: garante existencia do modelo (treina se faltar).

## Fluxo operacional recomendado

1. Gerar dataset inicial.
2. Normalizar dataset.
3. Treinar modelo.
4. Subir backend.
5. Subir frontend.

## Entrypoints

- Backend: `backend/app/main.py`
- Frontend: `frontend/index.js`
- Rota principal de verificacao: `POST /verify`
- Health check: `GET /health`

# Estrutura do Projeto

```text
Factum/
├── backend/
│   ├── app/
│   │   ├── api/                 # Rotas, schemas e dependências FastAPI
│   │   ├── application/         # Caso de uso principal e portas
│   │   ├── domain/              # Modelos de resposta
│   │   ├── infrastructure/      # Adaptadores Google, classificador e CSV
│   │   ├── ml_models/           # modelo.pkl treinado
│   │   ├── services/            # Cliente Google e loader do modelo
│   │   └── main.py              # App FastAPI
│   ├── tests/                   # Testes de API e caso de uso
│   └── requirements.txt
├── data/
│   ├── raw/                     # Coleta bruta do factcheckexplorer
│   ├── processed/               # Dataset limpo usado no treino
│   └── runtime/                 # Consultas geradas em execução
├── docs/                        # Documentação e apresentação
├── frontend/                    # App React Native/Expo
├── scripts/                     # Coleta, normalização e treino
├── iniciar_tudo.ps1             # Inicialização completa
├── parar_tudo.ps1               # Encerramento das portas locais
├── pytest.ini                   # Configuração dos testes
└── README.md
```

## Responsabilidade por Camada

- `frontend/`: recebe a afirmação do usuário, chama `/verify` e exibe resultado, confiança, fonte e histórico local.
- `backend/app/api/`: expõe `/health` e `/verify`.
- `backend/app/application/`: orquestra regras contextuais, consulta externa e classificador local.
- `backend/app/services/google_api.py`: consulta a Google Fact Check Tools API.
- `backend/app/services/ml_engine.py`: carrega e executa o modelo `joblib`.
- `backend/app/infrastructure/csv_dataset_repository.py`: salva consultas de runtime em CSV local.
- `scripts/bootstrap_dataset.py`: coleta dataset inicial com `factcheckexplorer`.
- `scripts/normalize_dataset.py`: limpa, normaliza, deduplica e filtra o dataset.
- `scripts/train_model.py`: treina `TF-IDF + Logistic Regression`.

## Fluxo Técnico

1. Usuário envia uma afirmação.
2. Frontend envia `POST /verify`.
3. Backend aplica regras contextuais para perguntas sem contexto suficiente e fatos eleitorais simples.
4. Quando não há regra local aplicável, consulta a Google Fact Check Tools API.
5. Havendo verificação relevante, retorna o resultado externo.
6. Sem verificação externa, chama o classificador local.
7. O resultado volta como `Verdadeiro`, `Falso` ou `Inconclusivo`.
8. A consulta é salva em `data/runtime/consultas.csv`.

## Entregáveis

- Código fonte: backend, frontend e scripts.
- Dataset utilizado: `data/raw/` e `data/processed/dataset_eleicoes.csv`.
- Modelo treinado: `backend/app/ml_models/modelo.pkl`.
- Documentação: `README.md` e `docs/`.
- Apresentação: `docs/ROTEIRO_APRESENTACAO.md` e `docs/Factum-Apresentacao.pptx`.
- Demonstração: `.\iniciar_tudo.ps1` inicia backend e frontend.

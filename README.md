# Factum

Factum é uma aplicação de verificação de fatos voltada ao contexto eleitoral brasileiro. O projeto combina um app React Native/Expo, uma API FastAPI, consulta à Google Fact Check Tools API e um classificador local treinado com dados coletados por `factcheckexplorer`.

## Arquitetura

- **Frontend mobile/web:** React Native com Expo, em `frontend/`.
- **Backend Python:** FastAPI, em `backend/`.
- **Consulta externa:** Google Fact Check Tools API.
- **Classificador local:** pipeline `TF-IDF + Logistic Regression`.
- **Regras contextuais:** verificações curtas para fatos eleitorais básicos e perguntas sem contexto suficiente.
- **Dataset:** dados brutos em `data/raw/`, base processada em `data/processed/` e consultas locais geradas em `data/runtime/`.

## Fluxo da Aplicação

1. O usuário envia uma afirmação pelo app.
2. O backend aplica regras contextuais para perguntas sem contexto suficiente e fatos eleitorais simples.
3. Quando não há regra local aplicável, consulta a Google Fact Check Tools API.
4. Quando há uma checagem externa relevante, o resultado é retornado ao usuário.
5. Sem uma checagem externa confiável, o classificador local retorna `Verdadeiro`, `Falso` ou `Inconclusivo`.
6. As consultas feitas durante o uso são salvas localmente em `data/runtime/consultas.csv`.

## Como Rodar no Windows

Crie/configure `backend/.env` com sua chave:

```env
GOOGLE_API_KEY=sua_chave_aqui
GOOGLE_MIN_RELEVANCE_SCORE=0.45
CORS_ALLOW_ORIGINS=http://localhost:8081,http://127.0.0.1:8081
```

Depois, na raiz do projeto:

```powershell
.\iniciar_tudo.ps1
```

O script normaliza o dataset, garante o modelo treinado e abre:

- Backend: <http://127.0.0.1:8001>
- Frontend: <http://localhost:8081>

Para parar os serviços:

```powershell
.\parar_tudo.ps1
```

## Como Rodar Manualmente

Backend:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

Frontend:

```powershell
cd frontend
npm install
$env:EXPO_PUBLIC_API_BASE_URL="http://127.0.0.1:8001"
npx.cmd expo start --web --port 8081
```

## Dataset e Treinamento

O dataset inicial é coletado com `factcheckexplorer`, usando palavras-chave como:

- eleição
- bolsonaro
- lula
- pt
- campanha
- urna
- voto
- fraude

Pipeline:

```powershell
python scripts/bootstrap_dataset.py
python scripts/normalize_dataset.py
python scripts/train_model.py
```

O normalizador preserva o formato `texto, fonte, source_url, veredito, data, image_url, tags`, remove ruído, corrige textos, elimina conflitos de merge e prioriza o contexto eleitoral brasileiro.

Dataset atual normalizado:

- 478 linhas
- 422 exemplos `FALSO`
- 56 exemplos `VERDADEIRO`

Métricas do último treino:

- Accuracy: 0.9479
- Precision da classe verdadeira: 1.00
- Recall da classe verdadeira: 0.55
- F1-score da classe verdadeira: 0.71

As métricas também ficam em `data/processed/metrics.json`.

## Testes

Na raiz do projeto:

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

Resultado atual:

```text
21 passed
```

## Observação

O Factum é uma ferramenta de apoio. Resultados vindos de regras ou do classificador local não substituem uma checagem jornalística ou institucional; para afirmações fora das regras locais, o sistema prioriza verificações externas.

## Apresentação

- Roteiro: `docs/ROTEIRO_APRESENTACAO.md`
- PowerPoint: `docs/Factum-Apresentacao.pptx`

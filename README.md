# Factum - FactCheck-AI

Factum e uma aplicacao academica de verificacao de fatos no contexto eleitoral brasileiro. A solucao combina uma interface React Native/Expo, um backend FastAPI, consulta a Google Fact Check Tools API e um modelo local de Machine Learning treinado com dados coletados via `factcheckexplorer`.

## Arquitetura

- **Frontend mobile/web:** React Native com Expo, localizado em `frontend/`.
- **Backend Python:** FastAPI, localizado em `backend/`.
- **API externa:** Google Fact Check Tools API.
- **Machine Learning:** pipeline `TF-IDF + Logistic Regression`.
- **Regras contextuais:** validacoes curtas para fatos eleitorais basicos antes do fallback estatistico.
- **Dataset:** dados brutos em `data/raw/`, dataset de treino em `data/processed/` e consultas de runtime em `data/runtime/`.

## Fluxo da Aplicacao

1. O usuario envia uma afirmacao pelo app.
2. O backend consulta a Google Fact Check Tools API.
3. Se a API encontrar verificacao, o resultado oficial e retornado e salvo em `data/runtime/consultas.csv`.
4. Se a API nao encontrar verificacao, o backend aplica regras contextuais curtas e, quando nao houver regra, consulta o modelo local de Machine Learning.
5. O resultado estimado e retornado ao usuario e tambem salvo em `data/runtime/consultas.csv`.

## Como Rodar no Windows

Crie/configure `backend/.env` com sua chave:

```env
GOOGLE_API_KEY=sua_chave_aqui
CORS_ALLOW_ORIGINS=http://localhost:8081,http://127.0.0.1:8081
```

Depois, na raiz do projeto:

```powershell
./iniciar_tudo.ps1
```

O script normaliza o dataset, garante o modelo treinado e abre:

- Backend: <http://127.0.0.1:8001>
- Frontend: <http://localhost:8081>

Para parar os servicos:

```powershell
./parar_tudo.ps1
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

O dataset inicial e coletado com `factcheckexplorer`, usando palavras-chave como:

- eleicao
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

O normalizador remove ruido, corrige textos, elimina conflitos de merge e adiciona exemplos verdadeiros de ground truth eleitoral para reduzir o desbalanceamento.

Dataset atual normalizado:

- 507 linhas
- 451 exemplos `FALSO`
- 56 exemplos `VERDADEIRO`

Metricas do ultimo treino:

- Accuracy: 0.9804
- Precision classe verdadeira: 1.00
- Recall classe verdadeira: 0.82
- F1-score classe verdadeira: 0.90

## Testes

Na raiz do projeto:

```powershell
python -m pytest -q
```

Resultado esperado:

```text
16 passed
```

## Observacao Academica

Este sistema e experimental. A classificacao por Machine Learning nao garante veracidade absoluta; ela deve ser usada apenas como apoio a analise, priorizando verificacoes oficiais quando disponiveis.

## Apresentacao

- Roteiro: `docs/ROTEIRO_APRESENTACAO.md`
- PowerPoint: `docs/Factum-Apresentacao.pptx`

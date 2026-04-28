# Como Iniciar

## Execucao rapida

Na raiz do projeto:

```powershell
./iniciar_tudo.ps1
```

O script:

1. instala dependencias, se necessario;
2. normaliza `data/raw/eleicoes.csv` ou `data/raw/eleições.csv`;
3. garante que `backend/app/ml_models/modelo.pkl` exista;
4. inicia o backend em `http://127.0.0.1:8001`;
5. inicia o frontend web em `http://localhost:8081`.

Para encerrar:

```powershell
./parar_tudo.ps1
```

## Backend manual

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

Teste:

```powershell
Invoke-RestMethod http://127.0.0.1:8001/health
```

## Frontend manual

```powershell
cd frontend
npm install
$env:EXPO_PUBLIC_API_BASE_URL="http://127.0.0.1:8001"
npx.cmd expo start --web --port 8081
```

Abrir:

```text
http://localhost:8081
```

## Testes

Na raiz:

```powershell
python -m pytest -q
```

## Problemas comuns

- **Backend indisponivel:** confirme se a API esta em `http://127.0.0.1:8001/health`.
- **Frontend apontando para porta errada:** confirme `EXPO_PUBLIC_API_BASE_URL=http://127.0.0.1:8001`.
- **Modelo ausente:** rode `python scripts/normalize_dataset.py` e `python scripts/train_model.py`.
- **Chave Google ausente:** configure `GOOGLE_API_KEY` em `backend/.env`. Sem a chave, o sistema usa o fallback de ML.

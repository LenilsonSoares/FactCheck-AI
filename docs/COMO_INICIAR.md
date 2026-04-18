# Como iniciar o sistema

Este guia mostra os comandos minimos para rodar o projeto localmente no Windows usando VS Code.

## 1. Abrir terminal na raiz do projeto

Caminho esperado:

C:/Users/lenil/OneDrive/Documentos/GitHub/FactCheck-AI

## 1.1 Iniciar tudo com um comando (recomendado)

Na raiz do projeto:

./iniciar_tudo.ps1

Esse comando abre dois terminais automaticamente:

1. Backend em http://127.0.0.1:8001
2. Frontend em http://localhost:8081

Para parar os servicos de uma vez:

./parar_tudo.ps1

## 2. Iniciar o backend (FastAPI)

No terminal 1:

1. Entrar na pasta backend:

cd backend

2. Instalar dependencias (apenas na primeira vez):

c:/python314/python.exe -m pip install -r requirements.txt

3. Subir a API:

c:/python314/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload

4. Testar se esta online:

Abrir no navegador:
http://127.0.0.1:8001/health

## 3. Iniciar o frontend (Expo Web)

No terminal 2:

1. Entrar na pasta frontend:

cd frontend

2. Instalar dependencias (apenas na primeira vez):

npm install

3. Definir URL do backend para a sessao atual e iniciar web:

PowerShell:
$env:EXPO_PUBLIC_API_BASE_URL="http://127.0.0.1:8001"; npx.cmd expo start --web --port 8081

4. Abrir no navegador:
http://localhost:8081

## 4. Rodar testes do backend

No terminal da pasta backend:

c:/python314/python.exe -m pytest -q

## 5. Parar os servicos

1. No terminal do backend: Ctrl + C
2. No terminal do frontend: Ctrl + C

## 6. Erros comuns

1. Porta 8001 em uso:
   - Fechar processo que esta usando a porta 8001.
   - Tentar novamente iniciar o backend.

2. Mensagem "Backend indisponivel" no frontend:
   - Confirmar backend online em http://127.0.0.1:8001/health.
   - Confirmar frontend apontando para EXPO_PUBLIC_API_BASE_URL=http://127.0.0.1:8001.

3. Porta 8081 ocupada:
   - Iniciar frontend em outra porta, por exemplo 8082.

# FactCheck-AI

Sistema inteligente de verificação de fatos para contexto eleitoral, combinando:

- consulta em API externa de fact-check;
- fallback para modelo de Machine Learning local;
- armazenamento contínuo dos resultados em dataset local.

## Arquitetura da Solução

### Arquitetura limpa implementada no backend

Camadas:

- domain: contratos de entrada/saida da API.
- application: caso de uso principal de verificacao (regra de negocio).
- infrastructure: adaptadores concretos (Google API, modelo ML, repositorio CSV).
- api: rotas HTTP, validacao de request e injeção de dependencias.

Principais modulos:

- backend/app/main.py: inicializacao da API FastAPI e middleware CORS.
- backend/app/api/routes.py: endpoints health e verify.
- backend/app/application/use_cases.py: fluxo API externa -> fallback ML -> persistencia.
- backend/app/infrastructure/google_fact_check_provider.py: adaptador da API externa.
- backend/app/infrastructure/ml_claim_classifier.py: adaptador de inferencia ML.
- backend/app/infrastructure/csv_dataset_repository.py: persistencia no dataset local.

### 1) Interface Mobile (Frontend)

Responsável por:

- receber perguntas/afirmações do usuário;
- enviar a afirmação para o backend;
- exibir resultado (fonte, veredito e confiança).

Tecnologias possíveis:

- Flutter
- React Native
- Android nativo
- Progressive Web App (PWA)

### 2) Backend em Python

Responsável por:

- receber requisições da interface;
- consultar APIs externas de fact-check;
- executar o modelo de Machine Learning local;
- gerenciar o dataset de histórico.

Frameworks possíveis:

- Flask
- FastAPI
- Django

### 3) API de Fact Checking

API alvo:

- <https://toolbox.google.com/factcheck/apis>

## Fluxo Funcional Esperado

1. Usuário envia uma afirmação.
2. Backend consulta a API de fact-check.
3. Se existir verificação:

- resultado é retornado ao usuário;
- informação é armazenada no dataset local.

1. Se não existir verificação:

- backend consulta o modelo de Machine Learning;
- resultado estimado é retornado ao usuário;
- informação é armazenada no dataset local.

## Dataset Inicial

Antes do uso do sistema, deve existir dataset inicial de verificações.

Fonte de coleta:

- <https://github.com/GONZOsint/factcheckexplorer/>

Referência de implementação:

- <https://github.com/jeftegoes/GenerativeIA/tree/main/Examples/GoogleFastCheck>

Palavras-chave iniciais sugeridas (contexto eleitoral):

- eleicao
- bolsonaro
- lula
- pt
- campanha
- urna
- voto
- fraude

Objetivo do dataset:

- servir de base para treinamento inicial do modelo de Machine Learning;
- suportar melhoria contínua com novos registros das consultas da aplicação.

Script de bootstrap automatizado:

- scripts/bootstrap_dataset.py

Este script coleta dados com palavras-chave eleitorais e prepara a base inicial de verificacoes.

## Modelo de Machine Learning

A equipe deve treinar um classificador de afirmações/notícias.

Algoritmos possíveis:

- Naive Bayes
- Logistic Regression
- Random Forest
- Support Vector Machine
- Transformers (opcional)

Documentação obrigatória do modelo:

- como o dataset foi preparado;
- qual algoritmo foi usado;
- como o treinamento foi realizado;
- quais métricas foram utilizadas.

Métricas mínimas recomendadas:

- Accuracy
- Precision
- Recall
- F1-score

Script de treinamento atual:

- scripts/train_model.py

Saida do modelo:

- backend/app/ml_models/modelo.pkl

## Execucao do Projeto

### Backend

1. Criar e ativar ambiente virtual Python.
2. Instalar dependencias:

- pip install -r backend/requirements.txt

1. Configurar variaveis de ambiente no arquivo `backend/.env`:

- Base recomendada: copiar de `backend/.env.example` para `backend/.env`.

- `GOOGLE_API_KEY` (opcional para fluxo com API externa).
- `CORS_ALLOW_ORIGINS` (opcional, lista separada por virgula com origens permitidas; ex: `http://localhost:19006,http://127.0.0.1:19006`).

1. Iniciar servidor:

- uvicorn app.main:app --reload --app-dir backend

Endpoints:

- GET /health
- POST /verify

### Frontend

1. Entrar na pasta frontend.
2. Instalar dependencias do projeto mobile/web.
3. Configurar URL do backend via variavel de ambiente Expo:

- Base recomendada: copiar de `frontend/.env.example` para `frontend/.env`.

- `EXPO_PUBLIC_API_BASE_URL` (recomendado para Android fisico/emulador e iOS).

1. Executar aplicacao no emulador/dispositivo.

## Checklist para Entrega

- codigo-fonte versionado e executavel.
- dataset inicial e dataset processado.
- modelo treinado salvo em backend/app/ml_models.
- apresentacao com arquitetura, fluxo e metricas.
- demonstracao ao vivo com:
  - caso encontrado na API;
  - caso em fallback para modelo local.

## Entregáveis

Cada equipe deve entregar:

- código-fonte do projeto;
- dataset utilizado;
- modelo treinado;
- apresentação do projeto;
- demonstração da aplicação funcionando.

## Critérios de Avaliação

- Arquitetura da solução: 20%
- Implementação da aplicação: 25%
- Uso de Machine Learning: 25%
- Qualidade do dataset: 15%
- Apresentação e demonstração: 15%

## Observação Importante

O sistema possui caráter acadêmico e experimental.
A classificação por Machine Learning não garante veracidade absoluta, sendo uma ferramenta de apoio à análise.

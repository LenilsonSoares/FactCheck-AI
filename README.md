🛡️ Factum - FactCheck-AI
Factum é um ecossistema completo de verificação de fatos focado no contexto eleitoral brasileiro. A solução utiliza uma arquitetura híbrida que combina a Google Fact Check API com um modelo de Machine Learning local (Regressão Logística) para classificar afirmações como Verdadeiras ou Falsas.
🚀 Como Iniciar
Para facilitar a avaliação, o projeto conta com um script de automação que executa todo o pipeline de dados (coleta, normalização e treinamento) e inicia o backend.
Pré-requisitos
Python 3.10+
Node.js & npm (para o frontend)
Chave de API do Google Fact Check (configurada no .env)
Configuração Rápida (Windows)
No terminal da raiz do projeto, execute:
powershell
./iniciar_tudo.ps1
Use o código com cuidado.
Este script instalará as dependências, gerará o dataset inicial via factcheckexplorer, normalizará os dados, treinará a IA e iniciará o servidor.
🏗️ Arquitetura da Solução
O projeto foi desenvolvido seguindo os princípios da Clean Architecture (Arquitetura Limpa), dividido em:
Frontend (Mobile/Web): Desenvolvido em React Native (Expo), oferecendo uma interface responsiva e intuitiva.
Backend (API): Construído com FastAPI, utilizando Injeção de Dependência e Padrão Singleton para alta performance.
Core de ML: Motor de inferência baseado em Scikit-Learn com lógica de incerteza.
Pipeline de Dados: Scripts automatizados para coleta e tratamento de dados.
Fluxo de Verificação
O usuário envia uma afirmação pelo App.
O Backend consulta a Google Fact Check Tools API.
Se houver resposta oficial: O veredito é retornado com 100% de confiança.
Se não houver resposta: O Modelo de ML local assume a análise.
Segurança: Se a confiança da IA for inferior a 70%, o sistema retorna "Inconclusivo" para evitar a propagação de desinformação.
🧠 Inteligência Artificial
Algoritmo: Logistic Regression (Regressão Logística) com TF-IDF Vectorizer.
Dataset: Gerado via biblioteca factcheckexplorer com termos como Lula, Bolsonaro, Urna, Fraude.
Balanceamento: Aplicamos técnicas de Upsampling e adição manual de fatos históricos (Ground Truth) para mitigar o viés do dataset original.
Métricas Finais:
Acurácia: ~98%
F1-Score (Classe 1): 0.80
📂 Estrutura de Pastas
text
├── backend/          # API FastAPI e Lógica de ML
├── frontend/         # App React Native / Expo
├── data/             # Datasets (Raw e Processed)
├── scripts/          # Automação do Pipeline de Dados
└── doc/              # Documentação técnica
Use o código com cuidado.
👥 Equipe
Lenilson, Alex, Kayky, Alice, Ana Clara, Kauã, Paulo Henrique e Lorran.
# Roteiro de Apresentacao

## Slide 1 - Factum / FactCheck-AI

- Sistema academico de verificacao de fatos eleitorais.
- Combina API oficial de fact-checking e Machine Learning.
- Aviso: ferramenta experimental de apoio, nao veredito absoluto.

## Slide 2 - Problema

- Noticias falsas podem influenciar decisoes eleitorais.
- O usuario precisa verificar afirmacoes rapidamente.
- Nem toda afirmacao tem checagem pronta em uma API externa.

## Slide 3 - Arquitetura

- Frontend: React Native/Expo.
- Backend: Python com FastAPI.
- API externa: Google Fact Check Tools API.
- ML local: TF-IDF + Logistic Regression.
- Dados: dataset bruto, processado e consultas de runtime.

## Slide 4 - Fluxo da Aplicacao

1. Usuario envia uma afirmacao.
2. Backend consulta Google Fact Check.
3. Se existir verificacao, retorna resultado oficial.
4. Se nao existir, consulta o modelo local.
5. Resultado e salvo no CSV de consultas.

## Slide 5 - Dataset

- Coleta inicial com `factcheckexplorer`.
- Palavras-chave: eleicao, bolsonaro, lula, pt, campanha, urna, voto, fraude.
- Normalizacao remove ruido, conflitos de merge e labels invalidas.
- Dataset atual: 507 linhas, 451 falsas e 56 verdadeiras.

## Slide 6 - Machine Learning

- Vetorizacao textual com TF-IDF.
- Classificador: Logistic Regression.
- Balanceamento no treino com upsampling da classe minoritaria.
- Resultado possivel: Verdadeiro, Falso ou Inconclusivo.

## Slide 7 - Metricas

- Accuracy: 0.9804.
- Precision classe verdadeira: 1.00.
- Recall classe verdadeira: 0.82.
- F1-score classe verdadeira: 0.90.
- Observacao: metricas sao academicas e dependem da qualidade do dataset.

## Slide 8 - Demonstracao

- Rodar `./iniciar_tudo.ps1`.
- Abrir frontend em `http://localhost:8081`.
- Testar uma afirmacao com resultado da API.
- Testar uma afirmacao sem resultado externo para acionar o ML.

## Slide 9 - Conclusao

- A solucao cumpre o fluxo pedido na atividade.
- Usa dataset inicial, API externa, ML treinado e interface funcional.
- Melhorias futuras: dataset maior, modelos mais robustos e avaliacao humana dos resultados.

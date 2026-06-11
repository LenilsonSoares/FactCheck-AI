# Roteiro de Apresentação

## Slide 1 - Factum

- Verificador de fatos para afirmações do contexto eleitoral brasileiro.
- Combina checagem externa, regras contextuais e classificador local.
- A proposta é apoiar a análise, não substituir uma checagem jornalística ou institucional.

## Slide 2 - Problema

- Notícias falsas podem influenciar decisões eleitorais.
- O usuário precisa verificar afirmações rapidamente.
- Nem toda afirmação tem checagem pronta em uma API externa.

## Slide 3 - Arquitetura

- Frontend: React Native/Expo.
- Backend: Python com FastAPI.
- Consulta externa: Google Fact Check Tools API.
- Classificador local: TF-IDF + Logistic Regression.
- Dados: dataset bruto, dataset processado e consultas de runtime.

## Slide 4 - Fluxo da Aplicação

1. Usuário envia uma afirmação.
2. Backend aplica regras contextuais para perguntas sem contexto suficiente e fatos eleitorais simples.
3. Quando não há regra local aplicável, consulta o Google Fact Check.
4. Se existir verificação confiável, retorna o resultado externo.
5. Sem verificação externa, consulta o classificador local.
6. Resultado é salvo no CSV de consultas.

## Slide 5 - Dataset

- Coleta inicial com `factcheckexplorer`.
- Palavras-chave: eleição, bolsonaro, lula, pt, campanha, urna, voto, fraude.
- Normalização remove ruído, conflitos de merge e labels inválidas.
- Filtro leve prioriza contexto eleitoral brasileiro.
- Exemplos verdadeiros de apoio vêm de fontes institucionais como TSE e Constituição Federal.
- Dataset atual: 478 linhas, 422 falsas e 56 verdadeiras.

## Slide 6 - Classificador Local

- Vetorização textual com TF-IDF.
- Classificador: Logistic Regression.
- Balanceamento no treino com upsampling da classe minoritária.
- `class_weight="balanced"` reduz o impacto do desbalanceamento.
- Resultado possível: Verdadeiro, Falso ou Inconclusivo.
- Regras contextuais tratam fatos eleitorais simples antes da consulta externa ou do classificador.

## Slide 7 - Métricas

- Accuracy: 0.9479.
- Precision da classe verdadeira: 1.00.
- Recall da classe verdadeira: 0.55.
- F1-score da classe verdadeira: 0.71.
- Métricas salvas em `data/processed/metrics.json`.
- A leitura das métricas depende do tamanho e da qualidade do dataset.

## Slide 8 - Demonstração

- Rodar `.\iniciar_tudo.ps1`.
- Abrir frontend em `http://localhost:8081`.
- Testar uma afirmação com resultado externo.
- Testar uma afirmação sem resultado externo para acionar o classificador local.

## Slide 9 - Conclusão

- A solução entrega interface, API, dataset, treinamento e consulta externa.
- O fluxo combina regras contextuais, verificações externas e fallback local quando necessário.
- Melhorias futuras: dataset maior, revisão humana de amostras e avaliação contínua dos resultados.

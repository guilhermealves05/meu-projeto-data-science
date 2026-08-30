# Parte 2 - Modelagem Supervisionada
**Responsável:** Guilherme Monteiro

Este documento apresenta os resultados reais das execuções do pipeline de modelagem supervisionada (Regressão Linear Múltipla e Classificação Binária) aplicados à base diária da AVP2. Os modelos foram treinados com dados de 2017 a 2021 e validados com dados do ano de 2022 para evitar vazamento temporal.

---

## 1. Regressão Linear Múltipla

O objetivo deste modelo foi prever a energia média contínua a partir de variáveis climáticas (`ghi_media`, `temp_media`, `umidade_media`, `nuvens_media`, `vento_media`).

### 1.1. Métricas de Avaliação
* **R² (Coeficiente de Determinação):** 0.7082 (O modelo explica ~70.8% da variância da energia média gerada no ano de teste).
* **RMSE (Raiz do Erro Quadrático Médio):** 328.17 Wh.

### 1.2. Coeficientes do Modelo
* **Intercepto:** 940.45 Wh
* **ghi_media:** 15.67
* **temp_media:** -16.24
* **umidade_media:** -3.66
* **nuvens_media:** -4.35
* **vento_media:** -10.74

### 1.3. Interpretação Estatística (Ceteris Paribus)
Seguindo o princípio estatístico *ceteris paribus* (mantendo todas as outras variáveis constantes), os coeficientes indicam que:
* O aumento de 1 unidade na Irradiação Global Horizontal (GHI) está associado a um incremento médio de **15.67 Wh** na energia gerada.
* O aumento de 1 unidade na Temperatura Média está associado a uma redução média de **16.24 Wh** na energia gerada.

**Aviso de Causalidade:** É estritamente importante ressaltar que a regressão linear múltipla modela *correlações condicionais* entre as variáveis e a variável alvo. Os coeficientes refletem associações estatísticas e **não afirmam uma relação de causalidade direta**, visto que não houve intervenção controlada.

---

## 2. Classificação Binária (Machine Learning)

O objetivo desta etapa foi prever se um dia de 2022 seria de "alta geração" ou "baixa geração", usando a mediana do conjunto de treino (2017-2021) como limiar estrito para evitar *data leakage*. O processo utilizou um Pipeline com `StandardScaler` e `GridSearchCV` (5 dobras).

### 2.1. Resultados e Comparação de Modelos

| Métrica | Regressão Logística | KNN (K-Nearest Neighbors) |
| :--- | :--- | :--- |
| **Acurácia** | 93.83% | 90.75% |
| **Precisão** | 92.76% | 89.68% |
| **Recall** | 97.92% | 96.53% |
| **F1-Score** | 95.27% | 92.98% |

### 2.2. Melhores Hiperparâmetros Encontrados (GridSearchCV)
* **Regressão Logística:** `C = 10`, `class_weight = None`
* **KNN:** `n_neighbors = 15`, `p = 1` (Distância Manhattan), `weights = 'uniform'`

### 2.3. Matriz de Confusão (Teste - 2022)
* **Regressão Logística:** 141 Verdadeiros Positivos (TP), 72 Verdadeiros Negativos (TN), 11 Falsos Positivos (FP) e apenas 3 Falsos Negativos (FN).
* **KNN:** 139 Verdadeiros Positivos (TP), 67 Verdadeiros Negativos (TN), 16 Falsos Positivos (FP) e 5 Falsos Negativos (FN).

### 2.4. Conclusão
A **Regressão Logística** demonstrou ser o melhor classificador para este problema. Ela superou o KNN em todas as métricas observadas, destacando-se pelo altíssimo F1-Score (95.27%) e pelo Recall quase perfeito (97.92%), indicando que o modelo foi extremamente eficaz em identificar corretamente os dias de alta geração sem sacrificar a precisão geral.
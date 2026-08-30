# Modelagem Não Supervisionada e Análise de Causalidade
Responsável: Paulo Cosmo

## 1. Redução de Dimensionalidade (PCA)
Para compreender melhor a relação entre a geração de energia e as múltiplas variáveis climáticas (GHI, temperatura, umidade, nuvens e vento), aplicamos a Análise de Componentes Principais (PCA) após a padronização dos dados. 
* O Componente Principal 1 (PC1) explicou [X]% da variância dos dados.
* O Componente Principal 2 (PC2) explicou [X]% da variância.
* A Variância Acumulada preservada pelas duas novas dimensões foi de [X]%.

A projeção bidimensional pode ser visualizada no arquivo pca_projecao.png, onde os dias com perfis meteorológicos semelhantes aparecem mais próximos uns dos outros.

## 2. Agrupamento (K-Means)
Para identificar regimes climáticos diários consistentes, testamos diferentes números de clusters (K de 2 a 10). 
* A escolha do melhor K foi fundamentada pelo método do cotovelo (inércia) e apoiada pelo Silhouette Score. O valor escolhido foi K = [X], pois apresentou a melhor separação entre os grupos, conforme demonstrado no gráfico curva_cotovelo_kmeans.png.

Abaixo, os perfis médios de cada cluster em suas unidades originais:

| Cluster | Energia Média (Wh) | GHI Médio | Temp Média (°C) | Umidade Média (%) | Nuvens Médio | Vento Médio (km/h) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | [X] | [X] | [X] | [X] | [X] | [X] |
| 1 | [X] | [X] | [X] | [X] | [X] | [X] |

O gráfico clusters_kmeans.png ilustra como esses grupos se separam no espaço de duas dimensões criado pelo PCA.

## 3. Discussão: Causalidade vs. Correlação
É fundamental separar correlação (variáveis que variam juntas) de causalidade (uma variável provocando o comportamento da outra) e previsão (uso de dados passados para estimar o futuro). Embora exista uma forte correlação entre alta irradiação solar (GHI) e aumento da energia gerada, não podemos afirmar uma relação puramente causal e isolada sem considerar as variáveis de confusão (confundidores).

### 3.1 Possíveis Confundidores
No contexto de energia solar, diversos fatores mascaram as relações diretas, tais como:
* Temperatura: Dias com altíssima irradiação frequentemente apresentam altas temperaturas, que aquecem os painéis solares e diminuem sua eficiência, criando um efeito de confusão (mais sol, mas menor rendimento relativo).
* Sujidade e Manutenção: O acúmulo de poeira nos painéis ou paradas programadas para manutenção reduzem a geração de energia abruptamente, independentemente do cenário climático.
* Fatores Sazonais: Estações do ano e variação da duração do dia afetam o total diário, além da ocorrência de chuvas.

### 3.2 Decisão Operacional
Com base nos regimes climáticos (clusters) identificados, e compreendendo as limitações causais, propõe-se a seguinte decisão operacional focada em manutenção preditiva:
* A equipe de operação deve agendar manutenções e limpezas profundas dos painéis (sujidade) preferencialmente durante os dias pertencentes ao regime/cluster com menor perfil de geração e maior cobertura de nuvens/chuva. Dessa forma, a perda produtiva pela parada dos equipamentos será minimizada, aproveitando os dias onde o potencial natural já estaria comprometido pelo clima.

*(Nota: Esta decisão operacional assume que as manutenções podem ser flexibilizadas de acordo com previsões climáticas de curto prazo e é limitada pela incapacidade de isolar perfeitamente a queda de geração provocada por sujeira daquela provocada pelo clima, reforçando a importância do monitoramento in loco).*
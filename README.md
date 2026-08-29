# 🌱 Pipeline de Dados - Energia, Clima e Recursos Renováveis

> Projeto desenvolvido para a disciplina de **Ciência de Dados**, com foco na construção de um pipeline de tratamento e análise de dados relacionados à geração de energia renovável.

## 👥 Equipe

* Guilherme Alves
* Guilherme Monteiro
* Paulo Cosmo

**Disciplina:** Ciência de Dados
**Tema Escolhido:** Opção F - Energia, Clima e Recursos Renováveis

---

# 📖 Fundamentação Teórica e Análise de Domínio

## 1. Camada de Ingestão (Amostragem e Viés)

### População-Alvo vs. Estrutura de Acesso

### População-Alvo

O cenário ideal seria possuir um registro contínuo, universal e em tempo real de todas as instalações de painéis solares distribuídas em diferentes regiões climáticas e geográficas.

### Estrutura de Acesso

Os dados utilizados neste projeto foram obtidos por meio de um dataset disponível no Kaggle, representando um subconjunto específico de usinas solares no período entre **2017 e 2022**.

### Risco de Viés de Seleção

Existe um risco significativo de **viés de seleção**, pois os dados foram coletados em locais específicos, podendo representar principalmente regiões com alta incidência solar.

Como consequência, um modelo treinado apenas com este conjunto de dados pode apresentar baixo desempenho quando aplicado em regiões com elevada nebulosidade, chuvas frequentes ou condições climáticas diferentes das presentes no dataset.

---

# 2. Análise Exploratória e Tratamento Estatístico (EDA)

## Tratamento de Valores Nulos

Para os atributos numéricos ausentes foi utilizada a técnica de **imputação pela mediana**.

### Impacto no Viés

A imputação introduz um pequeno viés, já que assume que os valores ausentes seguem a tendência central dos dados, podendo ocultar eventos anômalos.

### Impacto na Variância

Por outro lado, essa estratégia reduz significativamente a variância do conjunto de dados, evitando a remoção de um grande número de registros e preservando a consistência da série temporal.

---

## Tratamento de Outliers

Foi aplicada uma adaptação da técnica do **Intervalo Interquartil (IQR)**.

Antes do cálculo dos quartis (Q1 e Q3), os dados referentes ao período noturno foram separados, impedindo que valores naturalmente iguais a zero influenciassem os limites estatísticos.

Dessa forma, apenas os registros diurnos participaram do cálculo dos limites para detecção de valores extremos.

---

# 3. Análise de Domínio (Inferência Causal)

## Relação estudada

**Radiação Solar (GHI) × Energia Gerada**

### Correlação não implica causalidade

Embora exista uma forte correlação entre a radiação solar (GHI) e a energia produzida, essa relação estatística não é suficiente para comprovar causalidade.

A correlação apenas indica que ambas variáveis variam conjuntamente, sem demonstrar o mecanismo físico responsável pela geração de energia.

---

## Variáveis de Confusão

### Temperatura

Dias com alta radiação solar geralmente apresentam temperaturas elevadas.

Entretanto, temperaturas excessivas reduzem a eficiência das células fotovoltaicas, interferindo diretamente na produção de energia.

### Sujidade dos Painéis

O acúmulo de poeira ou falta de manutenção reduz a quantidade de luz absorvida pelos painéis solares.

Assim, mesmo com elevada radiação solar, a geração de energia pode ser inferior ao esperado.

---

## Cenário *Ceteris Paribus*

Para demonstrar uma relação causal entre radiação solar e geração de energia seria necessário um experimento controlado, utilizando:

* Dois painéis solares idênticos;
* Mesma temperatura;
* Mesmo nível de limpeza;
* Mesmas condições ambientais.

Nesse cenário, apenas a intensidade da radiação seria alterada, permitindo isolar seu efeito sobre a produção de energia.

---

# 📊 Parte 2 - Inferência Estatística e Teste A/B

## 4. Unidade de Análise

A base tratada pelo pipeline atual possui **186.625 registros**. Para a análise inferencial, as medições de 15 em 15 minutos foram agrupadas por dia, considerando somente os períodos em que `isSun = 1`. A base analítica resultante possui **2.005 dias**, entre 01/01/2017 e 31/08/2022.

Essa agregação foi escolhida para reduzir a dependência entre observações consecutivas. Se cada medição de 15 minutos fosse tratada como independente, o tamanho efetivo da amostra seria artificialmente inflado e os intervalos poderiam parecer mais precisos do que realmente são.

A variável central é `energia_media`, definida como a média de `Energy delta[Wh]` durante as horas de sol em cada dia. Também foram calculadas as médias diárias de radiação, temperatura, umidade, nebulosidade, vento, chuva e neve, formando uma interface única para os demais modelos.

## 5. Estimação da Média e Bootstrap

Foram obtidas as seguintes estatísticas para `energia_media`:

| Medida | Resultado |
|---|---:|
| Tamanho da amostra (N) | 2.005 dias |
| Média amostral | 1.007,27 Wh |
| Desvio padrão amostral | 658,75 Wh |
| Erro padrão | 14,71 Wh |
| Assimetria amostral | 0,124 |

O Bootstrap foi executado com **5.000 réplicas**, reamostragem com reposição e semente aleatória 42. Em cada réplica foram sorteados 2.005 dias e calculada uma nova média. O intervalo não paramétrico corresponde aos percentis 2,5% e 97,5% dessas médias.

| Método do IC de 95% | Limite inferior | Limite superior |
|---|---:|---:|
| Bootstrap percentil | 978,41 Wh | 1.035,74 Wh |
| Aproximação normal | 978,44 Wh | 1.036,11 Wh |

Os intervalos são praticamente coincidentes. A diferença pequena entre os limites indica que, para esta amostra, a distribuição Bootstrap da média se aproxima bem da distribuição normal prevista pelo Teorema Central do Limite.

### Aplicação do Teorema Central do Limite

As condições do TCL são razoáveis porque a amostra possui 2.005 unidades diárias e a assimetria observada, 0,124, é baixa. Além disso, o agrupamento diário reduz a forte dependência existente entre medições vizinhas de 15 minutos.

Entretanto, a independência não é perfeita: dias consecutivos podem compartilhar o mesmo regime meteorológico, há sazonalidade ao longo dos anos e alguns dias possuem menos medições solares que outros. O dataset também não constitui uma amostra aleatória de todas as usinas solares. Portanto, os intervalos descrevem com maior segurança o contexto representado pela base, e não todas as instalações fotovoltaicas possíveis.

## 6. Teste A/B por Permutação

O objetivo foi verificar se a média diária de energia difere entre dois cenários meteorológicos mutuamente exclusivos:

* **Grupo A - dias claros:** `nuvens_media <= 30%`;
* **Grupo B - dias nublados:** `nuvens_media >= 70%`.

As hipóteses formais do teste bicaudal foram:

* **H₀:** μ<sub>claros</sub> = μ<sub>nublados</sub>;
* **H₁:** μ<sub>claros</sub> ≠ μ<sub>nublados</sub>;
* **Nível de significância:** α = 0,05.

| Resultado | Dias claros | Dias nublados |
|---|---:|---:|
| Quantidade de dias | 276 | 1.122 |
| Média de energia | 1.751,20 Wh | 639,19 Wh |

A estatística observada foi `média_claros - média_nublados = 1.112,01 Wh`. Para construir a distribuição esperada sob H₀, os rótulos dos 1.398 dias selecionados foram embaralhados **5.000 vezes**, preservando os tamanhos originais dos grupos. O valor-p bicaudal foi calculado pela proporção corrigida de permutações em que `|diferença simulada| >= |diferença observada|`.

O resultado foi **p = 0,000200**. Como `p < 0,05`, a decisão formal é **rejeitar H₀**. Os dados fornecem evidência estatística de diferença entre a geração média dos dias claros e nublados no conjunto analisado.

Na prática, o resultado indica que a previsão de nebulosidade pode apoiar o planejamento operacional: dias claros apresentam maior potencial de geração e dias muito nublados exigem previsões mais conservadoras ou fontes complementares. Isso não prova que a nebulosidade isoladamente causou toda a diferença, pois GHI, estação do ano, temperatura, duração do dia, chuva e condição dos painéis podem atuar como confundidores ou mediadores.

## 7. Reprodutibilidade da Inferência

As duas simulações usam `random_state=42`, tornando os resultados reproduzíveis. O comando `python main.py` reconstrói o CSV canônico na raiz, prepara a base diária, executa os 5.000 ciclos de cada procedimento, exibe todos os resultados no terminal e gera:

* `distribuicao_bootstrap.png` - histograma das médias Bootstrap, com os dois ICs de 95%;
* `distribuicao_permutacao.png` - distribuição sob H₀, com `±|diferença observada|`.

Os módulos de regressão, classificação e aprendizado não supervisionado seguem uma interface comum. Assim que os arquivos dos demais integrantes forem adicionados em `src/models/`, o orquestrador passará a executá-los automaticamente.

---

# ⚙️ Como Executar o Projeto

## 1. Instalação

Clone o repositório:

```bash
git clone https://github.com/guilhermealves05/meu-projeto-data-science.git
cd meu-projeto-data-science
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## 2. Configuração do Dataset

Por questões de tamanho do arquivo, o dataset original não é armazenado no repositório.

Crie a seguinte estrutura:

```
Projeto/
│
├── dados_brutos/
│   └── Renewable.csv
│
├── main.py
├── requirements.txt
└── README.md
```

Baixe o dataset:

**Renewable Power Generation and Weather Conditions**

Renomeie o arquivo para:

```
Renewable.csv
```

e coloque-o dentro da pasta:

```
dados_brutos/
```

---

## 3. Execução

Execute o pipeline utilizando:

```bash
python main.py
```

O processo realizará automaticamente:

* Extração dos dados;
* Tratamento de valores ausentes;
* Remoção de outliers utilizando IQR;
* Limpeza da base;
* Geração das visualizações exploratórias;
* Construção da base analítica diária;
* Bootstrap com dois intervalos de confiança;
* Teste A/B por permutação.

---

# 📊 Arquivos Gerados

Ao término da execução serão criados automaticamente:

```
dados_limpos_final.csv
```

Base de dados tratada e pronta para futuras análises.

```
distribuicao_bootstrap.png
distribuicao_permutacao.png
```

Gráficos inferenciais obrigatórios da Parte 2, gerados na raiz do projeto.

```
grafico_1_ciclo_diario.png
```

Análise do comportamento diário da geração de energia.

```
grafico_2_historico_mensal.png
```

Evolução mensal da geração ao longo dos anos.

```
grafico_3_dispersao_radiacao.png
```

Gráfico de dispersão entre radiação solar e energia gerada.

---

# 📂 Estrutura do Projeto

```
Projeto/
│
├── dados_brutos/
│   └── Renewable.csv
│
├── dados_limpos_final.csv
├── grafico_1_ciclo_diario.png
├── grafico_2_historico_mensal.png
├── grafico_3_dispersao_radiacao.png
├── distribuicao_bootstrap.png
├── distribuicao_permutacao.png
│
├── main.py
├── requirements.txt
├── README.md
└── src/
    ├── analysis_utils.py
    ├── inference/
    │   ├── bootstrap.py
    │   └── ab_testing.py
    ├── extract/extractor.py
    ├── transform/cleaner.py
    └── visualize.py
```

---

# 🛠️ Tecnologias Utilizadas

* Python
* Pandas
* NumPy
* Matplotlib

---

# 🎯 Objetivo

Construir um pipeline completo de Ciência de Dados capaz de:

* Realizar ingestão dos dados;
* Efetuar limpeza e tratamento estatístico;
* Identificar e tratar valores extremos;
* Produzir análises exploratórias;
* Gerar visualizações para apoio à tomada de decisão no contexto de geração de energia renovável.

---

# 📄 Licença

Projeto desenvolvido exclusivamente para fins acadêmicos na disciplina de **Ciência de Dados**.

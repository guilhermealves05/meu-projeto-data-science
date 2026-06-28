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
* Geração das visualizações.

---

# 📊 Arquivos Gerados

Ao término da execução serão criados automaticamente:

```
dados_limpos_final.csv
```

Base de dados tratada e pronta para futuras análises.

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
│
├── main.py
├── requirements.txt
└── README.md
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

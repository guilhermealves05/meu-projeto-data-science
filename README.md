# Pipeline de Dados: Energia, Clima e Recursos Renováveis

**Autores:** Guilherme Alves, Guilherme Monteiro, Paulo Cosmo
**Disciplina:** Ciência de Dados
**Tema Escolhido:** Opção F - Energia, Clima e Recursos Renováveis

---

## 3.1 Camada de Ingestão (Amostragem e Viés)

### População-Alvo vs. Estrutura de Acesso (Access Frame)
* **População-Alvo:** O ideal teórico seria obter um registo contínuo e universal de todas as instalações de painéis solares do mundo, sob todas as variações climáticas, geográficas e de hardware possíveis ao longo de décadas.
* **Estrutura de Acesso:** A nossa amostra real provém de um *dataset* disponibilizado no Kaggle, que representa um subconjunto limitado de centrais de geração num período de tempo específico e localizado.

### Risco de Viés de Seleção
Existe um forte risco de Viés de Seleção. Como os dados foram colhidos de centrais específicas, a amostra pode estar sobrerrepresentada por uma zona climática particular (por exemplo, regiões com alta incidência solar) ou por equipamentos de um fabricante específico. Isto significa que um modelo treinado com estes dados poderia subestimar a quebra de produção em painéis instalados em zonas mais frias, húmidas ou com tecnologia mais antiga.

---

## 3.2 Análise Exploratória e Tratamento Estatístico (EDA)

### Dicionário de Dados Consolidado
*Breve amostra da classificação das variáveis tratadas no pipeline:*

| Variável | Tipo de Dado (Programação) | Classificação Estatística |
| :--- | :--- | :--- |
| `Energy delta[Wh]` | Numérico (Float) | Contínua |
| `GHI` (Global Horizontal Irradiance) | Numérico (Float) | Contínua |
| `Weather Conditions` (Condição Climática) | String (Object) | Categórica Nominal |
| `Date/Time` | DateTime / String | Discreta / Categórica |

### Tratamento de Nulos (Viés vs Variância)
A nossa estratégia para valores nulos consistiu na **imputação pela mediana** para variáveis numéricas e rotulagem como "desconhecido" para variáveis categóricas.
* **Impacto no Viés:** A imputação introduz um pequeno viés (erro sistemático) ao assumir que as leituras ausentes se comportam de forma idêntica à tendência central da amostra, reduzindo artificialmente as flutuações naturais.
* **Impacto na Variância:** Por outro lado, esta abordagem reduz a variância ao manter o volume de dados elevado (evitando a exclusão massiva de linhas), o que torna futuras modelagens menos sensíveis a pequenas perturbações, preservando a estabilidade estrutural do *dataset*.

---

## 3.3 Análise de Domínio (Inferência Causal e Ceteris Paribus)

### Relação Hipotética Escolhida: Radiação Solar (GHI) e Energia Gerada
A hipótese de senso comum dita que quanto maior a radiação solar (GHI), maior a energia gerada pelos painéis.

**a) Correlação Matemática vs. Nexo de Causalidade**
Encontrar uma correlação estatística forte (ex: Pearson > 0.8) entre GHI e Energia Gerada apenas indica que ambas crescem juntas. No entanto, matematicamente, a correlação não distingue se *A causa B*, se *B causa A*, ou se *C causa A e B*. Para atestar causalidade, precisamos provar o mecanismo físico subjacente e excluir todas as outras explicações, o que uma simples fórmula matemática não consegue fazer por si só.

**b) Variáveis de Confusão (Confounders)**
Se ignorarmos outras métricas, a análise será enviesada. Duas variáveis de confusão críticas neste contexto são:
1. **Temperatura Ambiente/do Painel:** Dias de extrema radiação solar costumam ser dias de calor extremo. No entanto, o calor excessivo *reduz* a eficiência das células fotovoltaicas. Assim, a temperatura atua como um *confounder* que afeta simultaneamente a radiação disponível e corta o rendimento final.
2. **Sujidade/Poeira (Acumulação):** Zonas áridas têm muita radiação solar, mas também acumulam poeira rapidamente sobre os painéis, o que bloqueia a luz real absorvida, distorcendo a relação entre o que o sensor de clima regista e o que o painel efetivamente gera.

**c) Validação Causal sob o Cenário *Ceteris Paribus***
Para isolar o verdadeiro efeito causal exclusivo da Radiação Solar na Energia Gerada sob a ótica *Ceteris Paribus* ("mantendo tudo o resto constante"), teríamos de desenhar uma experiência controlada onde:
Dois painéis idênticos (mesmo modelo, mesma degradação) operam com a **mesma temperatura ambiente rigorosamente controlada**, **mesmo nível de limpeza** e **mesma inclinação**. Apenas uma variável (a quantidade de luz/radiação emitida) seria alterada. Só observando a variação de energia neste cenário perfeitamente isolado poderíamos atestar o nexo causal absoluto, sem a interferência térmica ou de manutenção.
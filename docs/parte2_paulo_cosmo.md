# Modelagem não supervisionada e discussão causal

Responsável pela contribuição: Paulo Cosmo. Resultados preenchidos e texto
consolidado na integração final, a partir da execução na base de 2.005 dias.

## PCA

Seis variáveis padronizadas: energia, GHI, temperatura, umidade, nuvens e vento.
PC1 explica **59,99%**, PC2 **16,37%**, acumulando **76,36%** da variância.
Na SVD `Z = U Σ Vᵀ`, V define as direções principais; as duas primeiras
maximizam variância preservada em 2D. Perdem-se 23,64% da variância.
Figura: `pca_projecao.png` na raiz.

## K-Means

Agrupamento nas seis variáveis padronizadas; semente 42 e n_init=20.
Inércia para k=1…10; silhouette para k=2…10. A curva cai de 12.030 para
6.607,36 de k=1 a 2 (45,08%); de 2 a 3 cai 15,86%. Adotamos **k=2** pela
inspeção do cotovelo, parcimônia e silhouette máxima de **0,3764**. O cotovelo
é gradual e não prova um ótimo único. Veja a discussão completa no README.
Figuras: `curva_cotovelo_kmeans.png` e `clusters_kmeans.png`, na raiz.

| Cluster | Energia (Wh) | GHI | Temperatura | Umidade (%) | Nuvens (%) | Vento |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 492,75 | 27,24 | 6,68 | 85,05 | 85,53 | 4,57 |
| 1 | 1.551,91 | 85,51 | 15,46 | 66,64 | 48,99 | 3,66 |

São unidades originais, sem conversão não documentada; GHI e vento não têm
unidade confirmada. Energia é média dos intervalos solares, não total diário.
Cluster 0: menor energia/radiação e mais nuvens/umidade; cluster 1: maior
energia/radiação e menos nuvens/umidade. Rótulos são arbitrários.

## Causalidade e operação

Associação, previsão e causalidade são distintas. Sazonalidade e temperatura
podem afetar radiação/produção; sujidade, manutenção e equipamentos são fatores
omitidos plausíveis. Não houve intervenção que isole efeitos. GHI pode mediar
parte da relação nuvens–energia.

Os perfis sugerem investigar manutenção eletiva em janelas de menor geração
esperada, com previsões meteorológicas e avaliação prospectiva. Energia
observada integra os clusters: eles não são previsões prontas do futuro.
Chuva não entrou nos atributos; não se pode chamá-los de chuvosos só pelas
nuvens. Segurança e reparos urgentes prevalecem sobre ganhos energéticos.

O README reúne a análise completa e limitações; `resultados_avp2.json`
registra variâncias, inércias, silhouettes, tamanhos e perfis da execução.

"""Confere a entrega local. Execute main.py antes para atualizar os resultados."""
import hashlib
import json
import math
from pathlib import Path

import matplotlib.image as mpimg
import pandas as pd

RAIZ = Path(__file__).resolve().parent
GRAFICOS = ['distribuicao_bootstrap.png', 'distribuicao_permutacao.png',
            'curva_cotovelo_kmeans.png', 'clusters_kmeans.png', 'pca_projecao.png']


def verificar(raiz=RAIZ):
    erros = []

    def exigir(condicao, mensagem):
        if not condicao:
            erros.append(mensagem)

    arquivos = ['README.md', 'requirements.txt', 'main.py', 'dados_limpos_final.csv',
                'dados_brutos/Renewable.csv', 'resultados_avp2.json',
                'src/inference/bootstrap.py', 'src/inference/ab_testing.py',
                'src/models/regression.py', 'src/models/machine_learning.py',
                'src/models/unsupervised.py', 'src/relatorio.py',
                'docs/parte2_guilherme_monteiro.md', 'docs/parte2_paulo_cosmo.md']
    for nome in arquivos + GRAFICOS:
        caminho = raiz / nome
        exigir(caminho.is_file() and caminho.stat().st_size > 0,
               f'Arquivo ausente ou vazio: {nome}')
    if erros:
        return erros

    for nome in GRAFICOS:
        try:
            pixels = mpimg.imread(raiz / nome)
            exigir(pixels.shape[0] >= 400 and pixels.shape[1] >= 600,
                   f'Gráfico pequeno demais: {nome}')
        except (OSError, ValueError) as erro:
            erros.append(f'PNG inválido: {nome}: {erro}')

    for nome in ['README.md', 'docs/parte2_guilherme_monteiro.md',
                 'docs/parte2_paulo_cosmo.md']:
        exigir('[X]' not in (raiz / nome).read_text(encoding='utf-8'),
               f'Resultado não preenchido em {nome}')

    r = json.loads((raiz / 'resultados_avp2.json').read_text(encoding='utf-8'))
    d, b, ab = r['dados'], r['bootstrap'], r['teste_ab']
    exigir(hashlib.sha256((raiz / 'dados_brutos/Renewable.csv').read_bytes()).hexdigest()
           == d['sha256_bruto'], 'O bruto mudou: execute main.py novamente.')
    exigir(d['linhas_brutas'] == 196776 and d['linhas_limpas'] == 186625,
           'Contagem de registros diferente da base documentada.')
    exigir(len(pd.read_csv(raiz / 'dados_limpos_final.csv')) == d['linhas_limpas'],
           'CSV limpo e JSON têm contagens divergentes.')
    exigir(d['dias'] == b['n'] == 2005, 'Contagem de dias divergente.')
    exigir(d['dias_treino'] == 1778 and d['dias_teste'] == 227,
           'Divisão treino/teste diferente da documentada.')
    exigir(ab['n_grupo_a'] + ab['n_grupo_b'] + d['dias_excluidos_ab'] == d['dias'],
           'Tamanhos dos grupos A/B inconsistentes.')
    exigir(b['n_boot'] >= 2000 and ab['n_perm'] >= 2000,
           'São necessárias pelo menos 2.000 réplicas de cada procedimento.')
    exigir(math.isclose(ab['p_valor'], (ab['permutacoes_extremas'] + 1)
                       / (ab['n_perm'] + 1)), 'Valor-p não corresponde às permutações.')
    exigir(abs(b['media_amostral'] - 1007.273819) < 0.01,
           'Média não corresponde ao relatório; revise a execução e o README.')
    exigir(abs(r['regressao']['r2'] - 0.7081746) < 0.001,
           'R² divergente do relatório.')
    exigir(abs(r['regressao']['rmse'] - 328.17428) < 0.1,
           'RMSE divergente do relatório.')
    for nome, m in r['classificacao'].items():
        (tn, fp), (fn, tp) = m['matriz_confusao']
        exigir(tn + fp + fn + tp == d['dias_teste'], f'{nome}: matriz inconsistente.')
        for chave, calculado in {
            'acuracia': (tn + tp) / (tn + fp + fn + tp),
            'precisao': tp / (tp + fp), 'recall': tp / (tp + fn),
            'f1': 2 * tp / (2 * tp + fp + fn),
        }.items():
            exigir(math.isclose(m[chave], calculado), f'{nome}: {chave} inconsistente.')
    u = r['nao_supervisionado']
    exigir(math.isclose(u['variancia_pc1'] + u['variancia_pc2'],
                       u['variancia_acumulada']), 'Variâncias do PCA inconsistentes.')
    exigir(abs(u['variancia_acumulada'] - 0.7636206) < 0.001,
           'PCA divergente do relatório.')
    exigir(u['k_escolhido'] == u['k_melhor_silhouette'] == 2,
           'Rever escolha de k e justificativa no relatório.')
    exigir(sum(u['tamanhos_clusters'].values()) == d['dias'],
           'Tamanhos dos clusters inconsistentes.')
    exigir(len(u['perfis_clusters']) == u['k_escolhido'], 'Perfis incompletos.')
    exigir(all(a >= b for a, b in zip(u['inercias'], u['inercias'][1:])),
           'Curva de inércia inesperada; verificar ajustes.')
    return erros


if __name__ == '__main__':
    try:
        pendencias = verificar()
    except (KeyError, ValueError, TypeError, OSError, ZeroDivisionError) as erro:
        pendencias = [f'Resultados inválidos ou incompletos: {erro}. Rode main.py novamente.']
    if pendencias:
        for pendencia in pendencias:
            print(f'ERRO: {pendencia}')
        raise SystemExit(1)
    print('ENTREGA LOCAL VALIDADA: cinco gráficos, módulos, documentos e métricas conferidos.')
    print('Ainda confira o GitHub na main e faça a submissão na plataforma da disciplina.')

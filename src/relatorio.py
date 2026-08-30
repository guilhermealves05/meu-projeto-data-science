"""Exportação das métricas da execução, sem caminhos locais nem amostras extensas."""
import hashlib
import json
import platform
from importlib.metadata import version

import numpy as np
import pandas as pd


def _json_default(valor):
    if isinstance(valor, np.generic):
        return valor.item()
    if isinstance(valor, np.ndarray):
        return valor.tolist()
    if isinstance(valor, pd.DataFrame):
        return valor.reset_index().to_dict(orient='records')
    raise TypeError(f'Tipo não serializável: {type(valor).__name__}')


def salvar_resultados(bruto, limpo, diario, bootstrap, ab, modelos, raiz):
    def resumir(resultado, excluir):
        return {chave: valor for chave, valor in resultado.items() if chave not in excluir}

    treino = diario.loc[diario['ano'] <= 2021]
    teste = diario.loc[diario['ano'] == 2022]
    resultado = {
        'ambiente': {'python': platform.python_version(), **{
            nome: version(nome) for nome in
            ['numpy', 'pandas', 'matplotlib', 'scikit-learn', 'seaborn']}},
        'dados': {
            'sha256_bruto': hashlib.sha256((raiz / 'dados_brutos' / 'Renewable.csv').read_bytes()).hexdigest(),
            'linhas_brutas': len(bruto), 'linhas_limpas': len(limpo),
            'dias': len(diario), 'inicio': str(diario['data'].min().date()),
            'fim': str(diario['data'].max().date()),
            'dias_treino': len(treino), 'dias_teste': len(teste),
            'mediana_energia_treino': float(treino['energia_media'].median()),
            'dias_excluidos_ab': len(diario) - ab['n_grupo_a'] - ab['n_grupo_b'],
            'alvo': 'Média das energias por intervalo solar retido de cada dia (Wh); não é total diário.',
        },
        'bootstrap': resumir(bootstrap, {'medias_bootstrap', 'grafico'}),
        'teste_ab': resumir(ab, {'diferencas_permutadas', 'grafico'}),
        'regressao': modelos['regressão'],
        'classificacao': modelos['classificação'],
        'nao_supervisionado': resumir(modelos['PCA e K-Means'], {'labels', 'centroides_padronizados'}),
    }
    (raiz / 'resultados_avp2.json').write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2, default=_json_default,
                   allow_nan=False) + '\n', encoding='utf-8')
    return resultado

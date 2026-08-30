"""Orquestrador do pipeline de dados e da análise estatística da AVP2."""

from __future__ import annotations

import logging
from pathlib import Path

from src.analysis_utils import preparar_base_diaria
from src.extract.extractor import realizar_ingestao
from src.inference.ab_testing import executar_teste_permutacao
from src.inference.bootstrap import executar_bootstrap
from src.models.regression import executar_regressao
from src.models.machine_learning import comparar_classificadores
from src.models.unsupervised import executar_nao_supervisionado
from src.relatorio import salvar_resultados
from src.transform.cleaner import realizar_transformacao
from src.visualize import gerar_visualizacao


RAIZ_PROJETO = Path(__file__).resolve().parent
CAMINHO_DADOS_BRUTOS = RAIZ_PROJETO / "dados_brutos" / "Renewable.csv"
CAMINHO_DADOS_LIMPOS = RAIZ_PROJETO / "dados_limpos_final.csv"
CAMINHO_BOOTSTRAP = RAIZ_PROJETO / "distribuicao_bootstrap.png"
CAMINHO_PERMUTACAO = RAIZ_PROJETO / "distribuicao_permutacao.png"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)


def _executar_modulos_da_equipe(df_diario) -> dict:
    """Na entrega final todas as etapas são obrigatórias, sem saltos silenciosos."""
    regressao = executar_regressao(df_diario)
    logging.info("Regressão | R²=%.4f | RMSE=%.2f Wh | intercepto=%.2f",
                 regressao['r2'], regressao['rmse'], regressao['intercepto'])
    logging.info("Coeficientes: %s", regressao['coeficientes'])
    classificacao = comparar_classificadores(df_diario)
    for nome, metricas in classificacao.items():
        logging.info("%s | acurácia=%.4f | precisão=%.4f | recall=%.4f | F1=%.4f",
                     nome, metricas['acuracia'], metricas['precisao'],
                     metricas['recall'], metricas['f1'])
        logging.info("%s | matriz=%s | parâmetros=%s", nome,
                     metricas['matriz_confusao'], metricas['melhores_parametros'])
    nao_supervisionado = executar_nao_supervisionado(df_diario, RAIZ_PROJETO)
    return {'regressão': regressao, 'classificação': classificacao,
            'PCA e K-Means': nao_supervisionado}


def _registrar_resultados_inferencia(bootstrap: dict, teste_ab: dict) -> None:
    ic_boot = bootstrap["ic_bootstrap_95"]
    ic_normal = bootstrap["ic_normal_95"]
    logging.info(
        "Bootstrap | N=%d | média=%.2f Wh | s=%.2f Wh | assimetria=%.3f",
        bootstrap["n"],
        bootstrap["media_amostral"],
        bootstrap["desvio_padrao_amostral"],
        bootstrap["assimetria_amostral"],
    )
    logging.info("IC 95%% Bootstrap: [%.2f; %.2f] Wh", *ic_boot)
    logging.info("IC 95%% normal: [%.2f; %.2f] Wh", *ic_normal)
    logging.info(
        "Teste A/B | claros: N=%d, média=%.2f Wh | nublados: N=%d, média=%.2f Wh",
        teste_ab["n_grupo_a"],
        teste_ab["media_grupo_a"],
        teste_ab["n_grupo_b"],
        teste_ab["media_grupo_b"],
    )
    logging.info(
        "H0: %s | H1: %s | diferença=%.2f Wh | p=%.6f | decisão: %s",
        teste_ab["h0"],
        teste_ab["h1"],
        teste_ab["diferenca_observada"],
        teste_ab["p_valor"],
        teste_ab["decisao"],
    )


def main() -> dict:
    logging.info("=== INICIANDO PIPELINE COMPLETO DA AVP2 ===")

    logging.info("Etapa 1/5 - Ingestão e limpeza dos dados")
    df_bruto = realizar_ingestao(str(CAMINHO_DADOS_BRUTOS))
    df_limpo = realizar_transformacao(df_bruto)

    logging.info("Etapa 2/5 - Exportação da base canônica")
    df_limpo.to_csv(CAMINHO_DADOS_LIMPOS, index=False)
    logging.info("Base limpa salva em: %s", CAMINHO_DADOS_LIMPOS)

    logging.info("Etapa 3/5 - Visualizações exploratórias da Parte 1")
    gerar_visualizacao(df_limpo, RAIZ_PROJETO / 'outputs')

    logging.info("Etapa 4/5 - Base diária e inferência estatística")
    df_diario = preparar_base_diaria(df_limpo)
    logging.info(
        "Base analítica diária criada: %d dias, de %s a %s.",
        len(df_diario),
        df_diario["data"].min().date(),
        df_diario["data"].max().date(),
    )
    resultado_bootstrap = executar_bootstrap(
        df_diario,
        n_boot=5_000,
        random_state=42,
        caminho_grafico=CAMINHO_BOOTSTRAP,
    )
    resultado_ab = executar_teste_permutacao(
        df_diario,
        n_perm=5_000,
        alpha=0.05,
        random_state=42,
        caminho_grafico=CAMINHO_PERMUTACAO,
    )
    _registrar_resultados_inferencia(resultado_bootstrap, resultado_ab)

    logging.info("Etapa 5/5 - Módulos analíticos da equipe")
    resultados_equipe = _executar_modulos_da_equipe(df_diario)

    salvar_resultados(df_bruto, df_limpo, df_diario, resultado_bootstrap,
                      resultado_ab, resultados_equipe, RAIZ_PROJETO)
    graficos = ['distribuicao_bootstrap.png', 'distribuicao_permutacao.png',
                'pca_projecao.png', 'curva_cotovelo_kmeans.png', 'clusters_kmeans.png']
    for nome in graficos:
        if not (RAIZ_PROJETO / nome).is_file():
            raise FileNotFoundError(f'Gráfico obrigatório ausente: {nome}')
    logging.info('Resultados completos: %s', RAIZ_PROJETO / 'resultados_avp2.json')

    logging.info("Gráfico Bootstrap: %s", CAMINHO_BOOTSTRAP)
    logging.info("Gráfico de permutação: %s", CAMINHO_PERMUTACAO)
    logging.info("=== PIPELINE CONCLUÍDO COM SUCESSO ===")
    return {
        "base_diaria": df_diario,
        "bootstrap": resultado_bootstrap,
        "teste_ab": resultado_ab,
        "modelos_equipe": resultados_equipe,
    }


if __name__ == "__main__":
    main()

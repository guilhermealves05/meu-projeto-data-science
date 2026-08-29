"""Estimativa da média de geração por Bootstrap e aproximação normal."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _validar_entrada(df_diario: pd.DataFrame, n_boot: int) -> np.ndarray:
    if "energia_media" not in df_diario.columns:
        raise ValueError("A base diária precisa conter a coluna energia_media.")
    if n_boot < 2_000:
        raise ValueError("O enunciado exige pelo menos 2.000 réplicas Bootstrap.")

    valores = pd.to_numeric(df_diario["energia_media"], errors="coerce").to_numpy()
    valores = valores[np.isfinite(valores)]
    if valores.size < 2:
        raise ValueError("São necessárias ao menos duas observações válidas.")
    return valores


def _reamostrar_medias(
    valores: np.ndarray, n_boot: int, gerador: np.random.Generator
) -> np.ndarray:
    """Gera as médias em blocos para limitar o consumo de memória."""
    replicas = np.empty(n_boot, dtype=float)
    tamanho_bloco = 250
    for inicio in range(0, n_boot, tamanho_bloco):
        fim = min(inicio + tamanho_bloco, n_boot)
        amostras = gerador.choice(
            valores, size=(fim - inicio, valores.size), replace=True
        )
        replicas[inicio:fim] = amostras.mean(axis=1)
    return replicas


def gerar_grafico_bootstrap(
    resultados: dict, caminho_saida: str | Path = "distribuicao_bootstrap.png"
) -> Path:
    """Salva o histograma e destaca os quatro limites dos ICs de 95%."""
    caminho = Path(caminho_saida)
    replicas = resultados["medias_bootstrap"]
    ic_boot = resultados["ic_bootstrap_95"]
    ic_normal = resultados["ic_normal_95"]

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.hist(replicas, bins=45, color="#3b82f6", alpha=0.72, edgecolor="white")
    ax.axvline(ic_boot[0], color="#b91c1c", linestyle="--", linewidth=2,
               label=f"IC Bootstrap: {ic_boot[0]:.2f} a {ic_boot[1]:.2f} Wh")
    ax.axvline(ic_boot[1], color="#b91c1c", linestyle="--", linewidth=2)
    ax.axvline(ic_normal[0], color="#166534", linestyle=":", linewidth=2.5,
               label=f"IC normal: {ic_normal[0]:.2f} a {ic_normal[1]:.2f} Wh")
    ax.axvline(ic_normal[1], color="#166534", linestyle=":", linewidth=2.5)
    ax.axvline(resultados["media_amostral"], color="#111827", linewidth=2,
               label=f"Média observada: {resultados['media_amostral']:.2f} Wh")
    ax.set_title("Distribuição Bootstrap da Média Diária de Energia")
    ax.set_xlabel("Média diária de energia durante as horas de sol (Wh)")
    ax.set_ylabel("Frequência das réplicas")
    ax.grid(axis="y", linestyle=":", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(caminho, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return caminho


def executar_bootstrap(
    df_diario: pd.DataFrame,
    n_boot: int = 5_000,
    random_state: int = 42,
    caminho_grafico: str | Path | None = "distribuicao_bootstrap.png",
) -> dict:
    """Calcula estatísticas amostrais e dois ICs de 95% para a média."""
    valores = _validar_entrada(df_diario, n_boot)
    n = int(valores.size)
    media = float(valores.mean())
    desvio = float(valores.std(ddof=1))
    erro_padrao = desvio / np.sqrt(n)
    gerador = np.random.default_rng(random_state)
    replicas = _reamostrar_medias(valores, n_boot, gerador)

    resultados = {
        "variavel": "energia_media",
        "unidade": "Wh",
        "n": n,
        "n_boot": int(n_boot),
        "media_amostral": media,
        "desvio_padrao_amostral": desvio,
        "erro_padrao": float(erro_padrao),
        "assimetria_amostral": float(pd.Series(valores).skew()),
        "ic_bootstrap_95": tuple(np.percentile(replicas, [2.5, 97.5]).astype(float)),
        "ic_normal_95": (float(media - 1.96 * erro_padrao), float(media + 1.96 * erro_padrao)),
        "medias_bootstrap": replicas,
        "random_state": int(random_state),
    }
    if caminho_grafico is not None:
        resultados["grafico"] = str(gerar_grafico_bootstrap(resultados, caminho_grafico))
    return resultados

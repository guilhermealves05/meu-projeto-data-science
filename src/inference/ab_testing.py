"""Teste A/B por permutação entre dias claros e dias nublados."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _extrair_grupos(df_diario: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    colunas = {"energia_media", "nuvens_media"}
    ausentes = sorted(colunas.difference(df_diario.columns))
    if ausentes:
        raise ValueError("A base diária não possui: " + ", ".join(ausentes))

    grupo_a = df_diario.loc[
        df_diario["nuvens_media"].le(30), "energia_media"
    ].to_numpy(dtype=float)
    grupo_b = df_diario.loc[
        df_diario["nuvens_media"].ge(70), "energia_media"
    ].to_numpy(dtype=float)
    grupo_a = grupo_a[np.isfinite(grupo_a)]
    grupo_b = grupo_b[np.isfinite(grupo_b)]
    if grupo_a.size < 2 or grupo_b.size < 2:
        raise ValueError("Os grupos A e B precisam ter ao menos duas observações cada.")
    return grupo_a, grupo_b


def gerar_grafico_permutacao(
    resultados: dict, caminho_saida: str | Path = "distribuicao_permutacao.png"
) -> Path:
    """Salva a distribuição nula e os dois limites da região observada."""
    caminho = Path(caminho_saida)
    diferencas = resultados["diferencas_permutadas"]
    modulo_observado = abs(resultados["diferenca_observada"])

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.hist(diferencas, bins=45, color="#7c3aed", alpha=0.72, edgecolor="white")
    ax.axvline(modulo_observado, color="#b91c1c", linewidth=2.5,
               label=f"Diferença observada: ±{modulo_observado:.2f} Wh")
    ax.axvline(-modulo_observado, color="#b91c1c", linewidth=2.5)
    ax.axvline(0, color="#111827", linestyle="--", linewidth=1.8,
               label="Centro esperado sob H₀")
    ax.set_title("Distribuição de Permutação sob a Hipótese Nula")
    ax.set_xlabel("Diferença de médias simulada: claros − nublados (Wh)")
    ax.set_ylabel("Frequência das permutações")
    ax.grid(axis="y", linestyle=":", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(caminho, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return caminho


def executar_teste_permutacao(
    df_diario: pd.DataFrame,
    n_perm: int = 5_000,
    alpha: float = 0.05,
    random_state: int = 42,
    caminho_grafico: str | Path | None = "distribuicao_permutacao.png",
) -> dict:
    """Testa H₀: μ_claros = μ_nublados contra H₁: μ_claros ≠ μ_nublados."""
    if n_perm < 2_000:
        raise ValueError("O enunciado exige pelo menos 2.000 permutações.")
    if not 0 < alpha < 1:
        raise ValueError("O nível de significância deve estar entre 0 e 1.")

    grupo_a, grupo_b = _extrair_grupos(df_diario)
    diferenca_observada = float(grupo_a.mean() - grupo_b.mean())
    combinados = np.concatenate([grupo_a, grupo_b])
    n_a = grupo_a.size
    gerador = np.random.default_rng(random_state)
    diferencas = np.empty(n_perm, dtype=float)

    for i in range(n_perm):
        embaralhados = gerador.permutation(combinados)
        diferencas[i] = embaralhados[:n_a].mean() - embaralhados[n_a:].mean()

    extremos = int(np.count_nonzero(np.abs(diferencas) >= abs(diferenca_observada)))
    # Correção de Monte Carlo evita reportar p = 0 com um número finito de permutações.
    p_valor = float((extremos + 1) / (n_perm + 1))
    rejeitar = p_valor < alpha
    resultados = {
        "grupo_a": "Dias claros (nuvens_media <= 30%)",
        "grupo_b": "Dias nublados (nuvens_media >= 70%)",
        "h0": "μ_claros = μ_nublados",
        "h1": "μ_claros ≠ μ_nublados",
        "alpha": float(alpha),
        "n_perm": int(n_perm),
        "n_grupo_a": int(grupo_a.size),
        "n_grupo_b": int(grupo_b.size),
        "media_grupo_a": float(grupo_a.mean()),
        "media_grupo_b": float(grupo_b.mean()),
        "diferenca_observada": diferenca_observada,
        "p_valor": p_valor,
        "permutacoes_extremas": extremos,
        "decisao": "rejeitar H0" if rejeitar else "não rejeitar H0",
        "rejeitar_h0": rejeitar,
        "diferencas_permutadas": diferencas,
        "random_state": int(random_state),
    }
    if caminho_grafico is not None:
        resultados["grafico"] = str(gerar_grafico_permutacao(resultados, caminho_grafico))
    return resultados

"""Funções compartilhadas pela camada analítica da AVP2."""

from __future__ import annotations

import pandas as pd


COLUNAS_OBRIGATORIAS = {
    "Time",
    "Energy delta[Wh]",
    "GHI",
    "temp",
    "humidity",
    "clouds_all",
    "wind_speed",
    "rain_1h",
    "snow_1h",
    "isSun",
}


def validar_colunas(df: pd.DataFrame, colunas: set[str]) -> None:
    """Interrompe a análise com uma mensagem clara quando faltam colunas."""
    ausentes = sorted(colunas.difference(df.columns))
    if ausentes:
        raise ValueError(
            "O conjunto de dados não possui as colunas obrigatórias: "
            + ", ".join(ausentes)
        )


def preparar_base_diaria(df: pd.DataFrame) -> pd.DataFrame:
    """Cria uma observação por dia a partir das medições com incidência solar.

    A agregação reduz a dependência temporal entre registros consecutivos de
    15 minutos. As médias preservam a escala original das variáveis e a coluna
    ``observacoes_solares`` permite identificar dias com cobertura incompleta.
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        raise ValueError("A base de entrada deve ser um DataFrame não vazio.")

    validar_colunas(df, COLUNAS_OBRIGATORIAS)
    base = df.copy()
    base["Time"] = pd.to_datetime(base["Time"], errors="coerce")

    datas_invalidas = int(base["Time"].isna().sum())
    if datas_invalidas:
        raise ValueError(
            f"A coluna Time possui {datas_invalidas} valor(es) que não puderam ser convertidos."
        )

    colunas_numericas = sorted(COLUNAS_OBRIGATORIAS.difference({"Time"}))
    for coluna in colunas_numericas:
        base[coluna] = pd.to_numeric(base[coluna], errors="coerce")

    nulos_numericos = base[colunas_numericas].isna().sum()
    nulos_numericos = nulos_numericos[nulos_numericos.gt(0)]
    if not nulos_numericos.empty:
        detalhes = ", ".join(f"{col}={qtd}" for col, qtd in nulos_numericos.items())
        raise ValueError(f"Foram encontrados valores numéricos inválidos: {detalhes}.")

    base = base.loc[base["isSun"].eq(1)].copy()
    if base.empty:
        raise ValueError("Não existem registros com isSun = 1 para formar a base diária.")

    base["data"] = base["Time"].dt.normalize()
    diario = (
        base.groupby("data", as_index=False)
        .agg(
            energia_media=("Energy delta[Wh]", "mean"),
            ghi_media=("GHI", "mean"),
            temp_media=("temp", "mean"),
            umidade_media=("humidity", "mean"),
            nuvens_media=("clouds_all", "mean"),
            vento_media=("wind_speed", "mean"),
            chuva_media=("rain_1h", "mean"),
            neve_media=("snow_1h", "mean"),
            observacoes_solares=("Energy delta[Wh]", "size"),
        )
        .sort_values("data")
        .reset_index(drop=True)
    )
    diario["ano"] = diario["data"].dt.year
    diario["mes"] = diario["data"].dt.month

    if diario["data"].duplicated().any():
        raise RuntimeError("A agregação produziu datas duplicadas inesperadamente.")
    if diario.isna().any().any():
        raise RuntimeError("A base diária ainda possui valores ausentes.")

    return diario

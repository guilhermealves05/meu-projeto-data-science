import pandas as pd
import logging

def padronizar_texto(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza strings categóricas para letras minúsculas e remove espaços em branco."""
    colunas_categoricas = df.select_dtypes(include=['object']).columns
    for col in colunas_categoricas:
        df[col] = df[col].astype(str).str.strip().str.lower()
    return df

def tratar_nulos(df: pd.DataFrame) -> pd.DataFrame:
    """Realiza a imputação de nulos utilizando a mediana para numéricos e 'desconhecido' para categorias."""
    colunas_numericas = df.select_dtypes(include=['number']).columns
    df[colunas_numericas] = df[colunas_numericas].fillna(df[colunas_numericas].median())
    
    colunas_categoricas = df.select_dtypes(include=['object']).columns
    df[colunas_categoricas] = df[colunas_categoricas].fillna('desconhecido')
    return df

def isolar_outliers_iqr(df: pd.DataFrame, colunas: list) -> pd.DataFrame:
    """Aplica o cálculo estatístico do IQR para remover outliers, 
       ajustado para não considerar os zeros (período noturno) como padrão."""
    df_limpo = df.copy()
    for col in colunas:
        if col in df_limpo.columns:
            # Pega apenas os valores do dia (maiores que zero) para fazer o cálculo justo
            valores_dia = df_limpo[df_limpo[col] > 0][col]
            
            # Só aplica o filtro se houver dados de dia suficientes
            if not valores_dia.empty:
                Q1 = valores_dia.quantile(0.25)
                Q3 = valores_dia.quantile(0.75)
                IQR = Q3 - Q1
                limite_inferior = Q1 - 1.5 * IQR
                limite_superior = Q3 + 1.5 * IQR
                
                # Regra mágica: Mantém as noites (== 0) E mantém os dias dentro do limite normal
                df_limpo = df_limpo[(df_limpo[col] == 0) | ((df_limpo[col] >= limite_inferior) & (df_limpo[col] <= limite_superior))]
                
    return df_limpo

def realizar_transformacao(df: pd.DataFrame) -> pd.DataFrame:
    logging.info("Iniciando limpeza e sanitização dos dados (Nulos, Encoding e IQR)...")
    
    df = padronizar_texto(df)
    df = tratar_nulos(df)
    
    # Aplica o filtro IQR nas colunas numéricas
    colunas_numericas = df.select_dtypes(include=['number']).columns.tolist()
    df = isolar_outliers_iqr(df, colunas_numericas)
    
    linhas, colunas = df.shape
    logging.info(f"Volumetria após tratamento -> Linhas: {linhas} | Colunas: {colunas}")
    
    return df
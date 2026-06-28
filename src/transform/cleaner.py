import pandas as pd
import logging

def padronizar_texto(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza strings categóricas para letras minúsculas e remove espaços em branco."""
    colunas_categoricas = df.select_dtypes(include=['object']).columns
    for col in colunas_categoricas:
        df[col] = df[col].astype(str).str.strip().str.lower()
    return df

def tratar_nulos(df: pd.DataFrame) -> pd.DataFrame:
    """Realiza a imputation de nulos utilizando a mediana agrupada por HORA 
       para manter o perfil do ciclo diário e evita distorções noturnas."""
    df_tratado = df.copy()
    
    # Se a coluna hour não existir diretamente, tentamos extrair do Time
    if 'hour' not in df_tratado.columns and 'Time' in df_tratado.columns:
        df_tratado['hour'] = pd.to_datetime(df_tratado['Time']).dt.hour
    
    colunas_numericas = df_tratado.select_dtypes(include=['number']).columns
    
    # Se tivermos a coluna 'hour', preenchemos pela mediana daquela hora específica
    if 'hour' in df_tratado.columns:
        for col in colunas_numericas:
            if col != 'hour':
                # Preenche o nulo com a mediana dos dados que pertencem à mesma hora do dia
                df_tratado[col] = df_tratado.groupby('hour')[col].transform(lambda x: x.fillna(x.median()))
    
    # Backup de segurança: Se ainda sobrar algum nulo (ex: coluna inteira vazia), usa a mediana global
    df_tratado[colunas_numericas] = df_tratado[colunas_numericas].fillna(df_tratado[colunas_numericas].median())
    
    # Trata colunas de texto (categorias)
    colunas_categoricas = df_tratado.select_dtypes(include=['object']).columns
    df_tratado[colunas_categoricas] = df_tratado[colunas_categoricas].fillna('desconhecido')
    
    return df_tratado

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
                
                # Regra: Mantém as noites (== 0) E mantém os dias dentro do limite normal
                df_limpo = df_limpo[(df_limpo[col] == 0) | ((df_limpo[col] >= limite_inferior) & (df_limpo[col] <= limite_superior))]
                
    return df_limpo

def realizar_transformacao(df: pd.DataFrame) -> pd.DataFrame:
    logging.info("Iniciando limpeza e sanitização dos dados (Nulos, Encoding e IQR)...")
    
    df = padronizar_texto(df)
    df = tratar_nulos(df)
    
    # CORREÇÃO DO BUG: Restringe o IQR apenas para variáveis físicas contínuas.
    # Evita aplicar IQR em variáveis de tempo/metadados como 'hour', 'month' ou 'isSun'
    colunas_para_iqr = ['Energy delta[Wh]', 'GHI', 'temp', 'pressure', 'humidity', 'wind_speed']
    df = isolar_outliers_iqr(df, colunas_para_iqr)
    
    linhas, colunas = df.shape
    logging.info(f"Volumetria após tratamento -> Linhas: {linhas} | Colunas: {colunas}")
    
    return df
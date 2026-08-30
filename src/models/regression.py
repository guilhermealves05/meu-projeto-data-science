import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

def executar_regressao(df_diario):
    """
    Executa a regressão múltipla da AVP2 com separação temporal.
    Y: energia_media
    X: ghi_media, temp_media, umidade_media, nuvens_media, vento_media
    """
    # 1. Copia o dataframe para evitar avisos do pandas
    df = df_diario.copy()
    
    # 2. Preparação das variáveis
    X_cols = ['ghi_media', 'temp_media', 'umidade_media', 'nuvens_media', 'vento_media']
    y_col = 'energia_media'
    
    # 3. Separação temporal (Treino 2017-2021; Teste 2022) usando a coluna 'data'
    df['ano'] = pd.to_datetime(df['data']).dt.year
    
    treino = df[df['ano'] <= 2021]
    teste = df[df['ano'] == 2022]
    
    X_treino = treino[X_cols]
    y_treino = treino[y_col]
    X_teste = teste[X_cols]
    y_teste = teste[y_col]
    
    # 4. Modelagem
    modelo = LinearRegression()
    modelo.fit(X_treino, y_treino)
    
    # 5. Avaliação apenas no teste
    predicoes = modelo.predict(X_teste)
    r2 = r2_score(y_teste, predicoes)
    rmse = np.sqrt(mean_squared_error(y_teste, predicoes))
    
    # 6. Formatação dos coeficientes
    coeficientes = dict(zip(X_cols, modelo.coef_))
    
    # Retorna o dicionário exigido pela equipe
    resultados_regressao = {
        'intercepto': modelo.intercept_,
        'coeficientes': coeficientes,
        'r2': r2,
        'rmse': rmse
    }
    
    return resultados_regressao
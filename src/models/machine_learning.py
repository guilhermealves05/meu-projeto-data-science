import pandas as pd
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

def comparar_classificadores(df_diario):
    """
    Executa a classificação binária de alta_geracao comparando Logística e KNN.
    """
    df = df_diario.copy()
    
    # 1. Preparação das variáveis
    X_cols = ['ghi_media', 'temp_media', 'umidade_media', 'nuvens_media', 'vento_media']
    y_col = 'energia_media'
    
    # 2. Separação temporal (Treino 2017-2021; Teste 2022)
    df['ano'] = pd.to_datetime(df['data']).dt.year
    treino = df[df['ano'] <= 2021].copy()
    teste = df[df['ano'] == 2022].copy()
    
    # 3. Criação do Target (Alta Geração)
    # REGRA CRÍTICA: Calcular mediana APENAS no treino e aplicar esse limiar no teste
    mediana_treino = treino[y_col].median()
    treino['alta_geracao'] = (treino[y_col] > mediana_treino).astype(int)
    teste['alta_geracao'] = (teste[y_col] > mediana_treino).astype(int)
    
    X_treino = treino[X_cols]
    y_treino = treino['alta_geracao']
    X_teste = teste[X_cols]
    y_teste = teste['alta_geracao']
    
    # Validação cruzada estratificada com 5 dobras
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    # ==========================================
    # MODELO 1: Regressão Logística
    # ==========================================
    pipe_lr = Pipeline([
        ('scaler', StandardScaler()),
        ('lr', LogisticRegression(max_iter=2000, random_state=42))
    ])
    
    grid_lr = {
        'lr__C': [0.1, 1, 10],
        'lr__class_weight': [None, 'balanced']
    }
    
    gs_lr = GridSearchCV(pipe_lr, grid_lr, cv=cv, scoring='f1', n_jobs=-1)
    gs_lr.fit(X_treino, y_treino)
    
    # ==========================================
    # MODELO 2: KNN
    # ==========================================
    pipe_knn = Pipeline([
        ('scaler', StandardScaler()),
        ('knn', KNeighborsClassifier())
    ])
    
    grid_knn = {
        'knn__n_neighbors': [3, 5, 7, 11, 15],
        'knn__weights': ['uniform', 'distance'],
        'knn__p': [1, 2]
    }
    
    gs_knn = GridSearchCV(pipe_knn, grid_knn, cv=cv, scoring='f1', n_jobs=-1)
    gs_knn.fit(X_treino, y_treino)
    
    # ==========================================
    # Avaliação no Teste e Retorno
    # ==========================================
    def avaliar_modelo(modelo, X_t, y_t):
        preds = modelo.predict(X_t)
        return {
            'melhores_parametros': modelo.best_params_,
            'matriz_confusao': confusion_matrix(y_t, preds).tolist(),
            'acuracia': accuracy_score(y_t, preds),
            'precisao': precision_score(y_t, preds),
            'recall': recall_score(y_t, preds),
            'f1': f1_score(y_t, preds)
        }
        
    resultados_classificacao = {
        'regressao_logistica': avaliar_modelo(gs_lr, X_teste, y_teste),
        'knn': avaliar_modelo(gs_knn, X_teste, y_teste)
    }
    
    return resultados_classificacao
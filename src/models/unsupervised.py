import pandas as pd
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

def executar_nao_supervisionado(df_diario):
    print("\n--- Iniciando Análise Não Supervisionada (Paulo Cosmo) ---")
    
    
    resultados = {}
    
   
    colunas_selecionadas = ['energia_media', 'ghi_media', 'temp_media', 'umidade_media', 'nuvens_media', 'vento_media']
    df_selecionado = df_diario[colunas_selecionadas].copy()

    
    scaler = StandardScaler()
    dados_padronizados = scaler.fit_transform(df_selecionado)

   
    pca = PCA(n_components=2)
    pca_componentes = pca.fit_transform(dados_padronizados)

   
    var_pc1 = pca.explained_variance_ratio_[0]
    var_pc2 = pca.explained_variance_ratio_[1]
    var_acumulada = var_pc1 + var_pc2

    
    resultados['variancia_pc1'] = var_pc1
    resultados['variancia_pc2'] = var_pc2
    resultados['variancia_acumulada'] = var_acumulada

    print(f"Variância explicada pelo PC1: {var_pc1:.4f}")
    print(f"Variância explicada pelo PC2: {var_pc2:.4f}")
    print(f"Variância acumulada (Total salvo): {var_acumulada:.4f}")

    
    plt.figure(figsize=(8, 6))
    plt.scatter(pca_componentes[:, 0], pca_componentes[:, 1], alpha=0.5, c='blue')
    plt.xlabel(f'Componente Principal 1 (PC1) - {var_pc1*100:.1f}%')
    plt.ylabel(f'Componente Principal 2 (PC2) - {var_pc2*100:.1f}%')
    plt.title('Projeção PCA - Energia e Variáveis Climáticas')
    plt.grid(True)
    plt.savefig('pca_projecao.png')
    plt.close()
    print("Gráfico 'pca_projecao.png' gerado com sucesso!")

    
    inercias = []
    silhouettes = []
    K_range = range(2, 11)

    for k in K_range:
        # random_state=42 e n_init=20 são obrigatórios pelo documento
        kmeans_temp = KMeans(n_clusters=k, random_state=42, n_init=20)
        kmeans_temp.fit(dados_padronizados)
        inercias.append(kmeans_temp.inertia_)
        silhouettes.append(silhouette_score(dados_padronizados, kmeans_temp.labels_))
    
    resultados['inercias'] = inercias
    resultados['silhouettes'] = silhouettes

    
    fig, ax1 = plt.subplots(figsize=(8, 6))
    
    color = 'tab:red'
    ax1.set_xlabel('Número de Clusters (k)')
    ax1.set_ylabel('Inércia', color=color)
    ax1.plot(K_range, inercias, marker='o', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_xticks(K_range)

    ax2 = ax1.twinx()  
    color = 'tab:blue'
    ax2.set_ylabel('Silhouette Score', color=color)  
    ax2.plot(K_range, silhouettes, marker='s', color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('Método do Cotovelo e Silhouette Score')
    fig.tight_layout()  
    plt.savefig('curva_cotovelo_kmeans.png')
    plt.close()
    print("Gráfico 'curva_cotovelo_kmeans.png' gerado com sucesso!")

    
    k_escolhido = K_range[silhouettes.index(max(silhouettes))]
    print(f"\nO K escolhido justificado pelo maior Silhouette Score foi: {k_escolhido}")
    
    kmeans_final = KMeans(n_clusters=k_escolhido, random_state=42, n_init=20)
    labels = kmeans_final.fit_predict(dados_padronizados)
    
    resultados['k_escolhido'] = k_escolhido
    resultados['labels'] = labels
    resultados['centroides_padronizados'] = kmeans_final.cluster_centers_

    
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(pca_componentes[:, 0], pca_componentes[:, 1], c=labels, cmap='viridis', alpha=0.6)
    plt.xlabel('Componente Principal 1 (PC1)')
    plt.ylabel('Componente Principal 2 (PC2)')
    plt.title(f'Clusters K-Means (k={k_escolhido}) Projetados no PCA')
    plt.colorbar(scatter, label='Cluster')
    plt.savefig('clusters_kmeans.png')
    plt.close()
    print("Gráfico 'clusters_kmeans.png' gerado com sucesso!")

    
    centroides_padronizados = kmeans_final.cluster_centers_
    
    centroides_originais = scaler.inverse_transform(centroides_padronizados)
    
    perfis_df = pd.DataFrame(centroides_originais, columns=colunas_selecionadas)
    perfis_df.index.name = 'Cluster'
    resultados['perfis_clusters'] = perfis_df
    
    print("\nPerfil dos clusters (médias nas unidades originais):")
    print(perfis_df)
    
    return resultados
import logging
import os
from src.extract.extractor import realizar_ingestao
from src.transform.cleaner import realizar_transformacao
from src.visualize import gerar_visualizacao

# ==========================================
# CONFIGURAÇÕES GLOBAIS DO PIPELINE
# ==========================================
CAMINHO_DADOS_BRUTOS = "dados_brutos/Renewable.csv"
DIRETORIO_OUTPUT = "outputs"
CAMINHO_DADOS_LIMPOS = os.path.join(DIRETORIO_OUTPUT, "dados_limpos_final.csv")

# Configura o log global do orquestrador
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')

def main():
    logging.info("=== INICIANDO PIPELINE DE DADOS ===")
    
    # 1. Camada de Ingestão
    df_bruto = realizar_ingestao(CAMINHO_DADOS_BRUTOS)
    
    # 2. Camada de Transformação (EDA)
    df_limpo = realizar_transformacao(df_bruto)
    
    # 3. Exportação da Base Consolidada
    os.makedirs(DIRETORIO_OUTPUT, exist_ok=True)
    df_limpo.to_csv(CAMINHO_DADOS_LIMPOS, index=False)
    logging.info(f"Ficheiro final automatizado gerado em: {CAMINHO_DADOS_LIMPOS}")
    
    # 4. Camada de Visualização
    gerar_visualizacao(df_limpo)
    
    logging.info("=== PIPELINE CONCLUÍDO COM SUCESSO ===")

if __name__ == "__main__":
    main()
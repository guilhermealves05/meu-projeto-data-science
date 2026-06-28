import logging
import os
from src.extract.extractor import realizar_ingestao
from src.transform.cleaner import realizar_transformacao
from src.visualize import gerar_visualizacao

# Configura o log global do orquestrador
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')

def main():
    logging.info("=== INICIANDO PIPELINE DE DADOS ===")
    
    # 1. Camada de Ingestão
    caminho_csv = "dados_brutos/Renewable.csv" 
    df_bruto = realizar_ingestao(caminho_csv)
    
    # 2. Camada de Transformação (EDA)
    df_limpo = realizar_transformacao(df_bruto)
    
    # 3. Exportação da Base Consolidada (Criando a pasta outputs)
    diretorio_output = "outputs"
    os.makedirs(diretorio_output, exist_ok=True)
    
    caminho_final = os.path.join(diretorio_output, "dados_limpos_final.csv")
    df_limpo.to_csv(caminho_final, index=False)
    logging.info(f"Arquivo final automatizado gerado em: {caminho_final}")
    
    # 4. Camada de Visualização
    gerar_visualizacao(df_limpo)
    
    logging.info("=== PIPELINE CONCLUÍDO COM SUCESSO ===")

if __name__ == "__main__":
    main()
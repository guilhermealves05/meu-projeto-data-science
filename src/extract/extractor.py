import pandas as pd
import logging
import sys

def realizar_ingestao(caminho_arquivo: str) -> pd.DataFrame:
    try:
        logging.info(f"Iniciando a leitura do arquivo: {caminho_arquivo}")
        df = pd.read_csv(caminho_arquivo)
        
        # Registra a volumetria bruta
        linhas, colunas = df.shape
        logging.info("Leitura concluída com sucesso!")
        logging.info(f"Volumetria bruta -> Linhas: {linhas} | Colunas: {colunas}")
        
        return df
        
    except FileNotFoundError:
        logging.error(f"Falha de caminho: O arquivo '{caminho_arquivo}' não foi encontrado.")
        sys.exit(1)
        
    except Exception as e:
        logging.error(f"Erro inesperado durante a ingestão: {e}")
        sys.exit(1)
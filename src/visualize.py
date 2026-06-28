import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import logging
import os

def gerar_visualizacao(df: pd.DataFrame):
    logging.info("Iniciando geração do pacote completo de visualizações (Dashboard)...")
    
    # Garante que a pasta outputs existe antes de salvar os gráficos
    diretorio_output = "outputs"
    os.makedirs(diretorio_output, exist_ok=True)
    
    df_plot = df.copy()
    
    # 1. Preparação do Tempo
    if 'Time' in df_plot.columns:
        df_plot['Time'] = pd.to_datetime(df_plot['Time'])
    else:
        col_tempo = [col for col in df_plot.columns if 'time' in col.lower()][0]
        df_plot['Time'] = pd.to_datetime(df_plot[col_tempo])
        
    coluna_energia = [col for col in df_plot.columns if 'energy' in col.lower()][0]
    
    # =====================================================================
    # GRÁFICO 1: O Ciclo Diário Ideal (Média por Hora do Dia)
    # =====================================================================
    logging.info("Gerando Gráfico 1: Ciclo Diário...")
    df_plot['Hora'] = df_plot['Time'].dt.hour
    df_media_hora = df_plot.groupby('Hora')[coluna_energia].mean().reset_index()
    
    plt.figure(figsize=(10, 5))
    plt.plot(df_media_hora['Hora'], df_media_hora[coluna_energia], color='#ff7f0e', marker='o', linewidth=2.5)
    plt.fill_between(df_media_hora['Hora'], df_media_hora[coluna_energia], color='#ff7f0e', alpha=0.3)
    
    plt.title('1. Ciclo Diário Médio: Geração de Energia por Hora do Dia', fontsize=14, pad=15)
    plt.xlabel('Hora do Dia (0h às 23h)', fontsize=12)
    plt.ylabel('Média de Energia (Wh)', fontsize=12)
    plt.xticks(range(0, 24, 2)) 
    plt.ylim(bottom=0)
    plt.xlim(0, 23)
    plt.grid(True, linestyle=':', alpha=0.7)
    
    plt.savefig(os.path.join(diretorio_output, 'grafico_1_ciclo_diario.png'), bbox_inches='tight', dpi=300)
    plt.close()

    # =====================================================================
    # GRÁFICO 2: Evolução Histórica (Todos os Anos Agrupados por Mês)
    # =====================================================================
    logging.info("Gerando Gráfico 2: Evolução Histórica Anual...")
    df_plot.set_index('Time', inplace=True)
    df_mensal = df_plot[coluna_energia].resample('ME').sum().reset_index()
    
    plt.figure(figsize=(12, 5))
    plt.plot(df_mensal['Time'], df_mensal[coluna_energia], color='#1f77b4', linewidth=2)
    plt.fill_between(df_mensal['Time'], df_mensal[coluna_energia], color='#1f77b4', alpha=0.2)
    
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    plt.title('2. Histórico de Longo Prazo: Soma Mensal de Geração (2017 - 2022)', fontsize=14, pad=15)
    plt.xlabel('Anos', fontsize=12)
    plt.ylabel('Energia Total Gerada no Mês (Wh)', fontsize=12)
    plt.ylim(bottom=0)
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.savefig(os.path.join(diretorio_output, 'grafico_2_historico_mensal.png'), bbox_inches='tight', dpi=300)
    plt.close()

    # =====================================================================
    # GRÁFICO 3: Dispersão (Radiação Solar vs Energia) apenas de DIA
    # =====================================================================
    logging.info("Gerando Gráfico 3: Relação de Dispersão (Causalidade)...")
    df_dia = df_plot[(df_plot['GHI'] > 0) & (df_plot[coluna_energia] > 0)]
    
    plt.figure(figsize=(10, 5))
    plt.scatter(df_dia['GHI'], df_dia[coluna_energia], alpha=0.3, color='#2ca02c', s=15)
    
    plt.title('3. Dispersão: Radiação Solar (GHI) vs Energia Gerada (Apenas Horas de Sol)', fontsize=14, pad=15)
    plt.xlabel('Radiação Solar (GHI)', fontsize=12)
    plt.ylabel('Energia Gerada (Wh)', fontsize=12)
    plt.ylim(bottom=0)
    plt.xlim(left=0)
    plt.grid(True, linestyle=':', alpha=0.7)
    
    plt.savefig(os.path.join(diretorio_output, 'grafico_3_dispersao_radiacao.png'), bbox_inches='tight', dpi=300)
    plt.close()

    logging.info("Todos os gráficos foram exportados com sucesso na pasta outputs!")
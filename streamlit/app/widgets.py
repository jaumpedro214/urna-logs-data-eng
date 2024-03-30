
import geopandas as gpd
import pandas as pd
import datetime
import re
import io
import streamlit as st

from maps import add_ufs_and_links_to_map, load_brazil_simplified_map, load_ufs_city_simplified_map
from data import DuckDBConnector

import matplotlib.pyplot as plt


@st.cache_resource
def get_duckdb_connector():
    return DuckDBConnector.get_instance()

def widgets_metricas_por_hora(container, turno, uf, zona, secao):


    metrics_df = get_duckdb_connector().get_metrics_over_time(uf, turno, zona, secao)
    metrics_df['timestamp_voto_computado_5min'] = pd.to_datetime(metrics_df['timestamp_voto_computado_5min'])
    metrics_df['tempo_voto_total_soma_cumulativo'] = metrics_df['tempo_voto_total_soma_cumulativo'].astype(int)
    metrics_df['tempo_biometria_soma_cumulativo'] = metrics_df['tempo_biometria_soma_cumulativo'].astype(int)

    # metrics_df = metrics_df.sort_values('timestamp_voto_computado_5min')
    # .fillna(pd.NaT)
    metrics_df = metrics_df.fillna( pd.NaT )

    # lineplot with time series
    FIGSIZE = (10, 5)
    fig, ax = plt.subplots( figsize=FIGSIZE )

    SECONDS_IN_YEAR = 365 * 24 * 3600
    YEARS = [0, 5, 20, 40, 60, 77, 100, 120] + [150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700]
    max_timestamp = metrics_df['tempo_voto_total_soma_cumulativo'].max()   

    y_axis_values = [y * SECONDS_IN_YEAR for y in YEARS if y * SECONDS_IN_YEAR <= max_timestamp]
    y_axis_labels = [format_time(y) for y in y_axis_values]

    # pegar só horas fechadas e 30min
    x_axis_values = (
        metrics_df
        .query("timestamp_voto_computado_5min.dt.minute == 0")
        ['timestamp_voto_computado_5min']
    )
    x_axis_labels = x_axis_values.dt.strftime('%H:%M')

    ax.plot(
        metrics_df['timestamp_voto_computado_5min'],
        metrics_df['tempo_voto_total_soma_cumulativo'],
        label='Tempo Voto Total',
        color='blue'
    )

    ax.plot(
        metrics_df['timestamp_voto_computado_5min'],
        metrics_df['tempo_biometria_soma_cumulativo'],
        label='Tempo Biometria',
        color='red'
    )

    ax.set_xticks(x_axis_values)
    ax.set_xticklabels(x_axis_labels, rotation=45, ha='right', fontsize=8)

    ax.set_yticks(y_axis_values)
    ax.set_yticklabels(y_axis_labels, fontsize=8)

    ax.fill_between(
        metrics_df['timestamp_voto_computado_5min'],
        metrics_df['tempo_voto_total_soma_cumulativo'],
        0,
        color='gray',
        alpha=0.5
    )

    container.pyplot(fig)


def widget_heatmap_tempo_medio_voto_mapa( container, turno, uf, zona, secao ):

    COLORMAP = 'coolwarm_r'
    RANGE_SECONDS_PLOT = 15
    FIGSIZE = (6, 6)

    container.markdown('#### Tempo Médio de Votação por UF')
    
    map_gdf = load_brazil_simplified_map()
    map_gdf_municipios = load_ufs_city_simplified_map()
    metrics_df = get_duckdb_connector().get_vote_time_metrics(uf, turno, zona, secao)

    if uf=='ALL':
        # merge using uf
        map_gdf = map_gdf.merge(metrics_df, left_on='SIGLA_UF', right_on='uf', how='left') 
        map_gdf = gpd.GeoDataFrame(map_gdf)

        tempo_voto_medio_ALL = metrics_df.query(f"uf == 'ALL'")['tempo_voto_medio'].max()
        map_gdf['tempo_voto_medio'] = tempo_voto_medio_ALL - map_gdf['tempo_voto_medio']
        
        fig = plt.figure(figsize=FIGSIZE)
        ax = fig.add_subplot(1, 1, 1)
        ax.axis('off')
        UFS = map_gdf['uf'].unique()

        for uf in UFS:
            (
                map_gdf
                .query(f"uf == '{uf}'")
                .plot(
                    column='tempo_voto_medio', 
                    ax=ax, 
                    cmap=COLORMAP,
                    legend=False,
                    vmin=-RANGE_SECONDS_PLOT,
                    vmax=+RANGE_SECONDS_PLOT,
                    gid=uf
                )
            )
        
        # save svg image to buffer
        svg_image_buffer = io.StringIO()
        plt.savefig(svg_image_buffer, format='svg')
        plt.close(fig)

        svg_image_with_links = add_ufs_and_links_to_map(svg_image_buffer.getvalue())
        container.markdown(svg_image_with_links, unsafe_allow_html=True)

    elif uf!='ALL' and zona=='ALL' and secao=='ALL':
        map_gdf_municipios = map_gdf_municipios.query(f"SIGLA_UF == '{uf}'")
        
        fig = plt.figure(figsize=FIGSIZE)
        ax = fig.add_subplot(1, 1, 1)
        ax.axis('off')

        map_gdf_municipios.plot(ax=ax, color='blue', lw=0.1, edgecolor='white')

        container.pyplot(fig)
        # container.write(map_gdf_municipios)

    elif uf!='ALL' and zona!='ALL' and secao=='ALL':
        pass
    elif uf!='ALL' and zona!='ALL' and secao!='ALL':
        pass


def widget_bignumber_votos( container, turno, uf, zona, secao ):
    
    metrics_df = get_duckdb_connector().get_vote_time_metrics(uf, turno, zona, secao)
    if uf == 'ALL':
        votos = metrics_df.query(f"uf == 'ALL'")['total_votos'].max()
    else:
        votos = metrics_df['total_votos'].max()
    
    votos_formatado = f"{votos:,}".replace(',', ' ')
    container.metric(label='Votos', value=votos_formatado)


def widget_bignumber_secoes( container, turno, uf, zona, secao ):
    
    metrics_df = get_duckdb_connector().get_vote_time_metrics(uf, turno, zona, secao)
    if uf == 'ALL':
        secoes = metrics_df.query(f"uf == 'ALL'")['total_secoes'].max()
    else:
        secoes = metrics_df['total_secoes'].max()

    section_formatado = f"{secoes:,}".replace(',', ' ')
    container.metric(label='Seções', value=section_formatado)


def widget_big_number_tempo_medio( container, turno, uf, zona, secao ):
    
    metrics_df = get_duckdb_connector().get_vote_time_metrics(uf, turno, zona, secao)
    if uf == 'ALL':
        tempo_medio = metrics_df.query(f"uf == 'ALL'")['tempo_voto_medio'].max()
    else:
        tempo_medio = metrics_df['tempo_voto_medio'].max()

    tempo_medio_formatado = format_time(tempo_medio)
    container.metric(label='Tempo Médio', value=tempo_medio_formatado)


def widget_big_number_tempo_medio_bio( container, turno, uf, zona, secao ):

    metrics_df = get_duckdb_connector().get_vote_time_metrics(uf, turno, zona, secao)
    if uf == 'ALL':
        tempo_medio = metrics_df.query(f"uf == 'ALL'")['tempo_biometria_medio'].max()
    else:
        tempo_medio = metrics_df['tempo_biometria_medio'].max()

    tempo_medio_formatado = format_time(tempo_medio)
    container.metric(label='Tempo Médio Biometria', value=tempo_medio_formatado)


def widget_qtd_votos_intervalo_tempo( container, turno, uf, zona, secao ):

    metrics_df = get_duckdb_connector().get_vote_time_metrics(uf, turno, zona, secao)
    if uf == 'ALL':
        metrics_df = metrics_df.query(f"uf == 'ALL'")

    format_time = lambda x: f"{x // 60}min{x % 60}s" if x >= 60 and x % 60!=0 else f"{x}s" if x < 60 else f"{x // 60}min"
    extrair_intervalo_superior_segundos = lambda col: int(col.split('_')[-2])
    extrair_intervalo_inferior_segundos = lambda col: int(col.split('_')[-3])

    colunas_qtd_votos_intervalo = [
        'votos_0_30_segundos', 'votos_30_60_segundos', 'votos_60_90_segundos',
        'votos_90_120_segundos', 'votos_120_150_segundos',
        'votos_150_180_segundos', 'votos_180_210_segundos',
        'votos_210_300_segundos', 'votos_300_9999_segundos'
    ]

    # format number in Mi, Mil, and integer 
    format_number = lambda number : (
        f"{number//1e6:.0f} Mi" 
        if number >= 1e6 else f"{number//1e3:.0f} Mil" 
        if number >= 1e3 else f"{number:.0f}"
    )

    valores_qtd_votos_intervalo = [
        (
         format_time(extrair_intervalo_inferior_segundos(col)) + " - " +
         format_time(extrair_intervalo_superior_segundos(col)),
         col, 
         metrics_df[col].max()
        )
        if col != 'votos_300_9999_segundos'
        else ("+ 5min", col, metrics_df[col].max())
        for col in colunas_qtd_votos_intervalo
    ]
    # revert order
    valores_qtd_votos_intervalo = valores_qtd_votos_intervalo[::-1]

    df_valores_qtd_votos_intervalo = pd.DataFrame(
        valores_qtd_votos_intervalo,
        columns=['intervalo', 'coluna', 'valor']
    )

    container.markdown('#### Em quanto tempo as pessoas votam?')

    # plot horizontal bar chart
    fig, ax = plt.subplots( figsize=(5, 15) )
    df_valores_qtd_votos_intervalo.plot.barh(x='intervalo', y='valor', legend=False, ax=ax)
    ax.set_xlabel('Quantidade de Votos')
    ax.set_ylabel('')
    # ax.set_title('Em quanto tempo as pessoas votam?\n', fontsize=20)

    # remover linha superior, direita e inferior
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    # remove x axis
    ax.xaxis.set_visible(False)

    # increase y axis font size
    ax.tick_params(axis='y', labelsize=24)

    # adicionar número no final de cada barra
    maior_valor = df_valores_qtd_votos_intervalo['valor'].max()
    offset = 0.05 * maior_valor
    for i, valor in enumerate(df_valores_qtd_votos_intervalo['valor']):
        ax.text(valor+offset, i, format_number(valor), color='black', va='center', fontsize=18)

    container.pyplot(fig)


def format_time(time_in_seconds):

    years = time_in_seconds // (365 * 24 * 3600)
    time_in_seconds = time_in_seconds % (365 * 24 * 3600)
    months = time_in_seconds // (30 * 24 * 3600)
    time_in_seconds = time_in_seconds % (30 * 24 * 3600)
    days = time_in_seconds // (24 * 3600)
    time_in_seconds = time_in_seconds % (24 * 3600)
    hours = time_in_seconds // 3600
    time_in_seconds %= 3600
    minutes = time_in_seconds // 60
    seconds = time_in_seconds % 60

    days = int(days)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)

    time_formated = ""
    if seconds > 0:
        time_formated += f"{seconds:.0f}s"
    if minutes > 0:
        time_formated = f"{minutes:.0f}m " + time_formated
    if hours > 0:
        time_formated = f"{hours:.0f}h " + time_formated
    if days > 0:
        time_formated = f"{days:.0f}d " + time_formated
    if months > 0:
        time_formated = f"{months:.0f} Meses " + time_formated
    if years > 0:
        time_formated = f"{years:.0f} Anos " + time_formated

    return time_formated

import streamlit as st
import geopandas as gpd
import pandas as pd
import re
import io

from maps import add_ufs_and_links_to_map, load_brazil_simplified_map, load_ufs_city_simplified_map
from data import DuckDBConnector

import matplotlib.pyplot as plt


UFS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO", "ZZ", "ALL"
]
TURNOS = ['1', '2']

def get_parameters():
    query_parameters = st.query_params
    select_parameters = lambda x, default, accepted: (
        default 
        if x not in query_parameters 
        else query_parameters[x] if query_parameters[x] in accepted
        else default
    )
    nr_zonas_secoes = [str(x) for x in range(0, 800)]

    uf =    select_parameters('uf',    'ALL', UFS            )
    turno = select_parameters('turno',     1, TURNOS         )
    zona =  select_parameters('zona',  'ALL', nr_zonas_secoes)
    secao = select_parameters('secao', 'ALL', nr_zonas_secoes)
    
    return uf, turno, zona, secao

@st.cache_resource
def get_duckdb_connector():
    return DuckDBConnector.get_instance()

def widget_heatmap_tempo_medio_voto_mapa( container, turno, uf, zona, secao ):

    COLORMAP = 'coolwarm_r'
    RANGE_SECONDS_PLOT = 15
    FIGSIZE = (6, 6)

    
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

    if days == 0 and hours != 0:
        return f" {hours:d}h {minutes:d}m {seconds:d}s"
    if days == 0 and hours == 0 and minutes != 0:
        return f" {minutes:d}m {seconds:d}s"
    if days == 0 and hours == 0 and minutes == 0:
        return f" {seconds:d}s"
    
    return f" {days:d}d {hours:d}h {minutes:d}m {seconds:d}s"


if __name__ == "__main__":
    st.set_page_config(layout="wide")

    uf, turno, zona, secao = get_parameters()
    
    st.title(f'Tempo de Votação')
    subtitulo = f'## {turno}º Turno'
    subtitulo = subtitulo + f' - {uf}' if uf != 'ALL' else subtitulo
    subtitulo = subtitulo + f' - Zona {zona}' if zona != 'ALL' else subtitulo
    subtitulo = subtitulo + f', Seção {secao}' if secao != 'ALL' else subtitulo

    st.markdown( subtitulo )

    col_bignumber_votos, col_bignumber_secoes, col_bignumber_tmedio, col_bignumber_tmedio_bio = st.columns(4)

    widget_bignumber_votos(col_bignumber_votos, turno, uf, zona, secao)
    widget_bignumber_secoes(col_bignumber_secoes, turno, uf, zona, secao)
    widget_big_number_tempo_medio(col_bignumber_tmedio, turno, uf, zona, secao)
    widget_big_number_tempo_medio_bio(col_bignumber_tmedio_bio, turno, uf, zona, secao)

    col_map, col_histogram, col_temporal_series = st.columns( [.3, .2, .5] )
    widget_heatmap_tempo_medio_voto_mapa(col_map, turno, uf, zona, secao)
    widget_qtd_votos_intervalo_tempo(col_histogram, turno, uf, zona, secao)

    st.divider()
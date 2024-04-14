
import geopandas as gpd
import pandas as pd
import datetime
import re
import io
import streamlit as st
import seaborn as sns

from maps import add_ufs_and_links_to_map, load_brazil_simplified_map, load_ufs_city_simplified_map
from data import DuckDBConnector
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

@st.cache_resource
def get_duckdb_connector():
    return DuckDBConnector.get_instance()

BLUE = "#0B1D51"
RED  = "#F08902"

# Seaborn set theme
# no grid
# gray background
sns.set_style("whitegrid")
sns.set_theme(style='whitegrid', palette='deep', font='sans-serif', font_scale=1, color_codes=True, rc=None)

def format_number_mi_mil(number):
    number_mi = number//1e6
    number_mil = (number - number_mi*1e6) / 1e3

    number_formatted = f"{number_mi:.0f} Mihão" if number_mi > 0 else ''
    if number_mil > 0:
        number_formatted  += f" {number_mil:.0f} Mil"
    elif number_mil > 0:
        number_formatted = str(number_mil).replace('.', ',')
        number_formatted = number_formatted[:number_formatted.index(',')+2] + ' Mil'
    number_formatted = number_formatted.strip()
    return number_formatted


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
        time_formated = f"{days:.0f} dias " + time_formated
    if months > 0:
        time_formated = f"{months:.0f} Meses " + time_formated
        if months == 1:
            time_formated = time_formated.replace('Meses', 'Mês')
    if years > 0:
        time_formated = f"{years:.0f} Anos " + time_formated
        if years == 1:
            time_formated = time_formated.replace('Anos', 'Ano')

        # Remover horas, minutos e segundos
        time_formated = re.sub(r'\d+[hms]', '', time_formated)

    return time_formated


def format_number(number):
    return (
        f"{number//1e6:.0f} Mi" 
        if number >= 1e6 else f"{number//1e3:.0f} Mil" 
        if number >= 1e3 else f"{number:.0f}"
    )


def widget_numero_votos_intervalo_5min(container, turno, uf, zona, secao):
    
    metrics_df = get_duckdb_connector().get_metrics_over_time(uf, turno, zona, secao)
    metrics_df['timestamp_voto_computado_5min'] = pd.to_datetime(metrics_df['timestamp_voto_computado_5min'])
    metrics_df = metrics_df.sort_values('timestamp_voto_computado_5min')
    metrics_df = metrics_df.fillna( pd.NaT )

    # define x and y
    y_metric = metrics_df['total_votos'].astype(int)

    # Get the maximum value of y
    # and the corresponding x value
    # ------------------------------
    x_value_max_y, max_y = metrics_df.loc[y_metric.idxmax(), ['timestamp_voto_computado_5min', 'total_votos']]
    x_value_max_y_formatted = x_value_max_y.strftime('%H:%M')
    max_y_formatted = format_number_mi_mil(max_y)

    # lineplot with time series
    FIGSIZE = (10, 5)
    fig, ax = plt.subplots( figsize=FIGSIZE )

    # pegar só horas fechadas e 30min
    x_axis_values = (
        metrics_df
        .query("timestamp_voto_computado_5min.dt.minute == 0")
        ['timestamp_voto_computado_5min']
    )
    x_axis_labels = x_axis_values.dt.strftime('%H:%M')

    if uf in ['ALL', 'SP', 'MG']:
        y_axis_values = [ 5e4, 1e5, 2.5e5, 5e5, 7.5e5, 1e6 ]
    else:
        y_axis_values = [ 1e3, 3e3, 5e3, 1e4, 1.5e4, 2e4, 5e4, 1e5, 5e5 ]
    y_axis_labels = [format_number(y) for y in y_axis_values]

    sns.lineplot(
        x=metrics_df['timestamp_voto_computado_5min'],
        y=y_metric,
        ax=ax,
        color=BLUE
    )

    # Fill area under the line
    # ------------------------
    ax.fill_between(
        metrics_df['timestamp_voto_computado_5min'],
        y_metric,
        0,
        zorder=0,
        alpha=0.5,
        color=BLUE
    )

    # Add vertical line at the maximum value
    # --------------------------------------
    ax.axvline(
        x=metrics_df.loc[y_metric.idxmax(), 'timestamp_voto_computado_5min'],
        color=RED,
        ymin=0,
        ymax=1,
        linestyle='-',
        linewidth=2
    )

    # Add a box in the line with the maximum value
    # left aligned
    # --------------------------------------------
    ax.text(
        x_value_max_y,
        0.9*max_y,
        f"{max_y_formatted}",
        color='white',
        fontsize=10,
        ha='left',
        va='center',
        bbox=dict(facecolor=RED, alpha=1)
    )


    ax.set_xticks(x_axis_values)
    ax.set_xticklabels(x_axis_labels, rotation=45, ha='right', fontsize=10)

    # remove right and top spines
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.set_yticks(y_axis_values)
    ax.set_yticklabels(y_axis_labels, fontsize=10)
    # add horizontal grid lines on the y axis
    # in the background
    ax.yaxis.grid(True, linestyle='-', alpha=1)
    # remove x grid lines
    ax.xaxis.grid(False)
    # remove x and y labels
    ax.set_xlabel('')
    ax.set_ylabel('')
    # set y limit
    ax.set_ylim(0, max_y)
    
    container.markdown('#### Número de votos efetuados a cada 5min')
    container.pyplot(fig)
    container.markdown(f'#### Às {x_value_max_y_formatted}, houve o pico de votos, com **{max_y_formatted}** computados em 5 minutos!')


def widget_tempo_medio_voto(container, turno, uf, zona, secao):

    if uf=='ALL':
        widget_heatmap_tempo_medio_voto_mapa(container, turno, uf, zona, secao)
    elif zona=='ALL':
        widget_tabela_tempo_medio_zonas(container, turno, uf, zona, secao)


def widget_tabela_tempo_medio_zonas( container, turno, uf, zona, secao ):
    container.markdown('#### Tempo Médio de Votação por Zona')
    metrics_df = get_duckdb_connector().get_vote_time_metrics(uf, turno, zona, secao)
    container.dataframe(metrics_df)


def widget_heatmap_tempo_medio_voto_mapa( container, turno, uf, zona, secao ):
    COLORMAP = 'coolwarm'
    RANGE_SECONDS_PLOT = 15
    FIGSIZE = (6, 6)
    
    map_gdf = load_brazil_simplified_map()
    metrics_df = get_duckdb_connector().get_vote_time_metrics(uf, turno, zona, secao)
    map_gdf = map_gdf.merge(metrics_df, left_on='SIGLA_UF', right_on='uf', how='left') 
    map_gdf = gpd.GeoDataFrame(map_gdf)

    tempo_voto_medio_ALL = metrics_df.query(f"uf == 'ALL'")['tempo_voto_medio'].max()
    map_gdf['tempo_voto_medio'] = map_gdf['tempo_voto_medio'] - tempo_voto_medio_ALL
    
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

    # add a horizontal colorbar
    sm = plt.cm.ScalarMappable(
        cmap=COLORMAP,
        norm=plt.Normalize(vmin=-RANGE_SECONDS_PLOT, vmax=+RANGE_SECONDS_PLOT)
    )

    cbar = fig.colorbar(sm, ax=ax, orientation='horizontal', pad=0.01, aspect=20, fraction=0.035)
    cbar.set_label('Segundos abaixo/acima da média', fontsize=10)
    cbar.ax.tick_params(labelsize=8)
    
    # save svg image to buffer
    svg_image_buffer = io.StringIO()
    plt.savefig(svg_image_buffer, format='svg')
    plt.close(fig)

    svg_image_with_links = add_ufs_and_links_to_map(svg_image_buffer.getvalue())

    container.markdown('#### Tempo Médio de Votação por UF')
    container.markdown(svg_image_with_links, unsafe_allow_html=True)


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


def widget_big_number_tempo_total_voto( container, turno, uf, zona, secao ):
    metrics_df = get_duckdb_connector().get_vote_time_metrics(uf, turno, zona, secao)

    if uf == 'ALL':
        tempo_medio = metrics_df.query(f"uf == 'ALL'")['tempo_voto_soma'].max()
    else:
        tempo_medio = metrics_df['tempo_voto_soma'].max()

    tempo_medio_formatado = format_time(tempo_medio)
    container.metric(label='Tempo Total Gasto', value=tempo_medio_formatado)


def widget_qtd_votos_intervalo_tempo( container, turno, uf, zona, secao ):

    metrics_df = get_duckdb_connector().get_vote_time_metrics(uf, turno, zona, secao)
    if uf == 'ALL':
        metrics_df = metrics_df.query(f"uf == 'ALL'")

    format_time = lambda x: f"{x // 60}:{x % 60:02d}"
    # format number in Mi, Mil, and integer 
    format_number = lambda number : (
        f"{number//1e6:.0f} Mi" 
        if number >= 1e6 else f"{number//1e3:.0f} Mil" 
        if number >= 1e3 else f"{number:.0f}"
    )

    extrair_intervalo_superior_segundos = lambda col: int(col.split('_')[-2])
    extrair_intervalo_inferior_segundos = lambda col: int(col.split('_')[-3])

    colunas_qtd_votos_intervalo = [
        'votos_0_30_segundos', 'votos_30_60_segundos', 'votos_60_90_segundos',
        'votos_90_120_segundos', 'votos_120_150_segundos',
        'votos_150_180_segundos', 'votos_180_210_segundos',
        'votos_210_300_segundos', 'votos_300_9999_segundos'
    ]

    valores_qtd_votos_intervalo = [
        (
         format_time(extrair_intervalo_inferior_segundos(col)) + " a " +
         format_time(extrair_intervalo_superior_segundos(col)),
         col, 
         metrics_df[col].max()
        )
        if col != 'votos_300_9999_segundos' and col != 'votos_0_30_segundos'
        else ("mais de 5:00", col, metrics_df[col].max())
        if col == 'votos_300_9999_segundos'
        else ("até 0:30", col, metrics_df[col].max())
        for col in colunas_qtd_votos_intervalo
    ]
    # revert order
    valores_qtd_votos_intervalo = valores_qtd_votos_intervalo[::-1]

    df_valores_qtd_votos_intervalo = pd.DataFrame(
        valores_qtd_votos_intervalo,
        columns=['intervalo', 'coluna', 'valor']
    )

    container.markdown('#### Em quantos minutos as pessoas votam?')

    # plot horizontal bar chart
    fig, ax = plt.subplots( figsize=(5, 12) )
    # df_valores_qtd_votos_intervalo.plot.barh(x='intervalo', y='valor', legend=False, width=.8, ax=ax)

    # make the barplot with seaborn
    sns.barplot(
        x='valor', 
        y='intervalo', 
        data=df_valores_qtd_votos_intervalo, 
        color=BLUE,
        ax=ax
    )
    fig.gca().invert_yaxis()

    # make the biggest bar red
    max_value = df_valores_qtd_votos_intervalo['valor'].max()
    max_value_index = df_valores_qtd_votos_intervalo['valor'].idxmax()
    ax.patches[max_value_index].set_facecolor(RED)
    # add the % inside the biggest bar
    max_value_percent = max_value / df_valores_qtd_votos_intervalo['valor'].sum()
    ax.text(
        max_value - 0.05 * max_value, 
        max_value_index, 
        f"{max_value_percent:.1%}",
        color='white', 
        ha = 'right', 
        va = 'center',
        size=20
    )

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
    ax.tick_params(axis='y', labelsize=20)

    # adicionar número no final de cada barra
    maior_valor = df_valores_qtd_votos_intervalo['valor'].max()
    offset = 0.05 * maior_valor
    for i, valor in enumerate(df_valores_qtd_votos_intervalo['valor']):
        ax.text(valor+offset, i, format_number(valor), color='black', va='center', fontsize=18)

    container.pyplot(fig)




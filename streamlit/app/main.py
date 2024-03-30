import streamlit as st
import geopandas as gpd
import re
import io

from maps import add_ufs_and_links_to_map, load_brazil_simplified_map
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

def widget_heatmap_mean_vote_time_map( container, turno, uf, zona, secao ):

    COLORMAP = 'coolwarm_r'
    RANGE_SECONDS_PLOT = 15

    
    map_gdf = load_brazil_simplified_map()
    metrics_df = get_duckdb_connector().get_vote_time_metrics(uf, turno, zona, secao)

    if uf=='ALL':
        # merge using uf
        map_gdf = map_gdf.merge(metrics_df, left_on='SIGLA_UF', right_on='uf', how='left') 
        map_gdf = gpd.GeoDataFrame(map_gdf)

        tempo_voto_medio_ALL = metrics_df.query(f"uf == 'ALL'")['tempo_voto_medio'].max()
        map_gdf['tempo_voto_medio'] = tempo_voto_medio_ALL - map_gdf['tempo_voto_medio']
        
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(1, 1, 1)
        # remove axis
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

    if uf!='ALL' and zona=='ALL':
        pass

    if uf!='ALL' and zona!='ALL':
        pass
    if uf!='ALL' and zona!='ALL' and secao!='ALL':
        pass


# st.markdown(generate_brazil_map_with_ufs_and_links(), unsafe_allow_html=True)
if __name__ == "__main__":
    st.set_page_config(layout="wide")

    uf, turno, zona, secao = get_parameters()
    
    st.title(f'Tempo de Votação')
    subtitulo = f'## {turno}º Turno'
    subtitulo = subtitulo + f' - {uf}' if uf != 'ALL' else subtitulo
    subtitulo = subtitulo + f' - Zona {zona}' if zona != 'ALL' else subtitulo
    subtitulo = subtitulo + f', Seção {secao}' if secao != 'ALL' else subtitulo

    st.markdown( subtitulo )

    col_map, col_histogram, col_temporal_series = st.columns( [.4, .2, .4] )
    widget_heatmap_mean_vote_time_map(col_map, turno, uf, zona, secao)

    st.divider()
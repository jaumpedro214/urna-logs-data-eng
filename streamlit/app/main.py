import streamlit as st
import geopandas as gpd
import re

from maps import generate_brazil_map_with_ufs_and_links
from data import DuckDBConnector

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

    uf =    select_parameters('uf',    'ALL',     UFS          )
    turno = select_parameters('turno',     1,     TURNOS       )
    zona =  select_parameters('zona',  'ALL',     nr_zonas_secoes)
    secao = select_parameters('secao', 'ALL',     nr_zonas_secoes)
    
    return uf, turno, zona, secao

@st.cache_resource
def get_duckdb_connector():
    return DuckDBConnector.get_instance()

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

    data = get_duckdb_connector().get_vote_time_metrics(uf, turno, zona, secao)
    st.write(data)

    st.divider()
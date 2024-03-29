import streamlit as st
import geopandas as gpd
import re

from maps import generate_brazil_map_with_ufs_and_links

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

    uf = select_parameters('uf', 'ALL', UFS)
    turno = select_parameters('turno', 1, TURNOS)
    
    return uf, turno

# st.markdown(generate_brazil_map_with_ufs_and_links(), unsafe_allow_html=True)
if __name__ == "__main__":
    st.set_page_config(layout="wide")

    uf, turno = get_parameters()

    st.title(f'{turno}º Turno {uf} - Tempo de Votação')
    st.divider()
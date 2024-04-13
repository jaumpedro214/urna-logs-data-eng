import streamlit as st

from widgets import (
    widget_bignumber_votos, widget_bignumber_secoes, 
    widget_big_number_tempo_medio, widget_big_number_tempo_medio_bio,
    widget_heatmap_tempo_medio_voto_mapa, widget_qtd_votos_intervalo_tempo,
    widgets_metricas_por_hora
)

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
    turno = select_parameters('turno',   '1', TURNOS         )
    zona =  select_parameters('zona',  'ALL', nr_zonas_secoes)
    secao = select_parameters('secao', 'ALL', nr_zonas_secoes)
    
    return uf, turno, zona, secao

if __name__ == "__main__":
    st.set_page_config(layout="wide")

    uf, turno, zona, secao = get_parameters()
    
    st.title(f'Eleições em Números - Tempo de Votação')
    subtitulo = f'## {turno}º Turno'
    subtitulo = subtitulo + f' - {uf}' if uf != 'ALL' else subtitulo
    subtitulo = subtitulo + f' - Zona {zona}' if zona != 'ALL' else subtitulo
    subtitulo = subtitulo + f', Seção {secao}' if secao != 'ALL' else subtitulo

    st.markdown( subtitulo )
    
    # ============================
    # Big Number Widgets
    # ============================

    col_bignumber_votos, col_bignumber_secoes, col_bignumber_tmedio, col_bignumber_tmedio_bio = st.columns(4)
    widget_bignumber_votos(col_bignumber_votos, turno, uf, zona, secao)
    widget_bignumber_secoes(col_bignumber_secoes, turno, uf, zona, secao)
    widget_big_number_tempo_medio(col_bignumber_tmedio, turno, uf, zona, secao)
    widget_big_number_tempo_medio_bio(col_bignumber_tmedio_bio, turno, uf, zona, secao)
    st.divider()

    # =================================
    # Heatmap and Histogram Widgets
    # =================================
    col_map, col_histogram, col_temporal_series = st.columns( [.3, .2, .5] )
    widget_heatmap_tempo_medio_voto_mapa(col_map, turno, uf, zona, secao)
    widget_qtd_votos_intervalo_tempo(col_histogram, turno, uf, zona, secao)
    widgets_metricas_por_hora(col_temporal_series, turno, uf, zona, secao)

    st.divider()
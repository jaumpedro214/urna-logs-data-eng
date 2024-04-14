import streamlit as st

from widgets import (
    widget_bignumber_votos, widget_bignumber_secoes, 
    widget_big_number_tempo_medio, widget_big_number_tempo_medio_bio,
    widget_big_number_tempo_total_voto,
    widget_tempo_medio_voto, widget_qtd_votos_intervalo_tempo,
    widget_numero_votos_intervalo_5min
)

UFS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO", "ZZ", "ALL"
]
TURNOS = ['1', '2']

def get_parameters_from_http_query_params():
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

    uf, turno, zona, secao = get_parameters_from_http_query_params()
    
    st.title(f'Eleições em Números - Tempo de Votação')
    subtitulo = ''
    subtitulo = subtitulo + f' - {uf}' if uf != 'ALL' else subtitulo + " - Brasil"
    subtitulo = subtitulo + f' - Zona {zona}' if zona != 'ALL' else subtitulo
    subtitulo = subtitulo + f', Seção {secao}' if secao != 'ALL' else subtitulo

    col_subtitle, col_change_turn = st.columns([4, 1])
    # col_subtitle.markdown( subtitulo )
    # add button to change the turn

    outro_turno = '1' if turno == '2' else '2'
    query_parameters = f"?turno={outro_turno}&uf={uf}&zona={zona}&secao={secao}"
    st.components.v1.html(
        f"""
        <div>
            <a href="{query_parameters}" class="btn btn-primary" role="button" target="_blank" style="text-decoration: none;">
                <button 
                    style="background-color: #F08902; 
                    color: white; 
                    padding: 10px 20px; 
                    font-size: 32px; 
                    border: none; 
                    cursor: pointer; 
                    font-family: sans-serif; 
                    font-weight: bold;"
                    height="70px";
                >
                {turno}º Turno
                </button>
            </a>
            <p style="font-size: 32px; margin-top: 10px; margin-left: 5px;
            font-family: sans-serif; font-weight: bold; display: inline-block;">
                {subtitulo}
            </p>
        </div>
        """,
        height=70
    )

    # ============================
    # Big Number Widgets
    # ============================

    col_bignumber_votos, col_bignumber_secoes, col_bignumber_tmedio, col_bignumber_tmedio_bio, col_bignumber_tempo_total = st.columns(5)
    widget_bignumber_votos(col_bignumber_votos, turno, uf, zona, secao)
    widget_bignumber_secoes(col_bignumber_secoes, turno, uf, zona, secao)
    widget_big_number_tempo_medio(col_bignumber_tmedio, turno, uf, zona, secao)
    widget_big_number_tempo_medio_bio(col_bignumber_tmedio_bio, turno, uf, zona, secao)
    widget_big_number_tempo_total_voto(col_bignumber_tempo_total, turno, uf, zona, secao)
    st.divider()

    # =================================
    # Heatmap and Histogram Widgets
    # =================================
    col_map, col_histogram, col_temporal_series = st.columns( [.3, .2, .5] )
    widget_tempo_medio_voto(col_map, turno, uf, zona, secao)
    widget_qtd_votos_intervalo_tempo(col_histogram, turno, uf, zona, secao)
    widget_numero_votos_intervalo_5min(col_temporal_series, turno, uf, zona, secao)

    st.divider()

    # =================================
    # Foot note. Author: João Pedro. Data gathered from TSE Open Data Portal. All code available at github.
    # =================================

    st.text('Author: João Pedro. Dados coletados do Portal de Dados Abertos do TSE. All code available at Github.')
    st.text('O projeto é complexo. Os podem não ser 100% precisos.')

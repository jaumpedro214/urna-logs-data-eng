import geopandas as gpd
import matplotlib.pyplot as plt
import re
import streamlit as st  

@st.cache_data()
def load_brazil_map():
    map_ufs = './maps/BR_UF_2022.zip'

    gdf = gpd.read_file(map_ufs)

    # simplify geometries to reduce file size
    # and improve performance on streamlit app
    gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.01)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ufs = gdf.SIGLA_UF

    for uf in ufs:
        gdf[gdf.SIGLA_UF == uf].plot(ax=ax, gid=uf)

    # remove axis
    plt.axis('off')
    # save as svg
    fig.savefig('brasil_simplify.svg')

def generate_brazil_map_with_ufs_and_links():
    load_brazil_map()

    brazil_image = open('brasil_simplify.svg', 'r').read()

    re_uf_map_pattern = r'(<g id="([A-Z][A-Z])">((.|\s)*?)</g>)'
    brazil_image_with_links = re.sub(
        re_uf_map_pattern, 
        r"<a target=\"_self\" rel=\"noopener noreferrer\" href=?uf=\2>\1</a>", 
        brazil_image
    )

    return brazil_image_with_links
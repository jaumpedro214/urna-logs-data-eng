import geopandas as gpd
import matplotlib.pyplot as plt
import re
import streamlit as st  

@st.cache_data()
def load_brazil_simplified_map():
    """
    Load the simplified map of Brazil.
    The simplification is done to reduce the file size
    and improve performance on the streamlit app.

    Returns:
        gpd.GeoDataFrame: GeoDataFrame with the simplified map of Brazil.
    """
    
    map_ufs = './maps/BR_UF_2022.zip'

    gdf = gpd.read_file(map_ufs)
    gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.01)

    return gdf

@st.cache_data()
def load_ufs_city_simplified_map():
    """
    Load the simplified map of Brazil with cities.
    """
    map_municipios = './maps/BR_Municipios_2022.zip'

    gdf = gpd.read_file(map_municipios)
    gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.01)

    return gdf

def add_ufs_and_links_to_map(svg_image_buffer):
    """
    Generate links for each UF in the SVG image buffer.
    And make the map clickable.

    Args:
        svg_image_buffer (str): SVG image buffer.

    Returns:
        str: SVG image buffer with links for each UF.
    """

    re_uf_map_pattern = r'(<g id="([A-Z][A-Z])">((.|\s)*?)</g>)'
    image_with_links = re.sub(
        re_uf_map_pattern, 
        r"<a target=\"_self\" rel=\"noopener noreferrer\" href=?uf=\2>\1</a>", 
        svg_image_buffer
    )
    return image_with_links

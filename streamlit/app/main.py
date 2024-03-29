import streamlit as st
import geopandas as gpd
import re

from maps import generate_brazil_map_with_ufs_and_links

st.title('Hello World!')
st.markdown(generate_brazil_map_with_ufs_and_links(), unsafe_allow_html=True)
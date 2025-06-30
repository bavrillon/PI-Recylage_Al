import streamlit as st

data = ... #les données à récupérer

st.markdown("Optimisation des alliages d'aluminium")

site = st.selectbox('Which factory?', data['site'])
'You selected:', site
ID_SITE = data[site]['site_code']

external_scrap = st.selectbox('Which scrap?', data['external_scrap'])
'You selected:', external_scrap
ID_SCRAP = data[external_scrap]['scrap_name']


if st.checkbox ('Show data'):
    data_visualization = ... #les données à visualiser dans un tableau
    data_visualization
import streamlit as st

data = ... #les données à récupérer

site = st.selectbox('Which factory?', data['site'])
'You selected:', site
external_scrap = st.selectbox('Which scrap?', data['external_scrap'])
'You selected:', external_scrap


if st.checkbox ('Show data'):
    data_visualization = ... #les données à visualiser
    data_visualization
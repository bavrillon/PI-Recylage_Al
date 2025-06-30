import streamlit as st

conn = st.connection("database",type="sql") #il faut mettre le bon nom je pense, et il faut créer un fichier secrets.toml
data = ... #les données à récupérer

st.markdown("Optimization of aluminium alloys")

site = st.selectbox('Which factory?', data['site'])
'You selected:', site
ID_SITE = data[site]['site_code']

external_scrap = st.selectbox('Which scrap?', data['external_scrap'])
'You selected:', external_scrap
ID_SCRAP = data[external_scrap]['scrap_name']

side=st.sidebar
side.text_input("What scrap do you want to add?")
if side.button("Add"):
    ... #rajouter la chute à la database

if st.checkbox ('Show data'):
    data_visualization = conn.query("SELECT * FROM ...") #les données à visualiser dans un tableau, il faut le nom de la table sql
    data_visualization

if st.button('Optimize'):
    scrap_column, no_scrap_column = st.columns(2)
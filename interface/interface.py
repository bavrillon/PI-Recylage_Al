import streamlit as st

conn = st.connection("database",type="sql") #il faut mettre le bon nom je pense, et il faut créer un fichier secrets.toml
data = ... #les données à récupérer en pandas

st.markdown("Optimization of aluminium alloys")

c1, c2 = st.columns(2)

with c1:
    site = st.selectbox('Which factory?', data['site']['name'])
    'You selected:', site
    ID_SITE = data[site]['site_code']

with c2:
    external_scrap = st.selectbox('Which scrap?', data['external_scrap']['scrap_name'])
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
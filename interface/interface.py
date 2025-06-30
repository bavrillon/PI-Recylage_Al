import streamlit as st

conn = st.connection("data_db",type="sql") #il faut créer un fichier secrets.toml !!!
data = conn.query("SELECT * FROM site, alloy, raw_material, recycling_costs, currency, external_scrap") #les données à récupérer en pandas

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
side.text_input("What scrap do you want to add?") #je pense pas que text_input soit le bon truc, ou alors il faut se mettre d'accord avec grégoire
                                                  # pour par ex séparer les colonnes par des virgules
if side.button("Add scrap"):
    conn.query("INSERT INTO data VALUES ... ") #rajouter la chute à la database

side.text_input("What alloy do you want to add?")
if side.button("Add alloy"):
    conn.query("INSERT INTO data VALUES ... ") #rajouter à la database

side.text_input("What site do you want to add?")
if side.button("Add site"):
    conn.query("INSERT INTO data VALUES ... ") #rajouter à la database

side.text_input("What raw material do you want to add?")
if side.button("Add material"):
    conn.query("INSERT INTO data VALUES ... ") #rajouter à la database

side.text_input("What currency do you want to add?")
if side.button("Add currency"):
    conn.query("INSERT INTO data VALUES ... ") #rajouter à la database

side.text_input("What recycling cost do you want to add?")
if side.button("Add recycling cost"):
    conn.query("INSERT INTO data VALUES ... ") #rajouter à la database


if st.checkbox ('Show data'):
    data_visualization = conn.query("SELECT * FROM alloy, raw_material, recycling_costs, currency") #les données à visualiser dans un tableau
    st.dataframe(data_visualization)

if st.button('Optimize'):
    scrap_column, no_scrap_column = st.columns(2)
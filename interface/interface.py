import streamlit as st

conn = st.connection("data_db",type="sql")
sites = conn.query("SELECT * FROM site") #returns a DataFrame
alloys = conn.query("SELECT * FROM alloy")
raw_materials = conn.query("SELECT * FROM raw_material")
recycling_costs = conn.query("SELECT * FROM recycling_costs")
currencies = conn.query("SELECT * FROM currency")
external_scraps = conn.query("SELECT * FROM external_scrap")

st.header("Optimization of aluminium alloys")

c1, c2 = st.columns(2)

with c1:
    site = st.selectbox('Which factory?', sites['name'])
    'You selected:', site
    ID_SITE = site['site_code']

with c2:
    external_scrap = st.selectbox('Which scrap?', external_scraps['scrap_name'])
    'You selected:', external_scrap
    ID_SCRAP = external_scrap['scrap_name']


if st.checkbox ('Show data'):
    edited_external_scraps = st.data_editor(external_scraps, num_rows="dynamic")
    external_scraps = edited_external_scraps

if st.button('Optimize'):
    scrap_column, no_scrap_column = st.columns(2)
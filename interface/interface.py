import streamlit as st
from optimisation import optimise_co2

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
    edited_alloys = st.data_editor(alloys, num_rows="dynamic")
    alloys = edited_alloys
    edited_raw_materials = st.data_editor(raw_materials, num_rows="dynamic")
    raw_materials = edited_raw_materials
    edited_recycling_costs = st.data_editor(recycling_costs, num_rows="dynamic")
    recycling_costs = edited_recycling_costs

if st.button('Optimize CO2'):
    scrap_column, no_scrap_column = st.columns(2)
    with scrap_column:
        alloy = st.selectbox('Which alloy?', data['alloy']['alloy_name'])
        'You selected:', alloy
        ID_ALLOY = data[alloy]['id_alloy']
        st.write("Optimizing with scrap...")
        # Call the optimization function here
        optimised_composition = optimise_co2(ID_SITE, ID_ALLOY, ID_SCRAP)
        st.write(f"Optimized composition: {optimised_composition}")
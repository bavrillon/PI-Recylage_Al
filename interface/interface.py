import streamlit as st
from optimisation import optimise_co2

conn = st.connection("data_db",type="sql")
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


if st.checkbox ('Show data'):
    edited_data = st.data_editor(data, num_rows="dynamic")
    edited_data
    data = edited_data

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
import streamlit as st

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

if st.button('Optimize'):
    scrap_column, no_scrap_column = st.columns(2)
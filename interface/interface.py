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


site = st.selectbox('Which factory?', sites['name'])
'You selected:', site
ID_SITE = site['site_code']

c1, c2, c3, c4, c5 = st.columns(5)
scrap_name = c1.text_input('Name of the scrap')
shape = c2.text_input('Shape of the scrap')
scrap_purchasing_cost_per_t = c3.text_input('Purchasing cost of the scrap (per t)')
transportation_cost_per_t = c4.text_input('Transportation cost of the scrap (per t)')
currency = c5.text_input('Currency of the costs')

st.write('Choose the composition of the scrap:')
c6, c7, c8, c9, c10, c11, c12, c13 = st.columns(8)
si = c6.number_input('Si')
fe = c7.number_input('Fe')
cu = c8.number_input('Cu')
mn = c9.number_input('Mn')
mg = c10.number_input('Mg')
cr = c11.number_input('Cr')
zn = c12.number_input('Zn')
ti = c13.number_input('Ti')

#ajouter les données input à la db scrap, en la vidant avant

if st.checkbox ('Show scraps'):
    edited_external_scraps = st.data_editor(external_scraps, num_rows="dynamic")
    external_scraps = edited_external_scraps
if st.checkbox ('Show alloys'):
    edited_alloys = st.data_editor(alloys, num_rows="dynamic")
    alloys = edited_alloys
if st.checkbox ('Show materials'):
    edited_raw_materials = st.data_editor(raw_materials, num_rows="dynamic")
    raw_materials = edited_raw_materials
if st.checkbox ('Show recycling costs'):
    edited_recycling_costs = st.data_editor(recycling_costs, num_rows="dynamic")
    recycling_costs = edited_recycling_costs
if st.checkbox ('Show currencies'):
    edited_currencies = st.data_editor(currencies, num_rows="dynamic")
    currencies = edited_currencies

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
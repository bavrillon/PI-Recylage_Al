#TRUC A FAIRE : REGARDER CE QUI DOIT ETRE ACTUALISE A CHAQUE FOIS ET CE QUI DOIT ETRE MIS EN CACHE
#probablement : mettre tous les trucs d'input dans une fonction input(conn,sites,...) avec le décorateur @st.cache_data

from os import path
import streamlit as st
from data.db_tools import Database

db = Database(path.join(path.dirname(__file__), "data.db"))


conn = st.connection("data_db",type="sql")
sites = conn.query("SELECT * FROM site") #returns a DataFrame
alloys = conn.query("SELECT * FROM alloy")
raw_materials = conn.query("SELECT * FROM raw_material")
recycling_costs = conn.query("SELECT * FROM recycling_cost")
currencies = conn.query("SELECT * FROM currency")
compositions = conn.query("SELECT * FROM composition")
shape_types = conn.query("SELECT * FROM shape_type")

st.header("Optimization of aluminium alloys")


site_select = st.selectbox('Which factory?', sites['name'])
ID_SITE = conn.query(f'SELECT site_code FROM site WHERE name="{site_select}"')

c1, c2, c3, c4, c5 = st.columns(5)
scrap_name = c1.text_input('Name of the scrap')
shape = c2.selectbox('Shape of the scrap', shape_types['name'])
scrap_purchasing_cost_per_t = c3.number_input('Purchasing cost of the scrap (per t)', min_value = 0.0)
transportation_cost_per_t = c4.number_input('Transportation cost of the scrap (per t)', min_value = 0.0)
currency = c5.selectbox('Currency of the costs', currencies['name'])

st.write('Choose the composition of the scrap (in proportions):')
c6, c7, c8, c9, c10, c11, c12, c13 = st.columns(8)
si = c6.number_input('Si', min_value = 0.0, max_value = 1.0, step = 0.000001, format = "%0.6f")
fe = c7.number_input('Fe', min_value = 0.0, max_value = 1.0, step = 0.000001, format = "%0.6f")
cu = c8.number_input('Cu', min_value = 0.0, max_value = 1.0, step = 0.000001, format = "%0.6f")
mn = c9.number_input('Mn', min_value = 0.0, max_value = 1.0, step = 0.000001, format = "%0.6f")
mg = c10.number_input('Mg', min_value = 0.0, max_value = 1.0, step = 0.000001, format = "%0.6f")
cr = c11.number_input('Cr', min_value = 0.0, max_value = 1.0, step = 0.000001, format = "%0.6f")
zn = c12.number_input('Zn', min_value = 0.0, max_value = 1.0, step = 0.000001, format = "%0.6f")
ti = c13.number_input('Ti', min_value = 0.0, max_value = 1.0, step = 0.000001, format = "%0.6f")

shape_id = conn.query(f"SELECT shape_type_id FROM shape_type WHERE name='{shape}'").iloc[0,0]


ID_SCRAP = 1 # ID_SCRAP is a constant for the scrap in the database (only 1 line), it can be changed if needed
compo_id = conn.query("SELECT COUNT(*) FROM composition").iloc[0,0] + 1


conn.query(f"INSERT INTO composition VALUES ('{compo_id}', '{si}', '{fe}', '{cu}', '{mn}', '{mg}', '{cr}', '{zn}', '{ti}')")


#adds the input data to the db table "scrap", emptying it first
conn.query("DELETE FROM scrap")
conn.query("INSERT INTO scrap (scrap_id, scrap_name, composition_id, shape_type_id, scrap_purchasing_cost_per_t, transportation_cost_per_t) " \
f"VALUES ('{ID_SCRAP}','{scrap_name}','{compo_id}', '{shape_id}', '{scrap_purchasing_cost_per_t}', '{transportation_cost_per_t}')")


if st.checkbox ('Show alloys'):
    edited_alloys = st.data_editor(alloys, num_rows="dynamic")
    alloys = edited_alloys
if st.checkbox ('Show raw materials'):
    edited_raw_materials = st.data_editor(raw_materials, num_rows="dynamic")
    raw_materials = edited_raw_materials
if st.checkbox ('Show recycling costs'):
    edited_recycling_costs = st.data_editor(recycling_costs, num_rows="dynamic")
    recycling_costs = edited_recycling_costs
if st.checkbox ('Show currencies'):
    edited_currencies = st.data_editor(currencies, num_rows="dynamic")
    currencies = edited_currencies
if st.checkbox ('Show sites'):
    edited_sites = st.data_editor(sites, num_rows="dynamic")
    sites = edited_sites
if st.checkbox ('Show compositions'):
    edited_compositions = st.data_editor(compositions, num_rows="dynamic")
    compositions = edited_compositions

if st.button('Optimize CO2 with/without scrap'):
    scrap_column, no_scrap_column = st.columns(2)
    with scrap_column:
        alloy_select = st.selectbox('Which alloy?', alloys['name'])
        'You selected:', alloy_select
        ID_ALLOY = conn.query(f'SELECT id_alloy FROM alloy WHERE name="{alloy_select}"')
        with st.spinner("Optimizing with scrap..."):
            optimised_composition = db.optimise_co2_with_scrap(ID_SITE, ID_ALLOY, ID_SCRAP)
        st.write(f"Optimized composition: {optimised_composition}")
    with no_scrap_column:
        alloy_select = st.selectbox('Which alloy?', alloys['name'])
        'You selected:', alloy_select
        ID_ALLOY = conn.query(f'SELECT id_alloy FROM alloy WHERE name="{alloy_select}"')
        with st.spinner("Optimizing without scrap..."):
            optimised_composition = db.optimise_co2_without_scrap(ID_SITE, ID_ALLOY)
        st.write(f"Optimized composition: {optimised_composition}")

if st.button('Optimize cost with/without scrap'):
    cost_column, no_cost_column = st.columns(2)
    with cost_column:
        alloy_select = st.selectbox('Which alloy?', alloys['name'])
        'You selected:', alloy_select
        ID_ALLOY = conn.query(f'SELECT id_alloy FROM alloy WHERE name="{alloy_select}"')
        with st.spinner("Optimizing cost with scrap..."):
            optimised_cost = db.optimise_cost_with_scrap(ID_SITE, ID_ALLOY, ID_SCRAP)
        st.write(f"Optimized composition: {optimised_cost}")
    with no_cost_column:
        alloy_select = st.selectbox('Which alloy?', alloys['name'])
        'You selected:', alloy_select
        ID_ALLOY = conn.query(f'SELECT id_alloy FROM alloy WHERE name="{alloy_select}"')
        with st.spinner("Optimizing cost without scrap..."):
            optimised_cost = db.optimise_cost_without_scrap(ID_SITE, ID_ALLOY)
        st.write(f"Optimized composition: {optimised_cost}")


#deletes the table entry "compo_id" in the table composition
conn.query(f"DELETE FROM composition WHERE composition_id={compo_id}")
#delete the table entry "ID_SCRAP" in the table scrap if needed
#conn.query(f"DELETE FROM scrap WHERE scrap_id={ID_SCRAP}")
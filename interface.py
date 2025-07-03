#TRUCS A FAIRE : excels + pb modifier db

from os import path
import streamlit as st
from data.db_tools import Database
from sqlalchemy import text

db = Database(path.join(path.dirname(__file__), "data.db"))


conn = st.connection("data_db",type="sql", connect_args={"timeout": 5})
sites = conn.query("SELECT * FROM site") #returns a DataFrame
alloys = conn.query("SELECT * FROM alloy")
raw_materials = conn.query("SELECT * FROM raw_material")
recycling_costs = conn.query("SELECT * FROM recycling_cost")
currencies = conn.query("SELECT * FROM currency")
compositions = conn.query("SELECT * FROM composition")
shape_types = conn.query("SELECT * FROM shape_type")

st.header("Optimization of aluminium alloys")


site_select = st.selectbox('Choose a site', sites['name'])
ID_SITE = conn.query(f'SELECT site_code FROM site WHERE name="{site_select}"').iloc[0,0]

c1, c2, c3, c4, c5 = st.columns(5)
scrap_name = c1.text_input('Name of the scrap')
shape = c2.selectbox('Shape of the scrap', shape_types['name'])
scrap_purchasing_cost_per_t = c3.number_input('Purchasing cost of the scrap (per t)', min_value = 0.0)
transportation_cost_per_t = c4.number_input('Transportation cost of the scrap (per t)', min_value = 0.0)
currency = str(c5.selectbox('Currency of the costs', currencies['name']))

st.write('Choose the composition of the scrap (%):')
c6, c7, c8, c9, c10, c11, c12, c13 = st.columns(8)
si = c6.number_input('Si', min_value = 0.0, max_value = 100.0, step = 0.00001, format = "%0.6f")
fe = c7.number_input('Fe', min_value = 0.0, max_value = 100.0, step = 0.00001, format = "%0.6f")
cu = c8.number_input('Cu', min_value = 0.0, max_value = 100.0, step = 0.00001, format = "%0.6f")
mn = c9.number_input('Mn', min_value = 0.0, max_value = 100.0, step = 0.00001, format = "%0.6f")
mg = c10.number_input('Mg', min_value = 0.0, max_value = 100.0, step = 0.00001, format = "%0.6f")
cr = c11.number_input('Cr', min_value = 0.0, max_value = 100.0, step = 0.00001, format = "%0.6f")
zn = c12.number_input('Zn', min_value = 0.0, max_value = 100.0, step = 0.00001, format = "%0.6f")
ti = c13.number_input('Ti', min_value = 0.0, max_value = 100.0, step = 0.00001, format = "%0.6f")

if si + fe + cu + mn + mg + cr + zn + ti > 100 :
    st.write("The sum of compositions cannot be greater than 100%")

else :

    shape_id = int(conn.query(f"SELECT shape_type_id FROM shape_type WHERE name='{shape}'").iloc[0,0])


    ID_SCRAP = 'S0' # ID_SCRAP is a constant for the scrap in the database (only 1 line), it can be changed if needed
    compo_id = int(conn.query("SELECT COUNT(*) FROM composition").iloc[0,0] + 1) # the scrap composition ID is the last ID in the composition table


    insert_compo = text("""INSERT INTO composition (composition_id, Si, Fe, Cu, Mn, Mg, Cr, Zn, Ti)
                        VALUES (:compo_id, :si, :fe, :cu, :mn, :mg, :cr, :zn, :ti)""")
    with conn.session as session:
        session.execute(
            insert_compo,
            dict(compo_id = compo_id, si = si/100, fe = fe/100, cu = cu/100, mn = mn/100, mg = mg/100, cr = cr/100, zn = zn/100, ti = ti/100)
        )
        session.commit()


    #adds the input data to the db table "scrap", emptying it first
    delete_scrap = text("""DELETE FROM scrap""")
    with conn.session as session:
        session.execute(
            delete_scrap
        )
        session.commit()

    insert_scrap = text("""INSERT INTO scrap (scrap_id, scrap_name, composition_id, shape_type_id, scrap_purchasing_cost_per_t, transportation_cost_per_t, currency) 
                        VALUES (:ID_SCRAP, :scrap_name, :compo_id, :shape_id, :scrap_purchasing_cost_per_t, :transportation_cost_per_t, :currency)""")
    with conn.session as session:
        session.execute(
            insert_scrap,
            dict(ID_SCRAP = ID_SCRAP,
                scrap_name = scrap_name,
                compo_id = compo_id,
                shape_id = shape_id,
                scrap_purchasing_cost_per_t = scrap_purchasing_cost_per_t,
                transportation_cost_per_t = transportation_cost_per_t,
                currency = currency) 
        )
        session.commit()
    
    
    alloys_from_site = conn.query("SELECT * FROM alloy a JOIN composition c "\
                                    "ON a.composition_id = c.composition_id "\
                                    f"WHERE a.site_code = '{ID_SITE}'")
    

    if st.checkbox('Show alloys from chosen site'):
        alloys_from_site = alloys_from_site.drop(['composition_id'], axis = 1)
        edited_alloys = st.data_editor(alloys_from_site, num_rows="dynamic")
        #alloys = edited_alloys
    if st.checkbox('Show raw materials'):
        raw = conn.query("SELECT * FROM raw_material r JOIN composition c ON r.composition_id = c.composition_id ")
        edited_raw_materials = st.data_editor(raw.drop(['composition_id'], axis = 1), num_rows="dynamic")
        #raw_materials = edited_raw_materials
    if st.checkbox('Show recycling cost from chosen site'):
        edited_recycling_costs = st.data_editor(conn.query(f"SELECT * FROM recycling_cost WHERE site_code = '{ID_SITE}'"))
    if st.checkbox('Show chosen currency'):
        edited_currencies = st.data_editor(conn.query(f"SELECT * FROM currency WHERE name = '{currency}'"))
    if st.checkbox('Show chosen site'):
        edited_sites = st.data_editor(conn.query(f"SELECT * FROM site WHERE site_code = '{ID_SITE}'"))

    
    elements = db.get_raw_materials_name()

    if 'show_co2' not in st.session_state:
        st.session_state.show_co2 = False
    if 'alloy_co2' not in st.session_state:
        st.session_state.alloy_co2 = None

    if st.button('Optimize CO2 with/without scrap'):
        st.session_state.show_co2 = True

    if st.session_state.show_co2:

        for _,row in alloys_from_site.iterrows():
            alloy_select = row['name']

            query = text("SELECT alloy_id FROM alloy WHERE name = :name")
            with conn.session as session:
                ID_ALLOY = session.execute(query, {"name": alloy_select}).first()[0]

            scrap_co2_column, no_scrap_co2_column = st.columns(2)

            with scrap_co2_column:
                st.subheader(alloy_select, 'with scrap')
                with st.spinner("Optimizing with scrap..."):
                    optimised_co2 = db.optimise_co2_with_scrap(ID_SITE, ID_ALLOY, ID_SCRAP)
                optimised_co2 = [x*100 for x in optimised_co2]
                st.write("Optimized composition (%):", dict(zip(elements + ['scrap'], optimised_co2)))

            with no_scrap_co2_column:
                st.subheader(alloy_select, 'without scrap')
                with st.spinner("Optimizing without scrap..."):
                    optimised_co2 = db.optimise_co2_without_scrap(ID_SITE, ID_ALLOY)
                optimised_co2 = [x*100 for x in optimised_co2]
                st.write("Optimized composition (%):", dict(zip(elements, optimised_co2)))


    if 'show_cost' not in st.session_state:
        st.session_state.show_cost = False
    if 'alloy_cost' not in st.session_state:
        st.session_state.alloy_cost = None

    if st.button('Optimize cost with/without scrap'):
        st.session_state.show_cost = True

    if st.session_state.show_cost:

        for  _,row in alloys_from_site.iterrows():
            alloy_select = row['name']

            query = text("SELECT alloy_id FROM alloy WHERE name = :name")
            with conn.session as session:
                ID_ALLOY = session.execute(query, {"name": alloy_select}).first()[0]

            scrap_cost_column, no_scrap_cost_column = st.columns(2)

            with scrap_cost_column:
                st.subheader(alloy_select, 'with scrap')
                with st.spinner("Optimizing cost with scrap..."):
                    optimised_cost = db.optimise_cost_with_scrap(ID_SITE, ID_ALLOY, ID_SCRAP)
                optimised_cost = [x*100 for x in optimised_cost]
                st.write("Optimized composition (%):", dict(zip(elements + ['scrap'], optimised_cost)))

            with no_scrap_cost_column:
                st.subheader(alloy_select, 'without scrap')
                with st.spinner("Optimizing cost without scrap..."):
                    optimised_cost = db.optimise_cost_without_scrap(ID_SITE, ID_ALLOY)
                optimised_cost = [x*100 for x in optimised_cost]
                st.write("Optimized composition (%):", dict(zip(elements, optimised_cost)))


    if 'show_material' not in st.session_state:
        st.session_state.show_material = False
    if 'alloy_material' not in st.session_state:
        st.session_state.alloy_material = None

    if st.button('Optimize use of materials with scrap'):
        st.session_state.show_material = True

    if st.session_state.show_material:

        for alloy_select in alloys_from_site['name']:

            query = text("SELECT alloy_id FROM alloy WHERE name = :name")
            with conn.session as session:
                ID_ALLOY = session.execute(query, {"name": alloy_select}).first()[0]

            st.subheader(alloy_select, 'with scrap')
            with st.spinner("Optimizing with scrap..."):
                optimised = db.optimise_utilisation_scrap(ID_SITE, ID_ALLOY, ID_SCRAP)
            optimised = [x*100 for x in optimised]
            st.write("Optimized composition (%):", dict(zip(elements + ['scrap'], optimised)))


    #deletes the table entry "compo_id" in the table composition once the optimization is done
    if st.session_state.show_co2 or st.session_state.show_cost or st.session_state.show_material:
        delete_compo = text("DELETE FROM composition WHERE composition_id=:compo_id")
        with conn.session as session:
            session.execute(
                delete_compo,
                dict(compo_id = compo_id)
            )
            session.commit()
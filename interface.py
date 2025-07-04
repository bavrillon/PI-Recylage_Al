#TRUCS A FAIRE : excels + améliorer output (faire un joli tableau)

from os import path
import streamlit as st
from data.db_tools import Database
from sqlalchemy import text
import pandas as pd

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
    compo_id = 'C' + str(compo_id)


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
        edited_alloys = st.data_editor(alloys_from_site, num_rows="dynamic", disabled=["alloy_id"])

        st.write('(the column id cannot be modified)')

        if st.button("Save modifications to database"):
            for _, row in edited_alloys.iterrows():

                if pd.isna(row["alloy_id"]): #if it is a new alloy
                    new_alloy_id = "A" + str(conn.query("SELECT COUNT(*) FROM alloy").iloc[0,0] + 1)
                    new_compo_id = "C" + str(conn.query("SELECT COUNT(*) FROM composition").iloc[0,0] + 1)
                    insert_compo = text("""INSERT INTO composition (composition_id, Si, Fe, Cu, Mn, Mg, Cr, Zn, Ti)
                                        VALUES (:composition_id, :Si, :Fe, :Cu, :Mn, :Mg, :Cr, :Zn, :Ti)""")
                    with conn.session as session:
                        session.execute(insert_compo,
                                        dict(composition_id=new_compo_id,
                                             Si=row["Si"],
                                             Fe=row["Fe"],
                                             Cu=row["Cu"],
                                             Mn=row["Mn"],
                                             Mg=row["Mg"],
                                             Cr=row["Cr"],
                                             Zn=row["Zn"],
                                             Ti=row["Ti"]))
                        session.commit()
                    insert_alloy = text("""INSERT INTO alloy (alloy_id, name, site_code, composition_id)
                                        VALUES (:alloy_id, :name, :site_code, :composition_id)""")
                    with conn.session as session:
                        session.execute(
                            insert_alloy,
                            dict(alloy_id=new_alloy_id,
                                name=row["name"],
                                site_code=row["site_code"],
                                composition_id=new_compo_id))
                        session.commit()

                else: #if the alloy already exists but was modified
                    alloy_id = row['alloy_id']
                    query_compo = text("SELECT composition_id FROM alloy WHERE alloy_id = :alloy_id")
                    with conn.session as session:
                        composition_id = session.execute(query_compo, {"alloy_id": alloy_id}).first()[0]

                    update_alloy = text("UPDATE alloy SET name = :name, site_code = :site_code WHERE alloy_id = :alloy_id")
                    with conn.session as session:
                        session.execute(update_alloy,dict(
                            name = row["name"],
                            site_code = row["site_code"],
                            alloy_id = alloy_id))
                        session.commit()
                    update_composition = text("""UPDATE composition SET
                            Si = :si,
                            Fe = :fe,
                            Cu = :cu,
                            Mn = :mn,
                            Mg = :mg,
                            Cr = :cr,
                            Zn = :zn,
                            Ti = :ti
                        WHERE composition_id = :composition_id""")
                    with conn.session as session:
                        session.execute(update_composition, dict(
                                si = row["Si"],
                                fe = row["Fe"],
                                cu = row["Cu"],
                                mn = row["Mn"],
                                mg = row["Mg"],
                                cr = row["Cr"],
                                zn = row["Zn"],
                                ti = row["Ti"],
                                composition_id = composition_id))
                        session.commit()

    if st.checkbox('Show raw materials'):
        raw = conn.query("SELECT * FROM raw_material r JOIN composition c ON r.composition_id = c.composition_id ")
        edited_raw_materials = st.data_editor(raw.drop(['composition_id'], axis = 1), num_rows="dynamic", disabled=["raw_material_id"])
        st.write('(the column id cannot be modified)')

        if st.button("Save modifications to database"):
            for _, row in edited_raw_materials.iterrows():

                if pd.isna(row["raw_material_id"]): #if it is a new material
                    new_material_id = "R" + str(conn.query("SELECT COUNT(*) FROM raw_material").iloc[0,0] + 1)
                    new_compo_id = "C" + str(conn.query("SELECT COUNT(*) FROM composition").iloc[0,0] + 1)
                    insert_compo = text("""INSERT INTO composition (composition_id, Si, Fe, Cu, Mn, Mg, Cr, Zn, Ti)
                                        VALUES (:composition_id, :Si, :Fe, :Cu, :Mn, :Mg, :Cr, :Zn, :Ti)""")
                    with conn.session as session:
                        session.execute(insert_compo,
                                        dict(composition_id=new_compo_id,
                                             Si=row["Si"],
                                             Fe=row["Fe"],
                                             Cu=row["Cu"],
                                             Mn=row["Mn"],
                                             Mg=row["Mg"],
                                             Cr=row["Cr"],
                                             Zn=row["Zn"],
                                             Ti=row["Ti"]))
                        session.commit()
                    insert_material = text("""INSERT INTO raw_material (raw_material_id, name, composition_id, cost_per_t, premium, currency, t_CO2_per_t)
                                        VALUES (:raw_material_id, :name, :composition_id, :cost_per_t, :premium, :currency, :t_CO2_per_t)""")
                    with conn.session as session:
                        session.execute(
                            insert_material,
                            dict(raw_material_id=new_material_id,
                                name=row["name"],
                                composition_id=new_compo_id,
                                cost_per_t=row["cost_per_t"],
                                premium=row['premium'],
                                currency=row['currency'],
                                t_CO2_per_t=row['t_CO2_per_t']))
                        session.commit()

                else: #if the material already exists but was modified
                    material_id = row['material_id']
                    query_compo = text("SELECT composition_id FROM raw_material WHERE raw_material_id = :material_id")
                    with conn.session as session:
                        composition_id = session.execute(query_compo, {"material_id": material_id}).first()[0]

                    update_material = text("UPDATE raw_material SET name=:name, cost_per_t=:cost_per_t, premium=:premium, currency=:currency, t_CO2_per_t=:t_CO2_per_t WHERE raw_material_id = :material_id")
                    with conn.session as session:
                        session.execute(update_material,dict(
                            name = row["name"],
                            cost_per_t = row["cost_per_t"],
                            premium = row['premium'],
                            currency = row['currency'],
                            t_CO2_per_t = row['t_CO2_per_t'],
                            material_id = material_id))
                        session.commit()
                    update_composition = text("""UPDATE composition SET
                            Si = :si,
                            Fe = :fe,
                            Cu = :cu,
                            Mn = :mn,
                            Mg = :mg,
                            Cr = :cr,
                            Zn = :zn,
                            Ti = :ti
                        WHERE composition_id = :composition_id""")
                    with conn.session as session:
                        session.execute(update_composition, dict(
                                si = row["Si"],
                                fe = row["Fe"],
                                cu = row["Cu"],
                                mn = row["Mn"],
                                mg = row["Mg"],
                                cr = row["Cr"],
                                zn = row["Zn"],
                                ti = row["Ti"],
                                composition_id = composition_id))
                        session.commit()

    if st.checkbox('Show recycling cost from chosen site'):
        edited_recycling_costs = st.data_editor(conn.query(f"SELECT * FROM recycling_cost WHERE site_code = '{ID_SITE}'"),
                                                disabled=['recycling_cost_id','site_code','shape_type_id'])
        if st.button('Save modifications to database'):
            for _,row in edited_recycling_costs.iterrows():
                recycling_cost_id = row['recycling_cost_id']
                recycling_cost_per_t = row['recycling_cost_per_t']
                update_recycling = text('UPDATE recycling_cost SET recycling_cost_per_t=:recycling_cost_per_t WHERE recycling_cost_id=:recycling_cost_id')
                with conn.session as session:
                    session.execute(update_recycling, dict(recycling_cost_per_t=recycling_cost_per_t, recycling_cost_id=recycling_cost_id))
                    session.commit()
        st.write('(only recycling_cost_per_t can be modified)')
    if st.checkbox('Show chosen currency'):
        edited_currencies = st.data_editor(conn.query(f"SELECT * FROM currency WHERE name = '{currency}'"), disabled=['name'])
        if st.button('Save modifications to database'):
            for _,row in edited_currencies.iterrows():
                USD = row['USD']
                name = row['name']
                update_currency = text('UPDATE currency SET USD=:USD WHERE name=:name')
                with conn.session as session:
                    session.execute(update_currency, dict(USD=USD, name=name))
                    session.commit()
        st.write('(name cannot be modified)')
    if st.checkbox('Show chosen site'):
        edited_sites = st.data_editor(conn.query(f"SELECT * FROM site WHERE site_code = '{ID_SITE}'"),
                                      disabled=['site_code','name','premium_per_t','currency'])
        st.write('(data cannot be modified)')

    
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
                st.subheader(alloy_select + ' with scrap')
                with st.spinner("Optimizing with scrap...", show_time=True):
                    optimised_co2 = db.optimise_co2_with_scrap(ID_SITE, ID_ALLOY, ID_SCRAP)
                optimised_co2 = [x*100 for x in optimised_co2]
                st.write("Optimized composition (%):", dict(zip(elements + ['scrap'], optimised_co2)))

            with no_scrap_co2_column:
                st.subheader(alloy_select + ' without scrap')
                with st.spinner("Optimizing without scrap...", show_time=True):
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
                st.subheader(alloy_select + ' with scrap')
                with st.spinner("Optimizing cost with scrap...", show_time=True):
                    optimised_cost = db.optimise_cost_with_scrap(ID_SITE, ID_ALLOY, ID_SCRAP)
                optimised_cost = [x*100 for x in optimised_cost]
                st.write("Optimized composition (%):", dict(zip(elements + ['scrap'], optimised_cost)))

            with no_scrap_cost_column:
                st.subheader(alloy_select + ' without scrap')
                with st.spinner("Optimizing cost without scrap...", show_time=True):
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

            st.subheader(alloy_select + ' with scrap')
            with st.spinner("Optimizing with scrap...", show_time=True):
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
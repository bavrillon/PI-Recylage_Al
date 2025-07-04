from os import path
import streamlit as st
from data.db_tools import Database
import pandas as pd
import io
from sqlalchemy import text


# Import the database
db = Database(path.join(path.dirname(__file__), "data.db"))
conn = st.connection("data_db", type="sql", connect_args={"timeout": 5})

st.title("Scrap data upload")

sites = conn.query("SELECT * FROM site") #returns a DataFrame
alloys = conn.query("SELECT * FROM alloy")
raw_materials = conn.query("SELECT * FROM raw_material")
# list of raw materials and their IDs, for the excel file creation
list_raw_materials = raw_materials['name'].tolist()
list_id_raw_materials = db.get_raw_materials_id()
recycling_costs = conn.query("SELECT * FROM recycling_cost")
currencies = conn.query("SELECT * FROM currency")
compositions = conn.query("SELECT * FROM composition")
shape_types = conn.query("SELECT * FROM shape_type")


# Testing excel file upload
st.write("You can upload here an Excel file with the scrap data. Please be careful to use the correct format (and a xlsx file), like the example provided.")
st.download_button(label="Download example file", data="interface/data_example_interface.py", file_name="data_example_interface.xlsx")
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    file_buffer = io.BytesIO(file_bytes)
    df_scrap = pd.read_excel(file_buffer, engine='openpyxl')
    columns = df_scrap.columns.tolist()
    if columns != ["scrap_name", "Si", "Fe", "Cu", "Mn", "Mg", "Cr", "Zn", "Ti",
                   "shape", "scrap_purchasing_cost_per_t", "transportation_cost_per_t", "currency"]:
        st.error("The uploaded file does not have the correct format. Please check the example file.")
    
    df_display = pd.DataFrame(columns=['Alloy', 'Optimization', 'Use scrap', 'Product', 'Price', 'CO2',
                                       'Mass', 'Si', 'Fe', 'Cu', 'Mn', 'Mg', 'Cr', 'Zn', 'Ti'])
    scrap_tables = {}

    for line in df_scrap.itertuples(index=False):
        scrap_name, si, fe, cu, mn, mg, cr, zn, ti, shape, scrap_purchasing_cost_per_t, transportation_cost_per_t, currency = line
        shape_id = conn.query(f"SELECT shape_type_id FROM shape_type WHERE name='{shape}'").iloc[0, 0]
        currency_id = conn.query(f"SELECT name FROM currency WHERE name='{currency}'").iloc[0, 0]
        compo_id = conn.query("SELECT COUNT(*) FROM composition").iloc[0, 0] + 1  # the scrap composition ID is the last ID in the composition table

        insert_compo = text("INSERT INTO composition (composition_id, Si, Fe, Cu, Mn, Mg, Cr, Zn, Ti) VALUES (:compo_id, :si, :fe, :cu, :mn, :mg, :cr, :zn, :ti)")
        with conn.session as session:
            session.execute(insert_compo, 
                                  dict(compo_id=compo_id, si=si, fe=fe, cu=cu, mn=mn, mg=mg, cr=cr, zn=zn, ti=ti))
            session.commit()
        
        delete_scrap = text("DELETE FROM scrap")
        with conn.session as session:
            session.execute(delete_scrap)
            session.commit()
        
        insert_scrap = text("""INSERT INTO scrap (scrap_id, scrap_name, composition_id, shape_type_id, scrap_purchasing_cost_per_t, transportation_cost_per_t, currency)
                                VALUES (:ID_SCRAP, :scrap_name, :compo_id, :shape_id, :scrap_purchasing_cost_per_t, :transportation_cost_per_t, :currency)""")
        with conn.session as session:
            session.execute(insert_scrap,
                            dict(ID_SCRAP=0,
                                     scrap_name=scrap_name,
                                     compo_id=compo_id,
                                     shape_id=shape_id,
                                     scrap_purchasing_cost_per_t=scrap_purchasing_cost_per_t,
                                     transportation_cost_per_t=transportation_cost_per_t,
                                     currency=currency))
            session.commit()
        
        # now, we do the calculations and put it in a new dataframe
        for _, row in alloys.iterrows():
            alloy_name = row['name']
            alloy_site_code = row['site_code']
            alloy_composition_id = row['composition_id']
            alloy_id = row['alloy_id']


# ===================================================================================================================
            # CO2 optimization with scrap
# ===================================================================================================================

            # if the program returns a ValueError, fill the excel table with NaN
            try:
                optimized_co2_with_scrap = [x*100 for x in db.optimise_co2_with_scrap(id_site=alloy_site_code,
                                                                                      id_alloy=alloy_id, id_scrap=0)] #composition in %
            except ValueError:
                new_line = {'Alloy': alloy_name, 'Optimization': 'CO2-Error', 'Use scrap': 'Yes', 'Product': 'NaN', 'Price': 'NaN',
                            'CO2': 'NaN', 'Mass': 'NaN', 'Si': 'NaN', 'Fe': 'NaN', 'Cu': 'NaN', 'Mn': 'NaN', 'Mg': 'NaN', 'Cr': 'NaN',
                            'Zn': 'NaN', 'Ti': 'NaN'}
                df_display = pd.concat(df_display, pd.DataFrame([new_line], ignore_index=True))
                continue


            # Adding the data to the dataframe with the methods to get price and CO2

            # we need the sum of all columns for the "total" line
            price_total, mass_total, si_total, fe_total, cu_total, mn_total, mg_total, cr_total, zn_total, ti_total = 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.

            # first, we add the scrap data
            # to get the composition of each element, we multiply the composition of each of the raw materials composing the element by the mass of the element in the optimized composition
            new_line = {
                'Alloy': alloy_name, 'Optimization': 'CO2', 'Use scrap': 'Yes', 'Product': scrap_name,
                'Price': db.get_cost_scrap(alloy_site_code, id_scrap=0)*optimized_co2_with_scrap[-1],
                'CO2': 0., 'Mass': optimized_co2_with_scrap[-1],
                'Si': db.get_composition_raw_material(list_id_raw_materials[0])[0]*optimized_co2_with_scrap[-1],
                'Fe': db.get_composition_raw_material(list_id_raw_materials[1])[1]*optimized_co2_with_scrap[-1],
                'Cu': db.get_composition_raw_material(list_id_raw_materials[2])[2]*optimized_co2_with_scrap[-1],
                'Mn': db.get_composition_raw_material(list_id_raw_materials[3])[3]*optimized_co2_with_scrap[-1],
                'Mg': db.get_composition_raw_material(list_id_raw_materials[4])[4]*optimized_co2_with_scrap[-1],
                'Cr': db.get_composition_raw_material(list_id_raw_materials[5])[5]*optimized_co2_with_scrap[-1],
                'Zn': db.get_composition_raw_material(list_id_raw_materials[6])[6]*optimized_co2_with_scrap[-1],
                'Ti': db.get_composition_raw_material(list_id_raw_materials[7])[7]*optimized_co2_with_scrap[-1]}
            df_display = pd.concat(df_display, pd.DataFrame([new_line]), ignore_index=True)

            price_total += db.get_cost_scrap(alloy_site_code, id_scrap=0)*optimized_co2_with_scrap[-1]
            mass_total += optimized_co2_with_scrap[-1]
            si_total += db.get_composition_raw_material(list_id_raw_materials[0])[0]*optimized_co2_with_scrap[-1]
            fe_total += db.get_composition_raw_material(list_id_raw_materials[1])[1]*optimized_co2_with_scrap[-1]
            cu_total += db.get_composition_raw_material(list_id_raw_materials[2])[2]*optimized_co2_with_scrap[-1]
            mn_total += db.get_composition_raw_material(list_id_raw_materials[3])[3]*optimized_co2_with_scrap[-1]
            mg_total += db.get_composition_raw_material(list_id_raw_materials[4])[4]*optimized_co2_with_scrap[-1]
            cr_total += db.get_composition_raw_material(list_id_raw_materials[5])[5]*optimized_co2_with_scrap[-1]
            zn_total += db.get_composition_raw_material(list_id_raw_materials[6])[6]*optimized_co2_with_scrap[-1]
            ti_total += db.get_composition_raw_material(list_id_raw_materials[7])[7]*optimized_co2_with_scrap[-1]
            
            # then, we add the raw materials data, that we can automatically get with a loop
            for i in range(len(optimized_co2_with_scrap)-1):
                df_display.append({
                    'Alloy': alloy_name, 'Optimization': 'CO2', 'Use scrap': 'Yes', 'Product': list_raw_materials[i],
                    'Price': db.get_cost_raw_material(alloy_site_code, list_id_raw_materials[i])*optimized_co2_with_scrap[i],
                    'CO2': db.get_total_co2(optimized_co2_with_scrap)[i], 'Mass': optimized_co2_with_scrap[i],
                    'Si': db.get_composition_raw_material(list_id_raw_materials[0])*optimized_co2_with_scrap[i],
                    'Fe': db.get_composition_raw_material(list_id_raw_materials[1])*optimized_co2_with_scrap[i],
                    'Cu': db.get_composition_raw_material(list_id_raw_materials[2])*optimized_co2_with_scrap[i],
                    'Mn': db.get_composition_raw_material(list_id_raw_materials[3])*optimized_co2_with_scrap[i],
                    'Mg': db.get_composition_raw_material(list_id_raw_materials[4])*optimized_co2_with_scrap[i],
                    'Cr': db.get_composition_raw_material(list_id_raw_materials[5])*optimized_co2_with_scrap[i],
                    'Zn': db.get_composition_raw_material(list_id_raw_materials[6])*optimized_co2_with_scrap[i],
                    'Ti': db.get_composition_raw_material(list_id_raw_materials[7])*optimized_co2_with_scrap[i]})
                price_total += db.get_cost_raw_material(alloy_site_code, list_id_raw_materials[i])*optimized_co2_with_scrap[i]
                mass_total += optimized_co2_with_scrap[i]
                si_total += db.get_composition_raw_material(list_id_raw_materials[0])*optimized_co2_with_scrap[i]
                fe_total += db.get_composition_raw_material(list_id_raw_materials[1])*optimized_co2_with_scrap[i]
                cu_total += db.get_composition_raw_material(list_id_raw_materials[2])*optimized_co2_with_scrap[i]
                mn_total += db.get_composition_raw_material(list_id_raw_materials[3])*optimized_co2_with_scrap[i]
                mg_total += db.get_composition_raw_material(list_id_raw_materials[4])*optimized_co2_with_scrap[i]
                cr_total += db.get_composition_raw_material(list_id_raw_materials[5])*optimized_co2_with_scrap[i]
                zn_total += db.get_composition_raw_material(list_id_raw_materials[6])*optimized_co2_with_scrap[i]
                ti_total += db.get_composition_raw_material(list_id_raw_materials[7])*optimized_co2_with_scrap[i]
                
            # lastly, add last line with total values of all the components
            df_display.append({
                'Alloy': alloy_name, 'Optimization': 'CO2', 'Use scrap': 'Yes', 'Product': 'Total',
                'Price': price_total, 'CO2': db.get_total_co2(optimized_co2_with_scrap)[-1],
                'Mass': mass_total, 'Si': si_total, 'Fe': fe_total, 'Cu': cu_total, 'Mn': mn_total,
                'Mg': mg_total, 'Cr': cr_total, 'Zn': zn_total, 'Ti': ti_total})


# ===================================================================================================================
            # CO2 optimization without scrap
# ===================================================================================================================

            try:
                optimized_co2_without_scrap = [x*100 for x in db.optimise_co2_without_scrap(id_site=alloy_site_code, id_alloy=alloy_id)]
            except ValueError:
                df_display = df_display.append({
                    'Alloy': alloy_name, 'Optimization': 'CO2-Error', 'Use scrap': 'No', 'Product': 'NaN', 'Price': 'NaN',
                    'CO2': 'NaN', 'Mass': 'NaN', 'Si': 'NaN', 'Fe': 'NaN', 'Cu': 'NaN', 'Mn': 'NaN', 'Mg': 'NaN', 'Cr': 'NaN',
                    'Zn': 'NaN', 'Ti': 'NaN'}, ignore_index=True)
                continue

            # Adding the data to the dataframe with the methods to get price and CO2 like before
            price_total, mass_total, si_total, fe_total, cu_total, mn_total, mg_total, cr_total, zn_total, ti_total = 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.

            # Since no scrap is used, we add directly the raw materials data with a loop
            for i in range(len(optimized_co2_without_scrap)):
                df_display.append({
                    'Alloy': alloy_name, 'Optimization': 'CO2', 'Use scrap': 'No', 'Product': list_raw_materials[i],
                    'Price': db.get_cost_raw_material(alloy_site_code, list_id_raw_materials[i])*optimized_co2_without_scrap[i],
                    'CO2': db.get_total_co2(optimized_co2_without_scrap)[i], 'Mass': optimized_co2_without_scrap[i],
                    'Si': db.get_composition_raw_material(list_id_raw_materials[0])*optimized_co2_without_scrap[i],
                    'Fe': db.get_composition_raw_material(list_id_raw_materials[1])*optimized_co2_without_scrap[i],
                    'Cu': db.get_composition_raw_material(list_id_raw_materials[2])*optimized_co2_without_scrap[i],
                    'Mn': db.get_composition_raw_material(list_id_raw_materials[3])*optimized_co2_without_scrap[i],
                    'Mg': db.get_composition_raw_material(list_id_raw_materials[4])*optimized_co2_without_scrap[i],
                    'Cr': db.get_composition_raw_material(list_id_raw_materials[5])*optimized_co2_without_scrap[i],
                    'Zn': db.get_composition_raw_material(list_id_raw_materials[6])*optimized_co2_without_scrap[i],
                    'Ti': db.get_composition_raw_material(list_id_raw_materials[7])*optimized_co2_without_scrap[i]})
                price_total += db.get_cost_raw_material(alloy_site_code, list_id_raw_materials[i])*optimized_co2_without_scrap[i]
                mass_total += optimized_co2_without_scrap[i]
                si_total += db.get_composition_raw_material(list_id_raw_materials[0])*optimized_co2_without_scrap[i]
                fe_total += db.get_composition_raw_material(list_id_raw_materials[1])*optimized_co2_without_scrap[i]
                cu_total += db.get_composition_raw_material(list_id_raw_materials[2])*optimized_co2_without_scrap[i]
                mn_total += db.get_composition_raw_material(list_id_raw_materials[3])*optimized_co2_without_scrap[i]
                mg_total += db.get_composition_raw_material(list_id_raw_materials[4])*optimized_co2_without_scrap[i]
                cr_total += db.get_composition_raw_material(list_id_raw_materials[5])*optimized_co2_without_scrap[i]
                zn_total += db.get_composition_raw_material(list_id_raw_materials[6])*optimized_co2_without_scrap[i]
                ti_total += db.get_composition_raw_material(list_id_raw_materials[7])*optimized_co2_without_scrap[i]
                
            # lastly, add last line with total values of all the components
            df_display.append({
                'Alloy': alloy_name, 'Optimization': 'CO2', 'Use scrap': 'No', 'Product': 'Total',
                'Price': price_total, 'CO2': db.get_total_co2(optimized_co2_without_scrap)[-1],
                'Mass': mass_total, 'Si': si_total, 'Fe': fe_total, 'Cu': cu_total, 'Mn': mn_total,
                'Mg': mg_total, 'Cr': cr_total, 'Zn': zn_total, 'Ti': ti_total})


# ===================================================================================================================
            # Price optimization with scrap
# ===================================================================================================================

            try:
                optimized_price_with_scrap = db.optimise_cost_with_scrap(id_site=alloy_site_code, id_alloy=alloy_id, id_scrap=0)
            except ValueError:
                df_display = df_display.append({
                    'Alloy': alloy_name, 'Optimization': 'Price-Error', 'Use scrap': 'Yes', 'Product': 'NaN', 'Price': 'NaN',
                    'CO2': 'NaN', 'Mass': 'NaN', 'Si': 'NaN', 'Fe': 'NaN', 'Cu': 'NaN', 'Mn': 'NaN', 'Mg': 'NaN', 'Cr': 'NaN',
                    'Zn': 'NaN', 'Ti': 'NaN'}, ignore_index=True)
                continue

            # Adding the data to the dataframe with the methods to get price and CO2

            # initializing the totals
            price_total, mass_total, si_total, fe_total, cu_total, mn_total, mg_total, cr_total, zn_total, ti_total = 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.

            # Adding the scrap data
            # Same way of reasoning as before
            df_display.append({
                'Alloy': alloy_name, 'Optimization': 'Price', 'Use scrap': 'Yes', 'Product': scrap_name,
                'Price': db.get_cost_scrap(alloy_site_code, id_scrap=0)*optimized_price_with_scrap[-1],
                'CO2': 0., 'Mass': optimized_price_with_scrap[-1],
                'Si': db.get_composition_raw_material(list_id_raw_materials[0])[0]*optimized_price_with_scrap[-1],
                'Fe': db.get_composition_raw_material(list_id_raw_materials[1])[1]*optimized_price_with_scrap[-1],
                'Cu': db.get_composition_raw_material(list_id_raw_materials[2])[2]*optimized_price_with_scrap[-1],
                'Mn': db.get_composition_raw_material(list_id_raw_materials[3])[3]*optimized_price_with_scrap[-1],
                'Mg': db.get_composition_raw_material(list_id_raw_materials[4])[4]*optimized_price_with_scrap[-1],
                'Cr': db.get_composition_raw_material(list_id_raw_materials[5])[5]*optimized_price_with_scrap[-1],
                'Zn': db.get_composition_raw_material(list_id_raw_materials[6])[6]*optimized_price_with_scrap[-1],
                'Ti': db.get_composition_raw_material(list_id_raw_materials[7])[7]*optimized_price_with_scrap[-1]})
            price_total += db.get_cost_scrap(alloy_site_code, id_scrap=0)*optimized_price_with_scrap[-1]
            mass_total += optimized_price_with_scrap[-1]
            si_total += db.get_composition_raw_material(list_id_raw_materials[0])[0]*optimized_price_with_scrap[-1]
            fe_total += db.get_composition_raw_material(list_id_raw_materials[1])[1]*optimized_price_with_scrap[-1]
            cu_total += db.get_composition_raw_material(list_id_raw_materials[2])[2]*optimized_price_with_scrap[-1]
            mn_total += db.get_composition_raw_material(list_id_raw_materials[3])[3]*optimized_price_with_scrap[-1]
            mg_total += db.get_composition_raw_material(list_id_raw_materials[4])[4]*optimized_price_with_scrap[-1]
            cr_total += db.get_composition_raw_material(list_id_raw_materials[5])[5]*optimized_price_with_scrap[-1]
            zn_total += db.get_composition_raw_material(list_id_raw_materials[6])[6]*optimized_price_with_scrap[-1]
            ti_total += db.get_composition_raw_material(list_id_raw_materials[7])[7]*optimized_price_with_scrap[-1]

            # Raw materials data
            for i in range(len(optimized_price_with_scrap)-1):
                df_display.append({
                    'Alloy': alloy_name, 'Optimization': 'Price', 'Use scrap': 'Yes', 'Product': list_raw_materials[i],
                    'Price': db.get_cost_raw_material(alloy_site_code, list_id_raw_materials[i])*optimized_price_with_scrap[i],
                    'CO2': db.get_total_co2(optimized_price_with_scrap)[i], 'Mass': optimized_price_with_scrap[i],
                    'Si': db.get_composition_raw_material(list_id_raw_materials[0])*optimized_price_with_scrap[i],
                    'Fe': db.get_composition_raw_material(list_id_raw_materials[1])*optimized_price_with_scrap[i],
                    'Cu': db.get_composition_raw_material(list_id_raw_materials[2])*optimized_price_with_scrap[i],
                    'Mn': db.get_composition_raw_material(list_id_raw_materials[3])*optimized_price_with_scrap[i],
                    'Mg': db.get_composition_raw_material(list_id_raw_materials[4])*optimized_price_with_scrap[i],
                    'Cr': db.get_composition_raw_material(list_id_raw_materials[5])*optimized_price_with_scrap[i],
                    'Zn': db.get_composition_raw_material(list_id_raw_materials[6])*optimized_price_with_scrap[i],
                    'Ti': db.get_composition_raw_material(list_id_raw_materials[7])*optimized_price_with_scrap[i]})
                price_total += db.get_cost_raw_material(alloy_site_code, list_id_raw_materials[i])*optimized_price_with_scrap[i]
                mass_total += optimized_price_with_scrap[i]
                si_total += db.get_composition_raw_material(list_id_raw_materials[0])*optimized_price_with_scrap[i]
                fe_total += db.get_composition_raw_material(list_id_raw_materials[1])*optimized_price_with_scrap[i]
                cu_total += db.get_composition_raw_material(list_id_raw_materials[2])*optimized_price_with_scrap[i]
                mn_total += db.get_composition_raw_material(list_id_raw_materials[3])*optimized_price_with_scrap[i]
                mg_total += db.get_composition_raw_material(list_id_raw_materials[4])*optimized_price_with_scrap[i]
                cr_total += db.get_composition_raw_material(list_id_raw_materials[5])*optimized_price_with_scrap[i]
                zn_total += db.get_composition_raw_material(list_id_raw_materials[6])*optimized_price_with_scrap[i]
                ti_total += db.get_composition_raw_material(list_id_raw_materials[7])*optimized_price_with_scrap[i]

            #then, add last line with total values of all the components
            df_display.append({
                'Alloy': alloy_name, 'Optimization': 'Price', 'Use scrap': 'Yes', 'Product': 'Total',
                'Price': price_total, 'CO2': db.get_total_co2(optimized_price_with_scrap)[-1],
                'Mass': mass_total, 'Si': si_total, 'Fe': fe_total, 'Cu': cu_total, 'Mn': mn_total,
                'Mg': mg_total, 'Cr': cr_total, 'Zn': zn_total, 'Ti': ti_total})
            

# ===================================================================================================================
            # Price optimization without scrap
# ===================================================================================================================

            try:
                optimized_price_without_scrap = db.optimise_cost_without_scrap(id_site=alloy_site_code, id_alloy=alloy_id)
            except ValueError:
                df_display = df_display.append({
                    'Alloy': alloy_name, 'Optimization': 'Price-Error', 'Use scrap': 'No', 'Product': 'NaN', 'Price': 'NaN',
                    'CO2': 'NaN', 'Mass': 'NaN', 'Si': 'NaN', 'Fe': 'NaN', 'Cu': 'NaN', 'Mn': 'NaN', 'Mg': 'NaN',
                    'Cr': 'NaN', 'Zn': 'NaN', 'Ti': 'NaN'}, ignore_index=True)
                continue

            # Adding the data to the dataframe with the methods to get price and CO2 like before
            price_total, mass_total, si_total, fe_total, cu_total, mn_total, mg_total, cr_total, zn_total, ti_total = 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.

            # Since no scrap is used, we add directly the raw materials data with a loop
            for i in range(len(optimized_price_without_scrap)):
                df_display.append({
                    'Alloy': alloy_name, 'Optimization': 'Price', 'Use scrap': 'No', 'Product': list_raw_materials[i],
                    'Price': db.get_cost_raw_material(alloy_site_code, list_id_raw_materials[i])*optimized_price_without_scrap[i],
                    'CO2': db.get_total_co2(optimized_price_without_scrap)[i], 'Mass': optimized_price_without_scrap[i],
                    'Si': db.get_composition_raw_material(list_id_raw_materials[0])*optimized_price_without_scrap[i],
                    'Fe': db.get_composition_raw_material(list_id_raw_materials[1])*optimized_price_without_scrap[i],
                    'Cu': db.get_composition_raw_material(list_id_raw_materials[2])*optimized_price_without_scrap[i],
                    'Mn': db.get_composition_raw_material(list_id_raw_materials[3])*optimized_price_without_scrap[i],
                    'Mg': db.get_composition_raw_material(list_id_raw_materials[4])*optimized_price_without_scrap[i],
                    'Cr': db.get_composition_raw_material(list_id_raw_materials[5])*optimized_price_without_scrap[i],
                    'Zn': db.get_composition_raw_material(list_id_raw_materials[6])*optimized_price_without_scrap[i],
                    'Ti': db.get_composition_raw_material(list_id_raw_materials[7])*optimized_price_without_scrap[i]})
                price_total += db.get_cost_raw_material(alloy_site_code, list_id_raw_materials[i])*optimized_price_without_scrap[i]
                mass_total += optimized_price_without_scrap[i]
                si_total += db.get_composition_raw_material(list_id_raw_materials[0])*optimized_price_without_scrap[i]
                fe_total += db.get_composition_raw_material(list_id_raw_materials[1])*optimized_price_without_scrap[i]
                cu_total += db.get_composition_raw_material(list_id_raw_materials[2])*optimized_price_without_scrap[i]
                mn_total += db.get_composition_raw_material(list_id_raw_materials[3])*optimized_price_without_scrap[i]
                mg_total += db.get_composition_raw_material(list_id_raw_materials[4])*optimized_price_without_scrap[i]
                cr_total += db.get_composition_raw_material(list_id_raw_materials[5])*optimized_price_without_scrap[i]
                zn_total += db.get_composition_raw_material(list_id_raw_materials[6])*optimized_price_without_scrap[i]
                ti_total += db.get_composition_raw_material(list_id_raw_materials[7])*optimized_price_without_scrap[i]
                
            # lastly, add last line with total values of all the components
            df_display.append({
                'Alloy': alloy_name, 'Optimization': 'Price', 'Use scrap': 'No', 'Product': 'Total',
                'Price': price_total, 'CO2': db.get_total_co2(optimized_price_without_scrap)[-1],
                'Mass': mass_total, 'Si': si_total, 'Fe': fe_total, 'Cu': cu_total, 'Mn': mn_total,
                'Mg': mg_total, 'Cr': cr_total, 'Zn': zn_total, 'Ti': ti_total})


# ===================================================================================================================
            # Optimization of the utilization of scrap
# ===================================================================================================================

            try:
                optimized_mass_with_scrap = db.optimise_utilisation_scrap(id_site=alloy_site_code, id_alloy=alloy_id, id_scrap=0)
            except ValueError:
                df_display = df_display.append({
                    'Alloy': alloy_name, 'Optimization': 'Mass-Error', 'Use scrap': 'Yes', 'Product': 'NaN', 'Price': 'NaN',
                    'CO2': 'NaN', 'Mass': 'NaN', 'Si': 'NaN', 'Fe': 'NaN', 'Cu': 'NaN', 'Mn': 'NaN',
                    'Mg': 'NaN', 'Cr': 'NaN', 'Zn': 'NaN', 'Ti': 'NaN'}, ignore_index=True)
                continue

            # Adding the data to the dataframe with the methods to get price and CO2

            # initializing the totals
            price_total, mass_total, si_total, fe_total, cu_total, mn_total, mg_total, cr_total, zn_total, ti_total = 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.

            # Adding the scrap data
            # Same way of reasoning as before
            df_display.append({
                'Alloy': alloy_name, 'Optimization': 'Scrap utilization', 'Use scrap': 'Yes', 'Product': scrap_name,
                'Price': db.get_cost_scrap(alloy_site_code, id_scrap=0)*optimized_mass_with_scrap[-1],
                'CO2': 0., 'Mass': optimized_mass_with_scrap[-1],
                'Si': db.get_composition_raw_material(list_id_raw_materials[0])[0]*optimized_mass_with_scrap[-1],
                'Fe': db.get_composition_raw_material(list_id_raw_materials[1])[1]*optimized_mass_with_scrap[-1],
                'Cu': db.get_composition_raw_material(list_id_raw_materials[2])[2]*optimized_mass_with_scrap[-1],
                'Mn': db.get_composition_raw_material(list_id_raw_materials[3])[3]*optimized_mass_with_scrap[-1],
                'Mg': db.get_composition_raw_material(list_id_raw_materials[4])[4]*optimized_mass_with_scrap[-1],
                'Cr': db.get_composition_raw_material(list_id_raw_materials[5])[5]*optimized_mass_with_scrap[-1],
                'Zn': db.get_composition_raw_material(list_id_raw_materials[6])[6]*optimized_mass_with_scrap[-1],
                'Ti': db.get_composition_raw_material(list_id_raw_materials[7])[7]*optimized_mass_with_scrap[-1]})
            price_total += db.get_cost_scrap(alloy_site_code, id_scrap=0)*optimized_mass_with_scrap[-1]
            mass_total += optimized_mass_with_scrap[-1]
            si_total += db.get_composition_raw_material(list_id_raw_materials[0])[0]*optimized_mass_with_scrap[-1]
            fe_total += db.get_composition_raw_material(list_id_raw_materials[1])[1]*optimized_mass_with_scrap[-1]
            cu_total += db.get_composition_raw_material(list_id_raw_materials[2])[2]*optimized_mass_with_scrap[-1]
            mn_total += db.get_composition_raw_material(list_id_raw_materials[3])[3]*optimized_mass_with_scrap[-1]
            mg_total += db.get_composition_raw_material(list_id_raw_materials[4])[4]*optimized_mass_with_scrap[-1]
            cr_total += db.get_composition_raw_material(list_id_raw_materials[5])[5]*optimized_mass_with_scrap[-1]
            zn_total += db.get_composition_raw_material(list_id_raw_materials[6])[6]*optimized_mass_with_scrap[-1]
            ti_total += db.get_composition_raw_material(list_id_raw_materials[7])[7]*optimized_mass_with_scrap[-1]

            # Raw materials data
            for i in range(len(optimized_mass_with_scrap)-1):
                df_display.append({
                    'Alloy': alloy_name, 'Optimization': 'Scrap utilization', 'Use scrap': 'Yes', 'Product': list_raw_materials[i],
                    'Price': db.get_cost_raw_material(alloy_site_code, list_id_raw_materials[i])*optimized_mass_with_scrap[i],
                    'CO2': db.get_total_co2(optimized_mass_with_scrap)[i], 'Mass': optimized_mass_with_scrap[i],
                    'Si': db.get_composition_raw_material(list_id_raw_materials[0])*optimized_mass_with_scrap[i],
                    'Fe': db.get_composition_raw_material(list_id_raw_materials[1])*optimized_mass_with_scrap[i],
                    'Cu': db.get_composition_raw_material(list_id_raw_materials[2])*optimized_mass_with_scrap[i],
                    'Mn': db.get_composition_raw_material(list_id_raw_materials[3])*optimized_mass_with_scrap[i],
                    'Mg': db.get_composition_raw_material(list_id_raw_materials[4])*optimized_mass_with_scrap[i],
                    'Cr': db.get_composition_raw_material(list_id_raw_materials[5])*optimized_mass_with_scrap[i],
                    'Zn': db.get_composition_raw_material(list_id_raw_materials[6])*optimized_mass_with_scrap[i],
                    'Ti': db.get_composition_raw_material(list_id_raw_materials[7])*optimized_mass_with_scrap[i]})
                price_total += db.get_cost_raw_material(alloy_site_code, list_id_raw_materials[i])*optimized_mass_with_scrap[i]
                mass_total += optimized_mass_with_scrap[i]
                si_total += db.get_composition_raw_material(list_id_raw_materials[0])*optimized_mass_with_scrap[i]
                fe_total += db.get_composition_raw_material(list_id_raw_materials[1])*optimized_mass_with_scrap[i]
                cu_total += db.get_composition_raw_material(list_id_raw_materials[2])*optimized_mass_with_scrap[i]
                mn_total += db.get_composition_raw_material(list_id_raw_materials[3])*optimized_mass_with_scrap[i]
                mg_total += db.get_composition_raw_material(list_id_raw_materials[4])*optimized_mass_with_scrap[i]
                cr_total += db.get_composition_raw_material(list_id_raw_materials[5])*optimized_mass_with_scrap[i]
                zn_total += db.get_composition_raw_material(list_id_raw_materials[6])*optimized_mass_with_scrap[i]
                ti_total += db.get_composition_raw_material(list_id_raw_materials[7])*optimized_mass_with_scrap[i]

            #then, add last line with total values of all the components
            df_display.append({
                'Alloy': alloy_name, 'Optimization': 'Scrap utilization', 'Use scrap': 'Yes', 'Product': 'Total',
                'Price': price_total, 'CO2': db.get_total_co2(optimized_mass_with_scrap)[-1],
                'Mass': mass_total, 'Si': si_total, 'Fe': fe_total, 'Cu': cu_total, 'Mn': mn_total,
                'Mg': mg_total, 'Cr': cr_total, 'Zn': zn_total, 'Ti': ti_total})



        # We can now add the dataframe to the dict of tables to be displayed in the Streamlit app and put in sheets for the Excel file, each sheet for a different scrap
        scrap_tables[scrap_name] = df_display



#Save the list of DataFrames to an Excel file
if st.button("Save to Excel"):
    with pd.ExcelWriter("optimized_scrap_data.xlsx") as writer:
        for scrap_name, df in scrap_tables.items():
            df.to_excel(writer, sheet_name=scrap_name, index=False)
    st.success("Data saved to optimized_scrap_data.xlsx")
    st.download_button(label="Download Excel file", data="optimized_scrap_data.xlsx", file_name="optimized_scrap_data.xlsx")
from os import path
import streamlit as st
from data.db_tools import Database
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

# testing excel file upload
st.write("You can upload here an Excel file with the scrap data. Please be careful to use the correct format, like the example provided.")
st.download_button(label="Download example file", data="interface/data_example_interface.py", file_name="data_example_interface.xlsx")
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is not None:
    df_scrap = pd.read_excel(uploaded_file)
    columns = df_scrap.columns.tolist()
    if columns != ["scrap_name", "Si", "Fe", "Cu", "Mn", "Mg", "Cr", "Zn", "Ti", "shape", "scrap_purchasing_cost_per_t", "transportation_cost_per_t", "currency"]:
        st.error("The uploaded file does not have the correct format. Please check the example file.")
    
    df_display = pd.DataFrame(columns=['Alloy', 'Optimization', 'Use scrap', 'Product', 'Price', 'CO2', 'Mass', 'Si', 'Fe', 'Cu', 'Mn', 'Mg', 'Cr', 'Zn', 'Ti'])
    scrap_tables = {}

    for line in df_scrap.itertuples(index=False):
        scrap_name, si, fe, cu, mn, mg, cr, zn, ti, shape, scrap_purchasing_cost_per_t, transportation_cost_per_t, currency = line
        shape_id = conn.query(f"SELECT shape_type_id FROM shape_type WHERE name='{shape}'").iloc[0, 0]
        currency_id = conn.query(f"SELECT currency_id FROM currency WHERE name='{currency}'").iloc[0, 0]
        compo_id = conn.query("SELECT COUNT(*) FROM composition").iloc[0, 0] + 1  # the scrap composition ID is the last ID in the composition table

        insert_compo = conn.query("INSERT INTO composition (composition_id, Si, Fe, Cu, Mn, Mg, Cr, Zn, Ti) "
                                "VALUES (:compo_id, :si, :fe, :cu, :mn, :mg, :cr, :zn, :ti)",
                                dict(compo_id=compo_id, si=si, fe=fe, cu=cu, mn=mn, mg=mg, cr=cr, zn=zn, ti=ti))
        with conn.session as session:
            session.execute(insert_compo)
            session.commit()
        
        delete_scrap = db.query("DELETE FROM scrap")
        with conn.session as session:
            session.execute(delete_scrap)
            session.commit()
        
        insert_scrap = db.query("INSERT INTO scrap (scrap_id, scrap_name, composition_id, shape_type_id, scrap_purchasing_cost_per_t, transportation_cost_per_t, currency_id) "
                                "VALUES (:ID_SCRAP, :scrap_name, :compo_id, :shape_id, :scrap_purchasing_cost_per_t, :transportation_cost_per_t, :currency_id)",
                                dict(ID_SCRAP=0,
                                     scrap_name=scrap_name,
                                     compo_id=compo_id,
                                     shape_id=shape_id,
                                     scrap_purchasing_cost_per_t=scrap_purchasing_cost_per_t,
                                     transportation_cost_per_t=transportation_cost_per_t,
                                     currency_id=currency_id))
        with conn.session as session:
            session.execute(insert_scrap)
            session.commit()
        
        # now, we do the calculations and put it in a new dataframe
        for _, row in alloys.iterrows():
            alloy_name = row['name']
            alloy_site_code = row['site_code']
            alloy_composition_id = row['composition_id']
            alloy_id = row['alloy_id']

            # if the program returns a ValueError, fill the excel table with NaN
            try:
                optimized_co2_with_scrap = [x*100 for x in db.optimise_co2_with_scrap(id_site=alloy_site_code, id_alloy=alloy_id, id_scrap=0)] #composition in %
            except ValueError:
                df_display = df_display.append({'Alloy': alloy_name, 'Optimization': 'CO2-Error', 'Use scrap': 'Yes', 'Product': 'NaN', 'Price': 'NaN', 'CO2': 'NaN', 'Mass': 'NaN',
                                                'Si': 'NaN', 'Fe': 'NaN', 'Cu': 'NaN', 'Mn': 'NaN', 'Mg': 'NaN', 'Cr': 'NaN', 'Zn': 'NaN', 'Ti': 'NaN'}, ignore_index=True)
                continue

            #adding the data to the dataframe with the methods to get price and CO2
            #then, add last line with total values of all the components

            try:
                optimized_co2_without_scrap = [x*100 for x in db.optimise_co2_without_scrap(id_site=alloy_site_code, id_alloy=alloy_id)]
            except ValueError:
                df_display = df_display.append({'Alloy': alloy_name, 'Optimization': 'CO2-Error', 'Use scrap': 'No', 'Product': 'NaN', 'Price': 'NaN', 'CO2': 'NaN', 'Mass': 'NaN',
                                                'Si': 'NaN', 'Fe': 'NaN', 'Cu': 'NaN', 'Mn': 'NaN', 'Mg': 'NaN', 'Cr': 'NaN', 'Zn': 'NaN', 'Ti': 'NaN'}, ignore_index=True)
                continue

            #adding the data to the dataframe with the methods to get price and CO2
            #then, add last line with total values of all the components

            try:
                optimized_price_with_scrap = db.optimise_price_with_scrap(id_site=alloy_site_code, id_alloy=alloy_id, id_scrap=0)
            except ValueError:
                df_display = df_display.append({'Alloy': alloy_name, 'Optimization': 'Price-Error', 'Use scrap': 'Yes', 'Product': 'NaN', 'Price': 'NaN', 'CO2': 'NaN', 'Mass': 'NaN',
                                                'Si': 'NaN', 'Fe': 'NaN', 'Cu': 'NaN', 'Mn': 'NaN', 'Mg': 'NaN', 'Cr': 'NaN', 'Zn': 'NaN', 'Ti': 'NaN'}, ignore_index=True)
                continue

            #adding the data to the dataframe with the methods to get price and CO2
            #then, add last line with total values of all the components

            try:
                optimized_price_without_scrap = db.optimise_price_without_scrap(id_site=alloy_site_code, id_alloy=alloy_id)
            except ValueError:
                df_display = df_display.append({'Alloy': alloy_name, 'Optimization': 'Price-Error', 'Use scrap': 'No', 'Product': 'NaN', 'Price': 'NaN', 'CO2': 'NaN', 'Mass': 'NaN',
                                                'Si': 'NaN', 'Fe': 'NaN', 'Cu': 'NaN', 'Mn': 'NaN', 'Mg': 'NaN', 'Cr': 'NaN', 'Zn': 'NaN', 'Ti': 'NaN'}, ignore_index=True)
                continue

            #adding the data to the dataframe with the methods to get price and CO2
            #then, add last line with total values of all the components

            try:
                optimized_mass_with_scrap = db.optimise_utilisation_scrap(id_site=alloy_site_code, id_alloy=alloy_id, id_scrap=0)
            except ValueError:
                df_display = df_display.append({'Alloy': alloy_name, 'Optimization': 'Mass-Error', 'Use scrap': 'Yes', 'Product': 'NaN', 'Price': 'NaN', 'CO2': 'NaN', 'Mass': 'NaN',
                                                'Si': 'NaN', 'Fe': 'NaN', 'Cu': 'NaN', 'Mn': 'NaN', 'Mg': 'NaN', 'Cr': 'NaN', 'Zn': 'NaN', 'Ti': 'NaN'}, ignore_index=True)
                continue

            #adding the data to the dataframe with the methods to get price and CO2
            #then, add last line with total values of all the components

        #Now, we can add the dataframe to the dict of tables to be displayed in the Streamlit app and put in sheets for the Excel file, each sheet for a different scrap
        scrap_tables[scrap_name] = df_display

    # Display the DataFrame in Streamlit
    st.write(df_display)

#Save the list of DataFrames to an Excel file
if st.button("Save to Excel"):
    with pd.ExcelWriter("optimized_scrap_data.xlsx") as writer:
        for scrap_name, df in scrap_tables.items():
            df.to_excel(writer, sheet_name=scrap_name, index=False)
    st.success("Data saved to optimized_scrap_data.xlsx")
    st.download_button(label="Download Excel file", data="optimized_scrap_data.xlsx", file_name="optimized_scrap_data.xlsx")
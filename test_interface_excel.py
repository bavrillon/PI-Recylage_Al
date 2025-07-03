from os import path
import streamlit as st
from data.db_tools import Database
import pandas as pd

db = Database(path.join(path.dirname(__file__), "data.db"))
conn = st.connection("data_db",type="sql", connect_args={"timeout": 5})

# testing excel file upload
st.write("You can upload here an Excel file with the scrap data. Please be careful to use the correct format, like the example provided.")
st.download_button(label="Download example file", data="interface/data_example_interface.py", file_name="data_example_interface.xlsx")
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    columns = df.columns.tolist()
    if columns != ["scrap_name", "Si", "Fe", "Cu", "Mn", "Mg", "Cr", "Zn", "Ti", "shape", "scrap_purchasing_cost_per_t", "transportation_cost_per_t", "currency"]:
        st.error("The uploaded file does not have the correct format. Please check the example file.")
    
    for line in df.itertuples(index=False):
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
        
        
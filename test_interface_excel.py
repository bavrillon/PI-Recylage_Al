from os import path
import streamlit as st
from data.db_tools import Database
import pandas as pd

db = Database(path.join(path.dirname(__file__), "data.db"))

# testing excel file upload
st.write("You can upload here an Excel file with the scrap data. Please be careful to use the correct format, like the example provided.")
st.download_button(label="Download example file", data="interface/data_example_interface.py", file_name="data_example_interface.xlsx")
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    
import streamlit as st

main_page = st.Page("interface.py", title="Optimized use of a scrap")
page_2 = st.Page("interface_excel.py", title="Import multiple scraps")

pg = st.navigation([main_page, page_2])

pg.run()
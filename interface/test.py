import streamlit as st
import pandas as pd
import numpy as np

st.markdown('Test')

st.sidebar.write('Trucs')
st.sidebar.slider('ouh la la')

st.text_input('écris')

left_column, right_column = st.columns(2)

left_column.button('Un bouton')
right_column.checkbox('NE COCHE PAS')
left_column.write(pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
}))
chart_data = pd.DataFrame(
     np.random.randn(20, 3),
     columns=['a', 'b', 'c'])

right_column.line_chart(chart_data)

map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.map(map_data)
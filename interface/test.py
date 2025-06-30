import streamlit as st

st.markdown('Test')

st.sidebar.write('Trucs')
st.sidebar.slider('ouh la la')

left_column, right_column = st.columns(2)

left_column.button('Un bouton')
right_column.checkbox('NE COCHE PAS')
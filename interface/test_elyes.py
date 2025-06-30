import streamlit as st
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

st.title("Test Interface Elyes")
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    st.write("DataFrame loaded successfully!")

    st.subheader("Data Preview")
    st.dataframe(df.head())

    st.subheader("Data Summary")
    st.write(df.describe())

    st.subheader('Select Data')
    columns = df.columns.tolist()
    selected_columns = st.selectbox('Select column to filter by', columns)
    unique_values = df[selected_columns].unique()
    selected_value = st.selectbox('Select value to filter by', unique_values)

    filtered_df = df[df[selected_columns] == selected_value]
    st.write(f"Filtered DataFrame where {selected_columns} is {selected_value}:")
    st.dataframe(filtered_df)

    st.subheader("Data Visualization")
    x_col = st.selectbox("Select X-axis column", columns)
    y_col = st.selectbox("Select Y-axis column", columns)

    if st.button("Plot Data"):
        plt.figure(figsize=(10, 5))
        plt.plot(df[x_col], df[y_col], marker='o')
        plt.title(f"{y_col} vs {x_col}")
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        st.pyplot(plt)
        
else:
    st.write("Please upload a CSV or Excel file to proceed.")
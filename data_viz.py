"""
Created on Sat Aug 20 2022

@author: Harold
"""

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


###############################################################################
#Start building Streamlit App
###############################################################################

st.title('Stock-Inventory Discrepancy (Analytics)')

# Upload data in Side bar
with st.sidebar:
    expected_file = st.file_uploader('CHOOSE EXPECTED DATA:', type='csv')
    counted_file = st.file_uploader('CHOOSE COUNTED DATA:', type='csv')


# Check if files are uploaded
if expected_file is not None:
    df_expected = pd.read_csv(expected_file, encoding='latin-1', dtype=str)
else:
    st.warning('Expected CSV file is missing!')

if counted_file is not None:
    df_counted = pd.read_csv(counted_file, encoding='latin-1', dtype=str)
else:
    st.warning('Counted CSV file is missing!')

# Side bar 
add_sidebar = st.sidebar.selectbox('Choose a function', ('Raw Datasets', 'Analysis Dashboard', 'Recomendations')) 

try:
    if add_sidebar == 'Raw Datasets':
        st.text('Expected Data')
        st.dataframe(df_expected)

        st.markdown('---')

        st.text('Counted Data')
        st.dataframe(df_counted)

    if add_sidebar == 'Analysis Dashboard':
        # Remove duplicates
        df_counted = df_counted.drop_duplicates("RFID")

        # We need to do an Product ID Agregation on SKU in the counted df
        df_B = df_counted.groupby("Retail_Product_SKU").count()[["RFID"]].reset_index().rename(columns={"RFID":"Retail_CCQTY"})

        # Selection of features for analysis
        my_cols_selected = ["Retail_Product_Color",
        "Retail_Product_Level1",
        "Retail_Product_Level1Name",
        "Retail_Product_Level2Name",
        "Retail_Product_Level3Name",
        "Retail_Product_Level4Name",
        "Retail_Product_Name",
        "Retail_Product_SKU",
        "Retail_Product_Size",
        "Retail_Product_Style",
        "Retail_SOHQTY"]

        # Creation of df with the selected features
        df_A = df_expected[my_cols_selected]

        # Merge with the agrupated Counted df
        df_discrepancy = pd.merge(df_A, df_B, how="outer", left_on="Retail_Product_SKU", right_on="Retail_Product_SKU", indicator=True)


        # Discrepancy data enrichment
        # Null elimination in CCQTY (We recomend fill with 0 because the trazability method)
        df_discrepancy['Retail_CCQTY'] = df_discrepancy['Retail_CCQTY'].fillna(0)

        # Fixing data type to numeric to calculation 
        df_discrepancy["Retail_CCQTY"] = df_discrepancy["Retail_CCQTY"].astype(int)

        # Same treatment for SQHQTY
        df_discrepancy["Retail_SOHQTY"] = df_discrepancy["Retail_SOHQTY"].fillna(0).astype(int)
        

        # Calculations
        # Difference calculation
        df_discrepancy["Diff"] = df_discrepancy["Retail_CCQTY"] - df_discrepancy["Retail_SOHQTY"]

        # Difference under --entender
        df_discrepancy.loc[df_discrepancy["Diff"]<0, "Unders"] = df_discrepancy['Diff'] * (-1)
        df_discrepancy["Unders"] = df_discrepancy["Unders"].fillna(0).astype(int) 
    
        # Display dataframe
        st.dataframe(df_discrepancy)

        # Accuracy Calculations
        # Retail product
        st.dataframe(df_discrepancy.groupby("Retail_Product_Level1Name").sum())
        st.dataframe(df_discrepancy.describe())

        # Indicators test
        col1, col2, col3 = st.columns(3)

        ind_test = 30
        col1.metric('Test', str(ind_test) + '%')
        col2.metric('Test', str(ind_test) + '%')
        col3.metric('Test', str(ind_test) + '%')

        # Viz test
        fig1 = plt.figure(figsize=(10, 4))
        ax = sns.countplot(x='Retail_Product_Color', data=df_discrepancy)
        ax.set_xticklabels(ax.get_xticklabels(), rotation = 45)

        st.pyplot(fig1)


    if add_sidebar == 'Recomendations':
        st.write('The dataframe needs more cleaning')

except Exception as e:
    st.write("Error: {}".format(e))

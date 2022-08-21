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

st.title('Stock-Inventory Discrepancy')

# Upload data in Side bar
with st.sidebar:
    st.subheader('Load Data')
    expected_file = st.file_uploader('CHOOSE EXPECTED DATA:', type='csv')
    counted_file = st.file_uploader('CHOOSE COUNTED DATA:', type='csv')
    st.subheader('Options')


# Check if files are uploaded
if expected_file is not None:
    df_expected = pd.read_csv(expected_file, encoding='latin-1', dtype=str)
else:
    st.warning('Expected CSV file is missing! Please load data')

if counted_file is not None:
    df_counted = pd.read_csv(counted_file, encoding='latin-1', dtype=str)
else:
    st.warning('Counted CSV file is missing! Please load data')

# Side bar 
add_sidebar = st.sidebar.selectbox('SELECT DISPLAY', ('Raw Datasets', 'Analysis Dashboard')) 

try:
    if add_sidebar == 'Raw Datasets':
        st.header('Expected Data')
        st.dataframe(df_expected)
        st.subheader('Expected Data Columns View')
        st.dataframe(df_expected.sample(4).T)

        st.markdown('---')

        st.header('Counted Data')
        st.dataframe(df_counted)
        st.subheader('Counted Data Columns View')
        st.dataframe(df_counted.sample(4).T)


    if add_sidebar == 'Analysis Dashboard':
        # Remove duplicates
        df_counted = df_counted.drop_duplicates('RFID')

        # We need to do an Product ID Agregation on SKU in the counted df
        df_B = df_counted.groupby('Retail_Product_SKU').count()[['RFID']].reset_index().rename(columns={'RFID':'Retail_CCQTY'})

        # Selection of features for analysis
        my_cols_selected = ['Retail_Product_SKU',
        'Retail_Product_Name',
        'Retail_Product_Color',
        'Retail_Product_Size',
        'Retail_Product_Dimension',
        'Retail_Product_Manufacturer',
        'Retail_Product_Style',
        'Retail_Product_Level1',
        'Retail_Product_Level1Name',
        'Retail_Product_Level2Name',
        'Retail_Product_Level3Name',
        'Retail_Product_Level4Name',
        'Retail_StoreNumber',
        'Retail_SOHQTY'
        ]

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
        # Difference diff
        df_discrepancy["Diff"] = df_discrepancy["Retail_CCQTY"] - df_discrepancy["Retail_SOHQTY"]

        # Difference under
        df_discrepancy.loc[df_discrepancy["Diff"]<0, "Unders"] = df_discrepancy['Diff'] * (-1)
        df_discrepancy["Unders"] = df_discrepancy["Unders"].fillna(0).astype(int)

        # Difference match
        df_discrepancy["Match"] = df_discrepancy["Retail_SOHQTY"] - df_discrepancy["Unders"]
    
        # Display dataframe
        st.header('Discrepancy Table')
        st.dataframe(df_discrepancy)

        # Accuracy Calculations
        df_calc = df_discrepancy.groupby("Retail_Product_Level1Name").sum()
        df_calc['SKUAccuracy'] = (df_calc['Match'] / df_calc['Retail_SOHQTY'])*100
        df_calc['ItemAccuracy'] = (df_calc['Retail_CCQTY'] / df_calc['Retail_SOHQTY'])*100

        st.subheader('Accuracy Calculation %')
        st.dataframe(df_calc)


        # Indicators test
        col1, col2, col3, col4 = st.columns(4)

        
        ind_test = 30
        col1.metric('Total SOHQTY', str(df_discrepancy['Retail_SOHQTY'].sum()))
        col2.metric('Total CCQTY', str(df_discrepancy['Retail_CCQTY'].sum()))
        col3.metric('Total DIFF', str(df_discrepancy['Retail_SOHQTY'].sum() - df_discrepancy['Retail_CCQTY'].sum()))

        total_loss = (((df_discrepancy['Retail_SOHQTY'].sum() - df_discrepancy['Retail_CCQTY'].sum()) * (-1)) / (df_discrepancy['Retail_CCQTY'].sum()))*100
        col4.metric('DIFF Percentage ', str(round(total_loss, 1)) + '%')

        # Visualizations
        fig1 = plt.figure(figsize=(10, 4))
        ax1 = sns.countplot(x='Retail_Product_Level1Name', data=df_discrepancy, palette='Paired')
        ax1.set_xticklabels(ax1.get_xticklabels(), rotation = 0)

        st.markdown('---')
        st.subheader('Visualizations')

        st.text('Product class distribution.')
        st.pyplot(fig1)

        fig2 = plt.figure(figsize=(10, 4))
        ax2 = sns.scatterplot(data=df_discrepancy, x='Retail_SOHQTY', y='Retail_CCQTY', color="skyblue")

        st.text('The scatterplot will show a straight line if SQHQTY and CCQTY are equal.')
        st.pyplot(fig2)

        fig3 = plt.figure(figsize=(10, 4))
        ax3 = sns.heatmap(df_discrepancy.corr(), annot=True, cmap='Blues')
        ax3.set_xticklabels(ax3.get_xticklabels(), rotation = 45)

        st.text('Correlation heatmap')
        st.pyplot(fig3)


except Exception as e:
    st.write("Error: {}".format(e))

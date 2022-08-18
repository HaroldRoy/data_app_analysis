import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title('CSV Reader')
file = st.file_uploader('upload a csv', type="csv")
if file:
    df = pd.read_csv(file)
    st.dataframe(df)
    st.markdown("---")
    fig1 = plt.figure(figsize=(10, 4))
    sns.countplot(x='Pclass', data=df)

    st.pyplot(fig1)

    st.markdown("---")

    fig2 = plt.figure(figsize=(10, 4))
    sns.boxplot(x='Pclass',
                y='Age',
                data = df
    )

    st.pyplot(fig2)

    st.markdown("---")
    
    fig3 = plt.figure(figsize=(10, 4))
    sns.heatmap(df.corr(), annot=True)

    st.pyplot(fig3)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title('CSV Reader')
file = st.file_uploader('upload a csv', type="csv")
if file:
    df = pd.read_csv(file)
    st.dataframe(df)
    st.markdown("---")
    fig1 = plt.figure(figsize =(10, 4))
    plt.hist(df['Sex'])

    st.pyplot(fig1)

    st.markdown("---")

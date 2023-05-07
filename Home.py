import streamlit as st
from components.authorization import authenticate
st.set_page_config(page_title="Insane Computing", page_icon="🧊")
st.title("Insane Computing")

authenticate()

st.write("You can now access the insane computing dashboard.")
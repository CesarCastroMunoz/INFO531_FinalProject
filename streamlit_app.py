import streamlit as st

st.set_page_config(page_title="INFO531", page_icon=":bar_chart:")

st.title("INFO531")
st.write("Welcome to my Streamlit app!")

name = st.text_input("Your name")
if name.strip():
    st.success(f"Hello, {name.strip()}!")

st.caption("Built with Streamlit.")

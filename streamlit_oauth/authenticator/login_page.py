import streamlit as st
import webbrowser

def login_page(title, auth_url):
    st.title(f'Welcome to {title}')

    st.write('Please authenticate in order to access this dashboard')

    login = st.button('Login')

    if login:
        webbrowser.open(auth_url)
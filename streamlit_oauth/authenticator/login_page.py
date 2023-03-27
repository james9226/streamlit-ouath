import streamlit as st
from bokeh.models.widgets import Div
import streamlit as st

def navigate_to(url):
    # Hacky solution, need to find literally anything else that works
    # There is the raw HTML href option, but it is ugly and extremely, extremely, hacky
    # Using ST components presents its own issue, as they are in sandboxed iframes
    js = f"window.open('{url}')" 
    html = '<img src onerror="{}">'.format(js)
    div = Div(text=html)
    st.bokeh_chart(div)

def login_page(title, auth_url, error_state = False):
    st.title(f'Welcome to {title}')

    if error_state:
        st.error('Login failed / timed out - please try again')
    else:
        st.info('Please authenticate in order to access this dashboard')
        
    col1, col2, col3 , col4, col5 = st.columns(5)

    with col1:
        pass
    with col2:
        pass
    with col4:
        pass
    with col5:
        pass
    with col3 :
        center_button = st.button('Login')

    if center_button:
        navigate_to(auth_url)




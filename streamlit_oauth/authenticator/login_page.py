import time
import streamlit as st
import streamlit.components.v1 as components
from streamlit.components.v1 import html
from bokeh.models.widgets import Div
import streamlit as st


# def nav_to(url):
#     nav_script = """
#         <meta http-equiv="refresh" content="0; url='%s'">
#     """ % (url)
#     st.write(nav_script, unsafe_allow_html=True)

# def nav_two(url):
#     nav_script = """
#     <meta http-equiv="refresh" content="5; URL=javascript:window.open('%s','_blank');">
#     """ % (url)

#     nav_script = f"""
#     <script> window.open({url}, '_blank').focus(); </script>
#     """
#     st.write(nav_script, unsafe_allow_html=True)


def navigate_to(url):
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


    with st.spinner():
        navigate_to(auth_url)

        # components.html(f"""
        #   <script>  window.top.location.href = "http://www.example.com" </script>; 
        # """)
        
        time.sleep(2)

        # if st.button('Go to Streamlit'):
        #     js = "window.open('https://www.streamlit.io/')"  # New tab or window
        #     # js = "window.location.href = 'https://www.streamlit.io/'"  # Current tab
        #     html = '<img src onerror="{}">'.format(js)
        #     div = Div(text=html)
        #     st.bokeh_chart(div)


        st.write(
            f"""<h1>
            <a target="_self"
            href="{auth_url}">Please login using OKTA</a></h1>""",
            unsafe_allow_html=True,
        )



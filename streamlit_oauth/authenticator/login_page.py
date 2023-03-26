import time
import streamlit as st

def nav_to(url):
    nav_script = """
        <meta http-equiv="refresh" content="0; url='%s'">
    """ % (url)
    st.write(nav_script, unsafe_allow_html=True)


def login_page(title, auth_url, error_state = False):
    st.title(f'Welcome to {title}')

    if error_state:
        st.error('Login failed / timed out - please try again')
    else:
        st.info('Please authenticate in order to access this dashboard')


    with st.spinner():
        nav_to(auth_url)
        time.sleep(2)
        st.write(
            f"""<h1>
            <a target="_self"
            href="{auth_url}">Please login using OKTA</a></h1>""",
            unsafe_allow_html=True,
        )



from datetime import datetime, timedelta
from streamlit_oauth.authenticator.auth_manager import AuthManager
from streamlit_oauth.authenticator.config import okta_client_config, redirect_uri
from streamlit_oauth.pages.dashboard import dashboard
import streamlit as st

st.set_page_config(
    page_title="Uber Dashboard",
    page_icon="🚕",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items={"About": "# This is a header. This is an *extremely* cool app!"},
)

auth_manager = AuthManager(
    client_config=okta_client_config,
    redirect_uri=redirect_uri,
    page_name='Uber Dashboard',
    cookies_enabled=True,
    cookie_name='ouath-streamlit',
    cookie_expiry_seconds=60*60,
    cookie_signing_key=st.secrets["cookie_signing_key"]
)

auth_manager.authenticate()

auth_manager.authenticated(dashboard)

from streamlit_cookies_manager import EncryptedCookieManager

# # This should be on top of your script
# cookies = EncryptedCookieManager(
#     # This prefix will get added to all your cookie names.
#     # This way you can run your app on Streamlit Cloud without cookie name clashes with other apps.
#     prefix="ktosiek/streamlit-cookies-manager/",
#     # You should really setup a long COOKIES_PASSWORD secret if you're running on Streamlit Cloud.
#     password=st.secrets["cookie_signing_key"],
# )
# if not cookies.ready():
#     # Wait for the component to load and send us current cookies.
#     st.stop()

# st.write("Current cookies:", cookies)
# value = st.text_input("New value for a cookie")
# if st.button("Change the cookie"):
#     cookies['a-cookie'] = value  # This will get saved on next rerun
#     if st.button("No really, change it now"):
#         cookies.save()  # Force saving the cookies now, without a rerun



def set_test_cookie():
    auth_manager.cookie_manager.set(
    'test123',
    'ThisIsATest',
    expires_at=datetime.now()
    + timedelta(seconds=60 * 60),
)


if st.button('Press to set a cookie!', key=2151):
    set_test_cookie()
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
)

auth_manager.authenticate()

auth_manager.authenticated(dashboard)
